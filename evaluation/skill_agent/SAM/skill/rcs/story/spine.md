# Paper Spine — Segment Anything (Kirillov et al., 2023)

**Problem:** Image segmentation lacks a foundation model: existing models are trained for fixed task/dataset combinations and cannot generalize zero-shot to new image distributions or segmentation tasks. {C001}

**Gap:** No large-scale, diverse, promptable segmentation dataset or model exists; masks are not naturally abundant on the internet, so the usual "train on web data" recipe for foundation models does not transfer to segmentation. {C002}

**Question:** Can we define a promptable segmentation task, build a model that generalizes zero-shot to arbitrary downstream segmentation tasks, and collect sufficient training data without relying on pre-existing web-scale mask annotations? {C003}

**Approach:** Co-develop three interdependent components — (1) a promptable segmentation task as both pre-training objective and inference interface; (2) SAM, a three-part model (image encoder + prompt encoder + lightweight mask decoder) designed for amortized real-time prompting; (3) a three-stage data engine that uses the evolving model to collect SA-1B (1.1B masks, 11M images). {C004, C005, C006}

**Key finding:** SAM, evaluated zero-shot, produces high-quality masks often competitive with or exceeding fully supervised methods on novel datasets and tasks (edge detection, object proposals, instance segmentation, text-to-mask); human raters consistently prefer SAM's masks over supervised baselines when judging intrinsic quality. {C007, C008, C009, C010}

**Meaning:** A single, promptable model can serve as a general-purpose segmentation component in larger systems, enabling composable computer vision pipelines without per-task retraining — analogous to how CLIP serves as the vision encoder in image generation systems. {C011}

**Main limit:** SAM is not a fully general segmentation solution: it misses fine structures, is not real-time at inference when the heavy image encoder is included, and lacks a clear prompting strategy for semantic or panoptic segmentation; transfer to domain-specific tasks may still require specialized tools. {C012, L001, L002}
