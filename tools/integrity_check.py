#!/usr/bin/env python3
"""Gate GI: the integrity check the author does not run (workflow steps 15 and 20; skill/integrity.md).

  python tools/integrity_check.py collect .rcs --stage pre --draft drafts/vNNN/paper.md
      Gather the evidence for failure modes M1-M7 and select the claim<->reference alignment sample, into
      audits/integrity/<stage>/bundle.json. The VERIFIER, in its own context, reads the bundle and writes
      audits/integrity/<stage>/verifier_report.json:
        {"draft_sha256": "...", "round": 1, "isolation": "isolated" | "none",
         "modes": {"M1": {"status": "CLEAR" | "SUSPECTED" | "INSUFFICIENT_EVIDENCE", "evidence": ["..."], "detail": "..."}, ...},
         "alignment": [{"row": "A001", "verdict": "supported" | "overstated" | "understated" | "unsupported" | "not_checkable",
                        "note": "..."}]}
  python tools/integrity_check.py gate .rcs --stage pre --draft drafts/vNNN/paper.md --out .rcs/audits/gates/GI_integrity.json
      Merge the VERIFIER's judgments with the deterministic results and decide. Run with the same draft.

The tool decides what it can prove, and the VERIFIER judges the rest. A CLEAR that contradicts a tool finding does not
stand (GI_CONTRADICTS_TOOL), and a CLEAR with no evidence cited is not a CLEAR. The report's words alone never pass the gate.

Blocking: any SUSPECTED; INSUFFICIENT_EVIDENCE on M1, M3, M5, M6 (at --stage final, on every mode). A declared
no-experiments paper is exempt from the INSUFFICIENT_EVIDENCE rule on M1, M3, M5, M6, unless the draft contradicts the
declaration. After at most 3 rounds, a block ends only by a named person's decision: list {"mode": "M5", "checkpoint":
"Q-012"} in audits/integrity/<stage>/decisions.json and answer that checkpoint with workflow_guard.py. A decision does
not change the mode's status, and it must appear in open_issues.md.

Stage final also confirms that paper/paper.md is the checked draft with the tags removed, that a mode SUSPECTED at stage
pre is now CLEAR, and that no cited source's retraction check is older than 30 days.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_draft import author_year_citations  # noqa: E402
from rce_common import CLAIM_ID_RE, CLAIM_TAG_RE, iter_paragraphs, load_json, load_schema, split_sentences, validate  # noqa: E402
import rce_index as ix  # noqa: E402
import verify_citations as vc  # noqa: E402
import verify_numbers  # noqa: E402
import workflow_guard  # noqa: E402

MODES = ("M1", "M2", "M3", "M4", "M5", "M6", "M7")
STATUSES = ("CLEAR", "INSUFFICIENT_EVIDENCE", "SUSPECTED")
EXPERIMENT_MODES = {"M1", "M3", "M5", "M6"}
VERDICTS = ("supported", "overstated", "understated", "unsupported", "not_checkable")
MAX_ROUNDS = 3
MIN_REASON = 20
RETRACTION_DAYS = 30
RESULT_TYPES = {"measured", "observed", "derived"}
METHOD_SECTION_RE = re.compile(r"\b(methods?|methodology|materials?|procedures?|setup|experiments?|experimental|implementation|study design)\b", re.I)
CORRECTNESS_RE = re.compile(r"\b(correctly implement\w*|implemented correctly|bug[- ]free|pipeline (is|was) correct|validated (the )?(implementation|pipeline)|"
                            r"verified (the )?(implementation|pipeline)|passes? (all )?tests?)\b", re.I)
LEAK_RE = re.compile(r"\b(leak\w*|overlap\w*|contaminat\w*|tuned on (the )?test|test set (was )?used|dev(elopment)? set|same (split|data) for|"
                     r"untuned|not tuned|default (hyper)?param\w*|unmatched|out of the box)\b", re.I)
COMPARE_RE = re.compile(r"\b(outperform\w*|better than|worse than|superior|beats?)\b", re.I)
SURPRISE_RE = re.compile(r"\b(surprising\w*|unexpected\w*|counter-?intuitive\w*|contrary to (our|the) (hypothes\w+|expectation\w*)|remarkabl\w*|strikingly)\b", re.I)
ROBUST_RE = re.compile(r"\b(seeds?|replicat\w*|rerun|re-run|ablation|repeated|robustness|sensitivity)\b", re.I)
SEEDS_RE = re.compile(r"\b(\d+)\s+(seeds?|runs?|repeats?|replicates?|folds?)\b", re.I)
RAN_RE = re.compile(r"\bwe (ran|trained|measured|evaluated|tested|benchmarked|recruited|collected)\b", re.I)
CAUSAL_RE = re.compile(r"\b(causes?|caused|leads? to|results? in|because of)\b", re.I)


def sha(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def tags(text: str) -> list[str]:
    return CLAIM_ID_RE.findall(" ".join(m.group(0) for m in CLAIM_TAG_RE.finditer(text)))


def strip_tags(md: str) -> str:
    return re.sub(r"\s*" + CLAIM_TAG_RE.pattern, "", md)


def sentences(md: str):
    for line, section, para in iter_paragraphs(md):
        for s in split_sentences(para):
            yield line, section, s


def _load(p: Path, default):
    return load_json(p) if p.exists() else default


def load_project(rcs: Path, root: Path, md: str) -> dict:
    cm = _load(rcs / "claims" / "claim_evidence_map.json", {})
    sources = _load(rcs / "corpus" / "source_registry.json", {"sources": []}).get("sources", [])
    spine = rcs / "story" / "spine.md"
    used = {t for _, _, s in sentences(md) for t in tags(s)}
    claims = {c["id"]: c for c in cm.get("claims", [])}
    return {"rcs": rcs, "root": root, "md": md, "claims": claims, "limitations": cm.get("limitations", []),
            "evidence": {e["id"]: e for e in _load(rcs / "evidence" / "research_evidence.json", {}).get("items", [])},
            "sources": sources, "state": _load(rcs / "state.json", {}), "config": _load(rcs / "plan" / "paper_config.json", {}),
            "spine_ids": set(CLAIM_ID_RE.findall(spine.read_text(encoding="utf-8"))) if spine.exists() else set(),
            "used": [claims[t] for t in sorted(used) if t in claims]}


def _hit(code: str, where: str, detail: str) -> dict:
    return {"code": code, "where": where, "detail": detail}


def _ev_items(p: dict, c: dict) -> list[dict]:
    return [p["evidence"][e] for e in c.get("evidence", []) if e in p["evidence"]]


def _ev_text(e: dict) -> str:
    return " ".join(str(e.get(k, "")) for k in ("summary", "notes", "conditions"))


# ------------------------------------------------------------------------------ deterministic evidence per mode
def m1_bug(p: dict) -> dict:
    signals, facts = [], []
    results = [c for c in p["used"] if c.get("claim_type") in RESULT_TYPES]
    for c in results:
        if not any(e.get("strength") == "hard" and (p["root"] / str((e.get("locator") or {}).get("path", ""))).is_file() for e in _ev_items(p, c)):
            signals.append(_hit("NO_RUN_RECORD", c["id"], "no hard evidence with an existing file behind this result"))
    for c in p["used"]:
        if CORRECTNESS_RE.search(c.get("statement", "")) and not any(re.search(r"test|log", str((e.get("locator") or {}).get("path", "")), re.I) for e in _ev_items(p, c)):
            signals.append(_hit("UNTESTED_PIPELINE_CLAIM", c["id"], "a correctness claim with no test or log behind it"))
    inv_p = p["rcs"] / "evidence" / "project_inventory.json"
    if inv_p.exists():
        files = load_json(inv_p)
        files = files.get("files", files) if isinstance(files, dict) else files
        classes = {f.get("class") or f.get("type") for f in files if isinstance(f, dict)}
        facts.append(f"inventory classes: {sorted(str(x) for x in classes)}")
        if results and not classes & {"code", "log", "result"}:
            signals.append(_hit("NO_CODE_OR_LOG", "evidence/project_inventory.json", "results are claimed, but no code, log or result file is inventoried"))
    spreads = [e["value"].get("std") for e in p["evidence"].values() if isinstance(e.get("value"), dict) and e["value"].get("std") is not None]
    for e in p["evidence"].values():
        v = e.get("value") if isinstance(e.get("value"), dict) else {}
        if v.get("std") == 0 and (v.get("n") or 0) > 1:
            signals.append(_hit("ZERO_VARIANCE", e["id"], f"std 0 across n={v.get('n')}: a constant may be leaking through"))
    if len(spreads) >= 3 and len(set(spreads)) == 1:
        signals.append(_hit("IDENTICAL_SPREADS", "evidence", f"every reported spread is {spreads[0]}: values too uniform to be measurements"))
    return {"errors": [], "signals": signals, "facts": facts}


def m2_citation(p: dict) -> dict:
    errors, signals = [], []
    gl = p["rcs"] / "audits" / "gates" / "GL_citations.json"
    reg = p["rcs"] / "corpus" / "source_registry.json"
    if not gl.exists():
        errors.append(_hit("GL_NOT_RUN", "audits/gates/GL_citations.json", "no GL report"))
    else:
        r = load_json(gl)
        if r.get("errors", 1) != 0:
            errors.append(_hit("GL_FAILED", "audits/gates/GL_citations.json", f"{r.get('errors')} error(s)"))
        elif reg.exists() and r.get("registry_sha256") != hashlib.sha256(reg.read_bytes()).hexdigest():
            errors.append(_hit("GL_STALE", "audits/gates/GL_citations.json", "the registry changed after GL ran: re-run it"))
    known = {(ix.surname(s["authors"][0]), int(s["year"])) for s in p["sources"] if s.get("authors") and s.get("year")}
    for no, line in enumerate(p["md"].splitlines(), 1):
        for name, year, text in author_year_citations(line):
            if (name, year) not in known:
                errors.append(_hit("CITATION_UNREGISTERED", f"line {no}", f"({text}) is not in the registry"))
    for s in p["sources"]:
        if (s.get("verification") or {}).get("lookup_verified") == "unresolvable":
            signals.append(_hit("UNRESOLVABLE_SOURCE", s["id"], "existence could not be confirmed by lookup; a person must check it"))
    return {"errors": errors, "signals": signals, "facts": [f"{len(p['sources'])} registered source(s)"]}


def m3_result(p: dict) -> dict:
    errors, signals = [], []
    for f in verify_numbers.verify(p["md"], p["rcs"], p["root"]):
        if f["rule"] == "UNTRACED_PVALUE" or f["level"] == "ERROR":
            errors.append(_hit(f["rule"], f"line {f['line']}", f"{f['excerpt']}: {f['message']}"))
        elif f["rule"] == "UNTRACED_NUMBER":
            signals.append(_hit(f["rule"], f"line {f['line']}", f["excerpt"]))
    for c in p["used"]:
        if c.get("claim_type") in RESULT_TYPES and not any(e.get("strength") == "hard" for e in _ev_items(p, c)):
            errors.append(_hit("NO_HARD_EVIDENCE", c["id"], "a result claim needs hard evidence"))
    ns = {e["value"].get("n") for e in p["evidence"].values() if isinstance(e.get("value"), dict) and e["value"].get("n")}
    for line, _, s in sentences(p["md"]):
        m = SEEDS_RE.search(strip_tags(s))
        if m and ns and int(m.group(1)) not in ns:
            signals.append(_hit("RUN_COUNT_UNMATCHED", f"line {line}", f"{m.group(0)!r} matches no recorded n ({sorted(ns)})"))
    return {"errors": errors, "signals": signals, "facts": []}


def m4_shortcut(p: dict) -> dict:
    signals = []
    for e in p["evidence"].values():
        if e.get("kind") in ("baseline", "limitation_noted", "observation", "method_detail", "negative_result") and LEAK_RE.search(_ev_text(e)):
            signals.append(_hit("SHORTCUT_NOTE", e["id"], _ev_text(e).strip()[:140]))
    for lim in p["limitations"]:
        if LEAK_RE.search(lim.get("statement", "")):
            signals.append(_hit("SHORTCUT_NOTE", lim.get("id", "limitation"), lim["statement"][:140]))
    for c in p["used"]:
        if COMPARE_RE.search(c.get("statement", "")) and not any(x.get("type") == "matched_evaluation" for x in c.get("licenses") or []):
            signals.append(_hit("UNMATCHED_COMPARISON", c["id"], "a comparison with no matched_evaluation license"))
    return {"errors": [], "signals": signals, "facts": []}


def m5_reframed(p: dict) -> dict:
    signals, facts = [], []
    for line, _, s in sentences(p["md"]):
        if SURPRISE_RE.search(s):
            items = [e for t in tags(s) if t in p["claims"] for e in _ev_items(p, p["claims"][t])]
            robust = any(isinstance(e.get("value"), dict) and (e["value"].get("n") or 0) >= 3 for e in items) or any(ROBUST_RE.search(_ev_text(e)) for e in items)
            if not robust:
                signals.append(_hit("UNEXAMINED_SURPRISE", f"line {line}", strip_tags(s)[:140]))
    negatives = [e["id"] for e in p["evidence"].values() if e.get("kind") == "negative_result"]
    if negatives:
        facts.append(f"negative results on record: {', '.join(negatives)}. Check none is reframed as a finding.")
    return {"errors": [], "signals": signals, "facts": facts}


def m6_method(p: dict) -> dict:
    errors, signals = [], []
    for line, section, s in sentences(p["md"]):
        if not METHOD_SECTION_RE.search(section):
            continue
        ids = [t for t in tags(s) if t in p["claims"]]
        for t in ids:
            basis = p["claims"][t].get("basis")
            if basis in ("none", "literature"):
                errors.append(_hit("METHOD_WITHOUT_BASIS", f"line {line} {t}", f"basis is {basis}: a method claim needs code or a project file"))
            elif basis not in ("code", "project_file"):
                signals.append(_hit("METHOD_BASIS_WEAK", f"line {line} {t}", f"basis is {basis or 'absent'}"))
        if not ids and re.search(r"\d", s):
            signals.append(_hit("UNTAGGED_METHOD_DETAIL", f"line {line}", strip_tags(s)[:140]))
    return {"errors": errors, "signals": signals, "facts": []}


def m7_frame(p: dict) -> dict:
    signals, facts = [], []
    alt = p["rcs"] / "story" / "alternatives.md"
    body = re.sub(r"^#.*$", "", alt.read_text(encoding="utf-8"), flags=re.M).strip() if alt.exists() else ""
    if not body:
        signals.append(_hit("NO_ALTERNATIVES", "story/alternatives.md", "no alternative explanation is recorded for the central claim"))
    changes = p["state"].get("story_changes") or []
    facts.append(f"{len(changes)} recorded RQ or spine change(s)")
    hashes = [r.get("sha256") for r in workflow_guard.load_ledger(p["rcs"]) if r.get("path") == "story/spine.md"]
    distinct = len(dict.fromkeys(hashes))
    if distinct > 1 and len(changes) < distinct - 1:
        signals.append(_hit("SILENT_SPINE_CHANGE", "story/spine.md", f"{distinct} spine versions in the ledger, {len(changes)} recorded change(s)"))
    if any(not str(c.get("reason", "")).strip() for c in changes if isinstance(c, dict)):
        signals.append(_hit("CHANGE_WITHOUT_REASON", "state.json", "an RQ or spine change has no reason"))
    if not (p["rcs"] / "story" / "rq_check.md").exists():
        signals.append(_hit("NO_RQ_CHECK", "story/rq_check.md", "step 5 left no record"))
    return {"errors": [], "signals": signals, "facts": facts}


CHECKS = {"M1": m1_bug, "M2": m2_citation, "M3": m3_result, "M4": m4_shortcut, "M5": m5_reframed, "M6": m6_method, "M7": m7_frame}


def declaration_contradicted(p: dict) -> list[str]:
    """A paper that declares no experiments but reports a run or a result as the authors' own contradicts itself."""
    if not p["config"].get("no_experiments"):
        return []
    found = [c["id"] for c in p["used"] if c.get("claim_type") in ("measured", "observed")]
    found += [f"line {line}" for line, _, s in sentences(p["md"]) if RAN_RE.search(s)]
    return found


