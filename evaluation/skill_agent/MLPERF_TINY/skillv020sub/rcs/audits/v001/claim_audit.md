# Step 12: Evidence / claim audit (draft v001)

## Tagging completeness
`lint_draft.py --rcs .rcs` (which auto-enables orphan-claim detection because the draft contains
`{C###}` tags) reports **0** `C1-orphan-claim` findings and **0** `tag-unresolved` findings after
this pass (earlier passes found and fixed 3 orphan claims: the VWW-dataset preprocessing
sentence, and two AD-architecture sentences -- all tagged with the claim already carried by the
rest of their paragraph, `{C012}` and `{C022}` respectively). Every `{C###}`/`{L###}` tag in the
draft resolves to an id present in `claims/claim_evidence_map.json`.

## Verb-vs-claim-type check
`lint_draft.py`'s `B4-verb-vs-type` rule reports **0** errors: no `interpretation`, `speculation`,
`hypothesis`, or `future`-typed claim is stated with a strong verb ("shows that", "proves",
"demonstrates", "establishes", "confirms"). One instance was caught and fixed in step 10: the
Introduction originally said the paper's Discussion/Limitations sections "discuss what that first
round does and does not **establish**" -- tagged `{C030}` (`interpretation`) two sentences later
in the same paragraph, tripping the rule because "establish" appears inside "does not establish."
Reworded to "does not **show**."

## Numeric spot-check (100% of the reported quantitative figures, exceeding the usual 20%/min-10
sample, given the draft has a tractable number of distinct figures)

| Draft figure | Location | Evidence id | Matches? |
|---|---|---|---|
| under 1 mW | Abstract, Intro P1 | E001 | Yes |
| 10-250 MHz, <50 mW | Intro P2 | E061 | Yes |
| >50 organizations | Intro P5 | E003 | Yes |
| June 2021 | Results P2 | E051 | Yes |
| Table 1 (all cells) | Method | E013 | Yes (AD input size corrected from "5x128" to source's own "5*128" during this audit) |
| VWW: alpha 0.25, 2 classes, 325 KB | Method P5 | E017 | Yes |
| VWW: person area >=2.5%, resized 96x96 | Method P5 | E016 | Yes |
| VWW: ~86% accuracy | Method P5 | E018 | Yes |
| VWW: 80% threshold | Method P5 | E019 | Yes |
| IC: 60,000 images, 10 classes, 5 train batches, 10,000-image test batch | Method P6 | E021 | Yes |
| IC: 3 stacks vs. 4, 96 KB | Method P6 | E023 | Yes |
| IC: 86.5% on 200 images, 85% threshold | Method P6 | E025, E026 | Yes |
| KWS: 105,829 utterances, 2,618 speakers, 30 words, 12 classes | Method P7 | E028 | Yes |
| KWS: 38.6K parameters, 92.2%/91.6%/91.7%, 90% threshold | Method P7 | E030, E033, E034 | Yes |
| AD: 6 machine types, 7 toy-cars, 1,000 samples | Method P8 | E036 | Yes |
| AD: 640 in/out, 128-unit x4 enc/dec, bottleneck 8, 128 mel bands, 32 ms, 6.4 s | Method P8 | E039 | Yes |
| AD: 248 samples/4 machines, AUC 0.88/0.86, threshold 0.85 | Method P8 | E041, E042 | Yes |
| Measurement: 5 runs, >=10 s, >=10 iterations | Method P3 | E047 | Yes |
| Round: 5 submissions, 4 closed + 1 open, per-row hardware/framework/numerics | Results P3, Table 2 | E052 | Yes |
| "microwatts to watts" | Abstract, Results P4 | E053 | Yes (verbatim range) |
| "roughly six orders of magnitude" | Abstract, Results P4 | derived from E053's two endpoints (1 uW = 1e-6 W; W/uW = 1e6 = 6 orders of magnitude) | Yes -- flagged as a writer-derived unit conversion using standard SI prefixes, not a number read from the source; hedged with "roughly" both times it appears; does not change any substantive finding |
| Negative result: no submitter changed the training dataset | Results P4 | E054 | Yes, and its `negative_result_decisions` entry (`reported_main`) is honored: it is reported in the main text (Results P4), not only in a supplement |

## Reference-list fidelity check (this audit's main finding)
Cross-checking every References entry against `project/paper.txt`'s own numbered reference list
found **one** fidelity problem: the Fedorov et al. entry had been silently "corrected" to the
title "SpArSe: Sparse Architecture Search for CNNs..." using the audit-writer's outside knowledge
of that paper's actual published title, rather than transcribing what `project/paper.txt`'s
reference list actually shows ("Sparse: Sparse architecture search for cnns..."). This is exactly
the kind of outside-knowledge substitution the hard rules forbid. **Fixed**: both
`corpus/source_registry.json` (SRC-009) and the draft's References entry now read "Sparse: Sparse
Architecture Search for CNNs on Resource-Constrained Microcontrollers" (title-cased, but not
"corrected" to a different title), matching the extracted text. No other reference entry showed
this problem; the rest are direct capitalization/ligature-artifact normalizations (e.g.
"Tensorﬂow" -> "TensorFlow", the ligature `ﬂ` decoding unambiguously to "fl") rather than content
changes.

## Claim-type ladder check
Every `measured` claim (C012, C016, C019, C024) rests on >=1 `hard` evidence item. Every
`interpretation` claim (C006, C030) rests on other claims plus, where available, a directly
quoted author statement of the same interpretation (E063 for C006; E064 for C030) rather than on
the audit-writer's inference alone. The one `future` claim (C032) paraphrases the authors' own
stated future-work sentences (E058-E060) rather than proposing a new direction. No claim's
evidence list was found stronger or weaker than declared.

## Negative-result coverage
The only `negative_result`-kind evidence item, E054, has a `negative_result_decisions` entry
(`reported_main`) and is reported in the main text (Results P4) with an interpretation in the
Discussion (D3), not dropped or moved to a footnote. No other negative or null result appears in
the evidence map that is absent from the draft.

**Result: 0 blocking defects.** One fidelity fix applied (Fedorov title); no claim-strength,
numeric, or coverage defects found.
