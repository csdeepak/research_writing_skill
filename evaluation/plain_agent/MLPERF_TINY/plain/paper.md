# MLPerf Tiny: An Industry-Standard Benchmark Suite for Ultra-Low-Power Machine Learning Systems

**Colby Banbury, Vijay Janapa Reddi, Peter Torelli, Jeremy Holleman, Nat Jeffries, Csaba Kiraly, Pietro Montino, David Kanter, Sebastian Ahmed, Danilo Pau, Urmish Thakker, Antonio Torrini, Peter Warden, Jay Cordaro, Giuseppe Di Guglielmo, Javier Duarte, Stephen Gibellini, Videet Parekh, Honson Tran, Nhan Tran, Niu Wenxu, Xu Xuesong**

*Harvard University, EEMBC, Syntiant, UNC Charlotte, Google, Digital Catapult, VoiceMed, MLCommons, Qualcomm, STMicroelectronics, SambaNova Systems, Silicon Labs, Columbia, UCSD, Latent AI, Fermilab, Peng Cheng Labs*

---

## Abstract

Advancements in ultra-low-power tiny machine learning (TinyML) systems promise to unlock an entirely new class of smart applications. However, continued progress is limited by the lack of a widely accepted and easily reproducible benchmark for these systems. To meet this need, this paper presents MLPerf Tiny, the first industry-standard benchmark suite for ultra-low-power tiny machine learning systems. The benchmark suite is the collaborative effort of more than 50 organizations from industry and academia and reflects the needs of the community. MLPerf Tiny measures the accuracy, latency, and energy of machine learning inference to properly evaluate the tradeoffs between systems. Additionally, MLPerf Tiny implements a modular design that enables benchmark submitters to show the benefits of their product, regardless of where it falls on the ML deployment stack, in a fair and reproducible manner. The suite features four benchmarks: keyword spotting, visual wake words, image classification, and anomaly detection.

---

## 1. Introduction

Machine learning (ML) inference on the edge is an increasingly attractive prospect due to its potential for increasing energy efficiency, privacy, responsiveness, and autonomy of edge devices. Thus far, edge ML has predominantly focused on mobile inference—smartphones and tablets running neural networks with hundreds of megabytes of available memory and power envelopes measured in watts. In recent years, however, there have been major strides towards expanding the scope of edge ML to ultra-low-power devices operating under fundamentally tighter constraints.

This subfield, known as "TinyML" (Banbury et al., 2021), targets ML inference under a milliWatt. At this power level, TinyML breaks the traditional power barrier that has historically prevented widely distributed machine intelligence. By performing inference on-device and near-sensor, TinyML enables greater responsiveness and privacy while avoiding the energy cost associated with wireless communication, which at this scale is far higher than the cost of compute itself (Bouguera et al., 2018). Furthermore, the efficiency of TinyML enables a class of smart, battery-powered, always-on applications that can revolutionize the real-time collection and processing of data—from industrial condition monitoring to wildlife tracking.

The hardware targeted by TinyML is qualitatively different from the platforms that the broader ML community is accustomed to benchmarking. TinyML devices are microcontrollers (MCUs) and similarly small processors typically running at between 10 MHz and 250 MHz, with peak memory measured in tens or hundreds of kilobytes (KB), not gigabytes. Deploying advanced ML applications at this scale requires co-optimization of each layer of the ML deployment stack—from the model architecture and numerical precision, to the inference runtime and the hardware microarchitecture—to achieve the maximum efficiency. This complex optimization makes direct comparison of solutions challenging and the impact of individual optimizations difficult to measure.

To enable continued innovation, a fair and reliable method of comparison is needed. This paper presents MLPerf Tiny, an open-source benchmark suite for TinyML systems. MLPerf Tiny provides a set of four standard benchmarks, selected by more than 50 organizations in academia and industry, measuring latency, energy, and accuracy simultaneously. It is designed with flexibility and modularity in mind to support both hardware and software users, and provides complete reference implementations to act as open-source community baselines.

---

## 2. Background: The TinyML Ecosystem and Its Benchmarking Challenges

