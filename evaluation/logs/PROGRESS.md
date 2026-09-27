# Progress Log (human-readable)

Machine-readable per-call log: `experiments.jsonl`. Decisions: `DECISIONS.md`.

- 2026-09-24 · Phase 0 done: `EXTERNAL_VALIDATION_STATUS.md` (skill 0.1.0 @ 437a385; 21/21 tests; thresholds marked provisional).
- 2026-09-24 · Harness: `harness/run_model.py` (claude / codex / openrouter; retries ×3; jsonl log). Smoke: claude ok; openrouter qwen free 429 (rate-limited).
- 2026-09-24 · Snapshots pinned for 6 candidate projects (`manifests/source_snapshots.json`): SWE-bench 22.1k words, BEIR 14.1k, MLPerf Tiny 7.5k, SAM 26.6k, Whisper 17.1k, OpenHands 14.7k (+ READMEs at pinned commits).
- 2026-09-24 · Phase 1 done: all 6 candidate projects assessed → **ACCEPT** (SAM) or **ACCEPT WITH CAVEATS** (SWE-bench, BEIR, MLPerf Tiny, Whisper, OpenHands). No substitution needed. Common caveats: pdftotext table damage; README diverged from paper (paper treated as authority); some results only in figures (NOT IN SNAPSHOT).
- 2026-09-24 · Phase 2: Gold drafts (Sonnet builders, after an Opus attempt died at the usage limit) for all 6; independent Opus verification running.
- 2026-09-24 · Phase 4 reviews running (F1 Claude Opus done for 4 packets; F2 Codex running). Phase 5 plain writers running for all 6.
- 2026-09-24 · Phase 2/3 done: all 6 Gold Accounts verified (ACCEPT AFTER CORRECTIONS), frozen as v1.0 (ground_truth/GOLD_SET_MANIFEST.md, manifests/gold_set_manifest.json). Codex/OpenAI became unavailable → F2 = NVIDIA Nemotron-3-Ultra (D-10). All 6 plain papers written.
- 2026-09-24 · Phase 4: F1 (Claude Opus, 2 seeds) + F2 (Nemotron, 1 seed) validation reviews complete; grading done/running. Preliminary: F1 pairwise discrimination 12/12; attribution sensitivity 0.868; clean-version flags explained by benchmark's own [CITATION NEEDED]/text-only figure (D-11).
- 2026-09-24 · Phase 5: all 6 skill papers written (no isolation breaches). Words: SWE 4671, BEIR 5096*, MLPerf 4270, SAM 4704, Whisper 5888*, OpenHands 4468 (* exceeds 4,500 limit; plain papers all within 3,967–4,792). Cost ≈ $3.3–3.9/skill paper vs ≈ $0.35–0.5/plain (~8×).
- 2026-09-24 · PROCESS AUDIT (results/skill_process_audit.json): skill adherence was partial — artifact coverage 0.38–0.69; question/term ledgers and lit→gap chain never built; validator/lint never run; section_rules.md, citation_rules.md, audience_model.md, information_design.md never read in any run; all runs self-reported gates G1–G5 "passed". Artifacts violate the skill's own schemas (validator errors 141–227/run). One positive: SWE_BENCH skill run reports catching and removing 2 fabricated numbers from its intermediate draft.
- 2026-09-24 · Phase 5 blind reviews launched (F1 Opus, F2 Nemotron, 12 papers each). Phase 6 cheap (Haiku) evidence agents launched for SWE_BENCH, WHISPER, OPENHANDS.
- 2026-09-25 · Phase 4 final (evaluator v0.2): F1 sens 0.956/FA 0.05, F2 0.933/0.00, pairwise 18/18 → REVIEWER_VALIDATION_REPORT.md.
- 2026-09-25 · Phase 5 (v0.2) F1 6/6 pairs: skill vs plain ΔRR −0.087 (5/6 lower), ΔMMF −0.074 (95% CI −0.20…+0.05), ΔDR +0.004, reviewer Δdims +0.56 (reviewer prefers skill papers while recall falls). F2 partial, mixed.
- 2026-09-25 · Phase 8 FAILURE_ANALYSIS.md: S1 author-stated limitations replaced by writer-derived (Q11 net −7), S2 author rationale/motivation lost, S3 low process adherence, S4 length overruns.
- 2026-09-25 · Phase 9: SKILL_AGENT candidate v0.2.0 (attribution fields + validator/lint checks, executable gates, length gate); 44/44 tests. Test runs started; interrupted by usage limit. Checkpoint: evaluation/RESUME.md.
