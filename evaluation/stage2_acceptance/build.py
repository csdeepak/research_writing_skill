#!/usr/bin/env python3
"""Build the vNext Stage 2 acceptance projects from REAL data (spec 12: ">= 2 real projects").

  (private)    the author's own unpublished project; built only when build_private_asmos.py exists locally
               (it is git-ignored and never published). The public release reproduces MLPERF_TINY only.
  MLPERF_TINY  published paper (frozen snapshot, evaluation/external_projects/MLPERF_TINY/snapshot):
               Table 1 reference-model sizes, re-typed into CSV; every value must occur in the paper text
               (visual gate V1 checks this via data.source_text).

Usage: python evaluation/harness/snapshot_sources.py restore MLPERF_TINY   (the paper text is not redistributed)
       python evaluation/stage2_acceptance/build.py
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
    ap.add_argument("--asmos", default=None, help="path to the private project (only with build_private_asmos.py)")
    a = ap.parse_args()
    snap = REPO / "evaluation" / "external_projects" / "MLPERF_TINY" / "snapshot" / "paper.txt"
    if not snap.exists():
        raise SystemExit(f"missing {snap}: run `python evaluation/harness/snapshot_sources.py restore MLPERF_TINY` first "
                         "(third-party paper texts are not redistributed in this repository)")
    built = [HERE / "MLPERF_TINY"]
    if (HERE / "build_private_asmos.py").exists() and a.asmos:
        import build_private_asmos
        build_private_asmos.build_asmos(Path(a.asmos))
        built.insert(0, HERE / "ASMOS")
    build_mlperf()
    print("built", *built)
