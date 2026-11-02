"""Regression tests for proposal 20261102-unified-workflow: gate GI (skill/integrity.md).

T-080  blocking matrix: a clean report passes; any SUSPECTED blocks; INSUFFICIENT_EVIDENCE blocks on M1/M3/M5/M6 at pre and on
       every mode at final
T-081  the VERIFIER cannot overrule the tools: a CLEAR with no evidence, or against a tool finding, does not stand; a report
       on another draft, a missing report or a missing bundle fails
T-082  alignment: the sample replays exactly, covers every high-impact sentence, bounds the sentinels; a failed sentinel widens
       to its section; overstated or unsupported makes M2 SUSPECTED; understated must be fixed
T-083  a declared no-experiments paper is exempt, unless the draft contradicts the declaration
T-084  decisions: a named person with a reason, listed in open_issues.md; anything less fails; a decision keeps the status;
       the round cap holds
T-085  stage final: paper.md must be the checked draft without tags; a pre-stage SUSPECTED must be CLEAR now; old retraction
       checks fail
T-086  nobody checks their own work: with a ledger the report must be recorded by the VERIFIER; AUTHOR may not write it
T-087  the deterministic evidence per mode finds what it should on planted defects

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import integrity_check as ic  # noqa: E402
import rce_index as ix  # noqa: E402
import workflow_guard as wg  # noqa: E402

DRAFT = """# A study of normalization

## Introduction

Forecasts degrade under level shift (Smith, 2021) {C003}.

## Methods

We trained the model for 12 epochs {C002}.

## Results

