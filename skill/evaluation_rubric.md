# Evaluation Rubric

Public part of the evaluation. AUTHOR and SKILL_AGENT may read it. REVIEW_AGENT's calibration
items and prompt wording live in `agents/review_agent.md` and are not shown to them. The full
protocol and metrics are in `docs/04_EVALUATION_FRAMEWORK.md`.

---

## 1. Reconstruction questions (answered from the paper alone)

Q1 What problem is this paper solving?
Q2 Why does this problem matter?
Q3 What is missing from existing approaches?
Q4 What exactly did the authors do?
Q5 Why did they choose this method?
Q6 What experiments were performed?
Q7 What are the strongest results?
Q8 What do those results actually establish?
Q9 What do they NOT establish?
Q10 What is the primary contribution?
Q11 What are the main limitations?
Q12 What should the reader remember one day later?

Answers cite paper locations. "Cannot determine" is valid.
Grading against the gold story: present / weakened / overstated / contradicted / absent, plus
intrusions. **Distortion (overstated or contradicted) is the most serious outcome.**

---

## 2. Twenty dimensions with anchors (0–5)

General anchors: **0** absent or incomprehensible · **1** seriously deficient (most readers of
the binding personas would be misled or lost) · **2** weak (the reader gets there only with
effort or guesswork) · **3** acceptable (understandable, with notable friction) · **4** strong
(clear, minor friction) · **5** excellent (effortless for the binding personas and precisely
scoped).

Specific anchors (what 1, 3, and 5 look like):

| # | Dimension | 1 | 3 | 5 |
|---|-----------|---|---|---|
| 1 | Problem | Problem must be inferred from methods | Stated, but abstract or late | Concrete problem, for whom, on page 1 |
| 2 | Motivation | No reason given, or a generic "important area" | A reason given, not tied to a consequence | A specific consequence of the problem, evidenced |
| 3 | Research question | No explicit question/objective | Stated, but vague or late | Explicit, early, answerable, echoed in results and discussion |
| 4 | Contribution | Can't identify what is new | Listed, but as features or unlinked to results | Each contribution = answer to the gap + pointer to the evidence |
| 5 | Method | Can't tell what was done | Understandable to an expert only | Intuition, then specifics; rationale for key choices |
| 6 | Experiments | Experiments listed without purpose | Purpose inferable | Each experiment tied to an RQ/hypothesis, with the falsifier stated |
| 7 | Results | Numbers without direction or reference | Direction clear; magnitude or robustness partial | Direction, magnitude against a reference, robustness, all clear |
| 8 | Interpretation | None, or contradicts the data | Present, but loosely tied to the RQ | Explicit answer to each RQ at the correct strength |
| 9 | Limitations | Absent or boilerplate | Present, weakly linked to claims | Tied to specific claims, with their effect on interpretation |
| 10 | Narrative coherence | Sections feel independent | One thread, with gaps | Every section advances one argument |
| 11 | Terminology | Many undefined terms for the binding personas | A few undefined terms | All defined at first use; stable terms |
| 12 | Logical flow | Frequent non-sequiturs | Mostly ordered; some jumps | Each paragraph follows from the last; transitions are true |
| 13 | Evidence traceability | Claims with no visible basis | Most main claims point to evidence | Every claim points to a result, figure, table, or citation |
| 14 | Figures/tables | Unexplained or decorative | Explained, but the takeaway must be inferred | Takeaway caption + prose + RQ link for each |
| 15 | Claim–evidence alignment | Several claims exceed their evidence | Occasional overreach | Strength matches evidence throughout |
| 16 | Unsupported inference | Major conclusions not supported | Minor unsupported steps | None found |
| 17 | Redundancy | Heavy repetition blocks progress | Some repetition | Repetition only where it orients (e.g. RQ echo) |
| 18 | Cognitive load | Reader must hold too much; dense notation | Demanding but manageable | Concepts paced; notation minimal; numbers selective |
| 19 | Orientation | Reader often doesn't know where they are or why | Signposts at section level | Section openers state questions; paper map; clear transitions |
| 20 | "So what?" | Significance never stated | Stated generically | Specific significance for the RQ and the field, within scope |

Every score has an entry: dimension · score · location · observed problem (or strength) ·
reader struggle · likely consequence · revision principle · persona(s).

---

## 3. Blocking defects

Any of these blocks the move to final editing:
- Any dimension ≤2 for a binding persona
- Dimensions 13, 15, or 16 <4
- Any distortion (overstated/contradicted) on a nugget of strength `interpretation` or stronger
- Any orphan claim, unresolved overclaim flag, or unverified citation that isn't marked
- Open failure states not accepted by the user

## 4. Exit criteria (per paper)

All blocking defects are resolved, Core RR ≥0.8 (Q1, Q4, Q7, Q10, Q11), and the automated
audits pass. Maximum 3 review rounds. Then report the remaining issues. Don't iterate further.

## 5. What the rubric is not

- Not a style score. Two papers with different voices can both score 5.
- Not a length score. Longer is not better.
- Not a target to optimize. Revisions follow the *revision principle* and the underlying
  artifact, never "whatever raises the number".

---

## Measured comprehension (v0.3 Stage 3, M13)

Reviewer ratings are not comprehension (Phase 5: ratings rose while reconstruction fell). Use
`tools/comprehension_kit.py`:
1. `key` freezes a pre-declared answer key from the claim map (questions DONE, DATA, FOUND,
   UNCERTAIN, LIMITS).
2. `packets` builds blinded **visual-only** (headings, figures, captions) and **full** packets.
   Visual-only tests whether the figures and captions carry the story on their own.
3. Readers answer from memory; two graders label each (answer, nugget) pair blind; `score` gives
   MMF/RR per condition with bootstrap CIs and Krippendorff's α.
4. An intrusion is an unsupported belief only if the **paper** does not state it (evaluator v0.3,
   D-24). A detail the key omits is not an error.
LLM proxy readers and graders (`llm`, `grade-tasks`) test the pipeline and give a cheap signal. They
are never reported as human results. Human procedure: `templates/human_study_protocol.md`.
