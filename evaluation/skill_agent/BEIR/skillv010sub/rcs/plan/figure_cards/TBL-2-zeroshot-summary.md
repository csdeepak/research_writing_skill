id: TBL-2
purpose: "let the reader compare all 10 systems' in-domain score and average zero-shot change vs. BM25 in one place"
rq: RQ1
takeaway: "Re-ranking and late-interaction are the only two families that beat BM25 on average zero-shot; every dense system and both term-reweighting sparse systems fall short of it, despite most beating BM25 solidly in-domain."
claims: [C001, C004, C005, C006, C007, C008, C009]
evidence: [E012, E013]
type: table
comparison_the_eye_must_make: "in-domain score (high for almost everyone) vs. the zero-shot delta column (positive for only 3 of 9 systems)"
uncertainty_shown: "none available -- the source reports no seed/replicate variance for these figures (L006); this is stated in the caption, not hidden"
baseline_or_reference: "BM25 shown as the reference row (delta column starts from it, defined as 0%)"
non_conclusions: "does not show per-dataset scores (available for 7 of the 10 systems in the source but not reconstructed here with full confidence for the other 3, see evidence/missing_evidence.json#MISS-001); does not show statistical significance of the differences"
honesty_checks: {axes_start: "n/a (table)", all_conditions_shown: true, dual_axis: false, "3d": false, cherry_picked: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (table)", min_font_pt_at_print: 7, alt_text: "A table listing all 10 evaluated retrieval systems with their architecture family, in-domain MS MARCO nDCG@10 score, and average percentage change in zero-shot nDCG@10 relative to BM25 across the 18 BEIR datasets."}
placement: "Results: Zero-Shot Generalization section, introduced by R1.1/R1.2 before the table appears"
caption: "Table 2. In-domain score and average zero-shot change vs. BM25 (nDCG@10) for all 10 evaluated systems. No replicate/seed variance is available for these figures (Thakur et al., 2021)."
source_script: "n/a (reconstructed by hand; see evidence/research_evidence.json#E012, #E013 and evidence/missing_evidence.json#MISS-001 for what was and was not reconstructed from the damaged source table)"
