```yaml
id: TAB-2
purpose: "show the actual diversity of the v0.5 round's 5 submissions -- division, numerics, framework, hardware, and what each was chosen to demonstrate"
rq: N05
takeaway: "The first submission round drew both divisions and five distinct hardware/software categories, each submitter demonstrating a different point in the deployment stack."
claims: [C005, C006]
evidence: [E009, E010]
type: table
comparison_the_eye_must_make: "hardware category and division across the 5 rows, to see the spread rather than convergence on one platform type"
uncertainty_shown: "none (this is a complete enumeration of all 5 v0.5 submissions, not a sample with variance)"
baseline_or_reference: "n/a"
non_conclusions: "does not show accuracy/latency/energy scores achieved by each submission (not recoverable from the extracted text -- see missing_evidence.json MISS-001); does not name the submitting organizations (the source paper itself does not map organization names to rows)"
selection_rule: "n/a -- reproduces all 5 v0.5 submissions, no subset"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, consistent_scales_across_panels: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "n/a (text table)", min_font_pt_at_print: 7, alt_text: "A 5-row table listing each v0.5 submission's division, numeric format, software framework, hardware class, and the specific advantage it was built to demonstrate."}
placement: "Evaluation/Results section, right after the paragraph introducing the v0.5 round"
caption: "The five submissions to the MLPerf Tiny v0.5 round (June 2021). Source: project/paper.txt Table 2 and Section 6.2; see table note on extraction reconstruction for row 5."
source_script: "n/a -- transcribed and reconstructed from project/paper.txt lines 104-190 (Table 2 extraction is damaged; see research_evidence.json E010 notes and claim_evidence_map.json L003)"
```
