# Self-audit summary, draft v001 (steps 11-17)

## Step 11-12: reconstruction / claim audit
Q1-Q12 answerable from the skeleton and the full draft (see plan/skeleton.md reconstruction check). Every reported number in the draft was checked against research_evidence.json / claim_evidence_map.json by hand; all match the evidence verbatim (55.2%, 29.3->12.8, 2.5 vs 2.7 conflict disclosed, 39M/6.7 WER, 5.3->1.4/73%/5.8%, 11.0->10.0 decoding table, 29.1 BLEU and Table 4 resource-group figures, Table 5 multilingual figures, Table 6 scaling figures, 0.83/0.24 correlations, 65% compute fraction). No orphan numbers found.

## Step 13: flow audit
Each Results subsection opens with the question/benchmark it addresses. Discussion opens with a per-RQ answer (4.1) before Limitations (4.2). Transitions checked for true relations; no decorative "moreover/furthermore" chains found.

## Step 14: terminology/load audit
WER and BLEU are glossed at first use (abstract and Results 3.3). "Zero-shot" and "effective robustness" are defined before use (Introduction, Method 2.2). Dataset/system proper nouns (LibriSpeech, VoxPopuli, Fleurs, CoVoST2, MLS, mSLAM, XLS-R, Maestro, wav2vec 2.0, TED-LIUM3, Kincaid46, CORAAL, etc.) are used as identifiers with enough surrounding context (task, benchmark type) for an adjacent-field reader to follow the comparisons, without a full dataset-by-dataset tutorial, per the term budget for mode B. `tools/lint_draft.py` flags several of these as "undefined acronyms" (A3); reviewed and accepted as false positives of the heuristic tool, since these are proper nouns identifying specific external systems/datasets, not technical concepts the reader must internalize to follow the argument.

## Step 15: figure/table audit
Six tables replace the paper's figures (no images per task constraint). Each has a card in plan/figure_cards/, a takeaway stated in prose, and is referenced by number before or at the point the reader meets it (Tables 1, 2, 3, 4, 5, 6 all named in text). Non-conclusions are stated for each.

## Step 16: citation audit
Three sources verified to the level the evidence package allows (corpus/source_registry.json): Amodei et al. (2015), Taori et al. (2020), Zhang et al. (2021) — first author + year only, verification.method=user_supplied_file, read_depth=abstract (no web access in this run). Each has a support quote and a stated role in the text (human-level error rate; effective-robustness framework; supervised SOTA trajectory). No other citations were added; systems/datasets without a first-author/year in the evidence are named but not cited, per the hard rule against fabricating references. Reference list entries are marked [CITATION NEEDED: full bibliographic details] rather than inventing titles/venues/initials.

## Step 17: overclaim audit
- B3 (SOTA): every "state of the art" statement names the benchmark (CoVoST2 X->en), the comparison set (Maestro, mSLAM-CTC, XLS-R), and the date (September 2022), and attributes the claim to the original authors rather than asserting it independently. `lint_draft.py` still flags the bare phrase "state of the art" as a pattern match (B3) in 4 locations; each was manually reviewed and found already fully qualified per citation_rules.md/anti_patterns.md B3, so no further change was made.
- B2/B9 (unsupported superiority / vague intensifiers): "significantly underperforms" was rewritten with the actual WER numbers (Results 3.4). Remaining B9 flags on words like "substantial"/"comparatively simple" in the Abstract and Conclusion are qualitative summary language backed by the specific numbers given earlier in the same sentences/paragraphs; reviewed and kept.
- B5 (causal wording): "driver"/"drives" language in Discussion 4.1 was softened to "is associated with" / "contributor to", and an explicit caveat was added that no ablation isolates data scale from architecture/recipe.
- B4 (proof language): no results are described as "proving" anything; hedged with "consistent with," "suggests," "supports the interpretation."
- Negative results (E019 VoxPopuli, E022 CoVoST2 high-resource, E024 Fleurs LangID, E031 negative transfer, E038 long-form failure modes) are all reported in the main text (Results 3.3-3.5, Discussion 4.2), matching negative_result_decisions in claims/claim_evidence_map.json.

## Tool output
- `python tools/validate_artifacts.py .rcs`: 0 schema errors; 48 locator-path errors (all `paper.txt`/`README_1.md`, expected and accepted per TASK.md's EVIDENCE INTERFACE — the original source files are not available in this run); 12 WARN "measured claim not backed by hard evidence" (expected: every evidence item in this run's package is `strength: soft`, disclosed as limitations L001-L003).
- `python tools/lint_draft.py .rcs/drafts/v001/paper.md --rcs .rcs`: 0 errors, 29 warnings remaining after fixes (mostly proper-noun "acronyms" for dataset/system names, and repeated SOTA-pattern matches on an already-qualified claim), 72 info-level notes (mostly sentence-length advisories in a technically dense paper for an adjacent audience — reviewed; kept where splitting would fragment a single coherent comparison, per the tie-breaker "reader need > convention" and "clarity > brevity" ordering in principles.md).

## Gate G4
Not attempted: steps 18-20 (blind REVIEW_AGENT, repeat rounds) are explicitly out of scope for this run per TASK.md's run-specific constraints ("Step 18 (blind review) is performed externally... After step 17... stop and reply DONE").
