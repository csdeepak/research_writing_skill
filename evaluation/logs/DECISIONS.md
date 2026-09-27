# Decision Log (external validation)

Each decision: context → choice → rationale → consequence/risk. Appended chronologically; never edited retroactively (corrections are new entries).

## D-01 · 2026-09-24 · Reviewer model families
- Available: Claude (claude CLI, Code account), OpenAI via Codex CLI (ChatGPT login), OpenRouter key on **free tier with 0 credits** (paid calls not used — would run an unfunded balance).
- Choice: **F1 = Claude Opus** (`claude -p`, no tools, no settings, empty cwd); **F2 = OpenAI (Codex CLI default model, recorded per call)** (`codex exec -s read-only --ephemeral`, empty cwd, content inline); **F3 = Qwen3.8-27B (OpenRouter free)** opportunistic third family for reliability only.
- Risk: F3 free endpoint rate-limited (429 observed at first smoke test) → F3 results may be partial; primary conclusions rest on F1+F2.

## D-02 · Grader
- RECON_GRADER = Claude Sonnet via `claude -p` (no tools), sees only gold nuggets + an unlabeled reconstruction (random ID). Second grader (Codex) on a subset for inter-grader agreement.
- Risk: F1 reconstructions graded by same vendor family → reported alongside F2 grading agreement.

## D-03 · What counts as "project evidence" for public projects
- Choice: frozen snapshot = official arXiv paper text (pinned version, pdftotext) + official repository README(s) at pinned commit (`manifests/source_snapshots.json`). Gold Accounts are built **only** from this snapshot, so writers are never scored on information they could not have had.
- Consequence: projects arrive with a strong narrative already (their paper). This likely compresses condition differences (ceiling) → conservative test of the skill. Recorded as limitation.
- Downloads: public PDFs/READMEs from arxiv.org and GitHub, authorized by the study brief ("obtain from public sources"). PDFs are not stored (re-downloadable from pinned URL); text is stored.

## D-04 · Python TLS
- Local MSYS Python lacks a CA bundle; all HTTPS fetches use `curl`. No security settings changed.

## D-05 · PR to main blocked
- Creating an empty `main` and merging it into the feature branch was denied twice by the permission classifier ("Git Destructive"). Not retried; left for the user. Not needed for the validation study.

## D-06 · Usage-limit event and model tiering for Gold Accounts
- All six Opus gold-builder agents hit the account session limit (HTTP 429, "session limit") before writing outputs (only MLPERF_TINY/PROJECT_ASSESSMENT.md was written). Relaunched after reset.
- To conserve plan quota for the remaining ~100 model calls: gold **builders** = Claude Sonnet; independent **verification** = Claude Opus (fresh context). Verification is the quality gate, so the stronger model is placed there.

## D-07 · Blinding substitution in variant G
- Reviewer packet for G replaces the reference note that reveals test-item status with "Reference list omitted in this manuscript version." Recorded in SEALED_MAPPING.json.

## D-08 · Writer protocol (Phase 5)
- Both conditions: Claude Sonnet (`claude -p`, reported `claude-sonnet-4-6`), identical task text, audience (mode B adjacent ML researchers), length (3,000–4,500 words), tools (Read/Write/Edit/Glob/Grep + python only), permission-mode dontAsk, no web, workspace outside repo (`%TEMP%/rce_ws/<P>__<cond>`), identical project snapshot. Stream-json tool logs audited for any path outside the workspace and for reads of reviewer/grader/optimizer prompts (ISOLATION_BREACH).
- Skill condition: session 1 = workflow steps 1–17; step 18 = external blind review (Claude Opus, hard isolation, skill REVIEW_AGENT prompt, structured diagnostics only returned); session 2 = steps 19 + 21. **One review round** (skill allows up to 3) to conserve quota — documented deviation.
- Known confound: the in-loop reviewer (Claude Opus) is the same model family as evaluation reviewer F1. F2 (OpenAI) evaluation is uncontaminated by in-loop feedback and is treated as the primary reviewer-dimension signal; the primary outcome (reconstruction vs frozen gold, graded without seeing papers) is less exposed to reviewer taste.
- Writers may run before Gold freeze: writers never see Gold, and Gold builders/verifiers never see papers. Gold is frozen before any scoring.

