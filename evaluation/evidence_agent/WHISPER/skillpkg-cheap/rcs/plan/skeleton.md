# Research skeleton (one sentence per paragraph slot)

## Abstract
Robust, general-purpose speech recognition/translation without per-dataset fine-tuning is the target; the method is a single Transformer trained on 680,000 hours of weakly supervised, multitask, multilingual internet audio-text data; the key finding is large, consistent zero-shot robustness and accuracy gains (55.2% relative error reduction, 29.1 BLEU SOTA, noise robustness) that scale with data and model size; the main limitation is uneven language coverage and a weaker data-translation correlation.

## Introduction
1. State the problem: benchmark-tuned ASR models are brittle outside their training distribution (N01,N02).
2. State what is known: unsupervised pre-training scales but leaves fine-tuning necessary; multi-dataset supervised pooling improves generality modestly (N03,N04).
3. State the gap: scaling weak supervision itself, at unsupervised-pretraining scale, is unexplored (N05).
4. State the RQ and approach in one sentence each (N06,N07).
5. State the contribution and give a one-paragraph map of the paper.

## Related Work
1. Self-supervised/unsupervised audio pre-training (wav2vec 2.0) needs a fine-tuned decoder per task (N03).
2. Multi-dataset supervised combination work (SpeechStew; Narayanan et al.; Likhomanenko et al.) improves generality without matching Whisper's data scale (N04).
3. Weakly supervised approaches at earlier, smaller scale set the precedent Whisper extends by an order of magnitude (N05).

## Method
1. Data collection and lightweight, mostly automated filtering, 680,000 hours total, composition breakdown (N09).
2. Task format: single text-based multitask decoder output (transcription/translation/timestamps/language ID) (N08).
3. Architecture and model family (Tiny-Large) (N08).
4. Training procedure: no augmentation/regularization, reliance on data diversity, batch/update schedule (N09).

## Experimental Setup
1. Zero-shot evaluation protocol: no fine-tuning on any target benchmark.
2. Benchmarks used: LibriSpeech, 12-dataset average, Fleurs, CoVoST2, VoxPopuli, MLS, long-form set, noise robustness set, human-comparison subset.
3. Text normalization caveat and the independent-normalizer check (N25).
4. Controlled scaling studies: dataset-size sweep and model-size sweep design (N10,N11).

## Results
1. LibriSpeech test-clean headline number, framed against the robustness claim (N12).
2. Cross-dataset robustness: 55.2% relative error reduction; interpretation (N13,N15).
3. Noise robustness vs 14 baselines (N14).
4. Multilingual recognition scaling correlation r²=0.83 (N16).
5. Translation: weaker correlation r²=0.24 but zero-shot SOTA 29.1 BLEU; why weaker (N17,N18).
6. Negative results: VoxPopuli underperformance; Fleurs language ID underperformance (N19).
7. Dataset-size scaling curves across three tasks (N20).
8. Model-size scaling (N21).
9. Multitask/multilingual transfer crossover (N22).
10. Long-form transcription vs open-source and vs human-level (N23).
11. Long-form decoding heuristics ablation (N24).

## Discussion / Limitations
1. Interpret the overall pattern: breadth of weak supervision substitutes for fine-tuning (N27).
2. English-heavy data and uneven language coverage (N25).
3. Text-normalizer risk and mitigation (N25).
4. Open question: encoder vs decoder source of robustness; residual structural errors (N26).
5. Future directions the authors flag (N28).

## Conclusion
Restate RQ, key finding, and implication in compressed form; end on scaling weak supervision as an underappreciated direction (N27).
