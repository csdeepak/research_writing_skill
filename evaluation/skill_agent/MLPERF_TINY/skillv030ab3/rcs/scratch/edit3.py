import re
p = ".rcs/drafts/v001/paper.md"
s = open(p, encoding="utf-8").read()


def rep(a, b, count=1):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, count)


# strong verbs / licensed wording
rep("so that users can demonstrate the competitive advantage of their specific contribution", "so that users can show the competitive advantage of their specific contribution")
rep("let such users demonstrate the benefit of their solution in a controlled setting {C002}. The modular design and the two divisions in Section 4.3 are the authors' response to this requirement.",
    "let such users show the benefit of their solution in a controlled setting {C002}. The modular design and the two divisions in Section 4.3 are the authors' response to this requirement {C027}.")
rep("and the evaluation set draws on four different machines so that models have generalization characteristics {C031}.",
    "and the evaluation set draws on four different machines, which the authors say is meant to give a broader test than a single machine would {C031}.")
# acronyms
rep("Machine-learning inference on very small", "Machine-learning (ML) inference on very small")
rep("The June 2021 round produced five submissions across microcontroller, RISC-V, single-board computer, accelerator and FPGA hardware {C015}",
    "The June 2021 round produced five submissions, on hardware from microcontrollers to accelerators and reconfigurable chips {C015}")
rep("microcontrollers (MCUs: small, low-power processors with very little memory)", "microcontrollers (small, low-power processors with very little memory)")
rep("ARM MCU | Baseline", "ARM microcontroller | Baseline")
rep("| RISC-V MCU | Performance", "| RISC-V microcontroller | Performance")
rep("The metric is the area under the ROC curve (AUC), which needs no threshold", "The metric is the area under the receiver operating characteristic (ROC) curve (AUC), which needs no threshold")
rep("The data are MSCOCO 2014 (Lin et al., 2014)", "The data are MSCOCO 2014 (Microsoft Common Objects in Context; Lin et al., 2014)")
rep("60000 32x32x3 RGB images", "60000 32x32x3 color images")
rep("Image classification uses CIFAR-10 (Krizhevsky et al., 2009)", "Image classification uses CIFAR-10 (Canadian Institute for Advanced Research; Krizhevsky et al., 2009)")
rep("The model is the small depthwise-separable CNN of Zhang et al. (2017)", "The model is the small depthwise-separable convolutional neural network (CNN) of Zhang et al. (2017)")
rep("additional model architectures such as RNNs {C022}", "additional model architectures such as recurrent neural networks {C022}")
rep("a host PC controls", "a host computer controls")
rep("connects the host PC to the DUT", "connects the host computer to the DUT")
# section names for rationale placement
rep("### 4.1 Four tasks, their datasets and models", "### 4.1 Design of the four tasks: data and models")
# orphan claims
rep("Hardware included microcontrollers, accelerators and reconfigurable hardware (FPGAs), and the reconfigurable hardware can use variable-precision models for increased performance.",
    "Hardware included microcontrollers, accelerators and reconfigurable hardware, which can use variable-precision models for increased performance {C016}.")
rep("Latency and energy for these tasks do not reflect the gains that streaming could allow {L002}", "Latency and energy for these tasks therefore do not reflect the gains that streaming could allow {L002}")
# result dumping: interpretive clauses
rep("Each closed-division submission must reach a quality target (Table 1). The authors set each target slightly below the reference accuracy, to accommodate differences due to quantization and rounding across platforms. ",
    "Each closed-division submission must reach a quality target (Table 1). The authors set each target slightly below the reference accuracy, to accommodate differences due to quantization and rounding across platforms {C029}. ")
rep("Section 5.1 gives the reference values and the resulting gaps.", "Section 5.1 gives the reference values and the resulting gaps, which show how much room the targets leave.")
rep("The visual wake words reference reaches about 86% accuracy against the 80% required of closed-division submissions {C010}.",
    "The visual wake words reference reaches about 86% accuracy against the 80% required of closed-division submissions, so it clears its target {C010}.")
rep("against a target of 85% {C011}.", "against a target of 85%, so its margin is small {C011}.")
rep("the model achieved 92.2% in the authors' own experiments {C012}.", "the model achieved 92.2% in the authors' own experiments. Both quantized numbers sit above the requirement {C012}.")
# conclusion tag
rep("the paper offers no submission measurements, and the authors say streaming, pre-processing and model-family coverage are not yet handled {L002} {L003} {L004} {L008}.",
    "the authors say streaming, pre-processing and model-family coverage are not yet handled {L002} {L003} {L004}, and the paper offers no submission measurements {C015}.")
# trims
s = re.sub(r"\*\*How the design maps to the challenges\.\*\*.*?\n\n", "", s, flags=re.S)
rep(" This account rests on the authors' characterization of three benchmarks; the paper does not report a comparison table and the cited works were not consulted for this presentation {C003}.",
    " This account rests on the authors' characterization of three benchmarks; the cited works were not consulted for this presentation {C003}.")
rep("The authors explain that the energy configuration is more complex and energy scores may not be wanted, hence two configurations. ", "The authors provide two configurations because the energy setup is more complex and energy scores may not be wanted. ")
rep("A host runner provides a consistent interface and standardizes execution, and it downloads the many input files that a platform with under a megabyte of flash memory cannot hold. ",
    "A host runner gives a consistent interface, standardizes execution, and downloads the many input files that a platform with under a megabyte of flash memory cannot hold. ")
open(p, "w", encoding="utf-8").write(s)
