id: TAB-1
purpose: "show that the architectures with the best average zero-shot generalization are not the ones that win in-domain, and that they cost the most compute"
rq: N05 (RQ)
takeaway: "Re-ranking and late-interaction generalize best zero-shot (beating BM25 on average) but cost far more per query than dense retrieval; four of six weaker-generalizing systems still beat BM25 in-domain."
claims: [C004, C006, C007]
evidence: [E005, E006, E014]
type: table
comparison_the_eye_must_make: "each system's in-domain MS MARCO column vs. its zero-shot avg-vs-BM25 column vs. its latency column"
uncertainty_shown: "none available (single run per system; noted in the caption and in Limitations, L006)"
baseline_or_reference: "BM25 row, marked as the 0% zero-shot reference"
non_conclusions: "does not show per-dataset variation (only the 18-dataset average); does not show index size (see paper.txt Table 3 for that)"
honesty_checks: {axes_start: "n/a (table)", all_conditions_shown: true, dual_axis: false, "3d": false, cherry_picked: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (table, not a chart)", min_font_pt_at_print: "n/a (Markdown table)", alt_text: "Table comparing 10 retrieval systems' in-domain MS MARCO score, average zero-shot score relative to BM25 across 18 datasets, and GPU query latency."}
placement: "Results, after R.1's opening sentence, before R.2"
caption: "Table 1. In-domain accuracy does not predict zero-shot generalization, and the best zero-shot generalizers cost the most compute. nDCG@10 on MS MARCO (in-domain, single run); average zero-shot nDCG@10 relative to BM25 across the 18 BEIR datasets (single run per system, no seed variance); GPU query latency on 1M sampled documents. Source: paper.txt Tables 2 and 3."
source_script: "n/a (transcribed from the project's own paper.txt Tables 2-3; no source script in this project)"
