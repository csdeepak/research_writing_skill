#!/usr/bin/env python3
"""Find literature candidates: corpus intake (workflow step 6) and global search (step 7). skill/literature.md sections 3-4.

Everything found here is a CANDIDATE in corpus/candidates.json. Nothing is citable until verify_citations.py registers it.

  python tools/lit_search.py .rcs --intake refs.bib --intake ~/Zotero/export.json --intake library_pdfs/
        ingest the user's library, read-only. .bib, .ris, CSL-JSON (Zotero), an Obsidian vault, a folder of PDFs.
        Every entry ends kept or reported; a file that cannot be parsed is named, and nothing is implied about it.
  python tools/lit_search.py .rcs [--topic "..."]
        with no corpus/search_plan.json yet: draft one from the story graph and evidence map, then stop. The plan's terms
        are what leave the machine, so they are reviewed first. --topic seeds it for a topic-only run.
  python tools/lit_search.py .rcs --online
        run the plan: every facet query on at least 2 indexes, within paper_config.budget.
  python tools/lit_search.py .rcs --online --snowball
        one level backward and forward from the first 5 kept candidates or registered sources (through OpenAlex).
  python tools/lit_search.py .rcs --stop-reason "two batches with no new method family"

Every query goes to corpus/corpus_log.md: string, index, date, hits, and status. An index that gave no answer is logged as
skipped, never as zero hits. Screening is the agent's job: set `decision` (keep | exclude) and `reason` in candidates.json;
each run rewrites the Screening table in the log from those fields.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zlib
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import INJECTION_RE, load_json, safe_stdout  # noqa: E402
import rce_index as ix  # noqa: E402

DEFAULT_QUERIES = 40
DEFAULT_SOURCES = 200
RESULT_ROWS = 10
STOP = set("a an and are as at be been by can do does for from has have how in into is it its of on or our over than that the "
           "their these this those to under was we were what when where which while who why will with within would".split())
DOI_RE = re.compile(rb"\b(10\.\d{4,9}/[^\s\"<>()\[\]{}]+)")


# ------------------------------------------------------------------------------ intake parsers
def _bib_entries(text: str) -> list[dict]:
    out, i = [], 0
    while True:
        m = re.compile(r"@(\w+)\s*\{").search(text, i)
        if not m:
            return out
        depth, j = 1, m.end()
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth:
            raise ValueError(f"unbalanced braces in the entry at offset {m.start()}")
        i = j
        if m.group(1).lower() in ("comment", "preamble", "string"):
            continue
        body = text[m.end():j - 1]
        fields = {k.lower(): v for k, v in _bib_fields(body)}
        names = [n.strip() for n in re.split(r"\s+and\s+", fields.get("author", "")) if n.strip()]
        year = re.search(r"\d{4}", fields.get("year", fields.get("date", "")))
        out.append({"title": _detex(fields.get("title", "")), "authors": [_detex(n) for n in names], "year": int(year.group()) if year else None,
                    "venue": _detex(fields.get("journal", fields.get("booktitle", ""))) or None, "doi": fields.get("doi"),
                    "url": fields.get("url"), "arxiv_id": fields.get("eprint") if fields.get("archiveprefix", "").lower() == "arxiv" else None})


def _bib_fields(body: str):
    """key = {value} | "value" | bareword, with nested braces. Regexes alone cannot do this."""
    i = body.find(",") + 1
    while i < len(body):
        m = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*").match(body, i)
        if not m:
            i += 1
            continue
        i = m.end()
        if i < len(body) and body[i] in '{"':
            close, depth, j = ("}" if body[i] == "{" else '"'), 1, i + 1
            while j < len(body) and depth:
                if body[j] == "{" and close == "}":
                    depth += 1
                elif body[j] == close:
                    depth -= 1
                j += 1
            yield m.group(1), body[i + 1:j - 1]
            i = j
        else:
            end = body.find(",", i)
            end = len(body) if end < 0 else end
            yield m.group(1), body[i:end].strip()
            i = end + 1


def _detex(s: str) -> str:
    return " ".join(re.sub(r"[{}]", "", re.sub(r"\\[a-zA-Z]+\s*", "", s)).split())


def _ris_entries(text: str) -> list[dict]:
    out, cur = [], {}
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])\s{2}-\s?(.*)$", line)
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "ER":
            out.append(cur)
            cur = {}
        else:
            cur.setdefault(tag, []).append(val)

    def one(e, *tags):
        return next((e[t][0] for t in tags if e.get(t)), None)
    if cur:
        raise ValueError("the last RIS record has no ER line")
    return [{"title": one(e, "TI", "T1") or "", "authors": e.get("AU", []) + e.get("A1", []), "year": _year(one(e, "PY", "Y1", "DA")),
             "venue": one(e, "JO", "JF", "T2"), "doi": one(e, "DO"), "url": one(e, "UR")} for e in out]


def _year(s: str | None) -> int | None:
    m = re.search(r"\d{4}", s or "")
    return int(m.group()) if m else None


def _csl_entries(data) -> list[dict]:
    items = data.get("items", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("expected a CSL-JSON list of items")
    out = []
    for it in items:
        names = [", ".join(x for x in (a.get("family"), a.get("given")) if x) or a.get("literal", "") for a in it.get("author", [])]
        parts = (it.get("issued") or {}).get("date-parts") or [[None]]
        out.append({"title": it.get("title", ""), "authors": [n for n in names if n], "year": parts[0][0] if parts[0] else None,
                    "venue": it.get("container-title"), "doi": it.get("DOI"), "url": it.get("URL")})
    return out


def _vault_entries(folder: Path) -> tuple[list[dict], list[str]]:
    out, failed = [], []
    for p in sorted(folder.rglob("*.md")):
        if ".obsidian" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            failed.append(f"{p.name}: {type(exc).__name__}")
            continue
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not m:
            continue                     # an ordinary note, not a literature note
        fm = dict(re.findall(r"^([A-Za-z_-]+):\s*(.+?)\s*$", m.group(1), re.M))
        title = fm.get("title", "").strip("\"'")
        if not (title or fm.get("doi")):
            continue
        authors = [a.strip(" \"'[]") for a in re.split(r";|,(?=\s*[A-Z][a-z]+\s)", fm.get("authors", fm.get("author", ""))) if a.strip(" \"'[]")]
        out.append({"title": title, "authors": authors, "year": _year(fm.get("year")), "venue": fm.get("venue"),
                    "doi": fm.get("doi", "").strip("\"'") or None, "as_cited": title or p.stem})
    return out, failed


def _pdf_doi(raw: bytes) -> str | None:
    """A DOI from the raw bytes, then from the first compressed streams. No PDF library in stdlib: a miss is reported."""
    m = DOI_RE.search(raw)
    if m:
        return m.group(1).decode("ascii", "ignore").rstrip(".,;")
    for s in list(re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S))[:25]:
        try:
            m = DOI_RE.search(zlib.decompress(s.group(1)))
        except zlib.error:
            continue
        if m:
            return m.group(1).decode("ascii", "ignore").rstrip(".,;")
    return None


def _pdf_entries(folder: Path) -> tuple[list[dict], list[str]]:
    out, failed = [], []
    for p in sorted(folder.rglob("*.pdf")):
        try:
            doi = _pdf_doi(p.read_bytes())
        except OSError as exc:
            failed.append(f"{p.name}: {type(exc).__name__}")
            continue
        out.append({"title": "", "authors": [], "year": None, "doi": doi, "as_cited": p.stem, "needs_metadata": True})
    return out, failed


def read_library(path: Path) -> tuple[list[dict], list[str], str]:
    """(entries, failures, kind). Opens the user's files read-only and never writes beside them."""
    if path.is_dir():
        if list(path.glob("*.pdf")) or (list(path.rglob("*.pdf")) and not list(path.rglob("*.md"))):
            entries, failed = _pdf_entries(path)
            return entries, failed, "pdf folder"
        entries, failed = _vault_entries(path)
        return entries, failed, "obsidian vault"
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".bib":
        return _bib_entries(text), [], "bibtex"
    if suffix == ".ris":
        return _ris_entries(text), [], "ris"
    if suffix == ".json":
        return _csl_entries(json.loads(text)), [], "csl-json"
    raise ValueError(f"unsupported library format {suffix or path.name}")


