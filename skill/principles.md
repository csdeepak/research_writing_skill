# Principles

Twelve principles. Each is stated once, traced to its origin, and tied to the **operational
check** that enforces it. A principle without a check is a wish. If you can't point to the
check, the principle isn't being applied.

Origins: **F0** = OOMD Technical Writing course (Units 1–4). `Sxx` = sources in
`docs/SOURCES.md`.

---

### P1. The reader defines meaning
*Origin:* F0 Unit 1 (reader-centered), S01 ("meaning is what readers interpret").
A sentence means what a competent target reader takes from it, not what the author intended.
**Check:** the reconstruction test (step 11 self-test, step 18 blind review). A mismatch
between the reader's answer and the gold story is a defect in the text, never in the reader.

### P2. Plan the argument before the prose
*Origin:* F0 Unit 1 (Planning → Drafting → Revising → Editing); S02, S03.
**Check:** Gate G1/G2. No section is drafted until the spine, story graph, claim map, and
paper architecture validate.

### P3. Every claim carries its evidence and its strength
*Origin:* F0 Unit 2 (evidence evaluation, levels of certainty, hard vs soft evidence); S18.
**Check:** the claim map. Every significant sentence has a `{C###}` tag. The claim's
`claim_type` limits its verbs (`evidence_model.md` §3).

### P4. Say how sure you are, and no surer
*Origin:* F0 Unit 2 ("a wrong conclusion is far worse than no definite conclusion"); S05, S23,
S30.
**Check:** the overclaim audit (step 17) and the non-conclusion step of the Result
Interpretation Chain. The "What the results do NOT establish" content must exist.

### P5. Answer the reader's next question
*Origin:* F0 Unit 1 (anticipated reader questions, Glenn's analysis).
**Check:** the question ledger. Every raised question is answered or explicitly deferred with a
pointer. Open question debt at the end of a section is a defect.

### P6. Every element earns its place
*Origin:* F0 Units 1 & 3 ("worthwhile content: all and only what readers need"; "a graphic
should serve a purpose").
**Check:** paragraph → story-node mapping, density classes, and figure/table cards. Unmapped
content is moved, cut, or justified in writing.

### P7. Say "so what"
*Origin:* F0 Unit 1 ("Don't just list facts. Explain the significance").
**Check:** the RIC (meaning + link to the research question) for every major result, and a
takeaway sentence for every figure and table.

### P8. Define before use; one name per thing
*Origin:* F0 Units 1 & 3 (define jargon; repeat key words, don't vary terms); S11–S13, S27.
**Check:** the term ledger. Lint flags use-before-definition, acronyms used fewer than 3 times,
and synonyms for a registered term.

### P9. Put old information first and new information last
*Origin:* F0 Unit 3 (coherence devices, topic sentences); S01 (topic and stress positions).
**Check:** the flow audit (step 13). A paragraph's opening links to what came before, and its
emphasis lands on the new point.

### P10. Represent evidence honestly, including what went wrong
*Origin:* F0 Unit 2 (ethical representation, misleading visuals, reasoning fallacies); S04,
S23.
**Check:** the negative-result inventory, visual honesty checks, and `SELECTIVE_REPORTING`
detection.

### P11. Credit precisely; cite only what supports
*Origin:* F0 Unit 2 (documentation, plagiarism); S06, S22, S25, S26.
**Check:** the citation pipeline (existence → metadata → support quote → strength →
primary-source preference).

### P12. The machine drafts; the human remains accountable
*Origin:* F0 Unit 4 ("AI generates; you verify"); S14–S17.
**Check:** `open_issues.md` and `disclosure.md` go to the user. Every AUTHOR-inferred claim is
marked `author_confirmation: pending` until the user confirms it.

---

## Tie-breakers when principles conflict

1. **Truth > clarity > brevity.** Never simplify a claim into a false one. When clarity and
   brevity conflict, choose clarity. Move detail to the supplement rather than delete it
   (reproducibility).
2. **Reader need > convention.** Follow the venue's structure, but when a convention would hide
   the argument (e.g. strict results/discussion separation for a multi-RQ ML paper), tell the
   user and propose the venue-compatible alternative.
3. **Content invariance > audience comfort.** Adapting to an audience can add explanation. It
   never removes caveats that bear on the claims.
