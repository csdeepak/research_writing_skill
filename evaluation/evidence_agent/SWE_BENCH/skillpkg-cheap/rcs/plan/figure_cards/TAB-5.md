```yaml
id: TAB-5
purpose: "Show that context quantity and precision, not just presence, drive performance, motivating the context-selection interpretation."
rq: N05
takeaway: "Claude 2's resolution rate rises from 1.96% (BM25) to 4.80% (oracle files) to 5.93% (oracle, collapsed to the edited region), while raw BM25 recall of oracle files stays under 51% even at 50k tokens."
claims: [C003, C004, C010, C013, C018]
evidence: [E015, E023, E024, E025, E026, E027, E028, E029, E030]
type: table
comparison_the_eye_must_make: "Resolution rate across retrieval conditions (BM25 at 3 context lengths, oracle, oracle-collapsed) for the same model, alongside BM25 recall at those context lengths."
uncertainty_shown: "none reported for resolution rate (single run per condition)"
baseline_or_reference: "BM25 13k-token condition, the paper's main reported figure (1.96%)"
non_conclusions: "Does not isolate whether the oracle-collapsed improvement is due to noise reduction or information loss trade-off (flagged as missing_evidence, mechanism unexplained in the source)."
selection_rule: "All context/retrieval conditions with a directly evidenced Claude 2 resolution rate or BM25 recall figure."
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric values in table cells", min_font_pt_at_print: 7, alt_text: "Table comparing Claude 2 resolution rate and BM25 recall across retrieval/context conditions."}
placement: "Results, after R.3"
caption: "Effect of context length and precision on Claude 2's resolution rate and on BM25 recall of the oracle files."
source_script: "n/a (values transcribed from research_evidence.json)"
```
