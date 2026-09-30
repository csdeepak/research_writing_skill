# MLPerf Tiny: A Benchmark Suite for Comparing Accuracy, Latency and Energy of Ultra-Low-Power Machine Learning Systems

## Abstract

Machine learning (ML) that runs on tiny, battery-powered devices ("TinyML") is hard to evaluate fairly, because the hardware, the software that executes the network and the power budget all differ from system to system {C009}. This paper presents MLPerf Tiny, an open-source benchmark suite built by more than 50 organizations from industry and academia {C001}. The suite has four tasks (keyword spotting, visual wake words, image classification and anomaly detection), each with a dataset, a small reference model and a quality target, and it measures accuracy, latency and energy of model inference {C001, C006}. A "closed" division fixes model and data so that inference stacks can be compared; an "open" division lets submitters change model, training or data to show other kinds of improvement {C007}. A host-side runner and an optional energy-measurement setup standardize how devices are driven and measured {C008}. The first submission round (June 2021) brought closed- and open-division results from a reference microcontroller baseline, a second microcontroller design based on the open RISC-V instruction set, a Raspberry Pi 4, a neural-network accelerator and a field-programmable gate array (FPGA) flow {C010}. Reference-model accuracy figures sit from 0.01 AUC (area under the ROC curve) to about 6 percentage points above the quality targets set for them {C005}. The authors attribute the variety of submissions to the modular design; the evidence is consistent with this but does not isolate the cause {C014}. Latency and energy values were not available to us in text form and are described only qualitatively {L001}.

## 1 Introduction

Running a neural network on the device that collects the data, instead of sending the data to a server, can improve energy efficiency, privacy and responsiveness {C009}. The authors focus on the extreme end of this trend, which they call TinyML: inference under a milliWatt on small, low-cost chips, especially microcontroller units (MCU), the single-chip processors found in sensors, appliances and wearables {C009}. At this scale, they argue, the energy of wireless communication is far higher than that of computing, so local inference suits always-on, battery-powered applications (Bouguera et al., 2018) {C009}.

The difficulty is that the field cannot easily say which system is better at what. A TinyML deployment stacks many choices: the chip, the software that executes the network, the toolchain, the numerical precision and the model. A change at one layer is hard to separate from changes at the others, so the effect of an individual optimization is hard to measure {C009}. Without a shared protocol, two reported numbers are rarely comparable, and here latency and energy, not only accuracy, are part of the result and depend on the hardware and software that produced them.

The authors state that existing benchmarks do not close this gap. They discuss CoreMark, a general benchmark for MCU-class devices (Gal-On et al., 2012); MLMark, an ML inference benchmark from the same consortium; and the MLPerf inference suite (Reddi et al., 2019). In their account, the first does not represent ML inference, the second uses models too large for MCUs and has no power measurement, and the third excludes MCUs for lack of small benchmarks and compatible implementations {C009}. On that basis they describe MLPerf Tiny as the first industry-standard suite for ultra-low-power systems; this framing rests on their own comparison of three benchmarks, not on a systematic literature search {C009, L008}.

We present the benchmark, from the authors' perspective, for readers outside embedded ML. Two questions organise the paper.

- **RQ1.** Can one benchmark specification give comparable accuracy, latency and energy results across very different TinyML systems, while leaving room for submitters to show improvements at different layers of the stack?
- **RQ2.** Did the first round of submissions show that the specification accommodates diverse submitters, and what did it reveal about the field?

The material supports four contributions:

1. A specification of four tasks with datasets, small reference models and quality targets, plus open-source reference implementations {C001, C002, C003}.
2. A closed/open rule set and a procedure for measuring accuracy, latency and energy of model inference only {C006, C007}.
3. A host-side runner and optional energy setup for driving and measuring devices in a standard way {C008}.
4. A description of the first round: five configurations, with observations on numerical formats and on what submitters did and did not change {C010, C011, C012}.

