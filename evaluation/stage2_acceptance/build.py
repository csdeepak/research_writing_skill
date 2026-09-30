#!/usr/bin/env python3
"""Build the vNext Stage 2 acceptance projects from REAL data (spec 12: ">= 2 real projects").

  ASMOS        the user's own project (C:/Users/csdee/PESU/CDSAML/ASMOS), raw experiment results.
               Only aggregate numbers (system x metric -> mean, 95% CI, n) are copied; per-query questions
               and answers are NOT copied. Original files are recorded by path + sha256 in PROVENANCE.md.
               The ASMOS repository is only read, never modified.
  MLPERF_TINY  published paper (frozen snapshot, evaluation/external_projects/MLPERF_TINY/snapshot):
               Table 1 reference-model sizes, re-typed into CSV; every value must occur in the paper text
               (visual gate V1 checks this via data.source_text).

Usage: python evaluation/stage2_acceptance/build.py [--asmos DIR]
Then:  python <candidate>/tools/visuals.py render <project>/.rcs
       python <candidate>/tools/validate_visuals.py <project>/.rcs --draft <project>/paper.md
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def sha(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def item(i, kind, summary, path, value=None, anchor=None, **kw):
    d = {"id": i, "kind": kind, "summary": summary, "locator": {"path": path}, "strength": "hard", "status": "ok"}
    if anchor:
        d["locator"]["anchor"] = anchor
    if value is not None:
        d["value"] = value
    d.update(kw)
    return d


def claim(i, stmt, ctype, ev, **kw):
    d = {"id": i, "statement": stmt, "claim_type": ctype, "evidence": ev, "confidence": "moderate",
         "author_confirmation": "confirmed", "basis": "project_file", "status": "VERIFIED", "licenses": []}
    d.update(kw)
    return d


# ======================================================================================== ASMOS
def build_asmos(src: Path) -> None:
    root = HERE / "ASMOS"
    if root.exists():
        shutil.rmtree(root)
    res = src / "results"
    files = {"A No-Memory": "no_memory.json", "B RAG": "rag.json", "C ASMOS": "asmos.json", "D ASMOS+RAG": "system_d.json"}
    records, prov = [], []
    for system, fname in files.items():
        d = json.loads((res / fname).read_text(encoding="utf-8"))
        assert d["system"].endswith(system.split(" ", 1)[1]), (d["system"], system)
        agg = d["aggregate"]
        for metric in ("exact_match", "token_f1"):
            m = agg[metric]
            records.append({"system": system, "metric": metric, "mean": m["mean"], "ci_low": m["ci95"][0],
                            "ci_high": m["ci95"][1], "n": agg["n"], "model": d.get("model")})
        prov.append(f"| `results/{fname}` | `aggregate` block only | {sha(res / fname)} |")
    write(root / "data" / "aggregates.json", {"records": records})
    shutil.copy2(res / "summary.csv", root / "data" / "summary.csv")
    shutil.copy2(res / "statistics.md", root / "data" / "statistics.md")
    prov += [f"| `results/summary.csv` | copied verbatim (aggregates only) | {sha(res / 'summary.csv')} |",
             f"| `results/statistics.md` | copied verbatim | {sha(res / 'statistics.md')} |"]
    write(root / "data" / "PROVENANCE.md",
          "# Provenance\n\nSource repository: `C:/Users/csdee/PESU/CDSAML/ASMOS` (read-only; not modified).\n"
          "Run: four-system keyed comparison, openai/gpt-4o-mini, n = 24 RULER QA questions (per ASMOS `results/summary.md`).\n"
          "`System D` = `system_d.json` (canonical per ASMOS `results/summary.md`; `asmos_rag.json` is a pointer to it).\n\n"
          "| Original file | What was taken | SHA-256 of original |\n|---|---|---|\n" + "\n".join(prov) +
          "\n\nPer-query questions/answers were deliberately NOT copied.\n")
    summ = list(csv.DictReader(io.StringIO((root / "data" / "summary.csv").read_text(encoding="utf-8"))))
    tf1 = {r["system"]: r for r in records if r["metric"] == "token_f1"}
    em = {r["system"]: r for r in records if r["metric"] == "exact_match"}
    ev = [
        item("E001", "result", "Token-F1 per system: mean, 95% CI, n=24", "data/aggregates.json", quantity="token_f1_by_system",
             value={k: [v["mean"], v["ci_low"], v["ci_high"]] for k, v in tf1.items()}, conditions={"n": 24, "benchmark": "RULER QA"}),
        item("E002", "result", "Exact match per system: mean, 95% CI, n=24", "data/aggregates.json", quantity="exact_match_by_system",
             value={k: [v["mean"], v["ci_low"], v["ci_high"]] for k, v in em.items()}, conditions={"n": 24, "benchmark": "RULER QA"}),
        item("E003", "result", "Paired bootstrap (10k) and Wilcoxon on token-F1, RAG minus ASMOS", "data/statistics.md",
             anchor="rag − asmos", quantity="token_f1_diff_rag_minus_asmos",
             value={"metric": "token_f1_difference", "value": 0.3358, "test": "paired bootstrap (10k) + Wilcoxon signed-rank",
                    "ci": [0.1494, 0.5228], "W": 100}),
        item("E004", "result", "Mean latency (s) per system, n=24", "data/summary.csv", quantity="latency_by_system",
             value={r["system"]: float(r["latency_s"]) for r in summ}),
    ]
    cl = [
        claim("C001", "On 24 RULER QA questions, RAG reached the highest token-F1 (0.751, 95% CI 0.612-0.891) and ASMOS-memory "
                      "the lowest (0.416, 95% CI 0.283-0.548).", "measured", ["E001"]),
        claim("C002", "ASMOS+RAG answered 62.5% of questions exactly yet had token-F1 0.433, second-lowest of the four systems: "
                      "exact match and token-F1 rank the systems differently.", "measured", ["E001", "E002"]),
        claim("C003", "Mean latency rose from 1.50 s (no memory) to 1.99 s (ASMOS+RAG).", "measured", ["E004"]),
        claim("C004", "RAG exceeded ASMOS-memory by +0.336 token-F1 (paired bootstrap 95% CI +0.149 to +0.523).", "derived", ["E003"],
              licenses=[{"type": "significance_test", "evidence": ["E003"]}]),
    ]
    write(root / ".rcs" / "evidence" / "research_evidence.json", {"project_root": ".", "generated_at": "2026-09-29", "items": ev})
    write(root / ".rcs" / "claims" / "claim_evidence_map.json", {"claims": cl, "limitations": [], "negative_result_decisions": []})
    common_req = ["n", "uncertainty", "metric"]
    reg = {"visuals": [
        {"id": "V001", "number": 1, "rq": "RQ1", "tier": "main", "kind": "COMPARATIVE", "representation": "dot_ci",
         "reader_question": "Which memory design answers questions most accurately, and how certain is the ranking?",
         "claim_ids": ["C001"], "evidence_ids": ["E001"], "title": "Token-F1 by system (mean, 95% CI)",
         "value_label": "token-F1", "domain": [0, 1], "x_labels": {"A No-Memory": "No memory", "B RAG": "RAG", "C ASMOS": "ASMOS (memory only)", "D ASMOS+RAG": "ASMOS + RAG"}, "figure_path": "figures/V001_token_f1.svg",
         "data": {"file": "data/aggregates.json", "scope": {"metric": "token_f1"}, "x": "system", "y": "mean",
                  "err_low": "ci_low", "err_high": "ci_high"},
         "caption": "RAG has the highest token-F1 (0.751) and ASMOS-memory alone the lowest (0.416); RAG's 95% confidence "
                    "interval lies above the means of the other three systems. Dots are means over n = 24 RULER QA questions, "
                    "whiskers are 95% confidence intervals, all systems use gpt-4o-mini.",
         "caption_requirements": common_req, "forbidden_implications": ["significance_test", "causal_design"],
         "alt_text": "Dot plot with confidence whiskers of token-F1 for four systems; RAG is highest at 0.75 and ASMOS-memory lowest at 0.42."},
        {"id": "V002", "number": 2, "rq": "RQ1", "tier": "main", "kind": "ANALYTICAL", "representation": "dot_ci",
         "reader_question": "Do exact match and token-F1 agree on which system is best?",
         "claim_ids": ["C002"], "evidence_ids": ["E001", "E002"], "title": "Exact match vs token-F1 by system (mean, 95% CI)",
         "value_label": "score", "domain": [0, 1], "x_labels": {"A No-Memory": "No memory", "B RAG": "RAG", "C ASMOS": "ASMOS (memory only)", "D ASMOS+RAG": "ASMOS + RAG"}, "series_labels": {"exact_match": "exact match", "token_f1": "token-F1"}, "figure_path": "figures/V002_metrics.svg",
         "data": {"file": "data/aggregates.json", "scope": {"metric": ["exact_match", "token_f1"]}, "x": "system", "y": "mean",
                  "err_low": "ci_low", "err_high": "ci_high", "series": "metric"},
         "caption": "ASMOS+RAG answers 62.5% of questions exactly yet has the second-lowest token-F1 (0.433), so the two metrics "
                    "rank the systems differently. Means over n = 24 questions with 95% confidence intervals for exact match "
                    "and token-F1.",
         "caption_requirements": common_req,
         "alt_text": "Paired dot plot of exact match and token-F1 for four systems; ASMOS+RAG is high on exact match but low on token-F1."},
        {"id": "V003", "number": 3, "rq": "RQ2", "tier": "main", "kind": "COMPARATIVE", "representation": "bar_h",
         "reader_question": "What does adding memory cost in latency?", "claim_ids": ["C003"], "evidence_ids": ["E004"],
         "title": "Mean latency per question", "value_label": "latency", "units": "s", "x_labels": {"A No-Memory": "No memory", "B RAG": "RAG", "C ASMOS": "ASMOS (memory only)", "D ASMOS+RAG": "ASMOS + RAG"}, "figure_path": "figures/V003_latency.svg",
         "data": {"file": "data/summary.csv", "scope": {}, "x": "system", "y": "latency_s",
                  "uncertainty_note": "summary.csv records only mean latency; no interval is available"},
         "caption": "Mean latency rises from 1.50 s without memory to 1.99 s for ASMOS+RAG. Mean seconds per question over "
                    "n = 24 questions; the source records no latency interval.",
         "caption_requirements": ["n", "units"],
         "alt_text": "Horizontal bar chart of mean latency in seconds for four systems, from 1.50 s for No-Memory to 1.99 s for ASMOS+RAG."},
        {"id": "T001", "number": 1, "rq": "RQ1", "tier": "supplementary", "kind": "ANALYTICAL", "representation": "table",
         "reader_question": "What are all measured values per system?", "claim_ids": ["C001", "C003"], "evidence_ids": ["E001", "E004"],
         "data": {"file": "data/summary.csv", "scope": {}, "x": "system", "y": "token_f1"}},
    ]}
    write(root / ".rcs" / "plan" / "visual_registry.json", reg)
    write(root / ".rcs" / "state.json", {"step": 15, "guardrail": "v0.3", "gates": {}})
    write(root / "paper.md",
          "# ASMOS: results excerpt (Stage 2 acceptance)\n\n## Results\n\n"
          "Figure 1 compares answer quality. RAG reached the highest token-F1, 0.751 (95% CI 0.612 to 0.891), and "
          "ASMOS-memory the lowest, 0.416 (95% CI 0.283 to 0.548) {C001}. The paired bootstrap puts RAG's advantage over "
          "ASMOS-memory at +0.336 token-F1 (95% CI +0.149 to +0.523) {C004}.\n\n"
          "The two quality metrics disagree, as Figure 2 shows: ASMOS+RAG answered 62.5% of questions exactly but had a "
          "token-F1 of only 0.433 {C002}.\n\n"
          "Figure 3 shows the latency cost. Mean latency rose from 1.50 s without memory to 1.99 s for ASMOS+RAG {C003}.\n")


# ================================================================================== MLPERF TINY
def build_mlperf() -> None:
    root = HERE / "MLPERF_TINY"
    if root.exists():
        shutil.rmtree(root)
    snap = REPO / "evaluation" / "external_projects" / "MLPERF_TINY" / "snapshot" / "paper.txt"
    (root / "project").mkdir(parents=True)
    shutil.copy2(snap, root / "project" / "paper.txt")
    rows = [("Keyword Spotting", "DS-CNN", 52.5, "90% (Top-1)"), ("Visual Wake Words", "MobileNetV1", 325, "80% (Top-1)"),
            ("Image Classification", "ResNet", 96, "85% (Top-1)"), ("Anomaly Detection", "FC-AutoEncoder", 270, ".85 (AUC)")]
    write(root / "data" / "reference_models.csv",
          "use_case,model,tflite_size_kb,quality_target\n" + "".join(f"{u},{m},{s},\"{q}\"\n" for u, m, s, q in rows))
    write(root / "data" / "PROVENANCE.md",
          "# Provenance\n\n`reference_models.csv` re-types Table 1 (\"MLPerf Tiny v0.5 Inference Benchmarks\") of "
          "`project/paper.txt` (frozen snapshot of the official paper). Every number must occur in the paper text; "
          "visual gate V1 checks this (`data.source_text`).\n\n"
          f"paper.txt {sha(root / 'project' / 'paper.txt')}\n")
    ev = [item("E001", "result", "TFLite size of each reference model (Table 1)", "project/paper.txt",
               anchor="Model (TFLite Model Size)", quantity="tflite_model_size_kb",
               value={m: s for _, m, s, _ in rows}),
          item("E002", "result", "Per-submission latency and energy (Figure 5)", "project/paper.txt", anchor="Figure 5",
               status="unverifiable", strength="soft", notes="values exist only in a figure; not recoverable from the text")]
    cl = [claim("C001", "The four MLPerf Tiny v0.5 reference models range from 52.5 KB (DS-CNN) to 325 KB (MobileNetV1).",
                "measured", ["E001"])]
    write(root / ".rcs" / "evidence" / "research_evidence.json", {"project_root": ".", "generated_at": "2026-09-29", "items": ev})
    write(root / ".rcs" / "evidence" / "missing_evidence.json",
          {"items": [{"figure": "V002", "claim": "per-submission latency comparison", "needed": "numeric values behind Figure 5",
                      "question": "Can the authors' results table for the v0.5 submission round be supplied?",
                      "effect_on_paper": "the latency comparison is described in words only"}]})
    write(root / ".rcs" / "claims" / "claim_evidence_map.json", {"claims": cl, "limitations": [], "negative_result_decisions": []})
    write(root / ".rcs" / "plan" / "visual_registry.json", {"visuals": [
        {"id": "V001", "number": 1, "rq": "RQ1", "tier": "main", "kind": "CONTEXTUAL", "representation": "bar_h",
         "reader_question": "How small are the benchmark's reference models?", "claim_ids": ["C001"], "evidence_ids": ["E001"],
         "title": "Reference model size per benchmark", "value_label": "TFLite model size", "units": "KB",
         "figure_path": "figures/V001_model_size.svg",
         "data": {"file": "data/reference_models.csv", "scope": {}, "x": "model", "y": "tflite_size_kb",
                  "source_text": "project/paper.txt"},
         "caption": "The four reference models span 52.5 KB to 325 KB, so every model fits in the few hundred kilobytes of "
                    "memory a microcontroller offers. TFLite model size in KB of each benchmark's reference model; single "
                    "values from Table 1 of the MLPerf Tiny paper.",
         "caption_requirements": ["units", "source"],
         "alt_text": "Horizontal bar chart of TFLite model size in kilobytes for four reference models, from 52.5 KB for DS-CNN to 325 KB for MobileNetV1."},
        {"id": "V002", "number": 2, "rq": "RQ2", "tier": "main", "kind": "COMPARATIVE", "representation": "bar_h",
         "reader_question": "How do the first submissions compare in latency?", "claim_ids": [], "evidence_ids": ["E002"],
         "status": "NO_VALID_VISUAL", "figure_path": "figures/V002_latency.svg",
         "data": {"file": "data/missing.csv", "x": "system", "y": "latency_ms"}},
    ]})
    write(root / ".rcs" / "state.json", {"step": 15, "guardrail": "v0.3", "gates": {}})
    write(root / "paper.md",
          "# MLPerf Tiny: excerpt (Stage 2 acceptance)\n\n## Benchmarks\n\n"
          "Figure 1 shows how small the reference models are: they range from 52.5 KB for DS-CNN to 325 KB for "
          "MobileNetV1 {C001}. The latency results of the first submission round appear only as a figure in the source, "
          "so they are described but not re-plotted here.\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--asmos", default="C:/Users/csdee/PESU/CDSAML/ASMOS")
    a = ap.parse_args()
    build_asmos(Path(a.asmos))
    build_mlperf()
    print("built", HERE / "ASMOS", HERE / "MLPERF_TINY")
