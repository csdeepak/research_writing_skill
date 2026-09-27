# Segment Anything: A Foundation Model for Image Segmentation

**Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alexander C. Berg, Wan-Yen Lo, Piotr Dollár, Ross Girshick**

*Meta AI Research, FAIR*

---

## Abstract

We present the Segment Anything (SA) project, which introduces three tightly coupled contributions aimed at establishing a foundation model for image segmentation: a new task formulation called *promptable segmentation*, a model called the Segment Anything Model (SAM), and a large-scale dataset called SA-1B. SAM accepts flexible spatial or textual prompts—points, boxes, masks, or free-form text—and returns a valid binary segmentation mask for the indicated region, even when the prompt is ambiguous. To collect sufficient training data, we built a three-stage data engine that co-evolved the model and annotations, ultimately generating over 1.1 billion masks on 11 million licensed, high-resolution, privacy-preserving images. SAM is designed for real-time interactive use: given a precomputed image embedding, the prompt encoder and mask decoder run in approximately 50 ms in a web browser. Evaluated under zero-shot transfer on 23 diverse segmentation datasets spanning domains unseen during training, SAM produces mask quality that surpasses prior interactive segmentation methods by human judgement and is competitive with fully supervised baselines on tasks such as edge detection, object proposal generation, and instance segmentation. We release SA-1B and SAM (Apache 2.0 license) to support future foundation model research in computer vision.

---

## 1. Introduction

Large language models pre-trained on web-scale text have demonstrated strong zero-shot and few-shot generalization across diverse tasks (Brown et al., 2020; Chowdhery et al., 2022). A key enabler is *prompting*: a user specifies the desired behavior through natural language, and the model responds appropriately without task-specific fine-tuning. This paradigm has also appeared in vision through models such as CLIP (Radford et al., 2021) and ALIGN (Jia et al., 2021), which align image and text representations and generalize to novel visual concepts via engineered text prompts. Yet computer vision encompasses a much broader set of problems—including segmentation, depth estimation, and tracking—for which abundant web-scale supervision does not naturally exist.

This work asks whether the same foundation-model philosophy can be applied to *image segmentation*, one of the most fundamental and challenging perception tasks. Three questions structure the effort:

1. What task formulation enables zero-shot generalization to new segmentation problems?
2. What model architecture satisfies the joint requirements of flexible prompting and real-time interactive use?
3. What data can power such a task and model when web-scale segmentation annotations do not exist?

The answers to these questions are interdependent, and the paper presents a unified solution. The *promptable segmentation task* provides a pre-training objective that generalizes to downstream applications through prompt engineering, analogously to next-token prediction in language modeling. The *Segment Anything Model (SAM)* is architected so that a costly image encoding step can be amortized across many prompts, enabling real-time mask prediction. Finally, a *data engine* bootstraps annotation by iterating between model-assisted labeling and model retraining, ultimately producing SA-1B, the largest segmentation dataset to date by a large margin—400× more masks than any prior dataset (Gupta et al., 2019; Kuznetsova et al., 2020).

---

## 2. Task: Promptable Segmentation

### 2.1 Formulation

The promptable segmentation task is defined as follows: given any *prompt* specifying what to segment in an image, return a valid segmentation mask. A prompt can be a set of foreground/background points, a rough bounding box, a coarse mask, free-form text, or any combination thereof. The requirement of a *valid* mask means that even when a prompt is inherently ambiguous—a single point on a shirt may correspond to the shirt, the person wearing it, or the whole scene—the model must return a reasonable mask for at least one valid interpretation, rather than averaging over interpretations or refusing to answer.

This requirement mirrors the expectation that a language model should produce a coherent response to an ambiguous prompt. It is also necessary for the task to serve as a general-purpose pre-training objective.

### 2.2 Pre-training and Zero-Shot Transfer

Pre-training simulates a sequence of prompts (points, boxes, masks) for each training sample and compares predicted masks against ground truth. This is adapted from interactive segmentation (Xu et al., 2016; Mahadevan et al., 2018), but with a crucial difference: rather than aiming to eventually converge on a valid mask after many user corrections, the model must always return a valid mask for *any* prompt, including ambiguous single-point prompts. This requirement is essential for automatic data annotation in the data engine.

