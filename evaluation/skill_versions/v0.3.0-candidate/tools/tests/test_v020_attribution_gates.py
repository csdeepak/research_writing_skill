"""Regression tests for proposal 20260924-attribution-and-adherence (skill 0.2.0 candidate).

T-008..T-011  attribution of limitations and author rationale (clusters S1, S2)
T-012..T-014  executable gates: no self-certified G1/G3/G5 (cluster S3)
T-015..T-016  length gate (cluster S4)
T-017..T-018  draft-side attribution lint (clusters S1, S2)

Every test here fails on skill/tools v0.1.0 (the rules, fields, and report files do not exist
there) and passes on the candidate. Run:  python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import lint_draft  # noqa: E402
import validate_artifacts  # noqa: E402
from rce_common import SKILL_DIR, main_text_words  # noqa: E402

PERT = SKILL_DIR / "tests" / "perturbations"
FIX = Path(__file__).resolve().parent / "fixtures"
DEMO = SKILL_DIR / "examples" / "demo_project"


class _Project(unittest.TestCase):
    """Each test works on a throw-away copy of the demo project."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.proj = self.tmp / "proj"
        shutil.copytree(DEMO, self.proj)
        self.rcs = self.proj / ".rcs"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def edit(self, rel: str, fn) -> None:
        p = self.rcs / rel
        data = json.loads(p.read_text(encoding="utf-8"))
        fn(data)
        p.write_text(json.dumps(data, indent=1), encoding="utf-8")

    def state(self, obj: dict) -> None:
        (self.rcs / "state.json").write_text(json.dumps(obj), encoding="utf-8")

    def validate(self) -> validate_artifacts.Report:
        rep = validate_artifacts.Report()
        loaded = validate_artifacts.check_schemas(self.rcs, rep)
        validate_artifacts.check_references(self.rcs, self.proj, loaded, rep)
        validate_artifacts.check_spine(self.rcs, rep)
        validate_artifacts.check_gates(self.rcs, self.proj, rep)
        return rep

    def msgs(self, rep, level: str = "ERROR") -> list[str]:
        return [f"{i['where']}: {i['message']}" for i in rep.items if i["level"] == level]

    def run_tool(self, mod, args: list[str]) -> None:
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            mod.main(args)

    def add_rationale_evidence(self, status: str = "ok") -> None:
        self.edit("evidence/research_evidence.json", lambda d: d["items"].append({
            "id": "E013", "kind": "rationale_stated",
            "summary": "Model size kept fixed so that capacity cannot explain differences between normalizations",
            "locator": {"path": "notes/lab_notes.md", "anchor": "## Hypothesis"},
            "strength": "soft", "status": status}))

    def add_rationale_claim(self, origin: str = "author_stated", rationale: str = "design_choice") -> None:
        self.edit("claims/claim_evidence_map.json", lambda d: d["claims"].append({
            "id": "C008", "statement": "The model was held fixed across normalizations so that capacity could not explain differences.",
            "claim_type": "interpretation", "evidence": ["E013", "E007"], "confidence": "moderate",
            "author_confirmation": "confirmed", "origin": origin, "rationale": rationale}))


# --------------------------------------------------------------------------- S1 / S2 artifacts
class AttributionValidatorTests(_Project):
    def test_T008_limitation_requires_origin(self) -> None:
        self.edit("claims/claim_evidence_map.json", lambda d: d["limitations"][0].pop("origin"))
        self.assertTrue(any("origin" in m for m in self.msgs(self.validate())))

    def test_T009_author_limitation_must_be_carried(self) -> None:
        def f(d):
            for lim in d["limitations"]:
                lim["origin"] = "writer_derived"
        self.edit("claims/claim_evidence_map.json", f)
        self.assertTrue(any("E008" in m and "AUTHOR_STATEMENT_DROPPED" in m for m in self.msgs(self.validate())))

    def test_T009b_superseded_author_limitation_is_exempt(self) -> None:
        def f(d):
            for lim in d["limitations"]:
                lim["origin"] = "writer_derived"
        self.edit("claims/claim_evidence_map.json", f)
        self.edit("evidence/research_evidence.json",
                  lambda d: next(i for i in d["items"] if i["id"] == "E008").update(status="superseded"))
        self.assertFalse(any("AUTHOR_STATEMENT_DROPPED" in m for m in self.msgs(self.validate())))

    def test_T010_writer_caveat_cannot_be_labelled_author_stated(self) -> None:
        self.edit("claims/claim_evidence_map.json",
                  lambda d: next(x for x in d["limitations"] if x["id"] == "L003").update(origin="author_stated"))
        self.assertTrue(any("L003" in m and "ATTRIBUTION_ERROR" in m for m in self.msgs(self.validate())))

    def test_T011_author_rationale_must_be_carried(self) -> None:
        self.add_rationale_evidence()
        self.assertTrue(any("E013" in m and "AUTHOR_STATEMENT_DROPPED" in m for m in self.msgs(self.validate())))
        self.add_rationale_claim()
        self.assertEqual(self.msgs(self.validate()), [])

    def test_T011b_rationale_cannot_be_writer_derived(self) -> None:
        self.add_rationale_evidence()
        self.add_rationale_claim(origin="writer_derived")
        self.assertTrue(any("C008" in m and "author_stated" in m for m in self.msgs(self.validate())))

    def test_demo_still_valid(self) -> None:
        self.assertEqual(self.msgs(self.validate()), [])


