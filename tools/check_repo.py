#!/usr/bin/env python3
"""Repository audit for public release (run in CI and before every release).

  secrets            API keys, tokens and private keys in any tracked text file                         ERROR
  absolute paths     local user paths in the public surface (skill/, tools/, docs/, examples/, cases/,
                     root files); evaluation/ logs are historical records and are only reported         ERROR / INFO
  private markers    strings listed in the optional, untracked .rce-audit-denylist (one per line)        ERROR
  markdown links     relative links in the public-surface Markdown resolve to existing files             ERROR
  svg                every SVG under docs/ and skill/ parses as XML and has a <title> (accessibility)   ERROR
  json               every JSON schema under skill/schemas parses                                       ERROR

Files are everything git would commit (tracked + untracked, minus .gitignore) when the root is a git repository
(so ignored private data is never scanned as "public"), otherwise every file under the root.

Usage: python tools/check_repo.py [ROOT]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_skill import ABS_PATH_RE, SECRET_RE  # noqa: E402

PUBLIC = ("skill/", "tools/", "docs/", "examples/", "cases/", ".github/")
BINARY = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".pyc", ".ico")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def tracked(root: Path) -> list[str]:
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True,
                             check=True).stdout.strip()
        if Path(top).resolve() != root.resolve():      # root is not itself a repository (e.g. a folder inside $HOME)
            raise subprocess.CalledProcessError(1, "git")
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root,
                             capture_output=True, text=True, check=True).stdout      # what would be committed
        return [f for f in out.splitlines() if f and (root / f).exists()]
    except (OSError, subprocess.CalledProcessError):
        return [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]


def public(f: str) -> bool:
    return f.startswith(PUBLIC) or "/" not in f


def audit(root: Path) -> tuple[list[str], list[str]]:
    errors, info = [], []
    deny_f = root / ".rce-audit-denylist"
    deny = [l.strip() for l in deny_f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] \
        if deny_f.exists() else []
    files = tracked(root)
    for f in files:
        if f.endswith(BINARY) or f == ".rce-audit-denylist":
            continue
        text = (root / f).read_text(encoding="utf-8", errors="replace")
        if SECRET_RE.search(text):
            errors.append(f"{f}: looks like a secret")
        m = ABS_PATH_RE.search(text)
        if m:
            (errors if public(f) else info).append(f"{f}: absolute local path {m.group(0)!r}")
        for marker in deny:
            if marker.lower() in text.lower():
                errors.append(f"{f}: private marker {marker!r}")
        if f.endswith(".md") and public(f):
            for link in LINK_RE.findall(text):
                if re.match(r"^[a-z]+:|^#|^mailto:", link):
                    continue
                target = (root / f).parent / link.split("#", 1)[0]
                if link.split("#", 1)[0] and not target.exists():
                    errors.append(f"{f}: broken link {link}")
        if f.endswith(".svg") and f.startswith(("docs/", "skill/")):
            try:
                el = ET.fromstring(text)
                if not any(c.tag.endswith("title") for c in el.iter()):
                    errors.append(f"{f}: SVG has no <title>")
            except ET.ParseError as exc:
                errors.append(f"{f}: SVG does not parse: {exc}")
        if f.startswith("skill/schemas/") and f.endswith(".json"):
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{f}: invalid JSON: {exc}")
    return errors, info


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = Path(argv[0]) if argv else Path(__file__).resolve().parents[1]
    errors, info = audit(root)
    for e in errors:
        print("ERROR", e)
    print(f"audit: {len(errors)} error(s); {len(info)} historical file(s) under evaluation/ contain local paths (reported only)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
