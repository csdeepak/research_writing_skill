```yaml
id: TAB-2
purpose: "Characterize the scale and difficulty of SWE-bench task instances so an adjacent-field reader can calibrate what 'realistic' means here."
rq: N05
takeaway: "A typical SWE-bench instance involves a codebase of thousands of files and hundreds of thousands of lines, and a gold fix touching under 2 files and about 33 lines."
claims: [C001, C008]
evidence: [E003, E004, E005, E006, E007, E008, E009, E010, E011, E012, E013, E014]
type: table
comparison_the_eye_must_make: "Mean vs. maximum for scale statistics; codebase scale vs. patch scale."
uncertainty_shown: "mean and max reported (as in the source); no variance/CI available for these descriptive statistics"
baseline_or_reference: "n/a (descriptive characterization, not a comparison)"
non_conclusions: "Does not show per-repository or per-instance variation beyond mean/median/max; does not show difficulty correlates (flagged as missing_evidence)."
selection_rule: "n/a (full-set descriptive statistics)"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric values in table cells", min_font_pt_at_print: 7, alt_text: "Table of descriptive statistics for issue length, codebase size, and gold-patch size."}
placement: "Methods, after M.3"
caption: "Descriptive statistics for SWE-bench task instances."
source_script: "n/a (values transcribed from research_evidence.json)"
```
