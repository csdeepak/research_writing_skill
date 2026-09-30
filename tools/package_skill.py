#!/usr/bin/env python3
"""Build and validate the distributable skill ZIP: dist/research-communication-engine-v<version>.zip

Layout (Agent Skills format; one top-level folder named exactly like the skill's `name`):

  research-communication-engine/
    SKILL.md, rules (*.md), agents/, schemas/, templates/, adapters/, examples/demo_project/, tests/perturbations/
    tools/          the deterministic checks and runners (stdlib Python; tests are not shipped)

Validation (the build fails if any check fails):
  one top-level folder == frontmatter name; SKILL.md present; name = lowercase letters/digits/hyphens, <= 64
  characters, no reserved words; description non-empty, <= 200 characters (the claude.ai upload limit; the platform
  limit is 1024), no XML tags; every file path SKILL.md references exists in the package; no secrets; no absolute local
  paths; no private markers (optional local denylist .rce-audit-denylist); every .py compiles; size <= 30 MB.

Usage: python tools/package_skill.py [--out dist] [--check ZIP]
"""
from __future__ import annotations

import argparse
import io
import py_compile
import re
import sys
import tempfile
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
SKILL = REPO / "skill"
MAX_BYTES = 30 * 1024 * 1024
MAX_DESC = 200
SKIP_DIRS = {"__pycache__", "versions", ".rcs-private"}
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9]{20,}|sk-or-v1-[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|"
                       r"AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
                       r"-----BEGIN [A-Z ]*PRIVATE KEY)")
ABS_PATH_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|/home/[a-z][a-z0-9_-]+/|/Users/[A-Za-z][A-Za-z0-9._-]+/)")
REF_RE = re.compile(r"`((?:tools|agents|schemas|templates|adapters|examples|tests)/[A-Za-z0-9_./-]+?\.(?:py|md|json|yaml|csv))`")


def frontmatter(md: str) -> dict[str, str]:
    md = md.replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def denylist() -> list[str]:
    f = REPO / ".rce-audit-denylist"
    return [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] if f.exists() else []


def build(out_dir: Path) -> Path:
    fm = frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    name, version = fm.get("name", "skill"), fm.get("version", "0.0.0")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{name}-v{version}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SKILL.rglob("*")):
            rel = p.relative_to(SKILL)
            if p.is_file() and not (set(rel.parts) & SKIP_DIRS):
                z.write(p, f"{name}/{rel.as_posix()}")
        for p in sorted(TOOLS.glob("*.py")):
            z.write(p, f"{name}/tools/{p.name}")
    return target


def check(zip_path: Path) -> list[str]:
    problems: list[str] = []
    if not zip_path.exists():
        return [f"{zip_path} does not exist"]
    if zip_path.stat().st_size > MAX_BYTES:
        problems.append(f"package is {zip_path.stat().st_size} bytes (> {MAX_BYTES})")
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        roots = {n.split("/", 1)[0] for n in names}
        if len(roots) != 1:
            return problems + [f"expected one top-level folder, found {sorted(roots)}"]
        root = roots.pop()
        if f"{root}/SKILL.md" not in names:
            return problems + ["SKILL.md is not at the top of the skill folder"]
        md = z.read(f"{root}/SKILL.md").decode("utf-8")
        fm = frontmatter(md)
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != root:
            problems.append(f"top-level folder {root!r} must equal the skill name {name!r}")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", name) or re.search(r"anthropic|claude", name):
            problems.append(f"name {name!r}: lowercase letters, digits, hyphens, <= 64 chars, no reserved words")
        if not desc or len(desc) > MAX_DESC or re.search(r"<[^>]+>", desc):
            problems.append(f"description must be non-empty, <= {MAX_DESC} characters, no XML tags (has {len(desc)})")
        for ref in sorted(set(REF_RE.findall(md))):
            if f"{root}/{ref}" not in names:
                problems.append(f"SKILL.md references {ref}, which is not in the package")
        private = denylist()
        with tempfile.TemporaryDirectory() as tmp:
            for n in names:
                data = z.read(n)
                if n.endswith((".png", ".jpg", ".pdf")):
                    continue
                text = data.decode("utf-8", errors="replace")
                if SECRET_RE.search(text):
                    problems.append(f"{n}: looks like a secret")
                if ABS_PATH_RE.search(text):
                    problems.append(f"{n}: absolute local path {ABS_PATH_RE.search(text).group(0)!r}")
                for marker in private:
                    if marker.lower() in text.lower():
                        problems.append(f"{n}: private marker {marker!r}")
                if n.endswith(".py"):
                    src = Path(tmp) / Path(n).name
                    src.write_bytes(data)
                    try:
                        py_compile.compile(str(src), doraise=True)
                    except py_compile.PyCompileError as exc:
                        problems.append(f"{n}: does not compile: {exc.msg[:120]}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO / "dist"))
    ap.add_argument("--check", help="only validate an existing ZIP")
    a = ap.parse_args(argv)
    z = Path(a.check) if a.check else build(Path(a.out))
    problems = check(z)
    with zipfile.ZipFile(z) as zf:
        n = len([x for x in zf.namelist() if not x.endswith("/")])
    for p in problems:
        print("ERROR", p)
    print(f"{z} ({z.stat().st_size} bytes, {n} files): {'INVALID' if problems else 'valid'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
