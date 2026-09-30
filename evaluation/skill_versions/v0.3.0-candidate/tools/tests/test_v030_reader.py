"""Regression tests for proposal 20260929-reader-comprehension (skill 0.3.0 candidate, vNext Stage 3).

T-036  M11 excess precision: flags decimals the interval doesn't support, accepts justified ones
T-037  M02 reader model: unknown terms, overload, prerequisite order, unaddressed misconception;
       persona checks are skipped without a reader model; synonym drift follows research_story.md section 5
T-038  M12 compression: numbers, scope, hedge, uncertainty and denominator drift caught; faithful skim passes
T-039  M13 key: pre-declared, frozen by hash, tampering detected; packets blinded (visual-only has no prose)
T-040  M13 scoring: Krippendorff's alpha (nominal) matches a hand-computed value; per-condition report
T-041  V5 human review: recorded review passes V5; a re-render after review makes it stale

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import audit_reader  # noqa: E402
import comprehension_kit as K  # noqa: E402
import record_review  # noqa: E402
import replay_fixtures  # noqa: E402
import skim_layer  # noqa: E402
import validate_visuals  # noqa: E402
import visuals  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "replay"


class PrecisionTests(unittest.TestCase):
    def test_T036(self) -> None:
        self.assertTrue(audit_reader.excess_precision("RAG reached 0.7513 (95% CI 0.6121 to 0.8905)."))
        self.assertFalse(audit_reader.excess_precision("RAG reached 0.75 (95% CI 0.61 to 0.89)."))
        self.assertTrue(audit_reader.excess_precision("MAE 0.4091 ± 0.007."))
        self.assertFalse(audit_reader.excess_precision("MAE 0.409 ± 0.007."))


class ReaderModelTests(unittest.TestCase):
    PERSONA = {"personas": [{"id": "B", "description": "adjacent", "known_terms": ["ML", "F1"], "new_term_budget": 1,
                             "prerequisite_concepts": [{"concept": "reranking", "needs": ["retrieval"]}],
                             "likely_misconceptions": [{"misconception": "higher exact match means better answers",
                                                        "trigger_terms": ["exact match"], "corrective_terms": ["token-F1"]}],
                             "reader_questions": ["What latency does memory add?"]}]}

    def rules(self, md: str, reader=None, ledger=None) -> set[str]:
        return {f["rule"] for f in audit_reader.audit(md, reader if reader is not None else self.PERSONA, ledger, None)}

    def test_T037_persona_checks(self) -> None:
        md = ("# T\n\n## Intro\n\nWe apply reranking with BM25 and a DPR encoder over an HNSW index.\n\n"
              "## Method\n\nRetrieval uses a corpus. Exact match rose to 0.62.\n")
        r = self.rules(md)
        self.assertTrue({"READER-UNKNOWN-TERM", "READER-TERM-OVERLOAD", "READER-PREREQ-ORDER", "READER-MISCONCEPTION",
                         "READER-QUESTION-UNANSWERED"} <= r)
        ok = ("# T\n\n## Intro\n\nRetrieval ranks documents; we then apply reranking with best matching 25 (BM25).\n\n"
              "Exact match counts identical answers, while token-F1 credits partial overlap. Memory adds latency.\n")
        self.assertFalse({"READER-PREREQ-ORDER", "READER-MISCONCEPTION", "READER-QUESTION-UNANSWERED"} & self.rules(ok))

    def test_T037b_no_reader_model_and_ledger(self) -> None:
        self.assertNotIn("READER-UNKNOWN-TERM", self.rules("We use BM25 and DPR.", reader={}))
        led = {"terms": [{"term": "BM25", "synonyms_forbidden": ["lexical baseline"]}]}
        self.assertIn("M11-SYNONYM-DRIFT", self.rules("The lexical baseline wins.", reader={}, ledger=led))


class SkimTests(unittest.TestCase):
    CLAIMS = {"C001": {"statement": "On one split, M reached 0.84 (95% CI 0.80 to 0.88); this suggests normalization helps."},
              "C002": {"statement": "M matched the baseline on 9 of 15 benchmarks."}}

    def test_T038(self) -> None:
        rules = lambda t: {f["rule"] for f in skim_layer.check(t, self.CLAIMS)}  # noqa: E731
        self.assertIn("M12-NUMBER-CHANGED", rules("M reached 0.86 on one split (95% CI) and suggests gains {C001}."))
        self.assertIn("M12-SCOPE-DROPPED", rules("M reached 0.84 (95% CI 0.80 to 0.88), which suggests gains {C001}."))
        self.assertIn("M12-SCOPE-WIDENED", rules("On one split and across datasets, M reached 0.84 (95% CI 0.80 to 0.88); this suggests gains {C001}."))
        self.assertIn("M12-HEDGE-DROPPED", rules("On one split M reached 0.84 (95% CI 0.80 to 0.88), so normalization helps {C001}."))
        self.assertIn("M12-UNCERTAINTY-DROPPED", rules("On one split, M reached 0.84; this suggests normalization helps {C001}."))
        self.assertIn("M12-DENOMINATOR-DROPPED", rules("M matched the baseline on 9 benchmarks {C002}."))
        self.assertEqual(rules("- On one split, M reached 0.84 (95% CI 0.80 to 0.88); this suggests gains {C001}.\n"
                               "- Figure 2: M matched the baseline on 9 of 15 benchmarks {C002}."), set())


class ComprehensionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        fx = next(f for f in replay_fixtures.load_fixtures(FIX) if f["id"] == "VIS-00")
        replay_fixtures.materialise(fx["files"], self.tmp)
        self.rcs = self.tmp / ".rcs"
        with contextlib.redirect_stdout(io.StringIO()):
            visuals.cmd_render(self.rcs, self.tmp, None)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_T039_key_frozen_and_packets_blind(self) -> None:
        key = K.build_key(self.rcs)
        self.assertIn("FOUND", key["questions"])
        K.verify_key(self.rcs)
        p = self.rcs / "evaluation" / "comprehension_key.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["questions"]["FOUND"][0]["text"] = "edited after freezing"
        p.write_text(json.dumps(d), encoding="utf-8")
        with self.assertRaises(SystemExit):
            K.verify_key(self.rcs)
        K.build_key(self.rcs)
        sealed = K.build_packets(self.rcs, self.tmp / "paper.md", self.tmp)
        conds = {v["condition"]: k for k, v in sealed.items()}
        vis = (self.rcs / "comprehension_runs" / "packets" / conds["visual_only"] / "packet.md").read_text(encoding="utf-8")
        full = (self.rcs / "comprehension_runs" / "packets" / conds["full"] / "packet.md").read_text(encoding="utf-8")
        self.assertNotIn("shows accuracy by system", vis)          # prose sentence absent in visual-only
        self.assertIn("shows accuracy by system", full)
        self.assertNotIn("{C001}", full)                           # claim tags stripped
        self.assertIn("Figure 1", vis)

    def test_T040_alpha_and_score(self) -> None:
        units = {"a": ["present", "absent"], "b": ["absent", "present"], "c": ["present", "present"], "d": ["absent", "absent"]}
        self.assertEqual(K.krippendorff_alpha_nominal(units), 0.125)   # hand-computed: 1 - 0.5/0.5714
        self.assertEqual(K.krippendorff_alpha_nominal({"a": ["present", "present"], "b": ["absent", "absent"]}), 1.0)
        K.build_key(self.rcs)
        K.build_packets(self.rcs, self.tmp / "paper.md", self.tmp)
        sealed = json.loads((self.rcs / "comprehension_runs" / "SEALED.json").read_text(encoding="utf-8"))
        resp = self.rcs / "comprehension_runs" / "responses.csv"
        with open(resp, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["participant", "packet", "question", "answer", "confidence", "minutes", "reader_type"])
            for pid in sealed:
                for q, _ in K.QUESTIONS:
                    w.writerow(["P1", pid, q, "D is most accurate at 0.80", "4", "3", "human"])
        sheet = K.build_sheets(self.rcs, resp)
        with open(sheet, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        for g, lab in (("g1", "present"), ("g2", "present")):
            with open(self.tmp / f"{g}.csv", "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                for r in rows:
                    w.writerow(dict(r, label=lab))
        rep = K.score(self.rcs, [self.tmp / "g1.csv", self.tmp / "g2.csv"])
        self.assertEqual(set(rep["by_condition"]), {"visual_only", "full"})
        self.assertEqual(rep["krippendorff_alpha_nominal"], 1.0)


class HumanReviewTests(ComprehensionTests):
    def test_T041_v5(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            record_review.main([str(self.rcs), "V001", "--reviewer", "A. Person", "--topic", "yes", "--takeaway", "yes",
                                "--detail", "yes"])
        rep = validate_visuals.Rep()
        st = validate_visuals.check(self.rcs, self.tmp, (self.tmp / "paper.md").read_text(encoding="utf-8"), rep)
        self.assertEqual(st["V5"], "PASSED")
        reg = self.rcs / "plan" / "visual_registry.json"
        d = json.loads(reg.read_text(encoding="utf-8"))
        d["visuals"][0]["render_sha256"] = "sha256:" + "0" * 64       # simulate a later re-render
        reg.write_text(json.dumps(d), encoding="utf-8")
        rep = validate_visuals.Rep()
        st = validate_visuals.check(self.rcs, self.tmp, (self.tmp / "paper.md").read_text(encoding="utf-8"), rep)
        self.assertNotEqual(st["V5"], "PASSED")
        self.assertTrue(any(i["code"] == "V5_REVIEW_STALE" for i in rep.items))

    test_T039_key_frozen_and_packets_blind = None  # type: ignore[assignment]
    test_T040_alpha_and_score = None  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
