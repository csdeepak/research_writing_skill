```yaml
id: TAB-1
purpose: "show that one unmodified generalist agent reaches specialist-range performance on two different software-engineering benchmarks, and that its score scales with backbone-model strength"
rq: RQ2 (N06)
takeaway: "OpenHands' CodeActAgent, unmodified, resolves 26.0% of SWE-Bench Lite issues and fixes 79.3% of HumanEvalFix bugs (0-shot) -- in the range of, though not always above, task-specialist agents."
claims: [C001, C002, C003, C004]
evidence: [E050, E051, E054]
type: table
comparison_the_eye_must_make: "OpenHands' rows against each benchmark's specialist baselines, and across OpenHands' own three backbone models"
uncertainty_shown: "none available (single run per cell); stated in the caption as a scope note, not a fabricated error bar"
baseline_or_reference: "each benchmark's own published specialist agents, listed in the same table"
non_conclusions: "does not show seed-to-seed variance; does not show performance on the other 5 software benchmarks OpenHands was also evaluated on (BIRD, ML-Bench, BioCoder, Gorilla APIBench, ToolQA), whose reported scores could not be recovered with confidence from the extracted table (see missing_evidence.json)"
selection_rule: "all agents/models reported in project/paper.txt's Table 4 for these two benchmarks are shown, except Aider and Moatless Tools (SWE-Bench Lite only), omitted for lacking a citable publication year (see missing_evidence.json MISS-005)"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "not applicable (table, not a chart)", min_font_pt_at_print: 7, alt_text: "A two-part table: SWE-Bench Lite resolve rates and HumanEvalFix pass rates for OpenHands and published baselines, by agent and backbone model."}
placement: "Results, after the paragraph introducing SWE-Bench Lite (R.1) and before HumanEvalFix is discussed (R.3)"
caption: "Table 1. Software-engineering results. Resolve rate on SWE-Bench Lite (300 instances, no hint text) and pass rate on HumanEvalFix (164 Python instances, pass@1, 0-shot for OpenHands). Bold marks OpenHands' own rows. Source: project/paper.txt Table 4 (E050, E051, E054)."
source_script: "not applicable (Markdown table transcribed directly from evidence items, per TASK.md 'Tables may be written in Markdown. No images.')"
```
