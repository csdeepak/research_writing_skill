#!/usr/bin/env python3
"""Supplementary analysis (D-23): are 'unsupported_belief' intrusions actually unsupported by the SOURCE?

The frozen grader (evaluator v0.2) tags an intrusion `unsupported_belief` when the reader states a claim about
the research that the GOLD story does not contain. The gold story is a curated subset (36-40 nuggets), not an
exhaustive record of the frozen source snapshot, so a true, source-stated detail the gold omitted is counted as
an unsupported belief. This script checks every such intrusion against the frozen source snapshot, blind to
condition, and reports IR_src / MMF_src alongside the frozen primary metrics. It does NOT replace them.

  make       build one blinded verification task per project (subagent task folders, see subagent_tasks.py)
  make-new TAG  incremental: only gradings not yet sealed (D-29); tasks IV-<project>-TAG
  analyze    after `subagent_tasks.py collect`: recompute IR_src, MMF_src per review and per contrast

Blinding: intrusions from every condition/phase of a project are pooled, shuffled and given random ids; the
verifier sees only the source snapshot and the statements. The id -> (review, condition) map is sealed in
intrusion_check/SEALED_INTRUSIONS.json.
"""
from __future__ import annotations

import json
import random
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402
import subagent_tasks as ST  # noqa: E402
from compare import CONTRASTS  # noqa: E402

EV = RL.ROOT / "evaluation"
CMP = EV / "results" / "comparison"
OUT = CMP / "intrusion_check"
SEALED = OUT / "SEALED_INTRUSIONS.json"
LABELS = ("SUPPORTED", "NOT_FOUND", "CONTRADICTED")

SYSTEM = """You are a source-fidelity checker. You receive (1) the complete frozen source material for one research
project and (2) a list of statements that readers made about that project. For EACH statement decide:

- SUPPORTED: every factual element of the statement (entities, numbers, relations, scope) is explicitly stated in
  the source, or follows by trivial arithmetic from numbers stated in the source. A faithful paraphrase is
  SUPPORTED. Numbers must match the source exactly (allowing only rounding the source itself uses).
- CONTRADICTED: the source states something incompatible (a different number, the opposite relation, a
  different scope).
- NOT_FOUND: anything else -- the source does not state it, it is a reader's inference or generalization beyond
  the source, a speculation about how the paper was written, or it is only partly supported (if ANY element is
  unsupported, the whole statement is NOT_FOUND, not SUPPORTED).

Judge only against the source text below. Do not use outside knowledge. When unsure, choose NOT_FOUND.
For SUPPORTED and CONTRADICTED give a verbatim quote of at most 30 words from the source as evidence."""

FMT = ('Reply with ONE JSON object only (no code fences): {"verdicts": {"<statement id>": {"label": '
       '"SUPPORTED|NOT_FOUND|CONTRADICTED", "quote": "<verbatim source quote, or empty for NOT_FOUND>"}, ...}} '
       'covering EVERY statement id exactly once.')


def source_text(project: str) -> str:
    snap = EV / "external_projects" / project / "snapshot"
    # errors="replace": some pdftotext snapshots (e.g. WHISPER) contain stray non-UTF-8 bytes
    parts = [f"## FILE paper.txt\n{(snap / 'paper.txt').read_text(encoding='utf-8', errors='replace')}"]
    for r in sorted(snap.glob("README__*.md")):
        parts.append(f"## FILE {r.name}\n{r.read_text(encoding='utf-8', errors='replace')}")
    return "\n\n".join(parts)


def primary_gradings() -> list[tuple[str, str, Path]]:
    """(review_key, pid, grading_path) for primary-grader (Sonnet) gradings of F1 reviews."""
    out = []
    for g in sorted((CMP / "grading").glob("F1_pkt-*.txt")):
        if "__" in g.stem:          # secondary graders carry a __<provider> suffix
            continue
        out.append((g.stem, g.stem.split("_", 1)[1], g))
    return out


