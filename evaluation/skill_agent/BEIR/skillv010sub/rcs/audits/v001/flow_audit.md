# Step 13 — Logical-flow audit

## Paragraph level
Each paragraph was checked against the paragraph model (information_design.md §1): point first
or second sentence, evidence in the middle, a link back to the previous point, a link forward.
Sampled in full for Sections 5-7 (the highest-density sections); spot-checked elsewhere. No
paragraph's point appears only in its last sentence outside the two narrative build-up spots
that are intentional (Introduction para 1, which builds context before the problem statement, and
Section 6 para 1, which builds the pooling mechanism before naming the risk it creates for
Section 5 -- both are deliberate context-before-point openings, matching information_design.md's
"CONTEXT first in the introduction's opening paragraph" exception).

## Section level
- Introduction ends with the RQ (implicit in the contributions + paper-map paragraphs) and a paper
  map by section/question. **Pass.**
- Each Results subsection opens with the question it answers: Section 5 opens by restating RQ1;
  Section 6 opens by questioning whether Section 5's comparison is itself distorted (RQ2). **Pass.**
- Discussion answers every RQ explicitly, one paragraph per question, before turning to
  implications. **Pass** (Section 7 paras 1-2).

## Transitions
Every connective was checked for a real relation:
- "however"/"but" (Section 5 "It still loses to the weaker-on-average ANCE..."; Section 6 "It does
  not overturn Section 5's overall ranking... But it is a correction to..."): each introduces a
  genuine contrast between an average pattern and a specific exception. **True.**
- "because" (Section 5, docT5query's vocabulary explanation; Section 7, causal-language hedge
  about TAS-B/ANCE): each names the actual mechanism argued in the source, not a decorative link.
  **True.**
- No "Moreover/Furthermore/Additionally" chains are used anywhere in the draft (checked via
  `lint_draft.py`'s `A15-decorative-transitions` signature; 0 instances, well under the 3-per-1000-
  words threshold). **Pass.**

## Old -> new information flow
Checked the RQ1 results sequence (Section 5): each paragraph's opening topic returns to the
previous paragraph's closing idea (best generalizers -> their cost -> the opposite group's poor
generalization -> the two exceptions to that group's trend -> what explains the overall pattern).
Key nouns are repeated rather than varied ("generalize" / "zero-shot" / "BM25" used consistently;
no synonym drift such as switching between "OOD" and "out-of-distribution" and "domain shift" for
the same idea -- checked against `story/term_ledger.json`). **Pass.**

## Result: no structural defects requiring a return to plan/paper_architecture.md.
