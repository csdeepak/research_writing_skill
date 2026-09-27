```yaml
id: TAB-1
purpose: "Show how the 3-stage filtering pipeline built SWE-bench from raw GitHub activity, establishing the benchmark's provenance and selectivity."
rq: N05
takeaway: "SWE-bench's 2,294 task instances survive a roughly 97.5% reduction from ~90,000 candidate pull requests, via two filtering stages."
claims: [C009]
evidence: [E055, E056, E057]
type: table
comparison_the_eye_must_make: "How the instance count shrinks across three pipeline stages."
uncertainty_shown: "none (exact counts)"
baseline_or_reference: "initial ~90,000 PRs"
non_conclusions: "Does not show what specifically was filtered out at each stage (criteria are described in prose, not broken down numerically here)."
selection_rule: "n/a (full pipeline counts)"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric values in table cells", min_font_pt_at_print: 7, alt_text: "Table showing pipeline stage counts: ~90,000 initial PRs, 11,407 after attribute-based filtering, 2,294 after execution-based validation."}
placement: "Methods, after M.2"
caption: "Construction pipeline: instance counts before and after each filtering stage."
source_script: "n/a (values transcribed from research_evidence.json E055-E057)"
```
