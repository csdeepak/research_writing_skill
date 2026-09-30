import re
p = ".rcs/drafts/v001/paper.md"
s = open(p, encoding="utf-8").read()

a = s.index("The authors name five challenges.")
b = s.index("## 3. Related work")
new2 = ("The authors name five challenges. On power, devices consume very different amounts of power, and the scope of a power measurement is hard to fix when data paths and pre-processing vary. On memory, TinyML systems work with resources about two orders of magnitude smaller than those of a smartphone, so models sized for other ML benchmarks do not fit, and several levels of quantization and precision need representing. On hardware heterogeneity, the system under test may lack standard features such as a system clock or a debug interface, and a standard interface with little porting effort is a key difficulty {C002}.\n\n"
        "On software heterogeneity, systems are often tightly coupled to a vendor's own inference stack, so any restriction on the stack could give unrepresentative results; the authors say they must balance optimality with portability, and comparability with representativeness. The fifth challenge is the cross-product: there is diversity at every level of the stack, and a user can improve the system at any layer, so a benchmark should let such users show the benefit of their solution in a controlled setting {C002}. The modular design and the two divisions in Section 4.3 are the authors' response to this requirement {C027}.\n\n")
s = s[:a] + new2 + s[b:]

a = s.index("The framework has two hardware configurations.")
b = s.index("## 5. Results")
new44 = ("The framework has two hardware configurations, provided because the energy setup is more complex and energy scores may not be wanted. The latency and accuracy configuration connects the host computer to the DUT through a serial port. The energy configuration adds an isolating input-output manager (an Arduino UNO board with custom firmware) and an energy monitor; the runner supports three monitors (the STMicroelectronics LPM01A, the Jetperch Joulescope JS110 and the Keysight N6705). Level-shifter power is excluded from the energy score because it is a framework cost, not a DUT cost, and only one power supply may power the core, so that no other energy source can defeat the measurement. A host runner gives a consistent interface, standardizes execution, and downloads the many input files that a platform with under a megabyte of flash memory cannot hold. On the device, thin firmware implements five functions: a timestamp of at least one millisecond resolution, serial communication, loading the input tensor, a single inference, and printing the results {C009} {C034}.\n\n")
s = s[:a] + new44 + s[b:]

old = "The repository README lists releases v0.5 (Jun 16, 2021), v0.7 (April 6, 2022), v1.0 (Nov 9, 2022) and v1.1 (Jun 27, 2023), and expects the deadline of the next round, v1.2, on March 15, 2024 (dates not yet finalized) {C019}."
assert old in s
s = s.replace(old, "The repository README lists releases from v0.5 (Jun 16, 2021) to v1.1 (Jun 27, 2023) and expects the next round, v1.2, to have a deadline of March 15, 2024 (dates not yet finalized) {C019}.")
old = "The round shows what entries were made. It does not show accuracy, latency or energy values for them, because none appear in the project materials {L008}. The trends come from five table rows in a single round {L007}."
assert old in s
s = s.replace(old, "The round shows what entries were made, not their accuracy, latency or energy, because no such values appear in the project materials {L008}. The trends come from five table rows in a single round {L007}.")
old = "This reading is consistent with the mix of divisions, hardware and software vendors in Table 3, and it rests on five entries in one round, without submission measurements, and without a comparison against a design that is not modular {L007} {L008}."
assert old in s
s = s.replace(old, "This reading is consistent with the mix of divisions and vendors in Table 3; it rests on five entries in one round, with no submission measurements and no comparison against a design that is not modular {L007} {L008}.")
open(p, "w", encoding="utf-8").write(s)
