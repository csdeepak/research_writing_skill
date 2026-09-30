# MLPerf Tiny: An Open Benchmark for Comparing Accuracy, Latency and Energy of Machine-Learning Inference on Ultra-Low-Power Devices

## Abstract

Machine-learning (ML) inference on very small, low-power devices, known as TinyML, is hard to compare across systems because the hardware and the software stacks that run the models differ so much. The authors of MLPerf Tiny say this lack of a widely accepted, easily reproducible benchmark limits progress. They describe existing benchmarks as unsuited to the task: a microcontroller benchmark that does not represent ML inference, an ML benchmark whose models are far too large for microcontrollers and that cannot measure power, and a general ML inference benchmark that precludes microcontrollers. MLPerf Tiny is an open-source suite of four benchmarks (keyword spotting, visual wake words, image classification and anomaly detection) that measures accuracy, latency and energy, built by more than 50 organizations from industry and academia. It fixes a dataset, a small model and a quality target for each task. It supplies open-source reference implementations, a strict closed division and a flexible open division in which submitters may change the model, training scripts and dataset, and a measurement procedure and framework. The reference models exceed their quality targets; for keyword spotting, the quantized reference model reaches 91.6% accuracy against a 90% requirement. The June 2021 round produced five submissions, on hardware from microcontrollers to accelerators and reconfigurable chips, including a software-only toolchain, which the authors read as showing that the modular design accommodates different goals. The authors state limits: streaming inputs and pre-processing are not captured.

## 1. Introduction

TinyML is machine-learning inference on ultra-low-power devices; the authors describe it as inference under a milliWatt. Running a model on the device, next to the sensor, gives responsiveness and privacy and avoids the energy cost of wireless communication, which the authors report is far higher than the cost of computing at this scale (Bouguera et al., 2018). The devices are microcontrollers (small, low-power processors with very little memory) and related hardware such as digital signal processors and tiny neural-network accelerators. The authors' motivation is that deploying ML at this scale requires co-optimizing every layer of the stack, from hardware to model to runtime, so the direct comparison of solutions is challenging and the effect of any single optimization is difficult to measure. They state that continued progress is limited by the lack of a widely accepted and easily reproducible benchmark, and that a fair and reliable method of comparison is needed.

As the authors describe them, three existing benchmarks each miss part of this need: CoreMark (Gal-On et al., 2012), MLMark and the MLPerf inference benchmark (Reddi et al., 2019). The authors state that none accurately represents the performance of TinyML workloads on tiny hardware. Section 3 sets these out by dimension.

The paper's aim can be read as three research questions (RQ1 to RQ3). RQ1: which tasks, datasets, models and quality targets make up a benchmark that fits such devices? RQ2: which rules and which measurement procedure let systems be compared fairly while letting different kinds of contribution be shown? RQ3: what did the first round of outside submissions show about how well the benchmark serves different submitters? The paper does not state these questions in this form; they organize the presentation.

The authors' answer is MLPerf Tiny, an open-source suite of four benchmarks selected by more than 50 organizations in academia and industry, with complete reference implementations that serve as community baselines. Three design choices shape it, and the authors give a reason for each. The suite measures latency, energy and accuracy together to capture the tradeoffs inherent to TinyML. Its design is modular, so that users can show the competitive advantage of their specific contribution, whether a single component or an end-to-end solution. It has two divisions, closed and open, to balance comparability and flexibility. In the closed division submitters use the same models, datasets and quality targets as the reference; the open division lets them change these.

The contributions, each with the place its evidence sits, are:

1. A suite of four benchmarks, each with a dataset, a small model and a quality target (Section 4.1, Table 1).
2. Quality targets set from measured reference accuracy, with room for quantization differences (Sections 4.2 and 5.1, Table 2).
3. A rule set and measurement framework: closed and open divisions, a modular reference implementation, and a procedure for latency, accuracy and energy (Sections 4.3 and 4.4).
4. A description of the June 2021 submission round, which the authors interpret as showing the design accommodates different goals (Section 5.3, Table 3).

Section 2 lays out the challenges, Section 3 the related benchmarks, Section 4 the design (RQ1 and RQ2), Section 5 the results (RQ1 to RQ3), Section 6 the discussion, and Section 7 the limits, with the authors' concessions first.

## 2. Why comparing TinyML systems is hard

