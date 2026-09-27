# Segment Anything: A Foundation Model and 1-Billion-Mask Dataset for Promptable Image Segmentation

**Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alexander C. Berg, Wan-Yen Lo, Piotr Dollár, Ross Girshick**

*Meta AI Research, FAIR*

---

## Abstract

Foundation models — large models pre-trained on broad data and deployed zero-shot across diverse tasks — have transformed natural language processing, yet image segmentation has lacked an equivalent. We present the Segment Anything (SA) project: a new task (promptable segmentation), a new model (SAM, the Segment Anything Model), and a new dataset (SA-1B) that together constitute a foundation model effort for image segmentation. The core challenge is that segmentation masks, unlike text, are not naturally abundant on the internet, making the standard web-scale data collection recipe inapplicable. We address this through a three-stage model-in-the-loop data engine, ultimately producing SA-1B — over 1 billion masks on 11 million licensed images, 400× larger than any prior segmentation dataset. SAM accepts spatial or textual prompts (points, bounding boxes, free-form text) and returns high-quality segmentation masks in approximately 50 ms per prompt after a one-time per-image encoding step. Evaluated zero-shot across 23 diverse benchmarks spanning egocentric, underwater, medical, aerial, and artistic imagery, SAM's masks are rated by human annotators as substantially higher quality than those of the strongest interactive segmentation baseline, and remain competitive with fully supervised methods on measures of intrinsic mask quality as judged by human annotators; SAM trails supervised methods on standard automatic precision metrics in instance segmentation. Both the model (Apache 2.0) and the dataset are released publicly.

---

## 1. Introduction

### 1.1 The Foundation Model Opportunity for Segmentation

Over the past several years, large language models pre-trained on web-scale text have exhibited an important property: by engineering appropriate input prompts, a single model can perform many downstream tasks without any parameter updates (Brown et al., 2020). This foundation model paradigm (Bommasani et al., 2021) scales with model capacity, dataset size, and compute, and has extended to vision-language domains through models such as CLIP (Radford et al., 2021), which aligns image and text representations through contrastive pre-training and enables zero-shot classification and retrieval.

Image segmentation is a core computer vision capability that underlies scene understanding, medical imaging, robot manipulation, and virtually any vision pipeline that must localize objects at the pixel level. Unlike text or image-text pairs, segmentation masks must be traced by human annotators at pixel precision, making them expensive to collect. The largest prior segmentation datasets contain on the order of millions of masks — far smaller than the text corpora behind NLP foundation models — and no general-purpose promptable segmentation model has existed.

### 1.2 Three Tightly Coupled Contributions

The central question this work addresses is: can a promptable segmentation task, a model architecture designed for amortized inference, and a scalable data engine together produce a zero-shot foundation model for image segmentation? The Segment Anything project pursues this question through three interdependent components:

1. **A task** — *promptable segmentation* — which defines a pre-training objective and inference interface general enough to subsume a wide range of downstream segmentation problems via prompt engineering.
2. **A model** — SAM — designed to accept flexible spatial and textual prompts and return valid segmentation masks at interactive speed after a one-time per-image computation.
3. **A dataset** — SA-1B — containing over 1 billion high-quality masks collected through a model-in-the-loop data engine, 400× larger than any prior segmentation dataset.

These components are entangled by design: the model must be efficient enough to assist annotators in real time; the data engine iteratively improves the model; the resulting model must generalize zero-shot to downstream tasks. The remainder of this paper describes each component, presents extensive zero-shot transfer experiments, and discusses limitations and implications.

---

## 2. The Promptable Segmentation Task

### 2.1 Image Segmentation: A Primer

For readers from adjacent ML fields: image segmentation asks a model to return a pixel-level binary mask indicating which pixels belong to a specified object or region. The standard quality metric is **Intersection over Union (IoU)**: IoU = |predicted ∩ ground truth| / |predicted ∪ ground truth|, where 1.0 is perfect overlap and 0.0 is no overlap. The mean of IoU across examples is **mIoU**. Averaged across object instances over a range of IoU thresholds, the mean precision is **AP** (average precision), the standard metric in detection and instance segmentation.

Three standard segmentation paradigms appear in this work, plus a distinct interaction mode:

