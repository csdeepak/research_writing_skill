# Representation patterns: choose by the reader's task

Use with `../representation_design.md` and `../figure_table_rules.md`. These are options with
conditions, not a checklist of graphics that every paper must contain. Research sources and
the scope of borrowed principles are in [representation_sources.md](representation_sources.md).

## Quantitative evidence

| Reader task / evidence | Useful form | Conditions and common failure |
|---|---|---|
| Find exact values or compare heterogeneous attributes | Table with grouped headers and units | Adjacent comparison columns; explain missing/not-run/not-applicable separately; avoid screenshots of spreadsheets |
| Compare estimates against a baseline | Dot-and-interval plot; aligned differences when paired | Identify the reference and interval definition; preserve pairing; do not derive intervals from rounded means |
| Understand small-sample variation | Individual points, paired points, or a distribution with observations | State the independent unit; repeated observations are not independent sample counts; a violin needs adequate distribution evidence |
| Read change over time, dose, scale or another ordered variable | Line plot or aligned small multiples | Connect meaningful order only; preserve gaps; describe smoothing; training steps are not independent replications |
| Examine association between measured variables | Scatterplot, optionally fit and uncertainty | Units, sample basis and overplotting treatment; association is not causal evidence |
| Compare many methods across conditions | Small multiples or a matrix/table | Maintain method order; shared scales for comparable quantities; separate incompatible units |
| See ablation effects | Component-presence matrix aligned with outcome columns or plots | Each row is a real evaluated configuration; show controls and confounders; absent runs remain absent |
| Examine a dense pattern | Heatmap with a labeled color scale | Sequential colors for magnitude, diverging only with a meaningful center; identify normalization and denominators |
| Understand composition | Stacked bars if categories partition a common whole | Totals and denominators must be compatible; independently computed rates do not form a 100% stack |
| Evaluate a decision system | Confusion matrix, threshold curve or calibration plot as appropriate | Label counts versus rates and row/column normalization; give prevalence/split/threshold where relevant |
| Examine cost-quality tradeoffs | Scatter or aligned cost and quality panels | Same evaluation conditions and hardware where required; do not invent a frontier from unmatched runs |
| Read a few isolated values | Prose, small table, or plot depending on the task | Two estimates with paired uncertainty may deserve a plot; count alone does not decide |

Use radar plots only if their radial geometry adds a necessary task benefit; order and scale
can change apparent area. Prefer aligned dot plots or small multiples for ordinary comparisons.
Avoid 3-D decoration, unmarked broken axes, exaggerated area encodings and gratuitous dual axes.

### Statistical communication contract

For an empirical result, identify metric and direction, evaluation population/split, independent
unit, denominator, aggregation, comparators, and available uncertainty. Distinguish variation
across runs from sampling uncertainty across participants/items. Repeated crops or folds do not
automatically enlarge the independent sample size. State SD, SE, CI or another interval in full
with its method and level; label missing uncertainty rather than fabricate it. Rounding follows
the evidence's useful precision, not the number of digits in a CSV.

Do not use overlapping SD bars as a significance test or a proof of equivalence. Report effect
estimates and their uncertainty where available; a non-significant test alone does not show
no effect. Separate descriptive maxima from statistically supported superiority. A table may
bold the largest observed estimate if that rule is explicit and does not imply significance.

Keep numerical summary tables and plots together only when they answer different reader tasks.
For example, a short plot can show the primary comparison while an appendix table preserves all
exact values. Explain this distinction in the cards instead of repeating every cell in prose.

## Methods, architecture and provenance

- **Overview plus detail:** first show inputs, main stages and outputs. Expand one important
  mechanism in a second panel or figure only when understanding it changes interpretation.
  Use matching labels, ports and component identifiers across both levels.
- **Distinct flows:** differentiate data, control, training and inference flows with labeled
  arrows or separated lanes. An arrow states a relationship; label ambiguous relationships.
  Draw external services and human decisions across explicit system boundaries.
- **State and scope:** show proposed or optional modules distinctly. A diagram reflects a
  named implementation or protocol, not an aspirational combination of alternatives.
  Do not add familiar blocks such as attention, preprocessing or feedback without a source.
- **Data / participant / study flow:** show source, eligibility, exclusions and final analysis
  sets when attrition affects interpretation. Counts must reconcile; distinguish patients,
  images, teeth, patches, runs or studies. Branches need not sum if explicitly overlapping.
- **Theory:** a dependency diagram can distinguish assumptions, lemmas and conclusions; a
  compact worked example can clarify symbols. Neither substitutes for proof.
- **Graphical abstract:** use only if requested or useful for the venue. Reduce to the main
  question, approach and supported message. It does not replace a scientific overview or make
  an unsupported result acceptable. Avoid decorative icons whose apparent meaning is untrue.

## Qualitative evidence and example images

Use aligned rows for cases and columns for input/reference/output/error when that comparison
fits the data. Keep the same case, crop, scale and method order across columns. A magnified
inset needs a marked source region. Show whole-image context if a crop could conceal failure.
Do not invent a physical scale bar when pixel spacing is unknown.

Declare selection before polishing the panel: random sample, predefined strata, common error,
edge case, or explicitly illustrative case. Include relevant failures and uncertain outcomes
alongside successes. Save sample IDs and the selection seed or deterministic rule. Example
panels illustrate mechanisms and failures; they do not estimate population performance.
Disclose transformations; do not selectively enhance, remove or synthesize experimental content.

For interview, field or textual studies, a theme/evidence matrix or carefully attributed excerpt
may be more useful than an image. Retain divergent cases and analysis context. Do not turn theme
mentions into prevalence claims unless the sampling and analysis support that interpretation.
Respect consent, privacy and reuse permissions for images and quotations.

## Layout, captions and reading order

Give each multi-panel figure a single reader question; let panels perform complementary jobs.
Use an explicit panel map in the caption. Align comparable panels and use whitespace to group
them. Remove repeated legends where a shared legend is genuinely unambiguous. When labels need
to become too small, simplify, split or move secondary detail; do not shrink without inspection.
The architecture and performance figures should look like parts of the same paper without
forcing identical encoding on different information types.

Caption pattern for results: **supported message → panel map → what/where/how measured → sample
basis and uncertainty → encoding/selection → scope limit where necessary**.
Caption pattern for methods: **purpose and status → panel map/process → arrow/line meanings →
implementation/source scope**. A methods caption need not pretend to be a finding.
Do not claim a result while its panel is only planned. Do not repeat the entire Methods section.

Tables benefit from concise group headings, units in headers, comparable precision, visual
separation of groups and restrained rules. Align numeric columns for comparison; wrap long
labels rather than rotate whole tables by default. A landscape table can be appropriate in a
supplement if legible and permitted. Caption location follows the venue, not a universal rule.

Use non-color cues as well as semantic colors. Inspect grayscale readability where relevant;
write alt text that communicates the visual's function and supported message. Avoid relying on
red/green distinctions alone. Choose vector output for editable line art where accepted and
adequate raster resolution for images at their actual final size; do not rasterize text merely
for convenience. Check the final PDF, not only an enlarged editor view.