The authors name five challenges. On power, devices consume very different amounts of power, and the scope of a power measurement is hard to fix when data paths and pre-processing vary. On memory, TinyML systems work with resources about two orders of magnitude smaller than those of a smartphone, so models sized for other ML benchmarks do not fit, and several levels of quantization and precision need representing. On hardware heterogeneity, the system under test may lack standard features such as a system clock or a debug interface, and a standard interface with little porting effort is a key difficulty.

On software heterogeneity, systems are often tightly coupled to a vendor's own inference stack, so any restriction on the stack could give unrepresentative results; the authors say they must balance optimality with portability, and comparability with representativeness. The fifth challenge is the cross-product: there is diversity at every level of the stack, and a user can improve the system at any layer, so a benchmark should let such users show the benefit of their solution in a controlled setting. The modular design and the two divisions in Section 4.3 are the authors' response to this requirement.

## 3. Related work

The authors compare MLPerf Tiny with three earlier benchmarks along two dimensions. The first dimension is whether the workload is a realistic ML inference workload that fits microcontroller-class devices. CoreMark is the standard benchmark for this class of device because it is easy to implement and uses real algorithms (Gal-On et al., 2012); it does not profile full programs and does not accurately represent ML inference workloads. MLMark does use actual ML inference workloads, but the authors say its models are far too large for these devices, needing gigabytes of memory and having long runtimes. The MLPerf inference benchmark is a community-driven suite for ML inference (Reddi et al., 2019); the authors say it precludes microcontrollers and other resource-constrained platforms, because it lacks small benchmarks and compatible implementations.

The second dimension is power measurement. CoreMark supports power measurement through a companion benchmark, whereas MLMark does not, which the authors call critical for a TinyML benchmark. The MLPerf inference benchmark had plans to add power measurements. The authors conclude that there is a clear and distinct need for a TinyML benchmark that suits ML workloads and makes power a first-class citizen. This account rests on the authors' characterization of three benchmarks; the cited works were not consulted for this presentation.

## 4. Benchmark design and measurement method

### 4.1 Design of the four tasks: data and models

MLPerf Tiny targets model inference. Quality is measured by Top-1 accuracy or, for anomaly detection, by the area under the receiver operating characteristic (ROC) curve (AUC). The measurement window does not include pre-processing or post-processing, because the authors judge that application-level benchmarks can obscure the target of the benchmark behind other stages of the pipeline. Each benchmark fixes a use case, a dataset, a model and a quality target (Table 1), and each has a reference implementation with training scripts, pre-trained models and C code.

**Table 1.** The four benchmarks of the v0.5 suite. Sizes are the TFLite model size. Values as listed by the authors.

| Task | Dataset (input size) | Model (TFLite size) | Quality target (metric) |
| --- | --- | --- | --- |
| Keyword spotting | Speech Commands (49x10) | DS-CNN (52.5 KB) | 90% (Top-1) |
| Visual wake words | VWW Dataset (96x96) | MobileNetV1 (325 KB) | 80% (Top-1) |
| Image classification | CIFAR10 (32x32) | ResNet (96 KB) | 85% (Top-1) |
| Anomaly detection | ToyADMOS (5*128) | FC-AutoEncoder (270 KB) | .85 (AUC) |

Visual wake words asks whether at least one person is in an image (Chowdhery et al., 2019). The authors chose it because it is directly relevant to smart doorbell and occupancy applications and because the challenge's reference network fits on most 32-bit embedded microcontrollers. The data are the Microsoft Common Objects in Context (MSCOCO) 2014 dataset (Lin et al., 2014), preprocessed so that positive images contain a person occupying more than 2.5% of the source image, and resized to 96x96. The model is a MobileNetV1 (Howard et al., 2017) with alpha 0.25 and two output classes; as a model for TensorFlow Lite for Microcontrollers (TFLM), the runtime of the reference implementations, it is 325KB.

Image classification uses CIFAR-10 (named for the Canadian Institute for Advanced Research; Krizhevsky et al., 2009), a labeled subset of the 80 Million Tiny Images dataset (Torralba et al., 2008): 60000 32x32x3 color images, 6000 per class, in 10 classes. The authors chose it because its low resolution makes it the most suitable source for tiny models and because much prior TinyML work has used it (Fedorov et al., 2019), so it gives a point of reference for relating future results to historical ones. The model is a customized ResNetv1 (He et al., 2016) with three residual stacks instead of the official four, no pooling after the first convolution, and fewer filters and lower strides; it is 96KB as a TFLite model.