At inference time, downstream segmentation tasks are solved by engineering appropriate prompts. For instance, cat instance segmentation can be performed by feeding a bounding-box detector's outputs as box prompts to SAM—no segmentation-specific fine-tuning is required. This is a form of task generalization (da Silva et al., 2012) distinct from multi-task segmentation systems, where training and test tasks are the same (Zhang et al., 2021; Cheng et al., 2022).

---

## 3. Model Architecture

SAM has three components: an image encoder, a prompt encoder, and a mask decoder. The overall design prioritizes *amortized efficiency*: the expensive image encoding step runs once per image, while the lightweight prompt encoder and mask decoder run per prompt.

### 3.1 Image Encoder

The image encoder is a Vision Transformer (ViT) (Dosovitskiy et al., 2021) pre-trained with Masked Autoencoder (MAE) self-supervision (He et al., 2022). Specifically, SAM uses a ViT-H/16 backbone with 14×14 windowed attention and four equally-spaced global attention blocks, following the high-resolution adaptation of (Li et al., 2022). Input images are rescaled and padded to 1024×1024; the image embedding is therefore 64×64×256. The encoder is computationally expensive (636 million parameters for ViT-H) but runs only once per image, regardless of how many prompts are subsequently applied.

### 3.2 Prompt Encoder

Two categories of prompts are supported:

- **Sparse prompts** (points, boxes, text): Points are represented as the sum of a positional encoding (Tancik et al., 2020) and a learned foreground/background embedding. Boxes are represented as an embedding pair encoding the top-left and bottom-right corners. Free-form text is embedded with CLIP's (Radford et al., 2021) off-the-shelf text encoder.
- **Dense prompts** (masks): Masks are processed by two stride-2 convolutions and a 1×1 convolution to produce a 256-dimensional spatial embedding, which is added element-wise to the image embedding.

### 3.3 Mask Decoder

The mask decoder maps the image embedding, prompt embeddings, and output tokens to one or more binary masks. It uses a modified Transformer decoder (Vaswani et al., 2017) inspired by DETR (Carion et al., 2020) and MaskFormer (Cheng et al., 2021). Each decoder layer performs four steps: (1) self-attention over prompt tokens; (2) cross-attention from prompt tokens to the image embedding; (3) a point-wise MLP update per token; and (4) cross-attention from the image embedding back to tokens, updating the image embedding with prompt information. Two such layers are used.

After the decoder, the image embedding is upsampled 4× via transposed convolutions, and a small MLP maps each output token to a dynamic linear classifier that predicts mask foreground probability at each spatial location.

### 3.4 Handling Ambiguity

When a single prompt is ambiguous, predicting a single mask produces an average over valid interpretations—an undesirable behavior. SAM instead predicts three masks simultaneously, corresponding to the whole object, a part, and a subpart, which typically covers the common cases of nested segmentation. During training, loss is backpropagated only through the minimum-loss mask (Charpiat et al., 2008; Guzman-Rivera et al., 2012; Li et al., 2018). At inference, the model also produces an estimated IoU confidence score for each mask, used for ranking.

### 3.5 Efficiency

Given a precomputed image embedding, the prompt encoder and mask decoder run in approximately 50 ms in a web browser on CPU, enabling seamless real-time interactive segmentation. Training uses a linear combination of focal loss (Lin et al., 2017) and dice loss (Milletari et al., 2016) in a 20:1 ratio, with an additional mean-squared-error loss on the IoU confidence predictions. Eleven iterative prompt rounds are simulated per mask during training, following (Sofiiiuk et al., 2022; Forte et al., 2020).

---

## 4. Data Engine

Because segmentation masks are not naturally abundant on the internet, the authors built a three-stage data engine that iterates between model-assisted annotation and model retraining.

### 4.1 Stage 1: Assisted-Manual Annotation

Professional annotators labeled masks using a browser-based interactive segmentation tool powered by SAM. Annotators clicked foreground/background points and could refine masks with pixel-precise brush and eraser tools. No semantic constraints were imposed; annotators labeled any object they could name or describe, in order of prominence.

