# Audience Profile

**Mode:** B — Adjacent ML researcher

**Description:**
Machine-learning researchers from subfields other than speech processing (e.g., NLP,
computer vision, RL, reinforcement learning from human feedback). They understand general
deep learning concepts, Transformer architectures, standard supervised and self-supervised
training, sequence-to-sequence models, multitask learning, scaling behavior, distribution
shift, and zero-shot evaluation. They do NOT know: ASR-specific terminology (WER, CER,
hybrid ASR systems, language models in ASR), speech-specific benchmarks (LibriSpeech,
CommonVoice, CHiME, CORAAL, Fleurs, CoVoST2, VoxPopuli), prior ASR model families
(wav2vec, HuBERT, CTC, conformer), or the specific challenges of audio as an input modality.

**What they need explained:**
- Word error rate and its limitations as a metric
- Why evaluating ASR on a single dataset is misleading
- What "weakly supervised" means in the speech context specifically
- The LibriSpeech benchmark and its role as the community reference
- What a Mel spectrogram is (brief)
- Effective robustness as a framing concept
- Voice activity detection and language identification as tasks

**What they already know that we can use as analogies:**
- CLIP and image-text pretraining (analogous to Whisper's internet data approach)
- GPT-2/GPT-3 style language models (shared tokenizer)
- Multi-task learning and transfer learning in NLP
- Scaling laws from LLMs (data size vs. performance curves)
- Shortcut learning / spurious correlations in neural networks

**Binding personas:**
1. NLP researcher familiar with CLIP-style pretraining, curious about the speech equivalent
2. Computer vision researcher asking whether weak supervision at scale works as well for audio as for images
