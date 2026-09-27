# MLPerf Tiny: A Benchmark Suite for Ultra-Low-Power Machine Learning Inference

**Colby Banbury, Vijay Janapa Reddi, Peter Torelli, Jeremy Holleman, Nat Jeffries, Csaba Kiraly, Pietro Montino, David Kanter, Sebastian Ahmed, Danilo Pau, Urmish Thakker, Antonio Torrini, Peter Warden, and collaborators from 50+ organizations**

---

## Abstract

Advances in ultra-low-power machine learning — a field known as TinyML — promise to enable a new class of always-on, battery-powered smart devices that perform inference directly on sensors, without cloud connectivity. However, the field has lacked a standardized, reproducible benchmark for comparing systems on the metrics that matter most: accuracy, latency, and energy consumption. We present MLPerf Tiny {C002}, the first industry-standard benchmark suite for TinyML inference, developed collaboratively by more than 50 organizations from academia and industry {C003}. The suite comprises four benchmarks — keyword spotting, visual wake words, image classification, and anomaly detection — spanning key embedded application domains. A modular two-division design enables hardware and software vendors alike to demonstrate the value of their specific contribution in a fair and reproducible setting. The first submission round (v0.5, June 2021) attracted five diverse submissions spanning ARM microcontrollers, RISC-V processors, neural network accelerators, a software optimization toolchain, and an FPGA platform {C006}, demonstrating that the benchmark accommodates fundamentally different hardware and software stacks within a single comparable round {C008}. MLPerf Tiny is open source and publicly available.

---

## 1. Introduction

Machine learning inference at the extreme edge — on devices that consume less than a milliwatt of power — is an emerging field with the potential to transform how intelligent sensing is deployed at scale. Devices in this class, typically microcontrollers (MCUs) running at 10–250 MHz with power budgets under 50 mW, can perform continuous inference near the sensor, enabling applications such as always-on keyword detection, occupancy sensing, and industrial anomaly detection. Because these devices operate at such small power budgets, the energy cost of wireless communication — transmitting raw sensor data to a cloud server for processing — far exceeds the energy cost of running inference locally (Bouguera et al., 2018). This changes the economics of data collection and processing fundamentally, making on-device inference not just convenient but necessary for battery-powered deployment.

The field of TinyML — ML inference under a milliwatt — sits at the intersection of machine learning, embedded systems, and hardware design. Co-optimizing across all three layers is required to meet the tight constraints of these devices. But co-optimization requires comparison: developers need to know whether a new model architecture, quantization scheme, or inference engine actually improves on the state of practice. Without a standard benchmark, claims of improvement are made against different baselines, on different hardware, using different metrics, making it impossible to judge whether progress is real or whether one system genuinely outperforms another.

In this paper, we present MLPerf Tiny, an open-source benchmark suite designed to fill this gap {C001}. MLPerf Tiny measures three axes of performance — accuracy, inference throughput (in inferences per second), and energy efficiency (in microjoules per inference) — for each of four representative benchmarks {C002}. The suite is built around a modular design that allows both hardware and software contributors to demonstrate the advantage of their product, and it provides complete reference implementations to act as open-source community baselines. The benchmark is the collaborative effort of more than 50 organizations from industry and academia, ensuring that the selected tasks reflect community needs rather than the preferences of a single vendor {C003}.

The paper is organized as follows. Section 2 describes the specific challenges that TinyML systems pose for benchmarking. Section 3 situates MLPerf Tiny in relation to existing benchmarks. Section 4 describes the four benchmark tasks, their datasets, models, and quality targets. Section 5 presents the measurement methodology and the two-division submission structure. Section 6 summarizes results from the first submission round. Sections 7 and 8 address limitations and conclusions.

---

## 2. Why TinyML Is Hard to Benchmark

Designing a fair benchmark for TinyML systems is more complex than adapting existing ML benchmarks to smaller models. Four challenges make this a distinct problem.

**Low power as a first-class metric.** On standard ML hardware (GPUs, server CPUs), energy is rarely the primary concern. For TinyML devices, power consumption is definitional: the field is defined by sub-milliwatt operation. A useful benchmark must therefore profile energy consumption, not just throughput or accuracy. However, measuring energy fairly is non-trivial. TinyML devices span a wide power range; determining the boundary of what counts as "device power" (versus framework overhead, peripherals, or level-shifters) is contested; and chip peripherals and firmware can affect measurements.

