id: TBL-1
purpose: "show the scale and diversity of the 18 BEIR datasets so the reader can judge how demanding a zero-shot generalization test this is"
rq: RQ1 (sets up the evidence base for it)
takeaway: "BEIR's 18 datasets span a 4,000x range in corpus size and cover both very short and very long queries/documents, drawn from ten-plus distinct domains."
claims: [C021, C022]
evidence: [E011, E003]
type: table
comparison_the_eye_must_make: "the spread of #Corpus, query-length and document-length columns across rows (domains), not any single value"
uncertainty_shown: "none (descriptive statistics, not an estimated quantity)"
baseline_or_reference: "none needed"
non_conclusions: "does not show any model's performance; scale alone does not imply difficulty"
honesty_checks: {axes_start: "n/a (table)", all_conditions_shown: true, dual_axis: false, "3d": false, cherry_picked: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (table, not a color-coded chart)", min_font_pt_at_print: 7, alt_text: "A table listing each of BEIR's 18 datasets with its task, domain, number of test queries, corpus size, average relevant documents per query, and average query/document length in words."}
placement: "The BEIR Benchmark section, right after the four selection criteria are introduced"
caption: "Table 1. The 18 BEIR zero-shot evaluation datasets. Corpus size and text length vary by orders of magnitude across the nine tasks. Values are as reported in the source paper's own Table 1 (Thakur et al., 2021)."
source_script: "n/a (reconstructed by hand from project/paper.txt; see evidence/research_evidence.json#E011)"