Section 2 explains why TinyML is hard to benchmark, Section 3 describes the tasks and how targets were set, Section 4 the rules and measurement (together addressing RQ1), Section 5 the first round (RQ2), Section 6 answers both questions and lists limitations, and Section 7 concludes.

## 2 Why TinyML is hard to benchmark

The authors name four primary obstacles for a TinyML benchmark, and a fifth point about how options combine {C009}.

**Low power.** Energy is a defining property, so a benchmark should measure it; but devices consume very different amounts of power, which makes measurement accuracy hard to maintain, and what falls inside the measurement is unclear when data paths and pre-processing differ {C009}.

**Limited memory.** Smartphone-class systems cope with gigabytes; TinyML systems typically have resources two orders of magnitude smaller, so benchmark overhead can make the benchmark too big to fit {C009}. The authors also want several levels of quantization (storing weights and activations with fewer bits, such as 8-bit integers instead of 32-bit floating point) represented {C009}.

**Hardware heterogeneity.** Devices range from general-purpose microcontrollers to unusual architectures, and the system under test may lack a system clock or debug interface. A standard interface with low porting effort is therefore essential {C009}.

**Software heterogeneity.** Users often write their own toolchains, particularly for systems with several compute units, so any benchmark restriction on the software stack could produce unrepresentative results. The authors say they must balance optimality with portability, and comparability with representativeness {C009}.

