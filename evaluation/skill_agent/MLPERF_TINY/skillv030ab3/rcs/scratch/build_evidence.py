import json
P = "project/paper.txt"
R = "project/README_1.md"
items = []


def add(kind, summary, anchor, notes="", value=None, conditions=None, strength="hard", path=P, quantity=None, status="ok"):
    e = {"id": "E%03d" % (len(items) + 1), "kind": kind, "summary": summary,
         "locator": {"path": path, "anchor": anchor}, "strength": strength, "status": status}
    if value is not None:
        e["value"] = value
    if conditions is not None:
        e["conditions"] = conditions
    if notes:
        e["notes"] = notes
    if quantity:
        e["quantity"] = quantity
    items.append(e)
    return e["id"]


# ---------------- suite-level facts
add("method_detail", "The suite has four benchmarks: keyword spotting, visual wake words, image classification, anomaly detection.",
    "line 10 (abstract, last sentence)", 'Quote: "The suite features four benchmarks: keyword spotting, visual wake words, image classification, and anomaly detection."',
    value={"n_benchmarks": 4})  # E001
add("observation", "The suite is described as a collaborative effort of more than 50 organizations from industry and academia; the four benchmarks were selected by more than 50 organizations.",
    "lines 10 and 18", 'Quote: "collaborative effort of more than 50 organizations from industry and academia"; "a set of four standard benchmarks, selected by more than 50 organizations in academia and industry".',
    value={"organizations": "more than 50"}, quantity="num_organizations")  # E002
add("method_detail", "The suite measures accuracy, latency and energy of ML inference; the reference implementations include training scripts, pre-trained models and C code, and are open source.",
    "lines 10, 18, 36", 'Quote: "MLPerf Tiny measures the accuracy, latency, and energy of machine learning inference"; "each benchmark has a reference implementation that includes training scripts, pre-trained models, and C code implementations".')  # E003

# ---------------- Table 1 rows
add("dataset", "Table 1 row, keyword spotting: Speech Commands dataset, input size 49x10, DS-CNN model (TFLite size 52.5 KB), quality target 90% (Top-1).",
    "lines 39-50 (Table 1, damaged extraction; column order preserved)",
    "Table 1 extraction lists columns in order: Use Case (KWS, VWW, IC, AD); Dataset (Input Size); Model (TFLite Model Size); Quality Target (Metric). Row alignment follows the order of the lists; the per-task text in section 4 confirms the target values 80%, 85%, 90%, AUC 0.85 and the sizes 325 KB and 96 KB.",
    value={"task": "Keyword Spotting", "dataset": "Speech Commands", "input_size": "49x10", "model": "DS-CNN", "tflite_size": "52.5 KB", "quality_target": "90% (Top-1)"},
    quantity="table1_kws")  # E004
add("dataset", "Table 1 row, visual wake words: VWW dataset, input size 96x96, MobileNetV1 (325 KB), quality target 80% (Top-1).",
    "lines 39-50 (Table 1)", "Text section 4.1 confirms MobileNetV1, 325KB and the 80% closed-division target.",
    value={"task": "Visual Wake Words", "dataset": "VWW Dataset", "input_size": "96x96", "model": "MobileNetV1", "tflite_size": "325 KB", "quality_target": "80% (Top-1)"},
    quantity="table1_vww")  # E005
add("dataset", "Table 1 row, image classification: CIFAR10, input size 32x32, ResNet (96 KB), quality target 85% (Top-1).",
    "lines 39-50 (Table 1)", "Text section 4.2 confirms 96KB and 85% top-1.",
    value={"task": "Image Classification", "dataset": "CIFAR10", "input_size": "32x32", "model": "ResNet", "tflite_size": "96 KB", "quality_target": "85% (Top-1)"},
    quantity="table1_ic")  # E006
add("dataset", "Table 1 row, anomaly detection: ToyADMOS, input size 5*128, FC-AutoEncoder (270 KB), quality target .85 (AUC).",
    "lines 39-50 (Table 1)", "Text section 4.4 gives the model input size as 640 (five frames of 128 bands) and the AUC 0.85 threshold. The 270 KB size appears only in Table 1.",
    value={"task": "Anomaly Detection", "dataset": "ToyADMOS", "input_size": "5*128", "model": "FC-AutoEncoder", "tflite_size": "270 KB", "quality_target": ".85 (AUC)"},
    quantity="table1_ad")  # E007

