"""Regression tests for proposal 20260929-full-workflow (skill 0.3.0 candidate, vNext Stage 4).

T-042  every Stage 4 replay fixture (WF-*): role violations, tamper evidence, checkpoints, accepted-risk kinds
T-043  checkpoint CLI: ask -> status exit 3 -> answer (named person) -> status 0
T-044  G4: no review -> fail; review of a different draft -> fail; blocking findings need dispositions;
       'fixed' with an unchanged draft -> fail; complete dispositions -> pass; state.json G4 needs the fresh report
T-047  ledger paths: the final manuscript (../paper/) is recordable by AUTHOR; a path outside the project is a
       ROLE_VIOLATION, not a crash (found by the Stage 4 e2e run)
T-048  review packet: linked figures copied (sanitized) and hashed; missing / parent links logged, not copied
T-049  a BLOCKED author rationale/limitation is withheld (WARN), not missing (ERROR); used anyway -> ERROR
T-059  G4 goes STALE when the newest draft states claims no blind review covered (found by the checkpoint-answer
       round of the end-to-end run: an answer added a claim after the review)
T-060  an author statement the authors rejected is neither 'missing' nor 'withheld' in the lint
T-061  stripping gap markers leaves no space before punctuation (seen in the end-to-end round-2 packet); a bare
       [CITATION NEEDED] without a note is a marker too, so the final lint (G5) fails on it
T-045  run_workflow: executes gates, logs every command with tool hash, writes back only validator-confirmed status

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import build_review_packet  # noqa: E402
import g4_check  # noqa: E402
import lint_draft  # noqa: E402
import replay_fixtures  # noqa: E402
import run_workflow  # noqa: E402
import validate_artifacts  # noqa: E402
import workflow_guard  # noqa: E402
from rce_common import SKILL_DIR  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "replay"
DIMS = ["problem", "motivation", "research_question", "contribution", "method", "experiment", "result", "interpretation",
        "limitation", "narrative_coherence", "terminology", "logical_flow", "evidence_traceability", "figure_table",
        "claim_evidence_alignment", "unsupported_inference", "redundancy", "cognitive_load", "orientation", "so_what"]


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


class ReplayStage4Tests(unittest.TestCase):
    def test_T042(self) -> None:
        fixtures = [f for f in replay_fixtures.load_fixtures(FIX) if f["id"].startswith("WF-")]
        self.assertGreaterEqual(len(fixtures), 8)
        for fx in fixtures:
            with self.subTest(fixture=fx["id"]):
                r = replay_fixtures.run_fixture(fx)
                self.assertTrue(r["ok"], json.dumps(r["checks"], indent=1)[:1200])


class _Proj(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(SKILL_DIR / "examples" / "demo_project", self.tmp / "p")
        self.root = self.tmp / "p"
        self.rcs = self.root / ".rcs"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class LedgerPathTests(_Proj):
    def test_T047(self) -> None:
        (self.root / "paper").mkdir(exist_ok=True)
        (self.root / "paper" / "paper.md").write_text("final", encoding="utf-8")
        outside = self.tmp / "elsewhere.md"
        outside.write_text("x", encoding="utf-8")
        recs = workflow_guard.record(self.rcs, "AUTHOR", [str(self.root / "paper" / "paper.md"), str(outside)])
        self.assertEqual(recs[0]["path"], "../paper/paper.md")
        self.assertTrue(workflow_guard.allowed("AUTHOR", recs[0]["path"]))
        self.assertFalse(workflow_guard.allowed("REVIEW", recs[0]["path"]))
        self.assertFalse(workflow_guard.allowed("AUTHOR", recs[1]["path"]))
        rep = validate_artifacts.Report()
        workflow_guard.run(self.rcs, self.root, {}, rep)
        viol = [i for i in rep.items if "ROLE_VIOLATION" in i["message"]]
        self.assertEqual(len(viol), 1)
        self.assertIn("elsewhere.md", viol[0]["message"])


class PacketFigureTests(_Proj):
    def test_T048(self) -> None:
        d = self.rcs / "drafts" / "v009"
        d.mkdir(parents=True)
        (self.rcs / "plan" / "figures").mkdir(parents=True, exist_ok=True)
        (self.rcs / "plan" / "figures" / "V1.svg").write_text("<svg><!-- internal E001 --><text>a\u200bb</text></svg>",
                                                               encoding="utf-8")
        (d / "paper.md").write_text("# P\n\n![Figure 1](figures/V1.svg)\n![x](figures/gone.svg)\n![y](../secret.svg)\n",
                                    encoding="utf-8")
        for n in ("audience.md", "objective.md"):
            (self.tmp / n).write_text(n, encoding="utf-8")
        out = self.tmp / "pkt"
        quiet(build_review_packet.main, [str(d / "paper.md"), "--out", str(out), "--audience", str(self.tmp / "audience.md"),
                                         "--objective", str(self.tmp / "objective.md")])
        fig = (out / "figures" / "V1.svg").read_text(encoding="utf-8")
        self.assertNotIn("E001", fig)
        self.assertNotIn("\u200b", fig)
        man = json.loads((out / "packet_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("figures/V1.svg", man["files"])
        warns = {w.get("warning"): w.get("link") for w in man["sanitization_log"] if "warning" in w}
        self.assertEqual(warns.get("figure_missing"), "figures/gone.svg")
        self.assertEqual(warns.get("figure_link_not_copied"), "../secret.svg")
        self.assertFalse((self.tmp / "secret.svg").exists())


class WithheldStatementTests(unittest.TestCase):
    def test_T049(self) -> None:
        claims = {"C001": {"id": "C001", "claim_type": "result", "status": "VERIFIED"},
                  "C008": {"id": "C008", "claim_type": "interpretation", "origin": "author_stated", "rationale": "motivation",
                           "status": "BLOCKED"},
                  "L001": {"id": "L001", "claim_type": "limitation", "origin": "author_stated", "status": "BLOCKED"}}
        md = "## 1 Introduction\n\nProblem {C001}.\n\n## 4 Limitations\n\nSmall corpus.\n"
        rules = {}
        for f in lint_draft.lint_text(md, claims, final=False, require_tags=False, known_acronyms=set()).findings:
            rules.setdefault(f["rule"], []).append(f["level"])
        self.assertEqual(rules.get("S1/S2-author-statement-withheld"), ["WARN", "WARN"])
        self.assertNotIn("S2-author-rationale-missing", rules)
        self.assertNotIn("S1-author-limitation-missing", rules)
        used = md.replace("Problem {C001}.", "Problem {C001}. It matters because X {C008}.")
        levels = {f["rule"]: f["level"] for f in lint_draft.lint_text(used, claims, final=False, require_tags=False,
                                                                        known_acronyms=set()).findings}
        self.assertEqual(levels.get("BLOCKED-claim-used"), "ERROR")
        claims["C008"]["status"] = "VERIFIED"
        levels = {f["rule"]: f["level"] for f in lint_draft.lint_text(md, claims, final=False, require_tags=False,
                                                                        known_acronyms=set()).findings}
        self.assertEqual(levels.get("S2-author-rationale-missing"), "ERROR")


class PostReviewClaimTests(_Proj):
    def test_T059(self) -> None:
        import hashlib
        (self.rcs / "revisions" / "v001_1").mkdir(parents=True, exist_ok=True)
        disp = self.rcs / "revisions" / "v001_1" / "dispositions.json"
        disp.write_text('{"items": []}', encoding="utf-8")
        gates = self.rcs / "audits" / "gates"
        gates.mkdir(parents=True, exist_ok=True)
        (gates / "G4_review.json").write_text(json.dumps({
            "errors": 0, "round": "v001_1", "claims_covered": ["C001", "C002"],
            "dispositions_sha256": hashlib.sha256(disp.read_bytes()).hexdigest()}), encoding="utf-8")
        sp = self.rcs / "state.json"
        state = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
        state.setdefault("gates", {})["G4"] = "passed"
        (self.rcs / "state.json").write_text(json.dumps(state), encoding="utf-8")
        d = self.rcs / "drafts" / "v009"
        d.mkdir(parents=True, exist_ok=True)
        (d / "paper.md").write_text("Result {C001}. Also {C002}.\n", encoding="utf-8")
        rep = validate_artifacts.Report()
        self.assertEqual(validate_artifacts.check_gates(self.rcs, self.root, rep).get("G4"), "PASSED")
        (d / "paper.md").write_text("Result {C001}. Also {C002}. New claim {C009}.\n", encoding="utf-8")
        rep = validate_artifacts.Report()
        self.assertEqual(validate_artifacts.check_gates(self.rcs, self.root, rep).get("G4"), "STALE")
        self.assertTrue(any("C009" in i["message"] for i in rep.items))

    def test_T060(self) -> None:
        claims = {"C001": {"id": "C001", "claim_type": "result", "status": "VERIFIED"},
                  "C024": {"id": "C024", "claim_type": "interpretation", "origin": "author_stated", "rationale": "motivation",
                           "status": "BLOCKED", "author_confirmation": "rejected"}}
        md = "## 1 Introduction\n\nProblem {C001}.\n\n## 4 Limitations\n\nSmall corpus.\n"
        rules = {f["rule"] for f in lint_draft.lint_text(md, claims, final=False, require_tags=False,
                                                         known_acronyms=set()).findings}
        self.assertFalse(rules & {"S1/S2-author-statement-withheld", "S2-author-rationale-missing"})


class MarkerStripTests(unittest.TestCase):
    def test_T061(self) -> None:
        md, _ = build_review_packet.sanitize("It is left open [ASK AUTHOR: why]. Prior work [CITATION NEEDED] shows x.\n", True)
        self.assertEqual(md.strip(), "It is left open. Prior work shows x.")
        final = lint_draft.lint_text("# T\n\nPrior work [CITATION NEEDED] shows x.\n", {}, final=True, require_tags=False,
                                     known_acronyms=set())
        self.assertIn("ERROR", {f["level"] for f in final.findings if f["rule"] == "marker"})


class CheckpointTests(_Proj):
    def test_T043(self) -> None:
        r = str(self.rcs)
        quiet(workflow_guard.main, ["ask", "--rcs", r, "--id", "Q-1", "--question", "Which split?", "--blocks", "C001"])
        self.assertEqual(quiet(workflow_guard.main, ["status", "--rcs", r]), 3)
        with self.assertRaises(SystemExit):
            quiet(workflow_guard.main, ["answer", "--rcs", r, "--id", "Q-1", "--answer", "test"])     # --by required
        quiet(workflow_guard.main, ["answer", "--rcs", r, "--id", "Q-1", "--answer", "test split", "--by", "A. Author"])
        self.assertEqual(quiet(workflow_guard.main, ["status", "--rcs", r]), 0)


class G4Tests(_Proj):
    def make_review(self, draft: Path, scores: dict[str, int], rnd: str = "v001_1", inference: int = 0) -> None:
        pk = self.rcs / "packets" / f"review_{rnd}"
        aud = self.tmp / "aud.md"
        aud.write_text("Readers: adjacent ML researchers.", encoding="utf-8")
        quiet(build_review_packet.main, [str(draft), "--out", str(pk), "--audience", str(aud), "--objective", str(aud)])
        pid = json.loads((pk / "packet_manifest.json").read_text(encoding="utf-8"))["packet_id"]
        findings = [{"dimension": d, "score": scores.get(d, 4), "persona": ["B"], "location": {"section": "Results"},
                     "observed": "observation text", "reader_struggle": "x", "likely_consequence": "y",
                     "revision_principle": "z"} for d in DIMS]
        diag = {"packet_id": pid, "binding_personas": ["B"], "findings": findings, "injection_suspected": [],
                "inference_issues": [{"kind": "overstrong_language", "location": {"section": "Abstract"},
                                      "claim_text": "clearly better", "missing_link": "no test"}] * inference}
        d = self.rcs / "diagnostics" / rnd
        d.mkdir(parents=True, exist_ok=True)
        (d / "diagnostics.json").write_text(json.dumps(diag), encoding="utf-8")

    def disp(self, items: list[dict], rnd: str = "v001_1") -> None:
        d = self.rcs / "revisions" / rnd
        d.mkdir(parents=True, exist_ok=True)
        (d / "dispositions.json").write_text(json.dumps({"items": items}), encoding="utf-8")

    def codes(self, revised: Path | None = None) -> list[str]:
        return [i["code"] for i in g4_check.check(self.rcs, "v001_1", revised)["items"]]

    def test_T044_g4(self) -> None:
        draft = self.root / "drafts" / "v001" / "paper.md"
        draft.parent.mkdir(parents=True)
        draft.write_text("# Paper\n\nM reduced error by 12%.\n", encoding="utf-8")
        self.assertIn("G4_NO_REVIEW", self.codes())
        self.make_review(draft, {"result": 2, "evidence_traceability": 3}, inference=1)
        self.assertEqual(self.codes().count("G4_UNADDRESSED"), 3)          # 2 blocking findings + 1 inference issue
        revised = self.root / "drafts" / "v002" / "paper.md"
        revised.parent.mkdir(parents=True)
        revised.write_text(draft.read_text(encoding="utf-8"), encoding="utf-8")
        blocking = g4_check.blocking(json.loads((self.rcs / "diagnostics" / "v001_1" / "diagnostics.json").read_text())["findings"])
        items = [{"item": f"finding:{i}", "disposition": "fixed", "where": "Results para 2"} for i in blocking] + \
                [{"item": "inference:0", "disposition": "declined", "reason": "the sentence already cites the paired test"}]
        self.disp(items)
        self.assertIn("G4_UNADDRESSED", self.codes(revised))              # 'fixed' but draft unchanged
        revised.write_text("# Paper\n\nM reduced error by 12% (Table 2).\n", encoding="utf-8")
        self.assertEqual(self.codes(revised), [])
        draft.write_text("# Paper\n\nchanged after review\n", encoding="utf-8")
        self.assertIn("G4_PACKET_MISMATCH", self.codes(revised))          # review no longer covers this draft
        draft.write_text("# Paper\n\nM reduced error by 12%.\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            g4_check.main([str(self.rcs), "--round", "v001_1", "--revised", str(revised),
                           "--out", str(self.rcs / "audits" / "gates" / "G4_review.json")])
        (self.rcs / "state.json").write_text(json.dumps({"gates": {"G4": "passed"}}), encoding="utf-8")
        self.assertEqual(validate_artifacts.check_gates(self.rcs, self.root, validate_artifacts.Report())["G4"], "PASSED")
        self.disp(items[:-1])                                              # dispositions changed after the check
        self.assertEqual(validate_artifacts.check_gates(self.rcs, self.root, validate_artifacts.Report())["G4"], "STALE")


class RunWorkflowTests(_Proj):
    def test_T045(self) -> None:
        draft = self.root / "paper.md"
        draft.write_text("# Paper\n\n## Results\n\nUnder shift 0.4, RWN reached an MAE of 0.433 {C002}.\n", encoding="utf-8")

        class A:
            pass
        a = A()
        a.draft, a.round, a.revised, a.final, a.before, a.edited = str(draft), None, None, None, None, None
        s = quiet(run_workflow.run_gates, self.rcs, self.root, a)
        log = [json.loads(x) for x in (self.rcs / "audits" / "gates" / "RUN_LOG.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual({e["gate"] for e in log}, {"G1", "G3"})
        self.assertEqual(log[-1]["gate"], "G1")          # G1 validates after the G3 reports are fresh
        self.assertTrue(all(len(e["tool_sha256"]) == 64 for e in log))
        state = json.loads((self.rcs / "state.json").read_text(encoding="utf-8"))
        for g, st in s["effective_gates"].items():
            if g in state["gates"]:
                self.assertEqual(state["gates"][g], "passed" if st == "PASSED" else st.lower())


if __name__ == "__main__":
    unittest.main()