SAM was initially trained on public segmentation datasets and retrained six times as more annotations accumulated, with the image encoder scaled from ViT-B to ViT-H. Average annotation time per mask decreased from 34 seconds to 14 seconds as the model improved—6.5× faster than COCO mask annotation (Lin et al., 2014) and only 2× slower than bounding-box labeling with extreme points (Papadopoulos et al., 2017; Maninis et al., 2018). The average number of masks per image increased from 20 to 44 over the course of this stage. In total, 4.3 million masks were collected from 120,000 images.

### 4.2 Stage 2: Semi-Automatic Annotation

To increase mask diversity, SAM was used to automatically generate confident masks for prominent objects (detected by a generic object bounding-box detector trained on Stage 1 data). Annotators were then shown images pre-filled with these masks and asked to annotate any remaining unannotated objects. This focus on less prominent objects increased per-image mask diversity. Five model retraining cycles occurred during this stage. An additional 5.9 million masks were collected from 180,000 images, bringing the cumulative total to 10.2 million masks. Average annotation time rose back to 34 seconds for the manually labeled objects (which were harder to segment), and the average number of masks per image grew from 44 to 72 (including automatic masks).

### 4.3 Stage 3: Fully Automatic Annotation

With a sufficiently capable and ambiguity-aware model, annotation became fully automatic. SAM was prompted with a 32×32 regular grid of foreground points on the full image, plus additional zoomed-in crops using finer point grids, yielding on average approximately 100 high-quality masks per image. The IoU prediction module filtered for confident masks; stability filtering further required that binary masks obtained at two different probability thresholds (0.5 − δ and 0.5 + δ) be similar. Non-maximal suppression removed duplicates. This fully automatic stage was applied to all 11 million images, producing 1.1 billion masks. The 99.1% of masks generated in this final stage constitute the released SA-1B dataset.

---

## 5. The SA-1B Dataset

### 5.1 Overview

SA-1B contains 11 million diverse, high-resolution, licensed, and privacy-preserving images with 1.1 billion high-quality segmentation masks—400× more masks than the largest previously existing segmentation dataset, Open Images (Kuznetsova et al., 2020), which has 2.7 million masks across 1 million images. Images were licensed from a provider working directly with photographers and have an average resolution of 3,300×4,950 pixels. Faces and vehicle license plates have been blurred in the released version, with the shortest side downsampled to 1,500 pixels for accessibility.

### 5.2 Mask Quality Verification

To validate the quality of the automatically generated masks, 500 images (~50,000 masks) were randomly sampled and professionally annotated to improve mask quality. Computing IoU between each automatic mask and its human-corrected counterpart revealed that 94% of pairs have IoU > 90%, and 97% have IoU > 75%. For comparison, prior work estimates inter-annotator consistency at 85–91% IoU (Everingham et al., 2010 as cited in; Kuznetsova et al., 2020). This confirms that the automatic masks are of quality comparable to human annotation.

### 5.3 Dataset Properties

**Scale.** SA-1B has 11× more images and 400× more masks than Open Images. On average, it has 36× more masks per image than Open Images; the closest dataset in masks per image, ADE20K (Zhou et al., 2019), still has 3.5× fewer.

**Spatial distribution.** Common photographer center-bias is present in SA-1B, as in other datasets, but SA-1B has greater coverage of image corners compared to LVIS v1 (Gupta et al., 2019) and ADE20K.

**Mask size and shape.** Because SA-1B has more masks per image, it includes a higher proportion of small and medium relative-size masks. Shape complexity (mask concavity) is broadly similar to that of other segmentation datasets after controlling for mask size.

**Geographic coverage.** Images span most of the world's countries. SA-1B has substantially higher representation of Europe and Asia & Oceania, and of middle-income countries, compared to COCO (Lin et al., 2014) and Open Images. All datasets underrepresent Africa and low-income countries, though SA-1B's African subset alone contains at least 28 million masks—more than the total mask count of any previous dataset.

---

## 6. Responsible AI Analysis