# ---------------- VWW
add("dataset", "Visual wake words: MSCOCO 2014 is used for training, validation and test; images contain at least one person occupying more than 2.5% of the source image; resized to 96x96; MobileNetV1 with alpha 0.25 and two output classes (person, no person); TFLM model 325KB.",
    "lines 53-55 (section 4.1)", 'Quote: "preprocessed to train on image which contain at least one person occupying more than 2.5% of the source image. Images are also resized to 96x96"; "alpha of 0.25 and two output classes (person and no person). The TFLM model is 325KB in size."',
    value={"train_val_test": "MSCOCO 2014", "min_person_area": "2.5%", "image_size": "96x96", "alpha": 0.25, "classes": 2, "model_size": "325KB"})  # E008
add("result", "VWW reference model reaches about 86% accuracy across the preprocessed MSCOCO 2014 test dataset; closed-division submissions should reach at least 80% accuracy.",
    "line 56 (section 4.1, Quality Target)", 'Quote: "the model reaches about 86% accuracy across the preprocessed MSCOCO 2014 test dataset"; "submissions to the closed category should reach at least 80% accuracy across the same dataset."',
    value={"metric": "accuracy", "reference": "about 86%", "quality_target": "80%"},
    conditions="preprocessed MSCOCO 2014 test dataset; based on validation and training accuracy per the authors", quantity="vww_reference_accuracy")  # E009

# ---------------- IC
add("dataset", "Image classification: CIFAR-10 has 60000 32x32x3 RGB images with 6000 images per class, 10 classes, five training batches and one testing batch of 10000 images each; the model is a customized ResNetv1 with three residual stacks instead of four, no pooling after the first convolutional layer, fewer filters and lower strides; TFLite model 96KB.",
    "lines 59-60 (section 4.2)", 'Quote: "60000 32x32x3 RGB images, with 6000 images per class"; "three compared to four"; "The TFLite model for IC is 96KB in size".',
    value={"images": 60000, "per_class": 6000, "classes": 10, "batches": "five training batches and one testing batch, each with 10000 images", "residual_stacks": "three (official ResNet: four)", "model_size": "96KB"})  # E010
add("result", "IC reference model reaches 86.5% accuracy across 200 test images selected from the CIFAR-10 test set; quality target set to 85% top-1 accuracy.",
    "lines 61-64 (section 4.2, Quality Target)", 'Quote: "A set of 200 images from the CIFAR-10 test set are selected"; "The model reaches 86.5% accuracy" ... "across the 200 testing raw images."; "we set the quality target to 85% top-1 accuracy."',
    value={"metric": "top-1 accuracy", "reference": "86.5%", "quality_target": "85%", "n_images": 200},
    conditions="200 images of the CIFAR-10 test set, evaluated with the benchmark framework runner", quantity="ic_reference_accuracy")  # E011

# ---------------- KWS
add("dataset", "Keyword spotting data: Speech Commands v2, 105,829 utterances from 2,618 speakers, 30 words plus background noises, split so that each speaker appears in one subset; 10 words used, the remaining 20 words combined with background noise as an open-set 'unknown' class; with 'silence' this gives 12 output classes.",
    "line 67 (section 4.3)", 'Quote: "a collection of 105,829 utterances collected from 2,618 speakers"; "results in 12 output classes".',
    value={"utterances": 105829, "speakers": 2618, "words": 30, "words_used": 10, "output_classes": 12})  # E012
add("method_detail", "Keyword spotting closed-division model: small depthwise-separable CNN of Zhang et al. with 38.6K parameters, achieving accuracy of 92.2% in the authors' experiments; feature extraction is excluded from the measurement and three choices of pre-computed features are given for the open division.",
    "line 68 (section 4.3, Model)", 'Quote: "with 38.6K parameters, it fits within the available memory of most microcontrollers ... while achieving accuracy of 92.2% in our experiments"; "we opted to exclude feature extraction from the measurement and provide three choices of pre-computed features for the open division".',
    value={"parameters": "38.6K", "accuracy": "92.2%", "feature_choices_open_division": 3}, quantity="kws_model_accuracy_authors_experiments")  # E013
