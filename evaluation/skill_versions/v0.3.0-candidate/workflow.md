# Workflow

21 steps in five phases. Each step lists **Role · Input · Do · Output · Done when · Failure
states**. Artifacts live in `<project_root>/.rcs/` (layout: `examples/project_layout.md`).
Record progress in `.rcs/state.json`:
`{"step": 7, "gates": {"G1": "passed", ...}, "length_limit_words": 4500, "open_failures": [...],
"accepted_risks": [...]}`.
A gate value is `"passed"` only when the tool report it requires exists under
`.rcs/audits/gates/` with 0 errors (see `SKILL.md`, "Gates are executable"). Otherwise it is
`"pending"` or `"unverified"`. `tools/validate_artifacts.py .rcs` checks this.

You can resume at any step by reading `state.json` and the artifacts. Never reconstruct state
from memory.

---

## PHASE 1 — PLAN: EVIDENCE

### Step 1 — Inspect project
- **v0.3:** set `"guardrail": "v0.3"` in `state.json` (G3/G5 then also need the numbers and invariance reports).
- **Role:** CORPUS_AGENT (mode=`evidence`)
- **Input:** `project_root`
- **Do:** walk the tree. Classify each file (result, log, config, code, figure, figure-source,
  note, draft, review, reference, dataset, other). Record size and modification time. Extract
  text from PDFs, notebooks, and docx. Don't open datasets larger than the budget; describe
  them instead (schema, row count).
- **Output:** `evidence/project_inventory.json`
- **Done when:** every file is classified or explicitly skipped with a reason.
- **Failure:** `NO_EVIDENCE` if there are no result-bearing files.

### Step 2 — Build the evidence map
- **Role:** CORPUS_AGENT
- **Do:** create evidence items `E###` (see `evidence_model.md` §1): results with verbatim
  values, units, conditions, n/seeds/variance; experiments; datasets; baselines; metrics;
  observations; **negative/failed results**; limitations the authors noted
  (`limitation_noted`, verbatim, one item each, broad ones included); the authors' stated
  motivation and design reasons (`rationale_stated`, verbatim); assumptions; hypotheses; method
  details. Detect conflicts. List missing evidence (e.g. a table with no
  variance, a baseline mentioned but never run, a figure with no data source).
- **Output:** `evidence/research_evidence.json`, `evidence/missing_evidence.json`,
  `claims/claim_candidates.json`, `plan/audience_assumptions.json`
- **Done when:** `tools/validate_artifacts.py` passes, every locator resolves, and a 20% numeric
  spot-check (min 10) matches the source.
- **Failure:** `CONFLICTING_EVIDENCE`, `MISSING_RESULT`.

### Step 3 — Build the Research Story Graph and Spine
- **Role:** AUTHOR
- **Input:** evidence map, claim candidates, the user's stated contribution (if any)
- **Do:**
  1. Draft the **spine** (`research_story.md` §1): 7 lines, each ≤2 sentences.
  2. Build the **story graph** (`research_story.md` §2), with nodes bound to evidence.
  3. Build an **experiment narrative chain** for each experiment (`research_story.md` §3). An
     experiment that can't be attached to a research question is flagged `ORPHAN_EXPERIMENT`:
     ask whether it belongs in the paper.
  4. Run the **contribution test**: can you state the contribution as an answer to the gap,
     supported by a RESULT node? If not, raise `CONTRIBUTION_UNCLEAR` and run contribution
     elicitation (`failure_states.md`).
- **Output:** `story/spine.md`, `story/story_graph.json`
- **Failure:** `CONTRIBUTION_UNCLEAR` (STOP), `AMBIGUOUS_CLAIM`.

### Step 4 — Build the Claim–Evidence Graph
- **v0.3 Stage 4:** confirmation questions for G1 go through `tools/workflow_guard.py ask` (claims they block stay `BLOCKED` until a person answers with `answer --by <name>`); unattended runs record `accepted_risks` of `kind: workflow` only.
- **Role:** AUTHOR
- **Do:** promote claim candidates into claims `C###`. For each one: statement, `claim_type`,
  evidence IDs, `confidence` (derived by the rules in `evidence_model.md` §4), scope conditions,
  limitation links, `permitted_verbs`, `author_confirmation` (`confirmed` if the claim appears in
  author-written notes, otherwise `pending`). Attach each negative result to the claims it
  bears on.
- **Attribution:** create one limitation `L###` with `origin: author_stated` for every
  `limitation_noted` item. Attach it to the claims it bounds, or to the central claim if it is
  broad. Limitations you infer get `origin: writer_derived`. Create one claim with
  `rationale: motivation | design_choice` and `origin: author_stated` for every
  `rationale_stated` item.
