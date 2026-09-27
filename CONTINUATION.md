# CONTINUATION — how to resume this work in a new session

Last checkpoint: 2026-09-27. Branch `rce-skill-v0.1.0` (GitHub: csdeepak/research_writing_skill). Tag `skill-v0.1.0` = frozen baseline skill.

Paste this to a new Claude Code session opened in this repo:

> Read `CONTINUATION.md`, `evaluation/RESUME.md`, `evaluation/logs/DECISIONS.md` (D-01…D-17) and `evaluation/logs/PROGRESS.md`, then continue the external-validation programme from "Remaining work" below. Do not modify `skill/` (canonical v0.1.0) or the frozen Gold Set. Keep all decisions logged.

---

## 1. What this project is
- `docs/` — design phase (foundation analysis of the OOMD Technical Writing course, corpus strategy, 3-agent architecture, evaluation framework, skill spec, verified sources).
- `skill/` — Research Communication Engine skill **v0.1.0** (frozen; manifest `skill/versions/0.1.0/MANIFEST.json`).
- `tools/` — validator, linter, packet builder, scoring (21 tests).
- `evaluation/` — the autonomous external-validation study (this is what is in progress).

## 2. The study (brief = the long "NEXT PHASE — AUTONOMOUS EXTERNAL VALIDATION" message)
Question: does the skill make readers reconstruct real research more faithfully than a plain agent? Primary metric = reconstruction fidelity against a frozen, verified Gold Account (MMF = RR − DR − 0.5·IR; RR recall, DR distortion, IR intrusions).

## 3. Status by phase
| Phase | Status | Where |
|-------|--------|-------|
| 0 Status record | ✅ | `evaluation/EXTERNAL_VALIDATION_STATUS.md` |
| 1 Project suitability (SWE-bench, BEIR, MLPerf Tiny, SAM, Whisper, OpenHands) | ✅ all accepted (with caveats) | `evaluation/external_projects/*/PROJECT_ASSESSMENT.md`, snapshots pinned in `evaluation/manifests/source_snapshots.json` |
| 2–3 Gold Accounts + independent verification + freeze | ✅ v1.0 frozen | `evaluation/ground_truth/` (`GOLD_SET_MANIFEST.md`, `*/gold_story.v1.json`, `*/VERIFICATION.md`) |
| 4 Reviewer validation (2 model families) | ✅ | `evaluation/reviewer_validation/REVIEWER_VALIDATION_REPORT.md` |
| 5 Plain vs skill (6 projects) | ✅ F1 6/6 pairs; F2 5/6 | `evaluation/results/comparison/` (`SEALED_MAPPING.json`, `raw/`, `grading/`, `scores/per_review.json`) |
| 6 Cheap vs strong evidence agent (3 projects) | packages ✅ scored; step-17 drafts ✅ 6/6; F1 reviews+grades ✅ 5/6 (**OPENHANDS skillpkg-strong review pending**) | `evaluation/evidence_agent/` |
| 7 Final report | ❌ not written | → `evaluation/results/FINAL_EXTERNAL_VALIDATION_REPORT.md` |
| 8 Failure analysis | ✅ draft | `evaluation/results/FAILURE_ANALYSIS.md` |
| 9 Engineering loop | candidate **v0.2.0** built, 44/44 tests; **A/B test runs interrupted** | `evaluation/skill_versions/v0.2.0-candidate/` (+ proposal in its `versions/proposals/`) |
| 10 Personal projects | ❌ not started | candidates: `C:/Users/csdee/PESU/capstone`, `PESU/PAY`, `PESU/CDSAML/ASMOS` |