add("result", "KWS quantized reference model: 91.6% accuracy on the full test set and 91.7% on a random 1000-utterance subset used for on-device evaluation; accuracy requirement set to 90%.",
    "line 69 (section 4.3, Quality Target)", 'Quote: "The quantized reference model demonstrated 91.6% accuracy on the full test set and 91.7% on the 1000-utterance subset."; "we set an accuracy requirement of 90%."',
    value={"metric": "accuracy", "full_test_set": "91.6%", "subset_1000": "91.7%", "requirement": "90%"},
    conditions="quantized reference model; 1000 utterances randomly selected from the speech commands for device evaluation", quantity="kws_quantized_reference_accuracy")  # E014

# ---------------- AD
add("dataset", "Anomaly detection data: DCASE2020 challenge data (itself a combination of ToyADMOS and MIMII); six machine types exist, only Toy-car is used; normal training samples of seven different toy-cars, 1000 samples each, mixing machine sound with environmental noise.",
    "line 72 (section 4.4, Dataset)", 'Quote: "we choose to use the Toy-car machine type only"; "normal sound samples of seven different toy-cars are provided, each having 1000 samples".',
    value={"machine_types_available": 6, "used": "Toy-car", "toy_cars": 7, "samples_per_car": 1000})  # E015
add("method_detail", "Anomaly detection model: fully-connected autoencoder with input and output size 640; encoder and decoder each made of four 128-unit FC layers (BatchNorm during training, ReLU), bottleneck of size 8; input is a log-mel-spectrogram with 128 bands and 32 ms frame size, applied over a sliding window of five frames; the MSE reconstruction error is averaged over the central 6.4 second part of the spectrogram of a 10 second clip to give an anomaly score.",
    "lines 77 (section 4.4, Model)", 'Quote: "The model has input and output sizes of 640."; "bottleneck layer is of size 8"; "averaged over the central 6.4 second part of the spectrogram".',
    value={"input": 640, "fc_layers_each_side": 4, "units": 128, "bottleneck": 8, "mel_bands": 128, "frame_ms": 32, "window_frames": 5, "audio_seconds": 10, "scored_seconds": 6.4})  # E016
add("result", "AD reference model: on an evaluation set of normal and anomalous sounds from four different machines totalling 248 samples, the fp32 model reaches an AUC of 0.88 and the quantized model 0.86; the benchmark threshold is set at AUC 0.85.",
    "line 77 (section 4.4, Quality Target)", 'Quote: "totalling 248 samples. On this set, the fp32 version of the reference model achieves an AUC of 0.88 while the AUC after quantization is 0.86."; "we\'ve set the threshold for the benchmark to AUC 0.85."',
    value={"metric": "AUC-ROC", "fp32": 0.88, "quantized": 0.86, "threshold": 0.85, "n_samples": 248, "machines": 4},
    conditions="evaluation set from four different machines", quantity="ad_reference_auc")  # E017

# ---------------- reference stack, divisions, modular, measurement, framework
add("method_detail", "The reference implementations run the reference models in TFLite format using TFLite for Microcontrollers (TFLM) on the NUCLEO-L4R5ZI board; a known-good snapshot of the TFLM runtime is used; the build is a bare-metal MBED project with the GCC-ARM toolchain; code is open source.",
    "line 36 (section 4)", 'Quote: "run the reference models in the TFLite format using TFLite for Microcontrollers (TFLM) [7] on the NUCLEO-L4R5ZI board."')  # E018
add("method_detail", "Closed division: same models, datasets and quality targets as the reference; post-training quantization with provided calibration datasets is allowed, retraining or weight replacement is prohibited. Open division: submitters may change model, training scripts and dataset, use the same test dataset for accuracy, need not meet the accuracy threshold, and must document deviations from the reference.",
    "lines 86-88 (section 5.2)", 'Quote: "prohibits any retraining or weight replacement"; "is not required to meet the accuracy threshold".')  # E019
add("method_detail", "Modular design: each benchmark has a reference implementation covering training scripts to a reference hardware platform; a submitter can modify components to show the performance of a single hardware or software component; components in green can be modified in either division, orange ones only in the open division (Figure 2).",
    "lines 76, 84, 86 (section 5.1-5.2, Figure 2 caption)", 'Quote: "it can be modified by a submitter wishing to show the performance of a single hardware or software component".')  # E020
