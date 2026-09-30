#!/usr/bin/env python3
"""Paragraph-level micro-reconstruction tests: tier 2 of the self-improvement loop (RECOMMENDED_NEXT_VERSION Part D).

Tier 1 (tools/replay_fixtures.py) is free but can only test CHECKERS: past drafts were written under the old
instructions. Tier 3 (a full live A/B) can test WRITING instructions but is expensive. Tier 2 sits in between: for one
paragraph at a time, a small reader answers a few questions from that paragraph alone, and the answer is graded
DETERMINISTICALLY against what the paragraph must convey (required facts) and must not suggest (forbidden overstatement).

Fixture (tools/tests/fixtures/micro/*.json):
  {"id": "...", "origin": "...",
   "passages": {"A": "<paragraph as currently written>", "B": "<paragraph under a proposed rule>"},   # B optional
   "questions": [{"q": "...", "required": [["0.751", "0.75"], ["RAG"]], "forbidden": ["significant", "outperforms all"]}]}
  A required item is a list of alternatives; it is conveyed if ANY alternative occurs in the answer (case-insensitive,
  numbers normalised). A forbidden string in the answer means the reader came away believing something stronger.

  make  --fixtures DIR --out TASKDIR [--reps 2]   one reader task per (fixture, passage, rep); the reader sees one passage
  score --fixtures DIR --answers TASKDIR          recall and overstatement per passage version; B - A per fixture

Cheap by design (a few hundred tokens per task), and noisy by design too: use it to screen writing-rule candidates
before a tier-3 live test, never to accept one.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

READER = ("Read the paragraph below once. Answer each question using only what the paragraph says, in one or two "
          "sentences. If the paragraph does not say, answer 'not stated'. Reply with ONE JSON object only: "
          '{"answers": ["...", "..."]} in question order.')


def _norm(t: str) -> str:
    t = t.lower().replace("−", "-").replace("–", "-")
    return re.sub(r"(\d),(\d{3})", r"\1\2", t)


def conveyed(answer: str, alternatives: list[str]) -> bool:
    a = _norm(answer)
    return any(_norm(x) in a for x in alternatives)


def load(d: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))]


def make(fixtures: Path, out: Path, reps: int) -> list[str]:
    ids = []
    for fx in load(fixtures):
        qs = "\n".join(f"{i + 1}. {q['q']}" for i, q in enumerate(fx["questions"]))
        for ver, passage in fx["passages"].items():
            for r in range(reps):
                tid = f"mr-{fx['id']}-{ver}-{r}"
                d = out / tid
                d.mkdir(parents=True, exist_ok=True)
                (d / "prompt.md").write_text(f"{READER}\n\n# PARAGRAPH\n{passage}\n\n# QUESTIONS\n{qs}\n\n---\nWrite your reply "
                                             "(only the JSON) to output.txt in this same folder.", encoding="utf-8")
                ids.append(tid)
    return ids


def score(fixtures: Path, answers: Path) -> dict:
    res = {}
    for fx in load(fixtures):
        per_ver: dict[str, list[dict]] = {}
        for ver in fx["passages"]:
            for d in sorted(answers.glob(f"mr-{fx['id']}-{ver}-*")):
                txt = (d / "output.txt").read_text(encoding="utf-8") if (d / "output.txt").exists() else ""
                m = re.search(r"\{.*\}", txt, re.S)
                ans = (json.loads(m.group(0)).get("answers", []) if m else [])
                req = hit = over = 0
                for i, q in enumerate(fx["questions"]):
                    a = ans[i] if i < len(ans) else ""
                    for alts in q.get("required", []):
                        req += 1
                        hit += conveyed(a, alts)
                    over += sum(1 for f in q.get("forbidden", []) if _norm(f) in _norm(a))
                per_ver.setdefault(ver, []).append({"recall": hit / req if req else None, "overstatements": over})
        summ = {v: {"runs": len(rs), "recall": round(statistics.mean(r["recall"] for r in rs if r["recall"] is not None), 3)
                    if rs else None, "overstatements": sum(r["overstatements"] for r in rs)} for v, rs in per_ver.items()}
        if "A" in summ and "B" in summ and summ["A"]["recall"] is not None and summ["B"]["recall"] is not None:
            summ["B_minus_A_recall"] = round(summ["B"]["recall"] - summ["A"]["recall"], 3)
        res[fx["id"]] = summ
    deltas = [v["B_minus_A_recall"] for v in res.values() if "B_minus_A_recall" in v]
    return {"fixtures": res, "mean_B_minus_A": round(statistics.mean(deltas), 3) if deltas else None,
            "note": "Tier-2 screen: noisy, few readers. Promising candidates go to a tier-3 live test; nothing is accepted here."}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make", "score"])
    ap.add_argument("--fixtures", default=str(Path(__file__).resolve().parent / "tests" / "fixtures" / "micro"))
    ap.add_argument("--out")
    ap.add_argument("--answers")
    ap.add_argument("--reps", type=int, default=2)
    a = ap.parse_args(argv)
    if a.cmd == "make":
        print("\n".join(make(Path(a.fixtures), Path(a.out), a.reps)))
    else:
        print(json.dumps(score(Path(a.fixtures), Path(a.answers)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