- **Instance segmentation**: each individual object receives its own mask.
- **Semantic segmentation**: all pixels of the same object *class* share one label; individual instances are not separated.
- **Panoptic segmentation**: a unified map combining both.
- **Interactive segmentation** (interaction mode, not a separate mask type): a human provides iterative clicks or other prompts until an acceptable mask is obtained.

### 2.2 Promptable Segmentation as a General Task

Inspired by how language models accept arbitrary text prompts to address diverse tasks, the authors define the **promptable segmentation task**: given any *prompt* that specifies what to segment, return a valid segmentation mask. A prompt can be foreground and background point clicks, a rough bounding box, a coarse mask, or free-form text. The critical requirement is that the output must be a *valid* mask — that is, even when a prompt is ambiguous (a click on a shirt could refer to the shirt or to the entire person), the model must return a reasonable mask for at least one valid interpretation, rather than returning an error or averaging across objects.

This framing serves two purposes. First, it defines a concrete pre-training objective: simulate a sequence of prompts during training and supervise predicted masks against ground truth. Second, it defines a composable inference interface: any downstream segmentation task that can be expressed as a prompt can in principle be solved by SAM without any parameter updates.

---

## 3. Model Architecture

### 3.1 Three-Component Design

SAM consists of three components motivated by the principle of amortization — paying an expensive computation once and sharing its result across many lightweight operations that follow:

1. **Image encoder** — a heavyweight network that processes the full image once and produces a fixed spatial embedding.
2. **Prompt encoder** — a lightweight network that maps the current prompt into an embedding.
3. **Mask decoder** — a lightweight module that combines the image and prompt embeddings to predict one or more segmentation masks.

The architectural split allows the expensive image encoding to run once per image, while the prompt encoder and mask decoder run separately for each new prompt. Given a precomputed image embedding, **the prompt encoder and mask decoder run in a web browser, on CPU, in approximately 50 ms** — enabling interactive use.

### 3.2 Image Encoder

The image encoder is a Vision Transformer (ViT-H/16; Dosovitskiy et al., 2021) initialized from MAE self-supervised pre-training (He et al., 2022) and minimally adapted for high-resolution inputs (Li et al., 2022). MAE — masked autoencoding — is a self-supervised technique in which random input patches are masked and the model learns to reconstruct them, producing dense visual representations without class labels. The ViT-H variant has approximately 636 million parameters. Images are resized and padded to 1024×1024; the encoder outputs a 64×64 spatial embedding (16× downsampled) with channel dimension 256. Because the image encoder runs only once per image, its high computational cost is amortized over all subsequent prompts.

### 3.3 Prompt Encoder

The prompt encoder handles sparse and dense prompts separately:

- **Sparse prompts** (points, boxes, text): Points are encoded as the sum of a learned positional encoding of their spatial location and a learned foreground/background indicator embedding. Boxes are encoded as two such embeddings (top-left and bottom-right corners). Free-form text is encoded using CLIP's (Radford et al., 2021) text encoder, exploiting the alignment between CLIP's text and image embedding spaces.
- **Dense prompts** (masks): Downsampled with convolutional layers and added element-wise to the image embedding.

### 3.4 Mask Decoder

The mask decoder is a two-layer modified Transformer decoder. Each layer performs four operations: (1) self-attention over prompt tokens; (2) cross-attention from prompt tokens to the image embedding; (3) a per-token MLP update; and (4) cross-attention from the image embedding to prompt tokens. This bidirectional cross-attention allows image features and prompt features to mutually update. After decoding, the image embedding is upsampled and a dynamically generated linear classifier — whose weights are produced by an MLP applied to an output token — predicts the foreground probability at each pixel. The dynamic-weight mechanism means each prompt produces a different classifier over the same precomputed image embedding, making repeated prompting on a single image computationally lightweight.

### 3.5 Handling Prompt Ambiguity

A single point prompt can correspond to multiple valid interpretations at different spatial scales (a subpart, a part, and the whole object). To avoid averaging over these interpretations, SAM predicts **three masks simultaneously** per prompt. During training, loss is computed for each predicted mask against the ground truth, but only the gradient from the minimum-loss prediction is used to update parameters — a standard technique for models with multiple structured outputs (Charpiat et al., 2008; Guzman-Rivera et al., 2012). A separate confidence head predicts an estimated IoU for each mask, enabling downstream systems to select the most relevant output. The authors find that three mask outputs are sufficient to cover the common nested-object cases (subpart, part, whole). When multiple prompts are given — making ambiguity rare — only a single mask is predicted.

