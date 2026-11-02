#!/usr/bin/env python3
"""Verify sources by lookup and run gate GL (workflow step 8; skill/literature.md sections 5 and 7).

  python tools/verify_citations.py .rcs --online [--refresh] [--only SRC-001,SRC-002]
      Look up every registered source and every candidate with decision "keep". Record lookup_verified, one row per
      index, retraction status and flags. A kept candidate that passes is registered; its metadata comes from the index
      record, never from memory. Exit 1 if a source is fabricated or retracted without acknowledgement.
  python tools/verify_citations.py .rcs --gate [--draft drafts/vNNN/paper.md] --out .rcs/audits/gates/GL_citations.json
      Gate GL: deterministic, no network.

Verdicts (verification.lookup_verified):
  true          the ID resolves and the title matches, or a title search finds the work
  false         the DOI resolver or arXiv reports the ID does not exist (ID_NOT_FOUND), or the ID resolves to a different
                work (DOI_MISMATCH). This is fabrication evidence: FABRICATED_CITATION
  unresolvable  no index could confirm the work (NOT_INDEXED, NO_TITLE_TO_COMPARE). A coverage gap, not proof of
                fabrication; it may stay, listed in open_issues.md
  (no verdict)  the lookups gave no answer (LOOKUP_DEGRADED). Run it again. GL treats it as unverified.

GL fails on: a registered source with lookup_verified false; a cited source with no verification record, no verdict or no
support quote; a gap or novelty claim not scoped to the logged search; a retracted source without retracted_acknowledged;
an unresolvable source missing from open_issues.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_draft import author_year_citations  # noqa: E402
from rce_common import INJECTION_RE, load_json, split_sentences  # noqa: E402
import rce_index as ix  # noqa: E402

DEFAULT_CUTOFF = 2024
PRIORITY = ("crossref", "openalex", "semantic_scholar", "arxiv")
RETRACTING = {"retraction", "withdrawal", "removal", "partial_retraction"}
REINSTATING = {"reinstatement"}
TOOL_FLAGS = {"preprint", "single_index", "post_llm_unconfirmed", "metadata_conflict", "expression_of_concern"}
AMBIGUOUS_MARGIN = 0.10
MAX_QUOTE_WORDS = 40
SRC_RE = re.compile(r"\bSRC-\d{3,}\b")
GAP_LINE_RE = re.compile(r"^\s*GAP\b.*", re.M)
NOVELTY_RE = re.compile(r"\b(no (prior|previous|existing) (work|study|studies|research|method|approach)\w*|for the first time|"
                        r"(the|our) first (to|study|work|method)|we are the first|has not (yet )?been (studied|addressed|examined|explored)|"
                        r"have not (yet )?been (studied|addressed|examined|explored)|remains? unexplored|to (the best of )?our knowledge)\b", re.I)
SCOPE_RE = re.compile(r"\b(among the \d+|\d+ (works|papers|studies|sources) retrieved|retrieved from|our search|we searched|logged search)\b", re.I)


# ------------------------------------------------------------------------------ one source
def _row(name: str, oc: ix.Outcome, score: float | None = None) -> dict:
    row = {"index": name, "status": oc.status, "match_score": None if score is None else round(score, 3)}
    if oc.reason:
        row["reason"] = oc.reason
    return row


def _work_key(rec: dict) -> str:
    return ix.arxiv_id_of(rec) or rec.get("doi") or ix.normalize_title(rec.get("title", ""))


def pick(cited: str, year: int | None, recs: list[dict]) -> tuple[list[dict], bool]:
    """Records that pass the title threshold, best first, and whether they leave a real choice. The threshold is coarse:
    'Part I' and 'Part II' both pass, so near-ties between different works go to a person."""
    scored = sorted(((ix.title_similarity(cited, r.get("title", "")), r) for r in recs), key=lambda x: -x[0])
    passing = [(s, r) for s, r in scored if s >= ix.TITLE_THRESHOLD]
    if year:
        passing = [(s, r) for s, r in passing if r.get("year") == year] or passing
    if not passing:
        return [], False
    best_score, best = passing[0]
    near = {_work_key(r) for s, r in passing if best_score - s <= AMBIGUOUS_MARGIN}
    return [r for s, r in passing if _work_key(r) == _work_key(best)], len(near) > 1


def _conflicts(src: dict, matched: list[dict]) -> list[dict]:
    """Disagreements between index records. Never resolved here: they are recorded for a person."""
    out = []
    years = {r["index"]: r.get("year") for r in matched if r.get("year")}
    if len(set(years.values())) > 1:
        out.append({"field": "year", "values": years, "minor": max(years.values()) - min(years.values()) <= 1})
    firsts = {r["index"]: ix.surname(r["authors"][0]) for r in matched if r.get("authors")}
    if len(set(firsts.values())) > 1:
        out.append({"field": "first_author", "values": firsts, "minor": False})
    titles = [r for r in matched if r.get("title")]
    if any(ix.title_similarity(a["title"], b["title"]) < 0.9 for a in titles for b in titles):
        out.append({"field": "title", "values": {r["index"]: r["title"] for r in titles}, "minor": False})
    if src.get("authors") and firsts and ix.surname(src["authors"][0]) not in firsts.values():
        out.append({"field": "first_author_cited", "values": {"cited": src["authors"][0], **firsts}, "minor": False})
    return out


def _event_date(u: dict) -> tuple:
    parts = ((u.get("updated") or {}).get("date-parts") or [[]])[0]
    return tuple(parts)


def retraction_of(doi: str | None, cr: dict | None, oa: dict | None, stamps: list[str]) -> dict:
    """What named resolvers returned on a date. Matched on DOI only: a title match never marks a paper retracted."""
    obs = []
    undated_conflict = False
    if cr is not None:
        events = [u for u in cr.get("updated_by", []) if str(u.get("type", "")).lower() in RETRACTING | REINSTATING]
        dated = sorted((e for e in events if _event_date(e)), key=_event_date)
        kinds = {str(e.get("type")).lower() in RETRACTING for e in events}
        undated_conflict = len(kinds) > 1 and len(dated) < len(events)
        last = dated[-1] if dated else (events[0] if len(kinds) == 1 else None)
        retracted = str(last.get("type")).lower() in RETRACTING if last else False
        obs.append({"source": "crossref", "retracted": retracted})
        if not events and ix.RETRACTED_PREFIX_RE.match(cr.get("title", "")):
            obs.append({"source": "crossref_title", "retracted": True})
    if oa is not None and isinstance(oa.get("is_retracted"), bool):
        obs.append({"source": "openalex", "retracted": oa["is_retracted"]})
    if not doi or not obs:
        status = "unknown"
    elif undated_conflict or len({o["retracted"] for o in obs}) > 1:
        status = "disputed"
    else:
        status = "retracted" if obs[0]["retracted"] else "not_retracted"
    dates = [s for s in stamps if s]
    return {"status": status, "checked_at": min(dates) if dates else ix.today(), "source": "+".join(o["source"] for o in obs) or "none",
            "observations": obs}


def verify_source(src: dict, client: ix.Client, cutoff: int = DEFAULT_CUTOFF) -> dict:
    doi, arx = ix.normalize_doi(src.get("doi")), ix.arxiv_id_of(src)
    cited = src.get("as_cited") or src.get("title") or ""
    year = src.get("year") if isinstance(src.get("year"), int) else None
    rows, recs, stamps = [], [], []
    registrar: list[str] = []

    def take(name: str, oc: ix.Outcome, is_registrar: bool = False) -> None:
        score = max((ix.title_similarity(cited, r.get("title", "")) for r in oc.records if r.get("title")), default=None) if cited else None
        rows.append(_row(name, oc, score))
        recs.extend(r for r in oc.records if r.get("title"))
        stamps.append(oc.checked_at)
        if is_registrar:
            registrar.append(oc.status)

    # arXiv works carry a DataCite DOI, so an arXiv id alone can still be triangulated. Crossref cannot hold such a DOI.
    lookup_doi = doi or (f"10.48550/arxiv.{arx}" if arx else None)
    if doi:
        take("doi.org", client.doi_exists(doi), True)
    if lookup_doi:
        if not ix.ARXIV_DOI_RE.match(lookup_doi):
            take("crossref", client.crossref_doi(lookup_doi))
        take("openalex", client.openalex_doi(lookup_doi))
        take("semantic_scholar", client.s2_doi(lookup_doi))
    if arx:
        take("arxiv", client.arxiv_id(arx), True)

    verdict, code, ambiguous, suggestion, matched = None, "LOOKUP_DEGRADED", False, None, []
    if doi or arx:
        if recs:                    # every record here came from the ID, so they are one work: no choice to leave open
            matched = [r for r in recs if ix.title_similarity(cited, r["title"]) >= ix.TITLE_THRESHOLD] if cited else recs
            if matched:
                verdict, code = True, None if cited else "NO_CITED_TITLE"
            else:
                verdict, code = False, "DOI_MISMATCH"
                suggestion = _suggest(cited, year, client)
        elif "found" in registrar:
            # The ID exists. Only indexes that answered can make this a coverage gap; if they were all down, it is no verdict.
            answered = any(r["status"] == "not_found" for r in rows if r["index"] not in ("doi.org", "arxiv"))
            verdict, code = ("unresolvable", "NO_TITLE_TO_COMPARE") if answered else (None, "LOOKUP_DEGRADED")
        elif registrar and all(s == "not_found" for s in registrar):
            verdict, code = False, "ID_NOT_FOUND"
            suggestion = _suggest(cited, year, client) if cited else None
    elif not cited:
        code = "NO_IDENTIFIER"
    else:
        answered = hit = False
        for name in ("crossref", "openalex", "semantic_scholar", "arxiv"):
            if name == "arxiv" and hit:                     # arXiv is slow to call: a last resort for title searches
                break
            oc = client.search(name, cited, 5)
            passing, _ = pick(cited, year, oc.records)
            status = oc.status if oc.status == "skipped" else "found" if passing else "not_found"
            rows.append(_row(name, oc._replace(status=status), max((ix.title_similarity(cited, r["title"]) for r in oc.records), default=None)))
            recs.extend(oc.records)
            stamps.append(oc.checked_at)
            answered, hit = answered or oc.status != "skipped", hit or bool(passing)
        matched, ambiguous = pick(cited, year, recs)
        if matched:
            verdict, code = True, None
            lookup_doi = next((r["doi"] for r in matched if r.get("doi")), None)
        elif answered:
            verdict, code = "unresolvable", "NOT_INDEXED"

    matched = sorted(matched, key=lambda r: PRIORITY.index(r["index"]) if r.get("index") in PRIORITY else 9)
    conflicts = _conflicts(src, matched)
    cr = next((r for r in matched if r["index"] == "crossref"), None)
    oa = next((r for r in matched if r["index"] == "openalex"), None)
    if lookup_doi and verdict is True and not (doi or arx):     # a title match found the DOI: check retraction on that DOI
        cr = cr or next(iter(client.crossref_doi(lookup_doi).records), None)
        oa = oa or next(iter(client.openalex_doi(lookup_doi).records), None)
    eoc = any(str(u.get("type", "")).lower() == "expression_of_concern" for u in (cr or {}).get("updated_by", []))
    retraction = retraction_of(lookup_doi, cr, oa, stamps)

    found_in = {r["index"] for r in matched}
    preprint = bool(matched) and all(ix.is_preprint(r) for r in matched)
    flags = set()
    if preprint or src.get("publication_status") == "PREPRINT":
        flags.add("preprint")
    if len(found_in) == 1:
        flags.add("single_index")
    the_year = next((r.get("year") for r in matched if r.get("year")), year)
    if "preprint" in flags and (the_year or 0) >= cutoff and len(found_in) <= 1:
        flags.add("post_llm_unconfirmed")
    if ambiguous or any(not c["minor"] for c in conflicts):
        flags.add("metadata_conflict")
    if eoc:
        flags.add("expression_of_concern")

    return {"lookup_verified": verdict, "code": code, "indexes": rows, "retraction": retraction, "flags": sorted(flags),
            "conflicts": conflicts, "matched": matched, "records": recs, "suggestion": suggestion,
            "doi": doi or (lookup_doi if not arx else None), "arxiv_id": arx}


def _suggest(cited: str, year: int | None, client: ix.Client) -> dict | None:
    """A wrong ID on a real paper is possible. A correction may come only from an index record, and only a person applies it."""
    for name in ("crossref", "openalex"):
        passing, _ = pick(cited, year, client.search(name, cited, 5).records)
        if passing:
            r = passing[0]
            return {"index": r["index"], "doi": r.get("doi"), "title": r.get("title"), "year": r.get("year")}
    return None


def _publication_status(rec: dict | None) -> str:
    if not rec or ix.is_preprint(rec):
        return "PREPRINT" if rec else "TECHNICAL_REPORT"
    return "PEER-REVIEWED" if rec.get("type") in ix.PEER_TYPES else "TECHNICAL_REPORT"


def apply_result(src: dict, res: dict) -> None:
    """Write the result into a source. Metadata moves only on a clean match: a conflict stays for a person to settle."""
    v = src.setdefault("verification", {"method": "manual", "date": ix.today()})
    verdict = res["lookup_verified"]
    if verdict is None:
        v.pop("lookup_verified", None)
    else:
        v["lookup_verified"] = verdict
    v["code"], v["indexes"], v["conflicts"] = res["code"], res["indexes"], res["conflicts"]
    if res.get("suggestion"):
        v["suggestion"] = res["suggestion"]
    src["retraction"] = {k: res["retraction"][k] for k in ("status", "checked_at", "source", "observations")}
    v["retraction_checked"] = res["retraction"]["status"] != "unknown"
    human = [f for f in src.get("flags", []) if f not in TOOL_FLAGS]
    src["flags"] = sorted(set(human) | set(res["flags"]))
    if verdict is True:
        v["method"], v["date"], v["verified_by"] = ("doi_lookup" if src.get("doi") else "index_lookup"), ix.today(), "agent"
        best = res["matched"][0] if res["matched"] else {}
        if res["doi"] and not src.get("doi"):
            src["doi"] = res["doi"]
        if res["arxiv_id"] and not src.get("arxiv_id"):
            src["arxiv_id"] = res["arxiv_id"]
        if not any(not c["minor"] for c in res["conflicts"]) and "metadata_conflict" not in res["flags"] and best:
            if best.get("title") and best["title"] != src.get("title"):
                src.setdefault("as_cited", src.get("title"))
                src["title"] = best["title"]
            for field in ("authors", "year", "venue"):
                if best.get(field):
                    src[field] = best[field]
            src["title_status"] = "verified"
    elif src.get("title_status") is None and src.get("as_cited"):
        src["title_status"] = "as_cited"


def _next_id(sources: list[dict]) -> str:
    nums = [int(s["id"].split("-")[1]) for s in sources if SRC_RE.fullmatch(s.get("id", ""))]
    return f"SRC-{max(nums, default=0) + 1:03d}"


def register(cand: dict, res: dict, sources: list[dict]) -> dict | None:
    """A kept candidate becomes a source. The tool does the lookup; the agent still reads it (read_depth stays abstract
    and establishes stays empty, so GL fails on any citation of it until a support quote exists)."""
    best = res["matched"][0] if res["matched"] else {}
    src = {"id": _next_id(sources), "title": best.get("title") or cand.get("title") or cand.get("as_cited"),
           "authors": best.get("authors") or cand.get("authors"), "year": best.get("year") or cand.get("year"),
           "venue": best.get("venue") or cand.get("venue"), "doi": res["doi"] or ix.normalize_doi(cand.get("doi")), "url": cand.get("url"),
           "publication_status": _publication_status(best or None), "peer_review_known": False, "level": 2,
           "verification": {"method": "index_lookup", "date": ix.today(), "verified_by": "agent"},
           "read_depth": "abstract", "establishes": [], "permitted_use": ["content_citation"], "as_cited": cand.get("as_cited") or cand.get("title"),
           "title_status": "as_cited"}
    if not (src["title"] and src["authors"] and src["year"]):
        return None
    if not src["doi"]:
        src.pop("doi")
    if not src["url"]:
        src.pop("url")
    apply_result(src, res)
    return src


def _registry(rcs: Path) -> dict:
    p = rcs / "corpus" / "source_registry.json"
    return load_json(p) if p.exists() else {"sources": []}


def _cutoff(rcs: Path) -> int:
    p = rcs / "plan" / "paper_config.json"
    return (load_json(p).get("contamination_cutoff_year") if p.exists() else None) or DEFAULT_CUTOFF


def run(rcs: Path, client: ix.Client, only: set[str] | None = None) -> int:
    reg, cands, cutoff = _registry(rcs), ix.load_candidates(rcs), _cutoff(rcs)
    lines, bad = [], 0

    def report(ident: str, title: str, res: dict) -> None:
        nonlocal bad
        for r in res["records"]:            # every record, not just matches: a mismatched record is the suspicious one
            for field in ("title", "abstract"):
                if INJECTION_RE.search(r.get(field) or ""):
                    ix.note_suspicious(rcs, f"{ident} ({r['index']} {field})", r[field])
        verdict = {True: "true", False: "FALSE", "unresolvable": "unresolvable", None: "no verdict"}[res["lookup_verified"]]
        st = res["retraction"]["status"]
        lines.append(f"{ident:10} {verdict:13} {res['code'] or '':20} {st:14} {','.join(res['flags'])}  {(title or '')[:50]}")
        if res["lookup_verified"] is False:
            bad += 1
            s = res.get("suggestion")
            lines.append(f"           FABRICATED_CITATION: remove it from the registry and the draft."
                         + (f" An index holds a similar title: {s['title'][:60]!r}, doi {s['doi']}. A person decides." if s else ""))
        if st == "retracted":
            bad += 1
            lines.append("           RETRACTED_SOURCE: remove it, or keep it only where the sentence discusses the retraction.")

    for s in reg["sources"]:
        if only and s["id"] not in only:
            continue
        res = verify_source(s, client, cutoff)
        apply_result(s, res)
        report(s["id"], s.get("title"), res)
    for c in cands["candidates"]:
        if c.get("decision") != "keep" or c.get("registered_as") or (only and c["id"] not in only):
            continue
        res = verify_source(c, client, cutoff)
        report(c["id"], c.get("title") or c.get("as_cited"), res)
        c["verification_code"], c["lookup_verified"] = res["code"], res["lookup_verified"]
        if res["lookup_verified"] in (True, "unresolvable"):
            src = register(c, res, reg["sources"])
            if src:
                reg["sources"].append(src)
                c["registered_as"] = src["id"]
            else:
                c["needs_metadata"] = True
                lines.append("           not registered: no title, author and year from any record")
    (rcs / "corpus").mkdir(parents=True, exist_ok=True)
    (rcs / "corpus" / "source_registry.json").write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
    ix.save_candidates(rcs, cands)
    ix.log_calls(rcs, client)
    print("\n".join(lines) or "nothing to verify: no registered sources and no candidates with decision 'keep'")
    degraded = sum(1 for s in reg["sources"] if (s.get("verification") or {}).get("code") == "LOOKUP_DEGRADED")
    if degraded:
        print(f"WARN  {degraded} source(s) got no verdict: the lookups gave no answer. That is not a pass. Run it again.")
    return 1 if bad else 0


# ------------------------------------------------------------------------------ gate GL
def _sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def _open_issues(rcs: Path) -> str:
    for p in (rcs / "open_issues.md", rcs.parent / "open_issues.md"):
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def _cited(rcs: Path, sources: list[dict], draft: Path | None) -> tuple[dict[str, str], list[str]]:
    """{source id: where it is cited}, and draft citations that resolve to nothing."""
    where: dict[str, str] = {}
    chain = rcs / "story" / "lit_gap_chain.md"
    if chain.exists():
        for sid in SRC_RE.findall(chain.read_text(encoding="utf-8")):
            where.setdefault(sid, "story/lit_gap_chain.md")
    cm = rcs / "claims" / "claim_evidence_map.json"
    if cm.exists():
        for c in load_json(cm).get("claims", []):
            for sid in c.get("sources", []) or []:
                where.setdefault(sid, f"claim {c.get('id')}")
    unresolved = []
    if draft and draft.exists():
        index: dict[tuple, list[str]] = {}
        for s in sources:
            if s.get("authors") and s.get("year"):
                index.setdefault((ix.surname(s["authors"][0]), int(s["year"])), []).append(s["id"])
        for line in draft.read_text(encoding="utf-8").splitlines():
            for name, year, text in author_year_citations(line):
                ids = index.get((name, year))
                if not ids:
                    unresolved.append(text)
                for sid in ids or []:
                    where.setdefault(sid, f"draft: {text}")
    return where, unresolved


def _norm_name(s: str) -> str:
    return re.sub(r"[\s_-]+", "", s).lower()


def check_scope(rcs: Path, draft: Path | None, add) -> None:
    log_p = rcs / "corpus" / "corpus_log.md"
    log = log_p.read_text(encoding="utf-8") if log_p.exists() else ""
    rows = [[c.strip() for c in l.strip("|").split("|")] for l in log.splitlines() if l.startswith("|") and "---" not in l]
    ok_rows = [r for r in rows if len(r) >= 6 and r[-1] == "ok"]
    logged = {_norm_name(r[1]) for r in ok_rows}
    chain = rcs / "story" / "lit_gap_chain.md"
    gaps = GAP_LINE_RE.findall(chain.read_text(encoding="utf-8")) if chain.exists() else []
    if gaps and not ok_rows:
        add("ERROR", "GAP_NOT_SCOPED", "story/lit_gap_chain.md", "the chain states a gap, but corpus_log.md records no successful query")
    for line in gaps:
        names_index = any(name and name in _norm_name(line) for name in logged)
        if not (re.search(r"\b\d+\b", line) and re.search(r"\b(19|20)\d{2}\b", line) and names_index):
            add("ERROR", "GAP_NOT_SCOPED", "story/lit_gap_chain.md",
                f"a gap must name the count, the date and a logged index: {line.strip()[:110]}")
    if draft and draft.exists():
        for s in split_sentences(draft.read_text(encoding="utf-8")):
            if NOVELTY_RE.search(s) and not SCOPE_RE.search(s):
                add("ERROR", "GAP_NOT_SCOPED", "draft", f"novelty claim not scoped to the logged search: {s[:110]}")


def gate(rcs: Path, draft: Path | None) -> dict:
    items: list[dict] = []

    def add(level: str, code: str, where: str, message: str) -> None:
        items.append({"level": level, "code": code, "where": where, "message": message})

    reg_p = rcs / "corpus" / "source_registry.json"
    sources = _registry(rcs)["sources"]
    if not reg_p.exists():
        add("ERROR", "NO_REGISTRY", "corpus/source_registry.json", "no source registry: step 8 has not run")
    by_id = {s.get("id"): s for s in sources}
    cited, unresolved = _cited(rcs, sources, draft)
    issues = _open_issues(rcs)
    for sid, where in sorted(cited.items()):
        if sid not in by_id:
            add("ERROR", "CITATION_UNREGISTERED", where, f"{sid} is cited but not registered")
    for text in unresolved:
        add("ERROR", "CITATION_UNREGISTERED", "draft", f"({text}) resolves to no registered source")
    for s in sources:
        sid, v = s.get("id"), s.get("verification") or {}
        verdict, is_cited = v.get("lookup_verified"), sid in cited
        listed = sid in issues or (s.get("title") or "\0") in issues
        if verdict is False:
            add("ERROR", "FABRICATED_CITATION", sid, f"{v.get('code') or 'lookup failed'}: remove it from the registry")
        elif verdict is None:
            if is_cited:
                add("ERROR", "UNVERIFIED_CITATION", sid, f"cited in {cited[sid]} with no lookup verdict ({v.get('code') or 'not run'})")
            else:
                add("WARN", "NO_VERDICT", sid, "registered with no lookup verdict and not cited")
        elif verdict == "unresolvable" and not listed:
            add("ERROR", "UNRESOLVABLE_NOT_LISTED", sid, "unresolvable sources are allowed only when listed in open_issues.md")
        st = (s.get("retraction") or {}).get("status")
        if st == "retracted" and "retracted_acknowledged" not in (s.get("flags") or []):
            add("ERROR", "RETRACTED_SOURCE", sid, "retracted, with no retracted_acknowledged flag")
        elif st in ("disputed", "unknown") and is_cited and not listed:
            add("WARN", "RETRACTION_UNCLEAR", sid, f"retraction status {st}: list it in open_issues.md")
        if is_cited:
            quoted = [e for e in s.get("establishes") or [] if str(e.get("support_quote", "")).strip() and str(e.get("location", "")).strip()]
            if not quoted:
                add("ERROR", "NO_SUPPORT_QUOTE", sid, f"cited in {cited[sid]} with no support quote and location")
            for e in quoted:
                if len(e["support_quote"].split()) > MAX_QUOTE_WORDS:
                    add("ERROR", "QUOTE_TOO_LONG", sid, f"support quotes are at most {MAX_QUOTE_WORDS} words")
    check_scope(rcs, draft, add)
    verdicts: dict[str, int] = {}
    for s in sources:
        key = str((s.get("verification") or {}).get("lookup_verified", "no_verdict")).lower()
        verdicts[key] = verdicts.get(key, 0) + 1
    log_p = rcs / "corpus" / "corpus_log.md"
    return {"tool": "verify_citations", "gate": "GL", "errors": sum(i["level"] == "ERROR" for i in items),
            "warnings": sum(i["level"] == "WARN" for i in items), "items": items, "sources": len(sources), "verdicts": verdicts,
            "cited": sorted(cited), "registry_sha256": _sha(reg_p), "log_sha256": _sha(log_p),
            "draft": str(draft).replace("\\", "/") if draft else None, "draft_sha256": _sha(draft) if draft else None}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--online", action="store_true", help="allow network calls (policy-checked and logged)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached responses")
    ap.add_argument("--only", help="comma-separated source or candidate ids")
    ap.add_argument("--gate", action="store_true", help="run gate GL instead of the lookups (no network)")
    ap.add_argument("--draft", help="also check this draft's citations and novelty claims")
    ap.add_argument("--out", help="write the GL report here")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    if not a.gate:
        return run(rcs, ix.Client(rcs, online=a.online, refresh=a.refresh), set(a.only.split(",")) if a.only else None)
    rep = gate(rcs, Path(a.draft) if a.draft else None)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    for i in rep["items"]:
        print(f"{i['level']:5} {i['code']:24} {i['where']}: {i['message']}")
    print(f"\nGL: {'PASSED' if rep['errors'] == 0 else 'FAILED'} ({rep['errors']} error(s), {rep['warnings']} warning(s); "
          f"{rep['sources']} source(s): {rep['verdicts']})")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
