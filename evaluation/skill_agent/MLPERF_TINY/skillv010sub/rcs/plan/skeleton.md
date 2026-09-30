# Research skeleton (one topic sentence per paragraph slot, claim-tagged)

**Title.** MLPerf Tiny: a community benchmark suite for accuracy, latency, and energy on microcontroller-class machine learning.

**Abstract.** [One paragraph: TinyML needs a standardized way to compare hardware/software solutions; no existing benchmark fits; MLPerf Tiny is a modular, open, four-benchmark suite that measures all three metrics on MCU-class hardware {C001,C004}; its first submission round drew diverse submissions across both divisions and five hardware/software categories {C005}, consistent with the design achieving its comparability-plus-flexibility goal {C006}; main scope limit: one round, n=5 {L001}.]

## Introduction
- I.1 TinyML performs ML inference under a milliwatt on MCU-class hardware, enabling always-on, battery-powered applications that mobile-scale ML cannot reach.
- I.2 Because every layer of the deployment stack must be co-optimized to fit these budgets, comparing solutions fairly -- and isolating what any one optimization contributes -- is difficult without a common yardstick.
- I.3 A general MCU benchmark does not test ML workloads, and the ML-inference benchmarks that do exist need memory or runtime budgets MCU-class hardware cannot provide, or do not measure power {C009,C010,C011,C012}.
- I.4 This paper asks: can one suite fairly measure accuracy, latency, and energy for representative ML workloads on MCU-class hardware, while still letting a specific hardware or software contribution be demonstrated and directly compared against a common reference?
- I.5 MLPerf Tiny answers this with four reference benchmarks, a fixed three-metric measurement protocol, and a closed/open division split that trades comparability against flexibility {C001,C003,C004}.
- I.6 Contributions: (1) four open reference implementations pairing a dataset, an MCU-sized model, and a calibrated quality target {C001,C002}; (2) a protocol and division structure that make accuracy, latency, and energy jointly comparable on MCU-class hardware for the first time among the benchmarks examined {C004,C012}; (3) evidence from a real first submission round that the design accommodates the field's hardware and software diversity {C006}.
- I.7 The paper explains the TinyML setting adjacent researchers need (Background), locates the gap in prior benchmarks (Related Work), describes the suite (Methods), reports the first submission round (Results), and discusses what it does and does not establish (Discussion).

## Background: The TinyML Setting
- B.1 TinyML devices run inference at roughly 10-250 MHz, under about a milliwatt, with memory about two orders of magnitude below smartphone-class ML hardware.
- B.2 This resource envelope creates four obstacles a benchmark must accommodate: an ambiguous scope for power measurement, memory too small for standard ML benchmarks' models, hardware heterogeneity (MCUs to novel accelerator architectures), and software heterogeneity (custom toolchains tightly coupled to specific hardware).
- B.3 Two vocabulary items matter before Methods: post-training quantization (PTQ) versus quantization-aware training (QAT), which distinguish the closed and open divisions {C004}; and AUC-ROC, the threshold-free accuracy metric used for the one benchmark whose output is a score rather than a class label.

## Related Work
- RW.1 CoreMark is the standard MCU-class benchmark, but it does not profile full programs or represent ML inference workloads {C009}.
- RW.2 MLMark and MLPerf Inference run real ML workloads, but MLMark's models need far more memory than MCUs provide and skip power measurement, while MLPerf Inference currently excludes MCU-class and other resource-constrained platforms {C010,C011}.
- RW.3 None of the three jointly measures accuracy, latency, and energy on MCU-class hardware with a reproducible methodology -- the gap this paper's suite targets {C012}.

## The MLPerf Tiny Benchmark Suite (Methods)
- M.1 Each benchmark ships as an open-source reference implementation -- training scripts, a pretrained model, and C code -- run via TFLite Micro on a reference board.
- M.2 The four benchmarks (keyword spotting, visual wake words, image classification, anomaly detection) each pair one dataset with one MCU-sized reference model and one numeric quality target (Table 1) {C001}.
- M.3 Each quality target is set a small margin below the reference model's own measured accuracy or AUC, to absorb cross-platform quantization and rounding differences {C002}.
- M.4 Latency and energy are each the median of five repeated runs (inferences-per-second; core-only microjoules per inference), and accuracy comes from one full pass over the validation set, gated by a minimum-accuracy check {C003}.
- M.5 The closed division fixes dataset, model, and quality target and allows only post-training quantization; the open division allows changing dataset, training, or model, drops the mandatory accuracy bar, and requires documenting every deviation {C004}.

