---
template: packet_audience_objective
field: objective
---

# Paper Objective

**Contribution type:** Benchmark / Dataset paper

**Central contribution:** MLPerf Tiny is the first community-developed, industry-standard benchmark suite that jointly measures accuracy, latency (inferences per second), and energy efficiency (µJ/inference) for ML inference on ultra-low-power microcontroller-class hardware. It comprises four benchmarks, a two-division submission structure, and a standardized measurement harness.

**Research question answered:** Can a benchmark suite be designed that fairly evaluates TinyML systems on accuracy, latency, and energy, accommodates hardware and software heterogeneity, and enables diverse submitters to demonstrate the value of their contribution?

**Key evidence:**
- Benchmark design: four tasks with specified datasets, models, quality targets (Table 1 in paper)
- Measurement protocol: latency (median IPS of 5 trials), energy (median µJ/inference of 5 trials), accuracy (single pass over evaluation set)
- v0.5 submission round: 5 submissions across ARM MCU, RISC-V, NN accelerator, Raspberry Pi 4, FPGA
- Reference model results: DS-CNN 92.2% / quantized 91.6%, AD autoencoder AUC 0.88 / quantized 0.86

**Scope limitations:**
- v0.5 is a single submission round (5 participants)
- Pre-processing and streaming excluded from measurement
- Closed division covers FC and CNN architectures only

**What the paper does NOT claim:**
- Does not show that MLPerf Tiny is complete or final
- Does not compare hardware platforms against each other (that is the purpose of results rounds)
- Does not claim causal explanations for submission patterns (e.g., INT-8 dominance)
