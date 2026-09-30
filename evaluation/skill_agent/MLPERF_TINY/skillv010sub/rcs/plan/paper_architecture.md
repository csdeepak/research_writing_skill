# Paper Architecture: MLPerf Tiny (restructured for adjacent ML researchers)

Story pattern: method_first (Problem -> Method -> Properties -> Evaluation -> Discussion), with a
short Background section inserted before Related Work because the audience (mode B) does not
know TinyML-specific terms yet (audience_assumptions.json).
Audience mode: B (adjacent researcher) - Binding personas: A, B, E - Venue profile:
plan/venue_profile.yaml (generic, all rules assumed:true; TASK.md overrides length/citation
style/no-images).

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Link forward |
|---|---------|---------------|---------------------------|-----------------------|--------|---------|--------|-----------|---------------|
| Ab.1 | Abstract | N01,N04,N05,N07,N10,N12 | Q1,Q3,Q4,Q7,Q10 (first-read subset) | one self-contained miniature of the spine | C001,C004,C005,C006,C012 | CORE | - | TinyML (1) | orients the whole paper |
| I.1 | Introduction | N01,N20 | What is the problem, for whom? | TinyML pushes ML inference under a milliwatt onto MCU-class hardware, unlocking always-on applications | - | CORE | - | TinyML, MCU-class | why comparing solutions is hard |
| I.2 | Introduction | N02 | Why does it matter? | Because every layer of the deployment stack must be co-optimized, a fair yardstick is needed or innovation's impact can't be measured | - | CORE | - | deployment stack | what's missing today |
| I.3 | Introduction | N03,N04 | What is missing from existing approaches? | A general MCU benchmark doesn't test ML workloads, and existing ML benchmarks don't fit MCU memory/power budgets | C009,C010,C011,C012 | CORE | - | - | so we ask |
| I.4 | Introduction | N05 | What exactly do you ask? | Can one suite measure accuracy+latency+energy on MCU hardware while letting a specific contribution be shown and compared? | - | CORE | - | - | how they answer it |
| I.5 | Introduction | N06,N07,N08 | What did you do (one idea)? | Build MLPerf Tiny: 4 reference benchmarks + a fixed 3-metric protocol + a closed/open division split | C001,C003,C004 | CORE | - | closed/open division | what they contribute |
| I.6 | Introduction | N13 | What do you contribute? | Numbered contributions: (1) the suite itself, (2) the joint 3-metric+MCU-fit design closing the gap, (3) evidence from a real first round | C001,C004,C012,C006 | CORE | - | - | paper map |
| I.7 | Introduction | (map) | Where is it in the paper? | one-sentence-per-section map, by question | - | CORE | - | - | Background |
| B.1 | Background | N20 | What is TinyML/MCU-class, concretely? | sub-milliwatt inference, ~10-250 MHz, ~2 orders of magnitude less memory than smartphone ML | - | CORE | - | milliwatt-scale, DUT | why measurement itself is hard here |
| B.2 | Background | N02 (detail from E019) | Why is benchmarking TinyML specifically hard? | four obstacles: ambiguous power-measurement scope, tiny memory, hardware heterogeneity, software/toolchain heterogeneity | - | CORE | - | - | Related Work |
| B.3 | Background | N21,N22 | What do PTQ/QAT and closed/open mean? | quantization-precision vocabulary needed before Table 2 and division rules are legible | C004 | CORE | - | PTQ, QAT, AUC-ROC | Related Work |
| RW.1 | Related Work | N03 (SRC-009) | What does the closest general benchmark do/not do? | CoreMark is the MCU standard but doesn't run or represent ML workloads | C009 | CORE | - | - | what about ML-specific benchmarks? |
| RW.2 | Related Work | N03 (SRC-019,SRC-018) | What do existing ML-inference benchmarks do/not do? | MLMark and MLPerf Inference run real ML workloads but need GB-scale memory, and MLMark skips power while MLPerf Inference excludes MCUs | C010,C011 | CORE | - | - | synthesize the gap |
| RW.3 | Related Work | N04 | So what's actually missing? | none of the three jointly fits MCU-scale + all 3 metrics + reproducible methodology | C012 | CORE | - | - | Methods |
| M.1 | Methods | N07,evidence E023,E024 | What is a "reference implementation" here? | training scripts + pretrained model + C code, run via TFLM on a reference board, fully open-source | - | CORE | - | reference implementation, TFLM | which benchmarks exist |
| M.2 | Methods | N07 | What are the four benchmarks, concretely? | Table 1: one dataset + one MCU-sized model + one quality target per benchmark | C001 | CORE | TAB-1 | DS-CNN, MobileNetV1, autoencoder | how the target numbers were set |
| M.3 | Methods | N07 (E026) | How was each quality target chosen? | each target sits just below the reference model's own measured accuracy/AUC, to absorb cross-platform quantization noise | C002 | CORE | - | - | how latency/energy are measured |
| M.4 | Methods | N07 (E006,E025) | How exactly are latency, energy, accuracy measured? | median of 5 runs for latency/energy (IPS, microjoules/inference, core power only); one full pass for accuracy, gated by a minimum bar | C003 | CORE | - | IPS | how submitters may differ from the reference |
| M.5 | Methods | N08 | What may a submitter change, and under which rules? | closed = fixed dataset/model/target, PTQ-only; open = anything changeable, no mandatory bar, deviations documented | C004 | CORE | - | - | did this work in practice? |
| R.1 | Results | N09 | What would count as the design working? | a real, community-run first round (v0.5, June 2021) is the test: diverse, peer-reviewed submissions vs. a homogeneous or empty round | - | CORE | - | - | what actually happened |
| R.2 | Results | N10 | What happened -- how many, and how varied? | 5 submissions, both divisions, 5 hardware/software categories (Table 2) | C005 | CORE | TAB-2 | RISC-V, HLS, FPGA | what each one showed |
| R.3 | Results | N10 (E012) | What did each submission specifically demonstrate? | one showed a hardware-agnostic toolchain, one an accelerator's efficiency, one a RISC-V AI MCU, one an FPGA HLS workflow | C005 | SUPPORTING | - | - | cross-cutting patterns |
| R.4 | Results | N11 | What patterns cut across all five? | INT-8 dominated numerics; frameworks ranged open-to-proprietary; power spanned uW-W; no one changed the dataset | C007,C008 | CORE | - | - | does this answer RQ? |
| R.5 | Results | N12 | Does this answer the research question? | yes for "accommodates heterogeneity while staying comparable" -- exactly the diversity-plus-structure the design targeted | C006 | CORE | - | - | Discussion |
| D.1 | Discussion | N05,N12 (recap) | Restate the answer to the RQ | the modular, dual-division design let 5 very different submitters each show a distinct advantage under one comparable protocol | C006 | CORE | - | - | how this relates to the gap/prior work |
| D.2 | Discussion | N13,N04 | How does this close the stated gap? | unlike CoreMark/MLMark/MLPerf Inference individually, MLPerf Tiny's first round shows the 3-metric, MCU-fit, reproducible combination working at once | C012,C006 | CORE | - | - | is this being used already? |
| D.3 | Discussion | N18 | Is there evidence of reuse/impact beyond this round? | already cited as a standard TinyML research task elsewhere | C013 | SUPPORTING | - | - | broader stakes |
| D.4 | Discussion | (E015) | What are the field's broader stakes? | on-device inference can widen access and preserve privacy, but the same reach creates surveillance and e-waste risk | - | SUPPORTING | - | - | but what does THIS suite not yet show |
| D.5 | Limitations | N14,N15,N17 | What does one round not establish? | single round/n=5 with no non-modular baseline; unreplicated reference accuracies; narrow closed-division architecture coverage | C002,C005,C006,C001 | CORE | - | - | one more open design tension |
| D.6 | Limitations | N16 | What measurement problem is still unresolved? | excluding feature extraction risks a loophole; including it over-counts its cost in a non-streaming protocol | C003,C004 | CORE | - | - | what comes next |
| D.7 | Discussion/Future | N19 | Where does the suite go next? | new domains with a stable core subset; wider streaming/pre-processing scope; broader architecture coverage (RNNs) | C014,C015,C016 | SUPPORTING | - | - | Conclusion |
| Cn.1 | Conclusion | N13,N12,spine L7 | What is understood now that wasn't before? | a fielded, modular, 3-metric MCU benchmark exists and a real first round shows it accommodates the field's diversity, bounded by one round's evidence | C006,C012 | CORE | - | - | (end) |

## Checks (Gate G2 prerequisites)
- [x] Every story-graph node (N01-N22) appears in >=1 row above.
- [x] The RQ (N05) has result rows (R.1-R.5), interpretation rows (R.5, D.1), and discussion rows (D.1-D.7).
- [x] No row lacks a story node.
- [x] Question ledger: see story/question_ledger.json -- no planned debt beyond the Introduction's paper map.
- [x] Term ledger: see story/term_ledger.json -- every term's defining row (Background, mostly) precedes its first-use row (Methods/Results).
- [x] TAB-1 and TAB-2 each have a completed card (plan/figure_cards/) with a takeaway and an RQ link.
- [x] No SUPPLEMENTARY items are planned (TASK.md allows no appendix/supplement; deep implementation detail such as the specific EMON hardware models is compressed to one clause rather than expanded).
- [x] Negative-result-adjacent findings (E013 no-dataset-change; E016-E018 self-flagged design tensions) are placed in Results (R.4) and Limitations (D.5-D.6), not omitted.