add("method_detail", "Latency procedure: perform five times: download an input stimulus, load the input tensor, run inference for a minimum of 10 seconds and 10 iterations, measure inferences per second (IPS); report the median IPS of the five runs as the score.",
    "line 94 and line 262", 'Quote: "run inference for a minimum of 10 seconds and 10 iterations, measure the inferences per second (IPS); report the median IPS of the five runs as the score."',
    value={"repeats": 5, "min_seconds": 10, "min_iterations": 10, "score": "median IPS"})  # E021
add("method_detail", "Accuracy procedure: a single inference on the entire set of validation inputs; compute Top-1 percent and the AUC; each model has a minimum accuracy that must be met for the score to be valid.",
    "line 95 and line 263", 'Quote: "Each model has a minimum accuracy that must be met for the score to be valid."')  # E022
add("method_detail", "Energy procedure: identical to latency, plus measurement of the total energy used in the timing window to compute micro-Joules per inference; the median of five measurements is used.",
    "line 96 and line 264", 'Quote: "compute micro-Joules per inference. The same method of taking the median of five measurements is used."')  # E023
add("method_detail", "Framework: a host PC running a runner GUI, the device under test (DUT) with a thin shim of firmware; two configurations (latency/accuracy over a serial port; energy adding an IO Manager, deployed as an Arduino UNO, and an energy monitor); three energy monitor drivers (STMicroelectronics LPM01A, Jetperch Joulescope JS110, Keysight N6705); level-shifter power is excluded from the energy score; only one power supply may power the core; timestamp resolution at least one millisecond in performance mode; the DUT implements five API functions (timestamp, UART, load input tensor, single inference, print results).",
    "lines 236-252 (Appendix A.1-A.2)", 'Quote: "it must supply one channel for the DUT and the other for the level shifters"; "the power used by level-shifters is not included in the total energy score because it is a cost associated with the framework and not the DUT"; "only one power supply is allowed to power the core".',
    value={"energy_monitors": ["STMicroelectronics LPM01A", "Jetperch Joulescope JS110", "Keysight N6705"], "timestamp_resolution": "at least one millisecond (1 kHz)", "api_functions": 5})  # E024
add("observation", "Reference implementation results (Figure 5, NUCLEO-L4R5ZI): the authors state the four benchmarks cover a wide scope in terms of latency and energy and each reference meets the minimum accuracy. The plotted latency and energy values are in a figure not recoverable from the extracted text.",
    "line 97 and line 91 (Figure 5 caption)", 'Quote: "The four benchmarks cover a wide scope in terms of latency and energy and each reference meets the minimum accuracy."',
    strength="soft", status="incomplete")  # E025

# ---------------- submissions
add("result", "Table 2 summarizes the v0.5 round of submissions in five rows: closed division ARM MCU with TensorFlow Lite Micro and INT-8 PTQ (baseline performance results on the reference platform); closed RISC-V MCU (performance of a RISC-V microcontroller customized for neural network inference); closed RasPi 4 with the LEIP Framework, FP-32 and INT-8 PTQ (capabilities of a software-only optimization toolchain that is agnostic of the hardware); closed neural network accelerator with the Syntiant TDK, INT-8 PTQ (ultra-low power hardware efficiency); open division FPGA with QKeras, Int-6/8 QAT and HLS4ML (rapid end-to-end development of ML accelerators on reconfigurable fabrics).",
    "lines 104-184 (Table 2, damaged extraction)", "Check-mark and X columns (dataset, training, model modifications) are not legible in the extraction; only the row contents above are used. Caption: 'The X indicates no modification was made from the reference. The check mark indicates a modification. PTQ refers to post training quantization and QAT refers to quantization aware training.'",
    value={"rows": 5, "closed": 4, "open": 1})  # E026
add("observation", "The first round of submissions took place in June 2021; submissions are accepted twice a year; results are peer-reviewed by the group of submitters and a review committee; each submission is public on GitHub with instructions to reproduce.",
    "lines 100-101, 186 (section 6.1)", 'Quote: "accepts results from submitting organizations twice a year"; "transparently peerreviewed by the group of submitters and a review committee".')  # E027
