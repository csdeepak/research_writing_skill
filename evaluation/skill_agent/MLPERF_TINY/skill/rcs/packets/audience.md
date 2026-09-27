---
template: packet_audience_objective
field: audience
---

# Audience Profile

**Mode:** B — Adjacent researcher

**Description:** Machine-learning researchers from subfields other than embedded/edge ML. They hold a PhD-level or equivalent understanding of supervised and unsupervised learning, standard neural network architectures (CNNs, ResNets, MobileNets, autoencoders), model quantization concepts, and evaluation metrics (top-1 accuracy, AUC-ROC). They are familiar with standard benchmarks such as ImageNet, COCO, and CIFAR-10. They are NOT familiar with:

- The TinyML subfield or why sub-milliwatt operation matters
- Microcontroller hardware (no OS, limited flash/SRAM, no standard debug)
- Embedded ML inference frameworks (TensorFlow Lite Micro)
- Why energy measurement is a separate, non-trivial undertaking at this scale
- The specific benchmark datasets (Speech Commands, ToyADMOS/MIMII) and tasks (keyword spotting, visual wake words)
- Hardware benchmarking conventions (CoreMark, MLMark)

**Primary personas:**
1. An NLP or vision researcher reading the NeurIPS Datasets and Benchmarks track, evaluating whether this benchmark matters for their community.
2. A systems ML researcher considering deploying models at the edge and wanting to understand the evaluation landscape.

**What must the paper accomplish for this audience:**
- Explain WHY energy is a first-class metric (wireless comm cost > compute cost at this scale)
- Explain what makes MCU-class hardware different from mobile/server hardware
- Connect the four benchmark tasks to familiar ML concepts (classification, anomaly detection with autoencoders)
- Justify the quality targets in terms the reader can understand (gap between fp32 and quantized accuracy)
- Make the measurement methodology legible without requiring embedded systems expertise
