# Gold Account v1 — WHISPER (verified)

Snapshot-only factual ledger. Sources: `evaluation/external_projects/WHISPER/snapshot/paper.txt` (arXiv 2212.04356v1, pdftotext) and `README__openai__whisper.md` (pinned commit `86098128c0b4f24f0e2aa2994de830614b474227`). The paper is authoritative for research claims. The README is authoritative only for artifact facts (install, license, currently offered checkpoints). "L##" = paper.txt line number. Numbers are copied exactly. Where the verifier computed something, it is marked "(verifier arithmetic)".

## Changes from draft
Issue numbers refer to `VERIFICATION.md`.

1. **(#1, high)** Removed the invented LibriSpeech conflict. The prose "2.5" is Large-v2 test-clean WER with beam search + temperature fallback (Table 9). The 2.7 in Table 2 is the greedy value (Table 8). No "2.7–4.2 range" exists for this cell.
2. **(#2)** The 55.2% average relative error reduction is taken over the **13** non-reference rows of Table 2 (12 OOD datasets + LibriSpeech test-other), not over "12 OOD datasets". Added the average WERs 29.3 (wav2vec 2.0) vs 12.8 (Whisper).
3. **(#3)** Deleted the Table 2 "Large (no LM)" ambiguity. That label is the wav2vec 2.0 column; the Whisper column is explicitly "Large V2".
4. **(#4)** The Table 3 MLS row is no longer attributed column by column. Only Whisper 7.3 is certain.
5. **(#5)** Long-form heuristics: the average is unchanged after temperature fallback and after the initial-timestamp constraint. The claim that "each heuristic reduces average WER" is corrected.
6. **(#6)** Diarization removed from the list of things Whisper's format replaces.
7. **(#7)** Deleted the unsupported interpretation that noise robustness comes from data diversity.
8. **(#8)** Research gap corrected. Prior labeled-data work reached 162,000 h (Narayanan et al., 2018). "No prior work combined multilingual/multitask" was dropped as drafter extrapolation.
9. **(#9)** Added the §4.3 multitask/multilingual transfer experiment.
10. **(#10, #11)** Added the missing author-stated limitations and hypotheses: normalizer overfitting risk, MLS standardizer caveat, heuristics as "workaround", LID coverage gap, negative transfer at small scale, strong-decoder hypothesis.
11. **(#12–#22)** Minor fixes:
    - strength labels (Q10a and Q12b changed to derived);
    - LID 13.6 vs 13.2 note;
    - removed the out-of-snapshot venue row;
    - README "six model sizes" conflict;
    - line locators;
    - SpeechStew attribution;
    - medium-model qualifier for Table 6;
    - Table 17 hyperparameters;
    - CoVoST2 68,000 h interpretation;
    - Q8a comparator wording.

---

## 1. Problem
Speech recognition systems built on unsupervised pre-trained audio encoders (e.g., Wav2Vec 2.0) lack an equivalently performant decoder, so they need a dataset-specific fine-tuning stage to perform a task such as speech recognition (§1, L11). Fine-tuning "can still be a complex process requiring a skilled practitioner" (L11) and risks learning brittle, dataset-specific patterns (L15). The authors' goal: a system that works reliably "out of the box" across environments "without requiring supervised fine-tuning of a decoder for every deployment distribution" (L16).

## 2. Motivation
- Fine-tuning can exploit dataset-specific quirks. Radford et al. (2021) saw a 9.2% ImageNet accuracy gain from fine-tuning with no average improvement on seven other datasets, and a "superhuman" model on one dataset can make many basic errors on another (L15).
- Supervised multi-dataset training (Narayanan et al., 2018; Likhomanenko et al., 2020; Chan et al., 2021) improves robustness, but high-quality supervised data is limited. SpeechStew mixes 7 datasets totalling 5,140 hours, tiny compared with the 1,000,000 hours of unlabeled speech in Zhang et al. (2021) (L17).
- Weakly supervised speech datasets reached 10,000 and 30,000 hours (Chen et al., 2021; Galvez et al., 2021; L18, L24). In computer vision, larger weakly supervised datasets improved robustness and generalization (L24).

## 3. Research gap
Recent weakly supervised speech datasets "are only a few times larger than the sum of existing high-quality datasets and still much smaller than prior unsupervised work" (L25). The authors close this gap by "scaling weakly supervised speech recognition the next order of magnitude to 680,000 hours of labeled audio data" (L25), and broaden scope beyond English-only recognition to multilingual and multitask training (L26). (Context: the Related Work section notes Narayanan et al. (2018) trained on 162,000 hours of labeled audio via semi-supervised pre-training, L1005.)

## 4. Research question / objective
Study "the capabilities of speech processing systems trained simply to predict large amounts of transcripts of audio on the internet" (L8). Test whether models trained at this scale "transfer well to existing datasets zero-shot, removing the need for any dataset-specific fine-tuning" (L25). Test whether joint multilingual and multitask training has drawbacks (L26, §4.3).

## 5. System / method
- **Data construction (§2.1, L30–45):**
  - Predict raw transcript text with no significant standardization, which removes the need for a separate inverse-text-normalization step (L30–33).
  - Audio paired with transcripts from the internet (L34).
  - Heuristics remove machine-generated transcripts, e.g., all-uppercase/all-lowercase text and never including commas (L35).
  - An audio language detector (fine-tuned from a prototype model on VoxLingua107) is checked against the transcript language via CLD2. Mismatched pairs are dropped, except that an English transcript becomes an X→en translation example (L36).
  - Fuzzy de-duplication of transcripts (L36).
  - 30-second segments; no-speech segments are kept with sub-sampled probability and used as VAD training data (L37).
  - A second filtering pass uses an initial model's error rate per data source plus manual inspection (L38–44).
  - Transcript-level de-duplication against evaluation sets "at higher risk of overlap, namely TED-LIUM 3" (L45).
- **Model (§2.2, L47–48):**
  - Off-the-shelf encoder–decoder Transformer, chosen "to avoid confounding our findings with model improvements".
  - Input: 16,000 Hz audio; 80-channel log-magnitude Mel spectrogram with 25 ms windows and 10 ms stride; globally scaled to [-1, 1] with ~zero mean.
  - Encoder: stem of 2 conv layers (filter width 3, GELU; the second has stride 2); sinusoidal position embeddings; pre-activation residual blocks; final layer norm.
  - Decoder: learned position embeddings; tied input-output token embeddings.
  - Encoder and decoder have the same width and depth.
  - Tokenizer: GPT-2 byte-level BPE for English-only models; vocabulary refit (same size) for multilingual models.
- **Multitask format (§2.3, L50–53):**
  - Goal: have a single model perform the whole speech-processing pipeline, not only core recognition. The tasks named are transcription, translation, voice activity detection, alignment and language identification (L52). Speaker diarization is named only as a component of typical pipelines and is not a Whisper task.
  - Decoder token sequence: optional previous-text context (added with some probability; loss masked), then `<|startoftranscript|>`, then a language token (99 total, from the VoxLingua107 model), `<|nospeech|>` if there is no speech, then `<|transcribe|>` or `<|translate|>`, then `<|notimestamps|>` or interleaved timestamp tokens (20 ms quantization), then text, then `<|endoftranscript|>`.
- **Training (§2.4, L212–241; Appendix F, L2127–2155):**
  - Data parallelism; FP16 with dynamic loss scaling; activation checkpointing.
  - Optimizer: AdamW (β1 0.9, β2 0.98, ε 10⁻⁶, weight decay 0.1); Gaussian Fan-In init; max grad norm 1.0.
  - Schedule: linear LR decay to zero after 2,048 warmup updates; batch 256 segments; 1,048,576 (2^20) updates, "between two and three passes over the dataset".
  - Data handling: speechless-audio subsample factor 10×; condition-on-prior-text rate 50% (Table 17).
  - No data augmentation or regularization for the original models.
  - A brief fine-tune on transcripts without speaker annotations removes speaker-name guessing (L215, L241).
- **Large V2 (fn. 3, L216; Table 18):**
  - Trained for 2.5× more epochs, adding SpecAugment, Stochastic Depth and BPE Dropout.
  - Table 18 settings: 655,360 updates, batch 1024, BPE dropout 0.1, stochastic depth 0.1, SpecAugment "LibriSpeech Basic".
  - "Reported results have been updated to this improved model unless otherwise specified."

## 6. Architecture
Table 1 (L222–237):

| Model | Layers | Width | Heads | Parameters |
|---|---|---|---|---|
| Tiny | 4 | 384 | 6 | 39M |
| Base | 6 | 512 | 8 | 74M |
| Small | 12 | 768 | 12 | 244M |
| Medium | 24 | 1024 | 16 | 769M |
| Large | 32 | 1280 | 20 | 1550M |

Max learning rates (Table 19, L2149–2155): Tiny 1.5×10⁻³, Base 1×10⁻³, Small 5×10⁻⁴, Medium 2.5×10⁻⁴, Large 1.75×10⁻⁴, Large V2 2.0×10⁻⁴.

**README-only artifact facts (not paper claims):**
- The README says "There are six model sizes" (README L60).
- It lists `turbo` (809 M, "an optimized version of `large-v3`", "not trained for translation tasks") and shows `large-v3`/`large-v2` per-language figures (README L64–88).
- The paper has five sizes plus Large V2 and never mentions `turbo` or `large-v3`. This is repo evolution after the paper; no paper result applies to those checkpoints.
- The README states that code and weights are MIT-licensed (README L160).

## 7. Dataset / data
- **Training:** 680,000 hours in total; 117,000 hours cover 96 non-English languages; 125,000 hours are X→en translation (L26). Figure 11 gives 65% English ASR (438,218 h), 17% multilingual ASR (117,113 h) and 18% translation (125,739 h) (L2101–2103). Per-language hours in Figure 11 are extraction-damaged: NOT IN SNAPSHOT (legibly). The dataset is not released; only models and inference code are (L8, L27).
- **Evaluation datasets (Appendix A, L1179–1222):**
  - Short-form English: LibriSpeech test-clean/test-other, TED-LIUM 3, Common Voice 5.1 (en), Artie, CallHome and Switchboard (LDC2002S09/LDC2002T43), WSJ (LDC93S6B/LDC94S13B), CORAAL (231 interviews), CHiME-6, AMI-IHM/AMI-SDM1.
  - Long-form: TED-LIUM 3 (11 full talks), Meanwhile (64 segments), Rev16 (16 of 30 episodes), Kincaid46 (46 files; a 25-file human-comparison subset), Earnings-21/22, CORAAL (231 full interviews).
  - Multilingual: MLS, Fleurs, VoxPopuli (16 languages incl. English), Common Voice 9, CoVoST 2.
- **Comparison models:** 14 HuggingFace checkpoints, "all … entirely or partly trained on LibriSpeech" (L1224–1228).

## 8. Experimental setup
- **Zero-shot protocol:** no training split of any evaluation dataset is used (L244).
- **WER normalization:** WER is computed after the authors' text normalizer, developed "through iterative manual inspection" (L247; Appendix C). §4.4 compares it with FairSpeech's normalizer.
- **Effective robustness (Taori et al., 2020):** LibriSpeech is the reference; 12 other academic datasets are out-of-distribution (L278). Table 2 pairs Whisper Large V2 with wav2vec 2.0 Large (no LM), the supervised model closest on LibriSpeech test-clean (L395).
- **Human reference (Figure 2):** one human ("Alec") (L259, L276).
- **Multilingual ASR:** MLS and VoxPopuli (Table 3), plus Fleurs with log-log regression against per-language training hours (L622).
- **Translation:** CoVoST2 X→en (Table 4), plus Fleurs re-purposed with English transcripts as references (L711).
- **Language ID:** Fleurs, 102 languages; Whisper has no training data for 20 of them (L715).
- **Additive noise:** white noise and pub noise (Audio Degradation Toolbox) at varying SNR. Compared against 14 LibriSpeech-trained models, 2 of which are NVIDIA STT models trained on a SpeechStew-like mixture (L722).
- **Long-form:** 7 datasets, compared with 4 commercial services ("default English transcription settings as of September 1st, 2022") and NVIDIA STT Conformer-CTC Large via buffered `FrameBatchASR` (L727–758).
- **Human comparison:** 25 Kincaid46 recordings, 5 professional transcription services (1 computer-assisted, 4 purely human) (L760).
- **Model-size scaling:** Figure 8 (L792).
- **Dataset-size scaling:** medium-sized models trained on 0.5%, 1%, 2%, 4% and 8% subsamples versus the full dataset. Early stopping on validation loss; evaluated with an EMA of parameters (smoothing 0.9999) (L794).
- **Multitask/multilingual transfer (§4.3, L895–932):** English-only models are compared with joint multitask/multilingual models on zero-shot English ASR. Results are adjusted for FLOPs spent on English ASR, since only 65% of compute goes to that task in joint training.
- **Long-form decoding heuristics (§4.5, L968–1000):**
  - Beam search with 5 beams (log-probability score).
  - Temperature starts at 0 and rises by 0.2 up to 1.0 when the average log-probability is < −1 or the gzip compression rate is > 2.4.
  - Previous-window text conditioning is used only when the temperature is < 0.5.
  - VAD: no-speech probability threshold 0.6 combined with the average log-probability threshold −1.
  - The initial timestamp is constrained to 0.0–1.0 s.

## 9. Metrics
- WER, based on string edit distance (L246), computed after text normalization.
- For Chinese, Japanese, Thai, Lao and Burmese, a space is inserted between characters, "effectively measuring the character error rate" (L1247).
- BLEU for translation (Tables 4, 14, 15; Figure 4).
- Accuracy for language ID (Table 5).
- r² of log-log fits (Figures 3 and 4).
- Relative error reduction (RER) in Table 2.

## 10. Results (exact numbers)
- **LibriSpeech test-clean, best zero-shot Whisper (Large V2):**
  - "2.5" (L279) = Table 9 value, beam search + temperature fallback (L1370–1372).
  - Greedy value 2.7 (Table 8, L1269), the figure used in Table 2.
  - Smallest model (39M): 6.7 test-clean WER, "roughly competitive with the best supervised LibriSpeech model when evaluated on other datasets" (L395).
- **Table 2 (L283–393):**
  - wav2vec 2.0 Large (no LM) vs Whisper Large V2, both 2.7 on LibriSpeech Clean (RER 0.0).
  - Averages over the other 13 rows (12 OOD datasets + LibriSpeech test-other): WER 29.3 vs 12.8, average RER **55.2%**.
  - Per-dataset RER: Artie 74.7, Common Voice 69.9, Fleurs En 69.9, TED-LIUM 61.9, CHiME6 61.2, VoxPopuli En 59.2, CORAAL 54.5, AMI IHM 54.3, Switchboard 51.2, CallHome 49.4, WSJ 49.4, AMI SDM1 46.2, LibriSpeech Other 16.1. Row alignment was reconstructed via Table 8 (verifier arithmetic reproduces 29.3/12.8/55.2).
- **Table 3 (L604–617):**
  - MLS WER: Zero-shot Whisper 7.3. Prior-work values 10.9 and 9.7 appear in the row, but their column attribution is not recoverable from the extraction (most consistent with the prose: XLS-R 10.9, mSLAM-CTC 9.7).
  - Authors' caveat: the simple text standardizer "prevents direct comparison or claims of SOTA performance" (L619).
  - VoxPopuli WER: VP-10K+FT 15.3, XLS-R (1B) 10.6, mSLAM-CTC (2B) 9.1, Maestro 8.1, Whisper 13.6. Whisper "only beats the VP-10K+FT baseline" (L619).
- **Fleurs ASR (L622):** r² = 0.83 between log WER and log training hours per language; the regression estimates WER halves for every 16× more training data. Whisper has ASR training data in 75 languages (L622).
- **Table 4 (L630–663), CoVoST2 X→en BLEU (High / Mid / Low / All):**

  | Model | High | Mid | Low | All |
  |---|---|---|---|---|
  | XMEF-X | 34.2 | 20.2 | 5.9 | 14.7 |
  | XLS-R (2B) | 36.1 | 27.7 | 15.1 | 22.1 |
  | mSLAM-CTC (2B) | 37.8 | 29.6 | 18.5 | 24.8 |
  | Maestro | 38.2 | 31.3 | 18.4 | 25.2 |
  | Zero-shot Whisper | 36.2 | 32.6 | 25.2 | 29.1 |

  - "New state of the art of 29.1 BLEU zero-shot without using any of the CoVoST2 training data"; +6.7 BLEU over mSLAM on the lowest-resource grouping; no improvement over Maestro and mSLAM on high-resource languages (L710).
- **Fleurs translation (L711–713):**
  - r² = 0.24.
  - Welsh (CY) scores 13 BLEU despite "supposedly having 9,000 hours" of translation data, which ranks 4th overall.
- **Table 5 (L665–673), Fleurs LID accuracy:**
  - w2v-bert-51 (0.6B) 71.4, mSLAM-CTC (2B) 77.7, Whisper 64.5.
  - Prose: "underperforms the supervised SOTA by 13.6%" (L715). The table difference is 13.2 points (verifier arithmetic); the table values are authoritative.
  - Upper bound 80.4% (no training data for 20 of 102 languages); 80.3% on the 82 overlapping languages (L715).
- **Noise (§3.7, L722; Figure 5 caption L707):**
  - Many models beat Whisper at low noise (40 dB SNR).
  - All models fall below Whisper under pub noise at SNR < 10 dB.
  - Exact curve values: NOT IN SNAPSHOT.
- **Long-form (§3.8, Figure 6):**
  - Whisper "performs better than the compared models on most datasets, especially on the Meanwhile dataset" (L758).
  - It outperforms NVIDIA STT on all datasets (Figure 6 caption, L755).
  - Per-system aggregate WERs are figure-only: NOT IN SNAPSHOT.
  - Whisper's own long-form WERs are in Table 16 (L1917, header order extraction-damaged).
- **Human comparison (§3.9, L760):**
  - The computer-assisted service has the lowest aggregate WER, "1.15% point better than Whisper's".
  - Pure-human performance is "only a fraction of a percentage point better than Whisper's".
  - Exact values: NOT IN SNAPSHOT (Figure 7).
- **Model scaling (§4.1, L792):** performance keeps improving with size for multilingual ASR, translation and LID. English ASR shows diminishing returns. Values: NOT IN SNAPSHOT (Figure 8).
- **Table 6 (L875–887), medium-sized models (hours → English WER / Multilingual WER / X→en BLEU):**

  | Hours | English WER | Multilingual WER | X→en BLEU |
  |---|---|---|---|
  | 3405 | 30.5 | 92.4 | 0.2 |
  | 6811 | 19.6 | 72.7 | 1.7 |
  | 13621 | 14.4 | 56.6 | 7.9 |
  | 27243 | 12.3 | 45.0 | 13.9 |
  | 54486 | 10.9 | 36.4 | 19.2 |
  | 681070 | 9.9 | 29.2 | 24.8 |

  - "All increases in the dataset size result in improved performance on all tasks" (L889).
  - The full dataset (another 12.5×) gives "only a further 1 point drop" in English WER (L889).
  - Multilingual WER follows a power law up to 54,000 h, then improves only 7 more points (L890).
- **Multitask transfer (§4.3, L896–932):**
  - Small joint models show negative transfer (they underperform English-only models at equal compute).
  - Joint models "scale better", and the largest outperform English-only models, even without compute adjustment ("slightly").
  - Values: NOT IN SNAPSHOT (Figure 9).
- **Text normalization (§4.4, L934):** the authors' normalizer and FairSpeech's perform similarly on most datasets. On WSJ, CallHome and Switchboard, the authors' normalizer lowers Whisper's WER significantly more.
- **Table 7 (L976–998), average long-form WER over 7 datasets:**

  | Heuristic added | Average WER |
  |---|---|
  | Greedy | 11.0 |
  | + Beam search | 10.6 |
  | + Temperature fallback | 10.6 (unchanged) |
  | + VAD | 10.2 |
  | + Previous-text conditioning | 10.0 |
  | + Initial timestamp constraint | 10.0 (unchanged) |

  Per-dataset changes are uneven. For example, previous-text conditioning raises Meanwhile WER from 4.61 to 6.16.

## 11. Supported claims (directly measured/observed)
- Zero-shot Whisper Large V2 matches wav2vec 2.0 Large (no LM) on LibriSpeech test-clean (2.7 vs 2.7) but is far better on the other datasets (Table 2). More broadly, zero-shot Whisper models outperform all benchmarked LibriSpeech models by large amounts on other datasets (L279).
- New zero-shot SOTA of 29.1 BLEU on CoVoST2 X→en, All (Table 4).
- Every dataset-size increase in the tested range improves English WER, multilingual WER and X→en BLEU (Table 6).
- The full long-form heuristic stack lowers average WER from 11.0 to 10.0. Temperature fallback and the initial-timestamp constraint do not change the average (Table 7).
- Whisper's Fleurs LID accuracy (64.5%) is below prior supervised results (Table 5).
- Whisper is more robust than LibriSpeech-trained models under pub noise at SNR < 10 dB (§3.7, Figure 5).
- Joint multitask/multilingual training shows negative transfer for small models and positive transfer for the largest models (§4.3, Figure 9).

## 12. Derived claims (computed/comparative)
- 55.2% is the average of per-dataset RERs in Table 2 (13 non-reference rows).
- The r² values of 0.83 (ASR) and 0.24 (translation) are regression statistics. "WER halves per 16×" is read from the fitted regression coefficient (L622).
- "Roughly competitive with the best supervised LibriSpeech model" for the 39M model is a cross-model comparison (L395).
- "Very close to human-level accuracy" (L760) and "roughly match their accuracy and robustness" (L395) are the authors' conclusions from one human in Figure 2 and 25 recordings in Figure 7.
- Whisper's "zero-shot" results are "often competitive with prior fully supervised results" (L8). This is a synthesis across benchmarks.

## 13. Interpretations (authors' explanations)
- The in-distribution vs out-of-distribution human/machine gap comes from "conflating different capabilities being measured" (L251).
- VoxPopuli underperformance "could be due to" other models using that distribution for unsupervised pre-training, plus its larger supervised data (L619).
- Fleurs outliers (HE, TE, ZH, KO) "could be due to" linguistic distance, a poor BPE fit, or data-quality variation (L622).
- Diminishing English ASR returns with model and data scale "could be due to saturation effects from approaching human-level performance" (L792, L889).
- The CoVoST2 SOTA is attributed to 68,000 hours of X→en pre-training data for those languages vs 861 hours in CoVoST2 (L710).
- The low Fleurs translation r² is "partly caused by" language-ID errors. The Welsh anomaly is traced by inspection to English audio misclassified as Welsh (L713).
- LID underperformance is "partially due to" the 20 languages absent from training (L673, L715).

## 14. Hypotheses / speculation
- Diminishing returns from 54,000 h to 680,000 h could mean the models are under-trained relative to dataset size, or that dataset-size scaling gains are nearing their end. "Further analysis is needed" (L893).
- "We suspect that Whisper's robustness is partially due to its strong decoder." It is "currently unclear" whether the benefit comes from the encoder, the decoder or both. Proposed ablations: a decoder-less CTC model, or wav2vec 2.0 combined with an LM (L1018–1020).
- Fine-tuning on high-quality supervised data and/or reinforcement learning could reduce long-form decoding errors (L1015).
- Fine-tuning would likely improve results where high-quality supervised data exists (L1017).
- Adding unsupervised pre-training or self-teaching objectives could further improve results; this is untested (L1021).

## 15. Limitations
**Author-stated (§6, L1008–1021):**
- Decoding: stubborn long-form errors remain: repeat loops, missing first/last words, and "complete hallucination" (L1015).
- Low-resource languages: performance is still poor, and most languages have < 1000 h because the data pipeline is English-centric (L1016).
- Only zero-shot transfer was studied; fine-tuning was not (L1017).
- It is unclear which component (encoder or decoder) drives robustness (L1018).
- No unsupervised pre-training or self-teaching was used (L1021).

**Author-stated elsewhere:**
- 30-second context: "cannot consume longer audio inputs at once". Long-form results rely on buffered windowing plus heuristics that "serve as a workaround for the noisy predictions of the model" (L724, L1000).
- The text normalizer, developed jointly with Whisper, risks "overfitting to the transcription style of Whisper models" (L239). §4.4 finds it favours Whisper on WSJ, CallHome and Switchboard (L934).
- The MLS comparison uses a simple standardizer that "prevents direct comparison or claims of SOTA performance" (L619).
- Commercial long-form systems may have been trained on these public datasets, so "these results may not be accurately reflecting the relative robustness" (L758).
- LID is heavily disadvantaged: Whisper has no training data for 20 of the 102 Fleurs languages (L715).
- Small joint multitask/multilingual models suffer negative transfer (L896).

**Scope boundary (verifier/drafter-derived, not author-stated):**
- Contamination de-duplication is explicitly reported only for TED-LIUM 3 (L45).

## 16. Actual contribution
"Whisper suggests that scaling weakly supervised pre-training has been underappreciated so far in speech recognition research … simply training on a large and diverse supervised dataset and focusing on zero-shot transfer can significantly improve the robustness of a speech recognition system" (L1023), without self-supervision or self-training.

Concretely, the work contributes:
- a family of encoder–decoder Transformers (39M–1550M) trained on 680,000 hours of weakly supervised, multilingual, multitask data;
- zero-shot results that are "often competitive with prior fully supervised results" (L8);
- far stronger out-of-distribution robustness than LibriSpeech-supervised models;
- near-human English ASR accuracy per the authors;
- released models and inference code (L8, L27).

## 17. Unsupported or weakly supported claims
- "WER halves per 16×" rests on one log-log fit (r² 0.83) on Fleurs, with no confidence interval reported (L622).
- Noise robustness is shown only for white noise and pub noise from one toolbox (L722). Nothing is claimed beyond these.
- The commercial-ASR comparison is self-qualified by the authors as possibly confounded (L758).
- The Welsh explanation rests on inspection of "the majority" of the data. The affected fraction is NOT IN SNAPSHOT (L713).
- The authors' prose says each long-form heuristic "incrementally reduces the WER overall" (L1000). Their own Table 7 shows two steps with no change in the average.
- The LID gap "13.6%" (L715) does not match Table 5 arithmetic (13.2).
- Footnote 3 (L216) makes Large V2 the default "unless otherwise specified". Tables and figures other than Table 2 and Figure 8 do not always label the checkpoint.

## 18. Claim → evidence → source table

| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| Trained on 680,000 h of weakly supervised multilingual multitask data | measured (design fact) | dataset statement | L25–26 | "scaling weakly supervised speech recognition the next order of magnitude to 680,000 hours of labeled audio data" |
| 117,000 h cover 96 non-English languages; 125,000 h X→en | measured (design fact) | dataset composition | L26 | "117,000 hours cover 96 other languages. The dataset also includes 125,000 hours of X→en translation data" |
| 55.2% average RER vs wav2vec 2.0 Large (no LM) over Table 2's 13 non-reference rows; avg WER 29.3 vs 12.8 | measured / derived | Table 2 | L285–393; L395 | "achieves an average relative error reduction of 55.2% when evaluated on other speech recognition datasets" |
| LibriSpeech test-clean 2.5 (beam+fallback) / 2.7 (greedy), Large V2 | measured | Tables 9 / 8, prose | L279; L1372; L1269 | "relatively unremarkable LibriSpeech clean-test WER of 2.5" |
| New SOTA 29.1 BLEU CoVoST2 X→en, zero-shot | measured | Table 4 | L654; L710 | "achieve a new state of the art of 29.1 BLEU zero-shot" |
| Fleurs ASR r² = 0.83; WER halves per 16× data | derived | regression | L622 | "strong squared correlation coefficient of 0.83" |
| Fleurs LID 64.5% vs 77.7% / 71.4% | measured | Table 5 | L665–673 | "not competitive with prior supervised results on Fleurs" |
| Dataset scaling 3,405 h → 681,070 h (medium models) | measured | Table 6 | L875–887 | "All increases in the dataset size result in improved performance on all tasks" |
| Long-form avg WER 11.0 → 10.0; two steps unchanged | measured | Table 7 | L976–998 | "incrementally reduces the WER overall, but not evenly across the dataset" |
| Negative transfer small models, positive at largest scale | measured (figure-only values) | Figure 9, §4.3 | L896–932 | "multilingual and multitask models scale better and for our largest experiments outperform their English-only counterparts" |
| Human/machine gap = in- vs out-of-distribution skill | interpretation | §3.3 | L251 | "two quite different abilities are being measured due to a difference in train data" |
| Encoder vs decoder contribution unresolved | hypothesis | §6 | L1018 | "currently unclear to what degree the benefits of Whisper stem from training its encoder, decoder, or both" |
| 30-second input limit | limitation (author-stated) | §3.8 | L724 | "trained on 30-second audio chunks and cannot consume longer audio inputs at once" |
| Normalizer overfitting risk | limitation (author-stated) | §3.2/§4.4 | L239; L934 | "risk of overfitting to the transcription style of Whisper models" |
| Pure-human WER only fractionally better than Whisper (value not in snapshot) | measured (figure-only) | Figure 7 prose | L760 | "only a fraction of a percentage point better than Whisper's" |
| README lists `turbo` / `large-v3` / "six model sizes", absent from paper | artifact fact (README-only; conflict) | README model table | README L60–76 | "the turbo model is an optimized version of large-v3" |
