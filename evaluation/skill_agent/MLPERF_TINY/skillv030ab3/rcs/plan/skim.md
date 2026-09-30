# Skim sheet (generated; claim text verbatim, do not paraphrase here)

## 30-second outline (paper spine)

- 1. **Problem.** TinyML systems (machine-learning inference on microcontroller-class devices) vary widely in hardware and software, so their accuracy, latency and energy cannot be compared fairly or reproducibly, and the effect of an individual optimization is hard to isolate {C001} {C002}.
- 2. **Gap.** The authors characterize the existing benchmarks they discuss (CoreMark, MLMark, the MLPerf inference benchmark) as not meeting TinyML needs: not ML workloads, models too large for microcontrollers, or no power measurement {C003}.
- 3. **Question.** How can one build an open benchmark that measures accuracy, latency and energy across heterogeneous TinyML stacks, compares fairly, and still lets different kinds of contribution be shown {C023} {C025} {C028}?
- 4. **Approach.** Four benchmark tasks with reference models and open-source reference implementations, quality targets, closed and open divisions, and a standardized measurement framework, developed with more than 50 organizations {C004} {C006} {C008} {C023}.
- 5. **Key finding.** The reference models clear their quality targets (for example 91.6% against a 90% requirement for keyword spotting), and the June 2021 round produced five diverse submissions in a Table 2 the authors read as showing the modular design accommodating different goals {C012} {C015} {C018}.
- 6. **Meaning.** In the authors' reading, a modular, two-division benchmark can serve hardware vendors, software vendors and researchers at once {C018} {C027} {C028}.
- 7. **Main limit.** Streaming inputs and pre-processing are not captured, the closed division covers mainly FC and CNN models, the suite must stay stable while evolving, and the paper gives no submission measurements {L002} {L003} {L004} {L001} {L008}.

## Findings in one sentence each

- The authors state that continued TinyML progress is limited by the lack of a widely accepted, easily reproducible benchmark, and that because deployment requires co-optimization at every layer of the stack, direct comparison of solutions is challenging and the impact of individual optimizations is difficult to measure, so a fair and reliable method of comparison is needed. {C001}
- The authors name five challenges for a TinyML benchmark: low power (very different power levels and unclear measurement scope), limited memory (about two orders of magnitude below smartphones), hardware heterogeneity (missing system clock or debug interface; porting effort), software heterogeneity (tightly coupled inference stacks; optimality versus portability) and a cross-product of options at every level of the stack. {C002}
- The authors characterize three existing benchmarks as not meeting TinyML needs: CoreMark does not profile full programs nor represent ML inference workloads; MLMark uses real ML workloads but its models are far too large for MCU-class devices and it lacks power measurement; the MLPerf inference benchmark precludes MCUs for lack of small benchmarks and compatible implementations. {C003}
- MLPerf Tiny is an open-source benchmark suite, developed as a collaboration of more than 50 organizations from industry and academia, that measures accuracy, latency and energy of ML inference on four benchmarks and provides complete reference implementations. {C023}
- The suite measures latency, energy and accuracy together because the authors want to capture the tradeoffs inherent to TinyML, and they treat power as a first-class concern. {C025}
- There are two divisions, closed and open, because the authors want to balance comparability and flexibility. {C028}
- MLPerf Tiny specifies four benchmarks, each with a dataset, a model and a quality target: keyword spotting (Speech Commands, DS-CNN, 90% Top-1), visual wake words (VWW dataset, MobileNetV1, 80% Top-1), image classification (CIFAR-10, ResNet, 85% Top-1) and anomaly detection (ToyADMOS, FC-autoencoder, AUC 0.85). {C004}
- MLPerf Tiny has a closed division (same models, datasets and quality targets; post-training quantization allowed, retraining and weight replacement prohibited) and an open division (model, training scripts and dataset may change; same test dataset; accuracy threshold not required; deviations documented). {C006}
- Measurement procedure: latency is the median inferences per second over five runs, each running inference for at least 10 seconds and 10 iterations; accuracy is Top-1 percent or AUC from a single inference over the whole validation set, with a minimum accuracy required for a valid score; energy repeats the latency procedure and adds total energy in the timing window to give micro-Joules per inference, again as the median of five measurements. {C008}
- On the keyword spotting benchmark the quantized reference model reaches 91.6% accuracy on the full test set and 91.7% on a 1000-utterance subset, against an accuracy requirement of 90%; the model achieved 92.2% in the authors' experiments. {C012}
- The v0.5 submission round (June 2021) produced five rows in the authors' Table 2: four closed-division entries (ARM MCU with TFLM; RISC-V MCU; software-only LEIP toolchain on a Raspberry Pi 4; Syntiant neural network accelerator) and one open-division FPGA entry (QKeras, Int-6/8 QAT, HLS4ML); results are peer-reviewed by submitters and a review committee and are public. {C015}
- The authors conclude that the diverse v0.5 submissions show the benchmark meeting a variety of needs, and they attribute its ability to accommodate submitters' different goals to its modular design. {C018}
- The design is modular so that hardware and software users can demonstrate the competitive advantage of their specific contribution, targeting one component such as quantization or offering an end-to-end solution. {C027}

## Figure takeaways

