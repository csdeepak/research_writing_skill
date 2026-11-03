"""Regression tests for proposal 20261102-unified-workflow, Stage D: the integrity benchmark (skill/tests/perturbations/).

T-105  every integrity variant in EXPECTED.json (integrity_variants) runs through the real lookup code, gate GL and the GI
       evidence on the demo project, with scripted index answers and no network: each planted defect is caught (a
       fabricated DOI, a DOI for the wrong paper, a retracted source, a hallucinated result, a method step with no basis)
       and the clean control raises nothing
T-106  the reviewer calibration set is unchanged by the integrity variants: calibrate still sees exactly the seven reviewer
       variants, and every integrity variant names a draft that exists

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import replay_fixtures  # noqa: E402
from rce_common import SKILL_DIR  # noqa: E402

PERT = SKILL_DIR / "tests" / "perturbations"
DEMO = SKILL_DIR / "examples" / "demo_project"


def demo_files() -> dict:
    return {p.relative_to(DEMO).as_posix(): p.read_text(encoding="utf-8") for p in DEMO.rglob("*") if p.is_file()}


def fixture(name: str, spec: dict) -> dict:
    files = demo_files()
    claims = json.loads(files[".rcs/claims/claim_evidence_map.json"])
    claims["claims"] += spec.get("claims_patch", [])
    files[".rcs/claims/claim_evidence_map.json"] = json.dumps(claims)
    files[".rcs/corpus/source_registry.json"] = json.dumps({"sources": spec["sources"]})
    files["paper.md"] = (PERT / name).read_text(encoding="utf-8")
    exp, forb = spec.get("expect", {}), spec.get("forbid", {})
    return {"id": name, "files": files, "checks": [
        {"tool": "verify", "index_responses": spec["index_responses"], "expect": exp.get("verify", []), "forbid": forb.get("verify", [])},
        {"tool": "gl", "draft": "paper.md", "expect": exp.get("gl", []), "forbid": forb.get("gl", [])},
        {"tool": "gi", "draft": "paper.md", "expect": exp.get("gi", []), "forbid": forb.get("gi", [])}]}


class IntegrityBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.expected = json.loads((PERT / "EXPECTED.json").read_text(encoding="utf-8"))

    def variants(self):
        return {k: v for k, v in self.expected["integrity_variants"].items() if not k.startswith("_")}

    def test_T105_every_planted_defect_is_caught_and_the_control_is_clean(self):
        for name, spec in self.variants().items():
            with self.subTest(variant=name):
                res = replay_fixtures.run_fixture(fixture(name, spec))
                bad = [c for c in res["checks"] if not c["ok"]]
                self.assertEqual(bad, [], f"{name}: {json.dumps(bad, indent=1)[:1500]}")

    def test_T105_each_defect_variant_plants_exactly_one_kind_of_failure(self):
        planted = {n: s for n, s in self.variants().items() if n != "A_clean.md"}
        self.assertEqual(sorted(planted), ["H_fabricated_doi.md", "I_wrong_paper_doi.md", "J_retracted_source.md",
                                           "K_hallucinated_result.md", "L_method_without_basis.md"])
        for name, spec in planted.items():
            self.assertTrue(any(spec["expect"].get(t) for t in ("verify", "gl", "gi")), name)
            self.assertTrue(set(spec["verifier_expected"].values()) <= {"SUSPECTED"}, name)

    def test_T106_reviewer_calibration_set_is_unchanged(self):
        self.assertEqual(sorted(self.expected["variants"]), ["A_clean.md", "B_poor_ordering.md", "C_jargon.md", "D_result_dumping.md",
                                                              "E_unsupported_interpretation.md", "F_buried_contribution.md", "G_citation_misuse.md"])
        for name in self.variants():
            self.assertTrue((PERT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