## D-09 · Reviewer schema strictness
- Reviewers write `location.paragraph` as strings ("§3.1 ¶2") where the schema expects integers. Treated as format-only (not a reviewer failure); counted separately in analysis.

## D-10 · Reviewer family 2 replaced: OpenAI (Codex) → NVIDIA Nemotron-3-Ultra
- Codex CLI (ChatGPT login) served one smoke call, then every model returned 404/"not supported" (default gpt-5.5 404; gpt-5.4/5.3-codex/5.2/5.1/5/5-codex/o4-mini "not supported"). 7 F2 reviews failed after the CLI's own 5 reconnects × 3 harness retries; no output was produced (nothing fabricated). Marked permanent failure for this session.
- OpenRouter paid models are not usable (0 credits). Free non-Anthropic models: Qwen, Gemma, GLM rate-limited (429), Inkling 403; **nvidia/nemotron-3-ultra-550b-a55b:free responds** → F2 = NVIDIA Nemotron-3-Ultra-550B. Genuinely different model family (NVIDIA, not Anthropic).
- Constraint: free tier = 50 requests/day → F2 runs 1 seed in Phase 4 (7 calls) and 1 per paper in Phase 5 (12) and Phase 6; F1 (Claude Opus) runs 2 seeds in Phase 4.
- OpenRouter retries raised to 5 with 90 s × attempt backoff.

## D-11 · Reviewer validation criteria refined (not the reviewer)
- F1 (Claude Opus) dimension-attribution sensitivity 0.868 < provisional 0.90; raw false-alarm rate on A 0.05/0.15 (mean 0.10).
- Diagnosis: (a) A_clean contains 3 [CITATION NEEDED] markers and a text-only figure caption — genuine traceability/figure defects shared by ALL variants, so reviewer flags on A for evidence_traceability/figure_table are correct, not false alarms (benchmark-design defect, category F). (b) The 7 attribution misses are single expected dimensions that EXPECTED.json arguably over-specifies (e.g., B still states contributions in its Conclusion).
- Decision: do NOT alter the reviewer to fit EXPECTED.json (would overfit the evaluator to the author's expectations). Report three criteria: pairwise discrimination (variant mean < A mean, same seed), dimension attribution (as provisional), and adjusted false alarms (excluding dimensions explained by properties constant across variants). Benchmark defect logged for a future benchmark version (not changed now: brief says do not redesign unless broken; comparisons vs A remain valid because the defect is constant).
- Second, cross-family grader (Nemotron) on F1 seed-1 reconstructions for inter-grader agreement.

## D-12 · Phase 6 design
- Projects: SWE_BENCH, WHISPER, OPENHANDS (most number-dense and conflict-heavy → hardest evidence extraction; budget allows 3 of 6).
- CORPUS_AGENT(mode=evidence): cheap = Claude Haiku 4.5, strong = Claude Opus; identical prompt, workspace (snapshot + corpus_agent.md + evidence_model.md + schemas only), tools, no web.
- Downstream: identical skill writer (Sonnet, skill v0.1.0) receives ONLY the package (not the paper) as ./project/; same in-loop review/revise protocol; packets + blind reviews + frozen-gold grading identical to Phase 5.
- Package metrics: objective numeric grounding (every number in package values/summaries checked against snapshot text), kinds/claim-type distributions, unresolved references, missing-evidence counts; plus gold-nugget coverage graded by Sonnet grader.

## D-13 · Evaluator defect found and repaired (evaluator v0.1 → v0.2)
- Observation: reviewers (both seeds, both phases) did NOT answer the 12 reconstruction questions as defined; they substituted their own sequence (e.g., Q3 "research question", Q4 "contributions", Q10 "dataset", Q11 "comparison to prior work"), inconsistently across reviews. The v0.1 output template listed keys Q1–Q12 without restating the questions; the questions exist only inside the long review_agent.md prompt. The grader then scored misaligned answers inconsistently (sometimes crediting content found under other keys, sometimes not).
- Classification: category E (reviewer) + F (evaluation design) — NOT a skill failure.
- Repair (harness only, skill untouched): (1) output instructions restate all 12 questions verbatim with "do not renumber/substitute"; (2) grader searches each gold nugget across the whole reconstruction and reports under the nugget's gold question (measures the reader's mental model independent of answer placement).
- All v0.1 outputs archived under evaluator_v0.1/ (not deleted). ALL Phase 4 and Phase 5 reviews are re-run with v0.2; conclusions use v0.2 only. Preliminary v0.1 Phase-5 pattern (skill higher reviewer dimension scores in 6/6 projects, lower reconstruction in 5/6) is retained in the archive for comparison but not used for conclusions.
- Also proposed for the SKILL (not applied during baseline): skill/agents/review_agent.md has the same weakness; recommended in RECOMMENDED_NEXT_VERSION.
- Second grader: Nemotron free quota is reserved for F2 reviews; inter-grader agreement will use Claude Haiku (different model, same vendor — weaker check; stated as limitation) plus the earlier v0.1 Nemotron grading where comparable.

