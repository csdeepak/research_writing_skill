#!/usr/bin/env python3
"""Write a version manifest (SHA-256 of every skill file) to skill/versions/<version>/MANIFEST.json.

Refuses to overwrite an existing version. Refuses if changelog.md has no heading for the
version (no silent changes). Tag the commit afterwards:  git tag skill-v<version>

Usage: python tools/snapshot_version.py <version>   e.g. 0.1.0
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import SKILL_DIR  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", argv[0]):
        print(__doc__)
        return 2
    version = argv[0]
    target = SKILL_DIR / "versions" / version
    if (target / "MANIFEST.json").exists():
        print(f"version {version} already exists; bump the version", file=sys.stderr)
        return 1
    changelog = (SKILL_DIR / "changelog.md").read_text(encoding="utf-8")
    if not re.search(rf"^##\s*\[?{re.escape(version)}\]?", changelog, re.M):
        print(f"changelog.md has no '## {version}' entry; document the change first", file=sys.stderr)
        return 1
    files = {}
    for p in sorted(SKILL_DIR.rglob("*")):
        rel = p.relative_to(SKILL_DIR)
        if p.is_file() and "versions" not in rel.parts and "__pycache__" not in rel.parts:
            files[str(rel).replace("\\", "/")] = hashlib.sha256(p.read_bytes()).hexdigest()
    target.mkdir(parents=True, exist_ok=True)
    manifest = {"version": version,
                "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "file_count": len(files), "files": files}
    (target / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {target / 'MANIFEST.json'} ({len(files)} files). Next: git tag skill-v{version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
