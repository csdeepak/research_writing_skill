# vNext Stage 4 — end-to-end workflow run on a real project (ASMOS)

Status: **complete** (2026-09-29). Gate outcome for the full-workflow proposal: process checks passed; G5 fails by design on 17 author-only markers.

## 1. What this run tests, and what it does not

It tests whether the v0.3.0 candidate can be run **as designed** on raw research evidence from a real project:
separate role agents, role-restricted writes with an append-only provenance ledger, human checkpoints that are
asked and not self-answered, executable gates whose statuses come only from tool reports, and an isolated blind
review whose findings each receive a disposition (G4).

It does **not** test whether the paper is better for readers than one written without the skill. There is one
project, one run and no comparison arm. Reader-level effects remain the job of a live A/B (tier 3) and the human
study (Stage 3).

## 2. Setup

- **Project:** the user's ASMOS repository, read-only. `prep.py` copied a curated set of 14 files (docs plus result
  artifacts, with no per-query questions/answers and no finished paper) into `%TEMP%/rce_ws/ASMOS_e2e/project/`.
  `INPUT_MANIFEST.json` records their SHA-256.
- **Skill:** `rce/skill` and `rce/tools` are copies of `evaluation/skill_versions/v0.3.0-candidate` taken at prep time.
  `state.json` opts into `"guardrail": "v0.3"`.
- **Roles**, each a separate agent with its own context and a task file:
  | step | role | agent | may write |
  |---|---|---|---|
  | 1–2 | CORPUS | Opus subagent (`TASK_CORPUS.md`) | `evidence/`, `claims/claim_candidates.json`, `corpus/` |
  | 3–17 | AUTHOR | Opus subagent (`TASK_AUTHOR_DRAFT.md`) | plan, claims map, drafts, visuals, audits |
  | 18 | REVIEW | Opus subagent that sees **one prompt file** (`review_step.py make`) and writes one output file | `diagnostics/` (recorded by the orchestrator) |
  | 19–21 | AUTHOR | Opus subagent (`TASK_AUTHOR_REVISE.md`) | revisions, dispositions, final draft |
- **No human is available** during the run. Wherever the skill says ASK or STOP, the agent must create a checkpoint
  and keep the affected claims `BLOCKED` and out of the paper. No agent may answer a checkpoint. Only the user can,
  with `workflow_guard.py answer --by <name>`.
- **Independent verification** (`verify_e2e.py`) runs the candidate's own tools rather than the workspace copy. It
  checks that the inputs and tools are byte-identical, and reports the validator's errors, the ledger roles,
  checkpoint integrity, whether blocked claims leaked into the draft (claim ids and sentinel phrases), and the
  effective gates.

## 3. Results

### 3.1 CORPUS (steps 1–2)
- 128 evidence items and 18 conflict pairs, each given a `quantity`, `conflicts_with` and `resolution`.
- The archived technical report was recognised as superseded: 10 of its 10 items are marked `superseded`.
- 0 validator errors and 0 role violations.
- Four blocking checkpoints were asked. They are real findings about the project:
  - **Q-001:** the cost headline is −23.84% (README and archive; its artifact is absent) vs −22.09% (the present n=50/N=10 artifact).
  - **Q-002:** "equal accuracy" vs the present artifact's 0.68–0.70 against 0.72; the "saturation" wording vs No-Memory EM 0.33.
  - **Q-003:** README results whose artifacts are absent from the package.
  - **Q-004:** "zero added labels" vs `labels_consumed = 10`.

### 3.2 AUTHOR draft (steps 3–17)
- **Claim map:** 38 claims (24 VERIFIED, 5 NEEDS_REVIEW, 9 BLOCKED) and 20 limitations. Every claim has
  `basis: project_file`.
- **Visuals:** 3 figures (two dot_ci, one line) and 2 tables. The data CSVs were derived from the project result
  files.
- **Draft v001:** 4,088 main-text words by the skill's counter (the limit is 4,500). It has 5 `[CITATION NEEDED]`
  markers (there is no source registry, and nothing was cited from memory) and 3 `[ASK AUTHOR]` markers.
- **Handling of the checkpoints:**
  - The paper uses only the cost result it can check (22.1% fewer tokens, CI 17.9–26.3%).
  - It reports accuracy as measured (A1 0.68–0.70 vs A0 0.72) and makes no "equal accuracy" statement.
  - It states that 10 labels were consumed.
- **Independent verification after the draft** (`verify_after_draft.json`):
  - Inputs and tools are unchanged.
  - Validator: 0 errors. The 44 warnings are 38 × author confirmation pending and 6 × measured claims backed only by
    soft evidence.
  - Ledger: 80 entries (CORPUS 7, AUTHOR 73) and 0 role violations. No answers were recorded, and all 3 accepted
    risks are `kind: workflow`.
  - All 9 claims blocked by checkpoints are BLOCKED. None is cited in the draft, and no sentinel phrase appears.
  - Effective gates: G1, G3 and V1–V4, V6 PASSED; V5 NOT_RUN (needs a person); G2 PENDING.
