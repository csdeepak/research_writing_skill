```yaml
id: TAB-1
purpose: "let the reader see, in one place, what each of the 4 benchmarks actually is (dataset, model, size, pass/fail bar) before Methods explains why"
rq: N05
takeaway: "The four benchmarks share one template -- one dataset, one MCU-sized reference model, one numeric quality target -- despite covering four very different tasks."
claims: [C001]
evidence: [E001]
type: table
comparison_the_eye_must_make: "model size (KB) and quality-target metric across the 4 rows, to see the shared template despite different tasks"
uncertainty_shown: "none (this is a specification table, not a measured-with-replicates result)"
baseline_or_reference: "n/a"
non_conclusions: "does not show measured latency/energy, or how the quality target compares to the reference model's own accuracy (that comparison is Table/claim C002, discussed separately)"
selection_rule: "n/a -- reproduces all 4 v0.5 benchmarks, no subset"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (text table)", min_font_pt_at_print: 7, alt_text: "A 4-column table listing, for each of keyword spotting, visual wake words, image classification, and anomaly detection: its dataset, reference model, model size in KB, and quality target."}
placement: "Methods section, right after the paragraph introducing the four benchmarks"
caption: "The four MLPerf Tiny v0.5 benchmarks. Each pairs one dataset, one reference model sized for microcontroller-class memory, and one numeric quality target. Source: project/paper.txt Table 1."
source_script: "n/a -- transcribed from project/paper.txt lines 39-50"
```
