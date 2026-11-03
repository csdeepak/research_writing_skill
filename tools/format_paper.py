#!/usr/bin/env python3
"""Format the final paper (workflow step 21; skill/finalize.md sections 1-2). Formatting changes appearance, never content.

  python tools/format_paper.py paper/paper.md --rcs .rcs --to latex,docx,pdf [--csl style.csl] [--online]
  python tools/format_paper.py paper/paper.md --rcs .rcs --bib-only

  1. references.bib is generated from corpus/source_registry.json, beside the paper. Every field comes from the registry,
     and only cited works are written.
  2. Author-year citations, the form lint_draft.py checks, are mapped to registry keys so Pandoc can restyle them
     ("(Smith et al., 2021)" becomes "[@SRC-012]"). A citation that does not map to exactly one key stops the run.
  3. Pandoc with --citeproc and a CSL style writes each output. PDF goes through LaTeX (tectonic or pdflatex), never HTML.
  4. Each output is checked: the paper's numbers and every cited work must appear in it.

The style comes from --csl, plan/venue_profile.yaml or plan/paper_config.json. CSL files are looked up in
.rcs/cache/csl/, or fetched with --online from the CSL styles repository (host raw.githubusercontent.com must be in
data_policy.allowed_hosts).

A missing tool stops that output and only that output (FORMAT_TOOL_MISSING), and nothing is substituted. Markdown needs no
tool. The report goes to .rcs/audits/format/format_report.json. Exit 1 if anything failed or was not produced.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_draft import CITE_GROUP_RE, CITE_ONE_RE, resolve_citation  # noqa: E402
from rce_common import CLAIM_TAG_RE, load_json, safe_stdout, yaml_block  # noqa: E402
import rce_index as ix  # noqa: E402

RUN = subprocess.run                # tests replace these two: no test needs Pandoc installed
WHICH = shutil.which
TARGETS = {"latex": "tex", "docx": "docx", "pdf": "pdf"}
PDF_ENGINES = ("tectonic", "pdflatex")
STYLE_IDS = {"ieee": "ieee", "apa": "apa", "acm": "association-for-computing-machinery", "nature": "nature",
             "chicago": "chicago-author-date", "vancouver": "vancouver", "harvard": "harvard-cite-them-right",
             "mla": "modern-language-association"}
GENERIC_STYLES = {"numeric": "ieee", "author-year": "apa"}     # what a generic profile says; recorded as assumed
CSL_URL = "https://raw.githubusercontent.com/citation-style-language/styles/master/{}.csl"
PREFIX_RE = re.compile(r"^\s*(see |e\.g\.,? |cf\. )", re.I)
NARRATIVE_RE = re.compile(r"\b([A-Z][A-Za-z'\-]+)((?: et al\.?| (?:and|&) [A-Z][A-Za-z'\-]+)?) \(((?:1[6-9]|20)\d{2})([a-z]?)\)")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
BIB_SPECIALS = str.maketrans({"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "$": r"\$", "{": "", "}": ""})
PROCEEDINGS_RE = re.compile(r"\b(proceedings|proc\.|conference|workshop|symposium)\b", re.I)


# ------------------------------------------------------------------------------ references
def _esc(s) -> str:
    return str(s).translate(BIB_SPECIALS)


def bib_entry(s: dict) -> str:
    venue, status = s.get("venue"), s.get("publication_status")
    kind = "misc" if status == "PREPRINT" or not venue else "inproceedings" if PROCEEDINGS_RE.search(venue) else "article"
    fields = [("author", " and ".join(_esc(a) for a in s.get("authors", []))), ("title", _esc(s.get("title", ""))), ("year", s.get("year"))]
    if venue:
        fields.append(("journal" if kind == "article" else "booktitle" if kind == "inproceedings" else "howpublished", _esc(venue)))
    if s.get("doi"):
        fields.append(("doi", s["doi"]))
    if s.get("url"):
        fields.append(("url", s["url"]))
    if s.get("arxiv_id"):
        fields += [("eprint", s["arxiv_id"]), ("archiveprefix", "arXiv")]
    if status == "PREPRINT":
        fields.append(("note", "Preprint"))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v not in (None, ""))
    return f"@{kind}{{{s['id']},\n{body}\n}}\n"


def map_citations(md: str, sources: list[dict]) -> tuple[str, set[str], list[str]]:
    """Rewrite citations to registry keys. Returns (text, cited ids, problems)."""
    used, problems = set(), []

    def resolve(name: str, year: int, text: str) -> str | None:
        ids = resolve_citation(sources, name, year, text)
        if len(ids) != 1:
            problems.append(f"({text}) maps to {len(ids)} registered sources; it must map to exactly one")
            return None
        used.add(ids[0])
        return ids[0]

    def group(m: re.Match) -> str:
        parts, out, cited = m.group(1).split(";"), [], 0
        for part in parts:
            one = CITE_ONE_RE.match(part)
            key = resolve(one.group(1).split()[-1].lower(), int(one.group(2)), part.strip()) if one else None
            prefix = PREFIX_RE.match(part)
            out.append(f"{prefix.group(1) if prefix else ''}@{key}" if key else part.strip())
            cited += bool(key)
        if cited == 0:
            return m.group(0)
        if cited == len(parts):
            return "[" + "; ".join(out) + "]"
        return "(" + "; ".join(f"[{o}]" if "@" in o else o for o in out) + ")"

    def narrative(m: re.Match) -> str:
        ids = resolve_citation(sources, m.group(1).lower(), int(m.group(3)), f"{m.group(3)}{m.group(4)}")
        if len(ids) != 1:
            return m.group(0)       # not a citation the lint recognises: leave the words alone
        used.add(ids[0])
        return f"{m.group(1)}{m.group(2)} [-@{ids[0]}]"

    lines, in_code = [], False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        lines.append(line if in_code else NARRATIVE_RE.sub(narrative, CITE_GROUP_RE.sub(group, line)))
    return "\n".join(lines) + "\n", used, problems


# ------------------------------------------------------------------------------ style
def style_name(rcs: Path) -> str | None:
    vp = rcs / "plan" / "venue_profile.yaml"
    if vp.exists():
        style = yaml_block(vp.read_text(encoding="utf-8"), "style")
        if isinstance(style, dict) and style.get("citation_style"):
            return str(style["citation_style"]).strip()
    cfg = rcs / "plan" / "paper_config.json"
    return load_json(cfg).get("citation_style") if cfg.exists() else None


def find_csl(rcs: Path, name: str, online: bool) -> tuple[Path | None, str]:
    """(path, note). Never falls back to Pandoc's default style: that would be a silent substitution."""
    key = name.strip().lower()
    note = ""
    if key in GENERIC_STYLES:
        note = f"the profile says only {name!r}; assumed {GENERIC_STYLES[key]}"
        key = GENERIC_STYLES[key]
    style_id = STYLE_IDS.get(key, key)
    p = rcs / "cache" / "csl" / f"{style_id}.csl"
    if p.exists():
        return p, note
    code, body, reason, _ = ix.Client(rcs, online=online).get("csl-fetch", CSL_URL.format(style_id))
    if code != 200:
        return None, f"style {style_id}: {reason or f'not found ({code})'}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p, note


