# Gold Set Manifest — FROZEN v1.0 (2026-09-24)

The Gold Set is the scoring authority for Phases 4–9. **Scoring files: `ground_truth/<P>/gold_story.v1.json`.** Drafts are kept unmodified for audit. SHA-256 of every file: `manifests/gold_set_manifest.json`. No Gold file may change during baseline evaluation; any later correction becomes v1.1 with a changelog entry and re-scoring of *all* conditions.

Process per project: Sonnet drafter (snapshot-only) → independent Opus verifier (fresh context, snapshot-only, issue table with quotes) → corrected v1. Writers never saw Gold; Gold builders/verifiers never saw papers.

| Project | Source snapshot (pinned) | Nuggets | Verification verdict | Issues found (high/med/low) | Most serious draft error caught | Unresolved uncertainty | Known limitations |
|---------|--------------------------|---------|----------------------|------------------------------|--------------------------------|------------------------|-------------------|
| SWE_BENCH | arXiv 2310.06770v3; SWE-bench/SWE-bench@02e7a74f | 40 | ACCEPT AFTER CORRECTIONS | 2/11/13 | Draft repeated the abstract's "Claude 2 best (1.96%)"; paper's v3 Table 5 shows Claude 3 Opus 3.79% | Inconsistent GPT-4 labelling across tables; Lite criteria (App. A.7) truncated | Paper internally inconsistent (abstract vs table) — table treated as authoritative |
| BEIR | arXiv 2104.08663v4; beir-cellar/beir@ef83d293 | 40 | ACCEPT AFTER CORRECTIONS | 1/8/12 | Claimed high-Hole@10 systems gained most after re-annotation; Table 4 contradicts | Table 3 per-model latency/index-size columns unmatched | Tables reflowed; values mapped by cross-checked row order |
| MLPERF_TINY | arXiv 2106.07597v4; mlcommons/tiny@4addd0fa | 40 | ACCEPT AFTER CORRECTIONS | 1/9/15 | Nugget scored readers on extraction loss ("not recoverable from snapshot") | Figure 5 latency/energy values and Table 2 check marks absent from text | Paper's central 3-axis result only partially in text |
| SAM | arXiv 2304.02643v1; facebookresearch/segment-anything@dca509fe | 36 | ACCEPT AFTER CORRECTIONS | 1/9/10 | Table 4 object-proposal values mis-mapped (baseline vs SAM) | Ablation magnitudes only in plots; Table 7 counts unmatched | Several results only in figures |
| WHISPER | arXiv 2212.04356v1; openai/whisper@86098128 | 40 | ACCEPT AFTER CORRECTIONS | 1/9/12 | Fabricated "conflict" 2.5 vs 2.7 WER (actually greedy vs beam decoding); 55.2% averaged over 13 not 12 sets | MLS column attribution; figure-only values | README describes later models (turbo, large-v3) absent from paper |
| OPENHANDS | arXiv 2407.16741v3; OpenHands/OpenHands@b0906809, OpenHands/benchmarks@405bae71 | 40 | ACCEPT AFTER CORRECTIONS | 3/6/10 | GAIA 32.1% attributed to the wrong agent | Table 1 cell contents lost; some Table 4 rows medium-confidence (excluded) | Both repos diverged from the paper → gold is paper-only; writer contamination risk from READMEs tracked |

## Scoring conventions fixed at freeze
- Nugget-weighted metrics (RR, DR, IR, MMF, Core RR) as defined in `docs/04 §2`; additionally a **question-macro RR** (mean of per-question RR) is reported because some questions have 5–8 nuggets (guideline 1–4 exceeded in SWE_BENCH, BEIR, MLPERF_TINY, WHISPER, OPENHANDS; left as verified rather than edited post hoc).
- Internal source conflicts: the specific table/number is authoritative over abstract/prose restatement unless the verifier recorded otherwise.
- `approved_by_researcher: false` for all — these are third-party projects; the verifier pass substitutes for researcher approval. Stated as a limitation.