**Extreme memory constraints.** Standard ML benchmarks are designed for models measured in megabytes or gigabytes of memory. TinyML devices typically provide flash and SRAM on the order of kilobytes to a few hundred kilobytes — roughly two orders of magnitude less than a smartphone. A benchmark for TinyML must use models that actually fit on the target hardware, which requires a fundamentally different selection of tasks and architectures.

**Hardware heterogeneity.** Despite its relative youth, the TinyML ecosystem already spans general-purpose MCUs (ARM Cortex-M, RISC-V), specialized neural network accelerators, digital signal processors, and reconfigurable hardware such as FPGAs. Unlike the relatively homogeneous landscape of datacenter ML (NVIDIA GPUs, TPUs), TinyML devices often lack otherwise standard features such as a system clock, debug interface, or operating system. A benchmark that requires any of these non-universal features immediately excludes large segments of the hardware landscape.

**Software heterogeneity.** To extract maximum performance from their hardware, TinyML practitioners often develop custom inference engines, compilers, and hardware-specific operators. Restricting a benchmark to a single inference framework (e.g., requiring TensorFlow Lite Micro on all platforms) would penalize hardware vendors who have built their own optimized stack, producing unrepresentative results. A useful benchmark must therefore permit a wide range of inference stacks while still enabling fair comparison.

These four challenges interact: a solution to the memory constraint (tiny models) interacts with the hardware heterogeneity challenge (some hardware supports only specific layer types), and software heterogeneity makes it hard to isolate the contribution of hardware versus software. MLPerf Tiny addresses each of these challenges through specific design choices described in Sections 4 and 5.

---

## 3. Related Work

Several existing benchmarks address related but distinct problems.

**CoreMark** (Gal-On & Levy, 2012) has become the standard benchmark for MCU-class devices because of its ease of implementation and use of real algorithms. However, CoreMark benchmarks general-purpose CPU performance — integer operations, data manipulation — rather than ML inference workloads. It does not include neural network operations, does not profile power consumption, and is therefore not representative of TinyML tasks.

**MLMark** (Torelli & Bangale, n.d.) addresses the ML inference gap by using actual neural network workloads. However, MLMark's supported models (ResNet-50, MobileNet-V1 at full scale, SSD-MobileNet) require hundreds of megabytes to gigabytes of memory — far beyond what TinyML devices provide. MLMark also does not include energy measurement, which is critical for any TinyML benchmark.

**MLPerf Inference** (Reddi et al., 2019) is the closest predecessor: a community-driven benchmark for ML inference across a range of hardware. MLPerf Inference has been influential at datacenter and edge scales and has plans to add power measurement. However, its current benchmarks target hardware with gigabytes of memory and require implementations of large models (ResNet-50, BERT, etc.) that are incompatible with MCU-class devices. The infrastructure assumptions of MLPerf Inference — file I/O, operating systems, standard debug interfaces — also exclude the hardware most relevant to TinyML.

None of these existing benchmarks jointly measures accuracy, latency, and energy for ML inference on microcontroller-class hardware. MLPerf Tiny is designed to fill this gap {C001}.

---

## 4. Benchmark Design

### 4.1 Overview

MLPerf Tiny v0.5 consists of four inference benchmarks, each targeting a representative embedded application domain {C003}. Every benchmark specifies a task, a dataset, a reference model with its TFLite model file size and memory footprint, and a minimum quality target. Table 1 summarizes the benchmarks.

**Table 1. MLPerf Tiny v0.5 Inference Benchmarks**

| Use Case | Dataset (Input Size) | Model (TFLite Size) | Quality Target (Metric) |
|---|---|---|---|
| Keyword Spotting | Speech Commands v2 (49×10) | DS-CNN (52.5 KB) | 90% (Top-1) |
| Visual Wake Words | VWW Dataset (96×96) | MobileNetV1 (325 KB) | 80% (Top-1) |
| Image Classification | CIFAR-10 (32×32) | ResNetv1 (96 KB) | 85% (Top-1) |
| Anomaly Detection | ToyADMOS/MIMII (5×128) | FC-AutoEncoder (270 KB) | 0.85 (AUC-ROC) |

Reference implementations run on the STMicroelectronics NUCLEO-L4R5ZI ARM Cortex-M4 board using TensorFlow Lite for Microcontrollers (TFLM) (David et al., 2020), built with the MBED bare-metal project and GCC-ARM toolchain. These implementations provide open-source baselines against which submitters can compare their results.

### 4.2 Keyword Spotting

