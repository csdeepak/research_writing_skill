```yaml
id: TAB-3
purpose: "Show how much of SWE-bench each model can even see, given its context window, before any evaluation of quality."
rq: N05
takeaway: "Smaller-context models (ChatGPT-3.5) fit fewer than 60% of instances in-context, while Claude 2's 100k-token window fits over 96%."
claims: [C014]
evidence: [E034, E035, E036, E037, E038, E039]
type: table
comparison_the_eye_must_make: "Context window size vs. percentage of instances covered, across models."
uncertainty_shown: "none (exact coverage percentages under oracle-retrieval token counts)"
baseline_or_reference: "n/a"
non_conclusions: "Coverage does not imply the model uses the available context well (see R.2-R.3)."
selection_rule: "n/a (all evaluated models with a reported context window)"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric values in table cells", min_font_pt_at_print: 7, alt_text: "Table of model context windows and percentage of SWE-bench instances that fit."}
placement: "Methods (Experimental Setup), after M.5"
caption: "Model context windows and coverage of SWE-bench instances."
source_script: "n/a (values transcribed from research_evidence.json)"
```
