# Paper Skeleton — Segment Anything

## Title
Segment Anything: A Foundation Model and 1-Billion-Mask Dataset for Promptable Image Segmentation

## Abstract
[Compressed argument: problem → approach → key result → impact]

## 1. Introduction
- The NLP recipe — web-scale pre-training with prompting — has produced foundation models that generalize zero-shot; image segmentation lacks an equivalent. {C001}
- Three tightly coupled challenges must be solved together: defining a suitable prompting interface, building a model architecture that supports it at interactive speed, and obtaining diverse training data at scale. {C002, C003}
- We present SAM and SA-1B: a promptable model and 1.1 billion-mask dataset that together constitute a foundation model for image segmentation. {C004, C005, C006}
- Paper roadmap: task definition → model → data engine → dataset → evaluation → discussion.

## 2. The Promptable Segmentation Task
- In NLP, the "next token" task is general enough to enable many downstream applications via prompting; we seek an analogous task for segmentation. {C003}
- A prompt specifies what to segment (points, boxes, masks, or free-form text); the model must return a valid mask for at least one interpretation of any ambiguous prompt. {C004}
- This task serves as both pre-training objective and zero-shot inference interface. {C004}

## 3. Model Architecture (SAM)
- SAM has three components: a heavyweight image encoder (run once per image), a prompt encoder, and a lightweight mask decoder (run per prompt). {C004}
- The image encoder is an MAE pre-trained ViT-H; the prompt encoder handles sparse (points, boxes, text) and dense (mask) prompts; the decoder uses cross-attention to predict masks in ~50ms on CPU. {C004}
- To handle prompt ambiguity, SAM predicts three masks per prompt and an IoU-based confidence score; training uses minimum-loss backpropagation over the three outputs. {C004}

## 4. SA-1B: A Data Engine and Dataset at Scale
- Masks are not naturally abundant online; we built a three-stage data engine that iteratively improves SAM and uses it to collect data. {C005}
- Stage 1 (assisted-manual): SAM helps annotators; 4.3M masks from 120k images; annotation time fell from 34 to 14 seconds per mask. {C005, E011}
- Stage 2 (semi-automatic): SAM auto-fills confident masks; annotators label the rest; 5.9M additional masks, 180k images. {C005, E012}
- Stage 3 (fully automatic): a 32×32 foreground-point grid prompts SAM on all 11M images; 1.1B masks produced; 99.1% of SA-1B is from this stage. {C005, C006, E013}
- SA-1B quality: 94% of auto masks exceed 90% IoU with professional corrections, comparable to inter-annotator consistency (85-91% IoU). {C013}
- SA-1B is 400× larger than the previous largest segmentation dataset. {C006}

## 5. Zero-Shot Transfer Experiments
- Evaluation framework: 23 diverse datasets spanning egocentric, underwater, X-ray, microscopy, driving, and art-painting imagery — none seen during training. {E024}
- Task 1 — single-point mask: SAM outperforms RITM on 16/23 datasets; with oracle ambiguity resolution, outperforms on all 23; human study confirms substantially higher mask quality (mean 7-9 vs. lower for RITM). {C007, C008}
- Task 2 — edge detection: SAM achieves ODS=.768 on BSDS500 without BSDS training, near the 2015 supervised HED (.788) and substantially above classical zero-shot baselines. {C010}
- Task 3 — object proposals: SAM achieves AR@1000=59.3 on LVIS, close to ViTDet-H (63.0) and outperforming on medium, large, and rare objects. {C007}
- Task 4 — instance segmentation: SAM (prompted with ViTDet boxes) achieves AP 46.5 on COCO vs. ViTDet 51.0; human raters prefer SAM's mask quality (8.1 vs. 7.9). {C009}
- Task 5 — text-to-mask: proof-of-concept using CLIP image/text embedding alignment; qualitative results demonstrate feasibility. {C011}
- Ablations: each data engine stage improves performance; automatic-only data yields only ~0.5 mIoU lower; 1M images comparable to full 11M; ViT-H substantially better than ViT-B with marginal gain over ViT-L. {C014}

## 6. Responsible AI Analysis
- SA-1B spans 161+ countries; underrepresents Africa and low-income countries relative to population. {E023}
- People segmentation: no statistically significant bias across perceived gender or skin tone. {C015}
- Clothing segmentation: gender-presentation bias detected at 1-point prompting (masculine: 81.0 vs. feminine: 76.3 mIoU, disjoint CIs). {C015}

## 7. Discussion
- SAM as a foundation model: the large-scale supervised training on SA-1B is the primary source of capability, contrasting with self-supervised emphasis in prior foundation model frameworks. {C011}
- Composability: SAM's interface enables plug-in use in larger systems (e.g., instance segmenter = detector + SAM; 3D reconstruction + SAM). {C011}
- Limitations: fine structure missed; no real-time end-to-end; text prompting not robust; semantic/panoptic prompting unclear. {C012, L001, L002}

## 8. Conclusion
- SAM, SA-1B, and the promptable segmentation task together constitute an attempt to bring image segmentation into the foundation model era. {C006, C011}
