# Research Communication Objective

**Paper:** "Robust Speech Recognition via Large-Scale Weak Supervision" (Radford et al., 2022)

**Deliverable:** Standalone research paper in Markdown for adjacent ML researchers (Mode B audience).

**Core claim to communicate:**
Training an encoder-decoder Transformer on 680,000 hours of weakly supervised internet
audio produces a speech recognition model that, evaluated zero-shot, achieves 55.2% average
relative error reduction over a supervised model matched on in-distribution performance —
across 13 diverse out-of-distribution benchmarks — and approaches human-level accuracy and
robustness on English speech.

**The one argument the reader must leave with:**
The robustness gap between human and machine speech recognition is a training distribution
problem, not a model capacity problem. Broad, diverse, weakly supervised data at scale
produces robustness that task-specific in-distribution training cannot.

**Why adjacent researchers should care:**
- Directly analogous to the CLIP result in vision: internet-scale weak supervision enables
  zero-shot generalization that matches specialized supervised baselines
- Reframes the meaning of "superhuman" benchmark performance (in-distribution ≠ generally capable)
- The scaling result is directly relevant to LLM-adjacent researchers thinking about
  data curation, training efficiency, and multitask generalization
- Released models serve as a strong multimodal backbone for further research

**What must NOT be overclaimed:**
- Fine-tuning performance is not studied; zero-shot results may be conservative
- Low-resource language performance is limited by training data, not the approach
- The human comparison uses a small sample (25 recordings) without confidence intervals
- Text normalizer co-development introduces modest evaluation bias on some benchmarks
- Language identification underperforms supervised SOTA due to missing training languages

**Success criterion:**
A reader who studies NLP or CV but not speech should finish the paper understanding:
(1) what the robustness problem in ASR is and why it matters,
(2) why existing approaches fail to solve it,
(3) how Whisper solves it and with what evidence,
(4) what the honest limitations are,
and should be able to describe the key result (55.2% RER) to a colleague.
