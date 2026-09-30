# Paper Architecture: MLPerf Tiny -- presented to adjacent ML researchers

Story pattern: method_first (Problem -> Method/design -> validation results -> discussion). Chosen
because the source material is a systems/benchmark-suite contribution (a designed artifact
validated by reference-implementation runs and a real submission round), not a single-hypothesis
experiment; `research_story.md` SS6 recommends method_first for "new method or system."

Audience mode: B (adjacent ML researcher) . Binding personas: A, B, E . Venue profile:
`plan/venue_profile.yaml` (assumed rules: structure/required-statements; NOT assumed: length and
citation style, which come directly from TASK.md).

Length limit (main text): 4500 words (min 3000) . Planned total below: ~4150 words (~92% of the
limit -- slightly over the skill's usual "<=90%" guideline because there is no supplement/appendix
in this single-file deliverable to relocate overflow into; the actual draft is metered against the
hard 4500 cap with `tools/lint_draft.py`, not against this planning estimate).

No images (TASK.md). Both planned visuals are Markdown tables (TAB-1, TAB-2); there are no FIG
cards in this architecture.

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Words | Link forward |
|---|---------|---------------|---------------------------|-----------------------|--------|---------|--------|-----------|-------|--------------|
| Ab.1 | Abstract | N01,N04,N05,N08,N16,N18,N20 | Whole-paper miniature | Problem, gap, question, approach, key finding with magnitudes, meaning, main limit | C033,C006,C007,C027,C030 | CORE | -- | TinyML, MCU | 220 | -- |
| I.1 | Introduction | N01,N02 | What is the problem and why care? | TinyML puts inference under a milliwatt, which is valuable but currently uncomparable across systems | C001,C033 | CORE | -- | TinyML, on-device inference | 140 | so how would we compare such systems fairly? |
| I.2 | Introduction | N06 | What resource envelope are we even talking about? | TinyML hardware runs at 10-250 MHz under 50 mW, several orders below phone/GPU-class deployment | -- (background) | CORE | -- | MCU-class, DUT | 90 | this gap in scale is exactly why existing benchmarks don't fit |
| I.3 | Introduction | N03,N04 | What is missing from existing approaches? | Three prior benchmarks each miss one required property (ML-representativeness, MCU-fit, or power) | C003,C004,C005,C006 | CORE | -- | PTQ (glossed) | 150 | so the authors ask... |
| I.4 | Introduction | N05 | What exactly do you ask? | Explicit RQ: one suite, fitting MCU constraints, measuring accuracy+latency+energy, fair across heterogeneous stacks | -- | CORE | -- | -- | 70 | here is what they built to answer it |
| I.5 | Introduction | N07,N08,N19 | What did you do and find, and where is it in the paper? | Numbered contributions (suite design; reference validation; first-round evidence) tied to results, plus paper map | C007,C026,C027 | CORE | -- | closed/open division | 180 | Section 2 gives the background a reader needs first |
| B.1 | Background & Related Work | N01,N02 | What does "TinyML" assume the reader already knows? | On-device inference under 1 mW enables always-on, private, battery-powered use, avoiding wireless energy cost | C001 | CORE | -- | wakeword | 130 | but building anything at this scale is unusually constrained |
| B.2 | Background & Related Work | N03 (approach: 4 challenges) | Why is benchmarking TinyML systems specifically hard? | Four coupled constraints: power-measurement scope, 100x-smaller memory, hardware heterogeneity, software/toolchain heterogeneity | C002 | CORE | -- | SUT | 160 | these are exactly the criteria the closest prior benchmarks fail |
| B.3 | Background & Related Work | N03,N04 | What is missing from existing approaches (in dimension form)? | CoreMark isn't ML-representative; MLMark and MLPerf's inference suite assume GB-scale memory and (for MLMark) skip power | C003,C004,C005 | CORE | TAB none (kept in prose; only 3 items) | TFLite Micro (glossed) | 170 | the authors state this gap directly, and it motivates one suite |
| B.4 | Background & Related Work | N04 | So what's the actual gap? | None of the three is simultaneously ML-representative, MCU-fitting, and power-aware; the authors say so explicitly | C006 | CORE | -- | -- | 110 | this is the gap MLPerf Tiny is built to close |
| M.1 | Method | N07,N08 | What did they build, in one idea? | Four fixed reference benchmarks + a shared 3-metric harness + a modular open/closed structure | C007,C008 | CORE | -- | reference implementation | 150 | first, the division structure that makes comparison fair |
| M.2 | Method | N08 (closed/open) | How is a fair comparison enforced while still allowing innovation? | Closed division fixes model/data/threshold (PTQ only); open division allows changing them but keeps the test set | C009 | CORE | -- | PTQ, QAT | 160 | second, exactly how latency/accuracy/energy are scored |
| M.3 | Method | N08 (protocol) | How exactly is each metric measured? | Median-of-5-runs protocol for latency/energy; full-validation-set pass for accuracy; one power supply only (anti-gaming) | C010 | CORE | -- | IPS | 170 | with the rules fixed, what are the four actual tasks? |
| M.4 | Method | N08,N09 | What are the four tasks, side by side? | Table (TAB-1) orients dataset/model/threshold per benchmark before the per-task walkthroughs | C007 | CORE | TAB-1 | -- | 90 | starting with visual wake words |
| M.5 | Method | N09,N10 | Why this task, this data, this model, this bar? (VWW) | VWW = person detection for doorbell/occupancy use; MobileNetV1 reaches ~86%; threshold set to 80% for quantization headroom | C011,C012,C013 | CORE | -- | -- | 130 | image classification follows a similar pattern with one twist |
| M.6 | Method | N09,N11 | Why this task, this data, this model, this bar? (IC) | CIFAR-10 continues a TinyML precedent; the reference ResNetv1 is shrunk and loses pooling for the low-res input; 86.5%/85% | C014,C015,C016,C017 | CORE | -- | residual stack (glossed) | 150 | keyword spotting adds a second design tension: words vs. open sound |
| M.7 | Method | N09,N12 | Why this task, this data, this model, this bar? (KWS) | 12-class design balances closed-vocabulary and open-set needs; 38.6K-parameter CNN reaches 92.2%/91.6%/91.7%; threshold 90% | C018,C019,C020,C021 | CORE | -- | depthwise-separable CNN (glossed) | 160 | anomaly detection is the one unsupervised, non-classification task |
| M.8 | Method | N09,N13 | Why this task, this data, this model, this bar? (AD) | Toy-car-only DCASE2020 subset; FC autoencoder reconstructs spectrograms; AUC 0.88/0.86 fp32/quantized; threshold 0.85 | C022,C023,C024,C025 | CORE | -- | log-mel-spectrogram (glossed), AUC-ROC (glossed) | 170 | with the suite specified, did it actually run, and who used it? |
| R.1 | Results | N05 (reopen) | Did the suite work, and was it exercised by real submitters? | Two-part evidence: reference validation on one board, then a first external submission round | -- | CORE | -- | -- | 60 | first, the reference implementations themselves |
| R.2 | Results | N14,N15 | Do the reference implementations meet their own targets? | All four met their accuracy targets on the reference board; latency/energy spread widely (qualitative; exact figures unavailable here) | C026 | CORE | -- | -- | 110 | second, what happened when the suite went external |
| R.3 | Results | N16 | Who submitted, and on what hardware? | Five results: 4 closed (ARM MCU, RISC-V MCU, RasPi4+toolchain, NN accelerator), 1 open (FPGA); table (TAB-2) lists each | C027 | CORE | TAB-2 | RISC-V (glossed) | 160 | each submission targeted a different layer of the stack |
| R.4 | Results | N17 | What patterns crossed the whole round? | INT8 dominant; frameworks ranged open-interpreter to hardware compiler; power spanned microwatts to watts | C028 | CORE | -- | -- | 120 | one thing every submitter left untouched |
| R.5 | Results | N17 | What did no one change? | No submitter modified the training dataset, against AI's broader data-centric trend; the authors note this directly | C029,C030 | CORE | -- | -- | 100 | what does this pattern, taken together, mean? |
| D.1 | Discussion | N05,N18 | So, does the suite answer the RQ? | Yes for the tested round: modular design + 3 metrics let 5 very different stacks report comparable, informative results | C030 | CORE | -- | -- | 130 | why would a modular design achieve that? |
| D.2 | Discussion | N18,N23 | Why did modularity work (mechanism)? | Fixing the reference implementation as a swappable baseline let each submitter isolate one stack layer without re-deriving the whole pipeline | C030 | CORE | -- | -- | 130 | but the round also shows a boundary on that success |
| D.3 | Discussion | N17,N18 | What did the round NOT show? | Diversity was in models/frameworks/hardware, not data; TinyML practice, per the authors, stayed non-data-centric in this round | C029,C030 | CORE | -- | -- | 120 | so what should a reader take away for practice? |
| D.4 | Discussion | N19,N23 | What does this mean for the field? | A 3-metric, modular suite is a workable way to standardize a fragmented hardware/software landscape without forcing one stack | C030 | CORE | -- | -- | 110 | that said, the authors are explicit about where this stops |
| L.1 | Limitations | N20 | What do the authors themselves concede (design)? | Streaming/pre-processing measurement is unresolved; closed division covers only FC/CNN; stability is a goal, not yet demonstrated | L001,L002 (author_stated) | CORE | -- | -- | 170 | the authors also flag a broader, non-technical caveat |
| L.2 | Limitations | N21 | What do the authors themselves concede (broader impact)? | Dual-use (surveillance) and e-waste risk are named directly by the authors as a caveat on the suite's benefit | L003 (author_stated) | CORE | -- | -- | 90 | "Additional caveats." (writer-derived, separate paragraph) |
| L.3 | Limitations | N22 | What further caveats apply (writer-derived)? | Evidence is one round of five results on one board; no per-submission scores or run variance appear in the paper text itself | L004,L005 (writer_derived) | CORE | -- | -- | 140 | -- |
| C.1 | Conclusion | N19,N23,N24 | What is now understood, and what's next? | A modular, 3-metric benchmark suite for MCU-class ML now exists and produced comparable first-round evidence; next rounds test data-centricity, new architectures, and stability | C030,C032 | CORE | -- | -- | 160 | -- |

