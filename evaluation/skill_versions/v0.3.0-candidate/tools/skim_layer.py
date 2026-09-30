#!/usr/bin/env python3
"""Claim compression and skimming layer (vNext Stage 3: M12).

  build  <.rcs>           write .rcs/plan/skim.md: a 30-second outline (the 7 spine lines), evidence-locked
                          one-sentence findings (verbatim spine-bound claim statements, tagged), and each figure's
                          takeaway (first caption sentence). Nothing is paraphrased by the tool.
  check  <text> --rcs     verify that compressed text (an abstract, a skim sheet, headings, a slide) keeps what the
                          tagged claims say:
      M12-NUMBER-CHANGED       a number appears that the tagged claim does not contain                  ERROR
      M12-SCOPE-DROPPED        a scope qualifier of the claim ("on one split", "n = 24") was dropped      ERROR
      M12-SCOPE-WIDENED        wording wider than the claim ("across datasets", "generally")             ERROR
      M12-HEDGE-DROPPED        the claim's hedge ("suggests") became plain assertion or strong verb      ERROR
      M12-UNCERTAINTY-DROPPED  a point estimate kept without the interval the claim reports             ERROR
      M12-DENOMINATOR-DROPPED  "9 of 15" became "9"                                                    ERROR
      M12-GENERIC-HEADING      a subsection heading names a slot ("Results 2") instead of the finding  INFO

Usage: python tools/skim_layer.py build .rcs
       python tools/skim_layer.py check abstract.md --rcs .rcs [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from claim_invariance import HEDGE_RE, NARROW_RE, STRONG_RE, WIDE_RE  # noqa: E402
from rce_common import CLAIM_ID_RE, CLAIM_TAG_RE, split_sentences  # noqa: E402

NUM_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?%?")
UNC_RE = re.compile(r"(\bCI\b|confidence interval|±|\+/-|\bstd\b|standard (deviation|error)|\binterval\b)", re.I)
N_RE = re.compile(r"\bn\s*=\s*\d+", re.I)
DENOM_RE = re.compile(r"\b(\d+)\s+(?:of|out of)\s+(?:the\s+)?(\d+)\b", re.I)
NUMBERING_RE = re.compile(r"\b(Figure|Fig\.|Table|Section|§|Appendix|Step|RQ|Q)\s*\d+[a-z]?\b:?", re.I)
GENERIC_HEADING_RE = re.compile(r"^#{3,}\s*(\d+(\.\d+)*\s*)?(results?|experiments?|analysis|evaluation|discussion|findings?|"
                                r"setup|ablations?|observations?)(\s+\d+)?\s*$", re.I)


def _nums(t: str) -> set[str]:
    return {n.rstrip("%") for n in NUM_RE.findall(t)}


def load_claims(rcs: Path) -> dict[str, dict]:
    p = rcs / "claims" / "claim_evidence_map.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    return {c["id"]: c for c in d.get("claims", []) + d.get("limitations", [])}


def check(text: str, claims: dict[str, dict]) -> list[dict]:
    f: list[dict] = []

    def add(rule, level, s, msg):
        f.append({"rule": rule, "level": level, "excerpt": s[:160], "message": msg})

    for line in text.splitlines():
        if GENERIC_HEADING_RE.match(line.strip()):
            add("M12-GENERIC-HEADING", "INFO", line, "heading names a slot; say what the section finds")
    units = [s for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")
             for s in split_sentences(re.sub(r"^\s*([-*]|\d+[.)])\s+", "", ln))]      # bullets are boundaries
    for s in units:
        ids = CLAIM_ID_RE.findall(" ".join(m.group(0) for m in CLAIM_TAG_RE.finditer(s)))
        src = " ".join(claims[i].get("statement", "") for i in ids if i in claims)
        if not src:
            continue
        s0 = NUMBERING_RE.sub(" ", CLAIM_TAG_RE.sub("", s))
        extra = _nums(s0) - _nums(src)
        if extra:
            add("M12-NUMBER-CHANGED", "ERROR", s0, f"numbers {sorted(extra)} are not in {ids}: compression may drop numbers, never change them")
        narrow = {m.group(0).lower() for m in NARROW_RE.finditer(src)} | {m.group(0).lower() for m in N_RE.finditer(src)}
        kept_narrow = {m.group(0).lower() for m in NARROW_RE.finditer(s0)} | {m.group(0).lower() for m in N_RE.finditer(s0)}
        if narrow - kept_narrow:
            add("M12-SCOPE-DROPPED", "ERROR", s0, f"scope qualifier(s) {sorted(narrow - kept_narrow)} of {ids} dropped")
        wide = {m.group(0).lower() for m in WIDE_RE.finditer(s0)} - {m.group(0).lower() for m in WIDE_RE.finditer(src)}
        if wide:
            add("M12-SCOPE-WIDENED", "ERROR", s0, f"wider than {ids}: {sorted(wide)}")
        hedges = {m.group(0).lower() for m in HEDGE_RE.finditer(src)}
        if hedges and (not HEDGE_RE.search(s0) or STRONG_RE.search(s0)):
            add("M12-HEDGE-DROPPED", "ERROR", s0, f"{ids} is hedged ({sorted(hedges)}); the compressed sentence is not")
        elif STRONG_RE.search(s0) and not STRONG_RE.search(src):
            add("M12-HEDGE-DROPPED", "ERROR", s0, f"strong wording not in {ids}")
        if UNC_RE.search(src) and (_nums(s0) & _nums(src)) and not UNC_RE.search(s0):
            add("M12-UNCERTAINTY-DROPPED", "ERROR", s0, f"keeps an estimate from {ids} but drops its interval")
        for m in DENOM_RE.finditer(src):
            num, den = m.group(1), m.group(2)
            if num in _nums(s0) and den not in _nums(s0):
                add("M12-DENOMINATOR-DROPPED", "ERROR", s0, f"'{m.group(0)}' in {ids} lost its denominator")
    return f


def build(rcs: Path) -> str:
    claims = load_claims(rcs)
    spine_p = rcs / "story" / "spine.md"
    spine = [ln.strip() for ln in spine_p.read_text(encoding="utf-8").splitlines() if re.match(r"^\s*[1-7][.)]", ln)] \
        if spine_p.exists() else []
    bound = [i for ln in spine for i in CLAIM_ID_RE.findall(ln) if i in claims and i.startswith("C")] or \
        [i for i in claims if i.startswith("C")]
    reg_p = rcs / "plan" / "visual_registry.json"
    reg = json.loads(reg_p.read_text(encoding="utf-8")) if reg_p.exists() else {"visuals": []}
    out = ["# Skim sheet (generated; claim text verbatim, do not paraphrase here)", "",
           "## 30-second outline (paper spine)", ""]
    out += [f"- {ln}" for ln in spine] or ["- (no spine.md yet)"]
    out += ["", "## Findings in one sentence each", ""]
    seen = []
    for i in bound:
        if i not in seen:
            seen.append(i)
            out.append(f"- {claims[i]['statement']} {{{i}}}")
    out += ["", "## Figure takeaways", ""]
    for v in reg.get("visuals", []):
        if v.get("caption") and v.get("status") not in ("BLOCKED", "NO_VALID_VISUAL"):
            first = split_sentences(v["caption"])[0]
            tags = "".join(f"{{{c}}}" for c in v.get("claim_ids", [])[:1])
            out.append(f"- {'Table' if v.get('representation') == 'table' else 'Figure'} {v.get('number', '?')}: {first} {tags}")
    text = "\n".join(out) + "\n"
    (rcs / "plan").mkdir(parents=True, exist_ok=True)
    (rcs / "plan" / "skim.md").write_text(text, encoding="utf-8")
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("rcs")
    c = sub.add_parser("check")
    c.add_argument("text")
    c.add_argument("--rcs", required=True)
    c.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        print(build(Path(a.rcs)))
        return 0
    f = check(Path(a.text).read_text(encoding="utf-8"), load_claims(Path(a.rcs)))
    errors = sum(x["level"] == "ERROR" for x in f)
    if a.json:
        print(json.dumps({"tool": "skim_layer", "errors": errors, "findings": f}, indent=2))
    else:
        for x in f:
            print(f"{x['level']:5} {x['rule']:26} {x['message']}")
        print(f"\n{errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
