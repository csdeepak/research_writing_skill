```yaml
id: FIG-<n> | TAB-<n>
purpose: ""                 # what job does this visual do for the argument?
rq: ""                      # which research question
takeaway: ""                # ONE true, specific sentence; becomes caption sentence 1
claims: []
evidence: []                # E-ids of the data that generate it
type: ""                    # table | line | dot/strip | box/violin | bar | small multiples | diagram | image panel
comparison_the_eye_must_make: ""
uncertainty_shown: ""       # what error bars / bands represent, n
baseline_or_reference: ""
non_conclusions: ""         # what this visual does NOT show
selection_rule: ""          # for qualitative examples / subsets: how chosen
honesty_checks:
  bar_axis_from_zero: true
  all_conditions_shown: true   # or selection_rule stated
  consistent_scales_across_panels: true
  dual_axis: false
  three_d: false
accessibility:
  colorblind_safe: true
  redundant_encoding: ""
  min_font_pt_at_print: 7
  alt_text: ""
placement: ""               # section + after which paragraph slot
caption: ""
source_script: ""
```