- **Self-reported tensions:**
  - The author added claim C031 ("the authors' reason is withheld pending an answer"), because S1/S2 required a
    BLOCKED author rationale to appear in the draft while `BLOCKED-claim-used` forbade it. This is a tool
    contradiction; see §3.5.
  - The author also carried the authors' own caveats about tests whose results are blocked.

### 3.3 REVIEW (step 18)
- **Isolation:** the reviewer (Opus) had Read/Write on one folder. Its prompt inlined `review_agent.md`, the two
  schemas and the packet (paper, audience, objective, 3 figures). It did not see `.rcs/`, the evidence or the claim map.
  `review_step.py collect` validated both outputs against their schemas (0 problems) and recorded them as REVIEW.
- **Reconstruction:**
  - All 12 questions were answered, none "cannot_determine", with confidence 3–5.
  - The headline (22.1%, CI), what the paper does not establish (Q9) and the limitations (Q11) match the evidence.
- **Diagnostics:** 26 findings over 20 dimensions, 11 inference issues and 5 objective discrepancies. No injected text
  was found.
  - Lowest scores: method 2 and figure/table 2.
  - Mean over dimensions (lowest score per dimension): 3.25.
  - There are 8 blocking findings (score ≤ 2, or a traceability/alignment/inference score below 4).
- **One finding exposed a real tool defect:**
  - In Figure 3 (a line chart), the value ticks and value label were drawn on the horizontal axis, which encodes
    step. So the figure read as "route@1 vs route@1".
  - None of V1–V6 caught it; V3 only checked bar lengths.
  - The fix and a renderer-independent check are described in §3.5.
- **Another finding is about the project, not the skill:** Table 2 shows ASMOS+RAG with exact match 0.625 above
  token-F1 0.433, which the reviewer calls impossible if both use the same predictions. The draft had already noted
  that the four-system metric definitions are undocumented (missing evidence M005/M006).
### 3.4 AUTHOR revise (steps 19–21) and G4
- **Dispositions:** there were 19 blocking items (8 findings and 11 inference issues). 18 were **fixed**, each with a
  location, and 1 was **deferred**: finding 4, "method mechanics missing", which only the authors can supply. The
  author turned it into a new checkpoint, Q-005, which blocks no claims, and put `[ASK AUTHOR]` markers at each gap.
  **G4 PASSED** (`g4_check`, 0 errors, bound to the diagnostics and dispositions hashes).
- **What changed was the substance, not only the wording:**
  - The ablation was narrowed to routing vs no routing, and its causal license was removed.
  - "Small accuracy cost" was replaced by "cannot be bounded" (1–2 of 50 questions per seed; the seeds are not
    independent).
  - The new-topic comparison became descriptive. The paper now discloses before the results that the thresholds
    differ and that labels were consumed on both sides.
  - Token accounting now states what it excludes.
  - Figure 3 was re-rendered with the fixed renderer.
  - The placeholder claim C031 was removed once the lint contradiction was fixed. The authors' reason now sits,
    withheld, on the BLOCKED claim C024.
- **Line edit:** `claim_invariance` from v002 to v003 shows 0 drift. The final manuscript `paper/paper.md` has
  4,368 prose words (the limit is 4,500). **Correction (2026-09-30):** that is a prose-only count. Counting headings
  and table text as well, it is 4,594, so it was already 94 words over. The skill's lint counted only prose, which is
  the defect the tier-3 A/B found (T-051). See §3.6.
- **Gates:** G1, G3, G4, V1–V4 and V6 are PASSED. V5 is NOT_RUN (a human review is needed). G2 is PENDING (it has no
  executable check).
- **G5 FAILED,** only because of 17 `marker` errors: 11 `[ASK AUTHOR]` and 6 `[CITATION NEEDED]`. That is the
  correct outcome for an unattended run. The skill refuses to call a manuscript final while it depends on facts only
  the authors have. The other G5 checks pass (validate, numbers, invariance).

### 3.5 Independent verification and defects found
- **Final verification** (`verify_final.json`):
  - Inputs and tools are unchanged (tools compared with the candidate after the logged mid-run swaps).
  - Validator: 0 errors.
  - Ledger: 136 entries (CORPUS 7, AUTHOR 125, REVIEW 4) and 0 role violations. No checkpoint answers exist.
  - Checkpoints Q-001 to Q-005 are open, and all 9 blocked claims are BLOCKED and absent from the manuscript.
  - One sentinel hit needs a person to read it: "the token saving is not a saving at equal accuracy". It states the
    *measured* contrary of the blocked claim C023 (the recorded accuracy is lower in every seed), not the blocked claim
    itself. Whether the authors want that sentence depends on their answer to Q-002.
