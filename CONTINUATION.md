# CONTINUATION — resume this work on another machine

Checkpoint: **2026-09-27**. Repo: `github.com/csdeepak/research_writing_skill`, branch **`rce-skill-v0.1.0`** (this is also the GitHub default branch; `main` does not exist yet — D-05). Tag `skill-v0.1.0` = frozen baseline skill.

---

## 0. Set up the new laptop (once)

```bash
git clone https://github.com/csdeepak/research_writing_skill.git
cd research_writing_skill
git checkout rce-skill-v0.1.0
python -m unittest discover -s tools/tests          # expect 21 OK (canonical skill v0.1.0)
python -m unittest discover -s evaluation/skill_versions/v0.2.0-candidate/tools/tests   # expect 44 OK
```
Requirements: Python ≥ 3.9 (stdlib only), `git`, `curl`. Optional: `gh` (GitHub CLI), `pdftotext` (only needed to re-snapshot sources — snapshots are already committed), `claude` CLI (only if its account has credit), `OPENROUTER_API_KEY` env var (only for the Nemotron reader, free tier 50 req/day).
Temp work folders are created under the OS temp dir (`rce_ws/`, `rce_tasks/`); set `RCE_TMP=<dir>` to put them elsewhere. **Nothing in the old laptop's temp folders is needed** — everything required is in git or regenerable.

## 1. Paste this into a new Claude Code session opened in the repo

> Read `CONTINUATION.md` fully, then `evaluation/logs/DECISIONS.md` (D-01…D-18), `evaluation/logs/PROGRESS.md` and `evaluation/results/FINAL_EXTERNAL_VALIDATION_REPORT.md`. Continue the autonomous external-validation programme from §4 "Remaining work" of CONTINUATION.md. Do not modify `skill/` (canonical v0.1.0) or the frozen Gold Set (`evaluation/ground_truth/*/gold_story.v1.json`). Evaluator is frozen at v0.2. Log every decision in DECISIONS.md and progress in PROGRESS.md. Work autonomously; run at most 4–6 subagents at once because of session usage limits.

---

## 2. What this repository contains
| Path | What |
|------|------|
| `docs/` | Design phase: foundation analysis of the OOMD Technical Writing course, corpus strategy, 3-agent architecture, evaluation framework, skill spec, verified sources |
| `skill/` | Research Communication Engine skill **v0.1.0** (frozen; `skill/versions/0.1.0/MANIFEST.json`) |
| `tools/` | validate_artifacts, lint_draft, build_review_packet, score_reconstruction, snapshot_version (21 tests) |
| `evaluation/` | The external-validation study (this is what is in progress) |
| `evaluation/harness/` | All experiment scripts (see §5) |
| `evaluation/skill_versions/v0.2.0-candidate/` | Candidate skill v0.2.0 (not yet accepted) + its tools/tests + proposal |

## 3. Study status (the brief = "NEXT PHASE — AUTONOMOUS EXTERNAL VALIDATION & ENGINEERING LOOP")
Primary metric: reader reconstruction fidelity vs a frozen, independently verified Gold Account. **MMF = RR − DR − 0.5·IR** (RR recall, DR distortion, IR unsupported beliefs).

| Phase | Status | Outputs |
|-------|--------|---------|
| 0 status record | ✅ | `evaluation/EXTERNAL_VALIDATION_STATUS.md` |
| 1 project suitability (SWE-bench, BEIR, MLPerf Tiny, SAM, Whisper, OpenHands) | ✅ all accepted | `evaluation/external_projects/*/PROJECT_ASSESSMENT.md`, `*/snapshot/`, `evaluation/manifests/source_snapshots.json` |
| 2–3 Gold Accounts, independent verification, freeze | ✅ v1.0 | `evaluation/ground_truth/` (`GOLD_SET_MANIFEST.md`, `*/gold_story.v1.json`, `*/GOLD_ACCOUNT_v1.md`, `*/VERIFICATION.md`) |
| 4 reviewer validation, 2 families | ✅ | `evaluation/reviewer_validation/REVIEWER_VALIDATION_REPORT.md` |
| 5 plain vs skill v0.1.0, 6 projects | ✅ (Opus 6/6 pairs, Nemotron 4/6) | `evaluation/results/comparison/` |
| 6 cheap vs strong evidence agent, 3 projects | ✅ complete | `evaluation/evidence_agent/` |
| 7 final report | ✅ drafted — **§6 Phase 9 pending** | `evaluation/results/FINAL_EXTERNAL_VALIDATION_REPORT.md` |
| 8 failure analysis | ✅ | `evaluation/results/FAILURE_ANALYSIS.md` |
| 9 engineering loop | candidate v0.2.0 built (44/44 tests); **A/B runs NOT done** (drafts running on the old laptop are abandoned — re-run) | `evaluation/skill_versions/v0.2.0-candidate/` |
| — recommended next version | ❌ not written | → `evaluation/results/RECOMMENDED_NEXT_VERSION.md` |
| 10 personal projects | ❌ not started | candidates: `PESU/capstone` (dental AI system + survey paper), `PESU/PAY`, `PESU/CDSAML/ASMOS` (on the old laptop — copy them over if needed) |