The authors investigate potential fairness concerns in two dimensions: the geographic and income distribution of the training dataset, and SAM's segmentation performance across demographic groups.

### 6.1 Geographic and Income Representation

Table 1 summarizes the geographic and income representation of SA-1B, COCO, and Open Images. SA-1B has 36.2% of images from Asia & Oceania and 49.8% from Europe, compared to COCO's 11.4% and 34.2% respectively. High-income countries account for 54.0% of SA-1B images; middle-income countries account for 45.0%. The average number of masks per image is fairly consistent across region and income level (94–108 per image), suggesting that mask density does not compound geographic imbalance.

**Table 1: Geographic and income representation in SA-1B, COCO, and Open Images.**

| Region | SA-1B % images | COCO % images | Open Images % images |
|---|---|---|---|
| Africa | 2.8% | 3.0% | 1.7% |
| Asia & Oceania | 36.2% | 11.4% | 14.3% |
| Europe | 49.8% | 34.2% | 36.2% |
| Latin America & Caribbean | 3.5% | 3.1% | 5.0% |
| North America | 7.7% | 48.3% | 42.8% |
| High income countries | 54.0% | 89.1% | 87.5% |
| Middle income countries | 45.0% | 10.5% | 12.0% |
| Low income countries | 0.9% | 0.4% | 0.5% |

### 6.2 Fairness in Segmenting People

SAM's performance was evaluated on the More Inclusive Annotations for People (MIAP) dataset (Schumann et al., 2021) for perceived gender presentation and age group, and on a proprietary dataset for perceived skin tone (Fitzpatrick types 1–6, Fitzpatrick 1988). Evaluation used simulated interactive segmentation with 1 and 3 random point prompts.

**Table 2: SAM's mIoU across demographic groups (95% confidence intervals shown).**

| Group | mIoU at 1 point | mIoU at 3 points |
|---|---|---|
| Perceived gender: feminine | 54.4 ± 1.7 | 90.4 ± 0.6 |
| Perceived gender: masculine | 55.7 ± 1.7 | 90.1 ± 0.6 |
| Perceived age: older | 62.9 ± 6.7 | 92.6 ± 1.3 |
| Perceived age: middle | 54.5 ± 1.3 | 90.2 ± 0.5 |
| Perceived age: young | 54.2 ± 2.2 | 91.2 ± 0.7 |
| Skin tone 1 (lightest) | 52.9 ± 2.2 | 91.0 ± 0.9 |
| Skin tone 2 | 51.5 ± 1.4 | 91.1 ± 0.5 |
| Skin tone 3 | 52.2 ± 1.9 | 91.4 ± 0.7 |
| Skin tone 4 | 51.5 ± 2.7 | 91.7 ± 1.0 |
| Skin tone 5 | 52.4 ± 4.2 | 92.5 ± 1.4 |
| Skin tone 6 (darkest) | 56.7 ± 6.3 | 91.2 ± 2.4 |

Within each grouping, all confidence intervals overlap (except for older vs. middle age), and no significant performance gap across skin tones is observed. An additional analysis of clothing segmentation found a bias across perceived gender presentation with one-point prompts (masculine: 81.0 ± 1.2; feminine: 76.3 ± 1.1, with disjoint confidence intervals at 1 point), though this gap closed with 3-point prompts. The authors caution that additional biases may emerge when SAM is used as a component in larger systems.

---

## 7. Zero-Shot Transfer Experiments

All experiments follow a zero-shot transfer protocol: SAM is not fine-tuned on any test dataset. The default model uses a ViT-H image encoder and is trained solely on the automatically generated masks of SA-1B.

### 7.1 Zero-Shot Single-Point Mask Evaluation

**Setup.** Segmentation quality from a single foreground point prompt is evaluated on a new benchmark suite of 23 diverse datasets covering domains including egocentric video, microscopy, X-ray, underwater imagery, aerial imagery, autonomous driving, and art paintings (see Figure 8 in the original paper for the full list). A single point is the most demanding prompt type because it is maximally ambiguous. Two metrics are used: (1) standard mIoU against ground truth and (2) human mask quality ratings on a 1–10 scale (1 = nonsense, 10 = pixel-perfect), because ground truth IoU can penalize a model for returning a valid but different interpretation of an ambiguous prompt. The primary baseline is RITM (Sofiiiuk et al., 2022), which the authors identify as the strongest published interactive segmenter on this benchmark.