For ML researchers from outside TinyML, understanding the unique constraints of the target platforms is essential for appreciating the design decisions behind MLPerf Tiny. Unlike benchmarks for server-class or mobile ML, where the dominant concern is throughput and occasionally memory, TinyML benchmarking must contend with four interacting and compounding obstacles.

### 2.1 Power as a First-Class Constraint

Power consumption is one of the defining features of TinyML systems; the canonical goal is inference under 1 mW. A useful benchmark must therefore profile the energy efficiency of each device in addition to its throughput and accuracy. This introduces practical challenges: TinyML devices can consume drastically different amounts of power, making it difficult to maintain measurement accuracy across the full range. Determining what falls under the scope of the power measurement is also non-trivial, since data paths and pre-processing steps can vary significantly between devices. Other factors, such as chip peripherals and underlying firmware, also affect measurements. Simply measuring wall-clock time and normalizing by a device's thermal design power—as is common in datacenter benchmarking—is insufficient.

### 2.2 Severe Memory Constraints

While traditional ML systems cope with resource constraints of a few gigabytes, TinyML systems typically cope with resources that are two orders of magnitude smaller. Popular inference benchmarks use models whose peak memory requirements are measured in gigabytes, while a typical TinyML device may offer only 256 KB of RAM and 1 MB of flash storage. This creates a model-selection problem: benchmarks must choose models that fit within these tight budgets while still representing meaningful ML tasks. Any overhead from the benchmarking framework itself can make the benchmark too large to run. Additionally, since devices vary widely even within the TinyML range, benchmarks should accommodate multiple levels of quantization and numerical precision.

### 2.3 Hardware Heterogeneity

Despite its relative youth, the TinyML ecosystem is already diverse in terms of performance, power, and capabilities. Devices range from general-purpose MCUs to novel architectures including event-based neural processors (Brainchip, 2021) and memory-compute devices. This heterogeneity poses challenges for any standardized framework. The device under test (DUT) may not include otherwise standard features such as a system clock or a debug interface. Creating a standard interface while minimizing porting effort is therefore a key challenge that existing benchmarks—designed for the relative uniformity of server or mobile hardware—do not adequately address.

### 2.4 Software and Toolchain Heterogeneity

TinyML systems are often tightly coupled with their inference stack and deployment tools. To achieve the highest efficiency, hardware vendors frequently develop proprietary toolchains that optimally deploy and execute a model on their specific hardware. This becomes increasingly critical on systems with multiple compute units, such as neural network accelerators and DSPs. A benchmark that restricts the inference stack—for instance, by mandating a single ML framework—would negatively impact performance on specialized systems and produce unrepresentative results. The benchmark must therefore balance optimality with portability, and comparability with representativeness.

---

## 3. Related Work

Several benchmarks exist for evaluating ML hardware, but none accurately represent the performance of TinyML workloads on tiny hardware.

EEMBC's CoreMark benchmark (Gal-On and Levy, 2012) has become the standard benchmark for MCU-class devices due to its ease of implementation and use of real algorithms. However, CoreMark profiles synthetic computational kernels, not full ML inference programs, and does not accurately represent machine learning workloads.

EEMBC's MLMark benchmark (Torelli and Bangale, n.d.) addresses this by using actual ML inference workloads. However, the supported models are far too large for MCU-class devices—requiring gigabytes of memory—and are not representative of TinyML workloads. Additionally, while CoreMark supports power measurements through EEMBC's ULPMark-CM benchmark, MLMark does not include energy measurement, which is critical for TinyML evaluation.

MLPerf Inference (Reddi et al., 2019), a community-driven benchmarking effort for large-scale ML inference, has plans to add power measurements. However, much like MLMark, the current MLPerf inference benchmark precludes MCUs and other resource-constrained platforms due to a lack of small benchmarks and compatible implementations.

There is thus a clear and distinct need for a TinyML benchmark that combines ML inference workloads with power as a first-class measurement, and prescribes a methodology suited to the hardware heterogeneity of the TinyML ecosystem. MLPerf Tiny fills this gap.

---

## 4. The MLPerf Tiny Benchmark Suite

