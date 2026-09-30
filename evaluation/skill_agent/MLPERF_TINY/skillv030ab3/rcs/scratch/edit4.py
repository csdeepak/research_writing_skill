p = ".rcs/drafts/v001/paper.md"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep("Existing benchmarks each miss part of this need, as the authors describe them. CoreMark, the standard benchmark for microcontroller-class devices (Gal-On et al., 2012), does not represent ML inference workloads. MLMark uses real ML workloads, but its models are far too large for these devices and it cannot measure power. The MLPerf inference benchmark (Reddi et al., 2019) precludes microcontrollers because it lacks small benchmarks and compatible implementations {C003}. Section 3 sets these out by dimension.",
    "As the authors describe them, three existing benchmarks each miss part of this need: CoreMark (Gal-On et al., 2012), MLMark and the MLPerf inference benchmark (Reddi et al., 2019). None combines ML workloads small enough for microcontrollers with power measurement {C003}. Section 3 sets these out by dimension.")
rep("TinyML devices can consume drastically different amounts of power, which makes it hard to keep measurement accurate across the range, and the scope of a power measurement is hard to fix when data paths and pre-processing vary between devices.",
    "TinyML devices can consume very different amounts of power, which makes it hard to keep measurement accurate across the range, and the scope of a power measurement is hard to fix when data paths and pre-processing vary.")
rep("so models sized for other ML benchmarks do not fit, benchmark overhead can make the suite itself too big, and several levels of quantization and precision need representing {C002}.",
    "so models sized for other ML benchmarks do not fit, benchmark overhead can make the suite too big, and several levels of quantization and precision need representing {C002}.")
rep("from general-purpose microcontrollers to novel architectures, so", "from general-purpose microcontrollers to newer architectures, so")
rep("needing gigabytes of memory and having significant runtimes", "needing gigabytes of memory and having long runtimes")
rep("MLPerf Tiny targets model inference. It does not include pre-processing or post-processing in the measurement window, because",
    "MLPerf Tiny targets model inference. Quality is measured by Top-1 accuracy or, for anomaly detection, by the area under the receiver operating characteristic (ROC) curve (AUC). The measurement window does not include pre-processing or post-processing, because")
rep(" AUC is the area under the ROC curve. Values as listed", " Values as listed")
rep("The metric is the area under the receiver operating characteristic (ROC) curve (AUC), which needs no threshold, and the evaluation set", "The metric is AUC, which needs no threshold, and the evaluation set")
rep("preprocessed so that positive images contain a person occupying more than 2.5% of the source image and resized to 96x96. The model",
    "preprocessed so that positive images contain a person occupying more than 2.5% of the source image, and resized to 96x96 {C004}. The model")
rep("Anomaly detection is unsupervised: the model sees only normal sounds in training and must score how anomalous a test sound is. ", "Anomaly detection is unsupervised: training uses only normal sounds, and the model scores how anomalous a test sound is. ")
rep(" Its input and output size is 640 (five frames of 128 log-mel spectrogram bands, a time-frequency representation of audio); encoder and decoder each have four 128-unit FC layers, and the bottleneck has size 8. The anomaly score is the reconstruction error averaged over the central 6.4 seconds of a 10-second clip {C031} {C004}.",
    " Its input and output size is 640 (five frames of 128 log-mel spectrogram bands); encoder and decoder each have four 128-unit FC layers, and the bottleneck has size 8. The anomaly score is the reconstruction error averaged over the central 6.4 seconds of a 10-second clip {C031} {C004}.")
rep("Quantization stores weights at lower precision; the closed division allows post-training quantization (PTQ), which converts a trained model without retraining, and quantization-aware training (QAT) appears among the open-division entries in Section 5.3. For anomaly",
    "The closed division allows post-training quantization (PTQ), which converts a trained model to lower precision without retraining; quantization-aware training (QAT), which trains with low precision in mind, appears among the open-division entries in Section 5.3 {C029}. For anomaly")
rep("shows 91.6% on the full test set and 91.7% on the random 1000-utterance subset used for on-device evaluation, against a requirement of 90%; the model achieved 92.2% in the authors' own experiments. Both quantized numbers sit above the requirement {C012}.",
    "shows 91.6% on the full test set and 91.7% on the random 1000-utterance subset used for on-device evaluation, both above the requirement of 90%; the model achieved 92.2% in the authors' own experiments {C012}.")
rep("The energy configuration adds an isolating IO Manager (an Arduino UNO with custom firmware) and an energy monitor; the runner supports three monitors (the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705).",
    "The energy configuration adds an isolating input-output manager (an Arduino UNO board with custom firmware) and an energy monitor; the runner supports three monitors (the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705).")
rep("The latency and energy values sit in the authors' Figure 5, which is not recoverable from the materials this presentation draws on, so no numbers are given and no chart is drawn {C014} {L005}. The statement is therefore a qualitative report at the authors' strength.",
    "The latency and energy values sit in the authors' Figure 5, which is not recoverable from the materials this presentation draws on, so no numbers are given and no chart is drawn {C014} {L005}.")
rep("The authors envision a subset of benchmarks kept long-term stable. The suite described here is therefore a snapshot of an evolving benchmark, and its four tasks are not final coverage {L001} {C022}.",
    "The authors envision a subset of benchmarks kept long-term stable. The suite described here is therefore a snapshot of an evolving benchmark, not final coverage {L001} {C022}.")
rep("The limited bandwidth between the test runner and the DUT makes it difficult to recreate a streaming scenario without adding delays from data transfer. Latency and energy for these tasks therefore do not reflect the gains that streaming could allow {L002} {C008} {C030} {C031}.",
    "The limited bandwidth between the test runner and the DUT makes it difficult to recreate a streaming scenario without adding delays from data transfer, so latency and energy for these tasks do not reflect the gains that streaming could allow {L002} {C008} {C030} {C031}.")
rep("The authors aim to widen the scope to pre-processing in future versions. Until then, measured latency and energy can misstate whole-application cost {L003} {C026} {C030}.",
    "The authors aim to include pre-processing in future versions. Until then, measured latency and energy can misstate whole-application cost {L003} {C026} {C030}.")
rep("The following are our own, not the authors', and each bounds specific claims.", "The following caveats are ours, not the authors', and each bounds specific claims.")
open(p, "w", encoding="utf-8").write(s)