**Combinations.** Options at every layer multiply (the authors' Figure 1 illustrates this), and software users can improve the whole system at any layer; a benchmark should let them show the benefit of their contribution in a controlled setting {C009}.

The authors also place the benchmark between two extremes. Low-level benchmarks target kernels such as matrix multiplication and miss factors like memory bandwidth; application-level benchmarks can hide the target behind other pipeline stages. MLPerf Tiny targets model inference and excludes pre- and post-processing from the measurement window {C006}.

## 3 The four benchmark tasks

Each benchmark specifies a use case, a dataset, a model and a quality target, and has a reference implementation with training scripts, pre-trained models and C code {C001}. The reference implementations run TensorFlow Lite models with TensorFlow Lite for Microcontrollers, a lightweight inference runtime (David et al., 2020), on an STMicroelectronics NUCLEO-L4R5ZI board {C001}. Table 1 summarizes the suite; sizes are those of the compressed model files.

**Table 1. The four v0.5 tasks span audio and image inputs, with models from 52.5 KB to 325 KB.** "Top-1" is the fraction of inputs whose highest-scoring class is correct; AUC is the area under the receiver operating characteristic curve. Source: the authors' Table 1 and Section 4 (damaged in extraction; rows checked against the text).

| Use case | Dataset (input size) | Reference model (TFLite size) | Quality target (metric) |
|---|---|---|---|
| Keyword spotting | Speech Commands (49x10) | DS-CNN (52.5 KB) | 90% (Top-1) |
| Visual wake words | VWW dataset (96x96) | MobileNetV1 (325 KB) | 80% (Top-1) |
| Image classification | CIFAR10 (32x32) | ResNet (96 KB) | 85% (Top-1) |
| Anomaly detection | ToyADMOS (5*128) | FC-AutoEncoder (270 KB) | .85 (AUC) |

Table 1 defines what is measured for RQ1; it reports no submissions. The suite covers audio and image inputs, with Top-1 accuracy for three tasks and the threshold-free AUC for anomaly detection, and all reference models are small enough for typical microcontrollers {C001, C002}.

### 3.1 Keyword spotting

Keyword spotting recognises specific spoken words or short phrases, which needs low latency and low power {C003}. The data are Speech Commands v2 (Warden, 2018): 105,829 utterances from 2,618 speakers, with 30 words plus background noise, split so that each speaker appears in only one subset {C003}. The authors keep 10 words and merge background noise with the other 20 words into an open-set "unknown" class; adding "silence" gives 12 output classes {C003}. The model is a small depthwise-separable convolutional neural network (CNN), called DS-CNN, described by Zhang et al. (2017); it has 38.6K parameters and reached 92.2% accuracy in the authors' experiments {C002}. It fits the memory of most microcontrollers and uses standard layers {C003}. Feature extraction (turning audio into the spectral input the network expects) is excluded from measurement, and the open division offers three pre-computed feature choices, which the authors justify by saying feature extraction is typically a small fraction of the compute {C003, C016}.

### 3.2 Visual wake words

This task asks whether an image contains at least one person, relevant to smart doorbells and occupancy sensing (Chowdhery et al., 2019) {C003}. Images come from MSCOCO 2014 (Lin et al., 2014), preprocessed so that an image is positive when a person occupies more than 2.5% of it, and resized to 96x96 {C003}. The model is a MobileNetV1 (Howard et al., 2017) with width multiplier (alpha) 0.25 and two output classes, in a 325 KB file {C002, C003}.

### 3.3 Image classification

The benchmark uses CIFAR-10 (Krizhevsky et al., 2009), a labelled subset of the 80 Million Tiny Images collection (Torralba et al., 2008): 60000 colour images of 32x32 pixels in 10 classes, 6000 per class {C003}. The authors chose it because its low resolution suits tiny models and because earlier TinyML work, for example Fedorov et al. (2019), used it, so future results can be related to historical data points {C003}. The model is a customised ResNet (He et al., 2016) with three residual stacks instead of four, no pooling after the first convolution, and fewer filters and smaller strides than the standard network; the file is 96 KB {C002, C003}.

### 3.4 Anomaly detection

The benchmark uses the unsupervised variant, in which only normal examples are available for training, as is common in machine-fault detection where failures are rare {C003}. The data come from the DCASE2020 challenge (Koizumi et al., 2020), itself built from ToyADMOS (Koizumi et al., 2019) and MIMII (Purohit et al., 2019). Of six machine types the authors use only toy cars, avoiding per-machine models; training uses normal sounds of seven toy cars, 1000 samples each, mixing machine sound with environmental noise {C003}.

The model is a fully connected autoencoder, a network trained to reproduce its input through a narrow bottleneck, so that large reconstruction error signals an anomaly. It takes and returns 640 values, with four 128-unit layers each in encoder and decoder and a bottleneck of size 8 {C002, C003}. Audio becomes a log-mel spectrogram (128 frequency bands, 32 ms frames); the model slides over windows of five frames (5 x 128 = 640 inputs), and the mean squared reconstruction error, averaged over the central 6.4 seconds of the clip, is the anomaly score {C003}. Because a score needs a threshold to become a decision, the authors evaluate quality with the threshold-free AUC {C003}. They chose this model as the DCASE2020 reference, hence a known baseline, and because it adds a model built only from fully connected layers {C003}.

### 3.5 How the quality targets were set

A valid closed-division submission must reach each task's target. The authors set each slightly below what the reference model achieved, to allow for quantization and rounding differences between platforms {C004, C005}. Table 2 places the figures side by side.

**Table 2. Quality targets sit below the reference model's reported figures by 0.01 AUC to about 6 points.** Reference values are as reported by the authors; "margin" is our subtraction of the target from the reference figure. Each reference figure comes from a different evaluation set and no spread is reported, so margins should not be compared across rows.

| Task | Reference figure reported | Evaluation set | Target | Margin (derived) |
|---|---|---|---|---|
| Visual wake words | about 86% | preprocessed MSCOCO 2014 test set | 80% | about 6 points |
| Image classification | 86.5% | 200 CIFAR-10 test images | 85% | 1.5 points |
| Keyword spotting | 91.6% (quantized) | full test set | 90% | 1.6 points |
| Keyword spotting | 91.7% (quantized) | 1000 random utterances | 90% | 1.7 points |
| Anomaly detection | 0.86 AUC (quantized); 0.88 AUC (fp32) | 248 samples from four machines | 0.85 AUC | 0.01 AUC |

The margin varies from about 6 points for visual wake words to 0.01 AUC for anomaly detection {C005}. The paper does not explain why the visual wake words margin is larger, nor state whether its "about 86%" is for the full-precision or quantized model {C005}. Robustness cannot be judged: three evaluation sets are subsets (200 images, 1000 utterances, 248 samples), and no variance or repeat count is given for any accuracy figure {L002}. For keyword spotting, the quantized model scores 91.6% on the full test set and 91.7% on the subset, a 0.1-point difference that suggests the subset is representative, though this is one comparison {C004}.

## 4 Rules and measurement

### 4.1 Closed and open divisions

Submitters pursue different goals (showing hardware, a toolchain or a better model), so the authors use a modular design in which a reference implementation contains everything from training scripts to a reference hardware platform, so a submitter can replace one component and hold the rest fixed {C007}. Two divisions organise this (Table 3).

**Table 3. The closed division fixes model and data to allow direct comparison; the open division relaxes them to allow tradeoffs.** Source: the authors' Section 5.2.

| | Closed division | Open division |
|---|---|---|
| Model, dataset, quality target | Same as the reference | May change model, training scripts and dataset |
| Quantization | Post-training quantization with provided calibration data allowed | Not separately stated |
| Retraining or weight replacement | Prohibited | Allowed |
| Accuracy | Must reach the target | Measured on the same test dataset; need not reach the threshold |
| Documentation | Not separately stated | Must document deviations from the reference |

Modifying only certain components of the reference (marked green in the authors' Figure 2) permits either division; modifying an orange component requires the open division {C007}. Post-training quantization converts a trained model to lower precision without further training; quantization-aware training includes the lower precision during training. The authors' rationale is that the closed division enables direct comparison of one inference stack with another in a controlled setting, while the open division lets submitters show accuracy, latency or energy tradeoffs at any pipeline stage {C007}. Whether this yields comparability is the concern of RQ2 (Section 5).

### 4.2 What is measured

The framework measures three quantities, to expose the tradeoffs between them {C006}.

- **Latency.** Repeat five times: download an input, load the input tensor, run inference for at least 10 seconds and 10 iterations, and measure inferences per second. The score is the median of the five runs {C006}.
- **Accuracy.** One inference over the entire validation set; the framework computes Top-1 percent or AUC, and a minimum accuracy per model must be met for the score to be valid {C006}.
- **Energy.** As for latency, plus the total energy in the timing window, reported as micro-Joules per inference, again as a median of five measurements {C006}.

The paper does not report how much the five runs varied {C006}, and because only model inference is measured, the reported cost is not that of a full application {C006, L003}.

### 4.3 The measurement framework

Target platforms typically lack file input and output and interactivity and have less than a megabyte of flash memory, so they cannot run a benchmark on their own {C008}. The framework therefore has a host personal computer (PC) running a graphical program, the runner, connected over a serial port to the device under test (DUT), which runs a thin firmware layer following a communication protocol {C008}. The runner configures a test, detects the hardware, issues commands that load input data and perform measurements, collects the scores, and downloads the many input files needed for accuracy measurement {C008}.

The submitter implements five functions: serial communication; a timestamp function with at least 1 ms resolution (or, in energy mode, a signal edge that triggers an external timer); loading the input tensor; running one inference; and printing predictions {C008}.

For energy, the framework adds an "IO Manager" (input/output manager), an Arduino UNO with custom firmware that isolates the device electrically through level shifters and keeps the serial connection alive across power cycling, and an energy monitor that supplies and measures power; the runner supports three monitors: the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705 {C008}. Level-shifter power is excluded, only power delivered to the core is measured, and only one supply may power the core, so batteries or energy harvesters cannot circumvent the measurement {C008}. The authors say the monitor's sampling frequency does not affect the score because it lies well within the time constant of the device's power-delivery capacitance; the text gives no measurement supporting this {C008, L007}. The runner also lets users lower the supply voltage, and the authors note that the performance-energy balance can be dictated by voltage, since higher voltage is often needed for higher clock frequency and on-board power-conversion efficiency varies; they call this a key insight of the benchmark {C017, L007}. A latency-and-accuracy configuration needs only the host and the device, because the energy setup is more complex and energy scores may not be wanted {C008}.

RQ1 is now addressed as a design: the tasks fix what is run, the divisions what may change, and the framework how measurements are taken. Whether the design permits comparison depends on what submitters did with it.

## 5 The first submission round

### 5.1 What was submitted

The benchmark accepts results twice a year; submitters implement the tasks on their own stack, all results are peer-reviewed transparently by the submitters and a review committee, and each submission is public with reproduction instructions {C020}. The first round took place in June 2021 {C010}. Table 4 lists its five configurations.

**Table 4. The first round contained four closed-division configurations and one open-division FPGA configuration.** "PTQ" is post-training quantization, and "QAT" is quantization-aware training. Source: the authors' Table 2, damaged in extraction; rows reconstructed from the column sequence and the authors' Section 6.2.

| Division | Numerics | Software framework | Hardware | What it demonstrates (authors' wording, shortened) |
|---|---|---|---|---|
| Closed | INT-8 PTQ | TensorFlow Lite Micro | ARM MCU | Baseline results on the reference platform |
| Closed | INT-8 PTQ | TensorFlow Lite Micro | RISC-V MCU | Performance of a RISC-V microcontroller customized for neural-network inference |
| Closed | FP-32 and INT-8 PTQ | LEIP Framework | Raspberry Pi 4 | A software-only, hardware-agnostic optimization toolchain |
| Closed | INT-8 PTQ | Syntiant TDK | Neural-network accelerator | Ultra-low-power hardware efficiency for deep neural networks |
| Open | Int-6/8 QAT | QKeras with hls4ml | FPGA | Rapid end-to-end development of ML accelerators on reconfigurable hardware |

Table 4 answers a factual question about who used the suite. Its takeaway is that the rows differ along most columns, and that one row, the FPGA, is in the open division and uses quantization-aware training at 6 or 8 bits {C010}. The authors describe four submitters: an organization showing hardware-agnostic developer tools, a hardware vendor showing its accelerator, an academic institute showing RISC-V microcontrollers, and a team showing the open-source hls4ml workflow {C010}. (RISC-V is a free, open instruction-set architecture (Asanovic et al., 2014).) The baseline row uses the reference platform, so five configurations are not five organizations {C010}.

### 5.2 What the round revealed

The authors draw these observations {C011}.

- The most common numerical format was 8-bit integer, which they say offers a performance boost with little effect on accuracy; the text we have does not present accuracy evidence for that statement, so what the round directly shows is the frequency of use {C011}.
- Software ranged from open-source interpreters (TensorFlow Lite Micro) to hardware-specific inference compilers, which the authors read as a continuing tradeoff between optimization and portability {C011}.
- Hardware included microcontrollers, accelerators and FPGAs, with power consumption from microWatts to Watts; the reconfigurable hardware could use variable-precision models {C011}.
- None of the submissions modified the training dataset {C012}. This is a null observation that bears on interpretation: the open division's freedom to change data was not exercised. The authors contrast it with a general trend towards data-centric design and anticipate a shift later; that expectation is forward-looking, not a finding {C012, C015}.

The reference implementations also produced results. The authors' Figure 5 reports latency and energy of the four reference implementations on the NUCLEO-L4R5ZI board; the text says the benchmarks cover a wide scope in latency and energy and that each reference meets its minimum accuracy {C013}. The values appear only in the figure, which is not in our text, so we cannot report them, nor any submission's numerical results {C013, L001}.

### 5.3 Interpretation and what the round does not show

For RQ2, Table 4 and Section 5.2 show that submitters from different parts of the stack all found a way to use the suite {C010, C011}. The authors attribute this to the modular design and the two divisions: each submitter had a specific element to show, and the suite could accommodate these diverse goals {C014}. The evidence is consistent with that attribution but does not isolate it: the round offers no comparison under a different rule set, submitters were self-selected, and only one round is described {C014, L005}. It also does not show that the rows are comparable with each other, since no numbers are available here {L001}. The authors call the results a snapshot of this emerging field, with future rounds able to show its evolution {C014, L005}.

## 6 Discussion

### 6.1 Answers to the research questions

**RQ1** asked whether one specification can give comparable results across heterogeneous systems while leaving room for different improvements {C001}. The paper offers fixed tasks and targets, an inference-only procedure with median-of-five scoring, and closed and open divisions {C001, C006, C007}. Its support for comparability is at the level of design: reference models meet their targets and one procedure is shared {C004, C013}. The paper reports no direct test of comparability, such as measuring one system in two setups or checking agreement across submitters, so we can say the specification is a defined attempt at comparable results, not that comparability has been demonstrated {C007, L001}.

**RQ2** asked whether the first round showed the specification accommodating diverse submitters. In the sense of variety, yes: five configurations on four kinds of platform, both divisions, and numerical formats from 32-bit floating point (FP-32) to 6-bit integers (Int-6) {C010, C011}. The authors' explanation, modular design, is their interpretation, consistent with the evidence {C014}.

### 6.2 Tradeoffs the authors acknowledge

The first concerns feature extraction. Excluding it from the measured window for keyword spotting and anomaly detection, while letting open-division submitters choose among pre-computed features, opens a degenerate case: a submitter could label every layer but the last as feature extraction and remove nearly the whole model from the measurement {C016}. Fixing feature extraction rigidly would preclude joint optimization of features and model, while including it would, for one second of audio, mean one inference but 40 feature extraction cycles, over-emphasizing its cost {C016}. The authors aim to include pre-processing in future versions {C018, L003}. Separately, the time-domain tasks are naturally streaming, but limited runner-to-device bandwidth makes streaming hard to reproduce without transfer delays {L003}.

The second concerns stability. The authors want the suite to evolve, with tasks in domains such as wearables, medical devices and environmental monitoring, and also to be a long-term record, so they envision keeping a subset of tasks stable {C018, L006}. This is a plan, not a demonstrated property. The project's readme file lists later releases (v0.7 on April 6, 2022, v1.0 on Nov 9, 2022, v1.1 on Jun 27, 2023) and an expected v1.2 deadline of March 15, 2024, dates not yet finalized, which is consistent with continuation but does not show stability of results {C019, L006}.

### 6.3 Limitations

In order of their effect on the main findings:

1. **Missing numbers.** Latency and energy values and submission results are not in our text, so statements about their range are qualitative {L001}.
2. **One round, self-selected submitters.** Observations describe June 2021 only {L005}.
3. **Evaluation sets and spread.** Three targets rest on subsets, with no spread or repeat count {L002}.
4. **Inference-only scope.** Latency and energy are those of the model alone {L003}.
5. **Model coverage.** Closed-division models are mainly fully connected and convolutional; recurrent networks are left to the open division or future versions {L004}.
6. **Energy methodology.** The sampling-frequency statement and the voltage insight lack supporting measurements {L007}.
7. **Framing of novelty.** The comparison with earlier benchmarks is the authors' own, and the cited works were not read for this paper {L008}.

### 6.4 Impact and risks

The authors report that the benchmarks have served as a standard set of tasks in TinyML research (Banbury et al., 2021) and as public projects on a TinyML development platform {C019}. They also list risks {C019}: TinyML could make it cheaper to track people without consent, and inexpensive devices could add electronic waste. These are statements of expectation, not measured outcomes.

## 7 Conclusion

The authors present MLPerf Tiny as a way to compare accuracy, latency and energy of TinyML hardware, models and runtimes under a shared, open-source specification developed by industry and academia {C001, C007}. It consists of four small tasks with reference implementations, an inference-only measurement procedure, closed and open divisions, and a runner framework with optional energy measurement {C001, C006, C007, C008}. The first round drew configurations from microcontrollers to an FPGA {C010}.

What remains unresolved is whether results are comparable in practice, which depends on numbers not available to us, and how the suite will treat feature extraction, streaming and stability as it evolves {L001, L003, L006}. The authors point to new domains, more layer types, pre-processing within the measured scope and a long-term stable subset as next steps {C018}. A useful check for outside researchers would be to test whether the same system, measured in different setups, yields the same score; the paper reports no such test.

## References

- Asanovic, K. and Patterson, D. A. (2014). Instruction sets should be free: The case for RISC-V. EECS Department, University of California, Berkeley, Tech. Rep. UCB/EECS-2014-146. Cited as (Asanovic et al., 2014).
- Banbury, C., Zhou, C., Fedorov, I., Matas, R., Thakker, U., Gope, D., Janapa Reddi, V., Mattina, M. and Whatmough, P. (2021). MicroNets: Neural network architectures for deploying TinyML applications on commodity microcontrollers. Proceedings of Machine Learning and Systems, 3.
- Bouguera, T., Diouris, J.-F., Chaillout, J.-J., Jaouadi, R. and Andrieux, G. (2018). Energy consumption model for sensor nodes based on LoRa and LoRaWAN. Sensors, 18(7):2104.
- Chowdhery, A., Warden, P., Shlens, J., Howard, A. and Rhodes, R. (2019). Visual wake words dataset. CoRR, abs/1906.05721.
- David, R., Duke, J., Jain, A., Reddi, V. J., Jeffries, N., Li, J., Kreeger, N., Nappier, I., Natraj, M., Regev, S., et al. (2020). TensorFlow Lite Micro: Embedded machine learning on TinyML systems. arXiv:2010.08678.
- Fedorov, I., Adams, R. P., Mattina, M. and Whatmough, P. (2019). SpArSe: Sparse architecture search for CNNs on resource-constrained microcontrollers. Advances in Neural Information Processing Systems 32, pages 4978-4990.
- Gal-On, S. and Levy, M. (2012). Exploring CoreMark, a benchmark maximizing simplicity and efficacy. The Embedded Microprocessor Benchmark Consortium. Cited as (Gal-On et al., 2012).
- He, K., Zhang, X., Ren, S. and Sun, J. (2016). Deep residual learning for image recognition. IEEE Conference on Computer Vision and Pattern Recognition, pages 770-778.
- Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M. and Adam, H. (2017). MobileNets: Efficient convolutional neural networks for mobile vision applications. arXiv:1704.04861.
- Koizumi, Y., Saito, S., Uematsu, H., Harada, N. and Imoto, K. (2019). ToyADMOS: A dataset of miniature-machine operating sounds for anomalous sound detection. IEEE WASPAA, pages 313-317.
- Koizumi, Y., Kawaguchi, Y., Imoto, K., Nakamura, T., Nikaido, Y., Tanabe, R., Purohit, H., Suefusa, K., Endo, T., Yasuda, M. and Harada, N. (2020). Description and discussion on DCASE2020 challenge task2: Unsupervised anomalous sound detection for machine condition monitoring. arXiv:2006.05822.
- Krizhevsky, A., Nair, V. and Hinton, G. (2009). CIFAR-10 (Canadian Institute for Advanced Research).
- Lin, T.-Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollar, P. and Zitnick, C. L. (2014). Microsoft COCO: Common objects in context. European Conference on Computer Vision, pages 740-755.
- Purohit, H., Tanabe, R., Ichige, K., Endo, T., Nikaido, Y., Suefusa, K. and Kawaguchi, Y. (2019). MIMII dataset: Sound dataset for malfunctioning industrial machine investigation and inspection. arXiv:1909.09347.
- Reddi, V. J., Cheng, C., Kanter, D., Mattson, P., et al. (2019). MLPerf inference benchmark.
- Torralba, A., Fergus, R. and Freeman, W. T. (2008). 80 million tiny images: A large data set for nonparametric object and scene recognition. IEEE Transactions on Pattern Analysis and Machine Intelligence, 30(11):1958-1970.
- Warden, P. (2018). Speech commands: A dataset for limited-vocabulary speech recognition. arXiv:1804.03209.
- Zhang, Y., Suda, N., Lai, L. and Chandra, V. (2017). Hello Edge: Keyword spotting on microcontrollers. arXiv:1711.07128.