MLPerf Tiny v0.5 consists of four benchmarks, each targeting a specific use case and specifying a dataset, a model, and a minimum quality target. The benchmarks were selected to cover a representative range of TinyML application domains while keeping model sizes within MCU memory budgets. Table 1 summarizes the four benchmarks.

**Table 1: MLPerf Tiny v0.5 Inference Benchmarks**

| Use Case | Dataset (Input Size) | Model (TFLite Model Size) | Quality Target (Metric) |
|---|---|---|---|
| Keyword Spotting | Speech Commands (49×10) | DS-CNN (52.5 KB) | 90% (Top-1) |
| Visual Wake Words | VWW Dataset (96×96) | MobileNetV1 (325 KB) | 80% (Top-1) |
| Image Classification | CIFAR-10 (32×32) | ResNet (96 KB) | 85% (Top-1) |
| Anomaly Detection | ToyADMOS (5×128) | FC-AutoEncoder (270 KB) | 0.85 (AUC) |

Each benchmark has a reference implementation that includes training scripts, pre-trained models, and C code. The reference implementations run the reference models in the TFLite format using TensorFlow Lite for Microcontrollers (TFLM) (David et al., 2020) on the NUCLEO-L4R5ZI board, a 32-bit ARM Cortex-M4-based microcontroller development board. A known-good snapshot of the TFLM runtime is used to ensure stability, and the reference implementation is built using a bare-metal MBED project with the GCC-ARM toolchain.

### 4.1 Keyword Spotting

**Motivation.** Recognition of specific words and brief phrases—known as keyword spotting (KWS)—is one of the primary use cases for ultra-low-power ML. Wake-word detection, a specific case of KWS (e.g., "Hey Siri," "OK Google"), requires continuous operation and therefore low power consumption: a 100 mA current drain would deplete a typical phone battery in one day from this task alone. Command-phrase recognition (e.g., "volume up," "turn left") provides a simple and natural interface to embedded devices. Both cases require low latency and low power and must typically run on small, low-cost devices.

**Dataset.** The benchmark uses the Speech Commands v2 dataset (Warden, 2018), a collection of 105,829 utterances collected from 2,618 speakers with a variety of accents, freely available under the Creative Commons BY license. The dataset contains 30 words plus background noise and is divided into training, validation, and test subsets such that any individual speaker appears in only one subset. Following typical usage, 10 words are used as target classes, while the background noise is combined with the remaining 20 words to form an "unknown" class; together with a "silence" class, this results in 12 output classes. This design exercises both command-phrase systems (multiple target words) and wake-word systems (open-set background noise rejection).

**Model.** The benchmark uses the small depthwise-separable CNN (DS-CNN) described in Zhang et al. (2017). With 38,600 parameters, this model fits within the available memory of most microcontrollers while achieving 92.2% accuracy in the authors' experiments. The model utilizes standard depthwise-separable convolution layers that can be expected of most neural network hardware. The TFLite model occupies 52.5 KB. Feature extraction (conversion of raw audio to a log-mel spectrogram representation, specifically a 49×10 feature map) is excluded from the measurement window and pre-computed; three choices of pre-computed features are provided for the open division.

**Quality Target.** The quantized reference model achieves 91.6% accuracy on the full test set and 91.7% on a 1,000-utterance subset used for on-device evaluation. The quality target is set to 90% Top-1 accuracy, allowing for slight variations in quantization strategies.

### 4.2 Visual Wake Words

**Motivation.** Tiny image processing models are increasingly widespread for simple image classification tasks. The Visual Wake Words (VWW) task—detecting whether at least one person is present in an image—is directly relevant to smart doorbell and occupancy applications. The task was first formalized as a challenge by Chowdhery et al. (2019), who also provided a reference network that fits on most 32-bit embedded microcontrollers.

**Dataset.** The benchmark uses the MSCOCO 2014 dataset (Lin et al., 2014), preprocessed to focus on images containing at least one person occupying more than 2.5% of the source image area. Images are resized to 96×96 for model training.