The error fell to 0.42 across 5 seeds {C001}.
"""


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.rcs = self.root / ".rcs"
        for d in ("claims", "evidence", "corpus", "story", "plan", "audits/gates", "drafts/v001"):
            (self.rcs / d).mkdir(parents=True)
        (self.root / "results").mkdir()
        (self.root / "results" / "metrics.csv").write_text("method,mae\nours,0.42\n", encoding="utf-8")
        self.claims = [{"id": "C001", "statement": "Error fell to 0.42.", "claim_type": "measured", "evidence": ["E001"], "basis": "project_file"},
                       {"id": "C002", "statement": "Trained for 12 epochs.", "claim_type": "observed", "evidence": ["E002"], "basis": "code"},
                       {"id": "C003", "statement": "Forecasts degrade under shift.", "claim_type": "literature", "evidence": [], "basis": "literature", "sources": ["SRC-001"]}]
        self.evidence = [{"id": "E001", "kind": "result", "summary": "ours MAE", "value": {"metric": "MAE", "mean": 0.42, "std": 0.01, "n": 5},
                          "locator": {"path": "results/metrics.csv", "anchor": "row ours"}, "strength": "hard", "status": "ok"},
                         {"id": "E002", "kind": "method_detail", "summary": "12 epochs", "value": {"epochs": 12},
                          "locator": {"path": "results/metrics.csv", "anchor": "x"}, "strength": "hard", "status": "ok"}]
        self.sources = [{"id": "SRC-001", "title": "T", "authors": ["Smith, Ann"], "year": 2021,
                         "verification": {"method": "doi_lookup", "date": "2026-11-02", "lookup_verified": True},
                         "establishes": [{"statement": "x", "support_quote": "forecasts degrade", "location": "p. 2"}],
                         "retraction": {"status": "not_retracted", "checked_at": ix.today(), "source": "crossref"}}]
        self.config = {"mode": "paper", "paper_type": "empirical"}
        self.draft = self.rcs / "drafts" / "v001" / "paper.md"
        self.draft.write_text(DRAFT, encoding="utf-8")
        (self.rcs / "story" / "spine.md").write_text("1. Problem {C003}\n5. Key finding {C001}\n", encoding="utf-8")
        (self.rcs / "story" / "alternatives.md").write_text("# Alternatives\n\n- Chance: ruled out by 5 seeds.\n", encoding="utf-8")
        (self.rcs / "story" / "rq_check.md").write_text("RQ checked\n", encoding="utf-8")
        (self.rcs / "state.json").write_text("{}", encoding="utf-8")
        self.save()

    def save(self):
        (self.rcs / "claims" / "claim_evidence_map.json").write_text(json.dumps({"claims": self.claims}), encoding="utf-8")
        (self.rcs / "evidence" / "research_evidence.json").write_text(json.dumps({"items": self.evidence}), encoding="utf-8")
        reg = self.rcs / "corpus" / "source_registry.json"
        reg.write_text(json.dumps({"sources": self.sources}), encoding="utf-8")
        (self.rcs / "plan" / "paper_config.json").write_text(json.dumps(self.config), encoding="utf-8")
        (self.rcs / "audits" / "gates" / "GL_citations.json").write_text(
            json.dumps({"errors": 0, "registry_sha256": hashlib.sha256(reg.read_bytes()).hexdigest()}), encoding="utf-8")

    def collect(self, stage="pre", draft=None):
        return ic.collect(self.rcs, self.root, stage, draft or self.draft)

    def verifier(self, stage="pre", modes=None, verdicts=None, draft=None, **extra):
        """A clean VERIFIER report for the current bundle, then the overrides under test."""
        b = self.collect(stage, draft)
        report = {"draft_sha256": b["draft_sha256"], "round": 1, "isolation": "isolated",
                  "modes": {m: {"status": "CLEAR", "evidence": ["checked"], "detail": ""} for m in ic.MODES},
                  "alignment": [{"row": r["id"], "verdict": "supported", "note": ""} for r in b["alignment_rows"]]}
        for m, status in (modes or {}).items():
            report["modes"][m] = {"status": status, "evidence": ["seen"], "detail": "planted"} if isinstance(status, str) else status
        for a in report["alignment"]:
            a["verdict"] = (verdicts or {}).get(a["row"], a["verdict"])
        report.update(extra)
        (ic.stage_dir(self.rcs, stage) / "verifier_report.json").write_text(json.dumps(report), encoding="utf-8")
        return report

    def gate(self, stage="pre", draft=None):
        return ic.gate(self.rcs, self.root, stage, draft or self.draft)

    def codes(self, rep):
        return {i["code"] for i in rep["items"] if i["level"] == "ERROR"}

    def status(self, rep, m):
        return rep["modes"][m]["status"]


class BlockingTests(Project):
    def test_T080_clean_report_passes(self):
        self.verifier()
        rep = self.gate()
        self.assertEqual(rep["errors"], 0, rep["items"])
        self.assertEqual(rep["stage"], "pre")

    def test_T080_any_suspected_blocks(self):
        for m in ic.MODES:
            self.verifier(modes={m: "SUSPECTED"})
            self.assertIn("INTEGRITY_SUSPECTED", self.codes(self.gate()), m)

    def test_T080_insufficient_at_pre(self):
        for m in ("M1", "M3", "M5", "M6"):
            self.verifier(modes={m: "INSUFFICIENT_EVIDENCE"})
            self.assertIn("INTEGRITY_SUSPECTED", self.codes(self.gate()), m)
        for m in ("M2", "M4", "M7"):
            self.verifier(modes={m: "INSUFFICIENT_EVIDENCE"})
            rep = self.gate()
            self.assertEqual(rep["errors"], 0, m)
            self.assertIn("GI_NOT_LISTED", {i["code"] for i in rep["items"]})

    def test_T080_insufficient_at_final_blocks_every_mode(self):
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "paper.md").write_text(ic.strip_tags(DRAFT), encoding="utf-8")
        self.verifier("final", modes={"M4": "INSUFFICIENT_EVIDENCE"})
        self.assertIn("INTEGRITY_SUSPECTED", self.codes(self.gate("final")))


class VerifierLimitTests(Project):
    def test_T081_clear_needs_evidence(self):
        self.verifier(modes={"M4": {"status": "CLEAR", "evidence": []}})
        rep = self.gate()
        self.assertIn("GI_CLEAR_WITHOUT_EVIDENCE", self.codes(rep))
        self.assertEqual(self.status(rep, "M4"), "INSUFFICIENT_EVIDENCE")

    def test_T081_a_tool_finding_overrides_clear(self):
        self.evidence[0]["strength"] = "soft"
        self.save()
        self.verifier()
        rep = self.gate()
        self.assertIn("GI_CONTRADICTS_TOOL", self.codes(rep))
        self.assertEqual(self.status(rep, "M3"), "SUSPECTED")

    def test_T081_failed_gl_cannot_be_cleared(self):
        (self.rcs / "audits" / "gates" / "GL_citations.json").write_text('{"errors": 2}', encoding="utf-8")
        self.verifier()
        self.assertEqual(self.status(self.gate(), "M2"), "SUSPECTED")

    def test_T081_report_on_another_draft(self):
        self.verifier(draft_sha256="0" * 64)
        self.assertIn("GI_REPORT_STALE", self.codes(self.gate()))

    def test_T081_missing_verifier_or_bundle(self):
        self.collect()
        self.assertIn("GI_NO_VERIFIER", self.codes(self.gate()))
        shutil.rmtree(ic.stage_dir(self.rcs, "pre"))
        self.assertIn("GI_BUNDLE_STALE", self.codes(self.gate()))

    def test_T081_changed_draft_makes_the_bundle_stale(self):
        self.verifier()
        self.draft.write_text(DRAFT + "\nA late sentence.\n", encoding="utf-8")
        codes = self.codes(self.gate())
        self.assertIn("GI_BUNDLE_STALE", codes)
        self.assertIn("GI_REPORT_STALE", codes)

    def test_T081_every_mode_needs_a_status(self):
        r = self.verifier()
        del r["modes"]["M7"]
        (ic.stage_dir(self.rcs, "pre") / "verifier_report.json").write_text(json.dumps(r), encoding="utf-8")
        self.assertIn("GI_MODE_MISSING", self.codes(self.gate()))

    def test_T081_isolation_must_be_stated(self):
        self.verifier(isolation="maybe")
        self.assertIn("GI_ISOLATION", self.codes(self.gate()))


class AlignmentTests(Project):
    def long_draft(self, n=40):
        lines = ["# Paper", "", "## Related work", ""]
        lines += [f"Prior work reported something useful (Smith, 2021) {{C003}}." for _ in range(n)]
        p = self.rcs / "drafts" / "v001" / "long.md"
        p.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
        return p

    def test_T082_high_impact_is_always_selected(self):
        rows = self.collect()["alignment_rows"]
        self.assertEqual([r["tier"] for r in rows], ["high_impact"])
        self.assertIn("spine", rows[0]["impact"])

    def test_T082_sample_replays_exactly(self):
        (self.rcs / "story" / "spine.md").write_text("1. Problem\n", encoding="utf-8")
        d = self.long_draft()
        a = [r["id"] for r in self.collect(draft=d)["alignment_rows"]]
        b = [r["id"] for r in self.collect(draft=d)["alignment_rows"]]
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4, "10% of 40")

    def test_T082_sentinel_bounds(self):
        (self.rcs / "story" / "spine.md").write_text("1. Problem\n", encoding="utf-8")
        self.assertEqual(len(self.collect(draft=self.long_draft(12))["alignment_rows"]), 3, "at least 3")
        self.assertEqual(len(self.collect(draft=self.long_draft(200))["alignment_rows"]), 10, "at most 10")
        self.assertEqual(len(self.collect(draft=self.long_draft(2))["alignment_rows"]), 2, "never more than exist")

    def test_T082_final_checks_every_cited_sentence(self):
        (self.rcs / "story" / "spine.md").write_text("1. Problem\n", encoding="utf-8")
        self.assertEqual(len(self.collect("final", self.long_draft(40))["alignment_rows"]), 40)

    def test_T082_overstated_and_unsupported_make_m2_suspected(self):
        for verdict in ("overstated", "unsupported"):
            self.verifier(verdicts={"A001": verdict})
            rep = self.gate()
            self.assertEqual(self.status(rep, "M2"), "SUSPECTED", verdict)
            self.assertIn("INTEGRITY_SUSPECTED", self.codes(rep))

    def test_T082_understated_must_be_fixed(self):
        self.verifier(verdicts={"A001": "understated"})
        self.assertIn("GI_ALIGNMENT_UNDERSTATED", self.codes(self.gate()))

    def test_T082_not_checkable_on_high_impact_is_insufficient(self):
        self.verifier(verdicts={"A001": "not_checkable"})
        self.assertEqual(self.status(self.gate(), "M2"), "INSUFFICIENT_EVIDENCE")

    def test_T082_every_selected_row_needs_a_verdict(self):
        self.verifier(alignment=[])
        self.assertIn("GI_ROW_NOT_JUDGED", self.codes(self.gate()))

    def test_T082_a_failed_sentinel_widens_to_its_section(self):
        (self.rcs / "story" / "spine.md").write_text("1. Problem\n", encoding="utf-8")
        d = self.long_draft(40)
        b = self.collect(draft=d)
        first = b["alignment_rows"][0]["id"]
        self.verifier(verdicts={first: "unsupported"}, draft=d)
        rep = self.gate(draft=d)
        missing = [i for i in rep["items"] if i["code"] == "GI_ROW_NOT_JUDGED"]
        self.assertEqual(len(missing), 40 - 4, "every other cited sentence in that section must now be judged")


class NoExperimentTests(Project):
    def theory(self):
        self.config["no_experiments"] = True
        self.claims = [self.claims[2], {"id": "C004", "statement": "The bound holds.", "claim_type": "derived", "evidence": [], "basis": "project_file"}]
        self.save()
        self.draft.write_text("# Theory\n\n## Argument\n\nDegradation is known (Smith, 2021) {C003}.\n", encoding="utf-8")

    def test_T083_declared_paper_is_exempt(self):
        self.theory()
        self.verifier(modes={m: "INSUFFICIENT_EVIDENCE" for m in ("M1", "M3", "M5", "M6")})
        self.assertEqual(self.gate()["errors"], 0)

    def test_T083_contradiction_voids_the_exemption(self):
        self.config["no_experiments"] = True
        self.save()
        self.verifier(modes={m: "INSUFFICIENT_EVIDENCE" for m in ("M1", "M5")})
        rep = self.gate()
        self.assertEqual(self.status(rep, "M3"), "SUSPECTED")
        self.assertEqual(self.status(rep, "M6"), "SUSPECTED")
        self.assertIn("GI_DECLARATION_CONTRADICTED", {i["code"] for i in rep["items"]})
        self.assertIn("INTEGRITY_SUSPECTED", self.codes(rep))

    def test_T083_contradiction_seen_in_prose(self):
        self.theory()
        self.draft.write_text(DRAFT.replace(" {C001}", "").replace(" {C002}", ""), encoding="utf-8")
        self.assertTrue(ic.declaration_contradicted(ic.load_project(self.rcs, self.root, self.draft.read_text(encoding="utf-8"))))


class DecisionTests(Project):
    def answered(self, answer="We accept this: the seeds were lost in a disk failure.", by="Dr Example", listed=True):
        wg.ask(self.rcs, "Q-012", "M5 is suspected", [], [], "")
        if by:
            wg.answer(self.rcs, "Q-012", answer, by)
        (ic.stage_dir(self.rcs, "pre") / "decisions.json").write_text(json.dumps({"decisions": [{"mode": "M5", "checkpoint": "Q-012"}]}), encoding="utf-8")
        (self.rcs / "open_issues.md").write_text("- Q-012 M5 proceeds by decision\n" if listed else "nothing\n", encoding="utf-8")

    def test_T084_a_named_decision_unblocks_but_keeps_the_status(self):
        self.verifier(modes={"M5": "SUSPECTED"})
        self.answered()
        rep = self.gate()
        self.assertEqual(rep["errors"], 0, rep["items"])
        self.assertEqual(self.status(rep, "M5"), "SUSPECTED")
        self.assertEqual(rep["decisions"]["M5"]["by"], "Dr Example")

    def test_T084_unanswered(self):
        self.verifier(modes={"M5": "SUSPECTED"})
        self.answered(by=None)
        self.assertIn("GI_DECISION_UNANSWERED", self.codes(self.gate()))

    def test_T084_needs_a_reason(self):
        self.verifier(modes={"M5": "SUSPECTED"})
        self.answered(answer="ok")
        self.assertIn("GI_DECISION_NO_REASON", self.codes(self.gate()))

    def test_T084_must_be_listed(self):
        self.verifier(modes={"M5": "SUSPECTED"})
        self.answered(listed=False)
        self.assertIn("GI_DECISION_NOT_LISTED", self.codes(self.gate()))

    def test_T084_round_cap(self):
        self.verifier(modes={"M5": "SUSPECTED"}, round=4)
        self.assertIn("GI_ROUND_CAP", self.codes(self.gate()))


class FinalStageTests(Project):
    def setUp(self):
        super().setUp()
        (self.root / "paper").mkdir()
        (self.root / "paper" / "paper.md").write_text(ic.strip_tags(DRAFT), encoding="utf-8")

    def test_T085_clean_final(self):
        self.verifier("final")
        rep = self.gate("final")
        self.assertEqual(rep["errors"], 0, rep["items"])
        self.assertEqual(rep["stage"], "final")

    def test_T085_paper_must_match_the_checked_draft(self):
        (self.root / "paper" / "paper.md").write_text(ic.strip_tags(DRAFT) + "\nAn extra sentence.\n", encoding="utf-8")
        self.verifier("final")
        self.assertIn("GI_PAPER_MISMATCH", self.codes(self.gate("final")))

    def test_T085_pre_stage_suspicion_must_be_resolved(self):
        d = ic.stage_dir(self.rcs, "pre")
        d.mkdir(parents=True)
        (d / "report.json").write_text(json.dumps({"modes": {"M5": {"status": "SUSPECTED"}}}), encoding="utf-8")
        self.verifier("final", modes={"M5": "SUSPECTED"})
        self.assertIn("GI_PRE_UNRESOLVED", self.codes(self.gate("final")))
        self.verifier("final")
        self.assertNotIn("GI_PRE_UNRESOLVED", self.codes(self.gate("final")))

    def test_T085_old_retraction_check_fails(self):
        self.sources[0]["retraction"]["checked_at"] = "2020-01-01"
        self.save()
        self.verifier("final")
        self.assertIn("GI_RETRACTION_STALE", self.codes(self.gate("final")))

    def test_T085_cli_writes_gate_and_stage_reports(self):
        self.verifier("final")
        out = self.rcs / "audits" / "gates" / "GI_integrity.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = ic.main(["gate", str(self.rcs), "--stage", "final", "--draft", str(self.draft), "--project-root", str(self.root), "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["stage"], "final")
        self.assertTrue((ic.stage_dir(self.rcs, "final") / "report.json").exists())


class RoleTests(Project):
    def test_T086_report_must_be_the_verifiers(self):
        self.verifier()
        path = ic.stage_dir(self.rcs, "pre") / "verifier_report.json"
        wg.record(self.rcs, "AUTHOR", [str(self.draft)])
        self.assertIn("GI_NOT_VERIFIER", self.codes(self.gate()))
        wg.record(self.rcs, "VERIFIER", [str(path)])
        self.assertNotIn("GI_NOT_VERIFIER", self.codes(self.gate()))

    def test_T086_author_may_not_write_integrity_verdicts(self):
        self.assertFalse(wg.allowed("AUTHOR", "audits/integrity/pre/verifier_report.json"))
        self.assertTrue(wg.allowed("AUTHOR", "audits/v001/lint.json"))
        self.assertTrue(wg.allowed("VERIFIER", "audits/integrity/pre/verifier_report.json"))
        self.assertFalse(wg.allowed("VERIFIER", "drafts/v001/paper.md"))
        self.assertTrue(wg.allowed("PANEL", "diagnostics/v001_1/panel/methodology.json"))


class EvidenceTests(Project):
    def det(self, draft=None):
        md = (draft or DRAFT)
        return ic.deterministic(ic.load_project(self.rcs, self.root, md))

    def codes_in(self, mode, key="signals", draft=None):
        return {x["code"] for x in self.det(draft)[mode][key]}

    def test_T087_clean_project_has_no_errors(self):
        self.assertEqual({m: d["errors"] for m, d in self.det().items() if d["errors"]}, {})

    def test_T087_m1(self):
        self.evidence[0]["value"]["std"] = 0
        self.evidence[0]["locator"]["path"] = "results/gone.csv"
        self.save()
        self.assertTrue({"NO_RUN_RECORD", "ZERO_VARIANCE"} <= self.codes_in("M1"))

    def test_T087_m2_unregistered_and_stale(self):
        self.assertIn("CITATION_UNREGISTERED", self.codes_in("M2", "errors", DRAFT + "\nOthers differ (Jones, 2020).\n"))
        (self.rcs / "corpus" / "source_registry.json").write_text('{"sources": []}', encoding="utf-8")
        self.assertIn("GL_STALE", self.codes_in("M2", "errors"))

    def test_T087_m3_run_count(self):
        self.assertIn("RUN_COUNT_UNMATCHED", self.codes_in("M3", draft=DRAFT.replace("5 seeds", "9 seeds")))

    def test_T087_m3_p_value(self):
        self.assertIn("UNTRACED_PVALUE", self.codes_in("M3", "errors", DRAFT + "\nThe drop was significant (p < 0.01) {C001}.\n"))

    def test_T087_m4(self):
        self.evidence[1]["notes"] = "the baseline was left untuned"
        self.evidence[1]["kind"] = "baseline"
        self.claims[0]["statement"] = "Ours outperforms the baseline."
        self.save()
        self.assertTrue({"SHORTCUT_NOTE", "UNMATCHED_COMPARISON"} <= self.codes_in("M4"))

    def test_T087_m5(self):
        self.evidence[0]["value"]["n"] = 1
        self.save()
        self.assertIn("UNEXAMINED_SURPRISE", self.codes_in("M5", draft=DRAFT + "\nSurprisingly, the error fell to 0.42 {C001}.\n"))

    def test_T087_m6(self):
        self.claims[1]["basis"] = "none"
        self.save()
        self.assertIn("METHOD_WITHOUT_BASIS", self.codes_in("M6", "errors"))

    def test_T087_m7(self):
        (self.rcs / "story" / "alternatives.md").write_text("# Alternatives\n", encoding="utf-8")
        self.assertIn("NO_ALTERNATIVES", self.codes_in("M7"))
        (self.rcs / "story" / "spine.md").write_text("v1\n", encoding="utf-8")
        wg.record(self.rcs, "AUTHOR", [str(self.rcs / "story" / "spine.md")])
        (self.rcs / "story" / "spine.md").write_text("v2\n", encoding="utf-8")
        wg.record(self.rcs, "AUTHOR", [str(self.rcs / "story" / "spine.md")])
        self.assertIn("SILENT_SPINE_CHANGE", self.codes_in("M7"))


if __name__ == "__main__":
    unittest.main()
