```yaml
id: TAB-2
purpose: "show the composition and stated purpose of the five v0.5 submissions without asserting per-submission numeric scores that are not recoverable from the paper text"
rq: N05 (RQ)
takeaway: "The first round drew one submission per major TinyML hardware class (general MCU, customized MCU, general-purpose SBC, dedicated accelerator, FPGA), and each explicitly targeted a different layer of the stack."
claims: [C027]
evidence: [E051, E052, E055]
type: table
comparison_the_eye_must_make: "division (closed/open) and platform/framework against what each submission was built to demonstrate"
uncertainty_shown: "none -- this table reports composition, not measured scores; no accuracy/latency/energy numbers are shown because none are recoverable from the extracted text (missing_evidence MISS-4)"
baseline_or_reference: "the closed-division ARM MCU row is the baseline-reference submission; it is listed first"
non_conclusions: "does not show which submission performed best on any metric, and does not show the fine-grained per-cell Dataset/Training/Model modification pattern from the source paper's own Table 2, which is not fully recoverable from extraction (missing_evidence MISS-3)"
selection_rule: "all five v0.5 submissions are shown; nothing was selected out"
honesty_checks: {bar_axis_from_zero: "not applicable (table)", all_conditions_shown: true, consistent_scales_across_panels: "not applicable", dual_axis: false, three_d: false}
accessibility: {colorblind_safe: "not applicable (text table)", redundant_encoding: "column headers plus a plain-language 'demonstrates' column", min_font_pt_at_print: 7, alt_text: "A five-row table listing each v0.5 submission's division (closed or open), hardware platform, numerics, framework, and what it was built to demonstrate."}
placement: "Results section, in the paragraph naming who submitted to the first round (slot R.3)"
caption: "Table 2. The five submissions to the first (v0.5, June 2021) MLPerf Tiny round. Per-submission accuracy/latency/energy scores are not given in the paper text and are not shown here (see Limitations). Source: project/paper.txt, Section 6.1, Table 2 (E051, E052)."
source_script: "not applicable -- transcribed from the source paper's Table 2, restricted to the columns that survived text extraction unambiguously"
```