**Model.** The model is a MobileNetV1 (Howard et al., 2017) with an alpha (width multiplier) of 0.25 and two output classes (person and no person). The width multiplier scales all channel widths by a factor of 0.25, dramatically reducing model size at the cost of some accuracy. The TFLite model occupies 325 KB. The model reaches approximately 86% accuracy on the preprocessed MSCOCO 2014 test dataset.

**Quality Target.** To accommodate changes in accuracy due to quantization and rounding differences between platforms, submissions to the closed category must reach at least 80% Top-1 accuracy on the same test dataset.

### 4.3 Image Classification

**Motivation.** Image classification on tiny devices is of broad cross-industry interest for manufacturing quality control, IoT devices, and autonomous agents. A compact vision system performing image classification at low cost and high efficiency provides a point of reference for scientific and industrial evaluation of new hardware platforms, algorithms, and development tools.

**Dataset.** The benchmark uses CIFAR-10 (Krizhevsky et al., 2009), a labeled subset of the 80 Million Tiny Images dataset (Torralba et al., 2008). The low resolution of the images (32×32×3 RGB) makes CIFAR-10 well suited for training tiny image classification models. CIFAR-10 consists of 60,000 images across 10 classes (airplanes, cars, birds, cats, deer, dogs, frogs, horses, ships, trucks), with 6,000 images per class. The dataset is divided into five training batches and one test batch of 10,000 images each. A significant body of prior TinyML research has used CIFAR-10 as a target dataset (Fedorov et al., 2019), so this choice creates a point of reference that relates future benchmark results to historical data.