add("observation", "The v0.5 submissions were diverse: open and closed divisions, from hardware and software vendors; each submitter had a specific element to demonstrate and the suite accommodated this due to its modular design.",
    "line 188 (section 6.2)", 'Quote: "the benchmark suite was able to accommodate this diverse set of goals due to its modular design."')  # E028
add("observation", "Trends the authors read from the submissions: 8-bit integer was the most common numerical format because it offers a performance boost with little impact to model accuracy; frameworks ranged from open source interpreters (TFLite Micro) to hardware specific inference compilers, indicating a trade-off between optimization and portability; hardware included MCUs, accelerators and FPGAs; reconfigurable hardware (FPGA) can use variable precision models for increased performance; power consumption ranged from µWatts to Watts.",
    "line 189 (section 6.2)", 'Quote: "the most common numerical format is 8-bit integer for inference as it offers a performance boost with little impact to the model accuracy"; "The power consumption of these platforms ranged from µWatts to Watts."')  # E029
add("observation", "Four submitter demonstrations are described: a software SDK claimed hardware agnostic and easy to use; a hardware vendor's neural network accelerator with a novel microarchitecture and optimized datapath; an academic research institute showing AI compute capability of RISC-V based AI micro-controllers; and a multi-disciplinary team's 'hls4ml' open-source workflow.",
    "line 190 (section 6.2)", "These are the submitters' own aims as reported by the authors; the paper does not report the corresponding latency or energy numbers in the text.")  # E030
add("observation", "None of the submissions in the first round modified the training dataset.",
    "line 191 (section 6.2)", 'Quote: "none of the submissions in the first round modified the training dataset."')  # E031

# ---------------- README
add("external_fact", "README version table: v0.5 released Jun 16, 2021; v0.7 April 6, 2022; v1.0 Nov 9, 2022; v1.1 Jun 27, 2023; the deadline of the next round v1.2 is expected to be March 15, 2024 with publication in April (dates not yet finalized); results of previous versions are on the MLCommons web page.",
    "README lines 18-27", "Project-status information from the repository README; it postdates the paper's v0.5 scope.", path=R, strength="soft",
    value={"versions": {"v0.5": "Jun 16, 2021", "v0.7": "April 6, 2022", "v1.0": "Nov 9, 2022", "v1.1": "Jun 27, 2023"}, "v1.2_deadline": "March 15, 2024"})  # E032
add("external_fact", "README describes embedded devices as microcontrollers, DSPs and tiny NN accelerators that typically run at between 10MHz and 250MHz and can perform inference using less than 50mW of power; the reference benchmarks use TFLM and submitters may use the software stack that works best on their hardware.",
    "README lines 3-14", 'Quote: "typically run at between 10MHz and 250MHz, and can perform inference using less then 50mW of power".', path=R, strength="soft",
    value={"clock": "10MHz to 250MHz", "power": "less than 50mW"}, quantity="readme_device_power_ceiling")  # E033
add("observation", "The paper states the benchmarks have already acted as a standard set of tasks for TinyML research and have been made into public projects on a TinyML development platform.",
    "line 195 (section 7)", 'Quote: "The benchmarks have already acted as a standard set of tasks for TinyML research [4]".')  # E034

# ---------------- challenges (observations by the authors)
add("observation", "Challenge named by the authors, low power: devices can consume drastically different amounts of power, which makes maintaining accuracy across the range of devices difficult; the scope of the power measurement is hard to determine when data paths and pre-processing vary between devices.",
    "line 21 (section 2)", 'Quote: "TinyML devices can consume drastically different amounts of power"')  # E035
add("observation", "Challenge named by the authors, limited memory: TinyML systems cope with resources two orders of magnitude smaller than the few GBs of smartphones; traditional ML benchmarks use models with peak memory in the order of gigabytes; benchmark overhead can make the suite too big to fit; multiple levels of quantization and precision should be represented.",
    "line 22 (section 2)", 'Quote: "resources that are two orders of magnitude smaller"')  # E036
add("observation", "Challenge named by the authors, hardware heterogeneity: devices range from general-purpose MCUs to novel architectures, so the system under test may lack standard features such as a system clock or debug interface; a standard interface with minimal porting effort is a key challenge.",
    "lines 23-26 (section 2)", 'Quote: "creating a standard interface while minimizing porting effort is a key challenge"')  # E037
