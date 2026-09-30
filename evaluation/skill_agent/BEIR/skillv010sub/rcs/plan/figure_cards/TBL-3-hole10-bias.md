id: TBL-3
purpose: "show that annotation-pool coverage (Hole@10) differs sharply by architecture type, and that fixing it changes scores accordingly"
rq: RQ2
takeaway: "Non-lexical systems had 5-12x more of their top-10 hits unjudged than lexical systems did, and closing that gap raised their scores by several points while lexical systems barely moved."
claims: [C017, C018]
evidence: [E037, E038, E039]
type: table
comparison_the_eye_must_make: "Hole@10 column (lexical vs. non-lexical rows) against the original-vs-annotated score columns for the same rows"
uncertainty_shown: "none reported in the source for this single re-annotation pass"
baseline_or_reference: "BM25's own small original-to-annotated change (0.656->0.668) as the reference 'if pooling were already fair' pattern"
non_conclusions: "measured on TREC-COVID only; does not establish the same bias magnitude on other BEIR datasets (L008)"
honesty_checks: {axes_start: "n/a (table)", all_conditions_shown: true, dual_axis: false, "3d": false, cherry_picked: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (table)", min_font_pt_at_print: 7, alt_text: "A table listing each system's Hole@10 percentage on TREC-COVID alongside its nDCG@10 before and after manually annotating the previously unjudged pairs."}
placement: "Annotation Selection Bias case-study section, after the Hole@10/re-annotation procedure is described"
caption: "Table 3. Hole@10 and nDCG@10 before/after manual re-annotation of 980 previously-unjudged pairs on TREC-COVID (Thakur et al., 2021)."
source_script: "n/a; see evidence/research_evidence.json#E037, #E038"