**Model.** The model is a customized ResNet (He et al., 2016) designed to fit within MCU memory budgets. Compared to the standard ResNet, the custom variant uses three residual stacks rather than four, omits the pooling layer after the first convolution (preserving spatial resolution at the input's 32×32 size), and uses fewer convolutional filters with reduced stride dimensions. The TFLite model occupies 96 KB and fits on most 32-bit embedded microcontrollers. The model achieves 86.5% accuracy on a 200-image evaluation subset drawn from the CIFAR-10 test set.

**Quality Target.** The quality target is set to 85% Top-1 accuracy, accommodating minor differences in quantization and other optimizations.

### 4.4 Anomaly Detection

**Motivation.** Anomaly detection—separating normal samples from anomalous ones—has applications across many fields. Its unsupervised variant is of particular importance to industrial use cases such as early detection of machine anomalies, where failure types are many and failure events can be rare, meaning labeled anomalous data is often unavailable for training. This benchmark is distinctive in requiring unsupervised learning and an autoencoder (AE) architecture, which broadens the range of model types covered by the suite beyond the supervised classifiers used in the other three benchmarks.

**Dataset.** The benchmark uses the dataset from the DCASE 2020 challenge (Koizumi et al., 2020), which combines two publicly available sources: the ToyADMOS dataset (Koizumi et al., 2019) and the MIMII dataset (Purohit et al., 2019). The DCASE dataset contains audio data for six machine types (slide rail, fan, pump, valve, toy-car, toy-conveyor); the benchmark restricts evaluation to the toy-car machine type for simplicity. For training, normal sound samples of seven different toy-cars are provided, each having 1,000 samples mixing machine sound with environmental noise. The evaluation dataset is composed of normal and anomalous sounds from four different machines, totaling 248 samples.

**Model.** The benchmark uses a fully-connected (FC) autoencoder, the same architecture used as the reference implementation in DCASE 2020. The model has input and output sizes of 640. Both the encoder and decoder are composed of four 128-unit FC layers with batch normalization applied during training and ReLU activations; the bottleneck layer has size 8. The model is not applied directly to the 10-second raw audio. Instead, audio is pre-processed into a log-mel spectrogram with 128 frequency bands and a 32 ms frame size. The model is then applied repeatedly over a sliding window of five frames (producing the 5×128 = 640 input), and the mean squared error (MSE) of the reconstruction is averaged over the central 6.4-second portion of the spectrogram, yielding an overall anomaly score. The TFLite model occupies 270 KB.

**Quality Target.** Because the autoencoder outputs a continuous anomaly score that requires a threshold before a binary decision can be made, the area under the ROC curve (AUC-ROC) is used as the threshold-free evaluation metric. The FP32 reference model achieves an AUC of 0.88; after quantization, the AUC is 0.86. The quality target is set to AUC 0.85.

---

## 5. Benchmark Infrastructure and Run Rules

### 5.1 Modular Design

TinyML applications often require cross-stack optimization to meet their tight constraints. Hardware vendors may contribute a novel microarchitecture; software vendors may contribute an optimized inference compiler; algorithm researchers may contribute a more efficient model or quantization scheme. To allow any such contributor to demonstrate the competitive advantage of their specific contribution, MLPerf Tiny employs a modular approach to benchmark design.

Each benchmark in the suite has a reference implementation containing everything from training scripts to a reference hardware platform. This reference implementation can be modified by a submitter wishing to show the performance of a single hardware or software component, rather than requiring end-to-end replacement of the entire stack. The modular components of a reference implementation include the dataset, training procedure, model architecture, post-training quantization, inference framework, and hardware platform.

### 5.2 Closed and Open Divisions

MLPerf Tiny provides two submission divisions that balance comparability with flexibility.

The **closed division** enables direct comparison of systems. Submitters must use the same models, datasets, and quality targets as the reference implementation. The closed division permits post-training quantization (PTQ) using provided calibration datasets, but prohibits any retraining or weight replacement. This controlled setting allows the inference stack of one system to be compared directly to another.

The **open division** is designed to broaden the scope of the benchmark and allow submitters to demonstrate improvements at any stage of the ML pipeline. Submitters may change the model, training scripts, and dataset. Open division submissions still use the same test dataset to evaluate accuracy but are not required to meet the accuracy threshold, allowing submitters to demonstrate tradeoffs between accuracy, latency, and energy consumption. Each open division submission must document its deviations from the reference implementation.

### 5.3 Measurement Procedure and Framework

TinyML platforms typically cannot run a complete benchmark locally—they lack file I/O, standard input/output, and interactivity. A benchmark framework running on a host PC therefore controls and measures the DUT. This framework is based on EEMBC's software development platform and supports two hardware configurations:

1. **Latency/accuracy configuration**: A direct serial-port connection between the host PC and the DUT. The host downloads input stimuli, loads them into the DUT's input tensor, triggers inference, and collects results.

2. **Energy configuration**: An expanded setup that interposes an electrical-isolation proxy (IO Manager, deployed as an Arduino UNO with custom firmware) and an energy monitor (EMON) between the host and the DUT. The IO Manager provides resilient serial connection state across power cycling and handles voltage-domain conversion. The energy monitor supplies and measures energy consumption. Three EMON devices are supported: the STMicroelectronics LPM01A, the Jetperch Joulescope JS110, and the Keysight N6705. Only the power delivered to the core is measured; power consumed by level-shifters and other framework components is excluded. Only one power supply is allowed to power the core, preventing the use of batteries, supercapacitors, or energy harvesters that could defeat the measurement.

The three measurement procedures are defined as follows:

- **Latency**: Perform the following five times—download an input stimulus, load the input tensor, run inference for a minimum of 10 seconds and 10 iterations, measure inferences per second (IPS). Report the median IPS of the five runs as the score.

- **Accuracy**: Perform a single inference on the entire set of validation inputs and collect output tensor probabilities. Compute Top-1 accuracy (for classification tasks) or AUC (for anomaly detection). Each model has a minimum accuracy that must be met for the score to be considered valid.

- **Energy**: Identical to the latency procedure, but in addition to measuring IPS, the total energy used during the timing window is measured and reported as micro-Joules per inference. The median of five measurements is reported.

The DUT firmware implements a standardized API consisting of five functions: a timestamp function, UART transmit/receive for communication with the host, a function for loading the input tensor, a function for performing a single inference, and a function for printing prediction results. This minimal API facilitates porting to new platforms while maintaining standardization.

---

## 6. Evaluation: First Round of Submissions (v0.5)

### 6.1 Submission Structure

The MLPerf Tiny benchmark suite accepts results from submitting organizations twice a year. Submitting organizations implement the benchmarks on their hardware/software stack and submit results and implementations by the deadline. All results are transparently peer-reviewed by the group of submitters and a review committee to ensure they conform to the rules. The first round of submissions (v0.5, June 2021) is summarized in Table 2.

**Table 2: Summary of MLPerf Tiny v0.5 Submissions**

| Division | Dataset | Training | Model | Numerics | Framework | Hardware | Demonstrates |
|---|---|---|---|---|---|---|---|
| Closed | ✓ | ✓ | ✓ | INT-8 PTQ | TensorFlow Lite Micro | ARM MCU | Baseline performance on the reference platform |
| Closed | ✓ | ✓ | ✓ | INT-8 PTQ | TensorFlow Lite Micro | RISC-V MCU | Performance of a RISC-V microcontroller customized for neural network inference |
| Closed | ✓ | ✓ | ✓ | FP-32 & INT-8 PTQ | LEIP Framework | RasPi 4 | Capabilities of a software-only optimization toolchain agnostic of the hardware |
| Closed | ✓ | ✓ | ✓ | INT-8 PTQ | Syntiant TDK | Neural Network Accelerator | Ultra-low power hardware efficiency for running deep neural networks |
| Open | ✓ | ✗ | ✗ | Int-6/8 QAT | HLS4ML | FPGA | Rapid end-to-end development of ML accelerators on reconfigurable fabrics |

*A ✓ indicates no modification was made from the reference; ✗ indicates a modification. PTQ = post-training quantization; QAT = quantization-aware training.*

### 6.2 Insights from v0.5 Results

The v0.5 submissions were diverse and demonstrated the desired flexibility of the benchmark suite. There were submissions to both the open and closed divisions, as well as from hardware vendors, software vendors, and academic research groups. Each submitter had a specific element they wished to demonstrate, and the modular design of the benchmark suite accommodated this diverse set of goals.

The submissions reveal several general trends in TinyML. The most common numerical format is 8-bit integer (INT-8) for inference, which offers a performance boost with little impact on model accuracy. ML frameworks range from open-source interpreters (TFLite Micro) to hardware-specific inference compilers, indicating that there is still a trade-off between optimization and portability. Results were collected on a wide variety of hardware platforms, including ARM MCUs, a RISC-V MCU, a dedicated neural network accelerator, and an FPGA, with power consumption ranging from microwatts to watts across the platform spectrum.

More specifically, the submission using a software-only optimization toolchain (LEIP Framework) demonstrated that hardware-agnostic software can provide meaningful optimization across different platforms, running on a Raspberry Pi 4 in the closed division. A hardware vendor used the benchmark to demonstrate outstanding performance on a dedicated neural network accelerator enabled by a novel microarchitecture that avoids wait-states and maintains high computational efficiency. An academic research team demonstrated the capabilities of a RISC-V-based AI microcontroller, showcasing the potential of the open RISC-V instruction set architecture (Asanovic and Patterson, 2014) for TinyML inference.

A multi-disciplinary team of scientists and engineers used the open division to showcase the "hls4ml" (high-level synthesis for ML) workflow—an open-source pipeline designed to enable researchers and engineers to co-design optimized neural networks for efficient dataflow architectures on reconfigurable hardware (FPGAs). Originally developed for ultra-fast sub-microsecond ML inference for the Large Hadron Collider, this workflow demonstrates the breadth of hardware that the open division can accommodate, as well as the value of quantization-aware training (QAT) for variable-precision deployments.

One notable observation is that, despite a general trend in AI towards data-centric design, none of the submissions in the first round modified the training dataset. While this may shift in future versions, TinyML design in its early phase is still largely focused on models, frameworks, and hardware optimization.

---

## 7. Impact and Societal Considerations

The MLPerf Tiny benchmarks have already acted as a standard set of tasks for TinyML research (Banbury et al., 2021) and have been made into public projects on a TinyML development platform (Moreau, n.d.). The benchmark suite standardizes a nascent field and enables future progress through competition and comparability across the entire TinyML stack.

TinyML has the potential to democratize AI by removing the barrier of expensive hardware and can preserve privacy by keeping user data on the device that captures it—a significant advantage over cloud-connected approaches that must transmit sensitive audio or image data. The efficiency of TinyML also enables always-on intelligence in battery-powered devices that would otherwise be impractical.

At the same time, the technology could be misused to more efficiently track and monitor individuals without their consent, since always-on sensor processing is difficult to detect. Furthermore, because the devices themselves are inexpensive, widespread TinyML deployment could lead to increased electronic waste. By establishing a collaborative community, MLPerf Tiny can aid in the creation of standards for the responsible deployment of TinyML and can help mitigate the potential negative impacts of the technology.

---

## 8. Limitations and Future Work

### 8.1 Benchmark Evolution and Long-term Stability

MLPerf Tiny will continue to evolve to reflect the needs of the community, including new benchmarks targeting application domains such as wearables, medical devices, and environmental monitoring. However, this creates a tension: adding and modifying benchmarks over time disrupts the long-term comparability needed to track historical progress in the field. To address this, a subset of benchmarks is planned to remain stable over the long term, providing a multi-year perspective on the evolution of TinyML performance. The open-source nature of the benchmark aids long-term reproducibility, and the MLCommons non-profit organization provides institutional support.

### 8.2 Streaming Inputs and Pre-processing

Time-domain tasks such as keyword spotting and anomaly detection typically involve continuously streaming inputs. Information from previous time steps can be exploited to improve the performance-efficiency tradeoff. However, limited bandwidth between the host PC and the DUT makes it difficult to recreate a true streaming scenario without introducing data-transfer delays that distort measurements.

The treatment of pre-processing also introduces subtleties. Excluding feature extraction from the measurement window while allowing submitter-selected variations in feature extraction creates a degenerate case where an entire model up to the penultimate layer could be defined as "feature extraction." Rigidly defining feature extraction precludes joint optimization over feature and model architecture, which can be critical in constrained systems. Including feature extraction in the benchmark window introduces its own distortions: for one second of audio, there would be one inference cycle but 40 feature extraction cycles, over-emphasizing the cost of feature extraction. Future versions of the benchmark aim to widen scope to include pre-processing while addressing these subtleties.

### 8.3 Coverage of Model Architectures and Layer Types

The closed division of the current benchmark suite includes models based mainly on fully-connected and convolutional layers in well-known architectures (DS-CNN, MobileNetV1, ResNet, FC-Autoencoder). While this provides a reasonable baseline that can be implemented on most hardware platforms, future benchmarks may include reference implementations using additional architectures such as recurrent neural networks (RNNs), which are relevant for temporal tasks. The open division already allows deviation from these architectures, permitting more experimental submissions.

---

## 9. Conclusion

The field of TinyML is poised to drive enormous growth within the IoT hardware and software industry. However, measuring the performance of these rapidly proliferating systems and comparing them in a meaningful way presents a considerable challenge: the complexity and dynamicity of the field—spanning diverse hardware, software, and application domains—obscures the measurement of progress and makes embedded ML system design and deployment difficult.

To enable more systematic development while fostering innovation, MLPerf Tiny provides a fair, replicable, and robust method of evaluating TinyML systems across three dimensions simultaneously: energy, latency, and accuracy. Developed as a collaboration between more than 50 organizations in academia and industry, the benchmark suite captures the full stack of TinyML optimization through its modular design and two-division submission structure. The four benchmarks—keyword spotting, visual wake words, image classification, and anomaly detection—cover a representative range of always-on, low-power application domains.

The first round of v0.5 submissions demonstrated the benchmark's ability to accommodate submissions from hardware vendors, software vendors, and academic researchers, each with distinct goals and optimization targets. Future submission rounds will track the evolution of TinyML hardware and software over time, providing the community with the longitudinal perspective needed to measure and celebrate genuine progress.

The benchmark suite and reference implementations are open-source and available at https://github.com/mlcommons/tiny.

---

## References

Asanovic, K. and Patterson, D. A. Instruction sets should be free: The case for risc-v. *EECS Department, University of California, Berkeley*, Tech. Rep. UCB/EECS-2014-146, 2014.

Banbury, C., Zhou, C., Fedorov, I., Matas, R., Thakker, U., Gope, D., Janapa Reddi, V., Mattina, M., and Whatmough, P. Micronets: Neural network architectures for deploying tinyml applications on commodity microcontrollers. *Proceedings of Machine Learning and Systems*, 3, 2021.

Bouguera, T., Diouris, J.-F., Chaillout, J.-J., Jaouadi, R., and Andrieux, G. Energy consumption model for sensor nodes based on lora and lorawan. *Sensors*, 18(7):2104, 2018.

Brainchip. Ai at the edge, Apr 2021.

Chowdhery, A., Warden, P., Shlens, J., Howard, A., and Rhodes, R. Visual wake words dataset. *CoRR*, abs/1906.05721, 2019.

David, R., Duke, J., Jain, A., Reddi, V. J., Jeffries, N., Li, J., Kreeger, N., Nappier, I., Natraj, M., Regev, S., et al. Tensorflow lite micro: Embedded machine learning on tinyml systems. *arXiv preprint arXiv:2010.08678*, 2020.

Fedorov, I., Adams, R. P., Mattina, M., and Whatmough, P. Sparse: Sparse architecture search for cnns on resource-constrained microcontrollers. In *Advances in Neural Information Processing Systems 32*, pages 4978–4990. Curran Associates, Inc., 2019.

Gal-On, S. and Levy, M. Exploring coremark a benchmark maximizing simplicity and efficacy. *The Embedded Microprocessor Benchmark Consortium*, 2012.

He, K., Zhang, X., Ren, S., and Sun, J. Deep residual learning for image recognition. In *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, pages 770–778, 2016.

Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., and Adam, H. Mobilenets: Efficient convolutional neural networks for mobile vision applications. *arXiv preprint arXiv:1704.04861*, 2017.

Koizumi, Y., Saito, S., Uematsu, H., Harada, N., and Imoto, K. Toyadmos: A dataset of miniature-machine operating sounds for anomalous sound detection. In *2019 IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA)*, pages 313–317. IEEE, 2019.

