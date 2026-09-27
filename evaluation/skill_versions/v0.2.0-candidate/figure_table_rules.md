# Figure and Table Rules

A figure must earn its place (F0 Unit 3: "A graphic should serve a purpose"). Never make a
figure because "papers have figures".

---

## 1. The Figure/Table Card (`plan/figure_cards/<id>.md`); written *before* the visual is final

```yaml
id: FIG-3
purpose: "show that error grows with shift magnitude for baselines but not for M"
rq: RQ2
takeaway: "Baseline error rises roughly linearly with shift; M stays within noise up to s=0.6."   # ONE sentence, true, specific
claims: [C009, C010]
evidence: [E020, E021]                 # data files that generate it
type: line plot                        # chosen by §2
comparison_the_eye_must_make: "slopes of M vs baselines"
uncertainty_shown: "shaded 95% CI across 5 seeds"
baseline_or_reference: "dashed line = noise floor (E024)"
non_conclusions: "does not show behavior beyond s=0.6 (not tested)"
honesty_checks: {axes_start: "y at 0 (bar)/justified", all_conditions_shown: true, dual_axis: false, 3d: false, cherry_picked: false}
accessibility: {colorblind_safe: true, redundant_encoding: "marker shapes", min_font_pt_at_print: 7, alt_text: "..."}
placement: "Results §4.2, after the paragraph introducing RQ2"
caption: "…"                           # §3
source_script: "plots/fig3.py"         # reproducibility
```

A card with an empty `takeaway` or `rq` means the visual has no job. Drop it or move it to the
supplement.

---

## 2. Figure or table?

| If the reader needs to… | Use |
|--------------------------|-----|
| Look up exact values; compare many attributes; reproduce | **Table** |
| See a trend, shape, distribution, interaction, or relative size | **Figure** |
| Understand a process, architecture, or pipeline | **Diagram** (block/flow) |
| See what something looks like, or qualitative outputs | **Image panel**, with labels and chosen examples plus a selection rule |
| Compare two or three numbers | **Prose**. No visual needed. |

Chart choice (from F0 Unit 3, modernized with S24):
- Distributions and variability: box/violin/strip or dot plots showing individual points when n
  is small. Avoid mean-only bar charts for continuous data.
- Trends over an ordered variable: line plot with markers and uncertainty bands.
- Part-to-whole: stacked bars or a plain bar chart. Pie charts only for ≤5 parts with large
  differences, or not at all.
- Many conditions × methods: small multiples with shared axes.
- **Never** 3-D charts for 2-D data, dual y-axes without strong justification, or decorative
  images.

**Ordering:** figures appear in the order of the argument (question order). Figure 1 should be
the one that orients the reader: the problem, the approach, or the headline result.

---

## 3. Captions

- **First sentence = the takeaway** (a declarative finding), not a description ("Comparison of
  methods").
- Then: what is plotted (axes, units), the conditions, n/seeds, what the error bars mean,
  abbreviations, and the data source.
- A table caption says what is compared and what the bold/underline marks mean (e.g. "bold =
  best mean; entries within one std of best are underlined"). Highlight rules must be honest:
  don't bold a best value that sits within noise without saying so.
- The caption must be understandable without the main text, and the takeaway must also appear
  in the prose.

## 4. Integration with the text (F0 Unit 3)
1. Refer to the visual by number *before* it appears ("Figure 3 shows…"), never "the figure
   below".
2. State in the prose what the reader should see: the takeaway plus the comparison.
3. Connect it to the RQ.
4. If the visual is SUPPLEMENTARY, cross-reference it ("Appendix Table B2").

## 5. Visual honesty (F0 Unit 2 "misleading visuals", extended)
- Bar charts start at zero. For line and dot plots, non-zero axes are fine when labeled and the
  differences are not presented as larger than they are.
- Show all conditions that were run for the comparison, or state the selection rule.
- Show uncertainty when replicates exist, and say what it represents.
- Use consistent scales across panels that invite comparison. Label deviations from this.
- Qualitative examples: state how they were chosen (random, worst-case, best-case). If
  cherry-picked, say so.
- No image manipulation beyond uniform adjustments, which must be disclosed.
- Log scales are labeled as such.

## 6. Tables (F0 Unit 3 table construction, kept)
- Numbered, with a descriptive title. Row and column headers with units. Consistent decimals
  (no more precision than the uncertainty justifies). Aligned decimals. Missing entries marked
  with an explained symbol (—, n/a). Footnotes for abbreviations. Source noted.
- Put the columns to compare side by side. Put reference rows (baseline) first or visually
  distinct.
- Limit to what answers the RQ. Move full tables to the supplement.

## 7. Accessibility
- Colorblind-safe palette plus redundant encoding (marker, line style, label).
- Minimum text size about 7 pt at print width.
- Alt text (1–2 sentences: type, variables, takeaway) where the venue supports it.
- Direct labeling instead of legends where possible.