### Key results so far
- **Reviewer (Q1):** Claude Opus sensitivity 0.956 / false alarms 0.05; Nemotron 0.933 / 0.00; 18/18 pairwise. Reconstruction detects overclaiming & citation misuse; not ordering/jargon/buried contribution.
- **Plain vs skill (Q2):** Opus reader ΔMMF −0.074 (95% CI −0.20…+0.05), ΔRR −0.087 (skill lower in 5/6), ΔDR +0.004; reviewer dimension ratings **+0.56 for skill** (looks better, understood no better). Nemotron: ΔMMF +0.049 (3/4 better). Both readers: BEIR +, SWE-bench +, SAM −; OpenHands disagrees.
- **Components (Q3):** losses concentrate in author-stated limitations (Q11 −7), motivation (Q2 −3), design rationale (Q5 −3); possible gain on results (Q7 +4, Nemotron). CLI-run writers ignored most rule files and self-certified gates.
- **Evidence agent (Q4):** strong (Opus) packages better on every package measure (coverage 0.60–0.75 vs 0.49–0.68, 100% numeric grounding vs 78–98%, more negative results/limitations, fewer over-strong claim types) at ≈ 9× cost; downstream reader fidelity did not track package quality (strong better 1/3, cheap better 2/3).

## 4. Remaining work (do in this order)

### 4.1 Phase 9 A/B test: skill v0.1.0 vs v0.2.0 (D-17)
1. `python evaluation/harness/prep_phase9.py` → creates 6 workspaces `<tmp>/rce_ws/{OPENHANDS,MLPERF_TINY,BEIR}__skillv0{10,20}sub`.
2. For each workspace launch one **Sonnet subagent** (≤ 4–6 at a time, run pairs together) with this prompt (replace `<W>`):
   > Your working directory for this entire task is `<W>`. Every relative path (./project/, ./rce/, ./.rcs/, ./paper.md) refers to that directory; always use absolute paths under it. Read `<W>/TASK.md` and carry it out completely (through step 17). Hard rules: never read, list, search or write anything outside that directory; do not use the web; do not spawn agents. You may run python on the tools under ./rce/tools/. When finished, reply DONE with the word count of ./paper.md.
   If a subagent is interrupted by a usage limit, resume it with SendMessage ("Continue from exactly where you stopped…") in the same session; in a new session, re-run `prep_phase9.py <PROJECT>` and restart that pair.
3. Collect + blind packets: `python evaluation/harness/writers.py collect <P> skillv010sub` (and `skillv020sub`), then `python evaluation/harness/compare.py packets <P> skillv010sub skillv020sub`.
4. Reviews (Opus reader): `python evaluation/harness/subagent_tasks.py make-cmp-reviews` → for each printed task id launch an **Opus subagent** with the task prompt (§5.2) → `python evaluation/harness/subagent_tasks.py collect`.
5. Grading: `python evaluation/harness/subagent_tasks.py make-grades cmp` → **Sonnet subagent** per task (§5.2) → `collect` → `python evaluation/harness/compare.py analyze`.
6. Compare per project: MMF, RR, DR, IR, **Q11/Q2/Q5 recall** (target), Q7/Q9 recall and words (regression checks). Use `per_question_RR` in `evaluation/results/comparison/scores/per_review.json`.
7. **Decision rule:** accept v0.2.0 only if Q11 recall improves and MMF and DR do not regress on ≥ 2 of 3 projects. If accepted: copy the candidate into `skill/` (and its tools into `tools/`), set `version: 0.2.0` in `skill/SKILL.md`, update the proposal's `gate` field, `skill/changelog.md` → `python tools/snapshot_version.py 0.2.0` → commit + `git tag skill-v0.2.0`. If rejected: record the gate failure in the proposal and changelog; keep v0.1.0.
8. Fill §6 of `FINAL_EXTERNAL_VALIDATION_REPORT.md`; log the decision (D-19).
Optional if Nemotron quota allows: `python evaluation/harness/compare.py review --families F2` then grading, to add the second reader family.