# ------------------------------------------------------------------------------ outputs
def _plain(path: Path) -> str | None:
    """Text of an output, for the content check. None when the format cannot be read here."""
    if path.suffix == ".tex":
        return path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".docx":
        with zipfile.ZipFile(path) as z:
            return re.sub(r"<[^>]+>", " ", z.read("word/document.xml").decode("utf-8", "replace"))
    if path.suffix == ".pdf" and WHICH("pdftotext"):
        p = RUN(["pdftotext", str(path), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        return p.stdout if p.returncode == 0 else None
    return None


def check_output(path: Path, paper_md: str, used: list[dict]) -> list[str]:
    """Formatting must not move content: every number in the paper and every cited work must appear in the output."""
    text = _plain(path)
    if text is None:
        return []
    found = set(NUM_RE.findall(text))
    body = CITE_GROUP_RE.sub(" ", paper_md)
    missing = sorted({n for n in NUM_RE.findall(body) if n not in found})
    problems = [f"numbers missing from the output: {', '.join(missing[:8])}"] if missing else []
    lowered = text.lower()
    gone = [s["id"] for s in used if ix.surname(s["authors"][0]) not in lowered]
    if gone:
        problems.append(f"cited works missing from the rendered references: {', '.join(gone[:8])}")
    return problems


def format_paper(paper: Path, rcs: Path, targets: list[str], csl: str | None, online: bool, bib_only: bool = False,
                 template: str | None = None) -> dict:
    items: list[dict] = []
    outputs: dict[str, dict] = {"markdown": {"status": "written", "path": str(paper).replace("\\", "/")}}

    def add(level: str, code: str, msg: str) -> None:
        items.append({"level": level, "code": code, "message": msg})

    def done() -> dict:
        rep = {"tool": "format_paper", "errors": sum(i["level"] == "ERROR" for i in items), "items": items, "outputs": outputs}
        d = rcs / "audits" / "format"
        d.mkdir(parents=True, exist_ok=True)
        (d / "format_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        return rep

    md = paper.read_text(encoding="utf-8")
    if CLAIM_TAG_RE.search(md):
        add("ERROR", "TAGS_PRESENT", "the paper still has claim tags: format the stripped manuscript (step 19)")
        return done()
    reg = rcs / "corpus" / "source_registry.json"
    sources = load_json(reg).get("sources", []) if reg.exists() else []
    mapped, used_ids, problems = map_citations(md, sources)
    for p in problems:
        add("ERROR", "CITATION_NOT_MAPPED", p)
    if problems:
        return done()
    used = [s for s in sources if s["id"] in used_ids]
    for s in used:
        if s.get("title_status") in ("as_cited", "unverifiable") or (s.get("verification") or {}).get("lookup_verified") == "unresolvable":
            add("WARN", "REFERENCE_UNVERIFIED", f"{s['id']} keeps the project's own text: list it in open_issues.md")
    bib = paper.parent / "references.bib"
    bib.write_text("\n".join(bib_entry(s) for s in used), encoding="utf-8")
    outputs["references"] = {"status": "written", "path": str(bib).replace("\\", "/"), "entries": len(used)}
    if bib_only:
        return done()
    pandoc = WHICH("pandoc")
    if not pandoc:
        for t in targets:
            outputs[t] = {"status": "not_produced", "reason": "pandoc is not installed"}
        add("ERROR", "FORMAT_TOOL_MISSING", f"pandoc is not installed: not produced: {', '.join(targets)}")
        return done()
    style_path, note = (Path(csl), "") if csl else (None, "")
    if not csl:
        name = style_name(rcs)
        if not name:
            add("ERROR", "FORMAT_TOOL_MISSING", "no citation style in the venue profile or paper config, and no --csl")
            return done()
        style_path, note = find_csl(rcs, name, online)
        if style_path is None:
            add("ERROR", "FORMAT_TOOL_MISSING", f"no CSL file: {note}. Supply --csl, or use --online")
            return done()
    if note:
        add("WARN", "STYLE_ASSUMED", note)
    work = rcs / "audits" / "format"
    work.mkdir(parents=True, exist_ok=True)
    source = work / "paper_cited.md"
    source.write_text(mapped, encoding="utf-8")
    for t in targets:
        out = paper.with_suffix("." + TARGETS[t])
        cmd = [pandoc, str(source), "--citeproc", "--bibliography", str(bib), "--csl", str(style_path), "--standalone",
               "--resource-path", str(paper.parent), "-o", str(out)]
        if template and t in ("latex", "pdf"):
            cmd.append(f"--template={template}")
        if t == "pdf":
            engine = next((e for e in PDF_ENGINES if WHICH(e)), None)
            if not engine:
                outputs[t] = {"status": "not_produced", "reason": "no LaTeX engine (tectonic or pdflatex)"}
                add("ERROR", "FORMAT_TOOL_MISSING", "no LaTeX engine (tectonic or pdflatex): PDF not produced. PDF never goes through HTML")
                continue
            cmd.append(f"--pdf-engine={engine}")
        p = RUN(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode != 0 or not out.exists():
            outputs[t] = {"status": "failed", "reason": (p.stderr or "")[-300:]}
            add("ERROR", "FORMAT_FAILED", f"{t}: {(p.stderr or 'pandoc failed')[-200:]}")
            continue
        changed = check_output(out, md, used)
        outputs[t] = {"status": "written", "path": str(out).replace("\\", "/"), "content_checked": _plain(out) is not None}
        if not outputs[t]["content_checked"]:
            add("WARN", "OUTPUT_NOT_CHECKED", f"{t}: no way to read this output here. Inspect it by hand")
        for problem in changed:
            add("ERROR", "FORMAT_CONTENT_CHANGED", f"{t}: {problem}")
    return done()


def main(argv: list[str] | None = None) -> int:
    safe_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper")
    ap.add_argument("--rcs", required=True)
    ap.add_argument("--to", default="latex,docx,pdf")
    ap.add_argument("--csl", help="a CSL style file")
    ap.add_argument("--template", help="a Pandoc LaTeX template, for a venue's own class (LaTeX and PDF only)")
    ap.add_argument("--online", action="store_true", help="fetch a missing CSL style (policy-checked)")
    ap.add_argument("--bib-only", action="store_true", help="write references.bib and stop")
    a = ap.parse_args(argv)
    targets = [t.strip() for t in a.to.split(",") if t.strip()]
    unknown = [t for t in targets if t not in TARGETS]
    if unknown:
        print(f"ERROR unknown output {', '.join(unknown)}; choose from {', '.join(TARGETS)}")
        return 2
    rep = format_paper(Path(a.paper), Path(a.rcs), targets, a.csl, a.online, a.bib_only, a.template)
    for i in rep["items"]:
        print(f"{i['level']:5} {i['code']:24} {i['message']}")
    for name, o in rep["outputs"].items():
        print(f"{name:10} {o['status']:13} {o.get('path') or o.get('reason', '')}")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
