#!/usr/bin/env python3
"""Qualitative sample selection by a declared rule (vNext Stage 2: M08).

Picks authentic examples for a qualitative figure -- successes, failures, edge cases and uncertain
cases -- by a rule you can state in the caption, instead of hand-picking attractive ones.

Input CSV columns: id, correct (1/0/true/false), confidence (0-1)
                   optional: permission (granted/...), identifying_data (true/false), prediction, ground_truth
Rule (deterministic for a given seed):
  success    correct, random
  failure    incorrect, random
  edge       confidence closest to --threshold (default 0.5), any outcome
  uncertain  lowest confidence
Samples without `permission: granted`, or with identifying data, are never selected; they are counted
as excluded with the reason. Output: a selection manifest to paste into the figure card (`samples`,
`selection_rule`); Stage 1 checks then block anything without permission.

Usage: python tools/select_samples.py samples.csv --per-category 2 --seed 0 [--out selection.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

TRUE = {"1", "true", "yes", "y"}


def select(rows: list[dict], k: int, seed: int, threshold: float) -> dict:
    ok, excluded = [], {"no_permission": 0, "identifying_data": 0}
    for r in rows:
        if str(r.get("permission", "granted")).strip().lower() != "granted":
            excluded["no_permission"] += 1
        elif str(r.get("identifying_data", "false")).strip().lower() in TRUE:
            excluded["identifying_data"] += 1
        else:
            ok.append(r)
    rng = random.Random(seed)
    conf = lambda r: float(r.get("confidence", 0) or 0)  # noqa: E731
    correct = lambda r: str(r.get("correct", "")).strip().lower() in TRUE  # noqa: E731
    pools = {
        "success": sorted([r for r in ok if correct(r)], key=lambda r: r["id"]),
        "failure": sorted([r for r in ok if not correct(r)], key=lambda r: r["id"]),
    }
    picked: dict[str, list[dict]] = {}
    used: set[str] = set()
    for cat in ("success", "failure"):
        cand = [r for r in pools[cat] if r["id"] not in used]
        picked[cat] = rng.sample(cand, min(k, len(cand)))
        used |= {r["id"] for r in picked[cat]}
    for cat, key in (("edge", lambda r: (abs(conf(r) - threshold), r["id"])), ("uncertain", lambda r: (conf(r), r["id"]))):
        cand = sorted([r for r in ok if r["id"] not in used], key=key)
        picked[cat] = cand[:k]
        used |= {r["id"] for r in picked[cat]}
    rule = (f"{k} random correct and {k} random incorrect cases (seed {seed}), the {k} cases with confidence closest "
            f"to {threshold}, and the {k} lowest-confidence cases; samples without usage permission or with identifying "
            "data were not eligible")
    samples = [{"id": r["id"], "category": cat, "correct": correct(r), "confidence": conf(r),
                "prediction": r.get("prediction"), "ground_truth": r.get("ground_truth"),
                "permission": "granted", "identifying_data": False}
               for cat, rs in picked.items() for r in rs]
    return {"selection_rule": rule, "seed": seed, "available": {c: len(p) for c, p in pools.items()},
            "eligible": len(ok), "excluded": excluded, "samples": samples,
            "caption_note": f"Examples chosen by rule: {rule}."}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--per-category", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    with open(a.csv, encoding="utf-8", newline="") as fh:
        rows = [dict(r) for r in csv.DictReader(fh)]
    res = select(rows, a.per_category, a.seed, a.threshold)
    text = json.dumps(res, indent=2)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