- **Output:** `claims/claim_evidence_map.json`
- **Gate G1:** every spine line references ≥1 claim. Every claim has ≥1 evidence ID or is typed
  `hypothesis`/`speculation`/`future`. No open STOP-class failure. **Executable:**
  `python tools/validate_artifacts.py .rcs --out .rcs/audits/gates/G1_validate.json` reports 0
  errors (schemas, IDs, locators, spine binding, attribution). **Show the spine and the claim
  list to the user and get confirmation of the pending claims.** This is the cheapest point to
  catch a misunderstanding.

---

## PHASE 2 — PLAN: CONTEXT

### Step 5 — Identify the audience
- **Role:** AUTHOR (+ user)
- **Do:** fill `plan/audience_profile.json` (`audience_model.md`): primary, secondary, and
  tertiary tiers; mode A–E; assumed knowledge (a list of concepts the reader already knows);
  term budget; binding personas for evaluation.
- **Failure:** `UNCLEAR_AUDIENCE` (STOP before step 8).

### Step 6 — Identify the venue requirements
- **Role:** AUTHOR (CORPUS_AGENT fetches if a URL or name is given)
- **Do:** fill `plan/venue_profile.yaml` from official guidelines only (template:
  `templates/venue_profile.yaml`): section template, limits, citation style, voice preference,
  required statements, checklists, reporting guideline (EQUATOR etc.), AI-use policy. Record
  source URLs and dates.
- **Failure:** `VENUE_UNKNOWN`. Use `templates/venue_profile.generic.yaml` and mark every rule
  `assumed: true`.

### Step 7 — Collect literature and exemplars
- **Role:** CORPUS_AGENT (mode=`literature`, then `patterns`)
- **Input:** story hints: RQ, method family, datasets, metrics (from the story graph).
  **Don't** send skill rules.
- **Do:** follow `docs/02_RESEARCH_CORPUS_STRATEGY.md` §2. Output a verified source registry,
  a literature map organized by **dimensions** (`citation_rules.md` §4), writing patterns, and
  anti-patterns.
- **Output:** `corpus/source_registry.json`, `corpus/literature_map.json`,
  `corpus/writing_patterns.json`, `corpus/anti_patterns.json`, `corpus/corpus_log.md`
- **Failure:** `INSUFFICIENT_LITERATURE`, `UNVERIFIED_CITATION`.
- **Then (AUTHOR):** build the **Literature → Gap → Question chain** (`citation_rules.md` §5).
  If the chain doesn't hold, the gap statement in the spine must be narrowed. Update step 3
  artifacts and note the change in `state.json`.

### Step 8 — Construct the paper architecture
- **Role:** AUTHOR
- **Do:** map the story graph onto the venue's section template (`templates/paper_architecture.md`).
  For **each paragraph slot**: section · story node(s) · reader question answered · claims ·
  density class · figures/tables used · the term(s) introduced · planned words. Complete a
  **figure/table card** for each planned visual (`figure_table_rules.md` §1). Assign each
  density-class SUPPLEMENTARY item a destination.
- **Output:** `plan/paper_architecture.md`, `plan/figure_cards/*.md`
- **Checks:** every story-graph node has a slot. Every RQ has results, interpretation, and
  discussion slots. Every `author_stated` limitation has a Limitations slot, and every rationale
  claim has an Introduction (motivation) or Introduction/Method (design choice) slot. Planned
  words sum to ≤ 90% of `length_limit_words`. The question ledger shows no planned debt. The term ledger shows no planned
  use-before-definition.