## 4. Key results so far (measured; details in PROGRESS/DECISIONS)
- **Reviewer (evaluator v0.2):** Claude Opus sens 0.956 / false alarms 0.05; Nemotron 0.933 / 0.00; 18/18 pairwise discriminations. Reconstruction detects overclaiming & citation misuse strongly; does NOT detect ordering/jargon/buried contribution (strong-LLM reader limitation).
- **Plain vs skill v0.1.0 (Opus reader, 6 projects):** ΔRR −0.087 (skill lower in 5/6), ΔMMF −0.074 (95% CI −0.20…+0.05), ΔDR +0.004; reviewer dimension ratings +0.56 in favour of skill → the reviewer prefers skill papers while readers recover less. Nemotron reader: mixed (ΔMMF ≈ +0.02 on 3 pairs).
- **Main failure clusters:** (S1) author-stated limitations replaced by writer-derived ones (Q11 net −7); (S2) author rationale/motivation lost; (S3) low process adherence in CLI runs (rule files unread, tools never run, gates self-certified); (S4) length overruns.
- **Evidence agent:** strong (Opus) packages 100% numerically grounded; cheap (Haiku) 78–98% — ungrounded numbers were unit reformatting, not fabrication. Downstream (Opus reader, step-17 drafts): SWE strong MMF 0.50 vs cheap 0.41 (cheap DR 0.10); Whisper cheap 0.625 vs strong 0.525 (strong DR 0); OpenHands cheap 0.225 (strong pending).

## 5. Execution constraints (important)
- `claude` CLI account is **out of credit** → Claude-family roles run as **in-session subagents** via task folders: `python evaluation/harness/subagent_tasks.py make-cmp-reviews | make-grades cmp|rv | collect`; tasks live in `%TEMP%/rce_tasks/<id>/prompt.md`; launch a subagent with: "Read …/prompt.md and do exactly what it asks. Only permitted actions: one Read of prompt.md and one Write of …/output.txt …". Check tool_uses == 2.
- Session usage limits hit every few hours → run ≤ 4–6 subagents at once; after an interruption, restart (subagent IDs from the previous session cannot be resumed in a new session).
- Reviewer family 2 = `nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter (free tier, 50 req/day, resets 00:00 UTC). Codex/OpenAI unavailable.
- Writer workspaces live outside the repo in `%TEMP%/rce_ws/<PROJECT>__<condition>/` (TASK.md inside). If missing, re-create with `evaluation/harness/writers.py prep` (Phase 9 prep code is in DECISIONS D-17 / session history: copy snapshot → `project/`, skill → `rce/skill`, tools → `rce/tools`, `TASK.md` = `writers.SKILL_PROMPT`).
- Evaluator frozen at v0.2; Gold Set frozen v1.0.

## 6. Remaining work (in order)
1. **Phase 6:** review + grade OPENHANDS/skillpkg-strong (packet `pkt-47ad65cd` exists; review task `t-5ce3c3ce` in `%TEMP%/rce_tasks` — relaunch it), then `python evaluation/harness/compare.py analyze` and write the Phase 6 section.
2. **Phase 9 A/B (v0.1.0 vs v0.2.0 on step-17 drafts, subagent path):** workspaces `%TEMP%/rce_ws/{OPENHANDS,MLPERF_TINY,BEIR}__skillv0{10,20}sub`. OPENHANDS v010 was nearly finished, v020 at step 9, MLPERF pair early, BEIR pair not started — simplest is to re-prep and re-run all six from scratch. Then `writers.py collect <P> skillv0{10,20}sub` → `compare.py packets <P> skillv010sub skillv020sub` → Opus reviews → Sonnet grades → compare Q11/Q2/Q5 recall, MMF, DR, words. Accept v0.2.0 into `skill/` only if Q11 recall improves and MMF/DR do not regress on ≥2/3 projects; then bump version, changelog, `tools/snapshot_version.py 0.2.0`.
3. **Phase 7:** `evaluation/results/FINAL_EXTERNAL_VALIDATION_REPORT.md` answering Q1–Q4 (measured vs observations vs interpretations vs assumptions vs limitations vs open questions) and `evaluation/results/RECOMMENDED_NEXT_VERSION.md` (include: attribution-preserving limitations/rationale, executable gates, length gate, restating reconstruction questions in review_agent.md (D-13), reviewer ratings are not a proxy for understanding).
4. **Phase 10:** personal projects (only after 1–3); build a verified gold account per project first.
5. Commit & push results when a milestone is complete.

## 7. Known open issues
- PR to `main`: `main` does not exist on GitHub; creating it was blocked by the permission classifier (D-05). The default branch on GitHub is `rce-skill-v0.1.0`.
- 2 Nemotron outputs permanently malformed (Whisper-plain comparison) — excluded.
- No human-reader validation (not possible autonomously).