## Evaluation: The v0.5 Submission Round (Results)
- R.1 Whether this design actually accommodates the field's diversity can only be tested by real submitters, so the authors solicited and peer-reviewed a first round (v0.5, June 2021).
- R.2 Five submissions arrived, spanning both divisions and five hardware/software categories, from an ARM MCU to an FPGA trained with quantization-aware learning (Table 2) {C005}.
- R.3 Each submission targeted a different point in the deployment stack: a hardware-agnostic software toolchain, an accelerator's efficiency, a RISC-V AI microcontroller, and an FPGA high-level-synthesis workflow, among others.
- R.4 Across all five, INT-8 was the dominant numeric format, frameworks ranged from open interpreters to hardware-specific compilers, measured power spanned microwatts to watts, and none of the five changed the training dataset {C007,C008}.
- R.5 This range of divisions, hardware, and software choices is consistent with the modular design achieving its intended goal: accommodating heterogeneity while the closed division kept results directly comparable {C006}.

## Discussion
- D.1 The first round therefore answers the research question affirmatively for the case tested: a single suite let five different submitters each show a distinct advantage under one shared, comparable protocol {C006}.
- D.2 This closes the gap identified in Related Work by combining what no single prior effort combined: MCU-scale fit, all three metrics, and a reproducible, modular methodology {C012}.
- D.3 The suite is already being reused as a standard task set in TinyML research beyond this paper {C013}.
- D.4 On-device inference of this kind can widen access to ML and keep data on-device, but the same reach could enable unwanted monitoring and adds to electronic waste as devices proliferate.
- D.5 The evidence that the design "works" rests on one round with five submissions and no non-modular baseline suite for comparison, and the reference accuracy figures behind each quality target carry no reported retraining variance {L001,L002}.
- D.6 The authors themselves flag two unresolved design tensions: excluding feature extraction from the measured window risks a loophole, while including it would over-count feature-extraction cost in a non-streaming protocol; and the closed division's architectures still cover mainly FC/CNN layers {L004,L005}.
- D.7 Planned or needed extensions include new application-domain benchmarks alongside a stable long-term core, wider measurement scope for streaming/pre-processing, and broader closed-division architecture coverage such as RNNs {C014,C015,C016}.

## Conclusion
- Cn.1 MLPerf Tiny gives the TinyML community an open, modular suite that jointly measures accuracy, latency, and energy on MCU-class hardware, and its first real submission round shows that design accommodating exactly the hardware and software diversity it targeted, bounded by the evidence of a single round {C006,C012,L001}.

---

## Gate G2 self-reconstruction (read top to bottom, skeleton only)
Q1 problem: TinyML lacks a fair, joint accuracy/latency/energy comparison method on MCU hardware. -> answerable (I.1-I.3).
Q2 why it matters: co-optimization across the whole stack makes isolating any one gain hard without a shared yardstick. -> answerable (I.2).
Q3 what's missing: no prior benchmark is simultaneously ML-realistic, MCU-scale, and power-aware. -> answerable (I.3, RW.1-RW.3).
Q4 what they did: built + fielded MLPerf Tiny (4 benchmarks, 3-metric protocol, closed/open divisions). -> answerable (I.5, M.1-M.5).
Q5 why this method: division split trades comparability vs. flexibility; targets calibrated to quantization noise. -> answerable (M.3, M.5).
Q6 experiments: the v0.5 community submission round. -> answerable (R.1).
Q7 strongest result: 5 submissions, both divisions, 5 hardware/software categories. -> answerable (R.2).
Q8 what it establishes: the design can accommodate real, heterogeneous submitters while staying comparable. -> answerable (R.5, D.1).
Q9 what it does NOT establish: generality beyond one round/n=5; stability of accuracy figures; full architecture coverage. -> answerable (D.5-D.6).
Q10 primary contribution: a fielded, gap-closing, 3-metric MCU benchmark suite. -> answerable (I.6, D.2).
Q11 main limitations: single round; unreplicated accuracy figures; narrow closed-division architectures; unresolved streaming/feature-extraction measurement tension. -> answerable (D.5-D.6).
Q12 one-day-later takeaway: MLPerf Tiny is the suite that finally measures accuracy+latency+energy together on real MCU hardware, and a real first round showed diverse submitters could use it. -> answerable (spine line 5-6, Cn.1).
**All 12 answerable from the skeleton alone. Gate G2: PASSED.**
