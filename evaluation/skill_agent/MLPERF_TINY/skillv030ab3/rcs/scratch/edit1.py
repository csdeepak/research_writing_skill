p = ".rcs/drafts/v001/paper.md"
s = open(p, encoding="utf-8").read()
R = [
 ("a general processor benchmark that does not represent ML inference,", "a microcontroller benchmark that does not represent ML inference,"),
 ("The devices are microcontrollers (small, low-power processors with very little memory) and related hardware such as digital signal processors and tiny neural-network accelerators {C019}.",
  "The devices are microcontrollers (MCUs: small, low-power processors with very little memory) and related hardware such as digital signal processors and tiny neural-network accelerators {C019}."),
 ("The authors conclude that a TinyML benchmark must fit small models, and make power a first-class citizen, which is the specification MLPerf Tiny is built to. This account",
  "The authors conclude that there is a clear and distinct need for a TinyML benchmark that suits ML workloads and makes power a first-class citizen. This account"),
 ("This requirement drives the modular design and the two divisions in Section 4.3.", "The modular design and the two divisions in Section 4.3 are the authors' response to this requirement."),
 ("**Table 1.** The four benchmarks of the v0.5 suite. Sizes are the TFLite model size. Values as listed by the authors.",
  "**Table 1.** The four benchmarks of the v0.5 suite. Sizes are the TFLite model size. AUC is the area under the ROC curve. Values as listed by the authors."),
 ("and two output classes, 325KB as a TFLM model {C004}.", "and two output classes; as a model for TensorFlow Lite for Microcontrollers (TFLM), the runtime of the reference implementations, it is 325KB {C004}."),
 ("on the NUCLEO-L4R5ZI board, using a known-good", "on the NUCLEO-L4R5ZI board, using a known-good"),
 ("TensorFlow Lite for Microcontrollers (TFLM) (David et al., 2020)", "TFLM (David et al., 2020)"),
 ("quantized value of 0.86 {C029}.", "quantized value of 0.86 {C029}."),
 ("For anomaly detection the threshold of AUC 0.85 was set from the floating-point (fp32) reference value of 0.88",
  "For anomaly detection the threshold of AUC 0.85 was set from the 32-bit floating-point (fp32) reference value of 0.88"),
 ("The results answer RQ1 and RQ2 with the reference numbers, and RQ3 with the submission round.", "The results answer RQ1 with the reference numbers, RQ2 with the reference-board statement, and RQ3 with the submission round."),
 ("These values answer RQ1 for the targets: a correct quantized implementation of each reference model clears the target by a margin that is small for the quantized anomaly detection model and larger for visual wake words {C035}.",
  "For RQ1 these values show that each target sits below what its reference model reaches, by a small margin for the quantized anomaly detection model and a larger one for visual wake words {C035}."),
 ("One organization used the benchmark to demonstrate that its SDK developer tools are hardware agnostic, another a neural-network accelerator, an academic institute the potential of RISC-V-based microcontrollers, and a team its hls4ml open-source workflow for designing neural networks for efficient dataflow architectures {C015}.",
  "One organization used the benchmark to demonstrate that its software development kit (SDK) tools are hardware agnostic, another a neural-network accelerator, an academic institute the potential of microcontrollers based on RISC-V, a free, open standard instruction set architecture (Asanovic et al., 2014), and a team its hls4ml (high-level synthesis for ML) open-source workflow for designing neural networks for efficient dataflow architectures {C015}."),
 ("Hardware included microcontrollers, accelerators and FPGAs, and the reconfigurable hardware can use variable-precision models for increased performance.",
  "Hardware included microcontrollers, accelerators and reconfigurable hardware (FPGAs), and the reconfigurable hardware can use variable-precision models for increased performance."),
 ("**What the design reflects.** The design follows the challenges in Section 2. Heterogeneous hardware and software stacks are met by a modular reference implementation, and by a framework that asks little of the device: five functions to port. The two divisions split the problem into comparing stacks under fixed models (closed) and showing gains from changing models or data (open) {C002} {C027} {C028}.",
  "**How the design maps to the challenges.** Read against Section 2, heterogeneous hardware and software stacks are met by a modular reference implementation and by a framework that asks a device for five functions, in keeping with the authors' aim of minimizing porting effort. The two divisions separate comparing stacks under fixed models (closed) from showing gains from changing models or data (open). This mapping is our reading of the authors' stated reasons {C002} {C027} {C028} {C008}."),
]
for a, b in R:
    assert a in s, a[:60]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
