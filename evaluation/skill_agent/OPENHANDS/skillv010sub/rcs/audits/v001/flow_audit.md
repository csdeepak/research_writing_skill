# Step 13 -- Logical-flow audit

**Paragraph level.** Checked each paragraph against the CLAIM/point-first model
(`information_design.md` S1) using `plan/paper_architecture.md`'s slot table as the reference
point/role for each paragraph. All paragraphs open with their point or their section's guiding
question; no buried ledes found on re-read. Transitional/short paragraphs (e.g. the one-line
openers of Web Browsing and Miscellaneous Assistance) are deliberate section-boundary bridges
(`information_design.md` S1 "transitional paragraphs"), not defects.

**Section level.**
- Introduction ends with the paper map (Q1-Q12-style roadmap) naming exactly 3 forward
  deferrals (Q7, Q10, Q11), matching `story/question_ledger.json`'s planned debt ceiling.
- Each Results subsection opens with the research question it answers (explicit "can a
  generalist agent..." / "software engineering exercises... web browsing exercises..." /
  "the final category shares the least...").
- Discussion opens by directly answering the RQ ("The question we opened with was...").
- Every deferred question lands where planned: Q7 (not-best-everywhere) -> Results synthesis +
  Limitations; Q10 (safety) -> Discussion paragraph 4; Q11 (statistics) -> Limitations
  paragraph 1. Debt = 0 at the end of the paper.

**Transitions.** Every "however/though/yet/but" and "therefore/thus/so" was checked for a real
relation: e.g. "It is, however, below a SWE-Agent configuration that reached 87.7%, but that
configuration was given one worked example..." -- the "however" marks a genuine contrast (a
higher number) and the "but" immediately supplies the confound that qualifies it. No decorative
"Moreover/Furthermore/Additionally" chain was introduced (`lint_draft.py`'s
`A15-decorative-transitions` check: transition-word density 0/1000 words, well under the 3/1000
threshold).

**Old -> new (S01) spot check.** Results:Cross-category synthesis's stress position ("a
structural fact about how the numbers were produced") is picked up as the topic of the next
sentence ("In every benchmark above, the system scored..."); Discussion paragraph 1's stress
position ("no single comparison baseline was shown to do the same") is picked up by paragraph
2's opening ("One reason this pattern is informative..."). Chains hold at each section boundary
checked.

**Result: PASS.** No non-sequiturs found; every planned forward-reference is honored downstream.