**Automatic metric results.** SAM yields higher mIoU than RITM on 16 of 23 datasets. Improvements are as large as ~47 IoU points on individual datasets. When the oracle (best of SAM's three predictions relative to ground truth) is used instead of the most-confident prediction, SAM outperforms RITM on all 23 datasets, revealing that much of the remaining gap is due to prompt ambiguity rather than mask quality.

**Human study results.** Human annotators consistently rated SAM's masks substantially higher than RITM across all evaluated datasets. SAM's mean ratings fall between 7 and 9 across datasets, corresponding to the guideline level "the object is identifiable and errors are small and rare." An ablated single-output version of SAM (which cannot handle ambiguity) receives consistently lower ratings than multi-output SAM, but still higher than RITM—confirming that both architectural ambiguity resolution and overall mask quality contribute to SAM's advantage.

**Scaling with prompt count.** As the number of points increases from 1 to 9, the gap between SAM and competing interactive segmenters (SimpleClick, Sofiiiuk et al., 2022 reference; FocalClick, Chen et al., 2022) decreases, as expected when the task becomes less ambiguous. The authors note that SAM is not optimized for the very high-IoU regime achievable with many correction points.

### 7.2 Zero-Shot Edge Detection

**Setup.** SAM is applied to edge detection on BSDS500 (Martin et al., 2001; Arbelaez et al., 2010) without any training on BSDS data. SAM is prompted with a 16×16 regular grid of foreground points, producing 768 masks. Edge maps are derived by Sobel-filtering the unthresholded mask probability maps, followed by edge NMS.

**Results.** Table 3 reports performance using the standard metrics ODS, OIS, AP, and R50.

**Table 3: Zero-shot edge detection on BSDS500.**

| Method | Year | ODS | OIS | AP | R50 |
|---|---|---|---|---|---|
| HED (Xie & Tu, 2015) | 2015 | .788 | .808 | .840 | .923 |
| EDETR (Pu et al., 2022) | 2022 | .840 | .858 | .896 | .930 |
| Sobel filter | 1968 | .539 | — | — | — |
| Canny (Canny, 1986) | 1986 | .600 | .640 | .580 | — |
| Felz-Hutt (Felzenszwalb & Huttenlocher, 2004) | 2004 | .610 | .640 | .560 | — |
| **SAM (zero-shot)** | 2023 | **.768** | **.786** | **.794** | **.928** |

SAM substantially outperforms prior zero-shot transfer baselines (Sobel, Canny, and Felzenszwalb & Huttenlocher, 2004) and approaches the performance of HED (Xie & Tu, 2015), which was fully supervised on BSDS500. SAM's recall at 50% precision (R50 = .928) matches that of HED and EDETR, reflecting a tendency to detect more edges than the BSDS500 ground truth annotations. This bias—producing edges that are valid but not annotated—explains the gap in precision-oriented metrics.

### 7.3 Zero-Shot Object Proposal Generation

**Setup.** SAM is used to generate object proposals on LVIS v1 (Gupta et al., 2019), which provides masks for 1,203 object categories and thus represents a challenging open-vocabulary test. The standard average recall (AR) at 1,000 proposals is reported. The comparison baseline is a cascade ViTDet-H detector (Li et al., 2022) that was fully supervised on LVIS—a demanding comparison because a trained in-domain detector can exploit dataset-specific biases to game AR (Chavali et al., 2016).

**Results.** Table 4 reports mask AR@1000 across object size and category frequency.

**Table 4: Object proposal generation on LVIS v1.**

| Method | AR@1000 all | small | med | large | freq | com | rare |
|---|---|---|---|---|---|---|---|
| ViTDet-H (supervised) | 63.0 | 51.7 | 80.8 | 87.0 | 63.1 | 63.3 | 58.3 |
| SAM – single output | 54.9 | 42.8 | 76.7 | 74.4 | 54.7 | 59.8 | 62.0 |
| **SAM** | **59.3** | **45.5** | **81.6** | **86.9** | **59.1** | **63.9** | **65.8** |

Despite being applied zero-shot, SAM outperforms ViTDet-H on medium and large objects and on rare and common object categories. SAM underperforms only on small and frequent objects, where ViTDet-H can leverage LVIS-specific biases. The multi-output version of SAM substantially outperforms the single-output ablation across all metrics, confirming that predicting multiple masks per point substantially improves recall.

### 7.4 Zero-Shot Instance Segmentation

**Setup.** SAM serves as the segmentation module within an instance segmenter: a fully supervised ViTDet-H detector provides bounding-box prompts, and SAM predicts the corresponding masks zero-shot. Performance is reported as mask Average Precision (AP) on COCO (Lin et al., 2014) and LVIS v1.

**Results.** Table 5 compares mask quality.

**Table 5: Zero-shot instance segmentation (mask AP).**

| Method | COCO AP | COCO APS | COCO APM | COCO APL | LVIS AP | LVIS APS | LVIS APM | LVIS APL |
|---|---|---|---|---|---|---|---|---|
| ViTDet-H (supervised) | 51.0 | 32.0 | 54.3 | 68.9 | 46.6 | 35.0 | 58.0 | 66.3 |
| SAM (zero-shot seg.) | 46.5 | 30.8 | 51.0 | 61.7 | 44.7 | 32.5 | 57.6 | 65.5 |

SAM's AP lags behind fully supervised ViTDet-H. However, a human study in which annotators rated mask quality from 1–10 reveals that SAM masks receive higher ratings than ViTDet-H masks (SAM: 8.1 ± 0.07; ViTDet-H: 7.9 ± 0.08; LVIS ground truth: 8.6 ± 0.06). The authors attribute the AP gap to annotation biases in the training datasets: ViTDet-H learns dataset-specific quirks (e.g., COCO masks' tendency toward lower boundary precision; LVIS masks being simple polygons without holes) that inflate AP without genuinely improving mask quality. SAM, being zero-shot, cannot exploit these biases—and conversely produces cleaner, more geometrically accurate masks.