Koizumi, Y., Kawaguchi, Y., Imoto, K., Nakamura, T., Nikaido, Y., Tanabe, R., Purohit, H., Suefusa, K., Endo, T., Yasuda, M., and Harada, N. Description and discussion on DCASE2020 challenge task2: Unsupervised anomalous sound detection for machine condition monitoring. *arXiv e-prints: 2006.05822*, June 2020.

Krizhevsky, A., Nair, V., and Hinton, G. Cifar-10 (canadian institute for advanced research). 2009.

Lin, T.-Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollár, P., and Zitnick, C. L. Microsoft coco: Common objects in context. In *European Conference on Computer Vision*, pages 740–755. Springer, 2014.

Moreau, L. Tinymlperf - speech commands. Edge Impulse Studio, n.d.

Purohit, H., Tanabe, R., Ichige, K., Endo, T., Nikaido, Y., Suefusa, K., and Kawaguchi, Y. Mimii dataset: Sound dataset for malfunctioning industrial machine investigation and inspection. *arXiv preprint arXiv:1909.09347*, 2019.

Reddi, V. J., Cheng, C., Kanter, D., Mattson, P., Schmuelling, G., Wu, C.-J., Anderson, B., Breughe, M., Charlebois, M., Chou, W., et al. Mlperf inference benchmark. 2019.

Torelli, P. and Bangale, M. Measuring inference performance of machine-learning frameworks on edge-class devices with the mlmark benchmark. EEMBC, n.d.

Torralba, A., Fergus, R., and Freeman, W. T. 80 million tiny images: A large data set for nonparametric object and scene recognition. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 30(11):1958–1970, 2008.

Warden, P. Speech commands: A dataset for limited-vocabulary speech recognition. *arXiv preprint arXiv:1804.03209*, 2018.

Zhang, Y., Suda, N., Lai, L., and Chandra, V. Hello edge: Keyword spotting on microcontrollers. *arXiv preprint arXiv:1711.07128*, 2017.