Keyword spotting uses Speech Commands v2 (Warden, 2018): 105,829 utterances from 2,618 speakers, split so that each speaker appears in one subset. The benchmark uses 10 of the 30 words and merges the other 20 with background noise into an open-set "unknown" class; with "silence", this gives 12 output classes. The model is the small depthwise-separable convolutional neural network (CNN) of Zhang et al. (2017), with 38.6K parameters. The authors chose it because it fits the memory of most microcontrollers and uses standard layers. Feature extraction (turning audio into the model's input features) is excluded from the measurement, and three pre-computed feature choices are offered for the open division. The authors reason that feature extraction is typically a small fraction of the overall compute cost, so the impact on the measurements is minor.

Anomaly detection is unsupervised: training uses only normal sounds, and the model scores how anomalous a test sound is. The data come from the DCASE2020 anomalous-sound-detection challenge (Koizumi et al., 2020), itself a combination of two public sound datasets, ToyADMOS (Koizumi et al., 2019) and MIMII (Purohit et al., 2019). The benchmark uses only the toy-car machine type, of seven toy-cars with 1000 normal samples each, because the authors judge that benchmarking would not benefit from separate models per machine type. The model is the DCASE2020 reference autoencoder, chosen because it is the reference for much of the audio anomaly-detection literature and adds a model type built only from fully connected (FC) layers. Its input and output size is 640 (five frames of 128 log-mel spectrogram bands); encoder and decoder each have four 128-unit FC layers, and the bottleneck has size 8. The anomaly score is the reconstruction error averaged over the central 6.4 seconds of a 10-second clip. The metric is AUC, which needs no threshold, and the evaluation set draws on four different machines, which the authors say is meant to give a broader test than a single machine would.

### 4.2 Quality targets

Each closed-division submission must reach a quality target (Table 1). The authors set each target slightly below the reference accuracy, to accommodate differences due to quantization and rounding across platforms. The closed division allows post-training quantization (PTQ), which converts a trained model to lower precision without retraining; quantization-aware training (QAT), which trains with low precision in mind, appears among the open-division entries in Section 5.3. For anomaly detection the threshold of AUC 0.85 was set from the 32-bit floating-point (fp32) reference value of 0.88 and the quantized value of 0.86. Section 5.1 gives the reference values and the resulting gaps, which show how much room the targets leave.

### 4.3 Divisions and a modular reference implementation

Each benchmark's reference implementation contains everything from training scripts to a reference hardware platform. It provides a baseline, and a submitter can modify one component to show what a single hardware or software component contributes. The reference implementations run TFLite models with TFLM (David et al., 2020) on the NUCLEO-L4R5ZI development board, using a known-good snapshot of the runtime for stability. Build details are in Appendix A.

In the closed division, submitters must use the same models, datasets and quality targets as the reference. PTQ with the provided calibration datasets is allowed; retraining and weight replacement are prohibited. This division is meant to compare inference stacks, not new models. In the open division, submitters may change the model, training scripts and dataset. The accuracy is still measured on the same test dataset, but the accuracy threshold need not be met, which lets submitters show tradeoffs between accuracy, latency and energy, and each must document how it deviates from the reference. Any change to a component the authors mark as open-division-only moves a submission to that division.

### 4.4 Measurement procedure and framework

The devices lack the resources to run a full benchmark locally, so a framework on a host computer controls and measures the device under test (DUT). Three scores are defined. For latency, the framework repeats five times: it downloads an input, loads the input tensor, runs inference for at least 10 seconds and 10 iterations, and measures inferences per second (IPS); the score is the median IPS of the five runs. For accuracy, it performs a single inference on the entire set of validation inputs and computes Top-1 percent or AUC, and each model has a minimum accuracy that must be met for the score to be valid. For energy, it repeats the latency procedure and also measures the total energy in the timing window to compute micro-Joules per inference, again taking the median of five measurements.

The framework has two hardware configurations, provided because the energy setup is more complex and energy scores may not be wanted. The latency and accuracy configuration connects the host computer to the DUT through a serial port. The energy configuration adds an isolating input-output manager and an energy monitor (hardware details in Appendix A). Level-shifter power is excluded from the energy score because it is a framework cost, not a DUT cost, and only one power supply may power the core, so that no other energy source can defeat the measurement. A host runner gives a consistent interface, standardizes execution, and downloads the many input files that a platform with under a megabyte of flash memory cannot hold. On the device, thin firmware implements five functions: a timestamp of at least one millisecond resolution, serial communication, loading the input tensor, a single inference, and printing the results.

## 5. Results

The results answer RQ1 with the reference numbers, RQ2 with the reference-board statement, and RQ3 with the submission round. The paper reports no variance for any accuracy or AUC value, and the reference latency and energy numbers appear only in a figure that is not available here.

### 5.1 Reference models against their quality targets

Table 2 puts each reference result beside its target. Each result exceeds its target, by a gap of 0.01 to 0.03 AUC for anomaly detection and about 1.5 to 6 accuracy points for the other three tasks.

**Table 2.** Reference results and quality targets. The gap is the reference value minus the target (our arithmetic).

| Benchmark | Reference result | Evaluation set | Quality target | Gap |
| --- | --- | --- | --- | --- |
| Visual wake words | about 86% accuracy | preprocessed MSCOCO 2014 test dataset | 80% | about 6 points |
| Image classification | 86.5% accuracy | 200 images from the CIFAR-10 test set | 85% | 1.5 points |
| Keyword spotting | 91.6% accuracy (91.7% on 1000 utterances) | full test set | 90% | 1.6 points |
| Anomaly detection | AUC 0.88 (fp32), 0.86 (quantized) | 248 samples, four machines | AUC 0.85 | 0.03 (fp32), 0.01 (quantized) |

The visual wake words reference reaches about 86% accuracy against the 80% required of closed-division submissions, so it clears its target. The image classification reference reaches 86.5% on 200 images chosen from the CIFAR-10 test set, against a target of 85%, so its margin is small. For keyword spotting, the quantized reference model shows 91.6% on the full test set and 91.7% on the random 1000-utterance subset used for on-device evaluation, both above the requirement of 90%; the model achieved 92.2% in the authors' own experiments. For anomaly detection, on an evaluation set of 248 samples from four different machines, the fp32 reference model reaches an AUC of 0.88 and the quantized model 0.86, against the benchmark threshold of AUC 0.85.

For RQ1 these values show that each target sits below what its reference model reaches, by a small margin for the quantized anomaly detection model and a larger one for visual wake words. They do not show how sensitive the targets are to the evaluation subset, because no spread or interval is reported and the on-device sets are small.

### 5.2 Reference implementations on the reference board

The authors ran each reference implementation on the NUCLEO-L4R5ZI board. They state that the four benchmarks cover a wide scope in terms of latency and energy, and that each reference meets the minimum accuracy. The latency and energy values sit in the authors' Figure 5, which is not recoverable from the materials this presentation draws on, so no numbers are given and no chart is drawn.

### 5.3 The June 2021 submission round

Submitting organizations implement the benchmarks on their own hardware and software stacks and submit results and implementations twice a year; the submitters and a review committee then peer-review the results. Table 3 lists the five rows of the first round, which took place in June 2021.

**Table 3.** The v0.5 submission round (the authors' Table 2). Modification marks in the original are illegible in the source text and omitted.

| Division | Numerics and software stack | Hardware | What the entry set out to demonstrate |
| --- | --- | --- | --- |
| Closed | INT-8 PTQ; TensorFlow Lite Micro | ARM microcontroller | Baseline performance results on the reference platform |
| Closed | INT-8 PTQ; TensorFlow Lite Micro | RISC-V microcontroller | Performance of a RISC-V microcontroller customized for neural network inference |
| Closed | FP-32 and INT-8 PTQ; LEIP Framework | RasPi 4 | Capabilities of a software-only optimization toolchain that is agnostic of the hardware |
| Closed | INT-8 PTQ; Syntiant TDK | Neural network accelerator | Ultra-low power hardware efficiency for running deep neural networks |
| Open | QKeras; Int-6/8 QAT; HLS4ML | FPGA | Rapid end-to-end development of machine learning accelerators on reconfigurable fabrics |

The round included both divisions and both hardware and software vendors, each with a specific element to show. One organization used the benchmark to demonstrate that its software development kit (SDK) tools are hardware agnostic, another a neural-network accelerator, an academic institute the potential of microcontrollers based on RISC-V, a free, open standard instruction set architecture (Asanovic et al., 2014), and a team its hls4ml (high-level synthesis for ML) open-source workflow for designing neural networks for efficient dataflow architectures. The authors read trends from these entries. Eight-bit integer was the most common numerical format because it offers a performance boost with little impact on accuracy. Software stacks ranged from open-source interpreters such as TFLite Micro to hardware-specific inference compilers, which the authors take to indicate a trade-off between optimization and portability. Hardware included microcontrollers, accelerators and reconfigurable hardware, which can use variable-precision models for increased performance. Power consumption ranged from µWatts to Watts. None of the submissions modified the training dataset, although the open division allows it; the authors expect this to change in future versions.

The authors conclude that the benchmark suite was able to accommodate this diverse set of goals because of its modular design. The round shows what entries were made, not their accuracy, latency or energy, because no such values appear in the project materials. The trends come from five table rows in a single round.

## 6. Discussion

**Answers to the three questions.** For RQ1, the paper specifies four tasks with datasets, small models and quality targets, and the reference models clear those targets, on single numbers without spread. For RQ2, the paper specifies a closed division that fixes models, datasets and targets, an open division that relaxes them, a modular reference implementation, and a procedure and framework for latency, accuracy and energy; these are stated design choices with the authors' reasons. What the paper does not give is a measured test of whether comparisons under these rules are fair. For RQ3, the authors interpret the round as showing that the modular design accommodated diverse goals. This reading is consistent with the mix of divisions and vendors in Table 3; it rests on five entries in one round, with no submission measurements and no comparison against a design that is not modular.

**Implications and the authors' expectations.** The authors state that the benchmarks have already acted as a standard set of tasks for TinyML research (Banbury et al., 2021), and that they have been turned into public projects on a TinyML development platform. The project's repository description (its README file) lists releases from v0.5 (Jun 16, 2021) to v1.1 (Jun 27, 2023) and expects the next round, v1.2, to have a deadline of March 15, 2024 (dates not yet finalized). The paper describes v0.5 only, so what changed in later versions is outside this presentation. The authors expect the benchmark to standardize the field and enable progress through competition and comparability, and expect a collaborative community to help set standards for responsible deployment. They also warn that the technology could be misused to track and monitor unwilling individuals and that inexpensive devices can increase electronic waste. These are forward-looking statements, not results.

## 7. Limitations

The authors state four limitations. First, MLPerf Tiny will keep evolving with new benchmarks for new application domains such as wearables, medical devices and environmental monitoring, while a benchmark must also be stable over time to track historical progress. The authors envision a subset of benchmarks kept long-term stable. The suite described here is therefore a snapshot of an evolving benchmark, not final coverage.

Second, streaming inputs are hard to recreate. Keyword spotting and anomaly detection are time-domain tasks that typically involve continuously streaming inputs, where information from previous time steps can improve the performance-efficiency tradeoff. The limited bandwidth between the test runner and the DUT makes it difficult to recreate a streaming scenario without adding delays from data transfer, so latency and energy for these tasks do not reflect the gains that streaming could allow.

Third, the pre-processing choice can distort results. Excluding feature extraction from the measurement while allowing submitters to choose variations creates a degenerate case in which everything up to the penultimate layer is defined as feature extraction. A rigidly defined feature extraction precludes joint optimization over features and model architecture, which can be critical in the constrained systems the suite targets, and the pre-selected feature choices somewhat limit innovation in keyword spotting. Including feature extraction has its own complexity: for one second of audio, a non-streaming benchmark would have one inference cycle and 40 feature extraction cycles, over-emphasizing the cost of feature extraction. The authors aim to include pre-processing in future versions. Until then, measured latency and energy can misstate whole-application cost.

Fourth, the closed division includes models based mainly on FC and CNN layers, and only open-division submissions may deviate. Future reference implementations may add other architectures, for example recurrent networks. Closed-division comparisons therefore cover these two model families only.

Additional caveats. The following caveats are ours, not the authors', and each bounds specific claims. First, the latency and energy values of the reference implementations are not in the project materials, so the statement that the references span a wide range is reported without magnitudes. Second, every accuracy and AUC value is a single number on a fixed set, of 200 images, 1000 utterances or 248 samples for the on-device sets, with no interval, so gaps of one or two points should not be read as precise margins. Third, the trends from the first round rest on five table rows from one round and describe that round, not the field. Fourth, no measured accuracy, latency or energy values from the submissions are available, so the fairness and comparability the design aims at are described but not shown numerically. Fifth, statements about current use, adoption and impact are the authors' own, and the README lists later versions whose changes the materials do not describe.

## 8. Conclusion

MLPerf Tiny specifies four tasks with quality targets, a modular reference implementation, closed and open divisions, and a framework that reports accuracy, latency and energy for ML inference on ultra-low-power devices. The reference models clear their targets and the June 2021 round drew varied entries, which the authors read as fitting the modular design. What remains open is whether comparisons under these rules stay fair as the suite changes: the authors say streaming, pre-processing and model-family coverage are not yet handled, and the paper offers no submission measurements. The authors plan new application domains, a subset kept stable over time, pre-processing in the measured scope, and additional model architectures such as recurrent neural networks.

## Appendix A. Reference platform and framework details

This appendix holds reproducibility detail that the main text points to. It supports the reference-platform and framework descriptions in Sections 4.3 and 4.4.

The reference implementations are built as a bare-metal MBED project with the GCC-ARM toolchain and run on the NUCLEO-L4R5ZI board. In the energy configuration the input-output manager is deployed as an Arduino UNO with its own custom firmware. The runner contains three energy-monitor drivers: the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705. Whichever monitor is used, it must supply one channel for the device and another for the level shifters, whose power is not counted in the energy score.

## References

- Asanovic, K., and Patterson, D. A. (2014). Instruction sets should be free: The case for risc-v. EECS Department, University of California, Berkeley, Tech. Rep. UCB/EECS-2014-146.
- Banbury, C., Zhou, C., Fedorov, I., Matas, R., Thakker, U., Gope, D., Janapa Reddi, V., Mattina, M., and Whatmough, P. (2021). Micronets: Neural network architectures for deploying tinyml applications on commodity microcontrollers. Proceedings of Machine Learning and Systems, 3.
- Bouguera, T., Diouris, J.-F., Chaillout, J.-J., Jaouadi, R., and Andrieux, G. (2018). Energy consumption model for sensor nodes based on lora and lorawan. Sensors, 18(7):2104.
- Chowdhery, A., Warden, P., Shlens, J., Howard, A., and Rhodes, R. (2019). Visual wake words dataset. CoRR, abs/1906.05721.
- David, R., Duke, J., Jain, A., Reddi, V. J., Jeffries, N., Li, J., Kreeger, N., Nappier, I., Natraj, M., Regev, S., et al. (2020). Tensorflow lite micro: Embedded machine learning on tinyml systems. arXiv preprint arXiv:2010.08678.
- Fedorov, I., Adams, R. P., Mattina, M., and Whatmough, P. (2019). Sparse: Sparse architecture search for cnns on resource-constrained microcontrollers. In Advances in Neural Information Processing Systems 32, pages 4978-4990.
- Gal-On, S., and Levy, M. (2012). Exploring coremark a benchmark maximizing simplicity and efficacy. The Embedded Microprocessor Benchmark Consortium.
- He, K., Zhang, X., Ren, S., and Sun, J. (2016). Deep residual learning for image recognition. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 770-778.
- Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., and Adam, H. (2017). Mobilenets: Efficient convolutional neural networks for mobile vision applications. arXiv preprint arXiv:1704.04861.
- Koizumi, Y., Saito, S., Uematsu, H., Harada, N., and Imoto, K. (2019). Toyadmos: A dataset of miniaturemachine operating sounds for anomalous sound detection. In 2019 IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA), pages 313-317.
- Koizumi, Y., Kawaguchi, Y., Imoto, K., Nakamura, T., Nikaido, Y., Tanabe, R., Purohit, H., Suefusa, K., Endo, T., Yasuda, M., and Harada, N. (2020). Description and discussion on DCASE2020 challenge task2: Unsupervised anomalous sound detection for machine condition monitoring. arXiv e-prints: 2006.05822.
- Krizhevsky, A., Nair, V., and Hinton, G. (2009). Cifar-10 (canadian institute for advanced research).
- Lin, T.-Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollar, P., and Zitnick, C. L. (2014). Microsoft coco: Common objects in context. In European conference on computer vision, pages 740-755.
- Purohit, H., Tanabe, R., Ichige, K., Endo, T., Nikaido, Y., Suefusa, K., and Kawaguchi, Y. (2019). Mimii dataset: Sound dataset for malfunctioning industrial machine investigation and inspection. arXiv preprint arXiv:1909.09347.
- Reddi, V. J., Cheng, C., Kanter, D., Mattson, P., Schmuelling, G., Wu, C.-J., et al. (2019). Mlperf inference benchmark.
- Torralba, A., Fergus, R., and Freeman, W. T. (2008). 80 million tiny images: A large data set for nonparametric object and scene recognition. IEEE transactions on pattern analysis and machine intelligence, 30(11):1958-1970.
- Warden, P. (2018). Speech commands: A dataset for limited-vocabulary speech recognition. arXiv preprint arXiv:1804.03209.
- Zhang, Y., Suda, N., Lai, L., and Chandra, V. (2017). Hello edge: Keyword spotting on microcontrollers. arXiv preprint arXiv:1711.07128.
