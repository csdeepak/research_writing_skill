```yaml
id: TAB-4
purpose: "Present the headline evaluation result: how often each model resolves a real issue under a realistic (BM25) retrieval setting."
rq: N05
takeaway: "Every evaluated model resolves a small minority of instances; figures range from 0.17% to 3.79% under BM25 retrieval on the full benchmark."
claims: [C002, C015]
evidence: [E015, E016, E017, E018, E019, E020, E021, E022]
type: table
comparison_the_eye_must_make: "Resolution rate across models, all under the same BM25-retrieval, full-benchmark condition."
uncertainty_shown: "none reported (Pass@1, single generation per instance; disclosed as a limitation, L005/state.json)"
baseline_or_reference: "n/a (all rows are experimental conditions, no external baseline reported in the evidence package)"
non_conclusions: "Does not establish a single unqualified 'best model' ranking; the source text's 'best-performing' framing and the table's own Claude 3 Opus figure conflict (L006), and both are disclosed rather than resolved by omission."
selection_rule: "All models evaluated on the full benchmark under BM25 retrieval per the evidence package (GPT-4-turbo's figure is a 25% subset, noted in-table)."
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric values in table cells", min_font_pt_at_print: 7, alt_text: "Table of BM25-retrieval resolution rates by model."}
placement: "Results, after R.1"
caption: "Resolution rate by model, BM25 retrieval, full SWE-bench."
source_script: "n/a (values transcribed from research_evidence.json)"
```
