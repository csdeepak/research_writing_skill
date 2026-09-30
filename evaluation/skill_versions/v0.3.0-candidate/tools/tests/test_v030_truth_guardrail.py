"""Regression tests for proposal 20260929-truth-guardrail (skill 0.3.0 candidate, vNext Stage 1).

T-019  every replay fixture (spec section 10 cases 1-10, real Phase 9 defects, negative controls)
T-020  mini-YAML reader used for figure cards
T-021  number tracer: rounding, %, K suffix, identifiers, derivation restricted to cited evidence
T-022  a fabricated-number probe is caught; a traceable number passes
T-023  license rule is fail-closed only for claim maps that use `licenses` (legacy maps: WARN)
T-024  backward compatibility: the demo project and the v0.2.0 attribution fixtures are unaffected
T-025  claim invariance: numbers/scope/strength drift, dropped and added tags
T-026  effective gate status: self-certified -> NOT_RUN, free text -> UNVERIFIED, pending -> PENDING
T-027  diagnostics: opt-in, and the record contains no project text, numbers or paths

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import claim_invariance  # noqa: E402
import lint_draft  # noqa: E402
import rce_diagnostics  # noqa: E402
import replay_fixtures  # noqa: E402
import truth_guardrail  # noqa: E402
import validate_artifacts  # noqa: E402
import verify_numbers  # noqa: E402
from rce_common import SKILL_DIR  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
DEMO = SKILL_DIR / "examples" / "demo_project"


class ReplayFixtureTests(unittest.TestCase):
    def test_T019_all_replay_fixtures(self) -> None:
        fixtures = replay_fixtures.load_fixtures(FIX / "replay")
        self.assertGreaterEqual(len(fixtures), 25)
        for fx in fixtures:
            with self.subTest(fixture=fx["id"]):
                r = replay_fixtures.run_fixture(fx)
                self.assertTrue(r["ok"], json.dumps(r["checks"], indent=1)[:1500])

    def test_T019b_every_spec_case_is_covered(self) -> None:
        origins = " ".join(str(f.get("origin")) for f in replay_fixtures.load_fixtures(FIX / "replay"))
        for n in range(1, 11):
            self.assertIn(f"spec 10 case {n}", origins, f"adversarial case {n} has no fixture")


class MiniYamlTests(unittest.TestCase):
    def test_T020_parse(self) -> None:
        y = """id: FIG-9
type: diagram   # comment
evidence: [E001, E002]
flag: true
components:
  - name: encoder
    traced_to: "src/m.py::class Encoder"
  - name: head
    status: proposed
nested:
  a: 1
  b: [x]
