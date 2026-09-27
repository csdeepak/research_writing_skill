# Gold Account Draft — WHISPER

Snapshot-only factual ledger, built from `evaluation/external_projects/WHISPER/snapshot/paper.txt` (arXiv 2212.04356v1, pdftotext) and `README__openai__whisper.md` (pinned commit `86098128c0b4f24f0e2aa2994de830614b474227`). Per task rules: **the paper is authoritative for research claims; the README is authoritative only for artifact facts (install, license, model names as currently offered).** "L##" = paper.txt line number. Numbers are copied exactly as they appear; no rounding, no inference across sources.

## 1. Problem
Speech recognition systems built on unsupervised pre-trained audio encoders (e.g., Wav2Vec 2.0) lack an equivalently high-quality decoder, so they require a dataset-specific fine-tuning stage to be usable, which limits their usefulness, requires skilled practitioners, and risks overfitting to dataset-specific patterns rather than learning generalizable speech recognition (§1, L10–16). The goal stated by the authors: "The goal of a speech recognition system should be to work reliably 'out of the box' in a broad range of environments without requiring supervised fine-tuning of a decoder for every deployment distribution" (§1, L16).

## 2. Motivation
- Fine-tuned models can achieve "superhuman" performance on a single dataset while making basic errors on other datasets, because they exploit dataset-specific quirks rather than learning genuinely general skills (§1, L15, citing Radford et al. 2021's finding of a 9.2% ImageNet fine-tuning accuracy gain with no improvement on 7 other datasets).
- Prior multi-dataset supervised speech recognition efforts (Narayanan et al. 2018; Likhomanenko et al. 2020; Chan et al. 2021's SpeechStew) showed higher robustness from combining datasets, but the total available high-quality supervised speech data (SpeechStew: 5,140 hours) is tiny compared to the 1,000,000 hours of unlabeled speech used in unsupervised pre-training work (Zhang et al. 2021) (§1, L17).
- Weakly supervised datasets in speech (10,000–30,000 hours; Chen et al. 2021, Galvez et al. 2021) and in computer vision (Mahajan et al. 2018; Kolesnikov et al. 2020) had shown quality/quantity trade-offs improve robustness, but speech recognition had not yet scaled weak supervision to the next order of magnitude (§1, L18, L24).

## 3. Research gap
Existing large-scale approaches were either (a) unsupervised pre-training at huge scale (up to 1,000,000 hours) but without a matching high-quality decoder, requiring fine-tuning, or (b) supervised/weakly-supervised training but capped at tens of thousands of hours — "these new datasets are only a few times larger than the sum of existing high-quality datasets and still much smaller than prior unsupervised work" (§1, L25). No prior work had scaled weakly supervised speech recognition to ~680,000 hours, nor combined this scale with multilingual and multitask (not just English transcription) training (§1, L25–26).

## 4. Research question / objective
Study "the capabilities of speech processing systems trained simply to predict large amounts of transcripts of audio on the internet" at very large scale (Abstract, L8), and test whether such models "transfer well to existing datasets zero-shot, removing the need for any dataset-specific fine-tuning" (§1, L25), while broadening scope to multilingual and multitask (translation, language ID, voice activity detection) training (§1, L26).

## 5. System / method
- **Data construction (§2.1, L29–45):** minimalist text pre-processing (predict raw transcript text, no significant standardization); audio+transcript pairs scraped from the internet; heuristic filters to remove machine-generated transcripts (e.g., detecting all-caps/all-lowercase text, missing punctuation patterns); audio-language detector (fine-tuned on VoxLingua107) checks transcript language against detected spoken language via CLD2 — mismatches are either dropped or repurposed as X→en translation pairs if the transcript is English; fuzzy de-duplication of transcript text; audio segmented into 30-second chunks; an additional filtering pass after an initial model was trained, using its per-source error rate plus manual inspection to remove low-quality sources; transcript-level de-duplication against evaluation sets, specifically noted for TED-LIUM 3 (L45).
- **Model (§2.2, L46–48):** encoder–decoder Transformer (Vaswani et al. 2017), chosen as an "off-the-shelf architecture to avoid confounding our findings with model improvements" (L47). Audio resampled to 16,000 Hz; 80-channel log-magnitude Mel spectrogram, 25ms windows, 10ms stride; input scaled to [-1, 1], ~zero mean. Encoder stem: two Conv1D layers (filter width 3, GELU activation), second conv has stride 2; sinusoidal position embeddings; pre-activation residual Transformer blocks (Child et al. 2019); final layer norm on encoder output. Decoder: learned position embeddings, tied input-output token representations (Press & Wolf 2017). Encoder and decoder share width and block count. Byte-level BPE tokenizer from GPT-2 for English-only models; refit (same size) vocabulary for multilingual models.
- **Multitask format (§2.3, L49–53):** single decoder-token-sequence interface specifying, in order: `<|startoftranscript|>`, a language token (99 total, sourced from the VoxLingua107 model), `<|nospeech|>` if no speech, a task token (`<|transcribe|>` or `<|translate|>`), a `<|notimestamps|>` flag or interleaved timestamp tokens (20ms resolution), caption text tokens, and `<|endoftranscript|>`. Optional preceding-transcript-text conditioning is added with some probability; training loss is masked over that previous-context text only.
- **Training (§2.4, L211–241, Appendix F L2127–2155):** data-parallel training, FP16 with dynamic loss scaling, activation checkpointing; AdamW optimizer (β1=0.9, β2=0.98, weight decay 0.1, Gaussian Fan-In weight init), gradient norm clipping, linear LR decay to zero after a 2,048-update warmup; batch size 256 segments; trained for 2^20 (1,048,576) updates (Table 17), "between two and three passes over the dataset" (L212); no data augmentation/regularization for the original models. A "Large V2" model was later trained for 2.5× more epochs with added SpecAugment, Stochastic Depth, and BPE Dropout regularization (footnote 3, L216; Table 18: 655,360 updates, batch size 1024, BPE dropout 0.1, stochastic depth 0.1, SpecAugment "LibriSpeech Basic" policy); footnote 3 states "reported results have been updated to this improved model unless otherwise specified" (L216).
- A brief fine-tuning pass on transcripts without speaker annotations was used to reduce a tendency to hallucinate plausible-but-incorrect speaker names (§2.4, L215, L239–241).

## 6. Architecture
Table 1 (L222–237), architecture details of the Whisper model family:
| Model | Layers | Width | Heads | Parameters |
|---|---|---|---|---|
| Tiny | 4 | 384 | 6 | 39M |
| Base | 6 | 512 | 8 | 74M |
| Small | 12 | 768 | 12 | 244M |
| Medium | 24 | 1024 | 16 | 769M |
| Large | 32 | 1280 | 20 | 1550M |

Learning rates per model (Table 19, L2149–2155): Tiny 1.5×10⁻³, Base 1×10⁻³, Small 5×10⁻⁴, Medium 2.5×10⁻⁴, Large 1.75×10⁻⁴, Large V2 2.0×10⁻⁴.

README-only artifact fact (not a paper claim): the pinned README also lists a `turbo` model (809M parameters, "an optimized version of large-v3") and describes `large-v3`/`large-v2` comparison figures — **neither `turbo` nor `large-v3` appears anywhere in the paper snapshot**; this is repo evolution after the paper, kept separate per task rules.

## 7. Dataset / data
- Training: 680,000 hours total; 117,000 hours cover 96 languages other than English; 125,000 hours are X→en translation data (§1, L26). Not released (Abstract, L8).
- Evaluation datasets are all pre-existing public/licensed academic corpora, listed in Appendix A (§A.1–A.3, L1179–1222): short-form English — LibriSpeech (test-clean/test-other), TED-LIUM 3, Common Voice 5.1 (English subset), Artie bias corpus, CallHome/Switchboard (LDC2002S09/LDC2002T43), WSJ (LDC93S6B/LDC94S13B), CORAAL (231 interviews), CHiME-6, AMI-IHM/AMI-SDM1; long-form English — TED-LIUM 3 (11 full talks), Meanwhile (64 Late Show segments), Rev16 (16 of 30 podcast episodes, specific file numbers listed), Kincaid46 (46 files; 25-file human-comparison subset with specific Ref IDs listed), Earnings-21 and Earnings-22, CORAAL (231 full interviews); multilingual — Multilingual LibriSpeech (MLS), Fleurs, VoxPopuli (16 languages incl. English), Common Voice 9, CoVoST 2.
- Comparison models: 14 public HuggingFace checkpoints (Appendix B, L1223–1228), all noted by the authors as "entirely or partly trained on LibriSpeech" (L1228).

## 8. Experimental setup
- Zero-shot protocol: no use of any evaluation dataset's own training split (§3.1, L244).
- WER computed after the authors' custom text normalizer (§3.2, Appendix C) to reduce penalizing non-semantic formatting differences; the normalizer was iteratively developed by manual inspection (§3.2, L246–247) and is compared against an independently developed FairSpeech normalizer in §4.4.
- Effective-robustness framework (Taori et al. 2020) with LibriSpeech as the reference (in-distribution) dataset and 12 other academic ASR datasets as out-of-distribution (§3.3, L278).
- Additive-noise robustness test: white noise and pub noise (from the Audio Degradation Toolbox) added at varying SNR, compared against 14 LibriSpeech-trained models, 2 of which are NVIDIA STT models (§3.7, L722).
- Long-form transcription evaluated on 7 datasets against 4 commercial ASR services (queried "using their default English transcription settings as of September 1st, 2022", L758) and the NVIDIA STT Conformer-CTC Large model via its buffered `FrameBatchASR` inference class (§3.8, L727–758).
- Human comparison: 25 recordings from Kincaid46 transcribed by 5 services — one computer-assisted, four purely human (§3.9, L759–760).
- Dataset-size ablation: medium-sized models trained on 0.5%, 1%, 2%, 4%, 8% subsampled versions of the full dataset, early-stopped on validation loss, evaluated using an exponential-moving-average parameter estimate (Polyak & Juditsky 1992, smoothing rate 0.9999) (§4.2, L793–794).
- Long-form decoding heuristics (§4.5, L967–1000): beam search with 5 beams (log-probability score); temperature starts at 0 and increases by 0.2 up to 1.0 when avg log-probability over generated tokens is below −1 or gzip compression rate exceeds 2.4; previous-window text conditioning applied when temperature is below 0.5; no-speech detection combines a no-speech-token probability threshold of 0.6 with the avg-logprob threshold of −1; initial timestamp token constrained to between 0.0 and 1.0 second.

## 9. Metrics
- Word Error Rate (WER), string-edit-distance-based (§3.2, L245).
- Character Error Rate is implicitly used for Chinese, Japanese, Thai, Lao, Burmese by inserting spaces between characters before scoring (Appendix C, L1247) — stated as a normalization procedure, not named as a separate "CER metric" in the main text.
- BLEU for translation tasks (§3.5, Table 4; Table 14, Table 15).
- Accuracy (%) for language identification (§3.6, Table 5).
- Squared correlation coefficient (r²) between log(WER) or log(BLEU) and log(training hours per language) (Figures 3 and 4).

## 10. Results (exact numbers, with table/section)
- English ASR: best zero-shot Whisper LibriSpeech test-clean WER described in prose as "2.5" (§3.3, L279); Table 8 (greedy decoding) and Table 9 (beam+temperature fallback) report Large-v2 values in the 2.7–4.2 range across decoding settings — both figures are recorded as-is; see Assessment Risk 4.
- Table 2 (L283–393): zero-shot Whisper (Large V2, no LM) makes an average **55.2%** relative error reduction vs. a matched-performance wav2vec 2.0 Large model across the 12-dataset OOD suite (also restated in prose, L395); on LibriSpeech Clean both models are within 0.1% of each other (L391–393 shows wav2vec 2.0 2.7 vs. Whisper 2.7 on LibriSpeech Clean row).
- Table 3 (L604–617): Multilingual LibriSpeech (MLS) WER — Zero-Shot Whisper 7.3 vs. VP-10K+FT 10.9, XLS-R(1B) 9.7, Maestro (best prior) not applicable to MLS row (only "-" listed); VoxPopuli WER — Zero-Shot Whisper 13.6 vs. VP-10K+FT 15.3, XLS-R(1B) 10.6, mSLAM-CTC(2B) 9.1, Maestro 8.1 (best).
- Fleurs multilingual ASR (§3.4, L622): squared correlation coefficient r²=0.83 between log(WER) and log(training hours/language); WER estimated to halve for every 16× increase in training data (regression-derived statement in the paper).
- Table 4 (L604–663): CoVoST2 X→en BLEU — Zero-Shot Whisper: High 36.2, Mid 32.6, Low 25.2, All 29.1; vs. best prior (Maestro): High 38.2, Mid 31.3, Low 18.4, All 25.2. Whisper "achieve[s] a new state of the art of 29.1 BLEU zero-shot" (L710); improves over mSLAM by 6.7 BLEU on the lowest-resource grouping (L710).
- Fleurs-as-translation (§3.5, L711): r²=0.24 (lower than the 0.83 for ASR); Welsh (CY) cited as an outlier at "only 13 BLEU despite supposedly having 9,000 hours of translation data" (L713), later attributed to language-ID mislabeling of English audio as Welsh.
- Table 5 (L665–673): Fleurs language ID accuracy — Zero-shot Whisper 64.5% vs. w2v-bert-51(0.6B) 71.4%, mSLAM-CTC(2B) 77.7%; Whisper underperforms supervised SOTA "by 13.6%" (L715); on the 82 overlapping languages (excluding 20 languages absent from Whisper's training data) best Whisper model achieves 80.3% (upper bound 80.4%) (L715).
- Table 6 (L875–887): dataset-size scaling (hours → English WER / Multilingual WER / X→en BLEU): 3405→30.5/92.4/0.2; 6811→19.6/72.7/1.7; 13621→14.4/56.6/7.9; 27243→12.3/45.0/13.9; 54486→10.9/36.4/19.2; 681070→9.9/29.2/24.8.
- Table 7 (L976–998): long-form WER averaged over 7 datasets — Greedy 11.0 → +Beam search 10.6 → +Temperature fallback 10.6 (no change from beam-only row) → +VAD 10.2 → +Previous-text conditioning 10.0 → +Initial timestamp constraint 10.0 (no change from previous row).
- §3.9 (L760): the computer-assisted human transcription service's aggregate WER on 25 Kincaid46 recordings is "1.15% point better than Whisper's"; pure-human transcription performance is "only a fraction of a percentage point better than Whisper's" — the exact pure-human WER value itself is **NOT IN SNAPSHOT** (only shown in Figure 7 image).
- §3.7 (L722): under additive pub noise below 10 dB SNR, "all models quickly degrade... performing worse than the Whisper model" — specific crossover WER values are NOT IN SNAPSHOT (Figure 5 image only).
- Model scaling (§4.1, L792): "performance continues to increase with model size across multilingual speech recognition, speech translation, and language identification," with an exception for English speech recognition showing diminishing returns — exact per-size values are in Figure 8 image, not extracted as text.

## 11. Supported claims (directly measured/observed)
- Zero-shot Whisper models substantially outperform supervised LibriSpeech-trained models on 12 out-of-distribution ASR datasets while performing similarly on the in-distribution LibriSpeech reference (Table 2, §3.3).
- Whisper achieves a new state-of-the-art 29.1 BLEU on CoVoST2 X→en translation ("All" resource group), zero-shot (Table 4, L710).
- Larger training datasets monotonically improve English WER, multilingual WER, and X→en BLEU on the tested subsample sizes (Table 6).
- Adding each long-form decoding heuristic incrementally reduces average long-form WER across 7 datasets, though not uniformly per-dataset (Table 7, L1000).
- Whisper's language identification accuracy on Fleurs is measurably below prior supervised SOTA (64.5% vs. 77.7%/71.4%) (Table 5).

## 12. Derived claims (computed/comparative)
- The "55.2% average relative error reduction" (Table 2) is explicitly computed by the authors from paired per-dataset WER values.
- The r²=0.83 (ASR) and r²=0.24 (translation) correlation coefficients (§3.4, §3.5) are derived statistics from regressions on log(WER)/log(BLEU) vs. log(training hours).
- The "WER halves for every 16× increase in training data" statement (§3.4, L622) is a derived regression-coefficient interpretation of the same correlation, not a directly measured single data point.
- The claim that Whisper is "roughly competitive with the best supervised LibriSpeech model when evaluated on other datasets" even at 39M parameters (§3.3, L395) is a comparative claim across two different models' result rows.

## 13. Interpretations (authors' explanations — label as interpretation)
- Interpretation: the human/machine performance gap on LibriSpeech is attributed to "conflating different capabilities being measured by human and machine performance on a test set" — humans measure out-of-distribution generalization, machines measure in-distribution generalization (§3.3, L251).
- Interpretation: VoxPopuli underperformance is suspected to be "due to other models including this distribution as a major source for their unsupervised pre-training data and the dataset having significantly more supervised data" (§3.4, L619).
- Interpretation: outlier languages (Hebrew, Telugu, Chinese, Korean) with worse-than-expected Fleurs ASR performance are attributed to possible "lack of transfer due to linguistic distance," a poor tokenizer match, "or variations in data quality" (§3.4, L622) — the paper explicitly presents this as one of several possible, unconfirmed explanations.
- Interpretation: diminishing returns in English ASR with model/dataset scaling are attributed to "saturation effects from approaching human-level performance" (§4.1, L792; §4.2, L889).
- Interpretation: the Welsh translation-data outlier is attributed to English audio being misclassified as Welsh by the language-ID system (§3.5, L713) — described by the authors as based on manual "inspection," i.e., an investigated but not exhaustively quantified explanation.
- Interpretation: robustness to noise is attributed generally to Whisper's training data diversity rather than a specific mechanism (§3.7, L722, "showcases Whisper's robustness to noise").

## 14. Hypotheses / speculation
- The authors explicitly flag as unresolved (§4.2, L893): whether diminishing returns from 54,000h→680,000h means "current best Whisper models are under-trained relative to dataset size" (suggesting more scaling would help) or that "we are nearing the end of performance improvements from dataset size scaling for speech recognition" — stated as two competing, undecided explanations requiring "further analysis... to characterize 'scaling laws'."
- §6 "Studying the impact of Language Models on Robustness" (L1018): the authors state "it's currently unclear to what degree the benefits of Whisper stem from training its encoder, decoder, or both," proposed as future ablation work, not resolved in this paper.
- §6 "Adding Auxiliary Training Objectives" (L1021): speculation that incorporating unsupervised pre-training/self-teaching objectives "is possible" to further improve results, explicitly marked as not tested ("we have not found them necessary").

## 15. Limitations
All from the paper's own §6 "Limitations and Future Work" (L1008–1021) unless marked as a derived scope boundary:
- **Improved decoding strategies needed**: remaining long-form errors (repeat loops, dropped first/last words, "complete hallucination") are described as "decidedly non-human/perceptual" failure modes not fully solved by the heuristics in §4.5 (L1015).
- **Low-resource language performance is still poor**, attributed to the training pipeline sourcing "primarily from English-centric parts of the internet," leaving "most languages... less than 1000 hours of training data" (L1016).
- **Only zero-shot transfer was studied**; fine-tuning was explicitly out of scope for this paper ("we have focused on the robustness properties... and as a result only studied the zero-shot transfer performance") (L1017).
- **Unclear locus of robustness benefit** (encoder vs. decoder vs. both) is stated as an open question (L1018).
- **No unsupervised pre-training/self-teaching used**; the authors note this departs from most contemporary SOTA systems and that they "have not found them necessary" but do not rule out further gains (L1021).
- **Scope boundary (derived from stated conditions):** because training-data filtering explicitly de-duplicates only against TED-LIUM 3 among the evaluation sets (§2.1, L45, "we thought were at higher risk of overlap, namely TED-LIUM 3"), the zero-shot claims for other evaluation datasets rest on the authors' general filtering pipeline rather than a dataset-specific contamination check; this is a scope boundary that follows from the stated de-duplication procedure, not a limitation the authors state directly.
- **Scope boundary (derived from stated conditions):** the multitask token format explicitly limits input audio to 30-second segments per forward pass (§2.3, L37; §3.8, L724, "Whisper models are trained on 30-second audio chunks and cannot consume longer audio inputs at once"), so all long-form results rest on the buffered-window heuristic procedure of §4.5, not direct long-context modeling — the paper itself states this directly (L724), so this item could also be listed as an author-stated limitation.

## 16. Actual contribution
As stated in the Conclusion (§7, L1022–1023): "Whisper suggests that scaling weakly supervised pre-training has been underappreciated so far in speech recognition research. We achieve our results without the need for the self-supervision and self-training techniques that have been a mainstay of recent large-scale speech recognition work and demonstrate how simply training on a large and diverse supervised dataset and focusing on zero-shot transfer can significantly improve the robustness of a speech recognition system." Concretely: an encoder-decoder Transformer trained on 680,000 hours of weakly supervised, multilingual, multitask audio-transcript data, released as inference code and model weights (Abstract, L8; README), demonstrating zero-shot robustness competitive with or exceeding prior supervised/fine-tuned systems and approaching human-level accuracy and robustness on English ASR (Abstract, L8; §3.9).

## 17. Unsupported or weakly supported claims (thin support in snapshot)
- The claim that WER "halves for every 16× increase in training data" (§3.4, L622) rests on a single regression fit (r²=0.83) over one metric (Fleurs multilingual ASR); no confidence interval or significance test is given in the snapshot text, and the authors do not report whether this trend holds outside the studied range.
- The assertion that Whisper's noise robustness generalizes beyond the two tested noise types (white noise, pub noise) is not made by the authors, but a reader could over-generalize from §3.7's framing ("showcases Whisper's robustness to noise") — the snapshot's actual evidence is limited to these two specific degradation types from one toolbox (Audio Degradation Toolbox).
- The long-form commercial-ASR comparison (§3.8, L758) is explicitly self-qualified by the authors: "we note the possibility that some of the commercial ASR systems have been trained on some of these publicly available datasets, and therefore these results may not be accurately reflecting the relative robustness of the systems" — i.e., the authors themselves flag this comparison as potentially confounded, not a clean claim.
- The Welsh-outlier explanation (§3.5, L713) is based on a qualitative "inspection" of "the majority of" mislabeled data, not a systematic audit — the exact fraction of affected Welsh training data is NOT IN SNAPSHOT.
- Table 2's "Large (no LM)" row is not clearly defined against Table 2/3/4/5's other "Large V2" rows given the footnote-3 statement that reported results already default to Large V2 "unless otherwise specified" (L216); the reader cannot fully disambiguate from the snapshot whether every "Large" cell in every table used the original or V2 checkpoint. Recorded as an ambiguity, not resolved.

## 18. Claim → evidence → source table

| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| Whisper trained on 680,000 hours of weakly supervised, multilingual, multitask audio-transcript data | measured (design fact) | dataset scale statement | paper.txt §1 L25–26 | "scaling weakly supervised speech recognition the next order of magnitude to 680,000 hours of labeled audio data" |
| 117,000 of 680,000 hours cover 96 non-English languages; 125,000 hours are X→en translation | measured (design fact) | dataset composition statement | paper.txt §1 L26 | "117,000 hours cover 96 other languages. The dataset also includes 125,000 hours of X→en translation data" |
| Zero-shot Whisper reduces error by 55.2% on average vs. matched wav2vec 2.0 on 12 OOD ASR datasets | measured | Table 2 + restated in prose | paper.txt Table 2 L283–393; L395 | "makes 55.2% less errors on average" |
| Whisper achieves new SOTA 29.1 BLEU on CoVoST2 X→en (All) zero-shot | measured | Table 4 | paper.txt Table 4 L604–663; L710 | "achieve a new state of the art of 29.1 BLEU zero-shot" |
| Fleurs ASR: r²=0.83 between log(WER) and log(training hours/language) | derived | regression statistic | paper.txt §3.4 L622 | "strong squared correlation coefficient of 0.83 between the log of the word error rate" |
| Language ID accuracy on Fleurs: 64.5% (Whisper) vs. 77.7% (mSLAM-CTC) | measured | Table 5 | paper.txt Table 5 L665–673 | "not competitive with prior supervised results on Fleurs" |
| Long-form heuristic stack reduces average WER from 11.0 to 10.0 across 7 datasets | measured | Table 7 | paper.txt Table 7 L976–998 | "adding each of the interventions above incrementally reduces the WER overall" |
| Human/machine gap attributed to in-distribution vs. out-of-distribution generalization difference | interpretation | authors' explanatory claim | paper.txt §3.3 L251 | "two quite different abilities are being measured due to a difference in train data" |
| Low-resource language performance attributed to English-centric data collection bias | interpretation (stated as limitation) | authors' explanatory + limitation statement | paper.txt §6 L1016 | "most languages have less than 1000 hours of training data" |
| Whether robustness stems from encoder, decoder, or both is unresolved | hypothesis/open question | authors' stated future work | paper.txt §6 L1018 | "currently unclear to what degree the benefits of Whisper stem from training its encoder, decoder" |
| Whisper models cannot consume audio longer than 30 seconds per forward pass | scope boundary (stated directly) | architectural/training constraint statement | paper.txt §3.8 L724 | "trained on 30-second audio chunks and cannot consume longer audio inputs at once" |
| Pure-human WER on Kincaid46 subset is only "a fraction of a percentage point" better than Whisper's | measured (value NOT IN SNAPSHOT) | prose summary of Figure 7 | paper.txt §3.9 L760 | "pure-human performance is only a fraction of a percentage point better than Whisper's" |
| README lists a `turbo` model and `large-v3`, absent from the paper | artifact fact (README-only, conflict) | README model table | README__openai__whisper.md L64–74 | "turbo model is an optimized version of large-v3 that offers faster transcription speed" |
| Repo/paper venue: ICML 2023 poster (outside snapshot, used for assessment only) | context | web search confirmation | (outside snapshot; see PROJECT_ASSESSMENT.md §3) | n/a — not from snapshot |
