# Research skeleton (step 9): one topic sentence per paragraph slot

## Abstract
Continued progress on ultra-low-power, on-device machine learning has been limited by the lack of a widely accepted, reproducible benchmark, so this paper presents MLPerf Tiny, a suite that measures accuracy, latency, and energy on four fixed reference tasks {C033,C007}, describes how its modular closed/open structure and shared measurement protocol let heterogeneous hardware and software be compared fairly {C009,C010}, reports that all four reference implementations met their targets and that a first external round produced five results across five different platforms {C026,C027}, and states the main boundary: one round of evidence, with streaming/pre-processing measurement and architectural coverage still open questions in the authors' own account {L001,L002}.

## 1 Introduction
- I.1 On-device machine-learning inference under about a milliwatt of power is valuable specifically because it avoids the energy cost of sending data over a radio link, but that value depends on being able to compare systems built for it {C001,C033}.
- I.2 That comparison has to respect an unusually tight resource envelope: TinyML hardware typically runs at 10-250 MHz under 50 mW, several orders of magnitude below phone- or GPU-class deployment.
- I.3 Three existing benchmarks each miss one property this envelope requires: one does not represent machine-learning inference at all, and the other two assume far more memory than a microcontroller provides, with one of those also skipping power measurement entirely {C003,C004,C005,C006}.
- I.4 This leaves an explicit question: can one suite fit microcontroller-class memory and power limits, score accuracy, latency, and energy together, and still let a fair comparison be made across a genuinely heterogeneous set of hardware and software stacks?
- I.5 The authors answer this with MLPerf Tiny, and this paper reports three things in turn: how the suite is designed to make that comparison fair (Section 2-3), whether the reference implementations meet their own targets and whether outside submitters could use the suite (Section 4), and what that first round does and does not establish (Section 5-6) {C007,C026,C027}.

## 2 Background and Related Work
- B.1 On-device, near-sensor inference is attractive because it avoids the higher energy cost of wireless transmission at this scale, in addition to gains in responsiveness and privacy {C001}.
- B.2 Designing any benchmark for this setting is hard because four constraints interact: what counts as the power measurement, memory that is roughly two orders of magnitude tighter than conventional ML benchmarks assume, hardware that ranges from general microcontrollers to novel accelerator architectures, and software toolchains that are tightly coupled to specific hardware {C002}.
- B.3 Measured against exactly these constraints, the closest existing benchmarks each fall short: CoreMark does not profile full programs or represent ML inference workloads, MLMark uses real ML workloads but needs gigabyte-scale memory and has no power measurement, and MLPerf's own inference suite excludes microcontroller-class platforms outright {C003,C004,C005}.
- B.4 None of the three is simultaneously ML-representative, small enough for microcontrollers, and power-aware, and the authors state directly that a benchmark treating power as a first-class citizen and fitting TinyML's constraints is needed {C006}.

## 3 The MLPerf Tiny Benchmark Suite
- M.1 MLPerf Tiny answers that need with four fixed reference benchmarks, each pairing a dataset, a model, and a quality threshold with a shared harness for latency, accuracy, and energy, built so a submitter who only changes one layer of the stack can still show that change against a common baseline {C007,C008}.
- M.2 A closed division fixes the model, dataset, and quality target and allows only post-training quantization, while an open division allows changing the model, training procedure, or dataset while still measuring accuracy on the same test set, so the suite can balance strict comparability against room to innovate {C009}.
- M.3 Latency and energy are each scored as the median of five runs of at least ten seconds and ten iterations, accuracy as Top-1 percent or AUC over the full validation set against a minimum threshold, and only one power supply may power the device core during energy measurement, specifically so auxiliary batteries or energy harvesters cannot be used to defeat the measurement {C010}.
- M.4 Table 1 lays out all four benchmarks together before the per-task rationale, data, model, and threshold are walked through in turn {C007}.
- M.5 Visual wake words asks whether a person is in an image, a task chosen because it fits smart-doorbell and occupancy use cases and its MobileNetV1 reference model reaches about 86% accuracy, which the authors then reduce to an 80% closed-division threshold to leave room for quantization differences {C011,C012,C013}.
- M.6 Image classification keeps CIFAR-10 partly to continue an existing TinyML precedent, and its reference model shrinks the standard ResNet and drops the pooling step after the first convolution because of the input's low resolution, reaching 86.5% accuracy on a 200-image test subset against an 85% threshold set for quantization headroom {C014,C015,C016,C017}.
- M.7 Keyword spotting's twelve-class design is built to test both a closed set of command words and an open set of background sounds at once, and its 38.6K-parameter reference model reaches 92.2% accuracy (91.6%/91.7% once quantized), against a 90% threshold set for quantization headroom {C018,C019,C020}.
- M.8 Anomaly detection restricts the DCASE2020 dataset to one machine type because the authors judge the added complexity of all six not to be worth it, scores a fully-connected autoencoder's reconstruction error with the threshold-free AUC-ROC metric, and sets its 0.85 AUC threshold directly from the reference model's own fp32 (0.88) and quantized (0.86) scores {C021,C022,C023,C024}.