# --------------------------------------------------------------------------- S3 executable gates
class GateTests(_Project):
    def test_T012_self_certified_gate_is_an_error(self) -> None:
        self.state({"step": 21, "gates": {"G1": "passed", "G3": "passed", "G5": "passed — lint clean"}})
        errs = self.msgs(self.validate())
        for g in ("G1", "G3", "G5"):
            self.assertTrue(any(f"state.json/{g}" in m and "SELF_CERTIFIED_GATE" in m for m in errs), g)

    def test_T012b_invalid_state_json_is_an_error(self) -> None:
        (self.rcs / "state.json").write_text('{"gates": {"G1": "passed" "G2": "passed"}}', encoding="utf-8")
        self.assertTrue(any("state.json" in m and "invalid JSON" in m for m in self.msgs(self.validate())))

    def test_T013_gate_backed_by_fresh_report_passes(self) -> None:
        self.run_tool(validate_artifacts, [str(self.rcs), "--out", str(self.rcs / "audits/gates/G1_validate.json")])
        self.state({"gates": {"G1": "passed"}})
        self.assertEqual(self.msgs(self.validate()), [])
        # Artifacts changed after G1: warn (re-run), not block
        self.edit("claims/claim_evidence_map.json", lambda d: d["claims"][0].update(confidence="low"))
        rep = self.validate()
        self.assertEqual(self.msgs(rep), [])
        self.assertTrue(any("stale" in m for m in self.msgs(rep, "WARN")))

    def test_T013b_stale_G5_report_blocks(self) -> None:
        self.run_tool(validate_artifacts, [str(self.rcs), "--out", str(self.rcs / "audits/gates/G5_validate.json")])
        self.edit("claims/claim_evidence_map.json", lambda d: d["claims"][0].update(confidence="low"))
        self.state({"gates": {"G5": "passed"}})
        self.assertTrue(any("G5" in m and "stale" in m for m in self.msgs(self.validate())))

    def test_T013c_report_with_errors_blocks(self) -> None:
        self.edit("claims/claim_evidence_map.json", lambda d: d["claims"][0].update(evidence=[]))
        self.run_tool(validate_artifacts, [str(self.rcs), "--out", str(self.rcs / "audits/gates/G1_validate.json")])
        self.state({"gates": {"G1": "passed"}})
        self.assertTrue(any("G1" in m and "reports" in m for m in self.msgs(self.validate())))

    def test_T014_G3_lint_report(self) -> None:
        draft = self.proj / "drafts" / "v001" / "paper.md"
        draft.parent.mkdir(parents=True)
        shutil.copy(FIX / "I_attributed_limitations.md", draft)
        out = self.rcs / "audits/gates/G3_lint.json"
        self.run_tool(lint_draft, [str(draft), "--rcs", str(self.rcs), "--out", str(out)])
        self.state({"gates": {"G3": "passed"}})
        self.assertEqual(self.msgs(self.validate()), [])
        # Draft edited after linting -> stale report blocks the gate
        draft.write_text(draft.read_text(encoding="utf-8") + "\nA new unchecked paragraph.\n", encoding="utf-8")
        self.assertTrue(any("G3" in m and "stale" in m for m in self.msgs(self.validate())))
        # Lint without --rcs cannot certify G3
        self.run_tool(lint_draft, [str(draft), "--out", str(out)])
        self.assertTrue(any("without --rcs" in m for m in self.msgs(self.validate())))

    def test_T014b_G3_lint_report_with_errors_blocks(self) -> None:
        draft = self.proj / "paper.md"
        shutil.copy(FIX / "H_author_limitations_replaced.md", draft)
        self.run_tool(lint_draft, [str(draft), "--rcs", str(self.rcs), "--out", str(self.rcs / "audits/gates/G3_lint.json")])
        self.state({"gates": {"G3": "passed"}})
        self.assertTrue(any("G3" in m and "reports 2 error" in m for m in self.msgs(self.validate())))