def cmd_make() -> None:
    mapping = json.loads((CMP / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
    by_project: dict[str, list[dict]] = {}
    sealed: dict[str, dict] = {}
    for key, pid, g in primary_gradings():
        m = mapping.get(pid)
        if not m:
            continue
        try:
            grading = RL.extract_json(g.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            print(f"skip unparsable {g.name}")
            continue
        for i, it in enumerate(grading.get("intrusions", [])):
            if it.get("tag") != "unsupported_belief":
                continue
            sid = f"I-{secrets.token_hex(3)}"
            sealed[sid] = {"review": key, "pid": pid, "project": m["project"], "condition": m["condition"],
                           "index": i, "question": it.get("question"), "text": it.get("text", "")}
            by_project.setdefault(m["project"], []).append({"id": sid, "statement": it.get("text", "")})
    OUT.mkdir(parents=True, exist_ok=True)
    SEALED.write_text(json.dumps(sealed, indent=1, ensure_ascii=False), encoding="utf-8")
    ix = ST.load_index()
    for project, items in sorted(by_project.items()):
        random.shuffle(items)
        user = (f"# SOURCE MATERIAL (frozen snapshot)\n\n{source_text(project)}\n\n# STATEMENTS TO CHECK\n"
                + json.dumps(items, indent=1, ensure_ascii=False) + "\n\n" + FMT)
        ST.add_task(ix, f"IV-{project}", "intrusion_verifier", "sonnet", SYSTEM, user, OUT / f"{project}.txt")
        print(f"{project}: {len(items)} statements")
    ST.save_index(ix)
    for tid, t in ix.items():
        if not t["collected"] and t["exp_id"].startswith("IV-"):
            print(tid, t["model"], t["exp_id"])


def cmd_make_new(tag: str) -> None:
    """Incremental (D-29): statements from gradings whose review is not yet in the sealed map, pooled per project
    across conditions and shuffled; one task per project written to <project>__<tag>.txt; the sealed map is merged."""
    mapping = json.loads((CMP / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
    sealed = json.loads(SEALED.read_text(encoding="utf-8")) if SEALED.exists() else {}
    done_reviews = {s["review"] for s in sealed.values()}
    verified_before = {p.stem for p in OUT.glob("*.txt")}
    by_project: dict[str, list[dict]] = {}
    new_reviews = []
    for key, pid, g in primary_gradings():
        m = mapping.get(pid)
        if not m or key in done_reviews:
            continue
        grading = RL.extract_json(g.read_text(encoding="utf-8"))
        new_reviews.append(key)
        for i, it in enumerate(grading.get("intrusions", [])):
            if it.get("tag") != "unsupported_belief":
                continue
            sid = f"I-{secrets.token_hex(3)}"
            sealed[sid] = {"review": key, "pid": pid, "project": m["project"], "condition": m["condition"],
                           "index": i, "question": it.get("question"), "text": it.get("text", "")}
            by_project.setdefault(m["project"], []).append({"id": sid, "statement": it.get("text", "")})
    SEALED.write_text(json.dumps(sealed, indent=1, ensure_ascii=False), encoding="utf-8")
    ix = ST.load_index()
    for project, items in sorted(by_project.items()):
        assert f"{project}__{tag}" not in verified_before, f"{project}__{tag} already verified"
        random.shuffle(items)
        user = (f"# SOURCE MATERIAL (frozen snapshot)\n\n{source_text(project)}\n\n# STATEMENTS TO CHECK\n"
                + json.dumps(items, indent=1, ensure_ascii=False) + "\n\n" + FMT)
        ST.add_task(ix, f"IV-{project}-{tag}", "intrusion_verifier", "sonnet", SYSTEM, user, OUT / f"{project}__{tag}.txt")
        print(f"{project}: {len(items)} statements")
    ST.save_index(ix)
    print(f"new reviews sealed: {len(new_reviews)}")
    for tid, t in ix.items():
        if not t["collected"] and t["exp_id"].startswith("IV-"):
            print(tid, t["model"], t["exp_id"])


def load_verdicts() -> dict[str, dict]:
    v: dict[str, dict] = {}
    for f in OUT.glob("*.txt"):
        try:
            v.update(RL.extract_json(f.read_text(encoding="utf-8")).get("verdicts", {}))
        except Exception as exc:  # noqa: BLE001
            print(f"PARSE ERROR {f.name}: {exc}")
    return v


def cmd_analyze() -> None:
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    verdicts = load_verdicts()
    missing = [s for s in sealed if s not in verdicts]
    if missing:
        print(f"WARNING: {len(missing)} statements have no verdict; they are counted as NOT_FOUND (conservative).")
    rows = json.loads((CMP / "scores" / "per_review.json").read_text(encoding="utf-8"))
    counts: dict[str, dict[str, int]] = {}
    for sid, s in sealed.items():
        lab = verdicts.get(sid, {}).get("label", "NOT_FOUND")
        lab = lab if lab in LABELS else "NOT_FOUND"
        counts.setdefault(s["review"], {k: 0 for k in LABELS})[lab] += 1
    out_rows = []
    for r in rows:
        key = f"{r['family']}_{r['pid']}"
        rec = r.get("recon_sonnet")
        if r["family"] != "F1" or not rec:
            continue
        c = counts.get(key, {k: 0 for k in LABELS})
        n = rec["nuggets"]
        ir_src = (c["NOT_FOUND"] + c["CONTRADICTED"]) / n
        mmf_src = max(-1.0, min(1.0, rec["RR"] - rec["DR"] - 0.5 * ir_src))
        out_rows.append({"pid": r["pid"], "project": r["project"], "condition": r["condition"],
                         "RR": rec["RR"], "DR": rec["DR"], "IR": rec["IR"], "MMF": rec["MMF"],
                         "intrusions_supported": c["SUPPORTED"], "intrusions_not_found": c["NOT_FOUND"],
                         "intrusions_contradicted": c["CONTRADICTED"],
                         "IR_src": round(ir_src, 3), "MMF_src": round(mmf_src, 3)})
    pairs = []
    for proj in sorted({r["project"] for r in out_rows}):
        by = {r["condition"]: r for r in out_rows if r["project"] == proj}
        for a, b in CONTRASTS:
            if a in by and b in by:
                pairs.append({"project": proj, "contrast": f"{b} - {a}",
                              "d_MMF": round(by[b]["MMF"] - by[a]["MMF"], 3),
                              "d_MMF_src": round(by[b]["MMF_src"] - by[a]["MMF_src"], 3),
                              "d_IR": round(by[b]["IR"] - by[a]["IR"], 3),
                              "d_IR_src": round(by[b]["IR_src"] - by[a]["IR_src"], 3),
                              f"{a}_MMF_src": by[a]["MMF_src"], f"{b}_MMF_src": by[b]["MMF_src"]})
    res = {"note": "Supplementary sensitivity analysis (D-23). Primary metrics (MMF/IR) are the frozen evaluator "
                   "v0.2; IR_src counts only intrusions the blinded verifier could NOT find in the source.",
           "statements": len(sealed), "verdicts": len(verdicts),
           "label_totals": {k: sum(c[k] for c in counts.values()) for k in LABELS},
           "per_review": out_rows, "pairs": pairs}
    (CMP / "scores" / "intrusion_sensitivity.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res["label_totals"]))
    for p in pairs:
        print(f"{p['project']:12s} {p['contrast']:34s} dMMF {p['d_MMF']:+.3f}  dMMF_src {p['d_MMF_src']:+.3f}  "
              f"dIR {p['d_IR']:+.3f}  dIR_src {p['d_IR_src']:+.3f}")


if __name__ == "__main__":
    if sys.argv[1] == "make-new":
        cmd_make_new(sys.argv[2])
    else:
        {"make": cmd_make, "analyze": cmd_analyze}[sys.argv[1]]()