Keyword spotting (KWS) — continuously monitoring audio for specific trigger words like "Hey Siri" or "Alexa" — is one of the most prevalent TinyML applications, requiring both low latency and low power for always-on operation. The reference model is a small depthwise-separable convolutional neural network (DS-CNN) described by Zhang et al. (2017). Depthwise-separable convolutions decompose a standard convolution into a depthwise spatial convolution followed by a pointwise (1×1) convolution, dramatically reducing parameter count and computation while preserving representational capacity. With 38.6K parameters, the DS-CNN fits within the memory constraints of most microcontrollers {C004}.

The benchmark uses the Speech Commands v2 dataset (Warden, 2018), a publicly available collection of 105,829 utterances from 2,618 speakers with diverse accents, covering 30 words plus background noise, under the Creative Commons BY license. Following common practice, the benchmark uses 10 command words; the remaining 20 words and background noise are combined into an "unknown" category, producing 12 output classes including "silence." This design exercises both command-phrase recognition (multiple specific words) and wake-word detection (open-set rejection of non-target audio).

Feature extraction (converting raw audio to the 49×10 log-mel spectrogram input) is excluded from the measurement window, since the benchmark focuses on model inference. The DS-CNN reference model achieves 92.2% top-1 accuracy in the authors' experiments; the quantized version reaches 91.6% on the full test set and 91.7% on a 1,000-utterance evaluation subset {C004}. The quality target for valid submissions is 90% top-1 accuracy on the 1,000-utterance subset, accommodating minor differences in quantization strategies.

### 4.3 Visual Wake Words

The visual wake words (VWW) task — detecting whether a person is present in an image — is directly relevant to smart home and occupancy-sensing applications, where a camera-equipped device must make a binary decision continuously and at low power. The benchmark is based on the Visual Wake Words Challenge (Chowdhery et al., 2019), which defines person detection as a binary classification problem.

The dataset is derived from MSCOCO 2014 (Lin et al., 2014), one of the standard large-scale image recognition datasets, preprocessed to retain only images where a person occupies more than 2.5% of the image area, and resized to 96×96 pixels. The reference model is MobileNetV1 (Howard et al., 2017) with a width multiplier of 0.25 — a deliberate reduction from the full MobileNetV1 to shrink the model to 325 KB TFLite format. The model achieves approximately 86% top-1 accuracy on the test set, and the quality target for closed-division submissions is 80%, providing a margin that accommodates quantization-induced accuracy variation.

### 4.4 Image Classification

The image classification benchmark uses CIFAR-10 (Krizhevsky et al., 2009), a 10-class benchmark with 60,000 images (32×32 pixels, RGB) covering airplanes, cars, birds, cats, deer, dogs, frogs, horses, ships, and trucks. CIFAR-10's low resolution makes it uniquely suited for TinyML: its 32×32 input is compatible with model sizes that fit on microcontrollers, and a substantial body of prior TinyML work (Fedorov et al., 2019) has used it as a reference point, enabling historical comparison.

The reference model is a customized version of ResNetv1 (He et al., 2016), modified to fit the resource constraints of MCUs. Compared to the original ResNet, this variant uses three residual stacks instead of four, omits the initial pooling layer (because the 32×32 input is already small), and uses fewer convolution filters and smaller strides, resulting in a 96 KB TFLite model. The model achieves 86.5% accuracy on a 200-image test subset {C005}; the quality target is 85%.

### 4.5 Anomaly Detection

The anomaly detection benchmark is distinctive in two ways: it uses unsupervised learning, and it evaluates a task of particular industrial relevance — detecting machine faults from acoustic signals. In industrial settings, failures are rare and diverse, so only normal-operation data is readily available for training. An autoencoder learns to reconstruct normal sounds; anomalous sounds produce higher reconstruction error and are flagged accordingly.

The dataset is drawn from the DCASE2020 Challenge Task 2 (Koizumi et al., 2020), which combines the ToyADMOS (Koizumi et al., 2019) and MIMII (Purohit et al., 2019) datasets. The benchmark uses only the toy-car subset, with seven toy-cars providing 1,000 training samples each of normal operation mixed with environmental noise.

The reference model is a fully connected autoencoder. Audio is pre-processed into a log-mel spectrogram with 128 frequency bands and 32 ms frames. The model operates on a sliding window of five consecutive frames (640 total input values), running over the central 6.4 seconds of a 10-second clip. The averaged reconstruction error (mean squared error) is the anomaly score. Both the encoder and decoder consist of four fully connected layers of 128 units each with batch normalization and ReLU activations, with a bottleneck of 8 units, yielding a 270 KB TFLite model.

