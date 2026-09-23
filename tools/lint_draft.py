#!/usr/bin/env python3
"""Lint a Markdown draft for Research Communication Engine anti-patterns.

This is a *screen*, not a judge. It finds surface signatures of problems described in
skill/anti_patterns.md, so that audits (workflow steps 12-17) look in the right places.
It never rewrites text.

Usage
  python tools/lint_draft.py draft.md [--rcs .rcs] [--final] [--require-tags]
                                      [--known-acronyms GPU,CPU] [--json]

  --rcs           resolve {C###} tags against .rcs/claims/claim_evidence_map.json and
                  check verbs against claim types
  --require-tags  treat untagged claim-like sentences as orphan claims (draft mode default
                  is: enabled automatically if the draft contains any {C###} tag)
  --final         final-manuscript mode: any remaining tag or [MISSING/CITATION NEEDED/ASK
                  AUTHOR] marker is an ERROR

Exit code 1 if any ERROR.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import (  # noqa: E402
    CLAIM_ID_RE,
    CLAIM_TAG_RE,
    INJECTION_RE,
    MARKER_RE,
    ZERO_WIDTH_RE,
    iter_paragraphs,
    load_json,
    split_sentences,
)

RULES = {
    # rule_id: (level, regex, message)
    "B1-novelty": ("WARN", re.compile(r"\b(novel|unprecedented|pioneering|first[- ]ever|for the first time|(?:is|are|was|were) the first (?:to|method|approach|work|study))\b", re.I),
                   "novelty claim: needs a search-scoped literature basis (citation_rules.md section 5)"),
    "B3-sota": ("WARN", re.compile(r"\b(state[- ]of[- ]the[- ]art|SOTA)\b"),
                "SOTA claim: name benchmark, full comparison set and date, or remove"),
    "B4-proof": ("WARN", re.compile(r"\b(prove[sd]?|proving|proven|conclusively|beyond (any )?doubt|undeniabl\w*|irrefutabl\w*)\b", re.I),
                 "proof language: empirical results 'show/indicate/suggest', they do not prove"),
    "B9-significance": ("WARN", re.compile(r"\bsignificant(ly)?\b", re.I),
                        "'significant' without a named statistical test in the same sentence"),
    "B9-intensifier": ("WARN", re.compile(r"\b(dramatic(ally)?|remarkabl[ey]|substantial(ly)?|huge|massive(ly)?|vastly|drastic(ally)?|tremendous(ly)?)\b", re.I),
                       "intensifier: give the number and a reference point instead"),
    "B5-causal": ("INFO", re.compile(r"\b(causes?|caused|leads? to|led to|drives?|driven by|due to|results? in)\b", re.I),
                  "causal wording: requires causal design or ablation; otherwise 'is associated with'"),
    "B13-invented-consensus": ("WARN", re.compile(r"\b(reviewers (will|would) (expect|agree)|the community agrees|it is (widely|well|generally) (known|accepted)|everyone knows)\b", re.I),
                               "appeal to unstated consensus: cite or remove"),
    "B-absolute": ("INFO", re.compile(r"\b(always|never|in all cases|without exception|guarantees?)\b", re.I),
                   "absolute term: justified only by complete enumeration or proof"),
    "C4-style-marker": ("INFO", re.compile(r"\b(delv(e|es|ing)|intricat\w*|pivotal|showcas\w*|underscor\w*|meticulous\w*|commendabl\w*|noteworthy|realm|tapestry|groundbreaking|game[- ]chang\w*)\b", re.I),
                        "LLM-associated style marker (not wrong per se; replace if it adds nothing)"),
    "A-hedge-filler": ("INFO", re.compile(r"\b(clearly|obviously|of course|needless to say)\b", re.I),
                       "assertive filler: delete or show why it is clear"),
    "A-figure-position": ("WARN", re.compile(r"\b(figure|table|fig\.)\s+(below|above)\b", re.I),
                          "refer to visuals by number, not position (F0 Unit 3)"),
}
SIG_TEST_RE = re.compile(r"(p\s*[<=>≤]|\btest\b|t-test|wilcoxon|anova|bootstrap|confidence interval|\bCI\b|α|alpha\s*=|statistically)", re.I)
NUMBER_RE = re.compile(r"(\d+(\.\d+)?\s*%|\b\d+\.\d+\b|\b\d+\s*(ms|s|x|×)\b)")
PERCENT_RE = re.compile(r"\d+(\.\d+)?\s*%")
DECIMAL_RE = re.compile(r"\b\d+\.\d+\b")
METRIC_WORD_RE = re.compile(r"\b(MAE|RMSE|MSE|error|accuracy|F1|score|loss|precision|recall|AUC|BLEU|perplexity|latency|throughput)\b", re.I)
COMPARATIVE_RE = re.compile(r"\b(outperform\w*|better than|worse than|improv\w*|reduc\w*|increas\w*|decreas\w*|higher|lower|faster|slower|exceed\w*|surpass\w*|superior)\b", re.I)
INTERPRETIVE_CUE_RE = re.compile(r"\b(suggest\w*|indicat\w*|mean\w*|because|therefore|thus|answer\w*|RQ\d|consistent with|impl(y|ies|ied)|so that|which shows|this (reduction|increase|difference|result|gap|pattern)|we interpret|explain\w*|attribut\w*|not (establish|show)\w*)\b", re.I)
STRONG_VERB_RE = re.compile(r"\b(shows? that|proves?|demonstrates?|establish(es)?|confirms?)\b", re.I)
PAPER_BY_PAPER_RE = re.compile(r"^(\[\d+(?:[,–-]\s*\d+)*\]|[A-Z][A-Za-z\-]+ (?:et al\.|and [A-Z][A-Za-z\-]+)(?: \(\d{4}\)| \[\d+\])?)\s+(proposed|introduced|used|developed|presented|studied|showed|applied|designed|explored|investigated|extended|built)\b")
ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,}[a-z]?)\b")
ACRONYM_DEF_RE = re.compile(r"\(([A-Z][A-Z0-9]{1,}[a-z]?)\)")
QUESTION_RE = re.compile(r"\b(RQ\d|we ask|research questions?|this (paper|work|study) asks|we (investigate|test|examine) whether|our (aim|objective|goal) is)\b", re.I)
CONTRIB_RE = re.compile(r"\b(contributions?|we contribute)\b", re.I)
TRANSITION_RE = re.compile(r"^(Moreover|Furthermore|Additionally|In addition|Besides|Also),", re.I)
CAPTION_RE = re.compile(r"^\**\s*(Figure|Fig\.|Table)\s+(\d+)[\.:]", re.I)
VISUAL_MENTION_RE = re.compile(r"\b(Figure|Fig\.|Table)\s+(\d+)", re.I)
ACRONYM_STOP = {"I", "II", "III", "IV", "V", "VI", "OK", "US", "UK", "EU", "PDF", "URL", "DOI", "ID", "IDS", "NA", "TODO",
                "MISSING", "RESULT", "CITATION", "NEEDED", "ASK", "AUTHOR", "RQ", "RQS", "SI"}


class Lint:
    def __init__(self) -> None:
        self.findings: list[dict] = []

    def add(self, rule: str, level: str, line: int, excerpt: str, msg: str) -> None:
        self.findings.append({"rule": rule, "level": level, "line": line,
                              "excerpt": excerpt[:160], "message": msg})

    def count(self, level: str) -> int:
        return sum(1 for f in self.findings if f["level"] == level)


def load_claims(rcs: Path | None) -> dict[str, dict]:
    """Claims and limitations keyed by ID (limitations get claim_type 'limitation')."""
    if not rcs:
        return {}
    p = rcs / "claims" / "claim_evidence_map.json"
    if not p.exists():
        return {}
    data = load_json(p)
    out = {c["id"]: c for c in data.get("claims", [])}
    out.update({lim["id"]: dict(lim, claim_type="limitation") for lim in data.get("limitations", [])})
    return out


def lint_text(md: str, claims: dict[str, dict], final: bool, require_tags: bool,
              known_acronyms: set[str]) -> Lint:
    L = Lint()
    has_tags = bool(CLAIM_TAG_RE.search(md))
    orphan_mode = require_tags or has_tags

    # Injection / hidden characters (whole text)
    for no, line in enumerate(md.splitlines(), 1):
        if ZERO_WIDTH_RE.search(line):
            L.add("C6-hidden-chars", "ERROR", no, line, "zero-width/hidden characters (possible injection)")
        if INJECTION_RE.search(line):
            L.add("C6-injection", "ERROR", no, line, "instruction-like text aimed at models/reviewers (INJECTION_DETECTED)")
        for m in MARKER_RE.finditer(line):
            L.add("marker", "ERROR" if final else "INFO", no, m.group(0),
                  "unresolved marker" + (" in final manuscript" if final else " (list in open_issues.md)"))
        if final and CLAIM_TAG_RE.search(line):
            L.add("tag-left", "ERROR", no, line, "claim tag left in final manuscript")

    paragraphs = list(iter_paragraphs(md))
    words_total = 0
    transitions = 0
    acr_first_use: dict[str, tuple[int, int]] = {}   # acronym -> (sentence position, line)
    acr_defined_at: dict[str, tuple[int, int]] = {}
    pos = 0
    acr_uses: dict[str, int] = {}
    caption_lines: dict[str, int] = {}
    mentions: dict[str, list[int]] = {}
    section_sents: dict[str, list[str]] = {}

    for start, section, para in paragraphs:
        sec_key = section.lower()
        cap = CAPTION_RE.match(para)
        if cap:
            key = f"{cap.group(1)[0].upper()}{cap.group(2)}"
            caption_lines.setdefault(key, start)
        else:
            for m in VISUAL_MENTION_RE.finditer(para):
                mentions.setdefault(f"{m.group(1)[0].upper()}{m.group(2)}", []).append(start)

        sents = split_sentences(para)
        section_sents.setdefault(sec_key, []).extend(sents)
        numeric_run = 0
        paper_run = 0
        for s in sents:
            pos += 1
            words = len(s.split())
            words_total += words
            if TRANSITION_RE.match(s):
                transitions += 1
            if words > 35:
                L.add("A-long-sentence", "INFO", start, s, f"{words}-word sentence: split or keep with reason")
            tag_ids = CLAIM_ID_RE.findall(" ".join(m.group(0) for m in CLAIM_TAG_RE.finditer(s)))

            for rule, (level, rx, msg) in RULES.items():
                m = rx.search(s)
                if not m:
                    continue
                if rule == "B9-significance" and SIG_TEST_RE.search(s):
                    continue
                if rule == "B5-causal":
                    types = {claims.get(t, {}).get("claim_type") for t in tag_ids}
                    if types & {"observed", "interpretation", "speculation", "hypothesis"}:
                        level = "WARN"
                L.add(rule, level, start, s, msg)

            # claim-tag checks
            for t in tag_ids:
                if claims and t not in claims:
                    L.add("tag-unresolved", "ERROR", start, s, f"{t} not in claim map")
                ctype = claims.get(t, {}).get("claim_type")
                if ctype in {"interpretation", "speculation", "hypothesis", "future"} and STRONG_VERB_RE.search(s):
                    L.add("B4-verb-vs-type", "ERROR", start, s, f"{t} is '{ctype}' but sentence uses a strong verb")

            is_numeric = bool(NUMBER_RE.search(s))
            claim_like = bool(COMPARATIVE_RE.search(s) or PERCENT_RE.search(s)
                              or (DECIMAL_RE.search(s) and METRIC_WORD_RE.search(s)))
            if orphan_mode and not cap and not tag_ids and not MARKER_RE.search(s) and claim_like \
                    and not s.rstrip().endswith("?") \
                    and not s.lower().startswith(("table", "figure", "fig.")):
                L.add("C1-orphan-claim", "WARN", start, s, "claim-like sentence without {C###} tag")

            # result dumping: consecutive numeric sentences without interpretation
            if is_numeric and not INTERPRETIVE_CUE_RE.search(s) and not cap:
                numeric_run += 1
                if numeric_run == 3:
                    L.add("A6-result-dumping", "WARN", start, s,
                          "3+ consecutive numeric sentences with no interpretation (apply the RIC)")
            else:
                numeric_run = 0

            if PAPER_BY_PAPER_RE.match(s):
                paper_run += 1
                if paper_run == 3:
                    L.add("A9-paper-by-paper", "WARN", start, s,
                          "'A did X. B did Y. C did Z.' pattern: organise literature by dimension")
            else:
                paper_run = 0

            # acronyms
            for m in ACRONYM_DEF_RE.finditer(s):
                acr_defined_at.setdefault(m.group(1), (pos, start))
            stripped = CLAIM_TAG_RE.sub("", MARKER_RE.sub("", s))
            for m in ACRONYM_RE.finditer(stripped):
                a = m.group(1)
                if a in ACRONYM_STOP or a in known_acronyms or re.fullmatch(r"[A-Z]\d+|RQ\d+|C\d{3,}|E\d{3,}", a):
                    continue
                acr_uses[a] = acr_uses.get(a, 0) + 1
                acr_first_use.setdefault(a, (pos, start))

    for a, (first_pos, first_line) in acr_first_use.items():
        d = acr_defined_at.get(a)
        if d is None:
            L.add("A3-undefined-acronym", "WARN", first_line, a, f"acronym '{a}' never defined")
        elif d[0] > first_pos:
            L.add("A3-use-before-definition", "WARN", first_line, a,
                  f"'{a}' used (line {first_line}) before its definition (line {d[1]})")
        if acr_uses[a] < 3 and d is not None:
            L.add("A4-rare-acronym", "INFO", first_line, a, f"'{a}' used {acr_uses[a]}x: spell out instead")

    for key, cap_line in caption_lines.items():
        before = [ln for ln in mentions.get(key, []) if ln < cap_line]
        if not mentions.get(key):
            L.add("A7-figure-not-discussed", "WARN", cap_line, key, f"{key} is never referred to in the text (FIGURE_NOT_EXPLAINED)")
        elif not before:
            L.add("A7-figure-late-reference", "INFO", cap_line, key, f"{key} is first referenced after it appears")

    if words_total and transitions * 1000 / words_total > 3:
        L.add("A15-decorative-transitions", "INFO", 0, f"{transitions} additive transitions",
              "many additive transitions: check each names a true relation")

    intro = " ".join(next((v for k, v in section_sents.items() if "introduction" in k), []))
    if intro:
        if not QUESTION_RE.search(intro):
            L.add("A1-late-question", "WARN", 0, "Introduction",
                  "no explicit research question/objective in the Introduction")
        if not CONTRIB_RE.search(intro):
            L.add("A2-buried-contribution", "WARN", 0, "Introduction",
                  "no contribution statement in the Introduction")

    abstract = next((v for k, v in section_sents.items() if "abstract" in k), [])
    conclusion = next((v for k, v in section_sents.items() if "conclusion" in k), [])
    if abstract and conclusion:
        def toks(x: str) -> set[str]:
            return {w for w in re.findall(r"[a-z]{4,}", x.lower())}
        overlap = 0
        for cs in conclusion:
            ct = toks(cs)
            if ct and any(len(ct & toks(a)) / max(1, len(ct | toks(a))) > 0.6 for a in abstract):
                overlap += 1
        if overlap / len(conclusion) > 0.4:
            L.add("A12-echo-conclusion", "WARN", 0, f"{overlap}/{len(conclusion)} sentences",
                  "conclusion largely repeats the abstract: synthesise instead")
    return L


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--rcs")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--require-tags", action="store_true")
    ap.add_argument("--known-acronyms", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    md = Path(args.draft).read_text(encoding="utf-8")
    known = {a.strip() for a in args.known_acronyms.split(",") if a.strip()}
    L = lint_text(md, load_claims(Path(args.rcs) if args.rcs else None), args.final, args.require_tags, known)
    if args.json:
        print(json.dumps({"errors": L.count("ERROR"), "warnings": L.count("WARN"), "findings": L.findings}, indent=2))
    else:
        for f in sorted(L.findings, key=lambda f: (f["line"], f["rule"])):
            print(f"{f['level']:5} L{f['line']:<4} {f['rule']:<28} {f['message']}\n      > {f['excerpt']}")
        print(f"\n{L.count('ERROR')} error(s), {L.count('WARN')} warning(s), {L.count('INFO')} info")
    return 1 if L.count("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