def deterministic(p: dict) -> dict:
    return {m: CHECKS[m](p) for m in MODES}


# ------------------------------------------------------------------------------ alignment sample
def citation_rows(p: dict) -> list[dict]:
    index: dict[tuple, list[dict]] = {}
    for s in p["sources"]:
        if s.get("authors") and s.get("year"):
            index.setdefault((ix.surname(s["authors"][0]), int(s["year"])), []).append(s)
    rows = []
    for line, section, s in sentences(p["md"]):
        cited = []
        for name, year, text in author_year_citations(s):
            for src in index.get((name, year), []):
                cited.append({"cited": text, "source": src["id"], "read_depth": src.get("read_depth"),
                              "establishes": [{k: e.get(k) for k in ("statement", "support_quote", "location", "strength")} for e in src.get("establishes") or []]})
        if cited:
            rows.append({"id": f"A{len(rows) + 1:03d}", "line": line, "section": section, "sentence": strip_tags(s), "claims": tags(s), "sources": cited})
    return rows


def impact_basis(row: dict, p: dict) -> list[str]:
    basis = []
    claims = [p["claims"][t] for t in row["claims"] if t in p["claims"]]
    if set(row["claims"]) & p["spine_ids"]:
        basis.append("spine")
    if re.search(r"\d", re.sub(r"\([^()]*\b\d{4}[a-z]?\)", "", row["sentence"])):
        basis.append("numerical")
    if CAUSAL_RE.search(row["sentence"]) or any(c.get("licenses") for c in claims):
        basis.append("causal_or_licensed")
    if METHOD_SECTION_RE.search(row["section"]):
        basis.append("methods")
    if any(p["evidence"].get(e, {}).get("status") == "conflicting" for c in claims for e in c.get("evidence", [])):
        basis.append("disputed")
    return basis


