#!/usr/bin/env python3
"""Visual opportunity planner (vNext Stage 2: M04 opportunities, M06 table-vs-figure, M10 selection).

For every factual claim, decide from the *shape of its evidence* whether a visual would help the reader,
and which form, before anything is drawn:

  PROSE     <= 3 values, one series, no uncertainty   -> say it in a sentence (no visual)
  TABLE     many attributes per category, or exact lookup
  line      values over an ordered numeric variable (trend)
  dot_ci    categories with an uncertainty interval
  bar_h     non-negative magnitudes across categories, no interval
  diagram   method/architecture evidence (STRUCTURAL; components must be traced to code/docs)

Ranking (M10): claims bound to the paper spine first, then hard evidence, then more values. The top
`max_main_figures` (state.json, default 6) go to the main text; the rest to the supplement. A claim that
carries negative results is never demoted (`must_show`).

Output: .rcs/plan/visual_opportunities.json. It proposes; it never writes the registry or draws. The
reader question it drafts is a template and is marked `needs_author_wording`.

Usage: python tools/plan_visuals.py .rcs [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NUM = (int, float)
STRUCT_RE = re.compile(r"\b(architecture|pipeline|workflow|system design|module|component|data flow)\b", re.I)


def _is_num(v) -> bool:
    return isinstance(v, NUM) and not isinstance(v, bool)


STAT_KEYS = {"n", "value", "mean", "std", "count", "p", "p_value", "W", "ci", "ci95", "spread", "err", "metric", "test",
             "run_id", "unit", "design", "matched"}


def shape(values: list) -> dict:
    """Describe the evidence values of one claim: categories (x positions), series (one per evidence item
    that spans the categories), whether x is ordered, and whether intervals exist."""
    xs: set[str] = set()
    series = singles = 0
    uncertainty = ordered = False
    attrs_per_cat = 1
    for v in values:
        if not isinstance(v, dict):
            if _is_num(v):
                singles += 1
            continue
        if any(k in v for k in ("std", "ci", "ci95", "spread", "err")):
            uncertainty = True
        by = [x for k, x in v.items() if k.startswith("by_") and isinstance(x, dict)]
        cat = {k: x for k, x in v.items() if k not in STAT_KEYS and not k.startswith("by_")
               and (_is_num(x) or (isinstance(x, list) and x and all(_is_num(i) for i in x)) or isinstance(x, dict))}
        if by:
            for x in by:
                ordered = all(re.fullmatch(r"-?\d+(\.\d+)?", str(kk)) for kk in x)
                xs |= {str(kk) for kk in x}
                uncertainty |= any(isinstance(xx, list) and len(xx) >= 2 for xx in x.values())
            series += 1
        elif len(cat) >= 2:
            xs |= set(cat)
            series += 1
            for x in cat.values():
                if isinstance(x, list) and len(x) >= 3:
                    uncertainty = True
                if isinstance(x, dict):
                    attrs_per_cat = max(attrs_per_cat, len([i for i in x.values() if _is_num(i)]))
                    uncertainty |= bool({"ci95", "std", "ci"} & set(x))
        elif _is_num(v.get("value")) or _is_num(v.get("mean")):
            singles += 1
    if xs:
        k, series = len(xs), max(series, 1)
    else:
        k, series = singles, 1
    return {"categories": k, "series": series, "points": k * series, "uncertainty": uncertainty, "ordered": ordered,
            "attrs_per_category": attrs_per_cat}


def decide(sh: dict) -> tuple[str, str, str]:
    k, pts = sh["categories"], sh["points"]
    if k == 0:
        return "none", "", "no numeric evidence"
    if sh["attrs_per_category"] >= 4:
        return "TABLE", "ANALYTICAL", f"{sh['attrs_per_category']} attributes per category: exact lookup reads best as a table"
    if pts <= 3:
        return "PROSE", "", f"{pts} value(s): a sentence is clearer than a figure (figure_table_rules.md section 2)"
    if sh["ordered"] and k >= 3:
        return "line", "ANALYTICAL", f"{k} ordered x values x {sh['series']} series: a trend"
    if sh["uncertainty"]:
        return "dot_ci", "COMPARATIVE", f"{k} categories x {sh['series']} series with intervals: show the uncertainty"
    return "bar_h", "COMPARATIVE", f"{k} non-negative magnitudes across categories"


def plan(rcs: Path) -> dict:
    load = lambda p, d: json.loads(p.read_text(encoding="utf-8")) if p.exists() else d  # noqa: E731
    ev = {e["id"]: e for e in load(rcs / "evidence" / "research_evidence.json", {}).get("items", [])}
    cm = load(rcs / "claims" / "claim_evidence_map.json", {})
    spine = (rcs / "story" / "spine.md").read_text(encoding="utf-8") if (rcs / "story" / "spine.md").exists() else ""
    state = load(rcs / "state.json", {})
    budget = state.get("max_main_figures", 6)
    reg_claims = {c for v in load(rcs / "plan" / "visual_registry.json", {}).get("visuals", []) for c in v.get("claim_ids", [])}
    ops = []
    for c in cm.get("claims", []):
        if c.get("claim_type") not in ("measured", "derived", "observed") or c.get("status") == "BLOCKED":
            continue
        items = [ev[r] for r in c.get("evidence", []) if r in ev and ev[r].get("status") != "superseded"]
        sh = shape([i.get("value") for i in items])
        rep, kind, why = decide(sh)
        if rep == "none":
            continue
        adverse = bool(c.get("negative_results")) or any(i.get("kind") == "negative_result" for i in items)
        score = (3 if c["id"] in spine else 0) + (1 if items and all(i.get("strength") == "hard" for i in items) else 0) \
            + min(sh["categories"], 6) / 6 + (2 if adverse else 0)
        ops.append({"claim_id": c["id"], "evidence_ids": [i["id"] for i in items], "representation": rep, "kind": kind,
                    "reason": why, "shape": sh, "must_show": adverse, "already_in_registry": c["id"] in reg_claims,
                    "reader_question": f"What does the evidence behind {c['id']} show? ({c.get('statement', '')[:80]})",
                    "needs_author_wording": True, "score": round(score, 2)})
    for e in ev.values():
        if e.get("kind") == "method_detail" and STRUCT_RE.search(e.get("summary", "")):
            ops.append({"claim_id": None, "evidence_ids": [e["id"]], "representation": "diagram", "kind": "STRUCTURAL",
                        "reason": "architecture/pipeline description: a traced schematic may help (components must "
                                  "resolve to code/docs)", "must_show": False, "already_in_registry": False,
                        "reader_question": "How do the system's parts fit together?", "needs_author_wording": True,
                        "score": 1.5})
    visual = [o for o in ops if o["representation"] not in ("PROSE",)]
    visual.sort(key=lambda o: (-o["must_show"], -o["score"]))
    main = 0
    for o in visual:
        if o["must_show"] or main < budget:
            o["tier"] = "main"
            main += 1
        else:
            o["tier"] = "supplementary"
    for o in ops:
        o.setdefault("tier", "none (prose)")
    out = {"budget_main": budget, "opportunities": ops,
           "summary": {"claims_considered": len(cm.get("claims", [])), "visual": len(visual),
                       "prose_only": sum(o["representation"] == "PROSE" for o in ops), "main": main},
           "note": "Proposals only. Nothing is drawn until a registry entry with real source data passes V1-V4."}
    (rcs / "plan").mkdir(parents=True, exist_ok=True)
    (rcs / "plan" / "visual_opportunities.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    out = plan(Path(a.rcs))
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        for o in out["opportunities"]:
            print(f"{str(o['claim_id']):6} {o['representation']:8} {o.get('kind') or '-':12} {o['tier']:14} "
                  f"{'MUST-SHOW ' if o['must_show'] else ''}{o['reason']}")
        print(f"\n{out['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
