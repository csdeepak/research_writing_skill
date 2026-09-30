#!/usr/bin/env python3
"""Local, opt-in run diagnostics for recursive self-improvement (RECOMMENDED_NEXT_VERSION.md Part D).

Every skill run already leaves a trail in .rcs/ (state.json, gate reports, audits). This tool turns
that trail into one CONTENT-FREE record per run -- rule IDs and counts only, never project text,
claims, numbers, titles or paths -- appended to a private log on this machine:

    $RCE_HOME/diagnostics.jsonl        (default RCE_HOME = ~/.rce)

Nothing is sent anywhere. Recording requires explicit opt-in (--opt-in, or RCE_DIAGNOSTICS=1).

  record  <.rcs> [--domain ml|biology|hci|...] [--opt-in]   append one record for this run
  summary [--min-runs 3] [--json]                           recurring failure patterns across runs
  export  [--min-runs 3] --out FILE                         aggregate counts only, for voluntary sharing

`summary` lists rules that fired in >= min-runs runs: candidates for a new minimal fixture in the
replay library (tools/replay_fixtures.py). A pattern is evidence about the skill's performance --
it is NOT permission to change the skill. Any rule change still goes through a proposal, the
replay gate, a live test where needed, and a human promotion decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import SKILL_DIR  # noqa: E402

CODE_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")      # FAILURE_STATE-style codes in messages
RULE_ID_RE = re.compile(r"^[A-Za-z0-9][\w\-]*$")


def home() -> Path:
    return Path(os.environ.get("RCE_HOME", Path.home() / ".rce"))


def skill_version() -> str:
    """Released version, or '<version>+candidate-<x>' while a candidate is being tested."""
    p = SKILL_DIR / "SKILL.md"
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    v = re.search(r"(?m)^version:\s*([\w.\-]+)", text)
    c = re.search(r"(?m)^candidate:\s*([\w.\-]+)", text)
    return (v.group(1) if v else "unknown") + (f"+candidate-{c.group(1)}" if c else "")


def _codes_from(report: dict) -> Counter:
    c: Counter = Counter()
    for f in report.get("findings", []) or []:
        rule = str(f.get("rule", ""))
        if RULE_ID_RE.match(rule):
            c[f"{f.get('level', '?')}:{rule}"] += 1
    for it in report.get("items", []) or []:
        for code in set(CODE_RE.findall(str(it.get("message", "")))):
            c[f"{it.get('level', '?')}:{code}"] += 1
    return c


def build_record(rcs: Path, domain: str | None) -> dict:
    """Aggregate counts from .rcs. Only identifiers and integers leave this function."""
    rules: Counter = Counter()
    for rep in sorted((rcs / "audits").rglob("*.json")) if (rcs / "audits").is_dir() else []:
        try:
            rules += _codes_from(json.loads(rep.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            rules["ERROR:UNREADABLE_REPORT"] += 1
    state = {}
    if (rcs / "state.json").exists():
        try:
            state = json.loads((rcs / "state.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rules["ERROR:MALFORMED_STATE"] += 1
    gates = {}
    try:
        import validate_artifacts as VA  # noqa: E402
        rep = VA.Report()
        gates = VA.check_gates(rcs, rcs.parent, rep)
    except Exception:  # noqa: BLE001
        gates = {}
    failures = Counter()
    for f in state.get("open_failures", []) or []:
        code = f.get("code") if isinstance(f, dict) else f
        if isinstance(code, str) and CODE_RE.fullmatch(code):
            failures[code] += 1
    return {
        "schema": "rce-diagnostics/1",
        "recorded": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skill_version": skill_version(),
        "project": hashlib.sha256(str(rcs.resolve()).encode()).hexdigest()[:12],   # one-way id, not the path
        "domain": domain if domain and re.fullmatch(r"[\w\-]{1,32}", domain) else None,
        "step": state.get("step") if isinstance(state.get("step"), int) else None,
        "effective_gates": {g: s for g, s in gates.items() if re.fullmatch(r"G\d|V\d", g)},
        "rules": dict(rules),
        "open_failures": dict(failures),
        "accepted_risks": len(state.get("accepted_risks", []) or []),
        "human_overrides": len(state.get("human_overrides", []) or []),
    }


def load_log() -> list[dict]:
    p = home() / "diagnostics.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def summarize(records: list[dict], min_runs: int) -> dict:
    runs_with: Counter = Counter()
    total: Counter = Counter()
    gate_status: Counter = Counter()
    for r in records:
        for k, v in (r.get("rules") or {}).items():
            runs_with[k] += 1
            total[k] += v
        for g, s in (r.get("effective_gates") or {}).items():
            gate_status[f"{g}={s}"] += 1
    recurring = [{"rule": k, "runs": n, "occurrences": total[k]} for k, n in runs_with.most_common() if n >= min_runs]
    return {"runs": len(records), "domains": dict(Counter(r.get("domain") or "unspecified" for r in records)),
            "skill_versions": dict(Counter(r.get("skill_version") for r in records)),
            "recurring_patterns": recurring, "gate_status": dict(gate_status),
            "note": "Recurring patterns are candidates for new replay fixtures, not instructions to change the skill."}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("rcs")
    r.add_argument("--domain")
    r.add_argument("--opt-in", action="store_true")
    r.add_argument("--dry-run", action="store_true", help="print the record, do not write it")
    s = sub.add_parser("summary")
    s.add_argument("--min-runs", type=int, default=3)
    s.add_argument("--json", action="store_true")
    e = sub.add_parser("export")
    e.add_argument("--min-runs", type=int, default=3)
    e.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "record":
        rec = build_record(Path(a.rcs), a.domain)
        if a.dry_run:
            print(json.dumps(rec, indent=2))
            return 0
        if not (a.opt_in or os.environ.get("RCE_DIAGNOSTICS") == "1"):
            print("diagnostics are opt-in: pass --opt-in or set RCE_DIAGNOSTICS=1 (use --dry-run to see what would be "
                  "recorded; nothing is ever sent off this machine)", file=sys.stderr)
            return 2
        home().mkdir(parents=True, exist_ok=True)
        with open(home() / "diagnostics.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"recorded run {rec['project']} -> {home() / 'diagnostics.jsonl'}")
        return 0
    summ = summarize(load_log(), a.min_runs)
    if a.cmd == "export":
        Path(a.out).write_text(json.dumps(summ, indent=2), encoding="utf-8")
        print(f"wrote aggregate counts for {summ['runs']} runs to {a.out} (review before sharing)")
        return 0
    if getattr(a, "json", False):
        print(json.dumps(summ, indent=2))
    else:
        print(f"{summ['runs']} runs; domains {summ['domains']}")
        for p in summ["recurring_patterns"]:
            print(f"  {p['rule']:40} in {p['runs']} runs ({p['occurrences']} occurrences)")
        print(summ["note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