## 4 Results
- R.1 Two kinds of evidence bear on whether the suite works: whether the reference implementations themselves meet their own targets, and whether outside submitters could use the suite at all.
- R.2 All four reference implementations, run on the shared reference board, met their accuracy targets, and their latency and energy scores spanned a wide range across the four tasks, though the paper's own figure does not give recoverable exact numbers for that spread {C026}.
- R.3 The first submission round, in June 2021, produced five results: four in the closed division, on an ARM MCU, a customized RISC-V MCU, a Raspberry Pi 4 run through a hardware-agnostic toolchain, and a dedicated neural-network accelerator, plus one open-division FPGA submission built through a high-level-synthesis flow, each aimed at demonstrating a different layer of the stack {C027}.
- R.4 Across the round, 8-bit integer numerics dominated, frameworks ranged from an open interpreter to hardware-specific compilers, and measured power spanned roughly six orders of magnitude, from microwatts to watts {C028}.
- R.5 One thing did not change across any submission: the training dataset, even though the wider machine-learning field was trending toward data-centric methods, a pattern the authors themselves point out {C029}.

## 5 Discussion
- D.1 Read together, the round answers the paper's question for the case actually tested: a modular, three-metric design was enough to let five very different hardware and software stacks report results that a reader can put side by side {C030}.
- D.2 That works because fixing a swappable reference implementation lets one submitter isolate a single layer of the stack (a chip, a compiler, a training flow) without having to rebuild everything else the comparison depends on.
- D.3 What the round does not show is a shift toward data-centric TinyML: every submission left the training dataset untouched, so, in the authors' own words, TinyML design in this first round stayed focused on models, frameworks, and hardware {C029,C030}.
- D.4 Taken as a whole, a modular suite that scores three metrics at once looks like a workable way to standardize a genuinely fragmented hardware and software landscape without forcing every submitter onto one stack, though the authors are explicit about how far that conclusion currently reaches {C030}.

## 6 Limitations
- L.1 The authors themselves flag two design-level limits: streaming and pre-processing measurement remains unresolved because excluding feature extraction while letting submitters vary it risks a degenerate case, and because a non-streaming benchmark cannot cleanly represent a continuously streaming task {L001}; and the closed division currently supports only fully-connected and convolutional architectures, with long-term, cross-version stability stated as a goal rather than a demonstrated property {L002}.
- L.2 The authors also name a broader, non-technical caveat: the same inexpensive, on-device technology that can preserve privacy could be misused for surveillance, and cheap devices can add to electronic waste {L003}.
- L.3 Additional caveats. Beyond what the authors state, the evidence here is one submission round of five results on one reference board, with no per-submission numeric scores or run-to-run variance reported in the paper text itself, which bounds how far the round's diversity can be read as proof that the design generalizes {L004,L005}.

## 7 Conclusion
- C.1 MLPerf Tiny gives the field a suite that fits microcontroller-class constraints, scores accuracy, latency, and energy together, and produced comparable evidence from five different hardware and software stacks in its first round, leaving open, by the authors' own account, whether future rounds bring in more architectures, more application domains, and, notably, any submission that changes the training data itself {C030,C032}.

---

## Gate G2: skeleton self-reconstruction (answered from the skeleton above only)

Q1 What problem is this paper solving? -- TinyML lacks a widely accepted, reproducible benchmark for comparing ultra-low-power ML systems (I.1-I.4, Abstract).
Q2 Why does this problem matter? -- On-device inference under 1 mW enables always-on, private, battery-efficient applications, but only if systems built for it can be fairly compared (I.1, B.1).
Q3 What is missing from existing approaches? -- CoreMark isn't ML-representative; MLMark and MLPerf Inference assume far more memory, and MLMark also skips power (I.3, B.3-B.4).
Q4 What exactly did the authors do? -- Built four fixed reference benchmarks with a shared latency/accuracy/energy harness and a closed/open division structure (M.1-M.8).
Q5 Why did they choose this method? -- Modularity lets one submitter isolate one stack layer (M.1); closed/open balances comparability and flexibility (M.2); each per-task design choice is tied to a stated reason (M.5-M.8).
Q6 What experiments were performed? -- Running the reference implementations on one board, then opening the suite to a first external submission round (R.1-R.3).
Q7 What are the strongest results? -- All four reference implementations met target; the first round drew five results across five different hardware classes (R.2-R.3).
Q8 What do those results actually establish? -- That the suite's design is usable end to end and produces comparable, informative results from very different stacks (D.1-D.2).
Q9 What do they NOT establish? -- That practice will become data-centric, that the design holds beyond one round, or exact per-submission scores (R.5, L.3).
Q10 What is the primary contribution? -- An open, modular, three-metric TinyML benchmark suite, validated by reference runs and a first real submission round (I.5, M.1, D.4).
Q11 What are the main limitations? -- Streaming/pre-processing measurement unresolved; closed division limited to FC/CNN; dual-use/e-waste caveat; single-round evidence with no per-submission scores or variance reported (L.1-L.3).
Q12 What should the reader remember one day later? -- MLPerf Tiny made ultra-low-power ML systems comparable on accuracy, latency, and energy at once, and its first round showed that this works across very different hardware, but not yet that it changes what data TinyML researchers use (C.1).

All 12 answerable from the skeleton alone. Gate G2: **passed**.
