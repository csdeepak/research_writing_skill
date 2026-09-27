# Audience Profile

**Mode:** B — Adjacent researcher

**Description:** Machine-learning researchers from other subfields (NLP, reinforcement learning, generative models, etc.) who know general ML, deep learning, standard evaluation practice, and statistics, but are not specialists in computer vision segmentation subfield terminology, datasets, or prior work.

**Assumed knowledge:**
- Transformer architecture (self-attention, cross-attention, encoders, decoders)
- Vision Transformers (ViT) at high level
- Foundation models and the NLP prompting paradigm (GPT, CLIP at high level)
- Standard evaluation metrics (IoU, precision, recall, AP)
- Transfer learning and zero-shot learning concepts
- Standard supervised training pipelines
- MAE (masked autoencoders) concept
- Contrastive learning (CLIP)

**Terms requiring definition in the paper:**
- Image segmentation (pixel-level mask)
- Instance vs. semantic vs. panoptic segmentation
- Interactive segmentation
- mIoU (mean Intersection over Union)
- Average recall (AR) in proposal generation
- ODS / OIS in edge detection
- Promptable segmentation task
- SA-1B

**Binding personas (for evaluation):**
1. An NLP researcher who understands GPT-style prompting but has never worked with segmentation datasets
2. A generative model researcher (diffusion/GAN) who uses segmentation as a preprocessing step
3. A reinforcement learning researcher interested in composable perception modules