def intake(rcs: Path, paths: list[str]) -> int:
    data, problems, kept, log = ix.load_candidates(rcs), 0, 0, []
    for raw in paths:
        p = Path(raw)
        try:
            entries, failed, kind = read_library(p)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"ERROR could not read {p}: {exc}. Nothing from this file was ingested; it is NOT covered.")
            log.append([ix.today(), p.name, "(whole file)", f"unreadable: {exc}"])
            problems += 1
            continue
        for f in failed:
            print(f"ERROR could not read {f}")
            log.append([ix.today(), p.name, f, "unreadable"])
            problems += 1
        for e in entries:
            label = e.get("title") or e.get("as_cited") or "(no title)"
            if not (e.get("title") or e.get("doi")):
                log.append([ix.today(), p.name, label, "kept as a stub: no title or DOI, needs metadata"])
            else:
                log.append([ix.today(), p.name, label, "candidate"])
            e.setdefault("as_cited", e.get("title") or None)
            e["doi"] = ix.normalize_doi(e.get("doi"))
            is_new = ix.add_candidate(data, e, f"corpus:{p.name}")
            kept += is_new
            if not is_new:
                log[-1][3] = "duplicate of an existing candidate"
        print(f"{p.name} ({kind}): {len(entries)} entries read")
    ix.save_candidates(rcs, data)
    ix.append_log(rcs, "Corpus intake", log)
    print(f"intake: {kept} new candidate(s), {problems} unreadable item(s)")
    return 1 if problems else 0


