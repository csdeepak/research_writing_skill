#!/usr/bin/env python3
"""Calibrate the SKILL's own reviewer (v0.3.0-candidate agents/review_agent.md) on the planted-defect benchmark.

Phase 4 validated the harness reviewer prompt (review_lib.REVIEWER_SYSTEM). The skill's in-loop reviewer is a
different prompt, and v0.3.0 changed it (12 questions restated verbatim), so its own calibration requirement
("detect planted defects with >= 90% sensitivity and <= 10% false alarms on the clean variant", review_agent.md)
had never been checked. This reuses Phase 4's blinded packets (random ids, sealed mapping, D-07 substitution).

  make    one task folder per packet: review_agent.md + the two output schemas + the packet files, inlined
          (<RCE_TMP>/rce_tasks/v030cal/<pid>/prompt.md); the reviewer reads only that and writes output.txt
  score   schema-validate every output; dimension sensitivity vs A (expected dims >= 1 lower), false alarms on A
          (dims <= 2), same definitions as reviewer_validation.py; writes v030_calibration.json

Usage: python evaluation/reviewer_validation/v030_calibrate.py make|score
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAND = HERE.parents[0] / "skill_versions" / "v0.3.0-candidate"
TASKS = Path(os.environ.get("RCE_TMP", tempfile.gettempdir())) / "rce_tasks" / "v030cal"
sys.path.insert(0, str(CAND / "tools"))
from rce_common import load_schema, validate  # noqa: E402

MAPPING = json.loads((HERE / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CAND / "tests" / "perturbations" / "EXPECTED.json").read_text(encoding="utf-8"))["variants"]
DIMS = load_schema("diagnostics.schema.json")
DIM_NAMES = re.findall(r'"(\w+)"', json.dumps(DIMS).split('"problem"', 1)[1].split("]", 1)[0])
DIM_NAMES = ["problem"] + DIM_NAMES
SENS_MIN, FA_MAX = 0.90, 0.10


def make() -> None:
    head = ["# ROLE INSTRUCTIONS (treat as your system prompt)\n", (CAND / "agents" / "review_agent.md").read_text(encoding="utf-8"),
            "\n\n# OUTPUT SCHEMAS\n## reconstruction.schema.json\n", (CAND / "schemas" / "reconstruction.schema.json").read_text(encoding="utf-8"),
            "\n## diagnostics.schema.json\n", (CAND / "schemas" / "diagnostics.schema.json").read_text(encoding="utf-8")]
    for pid in sorted(MAPPING):
        pkt = HERE / "packets" / pid
        parts = head + [f"\n\n# YOUR PACKET (packet_id: {pid}); these are the only files you may use\n"]
        for f in sorted(p for p in pkt.iterdir() if p.is_file()):
            parts.append(f"\n## FILE {f.name}\n\n{f.read_text(encoding='utf-8')}\n")
        parts.append('\n---\nWrite ONE JSON object only (no code fences) to the file output.txt in this same folder: '
                     '{"reconstruction": <object valid against reconstruction.schema.json>, "diagnostics": <object valid '
                     'against diagnostics.schema.json>, "reviewer_notes_private": "<your free reasoning>"}. Use packet_id '
                     f'"{pid}" in both objects. Give every one of the 20 dimensions at least one finding.')
        d = TASKS / pid
        d.mkdir(parents=True, exist_ok=True)
        (d / "prompt.md").write_text("".join(parts), encoding="utf-8")
        print(d / "prompt.md")


def dims_of(diag: dict) -> dict[str, int]:
    out: dict[str, int] = {}
    for f in diag.get("findings", []):
        if isinstance(f.get("score"), int):
            out[f["dimension"]] = min(out.get(f["dimension"], 9), f["score"])   # most severe finding (as Phase 4)
    return out


def score() -> dict:
    rows = {}
    for pid, m in MAPPING.items():
        f = TASKS / pid / "output.txt"
        if not f.exists():
            rows[m["variant"]] = {"pid": pid, "missing": True}
            continue
        txt = f.read_text(encoding="utf-8")
        obj, _ = json.JSONDecoder().raw_decode(txt[txt.index("{"):])   # tolerate trailing text after the object
        errs = [f"diagnostics: {e}" for e in validate(obj["diagnostics"], load_schema("diagnostics.schema.json"))]
        errs += [f"reconstruction: {e}" for e in validate(obj["reconstruction"], load_schema("reconstruction.schema.json"))]
        d = dims_of(obj["diagnostics"])
        rows[m["variant"]] = {"pid": pid, "dims": d, "schema_problems": len(errs), "missing_dims": [x for x in DIM_NAMES if x not in d],
                              "n_inference_issues": len(obj["diagnostics"].get("inference_issues", [])),
                              "reconstruction_keys": sorted(obj["reconstruction"].get("answers", {}))}
    base = rows.get("A_clean.md", {}).get("dims")
    det = []
    for v, r in sorted(rows.items()):
        if v == "A_clean.md" or "dims" not in r or not base:
            continue
        exp = EXPECTED[v]["reviewer_expected_drop"]
        hits = [x for x in exp if r["dims"].get(x, 9) <= base.get(x, -9) - 1]
        det.append({"variant": v, "expected": exp, "detected": hits, "missed": [x for x in exp if x not in hits],
                    "sensitivity": round(len(hits) / len(exp), 3) if exp else None,
                    "mean_dim": round(statistics.mean(r["dims"].values()), 2)})
    fa = [x for x, s in (base or {}).items() if s <= 2]
    sens = [x["sensitivity"] for x in det if x["sensitivity"] is not None]
    out = {"reviewer": "v0.3.0-candidate agents/review_agent.md (Opus subagent, 1 seed)",
           "thresholds": {"sensitivity_min": SENS_MIN, "false_alarm_max": FA_MAX},
           "mean_dimension_sensitivity": round(statistics.mean(sens), 3) if sens else None,
           "false_alarm_dims_on_A": fa, "false_alarm_rate_on_A": round(len(fa) / 20, 3) if base else None,
           "mean_dim_A": round(statistics.mean(base.values()), 2) if base else None,
           "reconstruction_uses_Q1_Q12": all(r.get("reconstruction_keys") == sorted(f"Q{i}" for i in range(1, 13))
                                             for r in rows.values() if "dims" in r),
           "phase4_reference_F1_harness_prompt": {"mean_dimension_sensitivity": 0.956, "false_alarm_rate_on_A": 0.05},
           "detection": det, "per_variant": rows}
    ok = out["mean_dimension_sensitivity"] is not None and out["false_alarm_rate_on_A"] is not None
    out["calibrated"] = ok and out["mean_dimension_sensitivity"] >= SENS_MIN and out["false_alarm_rate_on_A"] <= FA_MAX
    (HERE / "scores").mkdir(exist_ok=True)
    (HERE / "scores" / "v030_calibration.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("mean_dimension_sensitivity", "false_alarm_rate_on_A", "false_alarm_dims_on_A",
                                          "mean_dim_A", "reconstruction_uses_Q1_Q12", "calibrated")}, indent=1))
    for x in det:
        print(f"  {x['variant']:32s} sens {x['sensitivity']}  missed {x['missed']}")
    return out


if __name__ == "__main__":
    {"make": make, "score": score}[sys.argv[1]]()
