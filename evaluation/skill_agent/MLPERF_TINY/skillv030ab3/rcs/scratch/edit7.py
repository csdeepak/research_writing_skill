p = ".rcs/drafts/v001/paper.md"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep("The paper's aim can be read as three questions. RQ1:", "The paper's aim can be read as three research questions (RQ1 to RQ3). RQ1:")
rep("It fixes a dataset, a small model and a quality target for each task {C004}, offers a strict closed division",
    "It fixes a dataset, a small model and a quality target for each task {C004}, supplies open-source reference implementations {C005}, offers a strict closed division")
rep("The data are MSCOCO 2014 (Microsoft Common Objects in Context; Lin et al., 2014)", "The data are the Microsoft Common Objects in Context (MSCOCO) 2014 dataset (Lin et al., 2014)")
rep("Image classification uses CIFAR-10 (Canadian Institute for Advanced Research; Krizhevsky et al., 2009)", "Image classification uses CIFAR-10 (named for the Canadian Institute for Advanced Research; Krizhevsky et al., 2009)")
rep("The data come from the DCASE2020 challenge (Koizumi et al., 2020), itself a combination of ToyADMOS (Koizumi et al., 2019) and MIMII (Purohit et al., 2019).",
    "The data come from the DCASE2020 anomalous-sound-detection challenge (Koizumi et al., 2020), itself a combination of two public sound datasets, ToyADMOS (Koizumi et al., 2019) and MIMII (Purohit et al., 2019).")
rep("The repository README lists releases from", "The project's repository description (its README file) lists releases from")
# move platform/framework names to an appendix
rep("The reference implementations run TFLite models with TFLM (David et al., 2020) on the NUCLEO-L4R5ZI board, using a known-good snapshot of the runtime for stability and a bare-metal MBED project built with the GCC-ARM toolchain {C005} {C034}.",
    "The reference implementations run TFLite models with TFLM (David et al., 2020) on the NUCLEO-L4R5ZI development board, using a known-good snapshot of the runtime for stability {C005} {C034}. Build details are in Appendix A.")
rep("The energy configuration adds an isolating input-output manager (an Arduino UNO board with custom firmware) and an energy monitor; the runner supports three monitors (the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705). Level-shifter",
    "The energy configuration adds an isolating input-output manager and an energy monitor (hardware details in Appendix A). Level-shifter")
app = """## Appendix A. Reference platform and framework details

This appendix holds reproducibility detail that the main text points to. It supports the reference-platform and framework descriptions in Sections 4.3 and 4.4.

The reference implementations are built as a bare-metal MBED project with the GCC-ARM toolchain and run on the NUCLEO-L4R5ZI board {C005}. In the energy configuration the input-output manager is deployed as an Arduino UNO with its own custom firmware. The runner contains three energy-monitor drivers: the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705 {C009}. Whichever monitor is used, it must supply one channel for the device and another for the level shifters, whose power is not counted in the energy score {C009} {C034}.

"""
rep("## References", app + "## References")
open(p, "w", encoding="utf-8").write(s)