### 7.5 Zero-Shot Text-to-Mask

As a proof-of-concept, SAM is adapted to accept free-form text prompts. The adaptation exploits CLIP's aligned image-text embedding space: during training, SAM is prompted with CLIP image embeddings of masked image crops; at inference, CLIP text embeddings are used instead. This requires no new text annotations. Qualitative results show that SAM can segment objects from simple noun phrases ("a wheel") and more nuanced descriptions ("beaver tooth grille"), and that ambiguous text predictions can be refined with an additional point prompt.

### 7.6 Ablation Studies

Three ablation studies are conducted on the 23-dataset benchmark:

**Data engine stages.** Training on only Stage 1 (assisted-manual) data is the weakest. Each additional stage improves mIoU. Crucially, training on only the automatically generated Stage 3 masks performs nearly as well (within ~0.5 mIoU) as training on all three stages combined. This is the default configuration, simplifying the training pipeline considerably.

**Training data volume.** At 0.1M images (~1% of SA-1B), performance degrades substantially. At 1M images (~10% of SA-1B, containing approximately 100 million masks), performance is comparable to training on all 11M images. This suggests a practical setting for resource-constrained use cases.

**Image encoder scaling.** ViT-H (636M parameters) outperforms ViT-B (91M parameters) substantially, but shows only marginal gains over ViT-L (308M parameters), suggesting diminishing returns from further encoder scaling at this time.

---

## 8. Discussion

### 8.1 Foundation Models for Segmentation

The Segment Anything project draws an explicit parallel to foundation models in NLP (Bommasani et al., 2021): large-scale pre-training on diverse data enables flexible downstream use through prompting and composition. One key distinction is the role of data supervision: whereas foundation models in NLP rely heavily on self-supervised objectives (Brown et al., 2020), SAM's capabilities emerge primarily from large-scale *supervised* training, made feasible by the data engine that bootstraps annotation automatically.

### 8.2 Compositionality

