# Paper Spine

1. **Problem.** Engineers and researchers building machine learning for microcontroller-class, ultra-low-power devices (TinyML) cannot compare accuracy, latency and energy across very different hardware and software stacks {C009}.
2. **Gap.** In the authors' account, CoreMark, MLMark and MLPerf inference each miss what TinyML needs (small ML workloads, power measurement, MCU compatibility) {C009, L008}.
3. **Question.** Can one benchmark specification give comparable results across heterogeneous TinyML systems while letting submitters show improvements at any layer, and did its first round show this? {C001, C007, C010}
4. **Approach.** Four tasks with reference models, inference-only measurement, closed and open divisions, and a runner framework with optional energy measurement {C001, C006, C007, C008}.
5. **Key finding.** The first round (June 2021) drew closed and open submissions on ARM and RISC-V MCUs, a Raspberry Pi 4, a neural-network accelerator and an FPGA, and reference models sit 0.01 AUC to about 6 points above their quality targets {C010, C005}.
6. **Meaning.** The authors attribute the breadth of submissions to the modular design; the evidence is consistent with that but does not isolate it {C014}.
7. **Main limit.** Latency and energy values are absent from the available text, evidence is one round, and feature extraction and streaming are outside the measurement {L001, L003, L005}.
