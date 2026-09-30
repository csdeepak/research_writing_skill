#!/usr/bin/env python3
"""Apply the PRE-REGISTERED D-29 rule to the tier-3 A/B (skill v0.1.0 vs candidate v0.3.0).

Run after compare.py analyze and intrusion_verify.py analyze. Reads scores/intrusion_sensitivity.json (MMF_src) and
scores/per_review.json (secondaries); writes scores/ab3_decision.json and prints the verdict.

  effect_p = MMF_src(skillv030ab3) - MMF_src(skillv010ab3)
  noise_p  = max(0.05, |MMF_src(skillv010ab3) - MMF_src(skillv010sub)|)
  better_p: effect_p > noise_p      worse_p: effect_p < -noise_p
  SHOWN (benefit)   iff better on >= 2/3 and worse on none
  SHOWN (regression) iff worse on >= 2/3 and better on none
  otherwise NOT SHOWN
The rule is fixed in logs/DECISIONS.md D-29 (written before any draft). Do not edit the constants.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402

CMP = RL.ROOT / "evaluation" / "results" / "comparison"
PROJECTS = ("OPENHANDS", "MLPERF_TINY", "BEIR")
A, B, REF = "skillv010ab3", "skillv030ab3", "skillv010sub"
NOISE_FLOOR = 0.05
QS = ("Q11", "Q2", "Q5", "Q7", "Q9")


def main() -> int:
    sens = json.loads((CMP / "scores" / "intrusion_sensitivity.json").read_text(encoding="utf-8"))["per_review"]
    per = json.loads((CMP / "scores" / "per_review.json").read_text(encoding="utf-8"))
    src = {(r["project"], r["condition"]): r for r in sens}
    rev = {(r["project"], r["condition"]): r for r in per if r["family"] == "F1"}
    rows, missing = [], []
    for p in PROJECTS:
        if not all((p, c) in src for c in (A, B, REF)):
            missing.append(p)
            continue
        a, b, ref = src[(p, A)], src[(p, B)], src[(p, REF)]
        effect = round(b["MMF_src"] - a["MMF_src"], 3)
        noise = round(max(NOISE_FLOOR, abs(a["MMF_src"] - ref["MMF_src"])), 3)
        row = {"project": p, "MMF_src_v010": a["MMF_src"], "MMF_src_v030": b["MMF_src"], "MMF_src_v010_phase9": ref["MMF_src"],
               "effect": effect, "noise": noise,
               "call": "better" if effect > noise else ("worse" if effect < -noise else "no detectable difference")}
        for k in ("RR", "DR", "IR", "IR_src", "MMF"):
            row[f"{k}_v010"], row[f"{k}_v030"] = a[k], b[k]
        for cond, tag in ((A, "v010"), (B, "v030")):
            r = rev.get((p, cond), {})
            pq = (r.get("recon_sonnet") or {}).get("per_question_RR", {})
            row[f"recall_{tag}"] = {q: pq.get(q) for q in QS}
            row[f"words_{tag}"] = r.get("words_main")
            row[f"markers_{tag}"] = r.get("markers_removed")
        rows.append(row)
    if missing:
        print(f"incomplete: no scores yet for {missing}")
    nb = sum(r["call"] == "better" for r in rows)
    nw = sum(r["call"] == "worse" for r in rows)
    if len(rows) < len(PROJECTS):
        verdict = "INCOMPLETE"
    elif nb >= 2 and nw == 0:
        verdict = "READER BENEFIT SHOWN"
    elif nw >= 2 and nb == 0:
        verdict = "REGRESSION SHOWN"
    else:
        verdict = "NOT SHOWN (no detectable difference at n=3, single seed)"
    out = {"rule": "D-29 (pre-registered)", "verdict": verdict, "better": nb, "worse": nw, "projects": rows}
    (CMP / "scores" / "ab3_decision.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for r in rows:
        print(f"{r['project']:12s} v010 {r['MMF_src_v010']:+.3f}  v030 {r['MMF_src_v030']:+.3f}  effect {r['effect']:+.3f}  "
              f"noise {r['noise']:.3f}  -> {r['call']}")
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