"""
        d = truth_guardrail.parse_mini_yaml(y)
        self.assertEqual(d["id"], "FIG-9")
        self.assertEqual(d["type"], "diagram")
        self.assertEqual(d["evidence"], ["E001", "E002"])
        self.assertIs(d["flag"], True)
        self.assertEqual(d["components"][0], {"name": "encoder", "traced_to": "src/m.py::class Encoder"})
        self.assertEqual(d["components"][1]["status"], "proposed")
        self.assertEqual(d["nested"], {"a": 1, "b": ["x"]})


class _TmpProject(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def project(self, items: list[dict], claims: list[dict] | None = None, files: dict | None = None) -> Path:
        files = dict(files or {})
        files[".rcs/evidence/research_evidence.json"] = {"project_root": ".", "generated_at": "x", "items": items}
        files[".rcs/claims/claim_evidence_map.json"] = {"claims": claims or [], "limitations": []}
        replay_fixtures.materialise(files, self.tmp)
        return self.tmp / ".rcs"


def _item(i: str, value, path: str = "r.csv", **kw) -> dict:
    d = {"id": i, "kind": "result", "summary": "s", "locator": {"path": path}, "strength": "hard", "status": "ok",
         "value": value}
    d.update(kw)
    return d


class NumberTests(_TmpProject):
    def rules(self, md: str, items: list[dict], claims=None, files=None, strict=False) -> list[str]:
        rcs = self.project(items, claims, files or {"r.csv": "x\n"})
        return [f["rule"] for f in verify_numbers.verify(md, rcs, self.tmp, strict)]

    def test_T021_rounding_percent_suffix_identifiers(self) -> None:
        items = [_item("E001", {"metric": "acc", "value": 0.8123}), _item("E002", {"metric": "share", "value": 0.196}),
                 _item("E003", {"metric": "params", "value": 38600})]
        md = "Accuracy was 0.81 and the share 19.6%. The model has 38.6K parameters. We used gpt-4-1106 in 2024."
        self.assertEqual(self.rules(md, items), [])

    def test_T021b_derivation_only_from_cited_evidence(self) -> None:
        items = [_item("E001", {"metric": "mae", "value": 0.553}, conditions={"m": "b"}),
                 _item("E002", {"metric": "mae", "value": 0.433}, conditions={"m": "r"})]
        claims = [{"id": "C001", "statement": "x", "claim_type": "derived", "evidence": ["E001", "E002"],
                   "confidence": "moderate", "author_confirmation": "confirmed"}]
        self.assertEqual(self.rules("MAE fell by 21.7% {C001}.", items, claims), ["DERIVED_MATCH"])
        self.assertEqual(self.rules("MAE fell by 21.7%.", items, claims), ["UNTRACED_NUMBER"])

    def test_T022_fabricated_vs_traceable(self) -> None:
        items = [_item("E001", {"metric": "acc", "value": 0.84})]
        self.assertIn("UNTRACED_NUMBER", self.rules("Accuracy reached 0.987.", items))
        self.assertEqual(self.rules("Accuracy reached 0.84.", items), [])
        self.assertIn("UNTRACED_PVALUE", self.rules("A clear gain (p < 0.05).", items))


class LicenseModeTests(unittest.TestCase):
    CLAIM = {"id": "C001", "statement": "x", "claim_type": "derived", "evidence": ["E001"], "confidence": "moderate",
             "author_confirmation": "confirmed"}

    def levels(self, claim: dict, md: str) -> list[str]:
        L = lint_draft.lint_text(md, {"C001": claim}, False, False, set(), None)
        return [f["level"] for f in L.findings if f["rule"].startswith("UNLICENSED")]

    def test_T023_fail_closed_only_with_licenses(self) -> None:
        md = "M significantly improves accuracy {C001}."
        self.assertEqual(self.levels(self.CLAIM, md), ["WARN"])                        # legacy claim map
        self.assertEqual(self.levels(dict(self.CLAIM, licenses=[]), md), ["ERROR"])      # v0.3 claim map
        ok = dict(self.CLAIM, licenses=[{"type": "significance_test", "evidence": ["E009"]}])
        self.assertEqual(self.levels(ok, md), [])                                         # evidence checked by validator

    def test_T023b_non_asserting_and_negated_uses_are_exempt(self) -> None:
        hyp = dict(self.CLAIM, claim_type="hypothesis", licenses=[])
        self.assertEqual(self.levels(hyp, "We test whether M generalizes {C001}."), [])
        self.assertEqual(self.levels(dict(self.CLAIM, licenses=[]), "M was not tested for robustness {C001}."), [])


class BackwardCompatTests(unittest.TestCase):
    def test_T024_demo_still_valid(self) -> None:
        rep = validate_artifacts.Report()
        rcs = DEMO / ".rcs"
        loaded = validate_artifacts.check_schemas(rcs, rep)
        validate_artifacts.check_references(rcs, DEMO, loaded, rep)
        truth_guardrail.run(rcs, DEMO, loaded, rep)
        self.assertEqual([i for i in rep.items if i["level"] == "ERROR"], [])

    def test_T024b_v020_fixtures_unchanged(self) -> None:
        for name in ("H_author_limitations_replaced.md", "I_attributed_limitations.md"):
            md = (FIX / name).read_text(encoding="utf-8")
            L = lint_draft.lint_text(md, {}, False, False, set(), None)
            self.assertFalse([f for f in L.findings if f["rule"].startswith(("UNLICENSED", "BLOCKED"))], name)


class InvarianceTests(unittest.TestCase):
    B = "M reached 0.84 on one split {C001}. This suggests X {C002}. Baselines were untuned {L001}."

    def rules(self, after: str) -> set[str]:
        return {f["rule"] for f in claim_invariance.compare(self.B, after)}

    def test_T025_drift_kinds(self) -> None:
        self.assertIn("CLAIM_DRIFT_NUMBER", self.rules(self.B.replace("0.84", "0.86")))
        self.assertIn("CLAIM_DRIFT_SCOPE", self.rules(self.B.replace("on one split", "across datasets")))
        self.assertIn("CLAIM_DRIFT_STRENGTH", self.rules(self.B.replace("suggests", "shows that")))
        self.assertIn("CLAIM_DROPPED", self.rules(self.B.replace(" {L001}", "")))
        self.assertIn("CLAIM_ADDED", self.rules(self.B + " New point {C009}."))
        self.assertEqual(self.rules("On one split, M reached 0.84 {C001}. This suggests X {C002}. "
                                    "The baselines were untuned {L001}."), set())


class GateStatusTests(_TmpProject):
    def eff(self, gates: dict) -> dict:
        rcs = self.project([])
        (rcs / "state.json").write_text(json.dumps({"gates": gates}), encoding="utf-8")
        rep = validate_artifacts.Report()
        return validate_artifacts.check_gates(rcs, self.tmp, rep)

    def test_T026_effective_status(self) -> None:
        e = self.eff({"G1": "passed", "G2": "passed", "G4": "pending_step_18", "G9": "ALL AUDITS PASS, see notes",
                      "G5": "not_run"})
        self.assertEqual(e["G1"], "NOT_RUN")   # no tool report
        self.assertEqual(e["G2"], "NOT_RUN")   # no executable check exists
        self.assertEqual(e["G4"], "PENDING")
        self.assertEqual(e["G9"], "UNVERIFIED")
        self.assertEqual(e["G5"], "NOT_RUN")


class StrictGateTests(_TmpProject):
    """T-028: with "guardrail": "v0.3", G3 needs a clean numbers report and G5 an invariance report."""

    def run_quiet(self, mod, args: list[str]) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            mod.main(args)

    def test_T028_v03_gates_require_new_reports(self) -> None:
        rcs = self.project([_item("E001", {"metric": "acc", "value": 0.84})],
                           [{"id": "C001", "statement": "x", "claim_type": "measured", "evidence": ["E001"],
                             "confidence": "moderate", "author_confirmation": "confirmed"}], {"r.csv": "x\n"})
        draft = self.tmp / "paper.md"
        draft.write_text("M reached 0.84 accuracy {C001}.\n", encoding="utf-8")
        self.run_quiet(lint_draft, [str(draft), "--rcs", str(rcs), "--out", str(rcs / "audits/gates/G3_lint.json")])

        def gate(guardrail: str | None) -> str:
            st = {"gates": {"G3": "passed"}}
            if guardrail:
                st["guardrail"] = guardrail
            (rcs / "state.json").write_text(json.dumps(st), encoding="utf-8")
            return validate_artifacts.check_gates(rcs, self.tmp, validate_artifacts.Report())["G3"]

        self.assertEqual(gate(None), "PASSED")            # v0.2 semantics kept for legacy projects
        self.assertEqual(gate("v0.3"), "NOT_RUN")         # numbers report missing
        self.run_quiet(verify_numbers, [str(draft), "--rcs", str(rcs), "--project-root", str(self.tmp),
                                        "--out", str(rcs / "audits/gates/G3_numbers.json")])
        self.assertEqual(gate("v0.3"), "PASSED")
        draft.write_text("M reached 0.987 accuracy (p < 0.01) {C001}.\n", encoding="utf-8")
        self.run_quiet(lint_draft, [str(draft), "--rcs", str(rcs), "--out", str(rcs / "audits/gates/G3_lint.json")])
        self.run_quiet(verify_numbers, [str(draft), "--rcs", str(rcs), "--project-root", str(self.tmp),
                                        "--out", str(rcs / "audits/gates/G3_numbers.json")])
        self.assertEqual(gate("v0.3"), "FAILED")          # inferred p-value is an ERROR in the report

    def test_T028b_G5_invariance_report(self) -> None:
        rcs = self.project([])
        before, after = self.tmp / "before.md", self.tmp / "after.md"
        before.write_text("M reached 0.84 on one split {C001}.\n", encoding="utf-8")
        after.write_text("M reached 0.84 across datasets {C001}.\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            claim_invariance.main([str(before), str(after), "--out", str(rcs / "audits/gates/G5_invariance.json")])
        (rcs / "state.json").write_text(json.dumps({"guardrail": "v0.3", "gates": {"G5": "passed"}}), encoding="utf-8")
        rep = validate_artifacts.Report()
        validate_artifacts.check_gates(rcs, self.tmp, rep)
        self.assertTrue(any("G5_invariance.json reports 1 error" in i["message"] for i in rep.items))


class DiagnosticsTests(_TmpProject):
    SECRET = "Confidential-Project-Zeta"

    def setUp(self) -> None:
        super().setUp()
        self.home = self.tmp / "home"
        os.environ["RCE_HOME"] = str(self.home)
        os.environ.pop("RCE_DIAGNOSTICS", None)

    def tearDown(self) -> None:
        os.environ.pop("RCE_HOME", None)
        super().tearDown()

    def make_run(self) -> Path:
        rcs = self.project([_item("E001", {"metric": "acc", "value": 0.8765}, summary=self.SECRET)],
                           files={"r.csv": "x\n"})
        (rcs / "audits" / "gates").mkdir(parents=True)
        (rcs / "audits" / "gates" / "G3_lint.json").write_text(json.dumps({"errors": 1, "findings": [
            {"rule": "B9-significance", "level": "WARN", "excerpt": f"{self.SECRET} improved 0.8765", "message": "m"}]}),
            encoding="utf-8")
        (rcs / "state.json").write_text(json.dumps({"step": 17, "gates": {"G3": "passed"},
                                                    "accepted_risks": [{"note": self.SECRET}]}), encoding="utf-8")
        return rcs

    def test_T027_opt_in_required(self) -> None:
        rcs = self.make_run()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(rce_diagnostics.main(["record", str(rcs)]), 2)
        self.assertFalse((self.home / "diagnostics.jsonl").exists())

    def test_T027b_record_is_content_free(self) -> None:
        rcs = self.make_run()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(rce_diagnostics.main(["record", str(rcs), "--opt-in", "--domain", "ml"]), 0)
        text = (self.home / "diagnostics.jsonl").read_text(encoding="utf-8")
        for leak in (self.SECRET, "0.8765", str(self.tmp), "improved"):
            self.assertNotIn(leak, text)
        rec = json.loads(text)
        self.assertEqual(rec["rules"], {"WARN:B9-significance": 1})
        self.assertEqual(rec["accepted_risks"], 1)
        summ = rce_diagnostics.summarize([rec, rec, rec], 3)
        self.assertEqual(summ["recurring_patterns"][0]["rule"], "WARN:B9-significance")



class LengthCountTests(unittest.TestCase):
    """T-051: the length gate counts headings and table text for v0.3 projects (tier-3 A/B: 3,751 prose words vs
    4,403 counted the usual way); table rules and pipes are never words; legacy projects keep the prose count."""

    def test_T051(self) -> None:
        import tempfile
        from rce_common import length_mode, main_text_words
        md = ("# Title words\n\nOne two three.\n\n| a b | c |\n|---|:---:|\n| d | e f |\n\n"
              "## References\n\nRef one two.\n")
        self.assertEqual(main_text_words(md), 3)
        self.assertEqual(main_text_words(md, "all"), 3 + 2 + 3 + 3)
        with tempfile.TemporaryDirectory() as t:
            rcs = Path(t)
            (rcs / "state.json").write_text('{"guardrail": "v0.3"}', encoding="utf-8")
            self.assertEqual(length_mode(rcs), "all")
            (rcs / "state.json").write_text('{"guardrail": "v0.3", "length_count": "prose"}', encoding="utf-8")
            self.assertEqual(length_mode(rcs), "prose")
            (rcs / "state.json").write_text("{}", encoding="utf-8")
            self.assertEqual(length_mode(rcs), "prose")


if __name__ == "__main__":
    unittest.main()
