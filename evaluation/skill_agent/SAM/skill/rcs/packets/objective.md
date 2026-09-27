# Paper Objective

**Deliverable:** Standalone research paper presenting the Segment Anything project.

**Primary research question:** Can a promptable segmentation task definition, a model architecture supporting real-time interactive prompting, and a model-in-the-loop data engine together enable a foundation model for image segmentation that generalizes zero-shot to diverse downstream tasks?

**Key contribution claimed:** Three interdependent contributions — task (promptable segmentation), model (SAM), and dataset (SA-1B with 1.1 billion masks, 400× larger than any prior segmentation dataset) — that together constitute a foundation model effort for image segmentation.

**The paper must convey to its audience:**
1. Why image segmentation lacks a foundation model (masks not web-abundant; no existing promptable model).
2. What "promptable segmentation" means and why it is the right task formulation for generalization.
3. How SAM is architecturally designed for amortized real-time prompting (image encoder once; prompt encoder + decoder per prompt, ~50ms).
4. How the three-stage data engine solved the data scarcity problem.
5. What zero-shot transfer experiments show: SAM outperforms RITM on 16/23 datasets automatically and all 23 with oracle; human raters prefer SAM; competitive with or trailing supervised methods by small margins in instance segmentation; strong edge detection without edge training.
6. The fairness analysis findings: no significant bias in people segmentation; bias detected in clothing segmentation across perceived gender.
7. The key limitation: SAM is not real-time end-to-end; misses fine structures; no robust text-to-mask; no semantic/panoptic prompting strategy.

**Scope boundary:** This paper presents SAM v1 (arXiv:2304.02643). SAM 2 (video extension) is not part of this work.
