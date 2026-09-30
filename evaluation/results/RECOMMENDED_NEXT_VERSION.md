# Recommended Next Version — Research Communication Engine skill

**Revised:** 2026-09-29 (first written 2026-09-28; this revision applies the review in D-23 and the
source-verification result in D-24). **Skill status:** v0.1.0 canonical (`skill/`). Candidate
v0.2.0 **rejected** (D-22, robust under D-24). This is CONTINUATION.md §4.2's deliverable, extended
with the user-supplied vNext spec (`docs/06_VNEXT_SPEC.md`) as the forward roadmap, and with a
recursive self-improvement loop the user asked for.

---

## Part A — What v0.2.0 taught us

v0.2.0 targeted a real problem (the authors' own limitations were overwritten by the writer's, S1/S2).
It fixed that on the worst case (OpenHands Q11 recall 0.2 → 0.6), but it produced **no detectable
overall reader gain**. Under both the frozen metric and the source-verified sensitivity metric it
regresses slightly on 2/3 projects, and every difference is small (|ΔMMF_src| ≤ 0.062) on a single
seed.

**Withdrawn:** the earlier explanation ("the labelled *Additional caveats* paragraph made writer
content salient and inflated intrusions"). The data refutes it: 0 of the 20 flagged OpenHands
intrusions came from that paragraph (D-23). The large OpenHands drop was an **evaluator artifact**:
the grader counts true, source-stated detail missing from the curated gold as an "unsupported
belief". A blinded source check of all 124 such intrusions across every phase found 70 SUPPORTED,
41 NOT_FOUND, 13 CONTRADICTED (D-24).

**Recommendations:**
1. **Evaluator v0.3 (future runs only; v0.2 stays frozen for completed phases):** an intrusion is an
   `unsupported_belief` only if the source snapshot does not state it. `harness/intrusion_verify.py`
   already implements this as a second pass. Fold it into the grader prompt, report MMF_src beside
   MMF, and measure inter-verifier agreement.
2. **Noise before thresholds.** Do not add "IR must never rise in any project" (earlier draft). With
   one seed per paper there is no noise model, so a non-negotiable per-project rule would reject on
   noise. Next A/B: ≥2 writer seeds per condition, plus one repeat grading per review to estimate a
   noise floor. Use a threshold of the form "no regression beyond the noise floor", and keep DR's
   existing non-negotiable status.
3. **Ablate, don't bundle.** v0.2.0 shipped three changes at once; the result can't be attributed
   to any one of them. One mechanism per candidate, or a factorial design.
4. **Keep the attribution idea alive.** It is unrefuted; it just wasn't shown to help overall. Re-test
   it alone, with seeds, after Stage 1.
5. **Within-draft consistency is a real, cheap-to-catch defect.** The v0.2.0 BEIR paper says "18
   datasets" four times and "19" once. It is now a Stage 1 fixture (Part C).

---

## Part B — Standing items from CONTINUATION.md §4.2 (still open)

(a) `skill/agents/review_agent.md` should restate the 12 reconstruction questions verbatim (D-13's
    harness fix, not yet in the skill).
(b) Reviewer quality ratings are not an optimization target (reviewer dimensions went up while
    reconstruction fell for v0.1.0; vNext §11 says the same).
(c) Evidence-stage tiering (Phase 6): a cheap model for inventory, a strong model or strong pass for
    claim typing and negative results. Implement inside vNext M01.
(d) Test on raw evidence, not finished papers (ceiling effect). **Phase 10 (the user's own projects)
    is exactly this test**; deferred by the user's choice, not cancelled.
(e) Human-reader validation (`docs/04_EVALUATION_FRAMEWORK.md` §10) has never been run. It is the
    load-bearing unresolved question.

---

## Part C — vNext roadmap (`docs/06_VNEXT_SPEC.md`)

**Stage 0 — Baseline freeze: done.** v0.2.0 tests reproduce (44/44); its release gate ran and
failed; the open result is documented (§6 of the final report, D-22/D-24).

**Stage 1 — Truth guardrail (in progress: `evaluation/skill_versions/v0.3.0-candidate`).** Design
decisions resolved in this revision:
- **Provenance is a second axis, not a replacement.** The spec's `OBSERVED/DERIVED/…/UNRESOLVED`
  list mixes two things: how a claim is justified (epistemic type) and where it comes from. The
  existing `claim_type` (measured/observed/derived/literature/interpretation/hypothesis/
  speculation/future) stays. New claim fields: `basis` ∈ {project_file, code, user_confirmed,
  literature, none}, and `status` ∈ {VERIFIED, NEEDS_REVIEW, BLOCKED}. The spec's list has no type
  for *interpretation*, which is a gap in the spec. Mapping: OBSERVED→measured|observed,
  DERIVED→derived, LITERATURE→literature, METHOD_FROM_CODE→basis=code, USER_CONFIRMED→
  basis=user_confirmed, HYPOTHESIS→hypothesis, PROPOSED→future|speculation, UNRESOLVED→status=BLOCKED.
- **Banned language becomes evidence-conditional.** Today's lint only *warns* on words like
  "significant". Stage 1 lets a claim carry `licenses` (e.g. `significance_test`,
  `sota_comparison`, `causal_design`, `ood_eval`, `latency_measured`) backed by evidence. A
  tagged sentence that uses a term without the license is an **ERROR**; untagged use stays a WARN.
- **Adversarial cases → executable checks.** Cases 1–3, 5, 9 and 10 are text/artifact checks.
  Cases 4, 6, 7 and 8 concern visuals, which this skill does not generate yet, so in Stage 1 they are
  **fail-closed figure-card checks**: `NO_VALID_VISUAL`, `UNTRACED_COMPONENT`,
  `BLOCKED_PERMISSION`. Actual visual generation is Stage 2.
- **Added fixture from real data:** within-draft numeric inconsistency (the BEIR 18/19 case).
- The earlier "11th adversarial case" (caveat-paragraph salience) is **withdrawn**; it rested on the
  refuted mechanism.

**Stage 2 — Visual intelligence (M04–M10, V1–V6).** After Stage 1. Needs project snapshots with real
figure source data; all six current external projects are text-only.

**Stage 3 — Reader comprehension (M02, M11–M13, V5).** This is where Part B(e), human-reader
validation, belongs.

**Stage 4 — Full workflow** (real agent separation, real human ASK/STOP, G4/G5, edit invariance).

---

## Part D — Recursive self-improvement loop (user request; adapted from Dream-RSI)

**Source:** Zheng et al., *"Dream-RSI: Recursive Self-Improvement through Evolving Worlds,"*
arXiv:2609.14858 (Sept 2026), read at abstract level. Their domains (algorithm, math, GPU-kernel
engineering) have a cheap, automatic reward. **This skill does not**: whether a reader understands
a paper correctly needs an LLM reader or a human. We adopt the insight, not the algorithm. Their core
idea is to keep the base agent unchanged, improve the orchestration layer around it, and use
accumulated history as a cheap offline "replay simulator" so fewer expensive online evaluations are
needed.

| Dream-RSI | This skill |
|---|---|
| Base agent unchanged | Claude is never fine-tuned; only SKILL.md, rules and tools change |
| Discovery history | `.rcs/state.json`, gate reports and audits from every local run |
| Replay simulator | A growing **fixture library** of real failure cases (minimal repros) |
| Cheap offline evaluation | Validator/lint/tests run against every fixture: no LLM calls, free |
| Expensive online evaluation | Live A/B with writer/reader/grader subagents (Phases 5/6/9) |
| Evolving simulator pool | Every new project and domain adds fixtures; the "worlds" diversify |

**Corrected scope (D-23 b):** the offline gate is **off-policy**. Past drafts were written under the
old rules, so replaying them can validate **checkers** (does a new lint/validator rule catch the
known failure without new false alarms?). It **cannot** tell whether a change to the *writer
instructions* improves reader understanding. v0.2.0 is the proof: 44/44 offline, and it still failed
live. So the loop has three tiers:
1. **Free (deterministic):** checker changes are tested against the fixture library.
2. **Cheap (small LLM calls):** paragraph-level micro-reconstruction fixtures, i.e. small
   passage-plus-question sets with known answers, calibrated against full runs. This gives some
   reader signal for instruction changes at a fraction of the cost.
3. **Expensive (live A/B with ≥2 seeds):** only for candidates that pass tiers 1–2.

**Loop:** local, opt-in diagnostics (counts and rule IDs only; no project text) → cluster recurring
patterns → turn each into a minimal fixture → propose a change using the proposal schema → tiers 1–3
→ **human-gated promotion, never automatic.** Diagnostics are data about the skill's performance, not
authority to rewrite the skill: a self-certified self-upgrade is the same failure this study exists
to catch. Cross-user fixture sharing is opt-in and reviewed like any contribution.

**Built in Stage 1:** the local diagnostics logger (tier-0 data) and the fixture replay runner
(tier 1). Tiers 2–3 reuse the existing harness later.

---

## Part E — Status (updated 2026-09-30)

**v0.3.0 is released** (D-32) as a process upgrade and is model-agnostic (D-31). Everything an agent can do is done.
What remains needs people:
1. **Human reading study** (Stage 3 acceptance): the kit is frozen in `ASMOS_rce_workspace/YOUR_STEPS.md` §3.
2. **V5 figure reviews:** three commands, same file §1.
3. **ASMOS Q-003 / Q-005:** result files and method notes only the authors have.
4. **Optional, for a "writes better" claim:** re-run the A/B with ≥ 3 writer runs per arm per project. Single runs
   cannot detect effects of about 0.07 (D-30). The runtime now makes that possible with non-Claude writers and
   reviewers too.