## D-14 · Claude CLI account out of credit → in-session subagents
- From ~13:40 UTC every `claude -p` call returns "Credit balance is too low" (hard blocker for the CLI account; not fixable autonomously — adding credit is a payment action). Failed: 3 evidence gradings, 3 F1 comparison reviews, all 6 Phase-6 writer drafts (+ dependent steps). No outputs fabricated; failed partial outputs are excluded (see D-15).
- In-session subagents (Agent tool) still work (different billing path). Claude-family roles continue as subagents: task folder outside the repo with prompt.md (role instructions + inputs inline); subagent reads only prompt.md, writes output.txt; harness collects + logs (provider=claude-subagent). Isolation audited via subagent tool-use counts (expected: 1 Read + 1 Write); fresh context = no access to this orchestrator's conversation.
- Consequence: F1 comparison reviews are split across two execution paths (6 via CLI, 6 via subagent) — same model tier (Opus), same prompt text; recorded as a possible confound.

## D-15 · Phase 6 writer runs redone via subagents
- All six CLI package-writer pipelines failed at the credit blocker; SWE_BENCH/skillpkg-cheap left a partial paper (3,924 words, draft session failed mid-run) and WHISPER/skillpkg-cheap an empty one. Both are INVALID and excluded; workspaces deleted and re-prepared.
- Re-run with in-session Sonnet subagents (draft, revise) + Opus subagent (in-loop review via task file), same prompts as Phase 5 (+ package note). Execution path differs from Phase 5 (CLI) but is identical across the cheap/strong contrast, which is what Phase 6 compares. Subagent transcripts audited for file paths outside the workspace.

## D-16 · Budget-driven protocol simplifications (after repeated usage-limit interruptions)
- Phase 6 compares cheap vs strong evidence packages on the skill writer's step-17 draft (steps 1–17), skipping the in-loop review/revise round for BOTH tiers (identical protocol within the contrast). Interrupted subagents are resumed with their context (SendMessage) rather than restarted.
- Phase 9 compares the candidate skill v0.2.0 against v0.1.0 on step-17 drafts as well: v0.1.0 step-17 drafts already exist (skill_agent/<P>/skill/rcs/drafts/v001/paper.md), so the comparison isolates the skill-document change from the review loop.

## D-17 · Phase 9 test protocol
- Candidate skill v0.2.0 (SKILL_AGENT proposal; 44/44 tests pass; canonical skill untouched) vs v0.1.0, both executed as in-session Sonnet subagents (same path; Phase 6 showed subagent writers read more skill files and ran tools, unlike CLI writers — so v0.1.0 is re-run on the subagent path instead of reusing CLI drafts), full project snapshot, workflow steps 1–17 (draft), identical TASK.md.
- Projects: OPENHANDS (largest v0.1 loss), MLPERF_TINY (rationale loss), BEIR (only project where v0.1 helped → regression check). No project is held out (v0.2 was derived from diagnostics on all six) — overfitting risk stated.
- Readers: F1 Claude Opus (subagent path), graded by Sonnet vs frozen gold v1. Primary: MMF, Q11/Q2/Q5 recall; regression checks: Q7/Q9 recall, DR, words.
