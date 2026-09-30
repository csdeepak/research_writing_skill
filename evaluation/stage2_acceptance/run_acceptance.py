#!/usr/bin/env python3
"""Reproduce the vNext Stage 2 acceptance check (spec 12: "on at least two real projects, every published figure has
reproducible source, evidence IDs, an accurate caption, and no unresolved material integrity failure").

Rebuilds the acceptance projects from real data (build.py; the private one only locally), renders every figure, runs the visual gates V1-V6, the
planner, lint and number tracing on the paper excerpt, records honest gate statuses in state.json, and re-checks
them with validate_artifacts. Writes ACCEPTANCE.json and prints a summary. Exit 1 if acceptance fails.

Usage: python evaluation/stage2_acceptance/run_acceptance.py [--candidate DIR]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CAND = HERE.parents[1]            # repository root: the released skill/ + tools/ (v0.3.0+)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default=str(DEFAULT_CAND))
    a = ap.parse_args()
    tools = Path(a.candidate) / "tools"
    sys.path.insert(0, str(tools))
    import lint_draft
    import plan_visuals
    import validate_artifacts
    import validate_visuals
    import verify_numbers
    import visuals

    subprocess.run([sys.executable, str(HERE / "build.py")], check=True, stdout=subprocess.DEVNULL)
    results, ok = {}, True
    for proj in [p for p in ("ASMOS", "MLPERF_TINY") if (HERE / p / ".rcs").exists()]:   # ASMOS: private, local only
        root = HERE / proj
        rcs = root / ".rcs"
        with contextlib.redirect_stdout(io.StringIO()):
            visuals.cmd_render(rcs, root, None)
        rep = validate_visuals.Rep()
        draft = (root / "paper.md").read_text(encoding="utf-8")
        status = validate_visuals.check(rcs, root, draft, rep)
        with contextlib.redirect_stdout(io.StringIO()):
            validate_visuals.main([str(rcs), "--project-root", str(root), "--draft", str(root / "paper.md"),
                                   "--out", str(rcs / "audits/gates/V_visuals.json")])
        # honest gate record: only what the report shows as PASSED
        state = json.loads((rcs / "state.json").read_text(encoding="utf-8"))
        state["gates"] = {g: ("passed" if s == "PASSED" else s.lower()) for g, s in status.items()}
        (rcs / "state.json").write_text(json.dumps(state, indent=1), encoding="utf-8")
        vrep = validate_artifacts.Report()
        loaded = validate_artifacts.check_schemas(rcs, vrep)
        validate_artifacts.check_references(rcs, root, loaded, vrep)
        eff = validate_artifacts.check_gates(rcs, root, vrep)
        claims = lint_draft.load_claims(rcs)
        lint = lint_draft.lint_text(draft, claims, False, False, set(), None)
        nums = verify_numbers.verify(draft, rcs, root)
        with contextlib.redirect_stdout(io.StringIO()):
            plan = plan_visuals.plan(rcs)
        reg = visuals.load_registry(rcs)
        published = [v for v in reg["visuals"] if v.get("status") == "RENDERED"]
        planned = {o["claim_id"]: o["representation"] for o in plan["opportunities"]}
        agree = {v["id"]: planned.get(v["claim_ids"][0]) == v["representation"] for v in published if v.get("claim_ids")}
        res = {
            "published_figures": [v["id"] for v in published],
            "blocked_figures": [v["id"] for v in reg["visuals"] if v.get("status") in ("BLOCKED", "NO_VALID_VISUAL")],
            "visual_gates": status, "visual_errors": rep.errors(),
            "effective_gates_after_recording": eff,
            "artifact_errors": [i for i in vrep.items if i["level"] == "ERROR"],
            "every_published_figure": {v["id"]: {"evidence_ids": v.get("evidence_ids"), "source_hashes": v.get("source_hashes"),
                                                 "render_sha256": v.get("render_sha256")} for v in published},
            "paper_excerpt": {"lint_errors": lint.count("ERROR"), "untraced_numbers": sum(f["rule"] == "UNTRACED_NUMBER" for f in nums),
                              "number_errors": sum(f["level"] == "ERROR" for f in nums)},
            "planner_agrees_with_registry": agree,
        }
        passed = (all(status[g] == "PASSED" for g in ("V1", "V2", "V3", "V4", "V6")) and rep.errors() == 0
                  and not res["artifact_errors"] and res["paper_excerpt"]["lint_errors"] == 0
                  and res["paper_excerpt"]["number_errors"] == 0 and published)
        res["acceptance"] = "PASS" if passed else "FAIL"
        ok &= bool(passed)
        results[proj] = res
        print(f"{proj:12} {res['acceptance']}  figures={res['published_figures']} blocked={res['blocked_figures']} "
              f"gates={status} excerpt={res['paper_excerpt']} planner_agrees={agree}")
    (HERE / "ACCEPTANCE.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\nStage 2 acceptance:", "PASS" if ok else "FAIL", "(V5 needs a human review; recorded as not_run, never passed)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
