```yaml
id: FIG-<n> | TAB-<n>
purpose: ""                 # what job does this visual do for the argument?
rq: ""                      # which research question
takeaway: ""                # ONE supported message; a method diagram states purpose/status, not a forced result
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
  min_font_pt_at_print: null # fill from verified venue profile; inspect at final physical size
  alt_text: ""
placement: ""               # section + after which paragraph slot
caption: ""
source_script: ""
presentation:              # optional planning/production metadata, not a new automatic gate
  evidence_state: ""       # measured | executed | implemented | proposed | summary-only
  panel_map: ""
  choice_reason: ""        # why this form fits the reader task
  production_route: ""     # bundled chart renderer | external scientific tool | editable diagram
  source_version_or_hash: ""
  export_path_and_hash: ""
  check_coverage: ""       # actual machine, agent and human checks; unresolved gaps
  final_size_review: "not performed"
```

Add the type-specific provenance fields in `figure_table_rules.md` §8: `source_data` for
results, `components` and `traced_to` for diagrams, `samples` and permissions for images.
Do not fill a human-review field for an agent inspection. Keep unsupported chart types
truthful and record registry/renderer coverage gaps in the representation plan.
