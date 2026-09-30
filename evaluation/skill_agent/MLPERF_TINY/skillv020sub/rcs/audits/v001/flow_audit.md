# Step 13: Logical-flow audit (draft v001)

## Section level
- **Introduction ends with the RQ, the contributions, and a paper map.** Confirmed: P4 states the
  RQ explicitly ("This paper asks an explicit question..."), P5 states the three contributions
  ("This paper's contributions are three points...") each tied to the sections that carry them
  ("Sections 2 and 3...", "Section 4...", "Sections 5 and 6..."). This satisfies A1/A2
  (`lint_draft.py` reports 0 findings for `A1-late-question` / `A2-buried-contribution` after the
  step-10 rewording).
- **Each Results subsection opens with the question it answers.** Results P1 states the two
  questions the section answers ("whether the reference implementations meet their own targets...
  and whether organizations outside the authors could use the suite at all") before P2 and P3
  answer them in that order.
- **The Discussion answers every RQ.** The paper has one RQ (spine line 3 / story-graph N05,
  consistent with a method-first, single-suite paper rather than a multi-RQ study). Discussion P1
  opens by answering it directly ("Taken together, the first round answers the paper's opening
  question..."), which satisfies the "discussion answers every RQ" check for the single-RQ case.
- **Limitations reports every `author_stated` limitation first, then a separately labeled
  "Additional caveats" paragraph for `writer_derived` ones.** Confirmed: Limitations P1-P2 cover
  L001-L003 (all `author_stated`), and P3 opens with the literal label "Additional caveats." before
  covering L004-L005 (`writer_derived`). This matches `S1-caveat-attribution` (0 findings).
- **Conclusion does not introduce new results or repeat the Abstract.** `lint_draft.py`'s
  `A12-echo-conclusion` check (>40% sentence-level token overlap with the Abstract) reports 0
  findings, and a manual read confirms the Conclusion synthesizes (states what is now understood
  and what remains open) rather than repeating the Abstract's sentences.

## Paragraph level (spot-checked against the paragraph model: point first, evidence, link-back,
link-forward)
- Method P5 (VWW): point ("Visual wake words asks whether...") is first; evidence (dataset, model,
  accuracy figures) follows; link-forward is implicit via the shared per-task template established
  in the Method's opening paragraphs (this is `writing_patterns.json` PAT-001, deliberately reused
  from the source paper's own structure).
- Results P4 (negative result): opens with "Two patterns emerge from looking across the round" --
  links back to P3 (the round just described) and previews what follows (two numbered patterns).
- Discussion P3: opens "At the same time," explicitly signaling a contrast with D1-D2's positive
  reading -- a true contrast (D1-D2 establish that the design worked; D3 bounds what "worked"
  means), not a decorative connective.
- No paragraph's point appears only in its final sentence (checked against `A-long-sentence` /
  buried-lede risk in the longest paragraphs: Method P5-P8, Discussion P1-P4); each opens with its
  claim before its detail.

## Transitions (every connective checked for a real relation)
`lint_draft.py`'s `A15-decorative-transitions` check (additive-connective density) reports 0
findings (the draft uses very few "Moreover/Furthermore/Additionally" chains; most transitions are
built into topic sentences instead, e.g. "At the same time,", "For a reader outside TinyML,",
"Put together,"). Manually re-checking each: "Put together" (Background P4) is true addition (it
synthesizes the three prior-benchmark critiques just given). "At the same time" (Discussion P3) is
a true contrast, as above. "Additional caveats." (Limitations P3) is a true category change
(author-stated -> writer-derived), not decorative.

## Old -> new (topic/stress position)
Spot-checked the Method section's four per-task paragraphs (P5-P8): each opens with the task name
(old information carried from Table 1, which the reader just saw) and closes with the numeric
quality-target sentence (new information, in stress position), matching the "topic = old, stress =
new" pattern from `information_design.md` SS4. The Discussion's D1->D2->D3->D4 chain: D1's stress
position ("report results that a reader can meaningfully set side by side") becomes D2's topic
("The mechanism behind that result..."); D2's close ("nothing else in common") sets up D3's topic
("the round's diversity was concentrated..."); D3's close ("a first observation... than a settled
property") sets up D4's topic ("For a reader outside TinyML, the more general point is this...").
The chain holds without a gap.

## Term ledger cross-check (paragraph mapping)
Re-checked `story/term_ledger.json` against the final draft's actual first-use locations (a few
shifted slightly during step 10 revision): TFLM is now defined at its first use, Method P1 (moved
up from its original Table-only appearance -- see `reconstruction_self.md`); "NUCLEO-L4R5ZI" is
likewise first used in Method P1, with Results P2 correctly reusing (not redefining) it. No term
is used before its definition anywhere in the final draft (`lint_draft.py`'s
`A3-use-before-definition` reports 0 findings).

**Result: 0 blocking flow defects.**
