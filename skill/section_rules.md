# Section Rules

Each section has a different job. There is no generic "academic writing" rule. A **section
contract** says: *Job · Reader questions answered · Must contain · Must not contain · Entry
condition · Exit check*. Venue profiles may rename, merge, or reorder sections. Contracts
follow the *function*, whatever the heading.

Division of labor (never let these collapse into each other):
**Introduction = orientation · Methods = reproducibility · Results = evidence ·
Discussion = interpretation · Conclusion = synthesis.**

---

## TITLE
- **Job:** a truthful promise about subject and finding or purpose (F0 Unit 3: "the title is a
  promise").
- **Must:** contain the key subject terms a searcher would use. State the finding if it's a
  single robust claim ("X reduces Y under Z") or the question if it isn't.
- **Must not:** claim more than the spine lines 5–7 allow; use undefined acronyms; use cute
  titles that hide the subject (a subtitle can carry the subject if the venue tolerates wit).
- **Exit check:** paraphrase test. A reader can restate the title as "this paper shows/asks
  that …", and the restatement matches spine line 3 or 5.

## ABSTRACT
- **Job:** a stand-alone miniature of the spine for the tertiary reader.
- **Structure (default, adapt to the venue):** context (1) → gap (1) → question/objective (1) →
  approach (1–2) → key results *with magnitudes* (1–2) → meaning (1) → main limitation or scope
  (≤1, if the venue allows).
- **Must:** use only claims with confidence ≥ moderate, or hedged ones. Include every number
  exactly as in the claim map. State the scope.
- **Must not:** introduce terms not defined in it; cite (unless the venue permits); include
  claims absent from the body; use "novel", "first", or "SOTA" unless the claim map licenses
  them.
- **Exit check:** abstract-only reconstruction gives correct Q1, Q3, Q4, Q7, and Q10 with no
  overstatement.

## INTRODUCTION: orientation
- **Job:** prepare the reader to understand the contribution. Nothing more.
- **Reader questions:** What is the problem? Why care? What's missing? What do you ask? What did
  you do? What did you find? Where is it in the paper?
- **Default move sequence** (CONTEXT → PROBLEM → GAP → QUESTION → APPROACH → CONTRIBUTION →
  PAPER MAP):
  1. Context and problem, at the primary audience's level (1–2 paragraphs).
  2. What is known and where it fails: the **gap**, derived from the lit→gap chain, with
     citations (1–2 paragraphs).
  3. The question or objective, explicitly stated. **It must appear within the first ~25% of
     the introduction's paragraphs or be clearly foreshadowed there.**
  4. The approach in one idea, with the design rationale in one sentence.
  5. The contributions: each is an answer to the gap, carries a result reference, and is phrased
     at its claim strength. Use a numbered list if there are ≥2 contributions.
  6. The paper map, by questions.
- **Must not:** give method detail beyond what's needed to understand the contribution; use
  terms that are defined only later; bury the contribution after related work; present a
  literature survey (that belongs in Related Work).
- **Entry condition:** the Results and Discussion drafts exist (write the introduction late).
- **Exit check:** first-read reconstruction (`audience_model.md` §4). Question debt ≤3 with
  explicit forward pointers.

## RELATED WORK / LITERATURE REVIEW
- **Job:** show the logical necessity of the research question. See `citation_rules.md` §4–5.
- **Organize by dimensions** (problem framing, method family, assumptions, datasets and
  evaluation, unresolved contradictions), **not by paper**.
- Each subsection's shape: *what this line of work achieves* → *its shared assumption or
  limitation* → *how this paper relates* (differs, builds, or tests).
- **Must not:** "A did X. B did Y. C did Z." sequences (≥3 consecutive sentences of that form
  fail the lint); citation lists with no stated contribution; unqualified "no prior work";
  strawmanning.
- **Placement** (venue-dependent): after the introduction, or before the conclusion if the
  introduction's gap paragraph already carries the necessary literature.
- **Exit check:** every GAP node is supported by the lit→gap chain. Every cited work's role is
  stated.

## METHODOLOGY: reproducibility
- **Job:** let a competent reader understand and reproduce what was done, and why each key
  choice was made.
- **Must:** describe the study design; data (source, size, splits, preprocessing, licenses,
  ethics approvals if relevant); the method (intuition → formal statement); baselines and **how
  they were tuned** (budget parity); metrics (definition, and why they fit the RQ); statistical
  procedures (runs/seeds, what the error bars represent, tests, multiple-comparison handling);
  implementation details needed for reproduction (the rest goes to the supplement); code/data
  availability; and the domain reporting-guideline items from the venue profile.
- **Design rationale:** for each non-obvious choice, one clause of *why* (Q5). Where the choice
  was arbitrary, say so. Don't invent a rationale. If none is recorded, `[ASK AUTHOR: rationale
  for …]`.
- **Must not:** report results; evaluate the method ("our elegant approach"); leave the actor
  ambiguous.
- **Exit check:** a reproducibility checklist derived from the evidence map. Every
  `method_detail` and `implementation_detail` item is placed (main or supplement).

## EXPERIMENTAL SETUP
(A separate section in many CS venues; otherwise part of Methods.)
- **Job:** connect each experiment to its RQ and hypothesis *before* any result is shown.
- **Must:** give a table or paragraph per experiment: RQ · hypothesis/falsifier · data ·
  comparison · metric · runs. This is the experiment narrative chain, minus results.

## RESULTS: evidence
- **Job:** present what was found, organized by research question, each result interpreted
  enough to be understood.
- **Organize** by RQ/experiment chain, in narrative order (`research_story.md` §3). Each
  subsection opens with the question it answers.
- **Result Interpretation Chain (RIC), for every major result:**
  1. **What was measured?** (metric, condition, comparison), briefly, pointing back to Setup
  2. **What happened?** (direction), with the key number(s)
  3. **How large is the effect?** (absolute and relative; against a meaningful reference:
     baseline, noise level, practical threshold)
  4. **Is it robust?** (variance across seeds/runs, CI or test, consistency across
     datasets/conditions, sensitivity)
  5. **What does it mean?** (a first-order interpretation at the correct claim strength)
  6. **How does it relate to the RQ?** (explicitly: "This answers RQ2 affirmatively for …")
  7. **What can we NOT conclude?** (scope limits, confounds not ruled out, conditions not tested)
  Steps 5–7 can be brief here and expanded in the Discussion. Venues with strict IMRaD
  separation keep only a one-clause version of step 5 and move the rest to the Discussion. The
  RIC must still be complete across the two sections.
- **Must:** include all results that bear on the claims, including negative ones; introduce
  every table/figure with its takeaway before or as the reader meets it.
- **Must not:** dump numbers (≥3 consecutive numeric sentences with no interpretive clause fail
  the lint); claim significance without a test; report only the metrics that favor the method
  when others were computed.
- **Exit check:** every RQ gets ≥1 result paragraph. Every major result has RIC steps 1–4 here
  and steps 5–7 here or in the Discussion.

## DISCUSSION: interpretation
- **Job:** say what the results mean for the question, the field, and practice, and how far
  that meaning extends.
- **Default structure:**
  1. The answer to each RQ, in one or two sentences each (mirrors the introduction's questions;
     F0 Unit 4: "Discussion and introduction are a pair").
  2. Interpretation and mechanism: why the results came out this way. Alternatives considered.
     Claim types `interpretation`/`speculation` clearly marked.
  3. Relation to prior work: agrees, disagrees, or extends, with the reason for any
     disagreement.
  4. Implications: for practice or theory, bounded by scope.
  5. Limitations (below).
- **Must not:** introduce new results (unless the venue merges R&D, in which case label them);
  repeat the results; turn speculation into findings.
- **Exit check:** every INTERPRETATION node → RQ edge is realized in the text.

## LIMITATIONS
- **Job:** tell the reader exactly which claims are bounded and how.
- **Must:** give each limitation as a triple: *limitation → which claim(s) it affects → effect
  on interpretation* (and, where possible, what would resolve it). Order by impact on the main
  claim. Include the scope boundaries from the claim map (datasets, scales, populations,
  conditions).
- **Must not:** give generic limitations ("more data would help") that are unattached to claims;
  pre-empt reviewers with trivial limitations while omitting serious ones (S21 notes that
  disclosed limitations sway LLM reviewers; the reverse strategy, hiding real ones, is
  forbidden); contradict claims stated elsewhere without revising those claims.
- **Exit check:** every LIMITATION node is linked. The main limitation matches spine line 7.

## CONCLUSION: synthesis
- **Job:** state what is now understood that wasn't before, and what follows. Don't repeat the
  abstract.
- **Must:** give the central finding at its claim strength; what it changes (spine line 6); the
  key boundary; one or two concrete next questions (FUTURE nodes).
- **Must not:** introduce new results or citations; add claims absent from the claim map;
  copy the abstract (lint flags >40% sentence overlap with the abstract).

## REFERENCES
- Only verified sources from the registry. Style from the venue profile. Every entry is cited
  in the text, and every in-text citation has an entry. No reference was added "for
  completeness" without being read.

## APPENDIX
- **Job:** hold SUPPLEMENTARY material that the main text points to. Each appendix section
  opens with a one-line statement of which main-text claim or method it supports.
- **Must not:** contain results that change the main conclusions without the main text saying so.

## SUPPLEMENTARY MATERIAL
- **Job:** complete reproducibility: full hyperparameters, extra runs, full tables, data
  statements, code pointers, and prompts/checkpoints where relevant.
- **Must:** use a stable structure and cross-reference IDs from the main text.

## REQUIRED STATEMENTS (venue-injected)
Data/code availability, ethics, conflicts of interest, funding, author contributions, AI-use
disclosure (S14–S17), and reporting checklists (e.g. S18, S19). They are generated from the
evidence map and user input only. Never assert that an approval, license, or data release
exists without evidence. Use `[ASK AUTHOR: …]`.