Because the anomaly score must be thresholded to produce a binary decision, and because the threshold depends on the deployment context, the quality metric is the area under the receiver operating characteristic curve (AUC-ROC), which evaluates discrimination performance without committing to a threshold. The fp32 reference model achieves AUC 0.88; the quantized version achieves AUC 0.86 on a 248-sample evaluation set covering normal and anomalous sounds from four machines {C005}. The quality target is AUC 0.85.

---

## 5. Measurement Methodology

### 5.1 Closed and Open Divisions

MLPerf Tiny uses a two-division submission structure designed to balance comparability with flexibility.

In the **closed division**, submitters must use the same model architecture, dataset, and quality target as the reference implementation. The only permitted modification is post-training quantization (PTQ) — applying fixed-point compression to the pre-trained reference weights using the provided calibration dataset. Retraining, fine-tuning, or replacing model weights is not permitted. The closed division enables direct, controlled comparison of inference stacks: two submitters in the closed division who meet the quality target can be compared on latency and energy with confidence that differences reflect the hardware and inference stack, not the model.

The **open division** is designed to capture a wider range of innovation. Submitters may change the model architecture, training procedure, and training dataset. They must use the same test dataset for accuracy evaluation but are not required to meet the quality threshold — allowing submitters to explore and report the tradeoff between accuracy, latency, and energy. Each open-division submission must document its deviations from the reference.

This structure is explicitly designed to accommodate different types of contributors: a hardware vendor demonstrating a new accelerator works best in the closed division (where the model is fixed), while a software team with a novel training-time quantization method benefits from the open division.

### 5.2 Measurement Harness

TinyML devices typically lack the resources needed to run a self-contained benchmark — they have no file I/O, no standard output, and often no operating system. The benchmark harness therefore separates the **host** (a PC running the benchmark runner software) from the **device under test** (DUT), connected via a serial port.

For latency and accuracy measurement, the connection is a simple serial link. For energy measurement, a third component — an electrical isolation proxy (an Arduino UNO acting as an IO Manager) — is placed between the host and the DUT, preventing the host's power supply from contaminating the DUT's energy reading. An energy monitor (one of three supported options: the STMicroelectronics LPM01A, Jetperch Joulescope JS110, or Keysight N6705) supplies and measures power to the DUT core only. Level shifters on the isolation proxy handle voltage domain differences; the power consumed by these level shifters is excluded from the reported score.

The DUT exposes a minimal firmware API: a timestamp function (1 ms resolution for latency; a GPIO toggle for energy synchronization), UART communication, an input-loading function, a single-inference function, and a results-printing function. This minimal API minimizes porting effort and does not restrict the underlying inference implementation — submitters can use any SDK, compiler, or hardware-specific library they choose.

### 5.3 Measurement Protocol

The measurement procedure is identical for latency and energy, differing only in what is recorded:

- **Latency:** Five measurement trials, each consisting of loading an input stimulus and running inference for a minimum of 10 seconds and 10 iterations. The score is the median inferences per second (IPS) across the five trials.
- **Energy:** The same five-trial procedure, additionally measuring total energy consumed in the timing window and computing microjoules per inference (µJ/inference). The score is the median across five trials.
- **Accuracy:** A single pass over the full evaluation set, collecting output probabilities and computing top-1 accuracy (for classification tasks) or AUC-ROC (for anomaly detection). A submission's latency and energy scores are valid only if its accuracy meets the minimum quality target.

Using the median of five runs reduces the impact of outlier measurements from initialization artifacts or transient system events. The minimum 10-second and 10-iteration requirements ensure that the measurement window captures steady-state behavior rather than startup overhead.

---

## 6. Submissions and Assessment

### 6.1 First Submission Round (v0.5)

The first submission round opened in June 2021. Five submissions were received, summarized in Table 2 {C006}. The results are publicly available at mlcommons.org and all implementations are reproducible via GitHub.

**Table 2. MLPerf Tiny v0.5 Submission Summary**

