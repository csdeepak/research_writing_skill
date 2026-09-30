# Step 14 -- Terminology / cognitive-load audit (draft v001)

## Term ledger compliance
Checked every entry in `story/term_ledger.json` against the draft:
- All 10 entries are defined at or before first use, **except** "MCU-class device", which is
  informally glossed at its very first use (Introduction P1: "microcontroller-class (MCU)
  hardware... under roughly a milliwatt of power, ... clocked between 10 and 250 MHz...") and
  then given its comparative envelope ("two orders of magnitude smaller...") in the same sentence
  -- so the full definition and the first use are in the same sentence, not meaningfully
  separated. This is the pre-recorded, accepted exception from the term ledger.
- No registered term is replaced by a synonym for the same concept anywhere in the draft (e.g.
  "reference implementation" is never called "baseline implementation" or "default
  implementation"; "closed/open division" is never called "strict/loose division").
- Acronyms used fewer than 3 times were checked against `lint_v001.json`'s A4 flags: CVPR,
  WASPAA, and ECCV each appear once, but only inside the References list (venue abbreviations in
  a bibliography entry, not main-text prose) -- not a term-ledger violation. PTQ, QAT, TFLM, AUC,
  and IPS each appear >=2 times in main-text prose after being defined; MCU appears >15 times
  (justifying its acronym use). This matches the rule "introduce an acronym only if used >=3
  times after definition, else spell out" for every acronym that actually recurs in prose.

## New-concept rate (mode B: <=2 new terms/paragraph)
Sampled the density: Background P2 (the four challenges paragraph) introduces four *named*
challenges but zero new *technical terms* requiring definition (they are described in plain
language, not named with jargon) -- within budget. Background P3 introduces exactly two new
terms (PTQ/QAT as one pair, AUC separately) across two sentences -- at the edge of, but within,
the mode-B budget for a background paragraph whose whole job is vocabulary-setting (an accepted,
deliberate concentration, matching the "term budget is diagnostic, not a hard quota" rule in
`audience_model.md` section 5).

## Sentence length
`lint_draft.py`'s A-long-sentence check flagged 27 sentences >35 words after the first revision
pass (down from the original count; see `lint_v001.json`). The 4 longest (>=54 words) were split
in the revision round (Methods' latency/energy/accuracy sentence; Discussion's degenerate-case
sentence; Results' interpretation sentence; Discussion's future-directions sentence). The
remaining 36-51-word sentences were kept deliberately: most list 3-4 grammatically parallel items
(e.g. the four benchmarks' dataset/model pairs in Methods, or the three literature critiques in
Related Work), where splitting would break the parallel structure information_design.md section
5 recommends for exactly this kind of list. Reason recorded per `information_design.md` section 1
("split them, or keep them with a reason").

## Information density
No DISTRACTING content was found needing removal (no project history, tool trivia, or abandoned
ideas are present in the source evidence to begin with). SUPPLEMENTARY-class implementation
detail (specific EMON hardware models, the Arduino-based IO Manager, the exact API function
signatures in Appendix A) was compressed to a single clause or omitted entirely, consistent with
TASK.md's no-supplement, 3000-4500-word constraint -- these details would have been
SUPPLEMENTARY/reproducibility-only for this paper's stated audience and purpose (mode B, not a
reproduction guide) and were not deleted from the evidence map, only left out of the main text.