Sigma words (Abstract + body, excluding References) approx: 220 + 630(I) + 570(B) + 1180(M) + 550(R) + 490(D) + 400(L) + 160(C) = **4200**, within the 3000-4500 word requirement.

## Checks (ticked before Gate G2)
- [x] Every story-graph node (N01-N24) appears in >=1 row (N01 Ab.1/I.1/B.1; N02 I.1/B.1; N03 I.3/B.2/B.3; N04 I.3/I.4?no-I.3/B.3/B.4; N05 I.4/R.1/D.1; N06 I.2; N07 I.5/M.1; N08 I.5/M.1-M.3; N09 M.4-M.8; N10-N13 M.5-M.8; N14 R.1; N15 R.2; N16 R.3; N17 R.4/R.5/D.3; N18 D.1-D.3; N19 I.5/D.4/C.1; N20 L.1; N21 L.2; N22 L.3; N23 D.2/D.4/C.1; N24 C.1).
- [x] Every RQ (N05) has result rows (R.1-R.5), interpretation rows (D.1-D.3), and discussion rows (D.1-D.4).
- [x] No row without a story node.
- [x] Question ledger: no planned debt beyond the introduction's own forward pointers (<=3; see `story/question_ledger.json`).
- [x] Term ledger: every term's defining row precedes its first-use row (see `story/term_ledger.json`).
- [x] Both visuals (TAB-1, TAB-2) have a card with a takeaway and an RQ link (`plan/figure_cards/TAB-1.md`, `TAB-2.md`).
- [x] No SUPPLEMENTARY items: this is a single-file deliverable with no appendix; anything SUPPLEMENTARY-class (full hyperparameter grids, firmware API listing, EMON hardware list) is placed at OPTIONAL density in-line as one clause, or omitted rather than left dangling. Nothing reproducibility-critical to the paper's own claims was cut (the underlying MLPerf Tiny GitHub repo remains the reproducibility artifact, per the source paper itself).
- [x] Every `author_stated` limitation (L001, L002, L003) has a Limitations row (L.1, L.2); writer-derived caveats (L004, L005) have a separate "Additional caveats" row (L.3).
- [x] Every rationale claim (C001, C008-C011, C013-C015, C017-C018, C020-C023, C025) has an Introduction/Background/Method row (I.1, M.1-M.8).
- [x] Sigma words (4200) <= the 4500 main-text limit (93%); the plan intentionally runs closer to the ceiling than the skill's usual 90% guideline because there is no appendix to relocate overflow into in this single-file deliverable -- the actual draft's word count is what the length gate checks, not this estimate.