### 4.2 Recommended next version
Write `evaluation/results/RECOMMENDED_NEXT_VERSION.md`: accepted/rejected v0.2.0 components with evidence; plus (a) restate the 12 reconstruction questions inside `skill/agents/review_agent.md` (evaluator defect D-13); (b) reviewer quality ratings must not be used as the optimisation target (they rose while reconstruction fell); (c) evidence stage: cheap model for inventory, strong model (or strong check) for claim typing and negative results; (d) test on raw-evidence projects, not finished papers (ceiling effect); (e) human-reader validation protocol (docs/04 §10).

### 4.3 Phase 10 — personal projects (only after 4.1–4.2)
For each project folder: build a Gold Account from the project's own files (Sonnet drafter + independent Opus verifier; prompts in `evaluation/prompts/gold_builder.md` / `gold_verifier.md` — **edit their hard-coded repo path** `C:/Users/csdee/PESU/research_skill/research_writing_skill` to the new location), then plain vs accepted-skill papers, blind review, grading, exactly as Phase 5. Treat as an independent generalisation set; do not tune the skill on it.

### 4.4 Finish
Update PROGRESS.md, commit, push.

## 5. How the harness works

### 5.1 Scripts (`evaluation/harness/`)
| Script | Purpose |
|--------|---------|
| `run_model.py` | logged calls to `claude` CLI / `codex` / OpenRouter (retries; `logs/experiments.jsonl`) |
| `snapshot_sources.py` | pin official paper/README snapshots |
| `review_lib.py` | evaluator v0.2: packet sanitising, reviewer/grader prompts (12 questions restated), JSON extraction/repair, scoring |
| `reviewer_validation.py` | Phase 4 |
| `writers.py` | writer workspaces (`prep`, `collect`), CLI writer sessions, audit of tool calls |
| `run_writers.sh`, `run_pkg_writers.sh` | batch writers via CLI (CLI currently unusable — no credit) |
| `compare.py` | blind packets (`SEALED_MAPPING.json`), reviews (CLI/OpenRouter), grading, `analyze` |
| `subagent_tasks.py` | task folders for in-session subagents (`make-cmp-reviews`, `make-grades cmp|rv`, `make-evgrades`, `list`, `collect`) |
| `evidence_agents.py`, `evidence_grade.py` | Phase 6 |
| `audit_skill_runs.py` | process-adherence audit of skill runs |
| `prep_phase9.py` | Phase 9 workspaces |

### 5.2 Subagent task prompt (reviews and grading)
> Read the file `<RCE_TMP>/rce_tasks/<task-id>/prompt.md` and do exactly what it asks. Your ONLY permitted file actions: one Read of that prompt.md, and one Write of `<RCE_TMP>/rce_tasks/<task-id>/output.txt` containing your complete reply. Do not read, search, list or open any other file or directory, and do not use the web. After writing, reply "done".

Reviewers = Opus subagents; graders = Sonnet subagents. Check each finished subagent used ~2 tool calls (isolation audit).

## 6. Execution constraints learned (read before running anything)
- `claude` CLI account on the old laptop ran **out of credit** (D-14); if the new laptop's CLI works, `compare.py review --families F1` / `grade` can be used directly; otherwise use the subagent task route.
- Session usage limits interrupt subagents every few hours — keep concurrency ≤ 4–6.
- OpenAI/Codex model access failed (D-10); second reader = Nemotron-3-Ultra (OpenRouter free).
- Nemotron sometimes emits malformed JSON; retry once, then exclude and log.

## 7. Known open issues
- PR to `main` blocked (D-05): create `main` manually on GitHub if needed, then open a PR from `rce-skill-v0.1.0`.
- No human-reader validation yet.
- Phase 5 used CLI writers, Phases 6/9 subagent writers (execution path confound, documented).
