#!/usr/bin/env python3
"""Validate the failure-case archive (cases/failures/FC-*.json) against skill/schemas/failure_case.schema.json.

Also checks that every regression test id (T-###) named by a case exists in tools/tests/, and every replay fixture
named by a case exists in tools/tests/fixtures/replay/. Cases are permanent: a case is never removed because a newer
version passes it (docs/concepts/SELF_IMPROVEMENT.md).

Usage: python tools/validate_cases.py [cases/failures]
Exit 1 on any problem.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import load_schema, validate  # noqa: E402

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent


def check(cases_dir: Path) -> list[str]:
    schema = load_schema("failure_case.schema.json")
    test_text = "\n".join(p.read_text(encoding="utf-8") for p in (TOOLS / "tests").glob("*.py"))
    fixtures = {p.stem for p in (TOOLS / "tests" / "fixtures" / "replay").glob("*.json")}
    problems, seen = [], set()
    files = sorted(cases_dir.glob("FC-*.json"))
    if not files:
        problems.append(f"no cases in {cases_dir}")
    for f in files:
        try:
            case = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{f.name}: invalid JSON: {exc}")
            continue
        problems += [f"{f.name}: {e}" for e in validate(case, schema)]
        if case.get("id") != f.stem:
            problems.append(f"{f.name}: id {case.get('id')} does not match the file name")
        if case.get("id") in seen:
            problems.append(f"{f.name}: duplicate id")
        seen.add(case.get("id"))
        reg = case.get("regression") or {}
        for t in reg.get("tests", []):
            if not re.search(rf"\b{re.escape(t)}\b|test_{t.replace('-', '')}", test_text):
                problems.append(f"{f.name}: regression test {t} not found in tools/tests/")
        for fx in reg.get("replay_fixtures", []):
            if fx not in fixtures:
                problems.append(f"{f.name}: replay fixture {fx} not found")
        if (case.get("resolution") or {}).get("status") == "fixed" and not (reg.get("tests") or reg.get("replay_fixtures")):
            problems.append(f"{f.name}: status 'fixed' needs a regression test or replay fixture")
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    d = Path(argv[0]) if argv else REPO / "cases" / "failures"
    problems = check(d)
    for p in problems:
        print("ERROR", p)
    print(f"{len(list(d.glob('FC-*.json')))} case(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
