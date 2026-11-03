"""Regression tests for proposal 20261102-unified-workflow, Stage C: schemas, the panel, the VERIFIER, G4 with a panel.

T-094  schemas: the registry extension is additive (v0.4 and demo registries still validate, Stage B output validates);
       new schemas reject what they should; a local $ref is enforced by the stdlib validator, not silently skipped
T-095  the VERIFIER report is schema-checked by GI; the bundle carries the rows a failed sentinel widens to
T-096  rce_roles.py panel: commitments never see the paper; reviews are stamped with their commitment's hash and the packet
       id by the tool; the ledger records PANEL; panel_check agrees
T-097  a synthesizer that states the wrong decision, or cites a finding no seat made, is sent back until it complies
T-098  panel_check catches: a missing seat, a commitment changed after the review, an uncommitted or unjudged criterion,
       "fails" without a finding, a wrong id prefix, an invented roadmap finding, an uncovered blocking finding, a downgrade
       quote not in the paper, and a decision the findings do not give
T-099  the decision rule and the rebuttal rule, case by case
T-100  G4 with a panel: standing major or fatal findings need dispositions; a declined devil's-advocate finding needs a
       rebuttal that takes it out of blocking (and a 4 right after a concession counts as 3); a Reject needs a named
       person's answered checkpoint; paper mode without a panel fails; legacy projects are unaffected; a third round fails
T-101  a re-review keeps the same cards and checks every roadmap item
T-102  rce_roles.py rebut scores in order and writes the seat's file
T-103  rce_roles.py verify: the tool sets the draft hash and isolation, records VERIFIER, and the report passes GI
T-104  every prompt, adapter and template the docs name exists; new roles are bound in the models template; artifacts are
       schema-validated by validate_artifacts

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import g4_check  # noqa: E402
import integrity_check as ic  # noqa: E402
import panel_check as pc  # noqa: E402
import rce_llm  # noqa: E402
import rce_roles  # noqa: E402
import validate_artifacts as va  # noqa: E402
import workflow_guard as wg  # noqa: E402
from rce_common import SKILL_DIR, load_schema, validate  # noqa: E402

PAPER = "# Normalization under shift\n\n## Results\n\nThe error fell to 0.42 under shift, across five seeds.\n\nSENTINEL-PAPER-TEXT\n"
CARDS = {"field": "machine learning", "subfield": "forecasting", "venue": "Test Venue", "article_type": "empirical",
         "criteria_source": "paper type and the rubric",
         "cards": [{"seat": s, "criteria": [{"id": f"{pc.PREFIX[s]}1", "criterion": f"{s} criterion one"}], "serious_failure": "a failure"}
                   for s in pc.SEATS]}


def loc():
    return {"section": "Results", "quote": "The error fell to 0.42"}


def finding(seat, n, severity, crit=None):
    p = pc.PREFIX[seat]
    return {"id": f"{p}-{n}", "criterion_id": crit or f"{p}1", "severity": severity, "location": loc(),
            "problem": "a planted problem here", "why_it_matters": "it matters", "repair_goal": "fix the thing"}


class PanelModel:
    """A fake model for every panel member: answers by phase and seat, and records what each call was shown."""

    def __init__(self, findings=None, decision=None, judgement="meets", checks=None):
        self.findings = findings or {"methodology": [finding("methodology", 1, "major")], "devils_advocate": [finding("devils_advocate", 1, "minor")]}
        self.decision = decision
        self.judgement = judgement
        self.checks = checks
        self.calls = []
        self.synth_replies = []

    def seat_of(self, system):
        m = re.search(r"\(prefix ([A-Z]{2})\)", system)
        return next((s for s, p in pc.PREFIX.items() if m and p == m.group(1)), None)

    def __call__(self, system, user):
        seat = self.seat_of(system)
        phase = "cards" if "reviewer_cards.schema.json" in user[:200] else "1" if "# PHASE 1" in user else "2" if "# PHASE 2" in user \
            else "3" if "# PHASE 3" in user else "synth"
        self.calls.append({"seat": seat, "phase": phase, "user": user})
        if phase == "cards":
            return json.dumps(CARDS)
        crit = f"{pc.PREFIX.get(seat, 'XX')}1"
        if phase == "1":
            return json.dumps({"seat": seat, "phase": "commitment", "plan": [{"criterion_id": crit, "how_judged": "look closely", "fails_when": "it is absent"}]})
        if phase == "2":
            fs = self.findings.get(seat, [])
            j = "partly" if fs else self.judgement
            return json.dumps({"seat": seat, "phase": "review", "criteria": [{"criterion_id": crit, "judgement": j, "location": loc()}], "findings": fs})
        if phase == "3":
            return json.dumps({"seat": seat, "phase": "verification", "checks": self.checks or [], "findings": []})
        if self.synth_replies:
            return json.dumps(self.synth_replies.pop(0))
        return json.dumps(self.decision)


def standard_decision(kind="full", decision="major"):
    return {"kind": kind, "decision": decision, "basis": "ME-1 is major", "roadmap": [
        {"id": "R-1", "from_findings": ["ME-1"], "priority": "blocking", "goal": "repair the design"},
        {"id": "R-2", "from_findings": ["DA-1"], "priority": "optional", "goal": "address the alternative"}]}


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        rce_llm.MOCK_REPLIES.clear()
        self.addCleanup(rce_llm.MOCK_REPLIES.clear)
        self.root = self.tmp
        self.rcs = self.tmp / ".rcs"
        (self.rcs / "drafts" / "v001").mkdir(parents=True)
        (self.rcs / "models.json").write_text(json.dumps({"roles": {"PANEL": {"provider": "mock"}, "VERIFIER": {"provider": "mock"}},
                                                          "keep_transcripts": False}), encoding="utf-8")
        self.draft = self.rcs / "drafts" / "v001" / "paper.md"
        self.draft.write_text(PAPER, encoding="utf-8")
        self.packet("v001_1")

    def packet(self, rnd, paper=PAPER):
        pk = self.rcs / "packets" / f"review_{rnd}"
        pk.mkdir(parents=True, exist_ok=True)
        (pk / "paper.md").write_text(paper, encoding="utf-8")
        (pk / "audience.md").write_text("adjacent researchers", encoding="utf-8")
        (pk / "objective.md").write_text("show the method helps", encoding="utf-8")
        (pk / "packet_manifest.json").write_text(json.dumps({"packet_id": f"pkt-{rnd}", "source_paper": ".rcs/drafts/v001/paper.md",
                                                             "source_sha256": hashlib.sha256(self.draft.read_bytes()).hexdigest()}), encoding="utf-8")
        return pk

    def run_panel(self, model, rnd="v001_1", verify_from=None):
        rce_llm.MOCK_REPLIES["PANEL"] = [model] * 40
        with contextlib.redirect_stdout(io.StringIO()):
            return rce_roles.panel_round(rce_llm.load_config(self.rcs), self.rcs, rnd, self.rcs / "packets" / f"review_{rnd}", verify_from)

    def panel_files(self, rnd="v001_1"):
        return self.rcs / "diagnostics" / rnd / "panel"

    def codes(self, rnd="v001_1"):
        return {c for _, c, _ in pc.check_round(self.rcs, rnd, f"pkt-{rnd}")[0]}


class SchemaTests(unittest.TestCase):
    def reg_schema(self):
        return load_schema("source_registry.schema.json")

    def test_T094_demo_registry_and_v04_still_validate(self):
        demo = SKILL_DIR / "examples" / "demo_project" / ".rcs"
        rep = va.Report()
        va.check_schemas(demo, rep)
        self.assertEqual([i for i in rep.items if i["level"] == "ERROR"], [])
        v04 = {"sources": [{"id": "SRC-001", "title": "T", "authors": ["A"], "year": 2020, "publication_status": "PEER-REVIEWED", "level": 2,
                            "verification": {"method": "doi_lookup", "date": "2026-01-01"}, "read_depth": "full", "permitted_use": ["content_citation"]}]}
        self.assertEqual(validate(v04, self.reg_schema()), [])

    def test_T094_stage_b_output_validates(self):
        import verify_citations as vc
        res = {"lookup_verified": True, "code": None, "indexes": [{"index": "crossref", "status": "found", "match_score": 1.0},
                                                                  {"index": "semantic_scholar", "status": "skipped", "match_score": None, "reason": "rate limited (429)"}],
               "retraction": {"status": "not_retracted", "checked_at": "2026-11-02", "source": "crossref", "observations": [{"source": "crossref", "retracted": False}]},
               "flags": ["preprint"], "conflicts": [{"field": "year", "values": {"crossref": 2021, "openalex": 2022}, "minor": True}],
               "matched": [{"index": "crossref", "title": "T", "authors": ["Smith, A"], "year": 2021, "venue": "J", "type": "journal-article"}],
               "records": [], "suggestion": {"index": "crossref", "doi": "10.1000/x", "title": "T", "year": 2021}, "doi": "10.1000/x", "arxiv_id": "2401.01234"}
        src = vc.register({"id": "CAND-0001", "title": "T", "as_cited": "T"}, res, [])
        self.assertEqual(validate({"sources": [src]}, self.reg_schema()), [])

    def test_T094_registry_rejects_bad_values(self):
        base = {"id": "SRC-001", "title": "T", "authors": ["A"], "year": 2020, "publication_status": "PEER-REVIEWED", "level": 2,
                "read_depth": "full", "permitted_use": ["content_citation"]}
        for extra, needle in (({"verification": {"method": "doi_lookup", "date": "2026-01-01", "lookup_verified": "maybe"}}, "lookup_verified"),
                              ({"verification": {"method": "doi_lookup", "date": "2026-01-01", "indexes": [{"index": "crossref", "status": "missing"}]}}, "status"),
                              ({"retraction": {"status": "probably", "checked_at": "2026-01-01"}}, "retraction"),
                              ({"flags": ["looks_fine"]}, "flags")):
            s = {**base, "verification": {"method": "doi_lookup", "date": "2026-01-01"}, **extra}
            errs = validate({"sources": [s]}, self.reg_schema())
            self.assertTrue(any(needle in e for e in errs), (needle, errs))

    def test_T094_ref_is_enforced(self):
        errs = validate({"seat": "domain", "phase": "review", "findings": [{"id": "DO-1"}]}, load_schema("panel_review.schema.json"))
        self.assertTrue(any("severity" in e for e in errs), errs)

    def test_T094_new_schemas_reject(self):
        self.assertTrue(validate({"mode": "novel"}, load_schema("paper_config.schema.json")))
        self.assertTrue(validate({"candidates": [{"id": "C1", "found_by": ["memory:x"], "decision": "keep"}]}, load_schema("candidates.schema.json")))
        self.assertTrue(validate({"kind": "full", "decision": "maybe", "roadmap": []}, load_schema("editorial_decision.schema.json")))
        self.assertTrue(validate({"field": "x", "article_type": "y", "cards": []}, load_schema("reviewer_cards.schema.json")))
        report = {"draft_sha256": "0" * 64, "round": 1, "isolation": "isolated", "modes": {"M1": {"status": "CLEAR", "evidence": ["x" * 4]}}, "alignment": []}
        self.assertTrue(any("M7" in e for e in validate(report, load_schema("integrity_report.schema.json"))))

    def test_T094_templates_validate(self):
        cfg = json.loads((SKILL_DIR / "templates" / "paper_config.json").read_text(encoding="utf-8"))
        cfg = {k: v for k, v in cfg.items() if not k.startswith("_")}
        cfg["venue"] = None
        self.assertEqual(validate(cfg, load_schema("paper_config.schema.json")), [])


class VerifierReportTests(Project):
    def test_T095_bundle_has_unselected_rows(self):
        (self.rcs / "corpus").mkdir()
        (self.rcs / "corpus" / "source_registry.json").write_text(json.dumps({"sources": [{"id": "SRC-001", "authors": ["Smith, A"], "year": 2021}]}), encoding="utf-8")
        md = "# P\n\n## Related\n\n" + "\n\n".join("Work exists (Smith, 2021)." for _ in range(30)) + "\n"
        self.draft.write_text(md, encoding="utf-8")
        b = ic.collect(self.rcs, self.root, "pre", self.draft)
        self.assertEqual(len(b["alignment_rows"]) + len(b["unselected_rows"]), 30)

    def test_T095_invalid_report_fails_gi(self):
        ic.collect(self.rcs, self.root, "pre", self.draft)
        (ic.stage_dir(self.rcs, "pre") / "verifier_report.json").write_text(json.dumps({"draft_sha256": "x", "modes": {}}), encoding="utf-8")
        codes = {i["code"] for i in ic.gate(self.rcs, self.root, "pre", self.draft)["items"]}
        self.assertIn("GI_REPORT_INVALID", codes)


class PanelRunTests(Project):
    def test_T096_full_round(self):
        model = PanelModel(decision=standard_decision())
        res = self.run_panel(model)
        self.assertEqual(res["decision"], "major")
        self.assertEqual(res["problems"], [])
        self.assertEqual(res["blocking"], ["ME-1"])
        self.assertEqual(self.codes(), set())

    def test_T096_commitments_never_see_the_paper(self):
        model = PanelModel(decision=standard_decision())
        self.run_panel(model)
        commitments = [c for c in model.calls if c["phase"] == "1"]
        self.assertEqual(len(commitments), 5)
        for c in commitments:
            self.assertNotIn("SENTINEL-PAPER-TEXT", c["user"])
            self.assertNotIn("0.42", c["user"])
        self.assertTrue(all("SENTINEL-PAPER-TEXT" in c["user"] for c in model.calls if c["phase"] == "2"))
        order = [c["phase"] for c in model.calls]
        self.assertEqual(order[0], "cards")
        self.assertEqual(order[-1], "synth")

    def test_T096_tool_stamps_hash_and_packet(self):
        self.run_panel(PanelModel(decision=standard_decision()))
        d = self.panel_files()
        for seat in pc.SEATS:
            r = json.loads((d / f"{seat}.review.json").read_text(encoding="utf-8"))
            self.assertEqual(r["commitment_sha256"], pc.sha_file(d / f"{seat}.commitment.json"))
            self.assertEqual(r["packet_id"], "pkt-v001_1")

    def test_T096_ledger_records_panel(self):
        (self.rcs / "provenance.jsonl").write_text("", encoding="utf-8")
        self.run_panel(PanelModel(decision=standard_decision()))
        roles = {r["role"] for r in wg.load_ledger(self.rcs)}
        self.assertEqual(roles, {"PANEL"})
        self.assertTrue(any(r["path"].endswith("editorial_decision.json") for r in wg.load_ledger(self.rcs)))

    def test_T097_wrong_decision_is_sent_back(self):
        model = PanelModel(decision=standard_decision())
        model.synth_replies = [standard_decision(decision="minor")]
        res = self.run_panel(model)
        self.assertEqual(res["decision"], "major")
        synth = [c for c in model.calls if c["phase"] == "synth"]
        self.assertEqual(len(synth), 2)
        self.assertIn("give 'major'", synth[1]["user"])

    def test_T097_invented_finding_is_sent_back(self):
        model = PanelModel(decision=standard_decision())
        bad = standard_decision()
        bad["roadmap"].append({"id": "R-3", "from_findings": ["ME-9"], "priority": "optional", "goal": "something new"})
        model.synth_replies = [bad]
        self.run_panel(model)
        self.assertIn("ME-9, which no seat reported", [c for c in model.calls if c["phase"] == "synth"][1]["user"])

    def test_T097_unfixable_synthesizer_fails_loudly(self):
        model = PanelModel(decision=standard_decision(decision="accept"))
        with self.assertRaises(rce_llm.LLMError):
            self.run_panel(model)


class PanelCheckTests(Project):
    def setUp(self):
        super().setUp()
        self.run_panel(PanelModel(decision=standard_decision()))
        self.d = self.panel_files()

    def edit(self, name, fn):
        p = self.d / name if not name.startswith("..") else self.d.parent / name[3:]
        obj = json.loads(p.read_text(encoding="utf-8"))
        fn(obj)
        p.write_text(json.dumps(obj), encoding="utf-8")

    def test_T098_missing_seat(self):
        (self.d / "perspective.review.json").unlink()
        self.assertIn("PANEL_SHRUNK", self.codes())

    def test_T098_commitment_changed_after_review(self):
        self.edit("methodology.commitment.json", lambda o: o["plan"][0].update(how_judged="rewritten after reading"))
        self.assertIn("PANEL_COMMITMENT_MISMATCH", self.codes())

    def test_T098_criterion_not_committed_or_not_judged(self):
        def add(o):
            o["cards"][1]["criteria"].append({"id": "ME2", "criterion": "a second criterion"})
        self.edit("cards.json", add)
        self.assertIn("PANEL_COMMITMENT_INCOMPLETE", self.codes())
        self.edit("domain.review.json", lambda o: o["criteria"].clear())
        self.assertIn("PANEL_CRITERION_UNJUDGED", self.codes())

    def test_T098_fails_without_finding(self):
        self.edit("domain.review.json", lambda o: o["criteria"][0].update(judgement="fails"))
        self.assertIn("PANEL_FAILS_WITHOUT_FINDING", self.codes())

    def test_T098_wrong_prefix(self):
        self.edit("domain.review.json", lambda o: o["findings"].append(finding("methodology", 7, "minor", crit="DO1")))
        self.assertIn("PANEL_FINDING_ID", self.codes())

    def test_T098_invented_or_uncovered(self):
        self.edit("../editorial_decision.json", lambda o: o["roadmap"][1].update(from_findings=["DA-9"]))
        self.assertIn("PANEL_INVENTED_FINDING", self.codes())
        self.edit("../editorial_decision.json", lambda o: o["roadmap"][0].update(priority="optional"))
        self.assertIn("PANEL_ROADMAP_INCOMPLETE", self.codes())

    def test_T098_downgrade_needs_a_real_quote(self):
        def down(o, quote):
            o["downgrades"] = [{"finding_id": "ME-1", "to": "minor", "quote": quote}]
            o["decision"] = "minor"
            o["roadmap"][0]["priority"] = "optional"
        self.edit("../editorial_decision.json", lambda o: down(o, "a sentence the paper never says"))
        self.assertIn("PANEL_DOWNGRADE_UNQUOTED", self.codes())
        self.edit("../editorial_decision.json", lambda o: down(o, "The error fell to 0.42 under shift"))
        self.assertEqual(self.codes(), set())

    def test_T098_decision_mismatch(self):
        self.edit("../editorial_decision.json", lambda o: o.update(decision="accept"))
        self.assertIn("PANEL_DECISION_MISMATCH", self.codes())


class RuleTests(unittest.TestCase):
    def test_T099_full_decisions(self):
        self.assertEqual(pc.derive_full({"A": "fatal", "B": "minor"}, ["meets"]), "reject")
        self.assertEqual(pc.derive_full({"A": "major"}, ["meets"]), "major")
        self.assertEqual(pc.derive_full({"A": "minor"}, ["meets"]), "minor")
        self.assertEqual(pc.derive_full({}, ["meets", "not_assessed"]), "minor", "silence is not acceptance")
        self.assertEqual(pc.derive_full({}, ["meets", "meets"]), "accept")
        self.assertEqual(pc.derive_full({"A": "withdrawn"}, ["meets"]), "accept")

    def test_T099_verification_decisions(self):
        rm = [{"id": "R-1", "priority": "blocking"}, {"id": "R-2", "priority": "optional"}]
        self.assertEqual(pc.derive_verification(rm, {"R-1": "addressed", "R-2": "addressed"}, {}), "accept")
        self.assertEqual(pc.derive_verification(rm, {"R-1": "addressed", "R-2": "partly"}, {}), "minor")
        self.assertEqual(pc.derive_verification(rm, {"R-1": "worsened", "R-2": "addressed"}, {}), "major")
        self.assertEqual(pc.derive_verification(rm, {"R-1": "addressed", "R-2": "addressed"}, {"ME-3": "major"}), "major")
        self.assertEqual(pc.derive_verification(rm, {"R-2": "addressed"}, {}), "major", "an unchecked blocking item counts as not addressed")

    def test_T099_rebuttal_rule(self):
        self.assertEqual(pc.rebuttal_outcomes([{"finding_id": "DA-1", "score": 4}, {"finding_id": "DA-2", "score": 4}]), {"DA-1": 4, "DA-2": 3})
        self.assertEqual(pc.rebuttal_outcomes([{"finding_id": "DA-1", "score": 5}, {"finding_id": "DA-2", "score": 5}]), {"DA-1": 5, "DA-2": 5})
        self.assertEqual(pc.rebuttal_outcomes([{"finding_id": "DA-1", "score": 2}, {"finding_id": "DA-2", "score": 4}]), {"DA-1": 2, "DA-2": 4})

    def test_T099_effective_severity(self):
        f = {"DA-1": {"severity": "major"}, "ME-1": {"severity": "fatal"}}
        self.assertEqual(pc.effective(f, {"downgrades": [{"finding_id": "ME-1", "to": "major"}]}, {"DA-1": 4}), {"DA-1": "minor", "ME-1": "major"})
        self.assertEqual(pc.effective(f, {"downgrades": [{"finding_id": "ME-1", "to": "fatal"}]}, {"DA-1": 5}), {"DA-1": "withdrawn", "ME-1": "fatal"},
                         "a 'downgrade' that raises severity is ignored")


class G4PanelTests(Project):
    def g4(self, rnd="v001_1"):
        return {i["code"]: i["message"] for i in g4_check.check(self.rcs, rnd, None)["items"]}

    def setUp(self):
        super().setUp()
        dims = ["problem", "motivation", "research_question", "contribution", "method", "experiment", "result", "interpretation",
                "limitation", "narrative_coherence", "terminology", "logical_flow", "evidence_traceability", "figure_table",
                "claim_evidence_alignment", "unsupported_inference", "redundancy", "cognitive_load", "orientation", "so_what"]
        diag = {"packet_id": "pkt-v001_1", "binding_personas": ["B"], "inference_issues": [], "injection_suspected": [],
                "findings": [{"dimension": d, "score": 4, "persona": ["B"], "location": {"section": "Results"}, "observed": "fine enough",
                              "reader_struggle": "", "likely_consequence": "", "revision_principle": ""} for d in dims]}
        dd = self.rcs / "diagnostics" / "v001_1"
        dd.mkdir(parents=True, exist_ok=True)
        (dd / "diagnostics.json").write_text(json.dumps(diag), encoding="utf-8")

    def dispositions(self, items, **extra):
        p = self.rcs / "revisions" / "v001_1"
        p.mkdir(parents=True, exist_ok=True)
        (p / "dispositions.json").write_text(json.dumps({"items": items, **extra}), encoding="utf-8")

    def test_T100_legacy_project_needs_no_panel(self):
        self.assertEqual(self.g4(), {})

    def test_T100_paper_mode_needs_a_panel(self):
        (self.rcs / "state.json").write_text(json.dumps({"mode": "paper"}), encoding="utf-8")
        self.assertIn("PANEL_MISSING", self.g4())

    def test_T100_blocking_findings_need_dispositions(self):
        self.run_panel(PanelModel(decision=standard_decision()))
        self.assertIn("G4_UNADDRESSED", self.g4())
        self.dispositions([{"item": "panel:ME-1", "disposition": "deferred"}])
        (self.rcs / "open_issues.md").write_text("- panel:ME-1 deferred\n", encoding="utf-8")
        self.assertEqual(self.g4(), {})

    def da_round(self, severity="major"):
        f = {"devils_advocate": [finding("devils_advocate", 1, severity)]}
        dec = {"kind": "full", "decision": "major", "basis": "DA-1", "roadmap": [{"id": "R-1", "from_findings": ["DA-1"], "priority": "blocking", "goal": "rule it out"}]}
        self.run_panel(PanelModel(findings=f, decision=dec))
        self.dispositions([{"item": "panel:DA-1", "disposition": "declined", "reason": "we disagree for stated reasons here"}])

    def scores(self, *pairs):
        (self.panel_files() / "devils_advocate.rebuttal.json").write_text(json.dumps({"seat": "devils_advocate", "phase": "rebuttal", "scores": [
            {"finding_id": f, "score": s, "reason": "scored against the paper"} for f, s in pairs]}), encoding="utf-8")

    def test_T100_declined_da_finding_needs_a_rebuttal(self):
        self.da_round()
        self.assertIn("G4_DA_REBUTTAL", self.g4())
        self.scores(("DA-1", 3))
        self.assertIn("G4_DA_REBUTTAL", self.g4())
        self.scores(("DA-1", 4))
        self.assertEqual(self.g4(), {}, "a 4 lowers major to minor, out of blocking")
        self.scores(("DA-1", 5))
        self.assertEqual(self.g4(), {})

    def test_T100_a_four_after_a_concession_counts_as_three(self):
        self.da_round()
        self.scores(("DA-0", 4), ("DA-1", 4))
        self.assertIn("G4_DA_REBUTTAL", self.g4())

    def test_T100_reject_needs_a_named_decision(self):
        f = {"methodology": [finding("methodology", 1, "fatal")]}
        dec = {"kind": "full", "decision": "reject", "basis": "ME-1 fatal", "roadmap": [{"id": "R-1", "from_findings": ["ME-1"], "priority": "blocking", "goal": "x" * 6}]}
        self.run_panel(PanelModel(findings=f, decision=dec))
        self.dispositions([{"item": "panel:ME-1", "disposition": "author_question", "checkpoint": "Q-001"}], reject_checkpoint="Q-001")
        wg.ask(self.rcs, "Q-001", "The panel rejects. Back to P1, another venue, or stop?", [], [], "")
        self.assertIn("PANEL_REJECT", self.g4())
        wg.answer(self.rcs, "Q-001", "Back to P1: we will redesign the evaluation.", "Dr Example")
        self.assertNotIn("PANEL_REJECT", self.g4())

    def test_T100_third_round_breaks_the_cap(self):
        self.run_panel(PanelModel(decision=standard_decision()))
        for rnd in ("v002_1", "v003_1"):
            d = self.rcs / "diagnostics" / rnd
            d.mkdir(parents=True)
            shutil.copy(self.rcs / "diagnostics" / "v001_1" / "editorial_decision.json", d / "editorial_decision.json")
        self.assertIn("PANEL_CAP", self.g4())

    def test_T100_round_two_uses_the_round_one_reader_and_keeps_unaddressed_items(self):
        """Found in the v0.5 live run: G4 on a panel-only round 2 failed G4_NO_REVIEW, and a blocking roadmap item the seats
        found not addressed needed no disposition."""
        (self.rcs / "state.json").write_text(json.dumps({"mode": "paper"}), encoding="utf-8")
        self.run_panel(PanelModel(decision=standard_decision()))
        self.dispositions([{"item": "panel:ME-1", "disposition": "fixed", "where": "section 3, the new design paragraph"}])
        self.packet("v002_1", PAPER + "\nRevised.\n")
        checks = [{"roadmap_id": "R-1", "verdict": "not_addressed", "location": loc()},
                  {"roadmap_id": "R-2", "verdict": "addressed", "location": loc()}]
        dec = {"kind": "verification", "previous_round": "v001_1", "decision": "major", "basis": "R-1 not addressed",
               "roadmap": [{"id": "R-1", "from_findings": ["ME-1"], "priority": "blocking", "goal": "repair the design"}]}
        self.run_panel(PanelModel(decision=dec, checks=checks), "v002_1", verify_from="v001_1")
        codes = self.g4("v002_1")
        self.assertNotIn("G4_NO_REVIEW", codes)
        self.assertNotIn("PANEL_PACKET_MISMATCH", codes)
        self.assertIn("panel:R-1", codes.get("G4_UNADDRESSED", ""))
        p = self.rcs / "revisions" / "v002_1"
        p.mkdir(parents=True)
        (p / "dispositions.json").write_text(json.dumps({"items": [{"item": "panel:R-1", "disposition": "deferred"}]}), encoding="utf-8")
        (self.rcs / "open_issues.md").write_text("- panel:R-1 still not addressed at the revision cap\n", encoding="utf-8")
        self.assertEqual(self.g4("v002_1"), {})


class VerificationRoundTests(Project):
    def test_T101_rereview(self):
        self.run_panel(PanelModel(decision=standard_decision()))
        self.packet("v002_1", PAPER + "\nA robustness check now rules out chance.\n")
        checks = [{"roadmap_id": "R-1", "verdict": "addressed", "location": loc()}, {"roadmap_id": "R-2", "verdict": "partly", "location": loc()}]
        model = PanelModel(decision={"kind": "verification", "decision": "minor", "basis": "R-2 partly", "roadmap": [
            {"id": "R-1", "from_findings": ["DA-1"], "priority": "optional", "goal": "finish the alternative"}]}, checks=checks)
        res = self.run_panel(model, "v002_1", verify_from="v001_1")
        self.assertEqual(res["decision"], "minor")
        self.assertEqual(res["problems"], [])
        old, new = self.panel_files("v001_1") / "cards.json", self.panel_files("v002_1") / "cards.json"
        self.assertEqual(pc.sha_file(old), pc.sha_file(new))
        self.assertTrue(all(c["phase"] in ("3", "synth") for c in model.calls), "no new cards, no new commitments")
        self.assertTrue(all("R-1" in c["user"] for c in model.calls if c["phase"] == "3"))

    def test_T101_unchecked_item_and_changed_cards(self):
        self.run_panel(PanelModel(decision=standard_decision()))
        self.packet("v002_1")
        model = PanelModel(decision={"kind": "verification", "decision": "major", "basis": "unchecked", "roadmap": []},
                           checks=[{"roadmap_id": "R-2", "verdict": "addressed", "location": loc()}])
        with self.assertRaises(rce_llm.LLMError):          # a seat that skips an item is sent back, and fails after retries
            self.run_panel(model, "v002_1", verify_from="v001_1")


class RebutTests(Project):
    def test_T102_rebut(self):
        f = {"devils_advocate": [finding("devils_advocate", 1, "major"), finding("devils_advocate", 2, "minor")]}
        dec = {"kind": "full", "decision": "major", "basis": "DA-1", "roadmap": [{"id": "R-1", "from_findings": ["DA-1"], "priority": "blocking", "goal": "rule it out"}]}
        self.run_panel(PanelModel(findings=f, decision=dec))
        (self.rcs / "revisions" / "v001_1").mkdir(parents=True)
        (self.rcs / "revisions" / "v001_1" / "rebuttals.json").write_text(json.dumps({"rebuttals": [
            {"finding_id": "DA-2", "text": "Table 3 shows the control"}, {"finding_id": "DA-1", "text": "Section 4 rules it out"}]}), encoding="utf-8")
        seen = []

        def da(system, user):
            seen.append(user)
            return json.dumps({"seat": "devils_advocate", "phase": "rebuttal", "scores": [
                {"finding_id": "DA-2", "score": 4, "reason": "the control is real"}, {"finding_id": "DA-1", "score": 4, "reason": "partly answered"}]})
        rce_llm.MOCK_REPLIES["PANEL"] = [da]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = rce_roles.main(["rebut", "--rcs", str(self.rcs), "--round", "v001_1"])
        self.assertEqual(code, 0)
        self.assertIn("DA-1: counts as 3/5", out.getvalue())
        self.assertIn("Section 4 rules it out", seen[0])
        self.assertTrue((self.panel_files() / "devils_advocate.rebuttal.json").exists())


class VerifyCommandTests(Project):
    def test_T103_verify(self):
        (self.rcs / "provenance.jsonl").write_text("", encoding="utf-8")
        b = ic.collect(self.rcs, self.root, "pre", self.draft)
        seen = []

        def verifier(system, user):
            seen.append((system, user))
            return json.dumps({"draft_sha256": "0" * 64, "round": 9, "isolation": "none",
                               "modes": {m: {"status": "CLEAR", "evidence": ["checked the records"]} for m in ic.MODES}, "alignment": []})
        rce_llm.MOCK_REPLIES["VERIFIER"] = [verifier]
        with contextlib.redirect_stdout(io.StringIO()):
            code = rce_roles.main(["verify", "--rcs", str(self.rcs), "--stage", "pre"])
        self.assertEqual(code, 0)
        report = json.loads((ic.stage_dir(self.rcs, "pre") / "verifier_report.json").read_text(encoding="utf-8"))
        self.assertEqual((report["draft_sha256"], report["round"], report["isolation"]), (b["draft_sha256"], 1, "isolated"))
        self.assertIn("VERIFIER", seen[0][0])
        self.assertIn("SENTINEL-PAPER-TEXT", seen[0][1])
        self.assertIn("VERIFIER", {r["role"] for r in wg.load_ledger(self.rcs)})
        codes = {i["code"] for i in ic.gate(self.rcs, self.root, "pre", self.draft)["items"] if i["level"] == "ERROR"}
        self.assertNotIn("GI_NOT_VERIFIER", codes)
        self.assertNotIn("GI_REPORT_INVALID", codes)


class FilesTests(unittest.TestCase):
    def test_T104_prompts_and_adapters_exist(self):
        for f in ("integrity_agent.md", "coach_agent.md", "panel/seat_protocol.md", "panel/field_analyst.md", "panel/synthesizer.md",
                  *(f"panel/{s}.md" for s in pc.SEATS)):
            self.assertTrue((SKILL_DIR / "agents" / f).exists(), f)
        for f in ("rce-verifier.md", "rce-panel.md", "rce-coach.md"):
            text = (SKILL_DIR / "adapters" / "claude_code" / "agents" / f).read_text(encoding="utf-8")
            for ref in re.findall(r"skill/(agents/[\w/]+\.md)", text):
                self.assertTrue((SKILL_DIR / ref).exists(), ref)
        models = json.loads((SKILL_DIR / "templates" / "models.json").read_text(encoding="utf-8"))
        self.assertTrue({"PANEL", "VERIFIER"} <= set(models["roles"]))

    def test_T104_skill_md_references_resolve(self):
        import package_skill
        md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        refs = package_skill.REF_RE.findall(md)
        self.assertIn("agents/integrity_agent.md", refs)
        for ref in refs:
            base = TOOLS.parent if ref.startswith("tools/") else SKILL_DIR
            self.assertTrue((base / ref).exists(), ref)

    def test_T104_validate_artifacts_checks_new_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            rcs = Path(tmp) / ".rcs"
            (rcs / "plan").mkdir(parents=True)
            (rcs / "diagnostics" / "v001_1").mkdir(parents=True)
            (rcs / "plan" / "paper_config.json").write_text('{"mode": "novel"}', encoding="utf-8")
            (rcs / "diagnostics" / "v001_1" / "editorial_decision.json").write_text('{"kind": "full"}', encoding="utf-8")
            rep = va.Report()
            va.check_schemas(rcs, rep)
            where = {i["where"] for i in rep.items if i["level"] == "ERROR"}
            self.assertIn("plan/paper_config.json", where)
            self.assertIn("diagnostics/v001_1/editorial_decision.json", where)


if __name__ == "__main__":
    unittest.main()
