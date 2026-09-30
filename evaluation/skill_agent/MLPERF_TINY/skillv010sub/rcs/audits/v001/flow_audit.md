# Step 13 -- Logical-flow audit (draft v001)

## Paragraph level
Sampled every paragraph against the paragraph model (role / point-first / evidence / link-back /
link-forward; `information_design.md` section 1). All paragraphs open with their point or a
direct link back to the previous paragraph's stress position (e.g. Methods' quality-target
paragraph opens "Every quality target in Table 1 sits a small margin below..." picking up
Table 1 from the sentence before it). No paragraph buries its point in a final sentence outside
the two narrative build-up spots (Intro P1, Background P1) where a short context-first opening is
the deliberate move (`information_design.md` section 1 exception for introductions).

## Section level
- Introduction ends with the paper map (Q-in-ledger sense: "The rest of the paper is organized
  around these questions...") -- satisfies section_rules.md's INTRODUCTION exit check.
- Each Results subsection opens with the question it answers (R1: "whether this design actually
  accommodates..."; R5 explicitly: "This answers the paper's research question...").
- Discussion opens with a direct, per-RQ-style answer (D1) before moving to relation-to-prior-work
  (D2), impact (D3), broader impact (D4), and only then Limitations -- matches section_rules.md's
  DISCUSSION default structure order.
- Limitations are placed as a labelled subsection inside Discussion (venue profile has no
  separate Limitations heading requirement beyond `limitations_section_required: true`, which a
  clearly labelled subsection satisfies).

## Transitions
Checked every connective for a true relation (`information_design.md` section 4):
- "however" (Related Work, Introduction): each instance precedes a real contrast (CoreMark's
  ease of use *however* not extending to ML workloads; MLMark's realism *however* not extending
  to MCU scale) -- true.
- "because" (Methods, Results): each instance precedes a real methodological or logical
  consequence (measurement protocol -> comparability; single round -> unverified generality) --
  true, and `lint_draft.py`'s B5-causal check found these are INFO-level only (not causal-overreach
  ERRORs), consistent with them describing design/inference logic rather than causal claims about
  results.
- No "Moreover/Furthermore/Additionally/In addition/Besides/Also" sentence-openers were used
  anywhere in the draft (checked by hand and by `lint_draft.py`'s A15 check, which fired at 0
  instances) -- so there is no decorative-transition pattern to flag.

## Old -> new information (S01 / topic-stress positions)
Spot-checked the Results -> Discussion boundary and the Methods internal flow: each paragraph's
last clause (stress position) is picked up as the next paragraph's opening topic (e.g. Methods'
protocol paragraph ends on "...remain comparable even though their surrounding measurement
hardware differs", and the next paragraph opens "The suite resolves the comparability-versus-
flexibility tension..." -- "comparability" is the carried-over word). No paragraph introduces its
topic cold without linking to the prior stress position.

**No `A1` (late question), `A2` (buried contribution), `A8` (disconnected experiments -- there is
only one experiment/chain here, and its `NEXT` field in story_graph.json is filled), `A10`
(discussion amnesia), or `A15` (decorative transitions) instances found.**