A central design goal is making SAM composable within larger systems. SAM exposes a clean interface—any valid spatial or textual prompt produces a reasonable mask—that allows it to be slotted into pipelines without task-specific retraining. Examples demonstrated include instance segmentation (SAM + ViTDet-H detector), text-conditioned segmentation (SAM + CLIP), and 3D reconstruction from a single RGB-D image (SAM + MCC, Wu et al., 2023). This composability is analogous to how CLIP (Radford et al., 2021) serves as a universal image-text alignment component in systems such as DALL·E (Ramesh et al., 2021).

### 8.3 Limitations

SAM is not without shortcomings. It can miss fine structures, hallucinate small disconnected components, and produces less crisp boundaries than specialized methods that "zoom in" on objects (Chen et al., 2022). At high point counts (e.g., 9+ corrections), dedicated interactive segmenters such as SimpleClick (Liu et al., 2022) may outperform SAM. SAM's overall pipeline is not real-time when including the heavy image encoder, though per-prompt latency is real-time. The text-to-mask capability is exploratory and not fully robust. Finally, designing prompts that implement semantic or panoptic segmentation—assigning class labels to regions—remains an open challenge not addressed by this work.

---

## 9. Conclusion

The Segment Anything project introduces three interconnected contributions—a promptable segmentation task, the Segment Anything Model (SAM), and the SA-1B dataset—aimed at lifting image segmentation into the foundation model era. The data engine that co-evolves model and annotations is the practical cornerstone of the work: it scales annotation by 100× over existing datasets without sacrificing mask quality, as verified through human evaluation showing 94% of automatic masks achieve IoU > 90% with professional corrections. Zero-shot transfer experiments across 23 diverse datasets demonstrate that SAM generalizes to image distributions and task formulations well outside its training distribution, performing comparably to or better than strongly supervised baselines on multiple tasks, while human studies consistently rank SAM's mask quality above fully supervised alternatives despite lower AP metrics. The release of SA-1B and SAM under permissive licenses is expected to support a broad range of follow-on research into foundation models for computer vision.

---

## References

Arbelaez, P., Maire, M., Fowlkes, C., and Malik, J. Contour detection and hierarchical image segmentation. *TPAMI*, 2010.

Bommasani, R., Hudson, D. A., Adeli, E., et al. On the opportunities and risks of foundation models. *arXiv:2108.07258*, 2021.

Brown, T., Mann, B., Ryder, N., et al. Language models are few-shot learners. *NeurIPS*, 2020.

Canny, J. A computational approach to edge detection. *TPAMI*, 1986.

Carion, N., Massa, F., Synnaeve, G., et al. End-to-end object detection with Transformers. *ECCV*, 2020.

Charpiat, G., Hofmann, M., and Schölkopf, B. Automatic image colorization via multimodal predictions. *ECCV*, 2008.

Chavali, N., Agrawal, H., Mahendru, A., and Batra, D. Object-proposal evaluation protocol is 'gameable'. *CVPR*, 2016.

Chen, X., Zhao, Z., Zhang, Y., et al. FocalClick: towards practical interactive image segmentation. *CVPR*, 2022.

Cheng, B., Schwing, A., and Kirillov, A. Per-pixel classification is not all you need for semantic segmentation. *NeurIPS*, 2021.

Cheng, B., Misra, I., Schwing, A. G., Kirillov, A., and Girdhar, R. Masked-attention mask transformer for universal image segmentation. *CVPR*, 2022.

Chowdhery, A., Narang, S., Devlin, J., et al. PaLM: Scaling language modeling with pathways. *arXiv:2204.02311*, 2022.

da Silva, B., Konidaris, G., and Barto, A. Learning parameterized skills. *ICML*, 2012.

Dosovitskiy, A., Beyer, L., Kolesnikov, A., et al. An image is worth 16×16 words: Transformers for image recognition at scale. *ICLR*, 2021.

Felzenszwalb, P. F. and Huttenlocher, D. P. Efficient graph-based image segmentation. *IJCV*, 2004.

Fitzpatrick, T. B. The validity and practicality of sun-reactive skin types I through VI. *Archives of Dermatology*, 1988.

