#!/usr/bin/env python3
"""RCE command-line entry point (stdlib only). Each command runs one of the tools in this folder.

  check PROJECT [--draft D] [--final]   run every deterministic check on a project (and a draft) and summarise:
                                        artifacts (G1), figures (V1-V6), draft lint and number tracing (G3/G5)
  gates PROJECT/.rcs ...                the gate runner (records only tool-confirmed statuses)   -> run_workflow.py gates
  validate PROJECT/.rcs                 artifact validation                                      -> validate_artifacts.py
  lint DRAFT --rcs .rcs                 draft lint (claims, licenses, citations, attribution)     -> lint_draft.py
  numbers DRAFT --rcs .rcs              trace every number to evidence                           -> verify_numbers.py
  visuals .rcs                          figure gates V1-V6                                      -> validate_visuals.py
  review / calibrate / run-tasks        single-shot roles on any model (.rcs/models.json)        -> rce_roles.py
  cases                                 validate the failure-case archive                        -> validate_cases.py
  package                               build + validate the skill ZIP                          -> package_skill.py
  audit                                 repository audit (secrets, paths, private markers, links)-> check_repo.py

Usage: python tools/rce.py <command> [args...]
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PASS = {"gates": ["run_workflow.py", "gates"], "validate": ["validate_artifacts.py"], "lint": ["lint_draft.py"],
        "numbers": ["verify_numbers.py"], "visuals": ["validate_visuals.py"], "review": ["rce_roles.py", "review"],
        "calibrate": ["rce_roles.py", "calibrate"], "run-tasks": ["rce_roles.py", "run-tasks"],
        "cases": ["validate_cases.py"], "package": ["package_skill.py"], "audit": ["check_repo.py"]}


def _run(args: list[str]) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(TOOLS / args[0]), *args[1:]], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


def check(project: Path, draft: Path | None, final: bool) -> int:
    rcs = project / ".rcs"
    steps = [("artifacts (G1)", ["validate_artifacts.py", str(rcs), "--project-root", str(project)])]
    if (rcs / "plan" / "visual_registry.json").exists():
        steps.append(("figures (V1-V6)", ["validate_visuals.py", str(rcs), "--project-root", str(project)]
                      + (["--draft", str(draft)] if draft else [])))
    if draft:
        steps.append(("draft lint", ["lint_draft.py", str(draft), "--rcs", str(rcs)] + (["--final"] if final else [])))
        steps.append(("number tracing", ["verify_numbers.py", str(draft), "--rcs", str(rcs), "--project-root", str(project),
                                         "--strict"]))
    worst = 0
    for name, args in steps:
        code, out = _run(args)
        worst = max(worst, code)
        lines = [l for l in out.splitlines() if l.strip()]
        findings = [l for l in lines if l.lstrip().startswith(("ERROR", "[ERROR]"))]
        print(f"== {name}: {'FAIL' if code else 'ok'} ({lines[-1].strip() if lines else ''})")
        for l in findings[:25]:
            print("   " + l.strip()[:170])
    print("RESULT:", "FAIL (see ERROR lines; each names the rule to satisfy)" if worst else "no errors")
    return 1 if worst else 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "check":
        if not rest:
            print("usage: python tools/rce.py check PROJECT [--draft D] [--final]")
            return 2
        draft = Path(rest[rest.index("--draft") + 1]) if "--draft" in rest else None
        return check(Path(rest[0]), draft, "--final" in rest)
    if cmd not in PASS:
        print(f"unknown command {cmd!r}\n{__doc__}")
        return 2
    return subprocess.call([sys.executable, str(TOOLS / PASS[cmd][0]), *PASS[cmd][1:], *rest])


if __name__ == "__main__":
    sys.exit(main())
