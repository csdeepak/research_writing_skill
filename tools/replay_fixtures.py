#!/usr/bin/env python3
"""Replay the fixture library through the deterministic checkers (tier 1 of the self-improvement loop).

Each fixture (tools/tests/fixtures/replay/*.json) is a minimal, content-light project materialised in a
temp directory, plus expectations about what the checkers must (and must not) report:

  {"id": "ADV-01", "origin": "spec 10 case 1 | real: <where it was observed>", "title": "...",
   "files": {"README.md": "text", ".rcs/evidence/research_evidence.json": {...}, ...},
   "checks": [{"tool": "validate" | "lint" | "verify_numbers" | "invariance",
               "draft": "paper.md", "before": "a.md", "after": "b.md", "strict": false, "final": false,
               "expect": ["ERROR:UNRECONCILED_CONFLICT"], "forbid": ["ERROR:*"]}]}

Findings are normalised to LEVEL:CODE (lint/number/invariance rule ids, and UPPER_SNAKE codes in validator
messages). "LEVEL:*" matches any code at that level.

This is the cheap offline gate. It can show that a CHECKER change catches known failures without new
false alarms. It cannot show that a WRITER-instruction change improves reader understanding (past drafts
were written under the old rules) -- that needs the live harness.

Usage: python tools/replay_fixtures.py [--dir DIR] [--only ID] [--log run_log.json] [-v]
Exit code 1 if any expectation fails.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claim_invariance  # noqa: E402
import lint_draft  # noqa: E402
import truth_guardrail  # noqa: E402
import validate_artifacts  # noqa: E402
import verify_numbers  # noqa: E402

DEFAULT_DIR = Path(__file__).resolve().parent / "tests" / "fixtures" / "replay"
CODE_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")


def materialise(files: dict, root: Path) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as fh:     # byte-exact on every OS (no CRLF translation)
            fh.write(content if isinstance(content, str) else json.dumps(content, indent=1))


def run_validate(root: Path) -> list[str]:
    rcs = root / ".rcs"
    rep = validate_artifacts.Report()
    loaded = validate_artifacts.check_schemas(rcs, rep)
    validate_artifacts.check_references(rcs, root, loaded, rep)
    truth_guardrail.run(rcs, root, loaded, rep)
    import workflow_guard
    workflow_guard.run(rcs, root, loaded, rep)
    validate_artifacts.check_spine(rcs, rep)
    eff = validate_artifacts.check_gates(rcs, root, rep)
    out = [f"{i['level']}:{c}" for i in rep.items for c in (CODE_RE.findall(i["message"]) or ["UNCODED"])]
    out += [f"GATE:{g}={s}" for g, s in eff.items()]
    return out


def run_check(chk: dict, root: Path) -> list[str]:
    tool = chk["tool"]
    if tool == "validate":
        return run_validate(root)
    if tool == "lint":
        md = (root / chk.get("draft", "paper.md")).read_text(encoding="utf-8")
        claims = lint_draft.load_claims(root / ".rcs")
        L = lint_draft.lint_text(md, claims, chk.get("final", False), chk.get("require_tags", False), set(), None)
        return [f"{f['level']}:{f['rule']}" for f in L.findings]
    if tool == "verify_numbers":
        md = (root / chk.get("draft", "paper.md")).read_text(encoding="utf-8")
        return [f"{f['level']}:{f['rule']}" for f in verify_numbers.verify(md, root / ".rcs", root, chk.get("strict", False))]
    if tool == "visuals":
        import contextlib
        import io
        import validate_visuals
        import visuals
        with contextlib.redirect_stdout(io.StringIO()):
            visuals.cmd_render(root / ".rcs", root, None)
        for t in chk.get("tamper", []):            # simulate edits after rendering
            p = root / t["file"]
            p.write_text(p.read_text(encoding="utf-8").replace(t["old"], t["new"]), encoding="utf-8")
        rep = validate_visuals.Rep()
        draft = (root / chk["draft"]).read_text(encoding="utf-8") if chk.get("draft") else None
        status = validate_visuals.check(root / ".rcs", root, draft, rep)
        return [f"{i['level']}:{i['code']}" for i in rep.items] + [f"GATE:{g}={s}" for g, s in status.items()]
    if tool == "invariance":
        f = claim_invariance.compare((root / chk["before"]).read_text(encoding="utf-8"),
                                     (root / chk["after"]).read_text(encoding="utf-8"))
        return [f"{x['level']}:{x['rule']}" for x in f]
    raise ValueError(f"unknown tool {tool}")


def _hit(token: str, found: list[str]) -> bool:
    level, _, code = token.partition(":")
    if code == "*":
        return any(f.startswith(level + ":") for f in found)
    return token in found


def run_fixture(fx: dict) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="rce_replay_"))
    try:
        materialise(fx.get("files", {}), tmp)
        results = []
        for chk in fx["checks"]:
            try:
                found = run_check(chk, tmp)
                err = None
            except Exception as exc:  # noqa: BLE001
                found, err = [], f"{type(exc).__name__}: {exc}"
            missing = [t for t in chk.get("expect", []) if not _hit(t, found)]
            unwanted = [t for t in chk.get("forbid", []) if _hit(t, found)]
            results.append({"tool": chk["tool"], "ok": not missing and not unwanted and err is None,
                            "missing": missing, "unwanted": unwanted, "error": err, "found": sorted(set(found))})
        return {"id": fx["id"], "origin": fx.get("origin"), "title": fx.get("title"),
                "ok": all(r["ok"] for r in results), "checks": results}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def load_fixtures(d: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--only")
    ap.add_argument("--log", help="write a machine log of every fixture, check and finding")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    fixtures = [f for f in load_fixtures(Path(a.dir)) if not a.only or f["id"] == a.only]
    res = [run_fixture(f) for f in fixtures]
    for r in res:
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['id']:<14} {r['title']}")
        for c in r["checks"]:
            if not c["ok"] or a.verbose:
                print(f"        {c['tool']:<15} missing={c['missing']} unwanted={c['unwanted']} error={c['error']}")
                if a.verbose or not c["ok"]:
                    print(f"        found: {c['found']}")
    n_fail = sum(not r["ok"] for r in res)
    print(f"\n{len(res) - n_fail}/{len(res)} fixtures pass")
    if a.log:
        Path(a.log).write_text(json.dumps({"tool": "replay_fixtures", "run_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"), "fixtures": len(res), "failed": n_fail, "results": res}, indent=2), encoding="utf-8")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