---

## 4. The SA-1B Data Engine and Dataset

### 4.1 Why a Data Engine Was Necessary

Prior segmentation datasets are small relative to the scale needed for a foundation model: COCO (Lin et al., 2014) contains 0.9 million masks, Open Images (Kuznetsova et al., 2020) 2.7 million, and LVIS (Gupta et al., 2019) 1.5 million. Since masks cannot be scraped from the internet the way text can, the authors built a **data engine** — an iterative loop in which the evolving SAM assists human annotators, and newly collected annotations retrain SAM.

### 4.2 Three Stages

**Stage 1 — Assisted-manual.** Professional annotators used a browser-based tool powered by SAM to click on objects; SAM proposed pixel-level masks, which annotators refined with brush and eraser tools. No semantic constraints were imposed — annotators labeled anything they could name or describe. SAM was initially trained on existing public segmentation data, then retrained six times as data accumulated. Average annotation time per mask **fell from 34 to 14 seconds** — 6.5× faster than pixel-tracing COCO-style annotation — and average masks per image grew from 20 to 44. Stage 1 produced **4.3 million masks from 120,000 images**.

**Stage 2 — Semi-automatic.** To increase mask diversity, SAM automatically pre-filled confident masks detected by a bounding-box predictor trained on Stage 1 data. Annotators labeled only the remaining unannotated objects. Stage 2 produced an additional **5.9 million masks from 180,000 images** (cumulative total: 10.2 million masks), growing average masks per image to 72. SAM was retrained five more times during this stage.

**Stage 3 — Fully automatic.** With a capable, ambiguity-aware model and a large, diverse mask pool, full automation became feasible. SAM is prompted with a 32×32 regular grid of foreground point locations on each image. For each point, it predicts three masks. Confident masks are selected by the model's predicted IoU score (threshold 88.0), and stable masks are retained by verifying that masks thresholded at nearby logit values (the raw pre-sigmoid model outputs) remain consistent (IoU ≥ 95.0). Non-maximum suppression — NMS, a standard technique that retains only the highest-scoring mask among a set of overlapping candidates — removes duplicates. Multiple overlapping zoomed-in crops are processed to improve small-mask quality. This stage produced **1.1 billion masks** from all 11 million images.

### 4.3 SA-1B Dataset

The final dataset, SA-1B, consists of **11 million high-resolution licensed images** (average 3300×4950 pixels, downsampled to 1500px shortest side for release) with **1.1 billion segmentation masks**, 99.1% of which were generated fully automatically in Stage 3.

SA-1B is **11× larger in images and 400× larger in masks** than Open Images, the previously largest segmentation dataset. On average, each image contains approximately 100 masks, with greater coverage of small and medium objects than prior datasets.

**Mask quality.** To validate automatic mask quality, 500 images (~50,000 masks) were randomly sampled and professional annotators were asked to improve any deficient masks using the same tooling. The IoU between each automatically predicted mask and its human-corrected version was computed: **94% of pairs exceeded 90% IoU, and 97% exceeded 75% IoU**. For comparison, prior work estimates inter-annotator consistency at 85–91% IoU (Gupta et al., 2019; Kuznetsova et al., 2020). These figures are not directly commensurable — the 94% figure is a threshold-exceedance rate while the 85–91% figure is a mean IoU — but together they suggest SA-1B's automatic masks are broadly in the range of human-annotated data quality.

---

## 5. Zero-Shot Transfer Experiments

### 5.1 Evaluation Setup and Metrics

All experiments follow a strict zero-shot protocol: SAM receives no images, annotations, or gradient updates from any evaluation benchmark. This mirrors the zero-shot evaluation of CLIP (Radford et al., 2021): the model is prompted differently for each task, but no fine-tuning occurs. Unless noted otherwise, SAM uses ViT-H and is trained exclusively on automatically generated SA-1B masks.

The 23 evaluation datasets span egocentric video, biological microscopy, X-ray scans of baggage, underwater scenes, aerial drone imagery, autonomous driving, art paintings, and synthetic indoor scenes — diverse distributions not seen during training.

