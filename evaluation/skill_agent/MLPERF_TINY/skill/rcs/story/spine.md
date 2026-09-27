# Paper Spine — MLPerf Tiny

**Line 1 — Problem**
Developers and researchers working on ultra-low-power machine learning for microcontrollers have no standard, widely accepted way to measure and compare the accuracy, latency, and energy of their systems. {C001}

**Line 2 — Gap**
Existing benchmarks either omit energy measurement, rely on models too large for microcontroller memory, or are incompatible with the hardware heterogeneity of this device class, making fair cross-system comparison impossible. {C001}

**Line 3 — Question**
Can a benchmark suite be designed that jointly evaluates TinyML systems on accuracy, latency, and energy; accommodates the extreme hardware and software heterogeneity of the field; and enables diverse submitters to demonstrate the value of their specific contribution in a fair, reproducible setting?

**Line 4 — Approach**
MLPerf Tiny defines four inference benchmarks spanning key embedded application domains, with a modular two-division structure (closed and open), a standardized host–device measurement harness, and complete reference implementations on an ARM microcontroller board. {C002} {C003}

**Line 5 — Key finding**
The benchmark successfully hosted its first submission round (v0.5, June 2021), drawing five diverse submissions across ARM MCU, RISC-V, neural network accelerator, software-only toolchain, and FPGA platforms, demonstrating that the modular design accommodates fundamentally different hardware and software stacks within a single comparable round. {C006} {C008}

**Line 6 — Meaning**
MLPerf Tiny provides the first community-developed, industry-standard point of comparison for TinyML systems, enabling systematic tracking of progress across the hardware–software stack as the field evolves. {C008}

**Line 7 — Main limit**
The v0.5 evidence is a single submission round with five participants; reference models cover only FC and CNN architectures; and pre-processing and streaming inputs are excluded from the measurement window. {L003} {L004} {L005}