# --------------------------------------------------------------------------- S4 length gate
class LengthGateTests(_Project):
    def test_T015_lint_length_rule(self) -> None:
        md = (PERT / "A_clean.md").read_text(encoding="utf-8")
        draft = lint_draft.lint_text(md, {}, final=False, require_tags=False, known_acronyms=set(), max_words=500)
        final = lint_draft.lint_text(md, {}, final=True, require_tags=False, known_acronyms=set(), max_words=500)
        roomy = lint_draft.lint_text(md, {}, final=True, require_tags=False, known_acronyms=set(), max_words=5000)
        self.assertIn(("S4-over-length", "WARN"), {(f["rule"], f["level"]) for f in draft.findings})
        self.assertIn(("S4-over-length", "ERROR"), {(f["rule"], f["level"]) for f in final.findings})
        self.assertNotIn("S4-over-length", {f["rule"] for f in roomy.findings})

    def test_T015b_main_text_excludes_back_matter(self) -> None:
        md = ("# T\n\n## Intro\n\none two three {C001}\n\n## References\n\nfour five\n\n"
              "## Appendix\n\n### A.1 Extra\n\nsix seven eight\n\n## Conclusion\n\nnine\n")
        self.assertEqual(main_text_words(md), 4)

    def test_T016_G5_length_gate(self) -> None:
        draft = self.proj / "paper.md"
        draft.write_text(" ".join(["word"] * 60) + ".\n", encoding="utf-8")
        self.state({"length_limit_words": 50, "gates": {"G5": "passed"}})
        self.run_tool(validate_artifacts, [str(self.rcs), "--out", str(self.rcs / "audits/gates/G5_validate.json")])
        self.run_tool(lint_draft, [str(draft), "--rcs", str(self.rcs), "--final",
                                   "--out", str(self.rcs / "audits/gates/G5_lint.json")])
        errs = self.msgs(self.validate())
        self.assertTrue(any("LENGTH_EXCEEDED" in m or "reports 1 error" in m for m in errs))
        # Within the limit the same gate passes
        self.state({"length_limit_words": 100, "gates": {"G5": "passed"}})
        self.run_tool(validate_artifacts, [str(self.rcs), "--out", str(self.rcs / "audits/gates/G5_validate.json")])
        self.run_tool(lint_draft, [str(draft), "--rcs", str(self.rcs), "--final",
                                   "--out", str(self.rcs / "audits/gates/G5_lint.json")])
        self.assertEqual(self.msgs(self.validate()), [])


# --------------------------------------------------------------------------- S1 / S2 draft lint
def _rules(md: str, claims: dict) -> dict[str, str]:
    res = lint_draft.lint_text(md, claims, final=False, require_tags=False, known_acronyms=set())
    out: dict[str, str] = {}
    for f in res.findings:
        out.setdefault(f["rule"], f["level"])
    return out


class AttributionLintTests(unittest.TestCase):
    claims = lint_draft.load_claims(DEMO / ".rcs")

    def test_T017_author_limitations_replaced_by_writer_caveats(self) -> None:
        r = _rules((FIX / "H_author_limitations_replaced.md").read_text(encoding="utf-8"), self.claims)
        self.assertEqual(r.get("S1-author-limitation-missing"), "ERROR")

    def test_T017b_limitations_dropped_variant_E(self) -> None:
        r = _rules((PERT / "E_unsupported_interpretation.md").read_text(encoding="utf-8"), self.claims)
        self.assertEqual(r.get("S1-author-limitation-missing"), "ERROR")

    def test_T017c_attributed_limitations_are_clean(self) -> None:
        r = _rules((FIX / "I_attributed_limitations.md").read_text(encoding="utf-8"), self.claims)
        self.assertFalse({k for k in r if k.startswith(("S1", "S2"))})
        self.assertNotIn("ERROR", r.values())

    def test_T017d_writer_caveat_mixed_into_author_limitations_warns(self) -> None:
        md = ("## 4 Discussion\n\nWe note limits. Data are synthetic {L001}. Only level shifts {L004}. "
              "The window was not tuned {L003}.\n")
        self.assertEqual(_rules(md, self.claims).get("S1-caveat-attribution"), "WARN")

    def test_T017e_single_section_draft_not_checked(self) -> None:
        md = "## 3 Results\n\nRWN reduced MAE by 29% {C002}.\n"
        self.assertFalse({k for k in _rules(md, self.claims) if k.startswith(("S1", "S2"))})

    def test_T018_author_rationale_must_reach_intro_or_method(self) -> None:
        claims = dict(self.claims)
        claims["C008"] = {"id": "C008", "claim_type": "interpretation", "origin": "author_stated",
                          "rationale": "motivation"}
        base = "## 1 Introduction\n\nProblem {C001}.\n\n## 4 Discussion\n\nLimits {L001} {L004}.\n"
        self.assertEqual(_rules(base, claims).get("S2-author-rationale-missing"), "ERROR")
        late = base + "\nWe care because operators need it {C008}.\n"
        self.assertEqual(_rules(late, claims).get("S2-rationale-misplaced"), "WARN")
        early = base.replace("Problem {C001}.", "Problem {C001}. Operators need it {C008}.")
        self.assertFalse({k for k in _rules(early, claims) if k.startswith("S2")})


if __name__ == "__main__":
    unittest.main()
