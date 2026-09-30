#!/usr/bin/env python3
"""Stage 4 end-to-end: the REVIEW role (workflow step 18) with structural isolation.

  make     build a task prompt = the skill's review_agent.md + the two output schemas + the packet files (inlined).
           The reviewer agent reads only that prompt and writes only output.txt -- it cannot see .rcs/, the evidence,
           the claim map or the author's notes.
  collect  split output.txt into .rcs/diagnostics/<round>/{diagnostics,reconstruction}.json, validate both against
           their schemas, write reviewer_log.json (what the reviewer was given), and record the two files in the
           provenance ledger under role REVIEW (the orchestrator records for the reviewer, which may not run tools).

Usage: python evaluation/stage4_e2e/review_step.py make|collect [--round v001_1]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAND = HERE.parents[0] / "skill_versions" / "v0.3.0-candidate"
W = Path(os.environ.get("RCE_TMP", tempfile.gettempdir())) / "rce_ws" / "ASMOS_e2e"
TASK = Path(os.environ.get("RCE_TMP", tempfile.gettempdir())) / "rce_tasks" / "e2e_review"


def make(rnd: str) -> Path:
    packet = W / ".rcs" / "packets" / f"review_{rnd}"
    files = sorted(p for p in packet.rglob("*") if p.is_file() and p.name != "packet_manifest.json")  # incl. figures/
    manifest = json.loads((packet / "packet_manifest.json").read_text(encoding="utf-8"))
    parts = ["# ROLE INSTRUCTIONS (treat as your system prompt)\n", (CAND / "agents" / "review_agent.md").read_text(encoding="utf-8"),
             "\n\n# OUTPUT SCHEMAS\n## reconstruction.schema.json\n", (CAND / "schemas" / "reconstruction.schema.json").read_text(encoding="utf-8"),
             "\n## diagnostics.schema.json\n", (CAND / "schemas" / "diagnostics.schema.json").read_text(encoding="utf-8"),
             f"\n\n# YOUR PACKET (packet_id: {manifest['packet_id']}); these are the only files you may use\n"]
    for f in files:
        parts.append(f"\n## FILE {f.relative_to(packet).as_posix()}\n\n{f.read_text(encoding='utf-8')}\n")
    parts.append('\n---\nWrite ONE JSON object only (no code fences) to the file output.txt in this same folder: '
                 '{"reconstruction": <object valid against reconstruction.schema.json>, "diagnostics": <object valid against '
                 'diagnostics.schema.json>, "reviewer_notes_private": "<your free reasoning>"}. Use packet_id '
                 f'"{manifest["packet_id"]}" in both objects. Give every one of the 20 dimensions at least one finding.')
    TASK.mkdir(parents=True, exist_ok=True)
    (TASK / "prompt.md").write_text("".join(parts), encoding="utf-8")
    (TASK / "given.json").write_text(json.dumps({"packet_files": [str(f) for f in files], "packet_id": manifest["packet_id"]}),
                                     encoding="utf-8")
    return TASK / "prompt.md"


def collect(rnd: str) -> int:
    sys.path.insert(0, str(W / "rce" / "tools"))
    from rce_common import load_schema, validate
    import workflow_guard
    txt = (TASK / "output.txt").read_text(encoding="utf-8")
    m = re.search(r"\{.*\}", txt, re.S)
    out = json.loads(m.group(0))
    d = W / ".rcs" / "diagnostics" / rnd
    d.mkdir(parents=True, exist_ok=True)
    errs = []
    for key, schema in (("diagnostics", "diagnostics.schema.json"), ("reconstruction", "reconstruction.schema.json")):
        (d / f"{key}.json").write_text(json.dumps(out[key], indent=1, ensure_ascii=False), encoding="utf-8")
        errs += [f"{key}: {e}" for e in validate(out[key], load_schema(schema))]
    (d / "reviewer_notes.private.md").write_text(str(out.get("reviewer_notes_private", "")), encoding="utf-8")
    given = json.loads((TASK / "given.json").read_text(encoding="utf-8"))
    (d / "reviewer_log.json").write_text(json.dumps({
        "mode": "packet files inlined into a single task prompt; the reviewer agent had Read/Write on that folder only",
        "files_read": given["packet_files"], "task_prompt_sha256": hashlib.sha256((TASK / "prompt.md").read_bytes()).hexdigest()},
        indent=1), encoding="utf-8")
    workflow_guard.record(W / ".rcs", "REVIEW", [str(d / "diagnostics.json"), str(d / "reconstruction.json"),
                                                  str(d / "reviewer_log.json"), str(d / "reviewer_notes.private.md")])
    print(f"collected round {rnd}; schema problems: {len(errs)}")
    for e in errs[:10]:
        print("  ", e)
    return 1 if errs else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["make", "collect"])
    ap.add_argument("--round", default="v001_1")
    a = ap.parse_args()
    if a.cmd == "make":
        print(make(a.round))
    else:
        sys.exit(collect(a.round))