Automatic evaluation uses **mIoU** for single-point tasks, **AP** (average precision) for instance segmentation, **AR@1000** (average recall at 1,000 proposals) for object proposals, and standard edge detection metrics for edge detection: **ODS** (F-score at the optimal threshold for the whole dataset), **OIS** (F-score at the optimal threshold per image), **AP** (area under the precision-recall curve), and **R50** (recall at 50% precision). Human evaluation uses a 1–10 mask quality rating by professional annotators, addressing a key limitation of ground-truth-based metrics: models can be penalized for predicting a valid but different object given an ambiguous prompt, or rewarded for learning dataset-specific annotation artifacts.

### 5.2 Single-Point Mask Evaluation

**Task.** A single foreground point click (chosen at the object's approximate centroid) is provided as the only prompt. This is deliberately challenging — a single click is often ambiguous — and is the core test of promptable segmentation. The primary baseline is RITM (Sofiiuk et al., 2022), the strongest evaluated interactive segmentation model.

**Automatic metrics.** Across 23 datasets, SAM outperforms RITM on **16 of 23 datasets by mIoU**, with gains ranging up to ~47 IoU points on the highest-margin datasets; on the 7 datasets where RITM leads, the margins are smaller. When an oracle evaluation selects the most relevant of SAM's three predicted masks (rather than SAM's own confidence-ranked choice), SAM outperforms RITM on **all 23 datasets**. The gap between oracle and confidence-selected performance may reflect genuine prompt ambiguity in the ground-truth annotation protocol — a single centroid click does not uniquely specify which of multiple valid objects to return — though confidence-head miscalibration could also contribute to this gap.

**Human study.** Annotators rated masks from SAM, single-output SAM (no ambiguity handling), and RITM on seven diverse datasets including both cases where SAM outperforms and underperforms RITM on automatic metrics. SAM's mean ratings fell **between 7 and 9** on the 1–10 scale (defined as "minor boundary errors only"), consistently substantially higher than RITM. Single-output SAM scored between SAM and RITM. On datasets where SAM scored lower than RITM by automatic IoU (e.g., DRAM art paintings, IBD drone imagery), human raters still preferred SAM's masks — indicating that automatic metrics penalize SAM for valid but different interpretations of ambiguous prompts.

**Multi-point behavior.** With 3–9 point prompts, the gap between SAM and other interactive segmentation baselines (SimpleClick; Liu et al., 2022; FocalClick; Chen et al., 2022) narrows as expected: more prompts reduce ambiguity and the task becomes easier. SAM is not optimized for the high-IoU multi-click regime; its advantage lies in single- and few-prompt settings.

### 5.3 Edge Detection

**Approach.** SAM is prompted with a 16×16 grid of foreground points, yielding 768 predicted masks. A Sobel filter — a standard image-processing operator that detects intensity gradients, here applied to unthresholded mask probability maps rather than raw pixel values — extracts edges; lightweight post-processing including edge non-maximum suppression produces the final edge map. SAM was never trained to predict edges.

**Results.** On BSDS500 (Martin et al., 2001), the standard edge detection benchmark, results are evaluated on 200 test images using ODS, OIS, AP, and R50 (defined in §5.1).

**Table 1.** Zero-shot edge detection on BSDS500. Trained methods (top) require BSDS500 training data; zero-shot methods (bottom) do not.

| Method | Year | ODS | OIS | AP | R50 |
|---|---|---|---|---|---|
| HED (Xie & Tu, 2015) | 2015 | .788 | .808 | .840 | .923 |
| EDETR (Pu et al., 2022) | 2022 | .840 | .858 | .896 | .930 |
| *Zero-shot methods:* | | | | | |
| Sobel filter | 1968 | .539 | — | — | — |
| Canny (1986) | 1986 | .600 | .640 | .580 | — |
| Felzenszwalb & Huttenlocher (2004) | 2004 | .610 | .640 | .560 | — |
| **SAM (zero-shot)** | 2023 | **.768** | **.786** | **.794** | **.928** |

SAM achieves ODS=.768, close to the 2015 HED model (.788) which was *trained* on BSDS500, and substantially above classical zero-shot baselines (Canny: ODS=.600; Felzenszwalb & Huttenlocher: ODS=.610). The high R50=.928 reflects SAM's tendency to detect more edges than human annotators label — including valid edges not annotated in BSDS500 — which reduces precision-oriented metrics. SAM naturally trails state-of-the-art supervised methods that have learned BSDS500-specific biases.