Forte, M., Price, B., Cohen, S., Xu, N., and Pitié, F. Getting to 99% accuracy in interactive segmentation. *arXiv:2003.07932*, 2020.

Gupta, A., Dollar, P., and Girshick, R. LVIS: A dataset for large vocabulary instance segmentation. *CVPR*, 2019.

Guzman-Rivera, A., Batra, D., and Kohli, P. Multiple choice learning: Learning to produce multiple structured outputs. *NeurIPS*, 2012.

He, K., Chen, X., Xie, S., et al. Masked autoencoders are scalable vision learners. *CVPR*, 2022.

Jia, C., Yang, Y., Xia, Y., et al. Scaling up visual and vision-language representation learning with noisy text supervision. *ICML*, 2021.

Kuznetsova, A., Rom, H., Alldrin, N., et al. The Open Images dataset v4. *IJCV*, 2020.

Li, Y., Mao, H., Girshick, R., and He, K. Exploring plain vision transformer backbones for object detection. *ECCV*, 2022.

Li, Z., Chen, Q., and Koltun, V. Interactive image segmentation with latent diversity. *CVPR*, 2018.

Lin, T.-Y., Goyal, P., Girshick, R., He, K., and Dollár, P. Focal loss for dense object detection. *ICCV*, 2017.

Lin, T.-Y., Maire, M., Belongie, S., et al. Microsoft COCO: Common objects in context. *ECCV*, 2014.

Liu, Q., Xu, Z., Bertasius, G., and Niethammer, M. SimpleClick: Interactive image segmentation with simple vision transformers. *arXiv:2210.11006*, 2022.

Mahadevan, S., Voigtlaender, P., and Leibe, B. Iteratively trained interactive segmentation. *BMVC*, 2018.

Maninis, K.-K., Caelles, S., Pont-Tuset, J., and Van Gool, L. Deep extreme cut: From extreme points to object segmentation. *CVPR*, 2018.

Martin, D., Fowlkes, C., Tal, D., and Malik, J. A database of human segmented natural images. *ICCV*, 2001.

Milletari, F., Navab, N., and Ahmadi, S.-A. V-Net: Fully convolutional neural networks for volumetric medical image segmentation. *3DV*, 2016.

Papadopoulos, D. P., Uijlings, J. R. R., Keller, F., and Ferrari, V. Extreme clicking for efficient object annotation. *ICCV*, 2017.

Pu, M., Huang, Y., Liu, Y., Guan, Q., and Ling, H. EDTER: Edge detection with transformer. *CVPR*, 2022.

Radford, A., Kim, J. W., Hallacy, C., et al. Learning transferable visual models from natural language supervision. *ICML*, 2021.

Ramesh, A., Pavlov, M., Goh, G., et al. Zero-shot text-to-image generation. *ICML*, 2021.

Schumann, C., Ricco, S., Prabhu, U., Ferrari, V., and Pantofaru, C. A step toward more inclusive people annotations for fairness. *AAAI/ACM AIES*, 2021.

Sofiiiuk, K., Petrov, I. A., and Konushin, A. Reviving iterative training with mask guidance for interactive segmentation. *ICIP*, 2022.

Tancik, M., Srinivasan, P., Mildenhall, B., et al. Fourier features let networks learn high frequency functions in low dimensional domains. *NeurIPS*, 2020.

Vaswani, A., Shazeer, N., Parmar, N., et al. Attention is all you need. *NeurIPS*, 2017.

Wu, C.-Y., Johnson, J., Malik, J., Feichtenhofer, C., and Gkioxari, G. Multiview compressive coding for 3D reconstruction. *CVPR*, 2023.

Xie, S. and Tu, Z. Holistically-nested edge detection. *ICCV*, 2015.

Xu, N., Price, B., Cohen, S., Yang, J., and Huang, T. S. Deep interactive object selection. *CVPR*, 2016.

Zhang, W., Pang, J., Chen, K., and Loy, C. C. K-Net: Towards unified image segmentation. *NeurIPS*, 2021.

Zhou, B., Zhao, H., Puig, X., et al. Semantic understanding of scenes through the ADE20K dataset. *IJCV*, 2019.
