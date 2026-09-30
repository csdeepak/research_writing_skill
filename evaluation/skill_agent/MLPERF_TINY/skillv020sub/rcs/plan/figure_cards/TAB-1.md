```yaml
id: TAB-1
purpose: "let the reader compare the four benchmark tasks' dataset, model, size, and quality target side by side before reading the four per-task walkthroughs"
rq: N05 (RQ)
takeaway: "The four benchmarks span audio, two vision tasks, and anomaly detection, but every reference model is under 330 KB, so the memory constraint -- not the task -- is what unifies the suite."
claims: [C007, C012, C016, C019, C024]
evidence: [E013, E018, E025, E030, E033, E041]
type: table
comparison_the_eye_must_make: "model size and quality-target metric across four unrelated task types"
uncertainty_shown: "none (single reported values; see limitations L004/L005 for why no variance is shown)"
baseline_or_reference: "not applicable -- this table has no baseline row; it specifies the four reference tasks themselves"
non_conclusions: "does not show latency or energy (Section on Results, TAB-2, and the qualitative Figure-5 summary cover those); does not show accuracy variance across runs (unavailable, see L005)"
selection_rule: "all four v0.5 benchmarks are shown; nothing was selected out"
honesty_checks: {bar_axis_from_zero: "not applicable (table, not a bar chart)", all_conditions_shown: true, consistent_scales_across_panels: "not applicable", dual_axis: false, three_d: false}
accessibility: {colorblind_safe: "not applicable (text table)", redundant_encoding: "column headers plus units in parentheses", min_font_pt_at_print: 7, alt_text: "A four-column table listing, for each of keyword spotting, visual wake words, image classification, and anomaly detection: its dataset and input size, its reference model and model size in KB, and its quality target metric and value."}
placement: "Method section, after the paragraph introducing the four benchmarks together (slot M.4), before the per-task walkthroughs (M.5-M.8)"
caption: "Table 1. The four MLPerf Tiny v0.5 reference benchmarks. Every reference model fits under 330 KB; quality targets are Top-1 accuracy for the three classification tasks and AUC-ROC for anomaly detection. Source: project/paper.txt, Section 4, Table 1 (E013)."
source_script: "not applicable -- transcribed directly from the source paper's Table 1; no new computation"
```
