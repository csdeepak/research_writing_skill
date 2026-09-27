#!/usr/bin/env python3
"""Phase 9: (re)create the A/B writer workspaces for skill v0.1.0 vs candidate v0.2.0 (D-17).

Each workspace = <RCE_TMP>/rce_ws/<PROJECT>__skillv0{10,20}sub with:
  project/  (frozen snapshot: paper.txt + README_*.md)
  rce/skill (v0.1.0 canonical skill  OR  evaluation/skill_versions/v0.2.0-candidate)
  rce/tools (matching tools)
  TASK.md   (= writers.SKILL_PROMPT, identical to Phase 5: workflow steps 1-17, stop before external review)

Usage: python evaluation/harness/prep_phase9.py [PROJECT ...]   (default: OPENHANDS MLPERF_TINY BEIR)
Existing workspaces are deleted and recreated (clean start).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writers as W  # noqa: E402

CAND = W.ROOT / "evaluation" / "skill_versions" / "v0.2.0-candidate"
ARMS = {"skillv010sub": (W.ROOT / "skill", W.ROOT / "tools"), "skillv020sub": (CAND, CAND / "tools")}


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
        (w / "TASK.md").write_text(W.SKILL_PROMPT, encoding="utf-8")
        print(w)


if __name__ == "__main__":
    for p in (sys.argv[1:] or ["OPENHANDS", "MLPERF_TINY", "BEIR"]):
        prep(p)