add("observation", "Challenge named by the authors, software heterogeneity: TinyML systems are often tightly coupled with their inference stack and users develop their own toolchains; any restriction on the inference stack could negatively impact performance and give unrepresentative results, so optimality must be balanced with portability, and comparability with representativeness.",
    "line 27 (section 2)", 'Quote: "we must balance optimality with portability, and comparability with representativeness"')  # E038
add("observation", "Challenge named by the authors, cross-product: there is diversity of options at every level of the TinyML stack (Figure 1), each layer affects performance, and software users can improve the system at any layer; a benchmark should let users show the benefits of their solution in a controlled setting.",
    "line 28 (section 2)", 'Quote: "A TinyML benchmark should enable these users to demonstrate the performance benefits of their solution in a controlled setting."')  # E039

# ---------------- related work
add("observation", "Related work as characterized by the authors: EEMBC's CoreMark is the standard benchmark for MCU-class devices because of its ease of implementation and use of real algorithms, but does not profile full programs nor accurately represent ML inference workloads.",
    "line 31 (section 3)", 'Quote: "CoreMark does not profile full programs, nor does it accurately represent machine learning inference workloads."')  # E040
add("observation", "Related work as characterized by the authors: EEMBC's MLMark uses actual ML inference workloads, but its models are far too large for MCU-class devices (memory in GBs, significant runtimes) and it does not support power measurements, unlike CoreMark with the ULPMark-CM benchmark.",
    "line 32 (section 3)", 'Quote: "the supported models are far too large for MCU-class devices"; "MLMark does not, which is critical for a TinyML benchmark."')  # E041
add("observation", "Related work as characterized by the authors: the MLPerf inference benchmark precludes MCUs and other resource-constrained platforms due to a lack of small benchmarks and compatible implementations, and had plans to add power measurements.",
    "line 33 (section 3)", 'Quote: "precludes MCUs and other resource-constrained platforms due to a lack of small benchmarks and compatible implementations"')  # E042

# ---------------- rationale_stated (author motivation and design reasons)
add("rationale_stated", "Motivation: continued progress in TinyML is limited by the lack of a widely accepted and easily reproducible benchmark for these systems.",
    "line 10 (abstract)", 'Quote: "continued progress is limited by the lack of a widely accepted and easily reproducible benchmark for these systems."')  # E043
add("rationale_stated", "Motivation: because the deployment stack needs co-optimization at every layer, direct comparison of solutions is challenging and the impact of individual optimizations is difficult to measure, so a fair and reliable method of comparison is needed.",
    "lines 12-17 (section 1)", 'Quote: "a fair and reliable method of comparison is needed."')  # E044
add("rationale_stated", "Design reason: the suite measures latency, energy and accuracy in order to capture the tradeoffs inherent to TinyML; power is a first-class citizen.",
    "lines 18, 33 (sections 1, 3)", 'Quote: "In order to capture the tradeoffs inherent to TinyML, the benchmark suite measures latency, energy, and accuracy."')  # E045
add("rationale_stated", "Design reason: MLPerf Tiny targets model inference and does not include pre- or post-processing in the measurement window, because application-level benchmarks can obscure the target of the benchmark behind other stages of the pipeline while low-level benchmarks gloss critical elements such as memory bandwidth or model-level optimizations.",
    "line 35 (section 4)", 'Quote: "application level benchmarks can obscure the target of the benchmark behind other stages of the application pipeline. MLPerf Tiny specifically targets model inference"')  # E046
add("rationale_stated", "Design reason: a modular design lets users demonstrate the competitive advantage of their specific contribution, targeting specific components (such as quantization) or offering end-to-end solutions.",
    "line 84 (section 5.1)", 'Quote: "to enable users to demonstrate the competitive advantage of their specific contribution, we employ a modular approach to benchmark design."')  # E047
add("rationale_stated", "Design reason: two divisions (closed and open) allow the benchmark to balance comparability and flexibility.",
    "line 86 (section 5.2)", 'Quote: "This two division design allows the benchmark to balance comparability and flexibility."')  # E048
