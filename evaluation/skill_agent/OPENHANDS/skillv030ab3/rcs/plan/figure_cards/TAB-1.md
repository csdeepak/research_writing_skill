```yaml
id: TAB-1
purpose: "Which benchmarks were run and at what size?"
rq: "evaluation question (N06)"
takeaway: "Table 1: benchmark suite by category with the subset used"
claims: [C024, C025]
evidence: [E030, E034, E035, E036]
type: table
source_data: ["project/paper.txt"]
comparison_the_eye_must_make: "OpenHands rows against the listed reference rows, per benchmark"
uncertainty_shown: "none: the source reports no variance, seeds or intervals (missing_evidence M003)"
baseline_or_reference: "reference rows are values reported in the source tables"
non_conclusions: "no ordering claim within about one point; no matched-tuning comparison; not a ranking of platforms"
selection_rule: "all rows of the source tables for the benchmarks shown, except cost columns and reference rows for gpt-3.5-class models on some benchmarks (summarized in text)"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric labels", min_font_pt_at_print: 7, alt_text: "Markdown table"}
placement: "S.1"
status: planned
```
