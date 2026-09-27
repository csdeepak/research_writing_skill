# Reader Reconstruction Self-Test — v001

Q1 What is the problem? → No standard benchmark to compare TinyML systems on accuracy, latency, and energy. ✓
Q2 What is the gap? → Existing benchmarks (CoreMark, MLMark, MLPerf inference) exclude energy measurement, use oversized models, or are incompatible with MCU hardware. ✓
Q3 What does the paper ask? → Can one benchmark fairly evaluate TinyML across all three axes while accommodating hardware/software heterogeneity? ✓
Q4 What did the authors do? → Defined 4 benchmarks with modular closed/open divisions and a standardized host-DUT measurement harness. ✓
Q5 Why this design? → Explained per challenge: modular design lets each submitter show their value; closed division fixes the model for fair comparison; open allows innovation. ✓
Q6 What did they find? → v0.5 attracted 5 diverse submissions (ARM MCU, RISC-V, NN accelerator, SW toolchain, FPGA). INT-8 PTQ dominated. Power range: µW to W. ✓
Q7 What does it mean? → Modular design accommodates fundamentally different hardware/software stacks in one comparable round. ✓
Q8 What can the result NOT show? → Streaming/pre-processing excluded. Single round. Only FC+CNN architectures in closed division. ✓
Q9 What remains open? → Streaming inputs, pre-processing measurement, RNN architectures, new domains. ✓
Q10 Are all terms introduced before use? → TinyML (§1), MCU (§1), DUT (§5.2), PTQ (§5.1), QAT (§6.2), DS-CNN (§4.2), AUC-ROC (§4.5), IPS (§5.3). ✓
Q11 Do all numbers match evidence? → 92.2% (E009), 91.6%/91.7% (E010), ~86% (E013), 86.5% (E016), 0.88/0.86/0.85 (E020), 38.6K params (E008), 248 eval samples (E021), 5 submissions (E026). ✓
Q12 Can reader reconstruct the spine? → Problem (§1), Gap (§3), Approach (§4-5), Finding (§6), Meaning (§6.2), Limit (§7). ✓

All 12 pass. No mismatches found.
