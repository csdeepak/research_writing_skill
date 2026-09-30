#!/usr/bin/env python3
"""Phase 5/6 blind comparison: reviewer families x papers, graded against the FROZEN gold (v1).

  packets <P> <cond...>   build blind packets (random IDs; sealed mapping) for the given conditions
  review  [--families F1,F2]   run all un-reviewed packets
  grade   [--grader claude:sonnet]  grade reconstructions vs frozen gold (grader sees gold + answers only)
  analyze                  per-paper metrics + paired differences

Conditions and their paper locations:
  plain            evaluation/plain_agent/<P>/plain/paper.md
  skill            evaluation/skill_agent/<P>/skill/paper.md
  skillpkg-cheap   evaluation/evidence_agent/<P>/skillpkg-cheap/paper.md
  skillpkg-strong  evaluation/evidence_agent/<P>/skillpkg-strong/paper.md
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402
from reviewer_validation import FAMILIES  # noqa: E402
from run_model import run  # noqa: E402

EV = RL.ROOT / "evaluation"
CMP = EV / "results" / "comparison"
LOC = {"plain": "plain_agent/{P}/plain", "skill": "skill_agent/{P}/skill",
       "skillpkg-cheap": "evidence_agent/{P}/skillpkg-cheap", "skillpkg-strong": "evidence_agent/{P}/skillpkg-strong",
       "skillv010sub": "skill_agent/{P}/skillv010sub", "skillv020sub": "skill_agent/{P}/skillv020sub",
       "skillv010ab3": "skill_agent/{P}/skillv010ab3", "skillv030ab3": "skill_agent/{P}/skillv030ab3"}   # D-29
AUDIENCE = ("Intended readers: machine-learning researchers from other subfields (adjacent researchers). They know "
            "general ML, deep learning, standard evaluation practice and statistics, but not this project's "
            "subfield-specific terminology, datasets or prior work.\nBinding reader types for this review: A (domain "
            "expert), B (adjacent-domain researcher), E (verifying reviewer).\nVenue type: journal-length research article.")
OBJECTIVE = "The authors intend this paper to present their research project to adjacent machine-learning researchers."
PROVENANCE_RE = re.compile(r"(research communication engine|\.rcs|claim[- ]evidence map|story graph|paper spine|"
                           r"open_issues|AI[- ]use (statement|disclosure)|(this|the) (manuscript|paper) was (drafted|written|"
                           r"prepared) (with|using)|language model was used (to|for)|generated (with|by) (an? )?(ai|llm|language model))", re.I)
MARKERS = re.compile(r"\[(MISSING RESULT|MISSING|CITATION NEEDED|ASK AUTHOR)[^\]]*\]")


def gold(project: str) -> dict:
    return json.loads((EV / "ground_truth" / project / "gold_story.v1.json").read_text(encoding="utf-8"))


def clean_paper(md: str) -> tuple[str, dict]:
    log = {"markers_removed": len(MARKERS.findall(md))}
    md = MARKERS.sub("", md)
    kept, removed = [], []
    for line in md.splitlines():
        if PROVENANCE_RE.search(line):
            removed.append(line.strip()[:200])
            continue
        kept.append(line)
    log["provenance_lines_removed"] = removed
    paper, slog = RL.sanitize_paper("\n".join(kept))
    log["sanitization"] = slog
    body = re.split(r"(?im)^#+\s*references\b", paper)[0]
    log["words_main"] = len(body.split())
    log["words_total"] = len(paper.split())
    return paper, log


def cmd_packets(project: str, conds: list[str]) -> None:
    mf = CMP / "SEALED_MAPPING.json"
    mapping = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    have = {(v["project"], v["condition"]) for v in mapping.values()}
    for c in conds:
        if (project, c) in have:
            print(f"exists {project}/{c}")
            continue
        src = EV / LOC[c].format(P=project) / "paper.md"
        if not src.exists():
            print(f"MISSING paper {src}")
            continue
        paper, log = clean_paper(src.read_text(encoding="utf-8"))
        pid = RL.new_packet_id()
        d = CMP / "packets" / pid
        d.mkdir(parents=True)
        (d / "paper.md").write_text(paper, encoding="utf-8")
        (d / "audience.md").write_text(AUDIENCE, encoding="utf-8")
        (d / "objective.md").write_text(OBJECTIVE, encoding="utf-8")
        mapping[pid] = {"project": project, "condition": c, "source": str(src.relative_to(RL.ROOT)), "clean_log": log}
        print(f"{pid} <- {project}/{c} ({log['words_main']} words; markers {log['markers_removed']}; "
              f"provenance lines {len(log['provenance_lines_removed'])})")
    mf.parent.mkdir(parents=True, exist_ok=True)
    mf.write_text(json.dumps(mapping, indent=1), encoding="utf-8")


def review_one(fam: str, pid: str) -> str:
    out = CMP / "raw" / f"{fam}_{pid}.txt"
    if out.exists():
        return f"skip {out.name}"
    d = CMP / "packets" / pid
    user = RL.reviewer_user_message(pid, (d / "audience.md").read_text(encoding="utf-8"),
                                    (d / "objective.md").read_text(encoding="utf-8"), (d / "paper.md").read_text(encoding="utf-8"))
    f = FAMILIES[fam]
    rec = run(f"CMP-{fam}-{pid}", "reviewer", f["provider"], f["model"], RL.REVIEWER_SYSTEM, user, out, timeout=3000)
    return f"{rec['status']} {out.name} {rec.get('error', '')[:100] if rec.get('error') else ''}"


def cmd_review(families: list[str], workers: int) -> None:
    pids = sorted(json.loads((CMP / "SEALED_MAPPING.json").read_text(encoding="utf-8")))
    jobs = [(f, p) for f in families for p in pids]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for m in ex.map(lambda j: review_one(*j), jobs):
            print(m, flush=True)


def grade_one(key: str, project: str, answers: dict, grader: str) -> str:
    prov, model = grader.split(":")
    tag = "" if grader == "claude:sonnet" else f"__{prov}"
    out = CMP / "grading" / f"{key}{tag}.txt"
    if out.exists():
        return f"skip {out.name}"
    rid = RL.new_packet_id().replace("pkt", "rec")
    rec = run(f"CMPG-{key}{tag}", "grader", prov, model, RL.GRADER_SYSTEM,
              RL.grader_user_message(gold(project), answers, rid), out, timeout=1500)
    return f"{rec['status']} {out.name}"


def load_norm(key: str) -> dict | None:
    raw = CMP / "raw" / f"{key}.txt"
    try:
        n, probs = RL.normalize_review(RL.extract_json(raw.read_text(encoding="utf-8")))
        n["validation_problems"] = probs
        return n
    except Exception as exc:  # noqa: BLE001
        return {"parse_error": str(exc)}


def cmd_grade(grader: str, workers: int, only_family: str | None) -> None:
    mapping = json.loads((CMP / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
    jobs = []
    for raw in sorted((CMP / "raw").glob("*.txt")):
        fam, pid = raw.stem.split("_", 1)
        if only_family and fam != only_family:
            continue
        n = load_norm(raw.stem)
        (CMP / "normalized").mkdir(exist_ok=True)
        (CMP / "normalized" / f"{raw.stem}.json").write_text(json.dumps(n, indent=1, ensure_ascii=False), encoding="utf-8")
        if n and "reconstruction" in n and n["reconstruction"].get("answers"):
            jobs.append((raw.stem, mapping[pid]["project"], n["reconstruction"]["answers"], grader))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for m in ex.map(lambda j: grade_one(*j), jobs):
            print(m, flush=True)


# (a, b) pairs reported as b - a. D-29 adds the tier-3 A/B and its noise contrast (v0.1.0 run-to-run).
CONTRASTS = (("plain", "skill"), ("skillpkg-cheap", "skillpkg-strong"), ("skillv010sub", "skillv020sub"),
             ("skillv010ab3", "skillv030ab3"), ("skillv010sub", "skillv010ab3"))


def cmd_analyze() -> None:
    mapping = json.loads((CMP / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
    rows = []
    for raw in sorted((CMP / "raw").glob("*.txt")):
        fam, pid = raw.stem.split("_", 1)
        m = mapping[pid]
        n = load_norm(raw.stem) or {}
        if n.get("parse_error"):
            print(f"PARSE ERROR {raw.stem}: {n['parse_error'][:120]}")
        row = {"family": fam, "pid": pid, "project": m["project"], "condition": m["condition"],
               "words_main": m["clean_log"]["words_main"], "markers_removed": m["clean_log"]["markers_removed"]}
        if n.get("dim_scores"):
            row["dims"] = n["dim_scores"]
            row["dim_mean"] = round(statistics.mean(n["dim_scores"].values()), 3)
            row["n_inference_issues"] = len(n["diagnostics"].get("inference_issues", []))
        for gfile in sorted((CMP / "grading").glob(f"{raw.stem}*.txt")):
            gtag = "sonnet" if gfile.stem == raw.stem else gfile.stem.split("__")[-1]
            try:
                met, probs = RL.score_grading(RL.extract_json(gfile.read_text(encoding="utf-8")), gold(m["project"]))
                row[f"recon_{gtag}"] = met
                row[f"grading_problems_{gtag}"] = len(probs)
            except Exception as exc:  # noqa: BLE001
                row[f"grading_error_{gtag}"] = str(exc)
        rows.append(row)
    (CMP / "scores").mkdir(exist_ok=True)
    (CMP / "scores" / "per_review.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    # paired differences per project x family, primary grader
    pairs = []
    for fam in sorted({r["family"] for r in rows}):
        for proj in sorted({r["project"] for r in rows}):
            by = {r["condition"]: r for r in rows if r["family"] == fam and r["project"] == proj and "recon_sonnet" in r}
            for a, b in CONTRASTS:
                if a in by and b in by:
                    ra, rb = by[a]["recon_sonnet"], by[b]["recon_sonnet"]
                    pairs.append({"family": fam, "project": proj, "contrast": f"{b} - {a}",
                                  **{f"d_{k}": round(rb[k] - ra[k], 3) for k in ("MMF", "RR", "CoreRR", "DR", "IR")},
                                  f"{a}_MMF": ra["MMF"], f"{b}_MMF": rb["MMF"], f"{a}_DR": ra["DR"], f"{b}_DR": rb["DR"],
                                  "d_dim_mean": round(by[b].get("dim_mean", 0) - by[a].get("dim_mean", 0), 3),
                                  f"{a}_words": by[a]["words_main"], f"{b}_words": by[b]["words_main"]})
    (CMP / "scores" / "paired.json").write_text(json.dumps(pairs, indent=1), encoding="utf-8")
    for p in pairs:
        print(json.dumps(p))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--families", default="F1,F2")
    ap.add_argument("--grader", default="claude:sonnet")
    ap.add_argument("--only-family", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.step == "packets":
        cmd_packets(a.args[0], a.args[1:])
    elif a.step == "review":
        cmd_review(a.families.split(","), a.workers)
    elif a.step == "grade":
        cmd_grade(a.grader, a.workers, a.only_family)
    elif a.step == "analyze":
        cmd_analyze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