# ------------------------------------------------------------------------------ search plan
LABEL_RE = re.compile(r"^(RQ|H|C|E|L|N)\d+$")
# Coined names (SynthLoad) and acronyms (RWN, RWN-fixed) are often the project's own vocabulary. A search sends them to
# the indexes, so the drafted plan names them for the reviewer (found in the end-to-end run on the demo project).
PROJECT_TERM_RE = re.compile(r"^([A-Z][a-z]+[A-Z][A-Za-z]*|[A-Z]{2,}[A-Za-z0-9]*(-[A-Za-z0-9]+)*)$")


def keywords(text: str, n: int = 6) -> str:
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9-]+", text) if w.lower() not in STOP and not LABEL_RE.match(w)]
    return " ".join(words[:n])


def project_terms(plan: dict) -> list[str]:
    return sorted({w for terms in plan.get("facets", {}).values() for t in terms for w in t.split() if PROJECT_TERM_RE.match(w)})


def draft_plan(rcs: Path, topic: str | None) -> dict:
    """Facets from the structured artifacts: evidence kinds supply datasets and metrics, story nodes the rest."""
    facets: dict[str, list[str]] = {"problem": [], "method": [], "dataset": [], "metric": []}
    if topic:
        facets["problem"].append(topic)
    sg = rcs / "story" / "story_graph.json"
    for n in (load_json(sg).get("nodes", []) if sg.exists() else []):
        slot = {"PROBLEM": "problem", "RQ": "problem", "APPROACH": "method", "DESIGN": "method"}.get(n.get("type"))
        if slot and keywords(n.get("text", "")):
            facets[slot].append(keywords(n.get("text", "")))
    ev = rcs / "evidence" / "research_evidence.json"
    for e in (load_json(ev).get("items", []) if ev.exists() else []):
        slot = {"dataset": "dataset", "metric": "metric", "baseline": "method"}.get(e.get("kind"))
        if slot and keywords(e.get("summary", ""), 4):
            facets[slot].append(keywords(e.get("summary", ""), 4))
    return {"facets": {k: list(dict.fromkeys(v)) for k, v in facets.items()}, "synonyms": {},
            "from_year": None, "indexes": ["openalex", "crossref", "semantic_scholar", "arxiv"]}


