#!/usr/bin/env python3
"""Phase 4: validate the blind reviewer on the 7-variant synthetic benchmark.

Steps (each idempotent; reruns skip completed outputs):
  packets : build blind packets (random IDs) + sealed mapping
  review  : run reviewer families x seeds x packets (parallel)
  grade   : grade reconstructions against the demo gold story (grader never sees the paper)
  analyze : sensitivity / false alarms / reconstruction metrics / family comparison

Usage: python evaluation/harness/reviewer_validation.py packets|review|grade|analyze [--families f1,f2,f3] [--seeds 2]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402
from run_model import run  # noqa: E402

ROOT = RL.ROOT
RV = ROOT / "evaluation" / "reviewer_validation"
PERT = ROOT / "skill" / "tests" / "perturbations"
GOLD = json.loads((ROOT / "skill/examples/demo_project/.rcs/evaluation/gold_story.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((PERT / "EXPECTED.json").read_text(encoding="utf-8"))["variants"]

FAMILIES = {
    "F1": {"provider": "claude", "model": "opus", "label": "Anthropic Claude Opus"},
    "F2": {"provider": "openrouter", "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "label": "NVIDIA Nemotron-3-Ultra-550B (OpenRouter free)"},
    "F2codex": {"provider": "codex", "model": "default", "label": "OpenAI via Codex CLI (UNAVAILABLE after first calls: model 404)"},
    "F3": {"provider": "openrouter", "model": "qwen/qwen3.8-27b:free", "label": "Alibaba Qwen3.8-27B (free)"},
}
GRADER = {"provider": "claude", "model": "sonnet"}

AUDIENCE = ("Intended readers: machine-learning researchers who work on robustness but are not time-series "
            "forecasting specialists.\nThey can be assumed to know: supervised learning, train/test splits, mean "
            "absolute error, standard deviation across random seeds.\nThey cannot be assumed to know: forecasting-"
            "specific normalization practice or the benchmark used.\nBinding reader types for this review: A (domain "
            "expert), B (adjacent-domain researcher), E (verifying reviewer).\nVenue type: workshop paper.")
OBJECTIVE = ("In the authors' words, this paper asks whether normalizing each input window of a forecaster with its "
             "own recent statistics reduces error when the level of the series shifts after training, without "
             "harming accuracy when there is no shift, and how much of any gain depends on continuing to adapt those "
             "statistics. A reader should come away knowing what was tested, what was found, and where the finding stops.")
# Blinding substitution (documented in DECISIONS D-07): remove wording that reveals test-item status.
REPLACEMENTS = {"G_citation_misuse.md": [(
    "[R1]–[R6] Synthetic placeholders. The benchmark's expected-answers file defines what each placeholder actually \"contains\".",
    "[R1]–[R6] Reference list omitted in this manuscript version.")]}


def cmd_packets() -> None:
    mapping_f = RV / "SEALED_MAPPING.json"
    if mapping_f.exists():
        print("packets exist; not rebuilding")
        return
    mapping = {}
    for variant in sorted(EXPECTED):
        pid = RL.new_packet_id()
        paper, log = RL.sanitize_paper((PERT / variant).read_text(encoding="utf-8"), REPLACEMENTS.get(variant))
        d = RV / "packets" / pid
        d.mkdir(parents=True)
        (d / "paper.md").write_text(paper, encoding="utf-8")
        (d / "audience.md").write_text(AUDIENCE, encoding="utf-8")
        (d / "objective.md").write_text(OBJECTIVE, encoding="utf-8")
        mapping[pid] = {"variant": variant, "sanitization": log, "replacements": REPLACEMENTS.get(variant, [])}
    mapping_f.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    print(f"{len(mapping)} packets; mapping sealed in {mapping_f.name}")


def review_job(fam: str, seed: int, pid: str) -> str:
    out = RV / "raw" / f"{fam}_s{seed}_{pid}.txt"
    if out.exists():
        return f"skip {out.name}"
    d = RV / "packets" / pid
    user = RL.reviewer_user_message(pid, (d / "audience.md").read_text(encoding="utf-8"),
                                    (d / "objective.md").read_text(encoding="utf-8"), (d / "paper.md").read_text(encoding="utf-8"))
    f = FAMILIES[fam]
    rec = run(f"RV-{fam}-s{seed}-{pid}", "reviewer", f["provider"], f["model"], RL.REVIEWER_SYSTEM, user, out, timeout=2400)
    return f"{rec['status']} {out.name} {rec.get('model_reported')} {rec.get('error','')[:120] if rec.get('error') else ''}"


def cmd_review(families: list[str], seeds: int, workers: int) -> None:
    pids = sorted(json.loads((RV / "SEALED_MAPPING.json").read_text(encoding="utf-8")))
    jobs = [(f, s, p) for s in range(1, seeds + 1) for f in families for p in pids]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for msg in ex.map(lambda j: review_job(*j), jobs):
            print(msg, flush=True)


def normalize_all() -> dict:
    norm = {}
    for raw in sorted((RV / "raw").glob("*.txt")):
        key = raw.stem
        out = RV / "normalized" / f"{key}.json"
        try:
            obj = RL.extract_json(raw.read_text(encoding="utf-8"))
            n, problems = RL.normalize_review(obj)
            n["validation_problems"] = problems
        except Exception as exc:  # noqa: BLE001
            n = {"parse_error": str(exc)}
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(n, indent=1, ensure_ascii=False), encoding="utf-8")
        norm[key] = n
    return norm


def grade_job(key: str, answers: dict, grader: dict = GRADER, tag: str = "") -> str:
    out = RV / "grading" / f"{key}{tag}.txt"
    if out.exists():
        return f"skip {key}{tag}"
    rid = RL.new_packet_id().replace("pkt", "rec")
    rec = run(f"RVG-{key}{tag}", "grader", grader["provider"], grader["model"], RL.GRADER_SYSTEM,
              RL.grader_user_message(GOLD, answers, rid), out, timeout=1200)
    return f"{rec['status']} grade {key}"


GRADER2 = {"provider": "openrouter", "model": "nvidia/nemotron-3-ultra-550b-a55b:free"}


def cmd_grade(workers: int, second: str | None = None) -> None:
    norm = normalize_all()
    jobs = [(k, v["reconstruction"]["answers"]) for k, v in norm.items() if "reconstruction" in v and v["reconstruction"].get("answers")]
    if second:  # second (cross-family) grader on keys matching the prefix, e.g. "F1_s1"
        jobs = [(k, a, GRADER2, "__nemotron") for k, a in jobs if k.startswith(second)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for msg in ex.map(lambda j: grade_job(*j), jobs):
            print(msg, flush=True)


def cmd_analyze() -> None:
    mapping = json.loads((RV / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
    norm = normalize_all()
    rows = []
    for key, n in norm.items():
        fam, seed, pid = key.split("_", 2)
        variant = mapping[pid]["variant"]
        row = {"key": key, "family": fam, "seed": seed, "variant": variant,
               "parse_ok": "dim_scores" in n, "validation_problems": len(n.get("validation_problems", []))}
        if n.get("dim_scores"):
            row["dims"] = n["dim_scores"]
            row["n_inference_issues"] = len(n["diagnostics"].get("inference_issues", []))
            row["inference_kinds"] = sorted({i.get("kind") for i in n["diagnostics"].get("inference_issues", [])})
        g2 = RV / "grading" / f"{key}__nemotron.txt"
        if g2.exists():
            try:
                row["recon_grader2"], _ = RL.score_grading(RL.extract_json(g2.read_text(encoding="utf-8")), GOLD)
                row["grader2_labels"] = RL.extract_json(g2.read_text(encoding="utf-8")).get("questions")
            except Exception as exc:  # noqa: BLE001
                row["grader2_error"] = str(exc)
        g = RV / "grading" / f"{key}.txt"
        if g.exists():
            try:
                metrics, probs = RL.score_grading(RL.extract_json(g.read_text(encoding="utf-8")), GOLD)
                row["recon"] = metrics
                row["grading_problems"] = probs
                row["grader1_labels"] = RL.extract_json(g.read_text(encoding="utf-8")).get("questions")
            except Exception as exc:  # noqa: BLE001
                row["grading_error"] = str(exc)
        rows.append(row)
    (RV / "scores").mkdir(exist_ok=True)
    (RV / "scores" / "per_review.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")

    # planted-problem detection vs variant A of the same family+seed
    det = []
    for r in rows:
        if r["variant"] == "A_clean.md" or "dims" not in r:
            continue
        base = next((b for b in rows if b["family"] == r["family"] and b["seed"] == r["seed"]
                     and b["variant"] == "A_clean.md" and "dims" in b), None)
        if not base:
            continue
        exp = EXPECTED[r["variant"]].get("reviewer_expected_drop", [])
        hits = [d for d in exp if r["dims"].get(d, 9) <= base["dims"].get(d, -9) - 1]
        det.append({"family": r["family"], "seed": r["seed"], "variant": r["variant"], "expected": exp,
                    "detected": hits, "missed": [d for d in exp if d not in hits],
                    "sensitivity": round(len(hits) / len(exp), 3) if exp else None,
                    "min_dim_variant": min(r["dims"].values()), "min_dim_A": min(base["dims"].values()),
                    "any_blocking_flag": min(r["dims"].values()) <= 2})
    fa = []
    for r in rows:
        if r["variant"] == "A_clean.md" and "dims" in r:
            low = [d for d, s in r["dims"].items() if s <= 2]
            fa.append({"family": r["family"], "seed": r["seed"], "false_alarm_dims": low,
                       "false_alarm_rate": round(len(low) / 20, 3), "n_inference_issues": r["n_inference_issues"]})
    summary = {"detection": det, "false_alarms_on_A": fa}
    for fam in sorted({r["family"] for r in rows}):
        s = [d["sensitivity"] for d in det if d["family"] == fam and d["sensitivity"] is not None]
        f = [x["false_alarm_rate"] for x in fa if x["family"] == fam]
        blocking = [d["any_blocking_flag"] for d in det if d["family"] == fam]
        summary[fam] = {"mean_dimension_sensitivity": round(statistics.mean(s), 3) if s else None,
                        "variant_level_flag_rate(any dim<=2)": round(sum(blocking) / len(blocking), 3) if blocking else None,
                        "mean_false_alarm_rate_on_A": round(statistics.mean(f), 3) if f else None,
                        "n_reviews": sum(1 for r in rows if r["family"] == fam)}
    (RV / "scores" / "detection_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k.startswith("F")}, indent=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["packets", "review", "grade", "analyze"])
    ap.add_argument("--families", default="F1,F2")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--second-grader-prefix", default=None)
    a = ap.parse_args()
    if a.step == "packets":
        cmd_packets()
    elif a.step == "review":
        cmd_review(a.families.split(","), a.seeds, a.workers)
    elif a.step == "grade":
        cmd_grade(a.workers, a.second_grader_prefix)
    else:
        cmd_analyze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