Note: Canny (1986) and Felzenszwalb & Huttenlocher (2004) are classical, non-learned algorithms that detect edges using gradient magnitude and graph-based clustering respectively; they represent a lower bound on what learning-based zero-shot methods should achieve.

### 5.4 Object Proposals

**Task.** Object proposal generation asks a model to produce candidate regions likely to contain objects, measured by average recall at 1,000 proposals (AR@1000): what fraction of ground-truth objects does at least one proposal cover, at 1,000 proposals per image?

SAM's automatic mask generation pipeline is applied zero-shot to the LVIS benchmark (Gupta et al., 2019), which provides high-quality masks for 1,203 object classes. The baseline is ViTDet-H (Li et al., 2022) with cascade Mask R-CNN, a fully supervised detector trained in-domain on LVIS — a model that has been shown to "game" AR metrics by exploiting in-domain knowledge (Chavali et al., 2016), making this a stringent comparison.

**Table 2.** Object proposal AR@1000 on LVIS v1. SAM is applied zero-shot.

| Method | All | Small | Med | Large | Freq | Com | Rare |
|---|---|---|---|---|---|---|---|
| ViTDet-H (supervised) | 63.0 | 51.7 | 80.8 | 87.0 | 63.1 | 63.3 | 58.3 |
| SAM – single output | 54.9 | 42.8 | 76.7 | 74.4 | 54.7 | 59.8 | 62.0 |
| **SAM** | **59.3** | **45.5** | **81.6** | **86.9** | **63.9** | **65.8** | **65.8** |

SAM achieves AR@1000=59.3 overall vs. ViTDet-H's 63.0. SAM trails only on small objects (45.5 vs. 51.7) and is essentially tied on large (86.9 vs. 87.0); on medium, frequent, common, and rare objects, SAM matches or surpasses the supervised baseline. The comparison between full SAM and single-output SAM confirms that predicting multiple masks per prompt substantially improves recall.

### 5.5 Instance Segmentation

**Task.** Instance segmentation assigns a separate mask to each individual object in an image. SAM is used as the segmentation module in a simple two-stage pipeline: a separately trained object detector (ViTDet-H; Li et al., 2022) provides bounding boxes as prompts, and SAM produces the corresponding masks. This tests composability — using SAM as a drop-in component — and compares its zero-shot masks to masks produced by the same detector's supervised segmentation head.

**Table 3.** Instance segmentation results. SAM is prompted with ViTDet boxes; it receives no instance labels from COCO or LVIS during training.

| Method | COCO AP | COCO APS | COCO APM | COCO APL | LVIS AP | LVIS APS | LVIS APM | LVIS APL |
|---|---|---|---|---|---|---|---|---|
| ViTDet-H (fully supervised) | 51.0 | 32.0 | 54.3 | 68.9 | 46.6 | 35.0 | 58.0 | 66.3 |
| **SAM (zero-shot)** | **46.5** | **30.8** | **51.0** | **61.7** | **44.7** | **32.5** | **57.6** | **65.5** |

SAM trails ViTDet-H by 4.5 AP on COCO and 1.9 AP on LVIS. However, the human study reverses this ranking: annotators rating masks on the LVIS validation set (ground-truth boxes provided to both models) gave **SAM a mean rating of 8.1 ± 0.07 vs. ViTDet-H's 7.9 ± 0.08**. LVIS ground-truth masks scored 8.6 ± 0.06. No significance test for the 8.1 vs. 7.9 difference is reported; given the narrow gap and overlapping confidence intervals, this result should be read as suggestive rather than definitively significant.

The authors propose that this reversal stems in part from annotation bias: ViTDet-H learns COCO and LVIS-specific mask conventions (e.g., COCO masks have relatively low quality; LVIS masks are simple polygons that cannot contain holes). SAM, as a zero-shot model, does not learn these conventions, producing cleaner boundaries that score better with human raters but worse against the ground truth. No controlled experiment directly isolates annotation-convention bias from other differences in mask style, so this explanation is consistent with the observed pattern but not uniquely confirmed by it.

### 5.6 Text-to-Mask (Proof of Concept)

SAM is adapted to accept free-form text as a prompt by exploiting CLIP's alignment between image and text embeddings (Radford et al., 2021). During training, CLIP image embeddings of ground-truth mask crops are used as prompts; during inference, CLIP text embeddings are substituted, requiring no new text annotations. Qualitative results demonstrate segmentation of objects described by simple phrases ("a wheel") and compositional phrases ("beaver tooth grille"). An additional point prompt can resolve failures when text alone is ambiguous. This task is presented as a proof of concept and is explicitly described as not fully robust.

