# Step 13 -- Logical-flow audit

## Section level
- **Introduction ends with the RQ, the contributions, and a paper map.** Checked: RQ1/RQ2 stated
  explicitly (para 4, "This paper asks two connected questions..."), contributions listed and
  each tied to a result (para 6, "This gives two contributions..."), paper map given (para 7,
  "Section 2 positions OpenHands...Section 7 states the limitations..."). Matches
  `section_rules.md`'s INTRODUCTION contract.
- **Each Results subsection opens with the question/category it answers.** Software engineering,
  Web browsing, and Beyond code and browsers are each bolded lead-ins that state the category
  before any number appears.
- **Discussion answers every RQ.** Para 1 answers RQ2 directly ("That directly answers the
  paper's second question..."); para 3 answers RQ1 directly ("This also speaks to the first
  question..."). Both answers point back to specific evidence rather than merely asserting.
- **Limitations reports every `author_stated` item first, then a clearly labeled "Additional
  caveats" paragraph for `writer_derived` items** -- checked directly against
  `claims/claim_evidence_map.json`; matches the S1 attribution rule (also confirmed by
  `lint_draft.py`'s S1-* checks reporting 0 errors).

## Paragraph level (sampled: every Results and Discussion paragraph, plus both Limitations
paragraphs -- 13 paragraphs)
For each: role (story node), point (first or second sentence), evidence present, link-back to
the previous paragraph's topic, link-forward to the next. All 13 pass:
- Every paragraph opens on old information (the benchmark or claim just introduced) and closes
  either on the next paragraph's topic (e.g., the SWE-Bench Lite paragraph closes by naming the
  "software half of the second question," which the next paragraph on HumanEvalFix continues) or
  on a stated scope limit that the following paragraph does not contradict.
- No paragraph's point appears only in its last sentence (no buried lede): each Results
  paragraph puts the number and the comparison in its first sentence.
- No paragraph needs splitting into "and also" halves; each covers one benchmark or one claim.

## Transitions
Manually reviewed every connective word ("but," "though," "while," "so," "because," "since")
for whether the relation it asserts actually holds:
- "but ... CC-Net ... reaches 91.1%" (MiniWoB++ paragraph): true contrast -- the preceding clause
  reports OpenHands' own higher-than-its-weaker-configuration score, and CC-Net's number is
  indeed higher still.
- "though not unconditionally" (Discussion para 1): true qualifier -- the next clause names the
  actual condition (9 of 11, not 11 of 11).
- No instance of "moreover/furthermore/additionally/besides/also," at a sentence opening was
  used anywhere in the draft (confirmed: `lint_draft.py`'s `A15-decorative-transitions` check,
  which flags a *rate* of such connectives above 3 per 1000 words, did not fire at all on this
  draft -- see `audits/gates/G3_lint.json`).

## Old -> new information flow
Spot-checked the Results section's benchmark-to-benchmark transitions: each new paragraph's
opening noun phrase ("On HumanEvalFix...", "On WebArena...", "On MiniWoB++...") is genuinely new
information relative to the previous paragraph's closing point, while the shared frame ("the same
unmodified CodeActAgent") is repeated verbatim throughout rather than drifting into synonyms
(checked against `story/term_ledger.json`'s "one term per concept" rule for "CodeActAgent").

**Result: no `A1` (late question), `A2` (buried contribution), `A10` (discussion amnesia), `A15`
(decorative transitions), or `A16` (buried lede) anti-pattern found.** Proceeding to step 14.
