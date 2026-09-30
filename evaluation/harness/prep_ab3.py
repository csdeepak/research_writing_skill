#!/usr/bin/env python3
"""Tier-3 live A/B (D-29): writer workspaces for skill v0.1.0 vs candidate v0.3.0, pre-registered protocol.

Each workspace = <RCE_TMP>/rce_ws/<PROJECT>__skillv0{10,30}ab3 with:
  project/  (frozen snapshot: paper.txt + README_*.md)
  rce/skill (v0.1.0 canonical skill  OR  evaluation/skill_versions/v0.3.0-candidate)
  rce/tools (matching tools)
  TASK.md   (TASK v2, identical for both arms)

TASK v2 = Phase 9's writers.SKILL_PROMPT with ONE change (D-29): the no-human clause defers to the skill's own
unattended procedure if it defines one. Phase 9's wording ("choose the most defensible option ... accepted_risks")
overrode v0.3.0's checkpoint procedure, i.e. it would have switched off part of what is being tested.

Usage: python evaluation/harness/prep_ab3.py [PROJECT ...]   (default: OPENHANDS MLPERF_TINY BEIR)
Existing workspaces are deleted and recreated (clean start).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writers as W  # noqa: E402

CAND = W.ROOT / "evaluation" / "skill_versions" / "v0.3.0-candidate"
ARMS = {"skillv010ab3": (W.ROOT / "skill", W.ROOT / "tools"), "skillv030ab3": (CAND, CAND / "tools")}

OLD_CLAUSE = """- No human is available. Wherever the skill says ASK or STOP for user input, choose the most defensible option
  from the evidence, record the assumption in ./.rcs/state.json (accepted_risks) and continue."""
NEW_CLAUSE = """- No human is available. Wherever the skill says ASK or STOP for user input: if the skill defines its own procedure
  for runs with no human available, follow that procedure; otherwise choose the most defensible option from the
  evidence, record the assumption in ./.rcs/state.json (accepted_risks) and continue."""
assert OLD_CLAUSE in W.SKILL_PROMPT, "Phase 9 task text changed; re-check D-29 before running"
TASK_V2 = W.SKILL_PROMPT.replace(OLD_CLAUSE, NEW_CLAUSE)


def prep(project: str) -> None:
    snap = W.EV / "external_projects" / project / "snapshot"
    for cond, (src_skill, src_tools) in ARMS.items():
        w = W.ws(project, cond)
        if w.exists():
            shutil.rmtree(w)
        (w / "project").mkdir(parents=True)
        shutil.copy2(snap / "paper.txt", w / "project" / "paper.txt")
        for i, r in enumerate(sorted(snap.glob("README__*.md")), 1):
            shutil.copy2(r, w / "project" / f"README_{i}.md")
        shutil.copytree(src_skill, w / "rce" / "skill", ignore=shutil.ignore_patterns("versions", "__pycache__", "tools"))
        shutil.copytree(src_tools, w / "rce" / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        (w / "TASK.md").write_text(TASK_V2, encoding="utf-8")
        print(w)


if __name__ == "__main__":
    for p in (sys.argv[1:] or ["OPENHANDS", "MLPERF_TINY", "BEIR"]):
        prep(p)
