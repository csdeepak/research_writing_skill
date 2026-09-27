#!/usr/bin/env python3
"""Fetch and pin the official source snapshot of each external project.

For each project: the arXiv PDF at a pinned version -> text via pdftotext (layout-free),
and the README of each official repository at the current default-branch commit (SHA pinned).
Writes evaluation/external_projects/<P>/snapshot/ and evaluation/manifests/source_snapshots.json.
Public, official sources only (arxiv.org, raw.githubusercontent.com, api.github.com).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "evaluation" / "external_projects"

PROJECTS = {
    "SWE_BENCH": {"arxiv": "2310.06770v3", "repos": ["SWE-bench/SWE-bench"]},
    "BEIR": {"arxiv": "2104.08663v4", "repos": ["beir-cellar/beir"]},
    "MLPERF_TINY": {"arxiv": "2106.07597v4", "repos": ["mlcommons/tiny"]},
    "SAM": {"arxiv": "2304.02643v1", "repos": ["facebookresearch/segment-anything"]},
    "WHISPER": {"arxiv": "2212.04356v1", "repos": ["openai/whisper"]},
    "OPENHANDS": {"arxiv": "2407.16741v3", "repos": ["OpenHands/OpenHands", "OpenHands/benchmarks"]},
}
UA = {"User-Agent": "rce-external-validation/0.1 (research evaluation; contact via repo)"}


def get(url: str) -> bytes:
    # curl rather than urllib: the local Python lacks a CA bundle
    return subprocess.run(["curl", "-sSfL", "-m", "180", "-A", UA["User-Agent"], url],
                          capture_output=True, check=True).stdout


def gh(path: str) -> dict:
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    manifest = {"created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "projects": {}}
    only = set(sys.argv[1:])
    for name, spec in PROJECTS.items():
        if only and name not in only:
            continue
        snap = EP / name / "snapshot"
        snap.mkdir(parents=True, exist_ok=True)
        entry = {"arxiv": spec["arxiv"], "files": {}, "repos": {}}
        pdf = get(f"https://arxiv.org/pdf/{spec['arxiv']}")
        (snap / "paper.pdf").write_bytes(pdf)
        subprocess.run(["pdftotext", "-enc", "UTF-8", str(snap / "paper.pdf"), str(snap / "paper.txt")], check=True)
        entry["files"]["paper.pdf"] = {"url": f"https://arxiv.org/pdf/{spec['arxiv']}", "sha256": sha(pdf)}
        txt = (snap / "paper.txt").read_bytes()
        entry["files"]["paper.txt"] = {"derived_from": "paper.pdf via pdftotext", "sha256": sha(txt),
                                       "words": len(txt.decode("utf-8", "replace").split())}
        for repo in spec["repos"]:
            info = gh(f"repos/{repo}")
            commit = gh(f"repos/{repo}/commits/{info['default_branch']}")["sha"]
            readme_meta = gh(f"repos/{repo}/readme?ref={commit}")
            raw = get(f"https://raw.githubusercontent.com/{repo}/{commit}/{readme_meta['path']}")
            fname = f"README__{repo.replace('/', '__')}.md"
            (snap / fname).write_bytes(raw)
            entry["repos"][repo] = {"commit": commit, "readme_path": readme_meta["path"]}
            entry["files"][fname] = {"url": f"https://github.com/{repo}/blob/{commit}/{readme_meta['path']}", "sha256": sha(raw)}
        (snap / "paper.pdf").unlink()  # keep text only in repo; PDF re-downloadable from pinned URL
        manifest["projects"][name] = entry
        print(name, entry["files"]["paper.txt"]["words"], "words;", ", ".join(f"{r}@{v['commit'][:8]}" for r, v in entry["repos"].items()))
    out = ROOT / "evaluation" / "manifests" / "source_snapshots.json"
    old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"projects": {}}
    old["projects"].update(manifest["projects"])
    old["created"] = old.get("created", manifest["created"])
    old["updated"] = manifest["created"]
    out.write_text(json.dumps(old, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