def select(rows: list[dict], p: dict, stage: str, seed: str) -> list[dict]:
    """100% of high-impact sentences plus sentinels ordered by a hash of the seed. The seed is the draft's SHA-256, so the
    choice can be replayed by anyone and tuned by no one. Stage final checks every cited sentence."""
    high, rest = [], []
    for r in rows:
        basis = impact_basis(r, p)
        (high if basis else rest).append({**r, "impact": basis})
    if stage == "final":
        return [{**r, "tier": "all"} for r in high + rest]
    k = min(len(rest), min(10, max(3, math.ceil(0.1 * len(rest)))))
    sentinels = sorted(rest, key=lambda r: sha(seed + r["id"]))[:k]
    return [{**r, "tier": "high_impact"} for r in high] + [{**r, "tier": "sentinel"} for r in sentinels]


# ------------------------------------------------------------------------------ collect
def stage_dir(rcs: Path, stage: str) -> Path:
    return rcs / "audits" / "integrity" / stage


def collect(rcs: Path, root: Path, stage: str, draft: Path) -> dict:
    md = draft.read_text(encoding="utf-8")
    seed = sha(md)
    p = load_project(rcs, root, md)
    rows = citation_rows(p)
    selected = select(rows, p, stage, seed)
    chosen = {r["id"] for r in selected}
    bundle = {"tool": "integrity_check", "stage": stage, "draft": str(draft).replace("\\", "/"), "draft_sha256": seed, "sample_seed": seed,
              "paper_type": p["config"].get("paper_type"), "no_experiments": bool(p["config"].get("no_experiments")),
              "declaration_contradicted": declaration_contradicted(p), "modes": deterministic(p),
              "cited_sentences": len(rows), "alignment_rows": selected,
              # judged only when a sentinel fails: then every cited sentence in that section must be judged
              "unselected_rows": [r for r in rows if r["id"] not in chosen]}
    d = stage_dir(rcs, stage)
    d.mkdir(parents=True, exist_ok=True)
    (d / "bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
    return bundle


# ------------------------------------------------------------------------------ gate
def _worst(*statuses: str) -> str:
    return max(statuses, key=STATUSES.index)


def blocks(mode: str, status: str, stage: str, exempt: bool) -> bool:
    if status == "CLEAR":
        return False
    if status == "SUSPECTED":
        return True
    if exempt and mode in EXPERIMENT_MODES:
        return False
    return stage == "final" or mode in EXPERIMENT_MODES


def _decisions(rcs: Path, stage: str, open_issues: str, items: list) -> dict[str, dict]:
    p = stage_dir(rcs, stage) / "decisions.json"
    answers = {q["id"]: q for q in _load(rcs / "checkpoints" / "answers.json", {"questions": []}).get("questions", [])}
    out = {}
    for d in _load(p, {"decisions": []}).get("decisions", []):
        mode, qid = d.get("mode"), d.get("checkpoint")
        a = answers.get(qid)
        if not a or not str(a.get("answered_by", "")).strip():
            items.append(("ERROR", "GI_DECISION_UNANSWERED", f"{mode}: checkpoint {qid} has no answer from a named person"))
        elif len(str(a.get("answer", "")).strip()) < MIN_REASON:
            items.append(("ERROR", "GI_DECISION_NO_REASON", f"{mode}: the answer to {qid} gives no reason (at least {MIN_REASON} characters)"))
        elif qid not in open_issues:
            items.append(("ERROR", "GI_DECISION_NOT_LISTED", f"{mode}: decision {qid} must be listed in open_issues.md"))
        else:
            out[mode] = {"checkpoint": qid, "by": a["answered_by"], "reason": a["answer"]}
    return out


def gate(rcs: Path, root: Path, stage: str, draft: Path) -> dict:
    raw: list[tuple] = []

    def add(level: str, code: str, msg: str) -> None:
        raw.append((level, code, msg))

    md = draft.read_text(encoding="utf-8")
    seed = sha(md)
    p = load_project(rcs, root, md)
    d = stage_dir(rcs, stage)
    det = deterministic(p)
    selected = select(citation_rows(p), p, stage, seed)
    vp = d / "verifier_report.json"
    verifier = _load(vp, None)
    if not (d / "bundle.json").exists() or load_json(d / "bundle.json").get("draft_sha256") != seed:
        add("ERROR", "GI_BUNDLE_STALE", f"no bundle for this draft: run integrity_check.py collect --stage {stage}")
    if verifier is None:
        add("ERROR", "GI_NO_VERIFIER", f"no VERIFIER report at audits/integrity/{stage}/verifier_report.json")
        verifier = {}
    else:
        for e in validate(verifier, load_schema("integrity_report.schema.json"))[:5]:
            add("ERROR", "GI_REPORT_INVALID", e)
        if verifier.get("draft_sha256") != seed:
            add("ERROR", "GI_REPORT_STALE", "the VERIFIER judged a different draft")
    ledger = workflow_guard.load_ledger(rcs)
    if ledger and vp.exists():
        digest = hashlib.sha256(vp.read_bytes()).hexdigest()
        if not any(r.get("role") == "VERIFIER" and r.get("sha256") == digest for r in ledger):
            add("ERROR", "GI_NOT_VERIFIER", "the ledger has no VERIFIER record of this report: nobody checks their own work")
    isolation = verifier.get("isolation")
    if verifier and isolation not in ("isolated", "none"):
        add("ERROR", "GI_ISOLATION", "the VERIFIER report must state isolation: isolated | none")
    issues = vc._open_issues(rcs)
    if isolation == "none" and "isolation" not in issues.lower():
        add("WARN", "GI_ISOLATION_NONE", "isolation: none must be noted in open_issues.md")

    # alignment
    judged = {a.get("row"): a for a in verifier.get("alignment", []) if isinstance(a, dict)}
    all_rows = {r["id"]: r for r in citation_rows(p)}
    required = {r["id"]: r for r in selected}
    counts: dict[str, int] = {}
    forced: dict[str, str] = {}
    for rid, r in list(required.items()):
        a = judged.get(rid)
        if a and r.get("tier") == "sentinel" and a.get("verdict") in ("overstated", "unsupported"):
            for other in all_rows.values():         # a failed sentinel means the error rate is unknown: widen to its section
                if other["section"] == r["section"]:
                    required.setdefault(other["id"], {**other, "tier": "extended"})
    for rid, r in required.items():
        a = judged.get(rid)
        if not a:
            add("ERROR", "GI_ROW_NOT_JUDGED", f"{rid} ({r.get('tier')}, line {r.get('line')}) has no alignment verdict")
            continue
        v = a.get("verdict")
        if v not in VERDICTS:
            add("ERROR", "GI_BAD_VERDICT", f"{rid}: {v!r}")
            continue
        counts[v] = counts.get(v, 0) + 1
        if v in ("overstated", "unsupported"):
            forced["M2"] = "SUSPECTED"
            add("WARN", "GI_ALIGNMENT", f"{rid} is {v}: {a.get('note', '')[:120]}")
        elif v == "understated":
            add("ERROR", "GI_ALIGNMENT_UNDERSTATED", f"{rid}: the sentence weakens the source. Fix the sentence")
        elif v == "not_checkable" and r.get("tier") in ("high_impact", "all") and forced.get("M2") != "SUSPECTED":
            forced["M2"] = "INSUFFICIENT_EVIDENCE"

    # modes
    exempt = bool(p["config"].get("no_experiments"))
    contradiction = declaration_contradicted(p)
    if contradiction:
        exempt = False
        forced["M3"] = forced["M6"] = "SUSPECTED"
        add("WARN", "GI_DECLARATION_CONTRADICTED", f"no_experiments is declared, but the draft reports work as run: {', '.join(contradiction[:6])}")
    modes: dict[str, dict] = {}
    decisions = _decisions(rcs, stage, issues, raw)
    round_no = verifier.get("round") or 1
    any_block = False
    for m in MODES:
        entry = (verifier.get("modes") or {}).get(m)
        if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
            add("ERROR", "GI_MODE_MISSING", f"{m} has no valid status from the VERIFIER")
            entry = {"status": "INSUFFICIENT_EVIDENCE", "evidence": []}
        status, evidence = entry["status"], entry.get("evidence") or []
        if status == "CLEAR" and not evidence:
            add("ERROR", "GI_CLEAR_WITHOUT_EVIDENCE", f"{m}: a CLEAR must cite its evidence")
            status = "INSUFFICIENT_EVIDENCE"
        if det[m]["errors"]:
            if status == "CLEAR":
                add("ERROR", "GI_CONTRADICTS_TOOL", f"{m} was marked CLEAR, but the tool found: {det[m]['errors'][0]['code']} at {det[m]['errors'][0]['where']}")
            status = "SUSPECTED"
        status = _worst(status, forced.get(m, "CLEAR"))
        blocked = blocks(m, status, stage, exempt)
        decision = decisions.get(m)
        if blocked and not decision:
            any_block = True
            add("ERROR", "INTEGRITY_SUSPECTED", f"{m} is {status}: {entry.get('detail') or (det[m]['errors'][0]['detail'] if det[m]['errors'] else '')}"[:200])
        elif blocked:
            add("WARN", "GI_DECISION", f"{m} stays {status}. {decision['by']} decided to proceed ({decision['checkpoint']})")
        elif status != "CLEAR" and m not in issues:
            add("WARN", "GI_NOT_LISTED", f"{m} is {status}: list it in open_issues.md")
        modes[m] = {"status": status, "blocking": blocked and not decision, "evidence": evidence, "tool_errors": len(det[m]["errors"]),
                    "tool_signals": len(det[m]["signals"]), "decision": decision}
    if isinstance(round_no, int) and round_no > MAX_ROUNDS and any_block:
        add("ERROR", "GI_ROUND_CAP", f"round {round_no}: the cap is {MAX_ROUNDS}. A named person must decide (skill/integrity.md section 6)")

    # stage final
    if stage == "final":
        paper = root / "paper" / "paper.md"
        if not paper.exists():
            add("ERROR", "GI_PAPER_MISMATCH", "paper/paper.md does not exist")
        elif strip_tags(md).strip().replace("\r\n", "\n") != paper.read_text(encoding="utf-8").strip().replace("\r\n", "\n"):
            add("ERROR", "GI_PAPER_MISMATCH", "paper/paper.md is not the checked draft with the tags removed")
        pre = stage_dir(rcs, "pre") / "report.json"
        if pre.exists():
            for m, e in (load_json(pre).get("modes") or {}).items():
                if e.get("status") == "SUSPECTED" and modes.get(m, {}).get("status") != "CLEAR" and not decisions.get(m):
                    add("ERROR", "GI_PRE_UNRESOLVED", f"{m} was SUSPECTED at stage pre and is not CLEAR now")
        limit = datetime.now(timezone.utc).date() - timedelta(days=RETRACTION_DAYS)
        cited = {x["source"] for r in all_rows.values() for x in r["sources"]}
        for s in p["sources"]:
            stamp = str((s.get("retraction") or {}).get("checked_at") or "")
            if s["id"] in cited and (not stamp or stamp[:10] < limit.isoformat()):
                add("ERROR", "GI_RETRACTION_STALE", f"{s['id']}: the retraction check is older than {RETRACTION_DAYS} days: run verify_citations.py --online --refresh")

    items = [{"level": lvl, "code": code, "message": msg} for lvl, code, msg in raw]
    try:
        rel = str(draft.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        rel = str(draft).replace("\\", "/")
    return {"tool": "integrity_check", "gate": "GI", "stage": stage, "errors": sum(i["level"] == "ERROR" for i in items),
            "warnings": sum(i["level"] == "WARN" for i in items), "items": items, "modes": modes, "round": round_no, "isolation": isolation,
            "alignment": {"seed": seed, "cited_sentences": len(all_rows), "judged": sum(counts.values()), "verdicts": counts},
            "decisions": decisions, "draft": rel, "draft_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(), "rcs_used": True}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["collect", "gate"])
    ap.add_argument("rcs")
    ap.add_argument("--stage", required=True, choices=["pre", "final"])
    ap.add_argument("--draft", required=True, help="the tagged draft")
    ap.add_argument("--project-root")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    root = Path(a.project_root) if a.project_root else rcs.resolve().parent
    draft = Path(a.draft)
    if not draft.exists() and (root / a.draft).exists():
        draft = root / a.draft
    if not draft.exists():
        print(f"ERROR draft not found: {a.draft}")
        return 1
    if a.command == "collect":
        b = collect(rcs, root, a.stage, draft)
        errors = sum(len(m["errors"]) for m in b["modes"].values())
        signals = sum(len(m["signals"]) for m in b["modes"].values())
        print(f"collected for stage {a.stage}: {errors} tool finding(s), {signals} signal(s), "
              f"{len(b['alignment_rows'])} of {b['cited_sentences']} cited sentence(s) selected. Hand audits/integrity/{a.stage}/bundle.json to the VERIFIER.")
        return 0
    rep = gate(rcs, root, a.stage, draft)
    d = stage_dir(rcs, a.stage)
    d.mkdir(parents=True, exist_ok=True)
    (d / "report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    for i in rep["items"]:
        print(f"{i['level']:5} {i['code']:26} {i['message']}")
    print(f"\nGI ({a.stage}): {'PASSED' if rep['errors'] == 0 else 'FAILED'} ({rep['errors']} error(s), {rep['warnings']} warning(s))")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
