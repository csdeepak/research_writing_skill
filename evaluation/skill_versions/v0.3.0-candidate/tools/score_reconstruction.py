#!/usr/bin/env python3
"""Compute reconstruction metrics from a RECON_GRADER grading.json.

grading.json format:
  {"questions": {"Q1": {"n1": "present", "n2": "weakened"}, ...},
   "intrusions": [{"question": "Q7", "text": "...", "tag": "unsupported_belief"}, ...]}

Metrics (docs/04_EVALUATION_FRAMEWORK.md section 2):
  RR  = (present + 0.5*weakened) / nuggets
  DR  = (overstated + contradicted) / nuggets
  IR  = unsupported_belief intrusions / nuggets
  MMF = clip(RR - DR - 0.5*IR, -1, 1)
  Core RR = RR over Q1, Q4, Q7, Q10, Q11

Usage: python tools/score_reconstruction.py grading.json [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CORE = {"Q1", "Q4", "Q7", "Q10", "Q11"}
LABELS = {"present", "weakened", "overstated", "contradicted", "absent"}


def score(grading: dict) -> dict:
    counts = {k: 0 for k in LABELS}
    core_counts = {k: 0 for k in LABELS}
    per_q = {}
    for q, nuggets in grading.get("questions", {}).items():
        qc = {k: 0 for k in LABELS}
        for label in nuggets.values():
            if label not in LABELS:
                raise ValueError(f"unknown label {label!r} in {q}")
            counts[label] += 1
            qc[label] += 1
            if q in CORE:
                core_counts[label] += 1
        n = sum(qc.values()) or 1
        per_q[q] = round((qc["present"] + 0.5 * qc["weakened"]) / n, 3)
    n = sum(counts.values())
    if n == 0:
        raise ValueError("no nuggets graded")
    rr = (counts["present"] + 0.5 * counts["weakened"]) / n
    dr = (counts["overstated"] + counts["contradicted"]) / n
    ir = sum(1 for i in grading.get("intrusions", []) if i.get("tag") == "unsupported_belief") / n
    cn = sum(core_counts.values()) or 1
    core_rr = (core_counts["present"] + 0.5 * core_counts["weakened"]) / cn
    mmf = max(-1.0, min(1.0, rr - dr - 0.5 * ir))
    return {"nuggets": n, "counts": counts, "RR": round(rr, 3), "DR": round(dr, 3), "IR": round(ir, 3),
            "MMF": round(mmf, 3), "CoreRR": round(core_rr, 3), "per_question_RR": per_q}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("grading")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = score(json.loads(Path(args.grading).read_text(encoding="utf-8")))
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"MMF {res['MMF']:+.3f} | RR {res['RR']:.3f} | CoreRR {res['CoreRR']:.3f} | "
              f"DR {res['DR']:.3f} | IR {res['IR']:.3f} | nuggets {res['nuggets']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
