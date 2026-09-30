#!/usr/bin/env python3
"""Reader-model and information-density audit (vNext Stage 3: M02 reader knowledge model, M11 density/terminology).

M02 -- `.rcs/plan/reader_model.json` describes the binding reader persona (schema reader_model.schema.json):
       known_terms, prerequisite_concepts, likely_misconceptions (with trigger terms and the corrective point),
       reader_questions, new_term_budget. An expert in one field is NOT assumed to know adjacent jargon.
M11 -- density and precision checks that preserve meaning (they flag, never rewrite).

  READER-UNKNOWN-TERM        an acronym/registered term the persona doesn't know is used before it is explained  WARN
  READER-TERM-OVERLOAD       more new (unknown) terms in one paragraph than the persona's budget                WARN
  READER-PREREQ-ORDER        a concept is used before the prerequisite the reader model says it needs           WARN
  READER-MISCONCEPTION       a known misconception's trigger appears but its corrective point never does        WARN
  READER-QUESTION-UNANSWERED a question the reader will ask is never addressed (no paragraph shares its key terms) INFO
  M11-EXCESS-PRECISION       a value reported with more decimals than its own interval justifies                WARN
  M11-SYNONYM-DRIFT          a registered term's forbidden synonym is used (term ledger)                         WARN
  M11-DENSE-PARAGRAPH        a paragraph packs >= 6 numbers and > 120 words without a table                     INFO

Usage: python tools/audit_reader.py paper.md --rcs .rcs [--persona B] [--json] [--out F]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import CLAIM_TAG_RE, MARKER_RE, iter_paragraphs, split_sentences  # noqa: E402

ACR_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,}[a-z]?)\b")
DEF_RE = re.compile(r"\(([A-Z][A-Z0-9]{1,}[a-z]?)\)|\b([A-Z][A-Z0-9]{1,}[a-z]?)\s*(?:\(|,)\s*(?:i\.e\.|that is|which|short for|meaning)", re.I)
STOP = {"I", "II", "III", "IV", "OK", "US", "UK", "EU", "PDF", "URL", "DOI", "ID", "CI", "SD", "SE", "RQ", "AI", "ML", "KB", "MB", "GB", "MS"}
VAL_CI_RE = re.compile(r"(?<![\w.])(\d+\.\d+)\s*(?:\(|,)?\s*(?:95%\s*)?(?:CI|confidence interval)?[:\s]*\[?\(?\s*(\d+\.\d+)\s*(?:-|–|to|,)\s*(\d+\.\d+)", re.I)
PM_RE = re.compile(r"(?<![\w.])(\d+\.\d+)\s*(?:±|\+/-|\+-)\s*(\d+\.\d+)")
NUM_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?%?")
WORD_RE = re.compile(r"[a-z][a-z\-]{3,}")
COMMON = set("that this with from were have which their there about would these other into than then they them been more most "
             "such only also each both some when what does did done used using show shows paper results result data".split())


def _terms_in(text: str) -> set[str]:
    return {t for t in ACR_RE.findall(CLAIM_TAG_RE.sub("", MARKER_RE.sub("", text))) if t not in STOP and not re.fullmatch(r"[CLEVQT]\d+", t)}


def _known(persona: dict) -> set[str]:
    return {t.lower() for t in persona.get("known_terms", [])}


def excess_precision(sentence: str) -> list[str]:
    """Values whose decimals exceed what their interval supports (one digit past the interval's leading digit)."""
    out = []
    for m in list(VAL_CI_RE.finditer(sentence)) + list(PM_RE.finditer(sentence)):
        v = m.group(1)
        if m.re is PM_RE:
            width = 2 * float(m.group(2))
        else:
            lo, hi = float(m.group(2)), float(m.group(3))
            if not lo <= float(v) <= hi:
                continue
            width = hi - lo
        if width <= 0:
            continue
        allowed = max(0, -math.floor(math.log10(width))) + 1
        dec = len(v.split(".")[1])
        if dec > allowed:
            out.append(f"{v} has {dec} decimals but its interval is {width:.3g} wide: {allowed} decimal(s) suffice")
    return out


def audit(md: str, reader: dict, ledger: dict | None, persona_id: str | None) -> list[dict]:
    personas = reader.get("personas", [reader]) if reader else []
    persona = next((p for p in personas if not persona_id or p.get("id") == persona_id), personas[0] if personas else {})
    known = _known(persona)
    budget = int(persona.get("new_term_budget", 2))
    f: list[dict] = []

    def add(rule, level, line, excerpt, msg):
        f.append({"rule": rule, "level": level, "line": line, "excerpt": str(excerpt)[:160], "message": msg})

    body = re.split(r"(?im)^#+\s*references\b", md)[0]
    paras = list(iter_paragraphs(body))
    explained: set[str] = set()
    for m in DEF_RE.finditer(body):
        explained.add((m.group(1) or m.group(2) or "").lower())
    seen_first: dict[str, int] = {}
    concept_first: dict[str, int] = {}
    for start, section, para in paras:
        new_here = []
        for t in (_terms_in(para) if persona else ()):     # persona checks need a reader model
            tl = t.lower()
            if tl in known:
                continue
            defined_here = bool(re.search(rf"\(\s*{re.escape(t)}\s*\)", para))
            if tl not in seen_first:
                seen_first[tl] = start
                new_here.append(t)
                if not defined_here and tl not in explained:
                    add("READER-UNKNOWN-TERM", "WARN", start, t,
                        f"'{t}' is not in the reader's known terms and is never explained: define it at first use")
        if len(new_here) > budget:
            add("READER-TERM-OVERLOAD", "WARN", start, ", ".join(new_here),
                f"{len(new_here)} new terms in one paragraph (reader budget {budget}): spread them out or explain them")
        low = para.lower()
        for pre in persona.get("prerequisite_concepts", []):
            for key in [pre.get("concept", "")] + pre.get("needs", []):
                if key and key.lower() in low:
                    concept_first.setdefault(key.lower(), start)
        nums = NUM_RE.findall(CLAIM_TAG_RE.sub("", para))
        if len(nums) >= 6 and len(para.split()) > 120 and not para.lstrip().startswith("|"):
            add("M11-DENSE-PARAGRAPH", "INFO", start, para[:80], f"{len(nums)} numbers in one paragraph: consider a table")
        for s in split_sentences(para):
            for msg in excess_precision(CLAIM_TAG_RE.sub("", s)):
                add("M11-EXCESS-PRECISION", "WARN", start, s, msg)
    for pre in persona.get("prerequisite_concepts", []):
        c = pre.get("concept", "").lower()
        if c in concept_first:
            for need in pre.get("needs", []):
                n = need.lower()
                if n not in concept_first or concept_first[n] > concept_first[c]:
                    add("READER-PREREQ-ORDER", "WARN", concept_first[c], pre.get("concept"),
                        f"'{pre.get('concept')}' appears before its prerequisite '{need}' is introduced")
    low_md = body.lower()
    for mis in persona.get("likely_misconceptions", []):
        trig = [t for t in mis.get("trigger_terms", []) if t.lower() in low_md]
        corr = [t for t in mis.get("corrective_terms", []) if t.lower() in low_md]
        if trig and not corr:
            add("READER-MISCONCEPTION", "WARN", 0, mis.get("misconception"),
                f"readers may think '{mis.get('misconception')}'; the paper mentions {trig} but never makes the "
                f"corrective point ({mis.get('corrective_point', '')})")
    for q in persona.get("reader_questions", []):
        keys = {w for w in WORD_RE.findall(q.lower()) if w not in COMMON}
        if keys and not any(len(keys & set(WORD_RE.findall(p.lower()))) >= max(1, len(keys) // 2) for _, _, p in paras):
            add("READER-QUESTION-UNANSWERED", "INFO", 0, q, "no paragraph addresses this reader question")
    entries = (ledger or {}).get("terms", [])      # research_story.md section 5: list of {term, synonyms_forbidden}
    if isinstance(entries, dict):
        entries = [dict(v, term=k) for k, v in entries.items()]
    for info in entries:
        term = info.get("term", "")
        for syn in info.get("synonyms_forbidden", []) or info.get("forbidden_synonyms", []) or []:
            for start, _, para in paras:
                if re.search(rf"\b{re.escape(syn)}\b", para, re.I):
                    add("M11-SYNONYM-DRIFT", "WARN", start, syn, f"'{syn}' drifts from the registered term '{term}'")
    return f


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--rcs", required=True)
    ap.add_argument("--persona")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    load = lambda p: json.loads(p.read_text(encoding="utf-8")) if p.exists() else None  # noqa: E731
    reader = load(rcs / "plan" / "reader_model.json") or {}
    ledger = load(rcs / "story" / "term_ledger.json")
    f = audit(Path(a.draft).read_text(encoding="utf-8"), reader, ledger, a.persona)
    rep = {"tool": "audit_reader", "reader_model": bool(reader), "errors": 0,
           "warnings": sum(x["level"] == "WARN" for x in f), "findings": f}
    if a.out:
        Path(a.out).write_text(json.dumps(rep, indent=2), encoding="utf-8")
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        for x in f:
            print(f"{x['level']:5} L{x['line']:<4} {x['rule']:28} {x['message']}")
        print(f"\n{rep['warnings']} warning(s)" + ("" if reader else " (no reader_model.json: persona checks skipped)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
