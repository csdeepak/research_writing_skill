```yaml
id: TAB-2
purpose: "show, for all 15 benchmarks, where OpenHands' best configuration stands relative to one named comparison baseline, so the reader sees the full pattern behind the generality claim rather than a selection of wins"
rq: N05
takeaway: "OpenHands' best configuration is above its comparison baseline on 11 of 15 benchmarks and below it on 4 (WebArena, MiniWoB++, MINT-code, Entity Deduction Arena), and it is the only agent design evaluated in every one of the three categories."
claims: [C001, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015]
evidence: [E001, E005, E006, E007, E008, E009, E010, E012, E013, E015, E016, E017, E018, E019, E021, E022]
type: table
comparison_the_eye_must_make: "the OpenHands column vs. the comparison-baseline column, per row, across the three category blocks"
uncertainty_shown: "none reported in the source (see Limitations); disclosed in a table note"
baseline_or_reference: "one representative comparison baseline per benchmark, named in the table (the strongest reproducible or most-discussed one for that row); the full baseline sets are in Results prose and in evidence/research_evidence.json"
non_conclusions: "does not show that any specific platform component (vs. the backbone LLM) causes the pattern; does not show statistical significance; not every baseline evaluated per benchmark is repeated here (see Results prose and the evidence map for the rest)"
honesty_checks: {all_conditions_shown: "all 15 evaluated benchmarks are shown, including the 4 where OpenHands trails -- none omitted", dual_axis: false, three_d: false, cherry_picked: false, selection_rule: "one comparison baseline per row = the one already named/discussed in the corresponding Results paragraph; where the paper compares against a range, the strongest or most directly comparable value is shown and the range is given in prose"}
accessibility: {colorblind_safe: "n/a (text table)", redundant_encoding: "n/a", min_font_pt_at_print: "n/a (Markdown table)", alt_text: "Table listing all 15 benchmarks across three categories, OpenHands' best configuration's score, one comparison baseline's score, and whether OpenHands is above or below it."}
placement: "Results:Cross-category Synthesis, immediately after the paragraph introducing the synthesis"
caption: "OpenHands' best configuration versus one named comparison baseline on all 15 evaluated benchmarks. No comparison baseline recurs across rows; no seed/replicate variance is reported for any entry."
source_script: "n/a -- hand-built from evidence items listed above"
```