add("rationale_stated", "Design reason: quality targets are set slightly below the reference accuracy to accommodate differences due to quantization and rounding (VWW: 86% reference, 80% target; IC: 86.5%, 85%; KWS: 91.6%, 90%); for AD the threshold of AUC 0.85 is based on the fp32 (0.88) and quantized (0.86) reference numbers.",
    "lines 56, 64, 69, 77", 'Quote: "In order to accommodate changes in accuracy due to quantization and rounding differences between platforms"; "To allow for slight variations in quantization strategies, we set an accuracy requirement of 90%."')  # E049
add("rationale_stated", "Design reason, keyword spotting model: the small depthwise-separable CNN was chosen because with 38.6K parameters it fits within the available memory of most microcontrollers and similarly-scaled devices, while achieving 92.2% accuracy, and it uses standard layers expected of most neural network hardware.",
    "line 68 (section 4.3)", 'Quote: "We chose this model because with 38.6K parameters, it fits within the available memory of most microcontrollers"')  # E050
add("rationale_stated", "Design reason, keyword spotting features: feature extraction is excluded from the measurement because it is typically a small fraction of the overall compute cost, so the impact on the measurements is minor; the three pre-selected feature choices are the features most commonly used in KWS systems.",
    "line 68 (section 4.3)", 'Quote: "Feature extraction is typically a small fraction of the overall compute cost, so the impact on the measurements is minor."')  # E051
add("rationale_stated", "Design reasons, anomaly detection: only the Toy-car machine type is used because benchmarking would not benefit from the complexity of separate models per machine type; the DCASE2020 reference autoencoder was chosen because it is the reference for a large part of the audio anomaly detection literature and adds a model type based entirely on FC layers; AUC-ROC is used because it is parameterless while other metrics require selecting a threshold; the evaluation set spans four different machines to ensure models have generalization characteristics.",
    "lines 72-77 (section 4.4)", 'Quote: "Benchmarking would not benefit from this type of complexity"; "the parameterless AUC-ROC ... fits better"; "To ensure models have generalization characteristics, we have selected an evaluation dataset composed of normal and anomalous sounds from four different machines".')  # E052
add("rationale_stated", "Design reasons, image classification: CIFAR-10 was chosen because its low resolution makes it the most suitable source for tiny image classification models and because much prior TinyML work has used it, creating a point of reference to relate future results to historical data points; the model has fewer residual stacks and no pooling after the first convolution because of the low resolution of the input.",
    "lines 58-60 (section 4.2)", 'Quote: "by continuing this trend, we create a point of reference in the benchmark suite that can be used to relate future results to historical data points."')  # E053
add("rationale_stated", "Design reason, visual wake words: the task is directly relevant to smart doorbell and occupancy applications, and the reference network from the Visual Wakewords challenge fits on most 32-bit embedded microcontrollers.",
    "line 53 (section 4.1)", 'Quote: "This task is directly relevant to smart doorbell and occupancy applications"')  # E054
add("rationale_stated", "Design reasons, framework: a known-good snapshot of TFLM is used to ensure stability; two framework configurations are provided because the energy configuration is more complex and energy scores may not be desired; level-shifter power is excluded because it is a framework cost not a DUT cost, and only one power supply may power the core so that no other energy source can be used to defeat the measurement; a host runner is needed to provide a consistent interface, standardize execution and download the large number of input files because the typical target platform has less than a megabyte of flash memory.",
    "lines 36, 238-240, 255-257", 'Quote: "energy configuration is a more complex setup, and energy scores may not be desired"; "the typical target platform has less than a megabyte of flash memory".')  # E055

# ---------------- limitation_noted (author-stated)
add("limitation_noted", "Author-stated limitation, new benchmarks and long-term stability: MLPerf Tiny will keep evolving with new benchmarks for new application domains (wearables, medical devices, environmental monitoring), while a benchmark must also be stable over time to track historical progress; the authors envision a subset of benchmarks kept long-term stable.",
    "line 197 (section 8, 'New benchmarks & Long-term stability')", 'Quote: "such a benchmark serves both as the comparison of state-of-the-art and for tracking historical progress. This latter goal requires benchmarks to be stable over time"; "we also envision a subset of benchmarks to be kept long-term stable".')  # E056