def build_queries(plan: dict) -> list[str]:
    """problem × method, then problem × dataset, method × dataset and method × metric, then synonym variants."""
    f = plan.get("facets", {})
    pairs = [("problem", "method"), ("problem", "dataset"), ("method", "dataset"), ("method", "metric")]
    out = [f"{a} {b}" for x, y in pairs for a, b in product(f.get(x, []), f.get(y, []))]
    if not out:
        out = [t for k in ("problem", "method") for t in f.get(k, [])]
    for term, syns in (plan.get("synonyms") or {}).items():
        out += [q.replace(term, s) for q in list(out) if term in q for s in syns]
    return list(dict.fromkeys(q.strip() for q in out if q.strip()))


def _budget(rcs: Path, a) -> tuple[int, int]:
    cfg_p = rcs / "plan" / "paper_config.json"
    b = (load_json(cfg_p).get("budget") or {}) if cfg_p.exists() else {}
    return a.max_queries or b.get("max_web_queries") or DEFAULT_QUERIES, a.max_sources or b.get("max_sources") or DEFAULT_SOURCES


def _screen_check(rcs: Path, rec: dict) -> None:
    for field in ("title", "abstract"):
        if INJECTION_RE.search(rec.get(field) or ""):
            ix.note_suspicious(rcs, f"index record {rec.get('doi') or rec.get('title', '')[:60]} ({field})", rec[field])


def run_search(rcs: Path, client: ix.Client, plan: dict, max_calls: int, max_sources: int) -> dict:
    data, calls, stop = ix.load_candidates(rcs), 0, "all planned queries ran"
    indexes = plan.get("indexes") or list(ix.SEARCH_INDEXES)
    queries, per_query = build_queries(plan), []
    if len(indexes) < 2:
        print("WARN  the plan names fewer than 2 indexes; literature.md section 4 needs at least 2 per facet")
    for q in queries:
        if calls + len(indexes) > max_calls:
            stop = f"query budget reached ({max_calls} calls)"
            break
        if len(data["candidates"]) >= max_sources:
            stop = f"source budget reached ({max_sources})"
            break
        new, answered = 0, 0
        for index in indexes:
            calls += 1
            oc = client.search(index, q, RESULT_ROWS, plan.get("from_year"))
            answered += oc.status != "skipped"
            for rec in oc.records:
                _screen_check(rcs, rec)
                new += ix.add_candidate(data, rec, f"search:{index}")
        per_query.append({"query": q, "new": new, "indexes_answered": answered})
        print(f"  {new:3d} new, {answered}/{len(indexes)} indexes answered: {q[:80]}")
    ix.save_candidates(rcs, data)
    ix.log_calls(rcs, client)
    return {"queries": len(per_query), "stop": stop, "under_two": [p["query"] for p in per_query if p["indexes_answered"] < 2],
            "candidates": len(data["candidates"]), "works": ix.distinct_works(data)}


