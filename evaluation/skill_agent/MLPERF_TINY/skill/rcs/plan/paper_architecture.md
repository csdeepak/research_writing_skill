# Paper Architecture — MLPerf Tiny

Story pattern: Method-first (Problem → Method → Results/Validation → Discussion)
Section order: Abstract → Introduction → Background/Challenges → Related Work → Benchmark Design → Measurement Methodology → Submission Results → Limitations → Conclusion

---

## Abstract
- Nodes: N01, N07, N12, N15
- Reader question: What is this paper about and why does it matter?
- Claims: C001, C002, C003, C006
- Density: CORE

## §1 Introduction
- Para 1: Hook — TinyML and its promise (N01, N02)
- Para 2: Why progress is stalled — no standard benchmark (N04)
- Para 3: This paper's contribution — MLPerf Tiny overview (N07, N15)
- Reader questions: What is TinyML? Why does it need its own benchmark?
- Claims: C001, C002
- Terms to introduce: TinyML, microcontroller (MCU), inference, energy efficiency

## §2 Background and Challenges
- Para 1: TinyML system characteristics — scale, power, always-on (N02, N08)
- Para 2: Challenge: Low Power (N01)
- Para 3: Challenge: Limited Memory (N01)
- Para 4: Challenge: Hardware Heterogeneity (N01)
- Para 5: Challenge: Software Heterogeneity (N01)
- Reader questions: What makes measuring these systems hard?
- Terms: MCU, Device Under Test (DUT), ML deployment stack

## §3 Related Work
- Para 1: CoreMark (N03)
- Para 2: MLMark (N03)
- Para 3: MLPerf inference (N03, N04)
- Claims: C001
- Reader question: What was missing from prior benchmarks?

## §4 Benchmark Design
- §4.1 Overview (N07, N09, N10): four benchmarks, modular design
- §4.2 Keyword Spotting (N10): DS-CNN, Speech Commands v2, 90% accuracy target
- §4.3 Visual Wake Words (N10): MobileNetV1, MSCOCO 2014, 80% target
- §4.4 Image Classification (N10): ResNetv1, CIFAR-10, 85% target
- §4.5 Anomaly Detection (N10): FC autoencoder, DCASE2020, 0.85 AUC target
- Claims: C003, C004, C005
- Terms: top-1 accuracy, AUC-ROC, post-training quantization (PTQ), depthwise-separable CNN, autoencoder

## §5 Measurement Methodology
- §5.1 Closed and Open Divisions (N09)
- §5.2 Harness Architecture (N11): host PC, DUT, energy monitor
- §5.3 Measurement Protocol (N11): latency, energy, accuracy procedures
- Claims: C002
- Terms: inferences per second (IPS), µJ/inference, Device Under Test (DUT)
- Table: Measurement protocol summary

## §6 Submissions and Assessment
- §6.1 v0.5 Submission Round (N12): five submissions, Table summary
- §6.2 Cross-platform Insights (N13, N14): INT-8 dominance, power range, no dataset modification
- Claims: C006, C007, C008, C009, C010
- Table: v0.5 submission summary

## §7 Limitations
- Para 1: Pre-processing and streaming exclusion (L004, N16)
- Para 2: Single-round evidence and architecture coverage (L003, L005, N16)
- Para 3: Future directions (N18)
- Claims: L003, L004, L005

## §8 Conclusion
- Nodes: N15, N17
- Claims: C002, C003, C006, C008
- Summary of contribution and path forward
