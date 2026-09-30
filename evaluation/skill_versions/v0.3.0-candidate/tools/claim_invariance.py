#!/usr/bin/env python3
"""Claim-invariance check across an edit (workflow step 21, gate G5; docs/06_VNEXT_SPEC.md section 10 case 9).

Compare the tagged draft before and after a language edit. For every claim/limitation tag, the text
carrying it must keep the same numbers, the same scope and at most the same strength.

  CLAIM_DROPPED           a tag present before the edit is gone                                ERROR
  CLAIM_DRIFT_NUMBER      the numbers attached to a claim changed                              ERROR
  CLAIM_DRIFT_SCOPE       the edit widened scope ("on one split" -> "across datasets") or
                          removed a scope qualifier                                            ERROR
  CLAIM_DRIFT_STRENGTH    the edit removed a hedge or added a strong verb ("suggests" ->
                          "shows")                                                             ERROR
  CLAIM_ADDED             a tag appears only after the edit                                    WARN

Both drafts must carry {C###}/{L###} tags (run this before tags are stripped).
Usage: python tools/claim_invariance.py before.md after.md [--json] [--out F]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import CLAIM_ID_RE, CLAIM_TAG_RE, split_sentences  # noqa: E402

NUM_RE = re.compile(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?%?")
WIDE_RE = re.compile(r"\b(across (?:all |multiple |several |many |the )?(?:datasets|domains|tasks|benchmarks|splits|settings|"
                     r"languages|models)|(?:all|every|any) (?:datasets?|domains?|tasks?|benchmarks?|settings?|conditions?|cases?)|"
                     r"in general|generally|generali[sz]\w*|universally|always|consistently|robust\w*|in practice)\b", re.I)
NARROW_RE = re.compile(r"\b(on (?:one|a single|this|the tested) (?:split|dataset|seed|run|benchmark|task)|single (?:split|dataset|"
                       r"seed|run)|only|in this setting|under (?:these|the tested) conditions|in our experiments|on (?:the )?"
                       r"(?:test|validation) split|for (?:this|the tested) (?:dataset|model|setting))\b", re.I)
HEDGE_RE = re.compile(r"\b(suggests?|may|might|could|appears?|seems?|is consistent with|indicat\w*|likely|possibly|"
                      r"we (?:interpret|hypothesi[sz]e|speculate))\b", re.I)
STRONG_RE = re.compile(r"\b(shows? that|proves?|demonstrates?|establish(?:es)?|confirms?|clearly|definitively)\b", re.I)


def claim_text(md: str) -> dict[str, str]:
    out: dict[str, list[str]] = {}
    for s in split_sentences(md.replace("\n", " ")):
        ids = CLAIM_ID_RE.findall(" ".join(m.group(0) for m in CLAIM_TAG_RE.finditer(s)))
        for i in ids:
            out.setdefault(i, []).append(CLAIM_TAG_RE.sub("", s))
    return {k: " ".join(v) for k, v in out.items()}


def _set(rx: re.Pattern, text: str) -> set[str]:
    return {m.group(0).lower() for m in rx.finditer(text)}


def compare(before: str, after: str) -> list[dict]:
    b, a = claim_text(before), claim_text(after)
    f: list[dict] = []

    def add(rule: str, level: str, cid: str, msg: str) -> None:
        f.append({"rule": rule, "level": level, "claim": cid, "message": msg})

    for cid, tb in b.items():
        if cid not in a:
            add("CLAIM_DROPPED", "ERROR", cid, "tag removed by the edit (the claim map still has it)")
            continue
        ta = a[cid]
        nb, na = Counter(NUM_RE.findall(tb)), Counter(NUM_RE.findall(ta))
        if nb != na:
            add("CLAIM_DRIFT_NUMBER", "ERROR", cid, f"numbers changed: {sorted(nb.elements())} -> {sorted(na.elements())}")
        widened = _set(WIDE_RE, ta) - _set(WIDE_RE, tb)
        narrowed_lost = _set(NARROW_RE, tb) - _set(NARROW_RE, ta)
        if widened or narrowed_lost:
            add("CLAIM_DRIFT_SCOPE", "ERROR", cid,
                "scope changed: " + "; ".join(x for x in (f"added {sorted(widened)}" if widened else "",
                                                           f"removed qualifier {sorted(narrowed_lost)}" if narrowed_lost else "") if x))
        hedges_lost = _set(HEDGE_RE, tb) - _set(HEDGE_RE, ta)
        strong_added = _set(STRONG_RE, ta) - _set(STRONG_RE, tb)
        if hedges_lost or strong_added:
            add("CLAIM_DRIFT_STRENGTH", "ERROR", cid,
                "strength changed: " + "; ".join(x for x in (f"hedge removed {sorted(hedges_lost)}" if hedges_lost else "",
                                                              f"strong wording added {sorted(strong_added)}" if strong_added else "") if x))
    for cid in a.keys() - b.keys():
        add("CLAIM_ADDED", "WARN", cid, "tag only in the edited draft: an edit must not add claims")
    return f


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    f = compare(Path(a.before).read_text(encoding="utf-8"), Path(a.after).read_text(encoding="utf-8"))
    import hashlib
    rep = {"tool": "claim_invariance", "before": str(a.before).replace("\\", "/"), "after": str(a.after).replace("\\", "/"),
           "after_sha256": hashlib.sha256(Path(a.after).read_bytes()).hexdigest(),
           "errors": sum(x["level"] == "ERROR" for x in f),
           "warnings": sum(x["level"] == "WARN" for x in f), "findings": f}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(rep, indent=2), encoding="utf-8")
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        for x in f:
            print(f"{x['level']:5} {x['claim']:6} {x['rule']:22} {x['message']}")
        print(f"\n{rep['errors']} error(s), {rep['warnings']} warning(s)")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
