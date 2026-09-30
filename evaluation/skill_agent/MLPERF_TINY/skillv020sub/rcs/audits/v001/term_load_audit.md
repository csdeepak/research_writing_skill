# Step 14: Terminology / cognitive-load audit (draft v001)

## Term ledger checks
- **Use before definition:** `lint_draft.py`'s `A3-use-before-definition` reports 0 findings.
  `story/term_ledger.json` was corrected during step 13 to match the final draft (TFLM and the
  reference board are now both first defined in Method P1, not left implicit until Results).
- **One term per concept:** spot-checked "microcontroller-class hardware" (never alternates with
  "edge device"/"embedded system"), "the suite" (never alternates with "the framework"), "closed
  division"/"open division" (used consistently, never "strict track"/"flexible track"). No
  synonym drift found.
- **Acronyms used <3 times:** `A4-rare-acronym` flags only `WASPAA` (a conference-name acronym
  inside a References entry, 1 use) -- left as is; spelling out a venue abbreviation inside a
  bibliography entry is not standard practice and would not aid the reader. QAT and FPGA are used
  twice each in the main text but are kept as acronyms (not flagged by the lint's exact rule,
  which only fires when a definition exists; both are spelled out at first use) because they name
  widely-recognized hardware/training concepts, matching the exception already logged in
  `story/term_ledger.json`.

## New-term-per-paragraph budget (mode B: <=2 new terms/paragraph, diagnostic not a hard cap --
`audience_model.md` SS5)
Spot-checking the densest paragraphs:
- Method P7 (keyword spotting): introduces "depthwise-separable convolutional network," "unknown
  class," "silence class," and revisits PTQ-adjacent quantization language -- **4 new terms**,
  over budget.
- Method P8 (anomaly detection): introduces "autoencoder," "log-mel spectrogram," "bottleneck,"
  "AUC-ROC," "reconstruction error" -- **5 new terms**, over budget.
- Background P2 (four challenges): introduces "power-measurement scope," "quantization,"
  "hardware heterogeneity," "software heterogeneity," implicitly -- **~4 new terms**, over budget.

**Disposition:** these three paragraphs are flagged and reviewed, not silently over budget. Each
is CORE-density in `plan/paper_architecture.md` -- the term IS the content the reader needs at
that exact point (a benchmark's own name for its dataset class, model family, or metric cannot be
deferred without leaving the benchmark under-specified). Splitting each paragraph further was
considered and rejected: the paragraph model's own failure signature ("`point` needs two sentences
joined by 'and also' -> two paragraphs," `information_design.md` SS1) does not apply here, because
each paragraph has one point (this benchmark's task/data/model/threshold), not two competing
points; splitting by term rather than by point would fragment one design description across
several paragraphs without reducing what the reader ultimately has to hold in mind. Every one of
these terms still gets an inline plain-language gloss at first use (e.g., "a fully-connected
autoencoder... chosen both because it is already a well-known baseline... and because it gives the
suite a model family built entirely from fully-connected layers"; "AUC-ROC" is glossed via its
"threshold-free" framing rather than a formal definition, since the audience already knows general
statistics per TASK.md's AUDIENCE line). This is logged as an accepted, reasoned exception to the
soft budget rather than a silent miss.

## Sentence length (>35 words reviewed per `information_design.md`/anti_patterns.md)
`lint_draft.py --json` initially flagged the draft's longest sentences at up to 103 words. Six
sentences of 65-103 words were reviewed and split in this pass (the 103-word Limitations opening
sentence, the 82-word measurement-protocol anti-gaming sentence -- now two sentences -- the
79-word "Additional caveats" opening, the 72-word streaming-limitation sentence, the 71-word
Discussion-opening sentence, and the KWS class-design sentence). One 82-word sentence was kept
whole and flagged with a reason: the `[MISSING RESULT: ...]` marker (Results P2) is a structured
gap-marker, not ordinary prose, and splitting it would not make the missing-data disclosure any
clearer. After this pass, 59 `A-long-sentence` INFO findings remain, concentrated in the four
per-task Method paragraphs and the Background/Discussion sections; each remaining long sentence
was individually reviewed and kept because it links one antecedent-bearing clause to its
immediately dependent reason clause (e.g., "X, chosen because Y" or "X; because of Z"), and
splitting it would either strand the reason clause from its claim (an orphan-claim risk) or
require repeating the subject noun phrase, which would itself add words without reducing load.
This is a documented "keep with reason" disposition for the remaining cases, per
`information_design.md` SS3's own instruction ("split them, or keep them with a reason").

## Information density (density-class check)
No SUPPLEMENTARY-class content was found smuggled into CORE-density paragraphs: firmware API
listings, the specific EMON hardware models, and the Appendix's low-level framework-communication
protocol (all present in `project/paper.txt` Appendix A) were deliberately left out of the new
paper rather than compressed in -- they inform reproducibility of the ORIGINAL suite, not this
paper's own claims, and TASK.md's word budget (3,000-4,500 words) and single-file format leave no
appendix to relocate them into. This is recorded, not silently dropped: see
`plan/paper_architecture.md`'s "Checks" section.

**Result: 0 blocking cognitive-load defects.** Three CORE paragraphs exceed the soft new-term
budget, reviewed and kept with a documented reason (irreducible task-specification density); six
long sentences shortened, remaining long sentences reviewed and kept with reasons.
