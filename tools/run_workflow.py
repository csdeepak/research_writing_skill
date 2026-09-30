#!/usr/bin/env python3
"""Run every executable gate in order and keep an execution log (vNext Stage 4: "executed gate logs, versioned scripts").

  python tools/run_workflow.py gates .rcs --draft drafts/v001/paper.md
         [--round v001_1 --revised drafts/v002/paper.md]
         [--final paper/paper.md --before drafts/v002/paper.md --edited drafts/v003_tagged.md]

Runs, as separate processes (the same commands a person would type):
  G1  validate_artifacts --out G1_validate.json
  G3  lint_draft --rcs --out G3_lint.json;  verify_numbers --out G3_numbers.json
  V*  visuals render;  validate_visuals --draft --out V_visuals.json          (if a visual registry exists)
  G4  g4_check --round --revised --out G4_review.json                          (if --round)
  G5  validate --out G5_validate.json; lint --final --out G5_lint.json; verify_numbers --out G5_numbers.json;
      claim_invariance before edited --out G5_invariance.json                  (if --final)
Then records in state.json only what the reports show ("passed" / "failed" / "not_run"; V5 only with a human
review), re-checks with validate_artifacts (effective status), and appends every command to
.rcs/audits/gates/RUN_LOG.jsonl with exit code, report hash, and the SHA-256 of the tool that ran (versioned scripts).
G2 has no executable check and is left untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def _sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def run_gates(rcs: Path, root: Path, a) -> dict:
    gates = rcs / "audits" / "gates"
    gates.mkdir(parents=True, exist_ok=True)
    log = gates / "RUN_LOG.jsonl"
    py = sys.executable
    plan: list[tuple[str, str, list[str], Path | None]] = [
        ("G1", "validate_artifacts.py", [str(rcs), "--project-root", str(root), "--out", str(gates / "G1_validate.json")], gates / "G1_validate.json"),
    ]
    if a.draft:
        plan += [("G3", "lint_draft.py", [a.draft, "--rcs", str(rcs), "--out", str(gates / "G3_lint.json")], gates / "G3_lint.json"),
                 ("G3", "verify_numbers.py", [a.draft, "--rcs", str(rcs), "--project-root", str(root),
                                              "--out", str(gates / "G3_numbers.json")], gates / "G3_numbers.json")]
    if (rcs / "plan" / "visual_registry.json").exists():
        plan += [("V", "visuals.py", ["render", str(rcs), "--project-root", str(root)], None),
                 ("V", "validate_visuals.py", [str(rcs), "--project-root", str(root)] + (["--draft", a.draft] if a.draft else [])
                  + ["--out", str(gates / "V_visuals.json")], gates / "V_visuals.json")]
    if a.round:
        plan.append(("G4", "g4_check.py", [str(rcs), "--round", a.round] + (["--revised", a.revised] if a.revised else [])
                     + ["--out", str(gates / "G4_review.json")], gates / "G4_review.json"))
    if a.final:
        plan += [("G5", "validate_artifacts.py", [str(rcs), "--project-root", str(root), "--out", str(gates / "G5_validate.json")], gates / "G5_validate.json"),
                 ("G5", "lint_draft.py", [a.final, "--rcs", str(rcs), "--final", "--out", str(gates / "G5_lint.json")], gates / "G5_lint.json"),
                 ("G5", "verify_numbers.py", [a.final, "--rcs", str(rcs), "--project-root", str(root),
                                              "--out", str(gates / "G5_numbers.json")], gates / "G5_numbers.json")]
        if a.before and a.edited:
            plan.append(("G5", "claim_invariance.py", [a.before, a.edited, "--out", str(gates / "G5_invariance.json")],
                         gates / "G5_invariance.json"))
    # G1's validator also checks that the G3/V/G4 reports are fresh, so it must run after they are regenerated
    # (Stage 4 e2e: with G1 first, the first run after every draft change reported G1 failed on stale reports)
    g1 = [x for x in plan if x[0] == "G1"]
    rest = [x for x in plan if x[0] != "G1"]
    k = next((i for i, x in enumerate(rest) if x[0] == "G5"), len(rest))
    plan = rest[:k] + g1 + rest[k:]
    results: dict[str, list[dict]] = {}
    with open(log, "a", encoding="utf-8") as fh:
        for gate, tool, args, report in plan:
            proc = subprocess.run([py, str(TOOLS / tool)] + args, capture_output=True, text=True, encoding="utf-8")
            entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "gate": gate, "tool": tool,
                     "tool_sha256": _sha(TOOLS / tool), "args": args, "exit": proc.returncode,
                     "report": str(report.relative_to(rcs)).replace("\\", "/") if report else None,
                     "report_sha256": _sha(report) if report else None, "stdout_tail": proc.stdout[-400:]}
            fh.write(json.dumps(entry) + "\n")
            results.setdefault(gate, []).append(entry)
    # record honest statuses
    state_p = rcs / "state.json"
    state = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {}
    g = state.setdefault("gates", {})
    for gate in ("G1", "G3", "G4", "G5"):
        if gate in results:
            g[gate] = "passed" if all(e["exit"] == 0 for e in results[gate] if e["report"]) else "failed"
    if "V" in results and (gates / "V_visuals.json").exists():
        vs = json.loads((gates / "V_visuals.json").read_text(encoding="utf-8")).get("gates", {})
        for vg, info in vs.items():
            g[vg] = "passed" if info.get("status") == "PASSED" else info.get("status", "not_run").lower()
    state_p.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    # re-check with the validator: effective statuses
    sys.path.insert(0, str(TOOLS))
    import validate_artifacts as VA
    rep = VA.Report()
    eff = VA.check_gates(rcs, root, rep)
    for gate, st in eff.items():         # write back what the validator confirms, not what the exit codes suggested
        if gate in g:
            g[gate] = "passed" if st == "PASSED" else st.lower()
    state_p.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    summary = {"effective_gates": eff, "gate_errors": [i for i in rep.items if i["level"] == "ERROR"],
               "commands": sum(len(v) for v in results.values()), "log": str(log)}
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["gates"])
    ap.add_argument("rcs")
    ap.add_argument("--project-root")
    ap.add_argument("--draft")
    ap.add_argument("--round")
    ap.add_argument("--revised")
    ap.add_argument("--final")
    ap.add_argument("--before")
    ap.add_argument("--edited")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    s = run_gates(rcs, Path(a.project_root) if a.project_root else rcs.resolve().parent, a)
    print("effective gates: " + ", ".join(f"{k}={v}" for k, v in sorted(s["effective_gates"].items())))
    for e in s["gate_errors"]:
        print(f"  {e['where']}: {e['message'][:150]}")
    print(f"{s['commands']} command(s) logged to {s['log']}")
    return 0 if all(v == "PASSED" for k, v in s["effective_gates"].items() if k != "V5") else 1


if __name__ == "__main__":
    sys.exit(main())
