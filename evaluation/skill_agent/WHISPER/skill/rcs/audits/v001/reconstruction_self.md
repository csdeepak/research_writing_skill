# Reconstruction Self-Test — v001

**Method:** Q1–Q12 answered from draft alone, compared with spine and claim map.

| Q# | Question | Answerable? | Notes |
|----|----------|-------------|-------|
| Q1 | What is the research problem? | Yes | ASR robustness gap |
| Q2 | Why does it matter? | Yes | Real-world deployment failure |
| Q3 | What was known before? | Yes | Unsupervised pretraining, multi-domain supervised |
| Q4 | What was the gap? | Yes | Weak supervision not scaled past ~30k hours for speech |
| Q5 | What did they do? | Yes | 680k hours, encoder-decoder Transformer, multitask tokens |
| Q6 | What was the key finding? | Yes | 55.2% RER, human-level robustness |
| Q7 | How robust is the finding? | Yes | 13 datasets, ablations, negative results |
| Q8 | What does it mean? | Yes | Distributional coverage drives robustness |
| Q9 | What are the limitations? | Yes | Section 6.4 |
| Q10 | What next? | Yes | Low-resource data, long-form decoding, fine-tuning |
| Q11 | How does it relate to other work? | Yes | CLIP, BiT, wav2vec |
| Q12 | One-day memory (spine test) | Yes | Whisper: 680k hours weakly supervised, 55.2% RER, human-level robustness |

**All 12 pass.**

## Defects found

1. **Effective robustness table is incomplete**: Shows 11 OOD rows; the paper's Table 2 has 14 total datasets (LibriSpeech clean reference + 13 OOD including Fleurs En, TED-LIUM, VoxPopuli En that are missing). Fix: add all 14 rows.

2. **CoVoST2 SOTA claim needs caveat**: Draft says "new state of the art" but the paper explicitly says "We caution that we do use a simple text standardizer for this result which prevents direct comparison or claims of SOTA performance." Fix: include the caveat.

3. **Human-level comparison nuance**: Phrase "within measurement noise" is not supported by evidence (no CI reported). Fix: use only language directly from the evidence.

4. **Claim tags**: Must be stripped in final paper.md.

## Verdict: Minor fixes required. No structural defects.