- **Five skill defects that only a real run exposed.** Each was fixed with a regression test and synced into the
  workspace between roles; the swaps are logged with hashes in `MIDRUN_TOOL_CHANGES.jsonl`.
  | # | defect | found by | fix | test |
  |---|---|---|---|---|
  | 1 | `workflow_guard.record` crashed on the final manuscript (outside `.rcs`) | orchestrator reading the revise task | `../paper/` allowed for AUTHOR; any other outside path is a ROLE_VIOLATION | T-047 |
  | 2 | the review packet omitted linked figures (the author copied them in later, unhashed) | orchestrator inspecting the packet | the builder copies, sanitizes and hashes linked figures | T-048 |
  | 3 | S1/S2 required a BLOCKED author statement in the draft; `BLOCKED-claim-used` forbade it | AUTHOR (self-reported) | `S1/S2-author-statement-withheld` (WARN) | T-049 |
  | 4 | **line charts drew the value axis horizontally**; no V gate noticed | **blind reviewer** (finding 18) | vertical value axis + `x_label`; new renderer-independent `V3_AXIS_ENCODING` | T-050 (real figure) |
  | 5 | the gate runner ran G1 before G3/V reports were refreshed, so the first run after an edit failed G1 | AUTHOR (revise) | G1 runs after G3/V/G4, before G5 | T-045 |

### 3.6 Human answers applied, and a second review round (2026-09-30)
- **Answers.** The project owner answered Q-001, Q-002 and Q-004 in chat. The answers were recorded with
  `workflow_guard.py answer --by`, and no agent answered. An AUTHOR agent applied them through the claim map:
  - C020, C021, C023 and C024 were rejected;
  - C001 and C007 were confirmed;
  - C022 was narrowed to "zero retraining" and confirmed, with `labels_consumed = 10` stated;
  - the paper changed by one sentence, and invariance reported only that addition.

  This was the first real exercise of the answer -> claim path. It exposed two defects, both fixed:
  - G4 did not notice a claim added after the review (now STALE, T-059);
  - the lint called rejected statements "withheld" (T-060).
- **Length.** Under the corrected count (T-051) the paper was 4,620 words. The AUTHOR relocated supplementary text to
  the appendix to reach 4,497 (v005), with 0 invariance errors.
- **Round-2 blind review (step 20)** ran through the model-agnostic tool (`rce_roles.py review`, `manual` provider: the
  tool wrote the prompt, a separate reader answered it, and the tool validated and recorded the reply).
  - It was valid on the first attempt.
  - Mean dimension score went from 3.25 to 3.5. Blocking findings fell from 8 to 2, and inference issues from 11 to 8.
  - AUTHOR dispositions: 7 fixed and 3 deferred (behind Q-003/Q-005). v006 is 4,487 words (all-count) and the final
    is 4,365.
  - Defects found and fixed along the way:
    - G4 resolved relative reviewer-log paths against the cwd, a false `G4_ISOLATION` (T-055);
    - marker stripping left stray spaces (T-061);
    - a bare `[CITATION NEEDED]` passed G5 unseen (T-061).
- **Final state** (`verify_after_answers.json`):
  - integrity: inputs and tools unchanged; 0 validator errors; 199 ledger entries (CORPUS 7, AUTHOR 184, REVIEW 8);
    0 role violations;
  - checkpoints: only Q-003 and Q-005 are open, and their blocked claims are absent;
  - gates: G1, G3, **G4 (round 2, covering every claim)**, V1-V4 and V6 PASSED; G5 FAILED only on the 17
    author-only markers.
- **Workspace:** the runnable workspace is kept outside the public repository at
  `research_skill/ASMOS_rce_workspace/`, with the owner's remaining steps in `YOUR_STEPS.md`.

## 4. What this shows, and limitations
- **Shown (process level):**
  - Separate role agents can run the workflow on a real, messy evidence package.
  - A stale archived report was recognised.
  - Four genuine inconsistencies in the project were raised as checkpoints rather than resolved by guesswork.
  - No blocked fact reached the paper.
  - The blind review changed the paper's substance.
  - Every gate status is backed by a tool report in `RUN_LOG.jsonl`.
  - The run found 5 tool defects that 78 unit tests and 49 replay fixtures had missed. That is the main argument for
    running end-to-end tests at all.
- **Not shown:**
  - Reader benefit: there is one project, one run and no comparison arm.
  - Reviewer calibration: the perturbation calibration in `review_agent.md` was not re-run for this reviewer.
  - Human-side behaviour: nobody answered a checkpoint, so the path from answer to restored claim was exercised only
    in unit tests (T-043), not on this project.
- **Integrity caveats:**
  - Tools changed mid-run (5 files, 6 swaps, all logged). Draft v001 was written with the old lint, packet builder
    and renderer.
  - The orchestrator records the REVIEW role's ledger entries. The ledger attests which role produced a file, not
    which process wrote the bytes.
  - The separation between roles is instruction-level. Agents had shell access inside the workspace, and the
    hash checks detect tampering with inputs or tools but do not prevent it.
- **Data note:** `run/` contains content derived from the user's ASMOS project (evidence summaries, draft and final
  paper). Whether to commit it is the user's decision.
