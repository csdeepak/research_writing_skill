```yaml
id: TAB-2
purpose: "show that OpenHands' web agent matches a prior domain-general baseline on WebArena but is clearly outperformed by a trained RL specialist on MiniWoB++"
rq: RQ2 (N06)
takeaway: "OpenHands is at or above the prior domain-general-prompting baseline on WebArena (15.5% vs. 14.4%) but trails a trained specialist by a wide margin on MiniWoB++ (40.8% vs. 91.1%)."
claims: [C005, C006]
evidence: [E070, E073]
type: table
comparison_the_eye_must_make: "OpenHands' rows against the domain-general baseline (WebArena Agent) and against trained specialists (AutoWebGLM, Auto Eval & Refine, CC-Net, Workflow-Guided Exploration) in the same column"
uncertainty_shown: "none available (single run per cell)"
baseline_or_reference: "WebArena Agent (domain-general prompting, same style as OpenHands' own Browsing Agent); trained specialists shown in the same rows for contrast"
non_conclusions: "does not show per-domain (shopping/forums/dev-platform/CMS) breakdowns of WebArena; does not show the vision-requiring subset of MiniWoB++ separately"
selection_rule: "all agents/models reported in project/paper.txt's Table 5 for these two benchmarks are shown"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "not applicable (table)", min_font_pt_at_print: 7, alt_text: "A two-part table: WebArena and MiniWoB++ success rates for OpenHands and published baselines, by agent and backbone model."}
placement: "Results, after the paragraph introducing WebArena (R.4) and continuing into the MiniWoB++ negative result (R.5)"
caption: "Table 2. Web-browsing results. Success rate on WebArena (812 instances) and MiniWoB++ (125 environments, full set). Bold marks OpenHands' own rows. Source: project/paper.txt Table 5 (E070, E073)."
source_script: "not applicable (Markdown table transcribed directly from evidence items)"
```
