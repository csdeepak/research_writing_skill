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

## D-18 · Migration to another machine (2026-09-27)
- User is moving the session to another laptop. Harness temp paths made portable (OS temp dir, override `RCE_TMP`); Phase 9 workspace creation scripted (`harness/prep_phase9.py`). Phase 6 is complete. Phase 9 draft runs in progress on the old laptop are abandoned and must be re-run from `prep_phase9.py` (no partial outputs were collected). `CONTINUATION.md` is the resume guide.

## D-19 · New-machine execution constraints: session limit + TLS interception (2026-09-27)
- All 6 Phase 9 writer subagents hit the account session limit simultaneously (~15:3x UTC, HTTP 429, "resets 10:40pm Asia/Kolkata"); resumed via SendMessage once the user confirmed the reset (no output lost — all 6 kept their `.rcs/` state and transcripts).
- Shortly after, all 6 failed again, this time with `SELF_SIGNED_CERT_IN_CHAIN` ("Unable to connect to API... usually a TLS-inspecting corporate proxy or a private CA" — Claude Code's own suggested fix is `NODE_EXTRA_CA_CERTS` or adding the CA to the system store). Distinct new constraint on this machine's network path, not seen on the old laptop (which only had D-04's Python-CA-bundle issue, worked around with `curl`). Not fixed here: trusting a new CA is a security-relevant, user-owned decision, not something to change autonomously. User said "Try again"; resumed all 6 via SendMessage without any CA change — treated as possibly transient. If it recurs persistently, this needs the user to either fix the underlying network path or explicitly approve a CA-trust change.
- Consequence: expect further interruptions of this kind; keep resuming via SendMessage (preserves partial work) rather than restarting from `prep_phase9.py`, and log each recurrence here rather than reopening this entry (append-only).

## D-22 · Phase 9 result: v0.2.0 REJECTED, v0.1.0 remains canonical (2026-09-28)
- Full A/B run completed: 6 writer subagents (OPENHANDS/MLPERF_TINY/BEIR × v0.1.0/v0.2.0, step-17 drafts, subagent path per D-17), 6 blind F1 (Opus) reviews, 6 Sonnet gradings vs frozen Gold Set v1.0. `compare.py analyze` (after the D-20 fix) produced the `skillv010sub`/`skillv020sub` paired contrast for the first time.
- Applying the pre-registered rule (D-17: accept only if Q11 recall improves AND MMF/DR do not regress on ≥2/3 projects): **MMF regressed on 2/3 projects** (MLPERF_TINY −0.037, OPENHANDS −0.162; BEIR improved +0.025) — fails the ≥2/3 bar under either plausible reading of the rule (checked both: MMF's own regression count, and the per-project MMF-AND-DR joint count; both give 1/3). Q11 recall also failed to clearly improve: OPENHANDS +0.4 (large), MLPERF_TINY −0.1 (worse), BEIR flat (already at ceiling 1.0, could not improve further). DR improved or held flat on 3/3 (not the blocking factor).
- Mechanism: the OpenHands MMF regression is arithmetically ~entirely an IR (unsupported-belief-intrusion) increase (0.175→0.500, DR and RR unchanged) — readers held *more* unsupported beliefs after v0.2.0, not fewer. This matches a risk the proposal pre-registered before the run: the new labelled "Additional caveats" paragraph may make writer-derived content more salient to the reader rather than less, even though it is now correctly attributed in the source artifacts. Not confirmed by a manual packet trace — recorded as the leading hypothesis. MLPerf Tiny's Q11 regression matches a second pre-registered risk near-verbatim (readers discounting content placed in the "Additional caveats" paragraph).
- Decision: **v0.2.0 rejected.** `skill/` (canonical v0.1.0) and the Gold Set are untouched, as required throughout. No `snapshot_version.py` run, no `skill-v0.2.0` tag. The candidate directory and its 44/44 passing unit tests are kept as-is (not deleted) — the gate result is recorded in the proposal JSON's `gate` field and `evaluation/skill_versions/v0.2.0-candidate/changelog.md`, not by editing history.
- This directly answers unresolved question U3 from `FINAL_EXTERNAL_VALIDATION_REPORT.md` ("Does v0.2.0 recover the author-attribution losses without new regressions?") — partially yes on attribution (OpenHands Q11), but with a new, larger regression (intrusions) that the original v0.1.0 failure analysis did not have on its radar. `FINAL_EXTERNAL_VALIDATION_REPORT.md` §6 updated with the full table.
- Next: `RECOMMENDED_NEXT_VERSION.md` (§4.2) to fold in both this result and the user-supplied `research_skill_spec.md` ("vNext": evidence-locked writing + visual intelligence + reader comprehension, staged Stage 0-4) as the forward plan, per user direction 2026-09-28 to proceed straight to vNext Stage 1 after this decision.

## D-20 · Harness defect: `compare.py analyze` had no v0.1.0/v0.2.0 contrast
- `cmd_analyze`'s paired-differences loop only listed `("plain","skill")` and `("skillpkg-cheap","skillpkg-strong")`; the Phase 9 conditions (`skillv010sub`/`skillv020sub`) were never diffed, so `paired.json` would have silently omitted the one comparison Phase 9 exists to make.
- Repair (harness only, `evaluation/harness/compare.py`, one line): added `("skillv010sub", "skillv020sub")` to the contrast tuple list. Same category as D-13 (evaluation-harness defect, not a skill defect) — caught before any grading ran, so no re-runs needed. `per_review.json`'s `per_question_RR` (per-question recall) is still read directly for the Q11/Q2/Q5 decision-rule check, as CONTINUATION.md §4.1 already specified — `paired.json` only needed the missing tuple for the aggregate MMF/RR/DR/IR/words diff.

## D-21 · Third interruption type (stream stall) + session/process restart survives via subagent transcripts
- A third, distinct interruption type observed (beyond D-19's rate-limit and TLS-cert): two Opus reviewer subagents failed with "Agent stalled: no progress for 600s (stream watchdog did not recover)" — no error, just no output for 10 minutes. Same mitigation as the others: resume via SendMessage, not restart.
- Separately, the underlying Claude Code process/session restarted mid-run (harness reported "Continuation from previous session", new user-email/gitStatus context re-read). This killed the 4 local `Monitor` bash watches on the writer workspaces (reported as orphaned/stopped — Monitor's poll loops are tied to a live process and do not survive a restart). It did **not** kill the 5 in-flight Agent-tool subagents (3 writers + 2 reviewers): all 5 resumed normally via SendMessage using their original agentIds after the restart, confirming subagent transcripts are stored independently of the orchestrating process. Lesson: after any restart, re-arm Monitor if still wanted, but don't assume subagents died too — try SendMessage first; workspace files on disk are the ground truth if an agentId ever does turn out to be unresumable (a fresh subagent can be pointed at the same partially-populated workspace to inspect `.rcs/state.json` and continue, without re-running `prep_phase9.py`).

## D-23 · Review of RECOMMENDED_NEXT_VERSION.md: evaluator defect undermines D-22's deciding evidence (2026-09-28, IN PROGRESS)
- Checked the doc's central mechanism claim ("the labelled 'Additional caveats' paragraph made writer content salient -> OpenHands IR spike") against the data: **0 of 20** OpenHands v0.2.0 unsupported-belief intrusions come from that paragraph. They are specific benchmark numbers, baselines and related-work details, and 22 of 23 spot-checked tokens appear verbatim in the frozen source snapshot. The mechanism hypothesis is refuted, so Part A rec. 1 and the proposed 11th adversarial case rest on nothing and must be withdrawn.
- Root cause (category F, evaluation design, present since v0.1.0): `skill/agents/recon_grader.md` defines `unsupported_belief` as "a claim about the research that the gold story doesn't contain". The gold story is a curated 36-40-nugget subset, so true, source-stated detail is penalized as an unsupported belief. That conflicts with the metric's stated purpose (docs/04 §11: readers must not believe *false* things more often). A more detailed but faithful paper scores worse on IR.
- D-22's rejection rests on OpenHands MMF -0.162, which is arithmetically entirely an IR change. The formal verdict under the frozen, pre-registered metric stands, but its deciding evidence is compromised. v0.2.0 is **not** promoted on a post-hoc metric either.
- Remedy (harness only, evaluator v0.2 stays frozen as the primary metric): `evaluation/harness/intrusion_verify.py`. It pools all 124 F1 unsupported-belief intrusions (all phases, all conditions, 6 projects), shuffles them blind, and has one Sonnet verifier per project label each intrusion SUPPORTED / NOT_FOUND / CONTRADICTED against the frozen snapshot. IR_src and MMF_src are then reported as a sensitivity analysis beside the primary metric. Sealed map: `results/comparison/intrusion_check/SEALED_INTRUSIONS.json`. Tasks: t-2baa6d66 BEIR, t-f10fabe3 MLPERF_TINY, t-5ead3268 OPENHANDS, t-e81f4c1d SAM, t-3a8bd081 SWE_BENCH, t-1bacbef7 WHISPER.
- Other flaws found in the doc (fix when it is next edited): (a) Part A rec. 2 would make IR non-negotiable "in every project", but there is no noise model (n=3, single seed), and IR itself is defective as shown above. Future gates need >=2 reader/writer seeds plus a repeat-grading noise floor. (b) Part E overstates the offline gate: v0.2.0 passed 44/44 offline tests and still failed live. Offline replay can validate *checkers* (lint/validator) but not *writer-instruction* changes, because past drafts were produced under the old rules (off-policy). It filters detector bugs, not reader-level effects, and the doc must say so. A cheaper intermediate tier (paragraph-level micro-reconstruction fixtures, calibrated against full runs) would give some reader signal. (c) Part C says to "reconcile" the spec's 8 provenance types with claim_type but never says how. Decision: keep them as separate axes. claim_type is epistemic; new `basis` (project_file|code|user_confirmed|literature|none) and `status` (VERIFIED|NEEDS_REVIEW|BLOCKED) record provenance. The spec's list has no `interpretation` type, which is a gap in the spec. (d) Spec adversarial cases 4, 6, 7 and 8 are about visuals. In Stage 1 they can only be implemented as fail-closed figure-card checks (NO_VALID_VISUAL, BLOCKED_PERMISSION, UNTRACED_COMPONENT), not as visual generation. (e) The spec file lives only in Downloads. Copy it into docs/.
- Stage 1 started: `evaluation/skill_versions/v0.3.0-candidate` copied from v0.2.0-candidate (44/44 tests pass on the copy). No Stage 1 code written yet. Planned components are in PROGRESS.md.

## D-24 · Intrusion verification result: v0.2.0 verdict robust, its stated reason was wrong (2026-09-29)
- All 6 blinded verifiers finished (124 F1 unsupported-belief intrusions, all phases). **70 SUPPORTED by the frozen source, 41 NOT_FOUND, 13 CONTRADICTED.** 56% of what the frozen metric called "unsupported beliefs" are true statements from the source that the curated gold simply omits. Results: `results/comparison/scores/intrusion_sensitivity.json`.
- Phase 9 under the source-verified sensitivity metric (MMF_src, v0.1.0 -> v0.2.0): BEIR 0.737 -> 0.675 (-0.062), MLPerf Tiny 0.787 -> 0.738 (-0.049), OpenHands 0.513 -> 0.538 (**+0.025**). The OpenHands "-0.162 regression" was an evaluator artifact: 16 of v0.2.0's 20 flagged intrusions were source-supported. v0.2.0 still regresses on 2/3 projects, so **the rejection stands under both metrics**, but all three differences are small (|d| <= 0.062) and single-seed. The honest reading: v0.2.0 is **not shown better and not shown worse**; there is no evidence to accept it.
- The real BEIR v0.2.0 regression: 3 contradicted beliefs (a reader thinking latency and dataset access "are not reported" when the paper does report them). The v0.2.0 BEIR paper is also internally inconsistent: "18 datasets" in 4 places and "8 of the 19 datasets we report on" in one. A within-draft numeric-consistency check would have caught that, so it becomes a Stage 1 fixture.
- Phase 5 (v0.1.0 vs plain) under MMF_src: mean -0.095 (frozen metric -0.074), skill better on 2/6. The Phase 5 conclusion is robust.
- Consequences: (1) the "Additional caveats salience" mechanism (D-22, report §6, RECOMMENDED_NEXT_VERSION Part A) is withdrawn as refuted. (2) Recommendation for evaluator v0.3 (future runs only; v0.2 stays frozen for the completed phases): a grader intrusion counts as `unsupported_belief` only if it is not stated in the source snapshot, i.e. check intrusions against the source and not just the gold. (3) Report MMF_src beside MMF from now on.
- `docs/06_VNEXT_SPEC.md` = the user-supplied spec, copied from Downloads for permanence.

## D-25 · vNext Stage 1 (truth guardrail) built: offline gate passed, promotion pending (2026-09-29)
- Candidate `evaluation/skill_versions/v0.3.0-candidate` (from v0.2.0-candidate). New: `tools/truth_guardrail.py`, `verify_numbers.py`, `claim_invariance.py`, `rce_diagnostics.py`, `replay_fixtures.py`; validator and lint extended; 3 schemas extended; SKILL.md hard rule 9 plus an inline guardrail section; workflow, evidence_model, figure_table_rules, citation_rules and failure_states updated; proposal `20260929-truth-guardrail.json` (validates against skill_change schema); changelog [0.3.0].
- Acceptance (spec Stage 1: "all ten adversarial cases behave as specified, with machine logs"): 25 replay fixtures pass (all 10 spec cases, 3 real Phase 9 defects, 9 negative controls). v0.2.0's tools catch 1/16 of the failure fixtures (only the self-certified gate); the candidate catches 16/16. 60/60 unit tests; demo project and v0.2.0 attribution fixtures unchanged.
- Calibration on real data (six Phase 9 drafts and evidence maps): 0 false conflict alarms; 1 true conflict (BEIR v0.2.0's 18-vs-17 resolved only in free text); 3 untraceable numbers, all genuine writer-invented bounds (MLPerf "under 350/330 KB" vs a 325 KB maximum); 1 true count inconsistency (BEIR 18/19). Three tool defects were found and fixed during calibration: (1) unrestricted derived-number matching "explained" 38/40 fabricated numbers, so derivation is now restricted to the evidence cited on the same line and the probe gives 35/40 caught; (2) '38.6K' was parsed as '38' and model IDs as numbers; (3) a count false positive on explained subsets.
- Design decisions: (a) provenance (`basis`/`status`) is a second axis beside `claim_type`, and the spec's list maps onto them (the spec lacks `interpretation`). (b) Strictness is opt-in per project (`licenses` present, `guardrail: v0.3`), so v0.2.0-era artifacts and gate contracts are unchanged, and no existing test was modified. (c) The four visual cases are implemented as fail-closed card checks, since no visuals are generated yet (Stage 2). (d) Proposal `gate.status` values corrected to the schema enum. The v0.2.0 proposal's "rejected" became "failed", which the skill's own validator flagged.
- Not done or not claimed: no live reader A/B for Stage 1 (checkers are validated offline; the reader effect is unmeasured). `skill/` is untouched. **Promotion of v0.3.0 into `skill/` needs the user's explicit decision.**

## D-26 · vNext Stage 2 (visual intelligence) built and accepted offline on 2 real projects (2026-09-29)
- In `v0.3.0-candidate` with its own proposal (`20260929-visual-intelligence.json`), separable from Stage 1: new files `plan_visuals.py`, `visuals.py`, `validate_visuals.py`, `select_samples.py`, `schemas/visual_registry.schema.json`, plus additive hooks in `validate_artifacts.py` (V1-V6 gates, registry schema) and `replay_fixtures.py`.
- Decisions: (a) **stdlib SVG, not matplotlib.** matplotlib is not installed here and would add a dependency, and deterministic stdlib output makes V6 a byte-exact regeneration check. (b) **Declarative transforms, not arbitrary plotting scripts**: every plotted value is re-derivable and checkable, and no unknown code is executed (spec §9.2). Complex derivations must first be written to a data file by a reviewed script. (c) **V5 is never machine-passed**: it needs a recorded human review, otherwise NOT_RUN (spec §7: "not fake a pass by subjective self-certification"). (d) **Acceptance data = real**: the user's own ASMOS results (aggregate numbers only, original files hashed in PROVENANCE.md, per-query Q/A deliberately not copied, ASMOS repo read-only) and MLPerf Tiny Table 1 (every value checked against the paper text by V1).
- Results: acceptance PASS on both (V1-V4, V6 PASSED; V5 NOT_RUN; 0 errors; excerpts 0 lint errors and 0 untraced numbers); 4 figures published, 1 refused (MLPerf latency exists only inside a source figure); the planner independently chose the same form for 4/4 figures; 67/67 tests; 41/41 fixtures (14 VIS failure fixtures caught, 2 controls pass).
- Found by *looking at* the rendered output rather than trusting the checks: unreadable ticks, an axis below zero for a [0,1] score, raw column names in legends, and a float-rounded label (0.415) contradicting the prose (0.416). Real captions also exposed 4 checker false positives. All were fixed with regression coverage. Lesson recorded: machine gates must be calibrated against real output and human inspection, which is why V5 stays human-gated.
- Not claimed: any reader-comprehension effect of figures (that is Stage 3, M13). Promotion needs the user's decision.

## D-27 · vNext Stage 3 (reader comprehension): tooling complete, human acceptance pending (2026-09-29)
- Built in `v0.3.0-candidate` with proposal `20260929-reader-comprehension.json`: `audit_reader.py` (M02 reader model + M11), `skim_layer.py` (M12), `comprehension_kit.py` (M13 + human protocol + Krippendorff's alpha), `record_review.py` (V5, human-only), `reader_model` schema and template, `templates/human_study_protocol.md`. 74/74 tests.
- **Acceptance (spec §12: "collect blinded human reconstruction results") is NOT met and cannot be met autonomously.** It needs real participants. Nothing is presented as human evidence. The kit makes the study runnable: freeze the key, send packets, fill in a form, grade on sheets, score with alpha.
- Proxy run (LLM readers/graders; ASMOS acceptance project; `evaluation/stage3_proxy/`): the first run was invalid. The grader reference lacked figure captions, so true caption facts were counted as unsupported beliefs (D-24 reappearing). Fixed, re-run, and the first run archived. Valid run: full MMF 0.643 / RR 0.786 vs visual-only MMF 0.571 / RR 0.571; grader alpha 1.0; n = 1 reader per condition, so no interval (a scoring bug that bootstrapped over graders instead of readers was fixed).
- Real-data finding from M11 on the Phase 9 drafts: writers break their own term ledgers (BEIR v0.2.0 uses 'lexical baseline' 3x after registering it as a forbidden synonym of BM25; 14-17 drift hits in two v0.2.0 drafts).
- Promotion needs the user's decision. Human study needs the user: a protocol with ≥3 readers per binding persona and two blind graders.

## D-28 · vNext Stage 4 (full workflow): built, end-to-end run on ASMOS complete; tier-2 self-improvement added (2026-09-29)
- Built in `v0.3.0-candidate` with proposal `20260929-full-workflow.json`:
  - `workflow_guard.py` (roles, ledger, checkpoints, accepted-risk kinds), `g4_check.py`, and `run_workflow.py` (gate
    runner, RUN_LOG).
  - `review_agent.md` now restates the 12 questions verbatim.
  - Tier 2 of the self-improvement loop: `micro_recon.py`. Pilot: MLPERF "under 350 KB" -> "325 KB" moved recall from
    0.0 to 1.0; removing ASMOS intervals moved it from 0.8 to 0.4. n=1 per cell, so it is a smoke test only.
- **E2E run** (`evaluation/stage4_e2e/`, report `E2E_REPORT.md`): the user's ASMOS project, run by 4 separate agents
  (CORPUS -> AUTHOR -> isolated REVIEW -> AUTHOR revise), with no human available.
  - Results: 0 validator errors, 0 role violations, 0 agent-answered checkpoints, and 9/9 blocked claims absent from
    the paper.
  - Review: 19/19 blocking items dispositioned (18 fixed, 1 deferred to a new checkpoint, Q-005). G4 PASSED.
  - **G5 FAILED by design** on 17 author-only markers.
  - The blind review changed the paper's substance (ablation narrowed, accuracy cost "cannot be bounded", new-topic
    comparison made descriptive).
- **Decision: fix tools mid-run rather than finish on known-broken tools.** Every swap is logged with hashes in
  `MIDRUN_TOOL_CHANGES.jsonl`, and the verifier compares the workspace tools with the candidate. **5 defects** were
  found that 78 tests and 49 fixtures had missed:
  1. ledger crash on `paper/`;
  2. packet without figures;
  3. S1/S2 vs BLOCKED contradiction, which forced a placeholder claim;
  4. **line-chart value axis drawn horizontally**, found by the blind reviewer, with a new renderer-independent
     `V3_AXIS_ENCODING` check;
  5. G1 ordered before the report refresh.

  Tests T-045 (extended) and T-047 to T-050 cover them: 83/83 tests and 49/49 fixtures pass. The Stage 2 acceptance
  was re-run and still PASSES.
- Real findings about the project, for the user (the four data checkpoints, Q-001 to Q-004, were already raised by
  CORPUS):
  - Q-001: two conflicting cost headlines, one without its artifact [project-specific values withheld: private project data, redacted 2026-09-30].
  - Q-002: an 'equal accuracy' wording contradicted by the measured accuracies [project-specific values withheld: private project data, redacted 2026-09-30].
  - Q-003: README results whose artifacts are absent.
  - Q-004: a 'zero added labels' wording contradicted by the recorded label count [project-specific values withheld: private project data, redacted 2026-09-30].
  - Q-005 (method details) came from the review. The reviewer also found an internally inconsistent metric pair in one table.
- Not claimed:
  - reader benefit (one run, no comparison arm);
  - reviewer calibration on perturbations;
  - the checkpoint answer -> restored-claim path on a real project (nobody answered).

  `run/` contains ASMOS-derived content; committing it is the user's decision. **Promotion of v0.3.0 into `skill/`
  needs the user's explicit decision.**

## D-29 · Tier-3 live A/B of v0.3.0 vs v0.1.0: protocol PRE-REGISTERED before any draft (2026-09-29)
- **Arms:** `skillv010ab3` (canonical `skill/` + `tools/`) vs `skillv030ab3` (`skill_versions/v0.3.0-candidate`).
  - Same writer path as D-17: in-session Sonnet subagent, full project snapshot, workflow steps 1-17 (draft).
  - Projects: OPENHANDS, MLPERF_TINY, BEIR (same as Phase 9).
- **Task (TASK v2)** is identical for both arms. It is Phase 9's TASK with one change: the no-human clause now says
  "if the skill defines its own procedure for runs with no human available, follow it; otherwise choose the most
  defensible option ... accepted_risks". Phase 9's wording overrode v0.3.0's checkpoint procedure, which would have
  disabled the thing being tested. v0.1.0 defines no such procedure, so its behaviour is unchanged.
  - "No images" stays for both arms: figures are **not** tested here (Stage 3 human study).
- **Measurement:** blind F1 (Opus) review -> Sonnet grading against frozen gold v1 -> blinded source verification of
  unsupported-belief intrusions (evaluator v0.3 sensitivity, D-24).
- **Primary metric:** MMF_src per project.
- **Noise per project:** noise_p = max(0.05, |MMF_src(skillv010ab3) - MMF_src(skillv010sub)|).
  - `skillv010sub` is the Phase 9 v0.1.0 run, an approximate replicate: the task differs only in a clause v0.1.0 has
    no procedure for.
  - 0.05 is the floor, about 2 nuggets, the granularity of a single review.
- **Rule:** effect_p = MMF_src(v030) - MMF_src(v010), both from ab3. A project is "better" if effect_p > noise_p and
  "worse" if effect_p < -noise_p.
  - **Reader benefit SHOWN** iff better on at least 2/3 projects and worse on none.
  - **Regression SHOWN** iff worse on at least 2/3 and better on none.
  - Otherwise **NOT SHOWN** (no detectable difference at n=3, single seed).
- **Secondary (reported, not decisive):** RR, DR, IR, IR_src, recall on Q11/Q2/Q5/Q7/Q9, words, residual markers,
  untraced numbers (`verify_numbers` on each draft), and factual accepted risks.
- This rule states what the evidence shows. Promotion remains the user's decision.

## D-30 · Tier-3 A/B result: reader benefit NOT SHOWN; reviewer calibration passed (2026-09-29)
- **Verdict under the pre-registered D-29 rule: NOT SHOWN.** Report: `results/AB3_REPORT.md`.
- **MMF_src, v0.1.0 -> v0.3.0 (noise):**
  - OpenHands 0.562 -> 0.712, **+0.150** (noise 0.050): better.
  - MLPerf 0.600 -> 0.575, -0.025 (noise 0.187).
  - BEIR 0.813 -> 0.887, +0.074 (noise 0.076).
  - Better on 1 of 3 projects, worse on none, mean +0.066. The frozen MMF gives the same verdict.
- **Consistent with the design, not decisive:**
  - Q11 (author-stated limitations) improved on 3/3 (0.8 -> 0.9, 0.5 -> 0.6, 0.33 -> 1.0).
  - Distortion unchanged, and IR_src within ±0.025.
  - Numbers not traceable to the source fell from 9 to 3; the remaining 3 are writer-derived margins in both arms.
- **Watch points:** MLPerf Q2 fell from 0.375 to 0.125. BEIR v0.3.0 is 4,808 words by the harness token count (which counts
  table pipes and rules) but 4,403 counting prose, headings and table text, so it is within the limit. The skill's
  lint counted prose only (3,751). Fixed after the run: v0.3 projects count headings and tables (`length_count`,
  T-051; 84/84 tests).
- **Main methodological finding:** v0.1.0's own run-to-run spread is 0.05-0.19 MMF_src (0.16 on MLPerf, driven by
  recall). Single-run A/Bs cannot detect +0.07 effects. Any future acceptance test needs at least 3 writer runs per
  arm per project. The same caveat applies retroactively to Phase 9's single-run v0.2.0 rejection (D-22/D-24): that
  verdict is "not shown better", not "shown worse".
- **Evaluator v0.3 note:** readers' critical meta-judgements ("the paper does not establish X") are counted as
  unsupported beliefs. They should be tagged separately.
- **Reviewer calibration** of v0.3.0's own `review_agent.md` on the 7 planted-defect papers (Phase 4 blinded packets,
  Opus, 1 seed):
  - Sensitivity 0.933 (at least 0.90 required) and false alarms 0.05 (at most 0.10 allowed): **passes**.
  - The Phase 4 harness reviewer scored 0.956 / 0.05.
  - All outputs are schema-valid and use Q1-Q12 verbatim.
  - The `review_agent.md` calibration note (which mentions the perturbation set) was left in the prompt, as it is
    deployed.
- **Consequence for promotion:** the evidence for v0.3.0 remains process-level:
  - its checks work (83 tests, e2e);
  - it is not shown to harm readers;
  - it is not shown to help them.

  Promotion remains the user's decision.

## D-31 · Model-agnostic runtime; human answers applied; second review round (2026-09-30)
- **User request:** "complete the rest and make it model agnostic". The user answered three ASMOS checkpoints in chat
  (Q-001, Q-002, Q-004; answers [project-specific values withheld: private project data, redacted 2026-09-30]), recorded with `--by`.
  - An AUTHOR agent applied the answers through the claim map: 4 claims rejected, 2 confirmed, 1 narrowed and
    confirmed; the paper changed by one sentence.
  - Q-003 and Q-005 need files or method notes only the user has, and stay open.
- **Model-agnostic runtime** (Stage 5; proposal `20260930-model-agnostic.json`):
  - `tools/rce_llm.py` covers OpenAI-compatible, Anthropic, Gemini, command, manual and mock providers. It enforces the
    data policy, reads keys only from env vars, logs content-free, repairs JSON, validates with retry, and retries
    transient errors.
  - `tools/rce_roles.py` provides review, calibrate and run-tasks.
  - `templates/models.json` defaults to a local server.
  - `adapters/README.md` and `entrypoints/AGENTS.md` are new; SKILL.md and workflow are now model-neutral.
- **Live proof** (`evaluation/model_agnostic/RESULTS.md`), reviewer calibration on the planted-defect benchmark via the
  tool:
  - NVIDIA Nemotron-3-Ultra 0.945 / 0.00 and Qwen3.8-27B 0.911 / 0.00: both calibrated. The Claude Opus reference is
    0.933 / 0.05.
  - Gemma was not measured: the free-tier 429 persisted.
  - Only synthetic benchmark papers were sent to the hosted endpoint; the ASMOS content never left the machine.
- **ASMOS round 2** (step 20, the first time a second round ran): the review went through `rce_roles review` with the
  `manual` provider and was valid on the first attempt.
  - Blocking findings fell from 8 to 2 and the mean score rose from 3.25 to 3.5.
  - 7 fixed / 3 deferred.
  - G4 PASSED for round v005_1, covering every claim. G5 fails only on 17 author-only markers.
- **Defects found by real use and fixed**, each with a test (T-052 to T-062):
  - rate-limit crash;
  - truncated JSON closers;
  - over-long quotes (cosmetic normalisation, counted);
  - G4 blind to post-review claims;
  - rejected statements called "withheld";
  - G4 isolation path bug;
  - stray spaces from marker stripping;
  - **a bare `[CITATION NEEDED]` passed G5 unseen**;
  - the ASMOS final was over length under the corrected count, so the E2E report was corrected.
- **Workspace:** the runnable ASMOS workspace is at `research_skill/ASMOS_rce_workspace/`, outside the public repo.
  `YOUR_STEPS.md` holds the owner's V5 commands, Q-003/Q-005, and the frozen human-study kit (key 118 points; blinded
  packets; form).

## D-32 · v0.3.0 promoted into skill/ by the user's decision (2026-09-30)
- The user chose "Promote as process upgrade" when asked, with the evidence stated:
  - process checks proven;
  - reviewer calibrated;
  - no reader harm shown;
  - reader benefit not shown (D-30).
- **Done:**
  - the candidate was copied into `skill/` and `tools/`, keeping `skill/versions/0.1.0`;
  - `version: 0.3.0` set;
  - changelog [0.3.0] marked released, with the claim limits stated;
  - five proposals set to gate `passed` with the release note;
  - `python tools/snapshot_version.py 0.3.0` run (72 files).
- **In place:** 95/95 tests, 49/49 replay fixtures, validator `--check-skill` 0 errors and 0 warnings.
- **Not done** (not requested): commit and `git tag skill-v0.3.0`.
- **Still the user's:**
  - the human reading study (Stage 3 acceptance);
  - V5 figure reviews;
  - ASMOS Q-003 and Q-005.

## D-33 · Open-source migration; release v0.4.0 (2026-09-30)
- Followed the author's migration brief: inspect → assessment (`docs/OPEN_SOURCE_MIGRATION_ASSESSMENT.md`) → change.
- **Author decisions (asked):** untrack private-project data going forward (history not rewritten); third-party texts
  are replaced by fetch + SHA-256 (`snapshot_sources.py restore|verify`, 13/13 verified); Apache-2.0; citation
  "C S Deepak", no affiliation.
- **Found in the audit and fixed:**
  - 212 private/third-party files untracked;
  - operator assistant-memory text quoted in 24 archived reviewer outputs, redacted (FC-0018: the harness CLI
    reviewers were not isolated from the operator's environment);
  - private-project values in 5 decision-log lines and in test examples replaced or redacted;
  - mixed CRLF/LF line endings normalised (`.gitattributes`).
- **Version 0.4.0, not 0.3.1:** the skill's own policy makes any new check a MINOR change. This release adds three:
  - the citation-registry check C5 (a fabricated citation previously passed every gate);
  - a per-project language policy;
  - a six-state finding lifecycle.
- **Added:**
  - CLI `tools/rce.py`, packager `tools/package_skill.py` (the claude.ai description limit, 200 characters, was
    verified in Anthropic's docs), repository audit `tools/check_repo.py`, and the failure-case schema, archive
    (18 cases) and validator;
  - synthetic example project (planted problems + clean control; 2 documented gaps);
  - CI (Ubuntu + Windows, Python 3.9/3.12), issue and PR templates, governance, security, privacy, roadmap, citation
    files, 5 SVG diagrams, and a README written to the evidence standard.
- **Corrected claims:**
  - "49 real failure cases" (from the brief) is really 49 replay fixtures = 29 adversarial + 16 controls + 4 from real
    failures, plus 18 documented real failure cases;
  - the private end-to-end run found 10 tool defects, not 14 (an earlier draft of EVALUATION.md said 14).
- **Results in place:** 104/104 tests, 49/49 replay fixtures, 18/18 cases valid, `--check-skill` 0/0, repository
  audit 0 errors, skill ZIP valid (102 files, about 270 KB). `skill/versions/0.4.0/MANIFEST.json` written.
- **Not done:** no commit or tag, and no GitHub release (the author's action). The ChatGPT install path is unverified
  (OpenAI's help page refused automated access).
- **Release (2026-09-30, the author's go-ahead: "reviewed, do the rest"):**
  - release commit `402f7ef` pushed;
  - `main` created and made the default branch;
  - PR #1 merged after CI (Ubuntu + Windows × Python 3.9/3.12) passed;
  - tag `skill-v0.4.0` created, with a GitHub release carrying the skill ZIP (SHA-256 `9b0e560d…`);
  - private vulnerability reporting and Discussions enabled.
- **Not done:** the git history still contains the untracked private and third-party files (the author declined a
  history rewrite).