| Division | Numerics | Framework | Hardware | What it demonstrates |
|---|---|---|---|---|
| Closed | INT-8 PTQ | TensorFlow Lite Micro | ARM MCU | Baseline performance on the reference platform |
| Closed | INT-8 PTQ | TensorFlow Lite Micro | RISC-V MCU | Performance of a RISC-V MCU customized for neural network inference |
| Closed | FP-32 & INT-8 PTQ | LEIP Framework | Raspberry Pi 4 | Capabilities of a hardware-agnostic software optimization toolchain |
| Closed | INT-8 PTQ | Syntiant TDK | NN Accelerator | Ultra-low power efficiency of a dedicated NN accelerator |
| Open | Int-6/8 QAT | HLS4ML | FPGA | Rapid end-to-end ML accelerator development on reconfigurable fabric |

All results underwent peer review by the submitting organizations and a review committee to verify conformance with the run rules.

### 6.2 Observations from v0.5

The v0.5 submissions collectively illustrate several trends in the emerging TinyML ecosystem.

**Quantization format.** Four of the five submissions used INT-8 post-training quantization, making it the most common numerical format {C007}. INT-8 inference offers a substantial throughput improvement over 32-bit floating point while incurring limited accuracy loss, as demonstrated by the small gap between fp32 and quantized accuracy across all benchmarks (e.g., AUC 0.88 vs. 0.86 for anomaly detection). The one open-division FPGA submission used INT-6/8 quantization-aware training (QAT) — a training-time quantization method that co-optimizes the model and its quantization for a target bit width — to achieve further efficiency on reconfigurable hardware.

**Platform diversity and power range.** The submissions span platforms from dedicated neural network accelerators (targeting ultra-low power, measured in microwatts) to a general-purpose Raspberry Pi 4 (measured in watts), illustrating the breadth of the TinyML landscape {C010}. The benchmark framework accommodated this three-orders-of-magnitude range in power consumption within a single submission round.

**Software heterogeneity.** ML inference frameworks ranged from TensorFlow Lite Micro (open-source interpreter) to hardware-specific inference compilers and a high-level synthesis (HLS) workflow (HLS4ML). The latter — originally developed at the Large Hadron Collider to perform sub-microsecond ML inference — demonstrates that the open division can attract contributions from outside the traditional embedded ML community.

**Dataset modification.** No v0.5 submission modified the training dataset {C009}. This suggests that at this stage of the field's development, optimization effort is concentrated on model architecture, inference framework, and hardware, rather than on data curation or augmentation. The benchmark's open division explicitly permits dataset modification, and future rounds may see this change.

**Flexibility confirmed.** The modular design successfully enabled submitters with fundamentally different goals — demonstrating hardware acceleration, validating a software toolchain's portability, and showcasing reconfigurable-hardware ML — to participate in the same benchmark round and produce directly comparable results on the metrics each cared about {C008}.

---

## 7. Limitations

**Pre-processing and streaming inputs.** The benchmark measures inference only: pre-processing steps (converting raw audio to spectrograms, resizing images) are excluded from the measurement window. This exclusion was motivated by the complexity of including pre-processing fairly when submitters may implement it differently. However, it creates a degenerate-case risk: a submitter could define most of the computation as "feature extraction" rather than "inference," artificially improving the reported score. Separately, TinyML applications typically process streaming input, but the bandwidth constraints of the serial link between the host PC and DUT make it infeasible to recreate a continuous streaming scenario without introducing data-transfer latency. Future versions plan to include pre-processing in the measurement window and to address streaming scenarios. {L004}

**Architecture coverage.** The closed-division reference models use fully connected and convolutional layers. Recurrent architectures (LSTMs, GRUs), attention mechanisms, and other layer types commonly used in sequence modeling are not represented in the current closed division. Submitters in the open division are free to use any architecture, but fair closed-division comparison is limited to the architectures the reference models can test. Expanding the reference model suite to include recurrent architectures is a planned future direction. {L005}

**Single submission round.** The v0.5 evidence is one submission round with five participants. Observations about trends — INT-8 dominance, the absence of dataset modification, the power ranges seen — reflect the state of the field at a single point in time and may change substantially in future rounds {L003}. MLPerf Tiny accepts submissions twice per year, and the benchmark is designed to track progress longitudinally. Readers should treat the v0.5 observations as a snapshot of an emerging field rather than stable characterizations.

---

## 8. Conclusion

TinyML — machine learning inference on devices that consume less than a milliwatt of power — enables a qualitatively new class of always-on, privacy-preserving, battery-powered intelligent devices. Progress in this field requires a standard method of comparison: without one, optimization claims are made against incompatible baselines and on hardware that cannot be directly compared. Existing benchmarks (CoreMark, MLMark, MLPerf Inference) do not address TinyML's unique requirements: they lack energy measurement, require models too large for microcontroller memory, or are incompatible with the hardware heterogeneity of the field {C001}.