### 5.7 Ablation Studies

Three ablation studies were run using the 23-dataset mIoU suite with single-center-point prompts:

**Data engine stages.** Each stage increases mIoU. Training on only automatically generated masks (Stage 3 only, with 10× oversampling of earlier-stage masks) reduces performance by only **~0.5 mIoU** relative to using all data — justifying automatic-only training as the default for simplicity.

**Training data volume.** Subsampling SA-1B to **1 million images** (~10% of the full dataset) achieves results comparable to the full 11 million image set. Dropping to 100,000 images causes a large mIoU decline. The 1M image regime, still providing ~100 million masks, may be practical for many downstream applications.

**Image encoder scale.** ViT-H (636M parameters) substantially outperforms ViT-B (91M parameters), but provides only marginal gains over ViT-L (308M parameters). Further scaling of the image encoder does not appear fruitful at current data scales.

---

## 6. Responsible AI Analysis

The performance-focused evaluation in Section 5 tests SAM's capabilities on task benchmarks; this section turns to potential concerns about fairness and representational bias in both the dataset and the model.

**Geographic representation.** SA-1B images span more than 160 countries. Europe (49.8%) and Asia & Oceania (36.2%) are most represented. Africa (2.8%), Latin America & Caribbean (3.5%), and low-income countries (0.9% of images) are underrepresented — a pattern shared by COCO and Open Images, which are even more concentrated in North America and Europe. Despite the relative underrepresentation, every region in SA-1B has at least 28 million masks — more than the total masks in any prior dataset.

**People segmentation fairness.** Using the MIAP dataset (Schumann et al., 2021), SAM's mIoU was measured across perceived gender presentation (feminine/masculine), perceived age group, and perceived skin tone (Fitzpatrick scale 1–6). At 1 point: feminine 54.4 ± 1.7, masculine 55.7 ± 1.7; skin tones ranged from 51.5 to 56.7, all with overlapping 95% confidence intervals. No statistically significant differences were found across gender presentation or skin tone. For age, those perceived as older showed slightly higher mIoU (62.9 ± 6.7 vs. 54.5 ± 1.3 for middle-aged), but the confidence interval for the older group is wide.

**Clothing segmentation bias.** Extending the analysis to clothing items, the authors find a significant performance difference: mIoU at 1 point is **81.0 ± 1.2 for masculine vs. 76.3 ± 1.1 for feminine perceived gender** (disjoint 95% CIs, indicating a statistically significant gap). This gap narrows substantially at 3-point prompting. The authors recommend that users be aware of this limitation when deploying SAM in systems where clothing segmentation is relevant.

---

## 7. Discussion

### 7.1 SAM as a Foundation Model

The term "foundation model" (Bommasani et al., 2021) refers to models trained on broad data at scale and adaptable to many downstream tasks. SAM broadly fits this description for image segmentation, with an important caveat: as noted in §7.3, clear prompting strategies for semantic and panoptic segmentation do not yet exist, so its zero-shot coverage of the full segmentation task space is incomplete. One noteworthy distinction from some foundation model frameworks: while SAM's image encoder is initialized with MAE self-supervised pre-training, the primary source of its capabilities is large-scale *supervised* training on SA-1B. When a data engine can scale annotations, supervised training provides an effective solution — the self-supervised initialization provides a head start, but the scale of human-in-the-loop annotation determines the final capability.

### 7.2 Composability

SAM's design as a promptable module enables composable computer vision pipelines. Just as CLIP (Radford et al., 2021) serves as the image encoder in DALL·E (Ramesh et al., 2021) for text-to-image generation, SAM can be inserted as the segmentation module in larger systems: an object detector provides bounding boxes, a 3D reconstruction system (Wu et al., 2023) uses SAM to isolate objects of interest, or a wearable device's gaze tracker provides point prompts. The enabling property is that SAM aims to produce a valid output for any reasonable prompt — creating a reliable interface between SAM and other components. This composability is broader than what multi-task systems offer, since a multi-task system performs a fixed set of tasks at training time, while SAM can be composed into novel pipelines not anticipated during its design.

### 7.3 Limitations

SAM is not a complete or universal segmentation solution. The authors identify several concrete limitations:

