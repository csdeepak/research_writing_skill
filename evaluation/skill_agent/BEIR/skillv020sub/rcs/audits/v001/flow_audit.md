# Step 13 -- Logical-flow audit

## Paragraph level
Spot-checked every paragraph against the paragraph model (`information_design.md` Section 1:
role, point-first, evidence, link-back, link-forward). All paragraphs open with a topic sentence
carrying the point; none bury the lede in a final sentence. Two short transitional paragraphs
exist by design (Results 5.1's closing cost sentence into 5.2's opening; Related Work's closing
gap-to-contribution sentence into Method) and are legitimate per `information_design.md`
("transitional paragraphs... at section boundaries").

## Section level
- Introduction ends with the numbered contributions and an explicit paper map by section
  ("Section 2 places...; Section 3 describes...; ...") -- satisfies the INTRODUCTION contract.
- Each Results subsection (5.1-5.4) opens by naming the question or comparison it addresses
  ("Our first finding answers our third question directly"; "The two sparse methods that split
  most sharply..."; "Among the dense bi-encoders..."; "The comparisons above assume...").
- Discussion answers each of the introduction's three implicit sub-questions (predictiveness;
  cost trade-off; trustworthiness of margins) in the same order the Results built them, then
  closes with one synthesis paragraph -- satisfies the DISCUSSION contract's "answer to each RQ"
  requirement.
- Limitations reports every `author_stated` limitation first (L001-L006), then a paragraph
  explicitly labeled "**Additional caveats.**" for the two `writer_derived` items (L007-L008) --
  satisfies the attribution ordering rule.
- Conclusion states the finding at claim strength and the main boundary, and does not introduce
  new results or citations; sentence-overlap with the Abstract is low (different sentences,
  different framing -- "we built BEIR to find out..." vs. the Abstract's "Retrieval models are
  typically trained..."), consistent with the A12/echo-conclusion check the lint also passed
  (0 `A12-echo-conclusion` findings).

## Transitions
Manually reviewed every "however", "in contrast", "yet", "though", "because", "so", and "but" in
the draft (there are no "moreover/furthermore/additionally" chains -- `tools/lint_draft.py`
reports 0 `A15-decorative-transitions` findings, and the additive-transition rate is 0 per 1000
words). Each checked connective names a relation that holds:
- "yet on average... it outperforms six of the nine" (Abstract, Sec. 5.1): true contrast between
  the in-domain and zero-shot numbers just given.
- "though this explanation is speculative..." (Sec. 5.3): true qualification of the immediately
  preceding attributed claim.
- "This case study does not overturn our main comparison -- ... -- but it means..." (Sec. 5.4):
  true scope-limiting relation, not a false concession.

## Old -> new information flow
Spot-checked the Results section's paragraph-to-paragraph chaining: each paragraph's stress
(sentence-final) concept is picked up in the next paragraph's topic position -- e.g. 5.1 ends on
cost ("Sparse methods are fastest... on CPU"), and 5.2 opens with the sparse-method split,
picking up "sparse" as old information before introducing the new point (the term-weighting vs.
expansion divergence). No paragraph starts on a wholly new topic without a link back.

## Outcome
No `A1` (late question), `A2` (buried contribution), `A8` (disconnected experiments), `A10`
(discussion amnesia), `A13` (private context leak), `A16` (buried lede), or `A17` (question
debt) instances found. Question ledger (`story/question_ledger.json`) shows 0 debt at the end of
every section.