def snowball(rcs: Path, client: ix.Client) -> int:
    data = ix.load_candidates(rcs)
    reg_p = rcs / "corpus" / "source_registry.json"
    seeds = [c.get("doi") for c in data["candidates"] if c.get("decision") == "keep" and c.get("doi")]
    if reg_p.exists():
        seeds += [s.get("doi") for s in load_json(reg_p).get("sources", []) if s.get("doi")]
    seeds = list(dict.fromkeys(seeds))[:5]
    if not seeds:
        print("ERROR no seeds: keep at least one candidate with a DOI before snowballing")
        return 1
    new = 0
    for doi in seeds:
        for direction in ("backward", "forward"):
            oc = client.snowball(ix.normalize_doi(doi), direction)
            if oc.status == "skipped":
                print(f"WARN  {direction} from {doi}: skipped ({oc.reason})")
            for rec in oc.records:
                _screen_check(rcs, rec)
                new += ix.add_candidate(data, rec, f"snowball:{direction}")
    ix.save_candidates(rcs, data)
    ix.log_calls(rcs, client)
    print(f"snowball: {new} new candidate(s) from {len(seeds)} seed(s)")
    return 0


def write_screening(rcs: Path) -> None:
    rows = [[c["id"], (c.get("title") or c.get("as_cited") or "") + (f" (version of {c['possible_version_of']}?)" if c.get("possible_version_of") else ""),
             c.get("decision"), c.get("reason") or ""] for c in ix.load_candidates(rcs)["candidates"]]
    ix.replace_section(rcs, "Screening", ix._table(["Candidate", "Title", "Decision", "Reason"], rows))


def main(argv: list[str] | None = None) -> int:
    safe_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--online", action="store_true", help="allow network calls (policy-checked and logged)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached responses")
    ap.add_argument("--intake", action="append", default=[], metavar="PATH", help="a .bib, .ris, CSL-JSON file, Obsidian vault or PDF folder")
    ap.add_argument("--topic", help="seed the plan's problem facet (topic-only runs)")
    ap.add_argument("--snowball", action="store_true")
    ap.add_argument("--stop-reason")
    ap.add_argument("--max-queries", type=int)
    ap.add_argument("--max-sources", type=int)
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    (rcs / "corpus").mkdir(parents=True, exist_ok=True)
    code = 0
    if a.intake:
        code = intake(rcs, a.intake)
    plan_p = rcs / "corpus" / "search_plan.json"
    client = ix.Client(rcs, online=a.online, refresh=a.refresh)
    if a.snowball:
        code = max(code, snowball(rcs, client))
    elif a.stop_reason:
        ix.replace_section(rcs, "Stopping reason", [f"{ix.today()}: {a.stop_reason}"])
    elif not plan_p.exists():
        if not a.intake or a.topic:
            plan = draft_plan(rcs, a.topic)
            suspects = project_terms(plan)
            if suspects:
                plan["_review"] = {"possible_project_terms": suspects,
                                   "note": "coined names and acronyms may be the project's own vocabulary: replace them with the field's terms"}
            plan_p.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"wrote a draft search plan to {plan_p}. Review its terms: they leave the machine. Then run with --online.")
            if suspects:
                print(f"WARN  possible project-internal terms in the plan: {', '.join(suspects)}. Replace them with the field's terms.")
    elif not a.intake or a.online:
        if not a.online:
            print("offline: answering from .rcs/cache/ only. A query with no cached response is skipped, not empty.")
        max_calls, max_sources = _budget(rcs, a)
        res = run_search(rcs, client, load_json(plan_p), max_calls, max_sources)
        ix.replace_section(rcs, "Stopping reason", [f"{ix.today()}: {res['stop']}"])
        print(f"search: {res['queries']} queries, {res['candidates']} candidates in total, {res['works']} distinct work(s) once "
              f"likely versions of one work are counted once (possible_version_of). Count works in a scoped gap. Stopped: {res['stop']}")
        if res["under_two"]:
            print(f"WARN  {len(res['under_two'])} query(ies) reached fewer than 2 indexes. See the Status column in the log.")
        if res["candidates"] == 0:
            print("ERROR nothing found. If every index was skipped, nothing was searched: INSUFFICIENT_LITERATURE.")
            code = 1
    write_screening(rcs)
    return code


if __name__ == "__main__":
    sys.exit(main())