- **Fine structures**: SAM occasionally misses fine-grained structural details and hallucinates small disconnected mask components.
- **Boundary crispness**: Boundaries are less precise than methods that process zoomed-in crops iteratively (e.g., FocalClick; Chen et al., 2022).
- **Many-prompt interactive segmentation**: Dedicated interactive methods optimized for iterative click-based refinement are expected to outperform SAM when many prompts are available.
- **Real-time inference**: While per-prompt latency (~50 ms for prompt encoder + decoder) is interactive-speed, end-to-end inference including the heavy ViT-H encoder is not real-time.
- **Semantic and panoptic segmentation**: No clear prompting strategy exists for producing full semantic or panoptic scene maps from SAM.
- **Text-to-mask robustness**: The CLIP-based text prompting approach demonstrated is not yet reliable.
- **Domain-specific tools**: Specialized models for domains such as bioimage analysis are expected to outperform SAM in their respective areas.

---

## 8. Conclusion

The Segment Anything project introduces three interdependent contributions: the promptable segmentation task, the SAM model, and the SA-1B dataset. The critical enabling innovation is the three-stage data engine — a model-in-the-loop annotation loop that iteratively co-develops model capability and training data, ultimately generating 1.1 billion high-quality masks without ongoing human input. The resulting dataset is 400× larger than any prior segmentation benchmark, and the model trained on it generalizes zero-shot across five qualitatively different task types and 23 diverse image domains, consistently producing masks rated by human annotators as competitive with or preferred over fully supervised baselines when judged on intrinsic quality, while trailing those baselines on standard automatic precision metrics.

The public release of both model weights and SA-1B is intended to support adoption of SAM as a composable building block for larger vision systems. Whether this system achieves lasting use as foundational infrastructure for computer vision will depend on how the research community builds upon it, and on progress toward the remaining open problems in semantic and panoptic prompting, robustness to fine structures, and reliable text-to-mask transfer.

---

## References

Bommasani et al. (2021). On the opportunities and risks of foundation models. *arXiv:2108.07258*.

Brown et al. (2020). Language models are few-shot learners. *NeurIPS*.

Canny, J. (1986). A computational approach to edge detection. *TPAMI*.

Charpiat et al. (2008). Automatic image colorization via multimodal predictions. *ECCV*.

Chavali et al. (2016). Object-proposal evaluation protocol is 'gameable'. *CVPR*.

Chen et al. (2022). FocalClick: towards practical interactive image segmentation. *CVPR*.

Dosovitskiy et al. (2021). An image is worth 16x16 words: Transformers for image recognition at scale. *ICLR*.

Felzenszwalb & Huttenlocher (2004). Efficient graph-based image segmentation. *IJCV*.

Gupta et al. (2019). LVIS: A dataset for large vocabulary instance segmentation. *CVPR*.

Guzman-Rivera et al. (2012). Multiple choice learning: Learning to produce multiple structured outputs. *NeurIPS*.

He et al. (2022). Masked autoencoders are scalable vision learners. *CVPR*.

Kuznetsova et al. (2020). The Open Images dataset V4. *IJCV*.

Li et al. (2022). Exploring plain vision transformer backbones for object detection. *ECCV*.

Lin et al. (2014). Microsoft COCO: Common objects in context. *ECCV*.

Liu et al. (2022). SimpleClick: Interactive image segmentation with simple vision transformers. *arXiv:2210.11006*.

Martin et al. (2001). A database of human segmented natural images and its application to evaluating segmentation algorithms and measuring ecological statistics. *ICCV*.

Pu et al. (2022). EDTER: Edge detection with transformer. *CVPR*.

Radford et al. (2021). Learning transferable visual models from natural language supervision. *ICML*.

Ramesh et al. (2021). Zero-shot text-to-image generation. *ICML*.

Schumann et al. (2021). A step toward more inclusive people annotations for fairness. *AAAI/ACM Conference on AI, Ethics, and Society*.

Sofiiuk et al. (2022). Reviving iterative training with mask guidance for interactive segmentation. *ICIP*.

Wu et al. (2023). Multiview compressive coding for 3D reconstruction. *CVPR*.

Xie & Tu (2015). Holistically-nested edge detection. *ICCV*.

Zhou et al. (2019). Semantic understanding of scenes through the ADE20K dataset. *IJCV*.