MLPerf Tiny addresses this gap through four inference benchmarks that jointly measure accuracy, latency, and energy, with a modular submission structure that accommodates both hardware and software contributors {C002} {C003}. The first submission round (v0.5, June 2021) demonstrated that the benchmark can attract and accommodate a diverse set of participants — spanning embedded MCUs, neural network accelerators, reconfigurable hardware, and software optimization toolchains — within a single, reproducible evaluation framework {C006} {C008}.

The benchmark is open source, community-governed, and designed for longitudinal use: successive submission rounds will build a multi-year record of TinyML system progress. As the field expands into new domains (wearable health monitoring, environmental sensing, medical devices), and as new architectural paradigms (transformers, neural architecture search) reach the embedded scale, the benchmark suite can be extended to reflect these developments. MLPerf Tiny provides the infrastructure for that comparison.

---

## References

Bouguera, T., Diouris, J.-F., Chaillout, J.-J., Jaouadi, R., and Andrieux, G. (2018). Energy consumption model for sensor nodes based on LoRa and LoRaWAN. *Sensors*, 18(7):2104.

Chowdhery, A., Warden, P., Shlens, J., Howard, A., and Rhodes, R. (2019). Visual wake words dataset. *CoRR*, abs/1906.05721.

David, R., Duke, J., Jain, A., Reddi, V. J., Jeffries, N., Li, J., Kreeger, N., Nappier, I., Natraj, M., Regev, S., et al. (2020). TensorFlow Lite Micro: Embedded machine learning on TinyML systems. *arXiv preprint arXiv:2010.08678*.

Fedorov, I., Adams, R. P., Mattina, M., and Whatmough, P. (2019). SpArSe: Sparse architecture search for CNNs on resource-constrained microcontrollers. *Advances in Neural Information Processing Systems*, 32:4978–4990.

Gal-On, S. and Levy, M. (2012). Exploring CoreMark: A benchmark maximizing simplicity and efficacy. *The Embedded Microprocessor Benchmark Consortium*.

He, K., Zhang, X., Ren, S., and Sun, J. (2016). Deep residual learning for image recognition. In *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, pages 770–778.

Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., and Adam, H. (2017). MobileNets: Efficient convolutional neural networks for mobile vision applications. *arXiv preprint arXiv:1704.04861*.

Koizumi, Y., Kawaguchi, Y., Imoto, K., Nakamura, T., Nikaido, Y., Tanabe, R., Purohit, H., Suefusa, K., Endo, T., Yasuda, M., and Harada, N. (2020). Description and discussion on DCASE2020 Challenge Task 2: Unsupervised anomalous sound detection for machine condition monitoring. *arXiv e-prints 2006.05822*.

Koizumi, Y., Saito, S., Uematsu, H., Harada, N., and Imoto, K. (2019). ToyADMOS: A dataset of miniature-machine operating sounds for anomalous sound detection. In *2019 IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA)*, pages 313–317.

Krizhevsky, A., Nair, V., and Hinton, G. (2009). CIFAR-10 (Canadian Institute for Advanced Research).

Lin, T.-Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollár, P., and Zitnick, C. L. (2014). Microsoft COCO: Common objects in context. In *European Conference on Computer Vision*, pages 740–755.

Purohit, H., Tanabe, R., Ichige, K., Endo, T., Nikaido, Y., Suefusa, K., and Kawaguchi, Y. (2019). MIMII dataset: Sound dataset for malfunctioning industrial machine investigation and inspection. *arXiv preprint arXiv:1909.09347*.

Reddi, V. J., Cheng, C., Kanter, D., Mattson, P., Schmuelling, G., Wu, C.-J., Anderson, B., Breughe, M., Charlebois, M., Chou, W., et al. (2019). MLPerf inference benchmark. *arXiv preprint*.

Torelli, P. and Bangale, M. (n.d.). Measuring inference performance of machine-learning frameworks on edge-class devices with the MLMark benchmark. *EEMBC Technical Literature*.

Warden, P. (2018). Speech commands: A dataset for limited-vocabulary speech recognition. *arXiv preprint arXiv:1804.03209*.

Zhang, Y., Suda, N., Lai, L., and Chandra, V. (2017). Hello Edge: Keyword spotting on microcontrollers. *arXiv preprint arXiv:1711.07128*.