add("limitation_noted", "Author-stated limitation, streaming inputs: time-domain tasks such as keyword spotting and anomaly detection typically involve continuously streaming inputs, and information from previous time steps can improve the performance-efficiency tradeoff; limited bandwidth between the test runner (e.g. a PC) and the DUT makes it difficult to recreate a streaming scenario without adding delays incurred by data transfer.",
    "line 198 (section 8, 'Streaming inputs & Pre-processing')", 'Quote: "limited bandwidth between the test runner (running on e.g. a PC) and the DUT makes it difficult to recreate a streaming scenario without adding delays incurred by data transfer."')  # E057
add("limitation_noted", "Author-stated limitation, pre-processing choice: whether to include pre-processing in the measured benchmark can have distorting effects on the results; excluding feature extraction from measurement while allowing submitter-selected variations creates a possible degenerate case where an entire model up to the penultimate layer is defined as feature extraction.",
    "line 198 (section 8)", 'Quote: "The choice of whether to include pre-processing in the measured benchmark can also have distorting effects on the results."')  # E058
add("limitation_noted", "Author-stated limitation, rigidly defined feature extraction: it precludes joint optimization over feature and model architecture that can be critical in the constrained systems targeted by the suite; the authors also state the pre-selected feature choices somewhat limit innovation in the overall KWS system.",
    "lines 68 and 198", 'Quote: "Rigidly defined feature extraction precludes joint optimization over feature and model architecture"; "the pre-selected feature choices somewhat limit innovation in the overall KWS system".')  # E059
add("limitation_noted", "Author-stated limitation, including feature extraction: including it brings its own complexities; operating on a single discrete audio input in a non-streaming benchmark, one second of audio would involve one inference cycle and 40 feature extraction cycles, over-emphasizing the cost of feature extraction. The authors aim to widen the scope to include pre-processing in future versions.",
    "line 198 (section 8)", 'Quote: "one second of audio would involve one inference cycle and 40 feature extraction cycles, over-emphasizing the cost of feature extraction."')  # E060
add("limitation_noted", "Author-stated limitation, coverage of layer types and model architectures: the closed division includes models based mainly on FC and CNN layers, allowing only open division submissions to deviate; future benchmarks may include reference implementations with additional architectures, e.g. RNNs.",
    "line 199 (section 8)", 'Quote: "The closed division of the current benchmark suite includes models based mainly on FC and CNN layers"')  # E061

# ---------------- impact statements
add("observation", "Impact section, stated by the authors: the benchmark will standardize the nascent field of TinyML and enable future progress through competition and comparability; TinyML has the potential to democratize AI and preserve privacy by keeping data on the device; the technology could be misused to more efficiently track and monitor unwilling individuals; because devices are inexpensive, TinyML can lead to increased electronic waste; by establishing a collaborative community MLPerf Tiny can aid the creation of standards for responsible deployment.",
    "line 195 (section 7)", 'Quote: "The benchmark will standardize the nascent field of TinyML and enable future progress through competition and comparability."; "By establishing a collaborative community, MLPerf Tiny can aid in the creation of standards for the responsible deployment of TinyML and mitigate the potential negative impacts of the technology."')  # E062
add("observation", "Context stated by the authors: TinyML achieves ML inference under a milliWatt; on-device near-sensor inference gives responsiveness and privacy while avoiding the wireless communication energy cost, which at this scale is far higher than that of compute.",
    "line 12 (section 1)", 'Quote: "achieves ML inference under a milliWatt"', quantity="tinyml_power_definition_paper")  # E063
add("observation", "The manuscript header states 'Preprint. Under review.' (arXiv v4, 24 Aug 2021); the benchmark suite and reference implementations are open source at the project GitHub repository.",
    "lines 1, 14, 201", "Publication status of the paper.")  # E064

add("observation", "Related work overall, as stated by the authors: there are a few ML related hardware benchmarks, but none that accurately represent the performance of TinyML workloads on tiny hardware; there is a clear and distinct need for a TinyML benchmark that caters to the unique needs of ML workloads, makes power a first-class citizen and prescribes a methodology that suits TinyML.",
    "lines 30, 33 (section 3)", 'Quote: "none that accurately represent the performance of TinyML workloads on tiny hardware"; "there is a clear and distinct need for a TinyML benchmark"')  # E065

doc = {"project_root": ".", "generated_at": "2026-09-29", "generated_by": "CORPUS_AGENT (performed by the author agent)", "items": items}
json.dump(doc, open(".rcs/evidence/research_evidence.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(len(items), "items")
