#!/usr/bin/env python3
"""Trace every number in a draft to the evidence (docs/06_VNEXT_SPEC.md section 4.4).

For each number in the draft (prose, tables, captions), look for a source value:
  1. numbers in .rcs evidence items (value, summary, notes, conditions),
  2. numbers in the project files that evidence locators point to,
allowing (a) the draft's own rounding (0.8123 -> 0.81), (b) % <-> fraction (19.6% <-> 0.196),
(c) simple derived values (difference, ratio, relative change in %) -- but ONLY between numbers in the
evidence items cited by the claim(s) tagged on the same line. Deriving from the whole source would
"explain" almost any number by chance (measured: 38 of 40 fabricated numbers against a real paper).

  UNTRACED_PVALUE   a p-value (p < 0.05, p = 0.01) with no evidence item recording that test result:
                    ERROR always ("do not infer a p-value", spec section 10 case 3)
  UNTRACED_NUMBER   a number with no source value: WARN (ERROR with --strict)
  DERIVED_MATCH     traced only as a derived value: INFO (check that the derivation is the stated one)

Ignored: years 1900-2100, section/table/figure/question/claim numbers, reference numbers, list
enumerators, and small integers <= 12 used as words would be ("3 datasets") unless --strict.

Usage: python tools/verify_numbers.py paper.md --rcs .rcs [--project-root DIR] [--strict] [--json] [--out F]
Exit code 1 if any ERROR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import CLAIM_TAG_RE, MARKER_RE, load_json  # noqa: E402

# number, optional % or K/M/B multiplier; not part of an identifier (gpt-4-1106, v1.2.3, 38.6K handled)
NUM_RE = re.compile(r"(?<![\w.\-/])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(\s*%|[KMB](?![A-Za-z]))?(?![\w\-]|\.\d)")
MULT = {"K": 1e3, "M": 1e6, "B": 1e9}
PVAL_RE = re.compile(r"\bp\s*(?:-value\s*)?(<|=|≤|<=|>)\s*(0?\.\d+|1\.0+|\d(?:\.\d+)?e-?\d+)", re.I)
SKIP_BEFORE_RE = re.compile(r"(section|sec\.|§|table|tab\.|figure|fig\.|appendix|eq\.|equation|step|phase|stage|"
                            r"version|v|rq|q|chapter|part|item|row|column|line)\s*$", re.I)
HEADING_RE = re.compile(r"^\s*#+\s*[\d.]*")
REF_SECTION_RE = re.compile(r"(?im)^#+\s*references\b")
CITE_RE = re.compile(r"\([^()]*\b(19|20)\d{2}[a-z]?\)|\[\d+(?:[,–-]\s*\d+)*\]")
ID_RE = re.compile(r"\b[CLEQ]\d{2,}\b|\bSRC-\d+\b|\bRQ\d+\b|\bQ\d+\b")
EXTRACT_RE = re.compile(r"(-?\d+(?:,\d{3})*(?:\.\d+)?(?:e-?\d+)?)([KMB](?![A-Za-z]))?")


def _float(tok: str) -> float | None:
    try:
        return float(tok.replace(",", ""))
    except ValueError:
        return None


def numbers_in(text: str) -> list[float]:
    """All numbers in text; '38.6K' yields both 38.6 and 38600."""
    out: list[float] = []
    for m in EXTRACT_RE.finditer(text):
        x = _float(m.group(1))
        if x is None:
            continue
        out.append(x)
        if m.group(2):
            out.append(x * MULT[m.group(2)])
    return out


def _item_numbers(e: dict) -> list[float]:
    return numbers_in(json.dumps({k: e.get(k) for k in ("value", "summary", "notes", "conditions")}))


def claim_pools(rcs: Path) -> dict[str, list[float]]:
    """claim/limitation id -> numbers of the evidence items it cites (following C-> C references)."""
    ev_p, cm_p = rcs / "evidence" / "research_evidence.json", rcs / "claims" / "claim_evidence_map.json"
    if not (ev_p.exists() and cm_p.exists()):
        return {}
    ev = {e.get("id"): e for e in load_json(ev_p).get("items", [])}
    cm = load_json(cm_p)
    recs = {c["id"]: c for c in cm.get("claims", []) + cm.get("limitations", [])}

    def refs(cid: str, seen: set) -> set:
        if cid in seen or cid not in recs:
            return set()
        seen.add(cid)
        out = set()
        for ref in (recs[cid].get("evidence") or []):
            out |= refs(ref, seen) if ref.startswith(("C", "L")) else {ref}
        return out
    return {cid: [x for ref in refs(cid, set()) if ref in ev for x in _item_numbers(ev[ref])] for cid in recs}


def collect_source_numbers(rcs: Path, project_root: Path) -> tuple[list[float], list[float]]:
    """(all source numbers, recorded p-values)."""
    nums: list[float] = []
    pvals: list[float] = []
    ev_path = rcs / "evidence" / "research_evidence.json"
    files: set[Path] = set()
    if ev_path.exists():
        ev = load_json(ev_path)
        for e in ev.get("items", []):
            if e.get("status") == "superseded":
                continue
            nums += _item_numbers(e)
            v = e.get("value")
            if isinstance(v, dict):
                for k in ("p", "p_value"):
                    if isinstance(v.get(k), (int, float)):
                        pvals.append(float(v[k]))
            loc = (e.get("locator") or {}).get("path")
            if loc and (project_root / loc).is_file():
                files.add(project_root / loc)
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        nums += numbers_in(text)
        pvals += [x for x in (_float(m.group(2)) for m in PVAL_RE.finditer(text)) if x is not None]
    return nums, pvals


def _decimals(tok: str) -> int:
    return len(tok.split(".")[1]) if "." in tok else 0


def _matches(x: float, dec: int, pct: bool, src: set[float]) -> bool:
    cands = {x}
    if pct:
        cands.add(x / 100)
    else:
        cands.add(x * 100)
    tol = 0.5 * 10 ** (-dec) + 1e-9
    for s in src:
        for c in cands:
            scale_tol = tol if c == x else tol / 100 if c == x / 100 else tol * 100
            if abs(s - c) <= scale_tol:
                return True
    return False


def _derived(x: float, dec: int, pct: bool, src: list[float]) -> bool:
    tol = 0.5 * 10 ** (-dec) + 1e-9
    uniq = sorted(set(s for s in src if s != 0))[:400]
    for i, a in enumerate(uniq):
        for b in uniq[i + 1:]:
            vals = [abs(a - b), a / b, b / a, abs(a - b) * 100, abs(a - b) / abs(a) * 100, abs(a - b) / abs(b) * 100,
                    a / b * 100, b / a * 100]
            if any(abs(v - x) <= tol for v in vals):
                return True
    return False


def verify(md: str, rcs: Path, project_root: Path, strict: bool = False) -> list[dict]:
    src_list, pvals = collect_source_numbers(rcs, project_root)
    src = set(src_list)
    pools = claim_pools(rcs)
    findings: list[dict] = []
    body = REF_SECTION_RE.split(md)[0]
    for no, raw in enumerate(body.splitlines(), 1):
        tagged = re.findall(r"[CL]\d{3,}", " ".join(m.group(0) for m in CLAIM_TAG_RE.finditer(raw)))
        pool = [x for t in tagged for x in pools.get(t, [])]
        line = CLAIM_TAG_RE.sub("", MARKER_RE.sub("", raw))
        if HEADING_RE.match(line):
            line = HEADING_RE.sub("", line)
        for m in PVAL_RE.finditer(line):
            pv = _float(m.group(2))
            if pv is None or not any(abs(pv - q) <= 1e-12 + 0.5 * 10 ** (-_decimals(m.group(2))) for q in pvals):
                findings.append({"rule": "UNTRACED_PVALUE", "level": "ERROR", "line": no, "excerpt": m.group(0),
                                 "message": "p-value not recorded in any evidence item: never infer or restate a p-value "
                                            "that the evidence does not contain"})
        masked = PVAL_RE.sub(" ", CITE_RE.sub(" ", ID_RE.sub(" ", line)))
        for m in NUM_RE.finditer(masked):
            tok, suf = m.group(1), (m.group(2) or "").strip()
            pct = suf == "%"
            x = _float(tok)
            if x is None:
                continue
            if suf in MULT and not _matches(x, _decimals(tok), False, src):
                x, tok = x * MULT[suf], "0"          # compare the expanded value (38.6K -> 38600)
            before = masked[:m.start()]
            if SKIP_BEFORE_RE.search(before) or re.search(r"^\s*(\d+[.)]|[-*])\s*$", before):
                continue
            if not pct and "." not in tok and 1900 <= x <= 2100:
                continue
            if not strict and not pct and "." not in tok and x <= 12:
                continue
            if _matches(x, _decimals(tok), pct, src):
                continue
            if pool and _derived(x, _decimals(tok), pct, pool):
                findings.append({"rule": "DERIVED_MATCH", "level": "INFO", "line": no, "excerpt": tok + ("%" if pct else ""),
                                 "message": "matches only a difference/ratio of two source numbers: confirm the derivation"})
                continue
            findings.append({"rule": "UNTRACED_NUMBER", "level": "ERROR" if strict else "WARN", "line": no,
                             "excerpt": tok + ("%" if pct else ""),
                             "message": "no evidence value or project-file value matches this number (after rounding and "
                                        "% conversion): trace it to an E### item or remove it"})
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--rcs", required=True)
    ap.add_argument("--project-root")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    root = Path(a.project_root) if a.project_root else rcs.resolve().parent
    draft = Path(a.draft)
    f = verify(draft.read_text(encoding="utf-8"), rcs, root, a.strict)
    errors = sum(1 for x in f if x["level"] == "ERROR")
    report = {"tool": "verify_numbers", "draft": str(draft), "draft_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
              "strict": a.strict, "errors": errors, "warnings": sum(1 for x in f if x["level"] == "WARN"), "findings": f}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        for x in f:
            print(f"{x['level']:5} L{x['line']:<4} {x['rule']:<16} {x['excerpt']:<10} {x['message']}")
        print(f"\n{errors} error(s), {report['warnings']} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
