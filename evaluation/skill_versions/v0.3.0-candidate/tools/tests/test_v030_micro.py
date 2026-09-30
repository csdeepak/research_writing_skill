"""T-046: tier-2 micro-reconstruction scoring is deterministic (RECOMMENDED_NEXT_VERSION Part D, tier 2)."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import micro_recon  # noqa: E402

FX = {"id": "T", "passages": {"A": "a", "B": "b"},
      "questions": [{"q": "size?", "required": [["325"]], "forbidden": ["350"]},
                    {"q": "who?", "required": [["rag"], ["0.751", "0.75"]], "forbidden": ["significant"]}]}


class MicroTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "fx").mkdir()
        (self.tmp / "fx" / "T.json").write_text(json.dumps(FX), encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def answer(self, ver: str, answers: list[str]) -> None:
        d = self.tmp / "ans" / f"mr-T-{ver}-0"
        d.mkdir(parents=True)
        (d / "output.txt").write_text(json.dumps({"answers": answers}), encoding="utf-8")

    def test_T046(self) -> None:
        self.assertTrue(micro_recon.conveyed("It is 1,250 KB", ["1250"]))
        self.assertTrue(micro_recon.conveyed("RAG scored 0.75", ["0.751", "0.75"]))
        self.assertFalse(micro_recon.conveyed("not stated", ["325"]))
        self.answer("A", ["under 350 KB", "RAG, 0.751, significantly better"])
        self.answer("B", ["325 KB", "RAG at 0.75"])
        r = micro_recon.score(self.tmp / "fx", self.tmp / "ans")["fixtures"]["T"]
        self.assertEqual(r["A"]["recall"], round(2 / 3, 3))
        self.assertEqual(r["A"]["overstatements"], 2)
        self.assertEqual(r["B"]["recall"], 1.0)
        self.assertEqual(r["B"]["overstatements"], 0)
        self.assertEqual(r["B_minus_A_recall"], round(1.0 - round(2 / 3, 3), 3))


if __name__ == "__main__":
    unittest.main()
