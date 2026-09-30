id: TAB-2
purpose: "show that the benchmark's own relevance judgments can be unevenly incomplete across architecture families, and that this changes scores unevenly"
rq: N05 (RQ) / the case-study hypothesis N18
takeaway: "On TREC-COVID, dense systems had 5-10x more unjudged top-10 hits than lexical systems, and their scores rose far more once those hits were judged."
claims: [C018, C019]
evidence: [E015, E016]
type: table
comparison_the_eye_must_make: "Hole@10 (%) column vs. the size of each system's score change from 'before' to 'after'"
uncertainty_shown: "none available (single annotation pass; scope limited to one dataset, see L007)"
baseline_or_reference: "BM25 row (lexical, lowest Hole@10 alongside docT5query)"
non_conclusions: "does not show whether the same bias magnitude holds on the other 17 BEIR datasets (not tested)"
honesty_checks: {axes_start: "n/a (table)", all_conditions_shown: true, dual_axis: false, "3d": false, cherry_picked: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (table, not a chart)", min_font_pt_at_print: "n/a (Markdown table)", alt_text: "Table comparing each system's Hole at 10 percentage and its nDCG at 10 before and after the missing judgments were added, for TREC-COVID."}
placement: "Results, R.9, after the sentence introducing the case study"
caption: "Table 2. TREC-COVID's original judgment pool undercounted non-lexical systems' top hits. Hole@10 = share of a system's top-10 hits absent from the original judgments; nDCG@10 before/after the authors manually completed the missing judgments (980 pairs total), blinded to which system had retrieved each one. Source: paper.txt Table 4."
source_script: "n/a (transcribed from the project's own paper.txt Table 4; no source script in this project)"