### Step 9 — Write the research skeleton
- **Role:** AUTHOR
- **Do:** write one sentence per paragraph slot (its topic sentence, the paragraph's point),
  with claim tags. Read the skeleton alone from top to bottom. **It must read as the complete
  argument in miniature.** If it doesn't, fix the architecture, not the sentences.
- **Output:** `plan/skeleton.md`
- **Gate G2:** skeleton self-reconstruction: answer Q1–Q12 (`evaluation_rubric.md` §1) from the
  skeleton only. All 12 must be answerable. Otherwise return to step 8.

---

## PHASE 3 — DRAFT

### Step 10 — Draft section by section
- **Role:** AUTHOR
- **Order:** Results → Methods/Experimental setup → Discussion (incl. Limitations) → Related
  work → Introduction → Conclusion → Abstract → Title. The introduction is written after you
  know exactly what it must prepare the reader for. The abstract and title come last because
  they compress a finished argument.
- **For each section:** load its contract (`section_rules.md`) and the paragraph model
  (`information_design.md` §1). Expand each skeleton sentence into a paragraph. Keep claim tags.
  Use visible markers for gaps. After the section, run its **contract self-check** and update
  the ledgers.
- **Output:** `drafts/vNNN/<section>.md` and `drafts/vNNN/paper.md` (assembled)
- **Gate G3:** all `{C###}` tags resolve and all contracts pass. **Executable:**
  `python tools/lint_draft.py drafts/vNNN/paper.md --rcs .rcs --out .rcs/audits/gates/G3_lint.json`
  reports 0 errors. This includes `S1-author-limitation-missing` and
  `S2-author-rationale-missing`.

---

## PHASE 4 — REVISE (structure before style)

Run the audits in this order. Each writes to `audits/vNNN/`. Fix structural defects before
moving to the next audit if they would change what that audit sees.

### Step 11 — Reader reconstruction self-test
- **v0.3 Stage 3:** also run `tools/audit_reader.py` against `.rcs/plan/reader_model.json`, and `tools/skim_layer.py build` then `check` on the abstract and skim sheet.
- **Role:** AUTHOR, in a *fresh context* if the runtime allows, with only `paper.md` (tags
  stripped).
- **Do:** answer Q1–Q12 from the draft alone and compare with the spine and claim map. Every
  mismatch goes into `audits/vNNN/reconstruction_self.md` with its location.
- **Note:** this is a cheap pre-screen. It does **not** replace step 18.

### Step 12 — Evidence/claim audit
- **v0.3:** run `tools/verify_numbers.py` (every number traced; no inferred p-values) and resolve every `UNLICENSED-*` lint finding by downgrading the wording or adding licensed evidence.
- Every claim-like sentence is tagged (the lint finds orphans: numbers, comparatives, causal
  verbs, "we show").
- Every number matches its evidence value (after declared rounding). Re-read it from the
  source.
- Claim types match their verbs. Negative-result coverage is complete.
- **Failure:** `OVERCLAIM`, `SELECTIVE_REPORTING`, `MISSING_RESULT`.

### Step 13 — Logical-flow audit
- **Paragraph level:** each paragraph passes the paragraph model (role, point first, evidence,
  link-back, link-forward).
- **Section level:** the introduction ends with the RQ, the contributions, and a paper map.
  Each results subsection opens with the RQ it answers. The discussion answers every RQ.
- **Transitions:** every connective ("however", "therefore", "moreover") names a relation that
  actually holds between the two claims. Delete connectives that assert false relations.
- Old→new flow (`information_design.md` §4).

### Step 14 — Terminology / cognitive-load audit
- Term ledger: no use before definition, no synonyms for registered terms, acronyms justified.
- ≤2 new technical concepts per paragraph for modes B–E (for mode A, count only project-specific
  terms).
- Sentences > 35 words are reviewed: split them, or keep them with a reason.
- Information density: DISTRACTING content is removed. SUPPLEMENTARY content is moved and
  pointed to.

### Step 15 — Figure/table audit
- **v0.3 Stage 2:** `tools/plan_visuals.py` (step 8-9 planning), `tools/visuals.py render`, then `tools/validate_visuals.py --draft --out .rcs/audits/gates/V_visuals.json`; record V1-V4/V6 as passed only from that report; V5 only with a human review (`figure_table_rules.md` §9).
- **v0.3:** cards must pass the fail-closed checks in `figure_table_rules.md` §8 (`NO_VALID_VISUAL`, `UNTRACED_COMPONENT`, `BLOCKED_PERMISSION`).
- Every visual has a complete card, is referenced in the text *before* it appears, has its
  takeaway stated in the prose, and passes the honesty and accessibility checks
  (`figure_table_rules.md` §4–5).
- **Failure:** `FIGURE_NOT_EXPLAINED`.

### Step 16 — Citation audit
- **v0.3:** titles stay `as_cited` unless verified by lookup (`citation_rules.md` §8).
- Run `citation_rules.md` §2 for every citation: exists → metadata → support quote → strength →
  primary source.
- No citation is decorative. Each sentence with a citation states what the source contributes.
- **Failure:** `UNVERIFIED_CITATION`.

### Step 17 — Scientific overclaim audit
- Run the anti-hype layer (`anti_patterns.md` §B). Lint the high-risk vocabulary.
- For each flag: **downgrade the language or flag it to the user. Never strengthen the evidence
  or search for support after the fact.**
- Check generalization scope: population, dataset, scale, and conditions in the claim vs the
  evidence.

### Step 18 — Blind audience evaluation
- **Any model:** `python tools/build_review_packet.py <draft> --out .rcs/packets/review_<round> ... --strip-markers`, then
  `python tools/rce_roles.py review --rcs .rcs --round <round>` (REVIEW_AGENT bound in `.rcs/models.json`; only the
  packet is sent). A runtime subagent that sees only the packet is equivalent.
- **v0.3 Stage 3:** for a measured result, use `tools/comprehension_kit.py` (a frozen key, visual-only vs full packets, two blind graders, α). Human sessions follow `templates/human_study_protocol.md`; LLM-proxy results are labelled as proxy.
- **Role:** REVIEW_AGENT (isolated; `agents/review_agent.md`)
- **Do:** build the packet (`tools/build_review_packet.py`), run the reviewer, and validate
  `diagnostics.json` and `reconstruction.json`.
- If a gold story exists, grade reconstruction with RECON_GRADER (`agents/recon_grader.md`).
  Otherwise compare with the spine and claim map yourself and label the result `provisional`.

### Step 19 — Revise
- **v0.3 Stage 4:** record a disposition for every blocking finding and inference issue in `.rcs/revisions/<round>/dispositions.json` (`fixed` + `where` | `declined` + `reason` | `deferred` + `open_issues.md` entry), then `python tools/g4_check.py .rcs --round <round> --revised <new draft> --out .rcs/audits/gates/G4_review.json`.
- Sort defects: blocking (any dimension ≤2, distortion, orphan claims, open failure states) →
  structural → local.
- Fix with the **revision principle** in each diagnostic. Where a diagnostic points to missing
  evidence, raise a failure state. Don't patch it with prose.
- **Fix structure in the artifacts first** (architecture, story graph), then regenerate the
  affected paragraphs. Don't patch symptoms sentence by sentence.
- Save as `drafts/v(NNN+1)/`.

### Step 20 — Repeat evaluation
- Return to step 11 (audits) and 18 (review) with a **new packet and a fresh reviewer
  context**.
- **Stop** when the exit criteria (`evaluation_rubric.md` §4) hold, or after 3 review rounds.
  At the cap, stop and put the remaining defects in `open_issues.md`. Don't keep iterating
  toward a score.

---

## PHASE 5 — EDIT

### Step 21 — Final language editing
- **v0.3:** before stripping tags, run `tools/claim_invariance.py <pre-edit tagged draft> <edited tagged draft> --out .rcs/audits/gates/G5_invariance.json`; any `CLAIM_DRIFT_*` is reverted.
- **Gate in:** G4 passed (or the user explicitly accepted the remaining issues).
- **Do:** line-level edit (the course's Phase 4). Grammar, word choice, concision, units and
  number formatting, consistent headings, citation style per the venue, figure/table numbering
  and cross-references. Voice per the venue profile (active voice is the default; S31).
- **Length gate:** if the main text exceeds `length_limit_words` (the lint's `S4-over-length`),
  relocate SUPPLEMENTARY paragraphs, secondary detail, and full tables to the appendix or
  supplement with a main-text pointer, and remove repetition. Never remove claims, negative
  results, `author_stated` limitations, or rationale claims to fit. If the text still doesn't
  fit, raise `LENGTH_EXCEEDED` and ask the user what to move.
- **Claim-invariance check:** re-extract claims from the edited text and compare them with the
  claim map (statements, types, scope, and verbs). Any change is `CLAIM_DRIFT`. Revert that
  edit.
- Strip tags. Write the markers that remain into `open_issues.md`. **A paper with unresolved
  `[MISSING …]` markers is a draft, not a final paper. Say so.**
- Draft `disclosure.md` per the venue's AI policy.
- **Gate G5:** the claim map is unchanged and the text is within the length limit.
  **Executable:** `validate_artifacts.py .rcs --out .rcs/audits/gates/G5_validate.json` and
  `lint_draft.py paper/paper.md --rcs .rcs --final --out .rcs/audits/gates/G5_lint.json` both
  report 0 errors. Then `validate_artifacts.py .rcs` (which re-checks every gate marked passed)
  reports 0 errors.

---

## Shortcuts (allowed, with explicit labeling)

| Situation | Allowed shortcut | Must still do |
|-----------|------------------|---------------|
| User wants only a restructure of an existing draft | Start at step 2 using the draft as a Level-0 communication artifact, and the data files as evidence | Steps 3–4, 8–9, all audits |
| User wants only a review | Steps 2 (light), 11–18; output diagnostics | Don't rewrite |
| No subagent support | Run the roles sequentially in fresh sessions with packet directories | Label the review `isolation: none` if it runs in the same context |
| Very small paper (workshop, 4 pages) | Merge steps 8–9 | Spine, claim map, RIC, citation audit |

No shortcut may skip: the claim map, the citation verification, the overclaim audit, or the
marking of missing evidence.
