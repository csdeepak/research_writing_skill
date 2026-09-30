# RESUME — superseded: see /CONTINUATION.md (checkpoint 2026-09-27). Historical checkpoint 2026-09-25 below.

Read this first when resuming. Logs: `logs/PROGRESS.md`, `logs/DECISIONS.md` (D-01…D-17), `logs/experiments.jsonl`.

## Execution constraints discovered
- `claude` CLI account: **out of credit** (D-14) → Claude roles run as in-session subagents via task folders (`harness/subagent_tasks.py`, tasks in `%TEMP%/rce_tasks`, index.json). Subagent prompt: "Read <task>/prompt.md … write <task>/output.txt"; verify tool_uses == 2.
- Session usage limits interrupt subagents every few hours → resume interrupted agents with SendMessage (context kept) rather than restarting; run ≤ 4–6 subagents at once.
- Reviewer F2 = NVIDIA Nemotron-3-Ultra via OpenRouter **free** (50 req/day, resets 00:00 UTC). Codex/OpenAI unavailable (D-10).
- Evaluator frozen at **v0.2** (D-13). Gold Set frozen v1.0.

## Phase status
| Phase | Status | Key outputs |
|-------|--------|-------------|
| 0 | done | `EXTERNAL_VALIDATION_STATUS.md` |
| 1 | done — all 6 accepted | `external_projects/*/PROJECT_ASSESSMENT.md` |
| 2–3 | done — verified + frozen | `ground_truth/GOLD_SET_MANIFEST.md`, `*/gold_story.v1.json` |
| 4 | **done** | `reviewer_validation/REVIEWER_VALIDATION_REPORT.md` (F1 sens 0.956 / FA 0.05; F2 0.933 / 0.00; 18/18 pairwise) |
| 5 | **done for F1 (6/6 pairs); F2 5/6 pairs** (Whisper-plain F2 malformed twice → excluded) | `results/comparison/scores/per_review.json`, `paired` stats in PROGRESS; F1: ΔRR −0.087 (skill lower in 5/6), ΔMMF −0.074 (CI crosses 0), Δdims +0.56 |
| 6 | packages done & scored (numeric grounding: strong 100%, cheap 78–98% — ungrounded = unit reformatting, not fabrication; gold coverage in `evidence_agent/gold_coverage_summary.json`); downstream step-17 drafts: SWE cheap ✅ SWE strong ✅ WHISPER cheap ✅ (reviewed F1 ✅, grading pending); **WHISPER strong, OPENHANDS cheap, OPENHANDS strong interrupted** | `evidence_agent/*` |
| 7 | pending (report) | — |
| 8 | **draft done** | `results/FAILURE_ANALYSIS.md` |
| 9 | candidate v0.2.0 built & tests pass (44/44) | `skill_versions/v0.2.0-candidate/` (+ proposal JSON/MD); **test runs interrupted**: workspaces `%TEMP%/rce_ws/{OPENHANDS,MLPERF_TINY,BEIR}__skillv0{10,20}sub` prepared (TASK.md = Phase 5 skill prompt, steps 1–17) |
| 10 personal projects | not started | [candidate project list redacted for the public release] |

## Next actions (in order)
1. Resume/finish Phase 6 drafts (WHISPER strong, OPENHANDS cheap/strong) → `writers.py collect <P> skillpkg-<t>` → `compare.py packets <P> skillpkg-<t>` → `subagent_tasks.py make-cmp-reviews` → Opus subagent reviews → `make-grades cmp` → Sonnet graders → collect → `compare.py analyze`.
2. Grade the 3 Phase-6 reviews already collected (`subagent_tasks.py make-grades cmp`).
3. Phase 9: run the 6 draft writers (pairs per project), collect with cond `skillv010sub` / `skillv020sub`, packets, Opus reviews, grading, compare (Q11/Q2/Q5 recall, MMF, DR, words). Decision rule: accept v0.2.0 only if Q11 recall improves and MMF/DR do not regress on ≥2/3 projects.
4. Phase 7 report `results/FINAL_EXTERNAL_VALIDATION_REPORT.md`; `results/RECOMMENDED_NEXT_VERSION.md`.
5. Phase 10 personal projects (after 1–4).
6. Canonical skill remains v0.1.0; do not commit until user asks (brief: "do not commit immediately").
