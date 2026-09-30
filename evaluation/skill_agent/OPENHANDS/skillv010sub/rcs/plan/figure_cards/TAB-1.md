```yaml
id: TAB-1
purpose: "ground the headline software-engineering number (26.0% on SWE-Bench Lite) against reproducible open baselines evaluated the same way, including per-instance cost"
rq: N05
takeaway: "OpenHands' generalist agent (26.0%, claude-3.5-sonnet) sits inside the 18.0-27.3% range spanned by five specialized open SWE baselines, and its cheapest configuration costs a fraction of most of them per instance."
claims: [C001, C002]
evidence: [E001, E002, E003]
type: table
comparison_the_eye_must_make: "OpenHands' three backbone-model rows vs. the five specialized-baseline rows; the cost column alongside the resolve-rate column"
uncertainty_shown: "none reported in the source; a table note discloses this explicitly rather than implying precision the source does not report"
baseline_or_reference: "five reproducible open SWE agents (SWE-Agent, AutoCodeRover, Aider, Moatless Tools, Agentless), each evaluated on the same 300-instance subset without benchmark-specific prompt engineering"
non_conclusions: "does not show performance on the full 2294-instance SWE-Bench set, nor any statistical test of the differences shown"
honesty_checks: {all_rows_shown: "all agents/configurations the source reports for SWE-Bench Lite in Table 4, plus the two extra baselines legible in Table 3, are shown -- none omitted", dual_axis: false, three_d: false, cherry_picked: false}
accessibility: {colorblind_safe: "n/a (text table, no color encoding)", redundant_encoding: "n/a", min_font_pt_at_print: "n/a (Markdown table)", alt_text: "Table comparing SWE-Bench Lite resolve rate and per-instance cost across OpenHands' three backbone-model configurations and five reproducible open baselines."}
placement: "Results:Software Engineering, immediately after the paragraph that names SWE-Bench Lite and states the headline number"
caption: "SWE-Bench Lite (300 instances, no hint text, 0-shot): resolve rate and average per-instance cost. OpenHands' claude-3.5-sonnet configuration (26.0%) falls within the range of five reproducible open baselines (18.0-27.3%); no seed/replicate variance is reported for any entry."
source_script: "n/a -- hand-built from evidence items E001-E003"
```
