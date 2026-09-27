# Robust Speech Recognition via Large-Scale Weak Supervision

**Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, Ilya Sutskever**  
OpenAI, San Francisco, CA

---

## Abstract

We study the capabilities of speech processing systems trained to predict large amounts of audio transcripts collected from the internet. When scaled to 680,000 hours of multilingual and multitask supervision, the resulting models generalize well to standard benchmarks and are often competitive with prior fully supervised results, but in a zero-shot transfer setting that requires no fine-tuning on any target dataset. When compared to humans, the models approach their accuracy and robustness. The approach, called Whisper, uses a standard encoder-decoder Transformer trained with a unified multitask format that encodes the desired task as a sequence of special tokens fed to the decoder. This single model handles transcription, speech-to-English translation, language identification, and voice activity detection across 99 languages. Extensive evaluation on 12 English-only benchmarks demonstrates that zero-shot Whisper models achieve 55.2% average relative error reduction over supervised LibriSpeech-trained models when evaluated on other datasets, closely matching human-level robustness. Models and inference code are publicly released to serve as a foundation for further work on robust speech processing.

---

## 1. Introduction

Progress in automatic speech recognition (ASR) has been energized by unsupervised pre-training techniques such as Wav2Vec 2.0 (Baevski et al., 2020), which learn directly from raw audio without human labels and have been scaled to 1,000,000 hours of unlabeled speech (Zhang et al., 2021). However, because these encoders are purely unsupervised, they lack a correspondingly powerful decoder and require a fine-tuning stage before they can produce usable transcriptions.

Fine-tuning introduces a critical weakness: machine learning models are highly adept at learning dataset-specific patterns that boost held-out performance within a distribution but do not transfer elsewhere. As a cautionary example from computer vision, Radford et al. (2021) documented a 9.2% increase in object classification accuracy from fine-tuning on ImageNet (Russakovsky et al., 2015) without any improvement on seven other natural image datasets. Models that achieve "superhuman" performance on a benchmark can still make many basic errors in other settings, precisely because they exploit dataset-specific quirks that humans do not (Geirhos et al., 2020).

A more robust alternative is to pre-train in a supervised fashion across many datasets and domains. Works such as Narayanan et al. (2018), Likhomanenko et al. (2020), and Chan et al. (2021) demonstrate that multi-source supervised training produces models that generalize more effectively to held-out datasets. SpeechStew (Chan et al., 2021), for instance, mixes 7 existing datasets totalling 5,140 hours. Yet this is still small compared to the 1,000,000 hours of unlabeled data used in semi-supervised pipelines.

Recent efforts have relaxed the requirement for gold-standard transcripts to scale weakly supervised data. Chen et al. (2021) and Galvez et al. (2021) use automated pipelines to produce 10,000 and 30,000 hours of noisier training data, respectively. This trade-off between quality and quantity parallels similar advances in computer vision, where moving beyond crowdsourced datasets to larger weakly supervised sources substantially improves robustness (Mahajan et al., 2018; Kolesnikov et al., 2020).

This work closes the remaining gap by scaling weakly supervised speech recognition by the next order of magnitude to 680,000 hours of labeled audio. The resulting model family, called **Whisper**, demonstrates that simply training on a large and diverse supervised dataset, with a focus on zero-shot transfer, can approach human-level robustness without any self-supervision or self-training techniques. In addition to scale, Whisper broadens scope to multilingual and multitask training: 117,000 of the 680,000 hours cover 96 languages other than English, and 125,000 hours are X-to-English translation data.

---

## 2. Method

### 2.1 Data Collection and Filtering

The dataset is constructed from audio paired with transcripts available on the internet. This yields a broad distribution of environments, recording setups, speakers, and languages. While diversity in audio quality helps train a robust model, diversity in transcript quality is harmful. Initial inspection revealed a large fraction of subpar transcripts, addressed through several automated filtering steps.

A major concern is that many internet transcripts are machine-generated rather than human-authored. Training on machine-generated transcripts risks learning "transcript-ese" — the stylistic conventions of ASR systems that are atypical of natural written language. Common signals include all-uppercase or all-lowercase text, absence of punctuation such as commas and question marks, and simplified inverse text normalization. These heuristics were used to detect and remove machine-generated transcripts.

An audio language detector, obtained by fine-tuning a prototype model on VoxLingua107 (Valk & Alümäe, 2021), was applied to verify that the spoken language matches the language of the transcript (verified against CLD2). Mismatched pairs were excluded from speech recognition training but, if the transcript language was English, were repurposed as X→English translation training examples. Fuzzy de-duplication was applied to reduce repeated and automatically generated content.

Audio files were segmented into 30-second chunks aligned with the corresponding transcript text. After training an initial model, data sources with high error rates were manually inspected and low-quality sources—including partially transcribed audio and misaligned captions missed by earlier filters—were removed. To avoid evaluation contamination, transcript-level de-duplication was performed between the training data and higher-risk evaluation datasets such as TED-LIUM 3 (Hernandez et al., 2018).

The final dataset contains 680,000 hours in total: 65% (438,218 hours) for English transcription, 17% (117,113 hours) for multilingual transcription across 96 languages, and 18% (125,739 hours) for X-to-English translation.

### 2.2 Model Architecture

Whisper uses an off-the-shelf encoder-decoder Transformer (Vaswani et al., 2017), chosen because this architecture has been well validated to scale reliably and to avoid confounding the study of data scaling with model innovations.

All audio is resampled to 16,000 Hz, and an 80-channel log-magnitude Mel spectrogram is computed on 25-millisecond windows with a 10-millisecond stride. The input is globally scaled to lie between −1 and 1 with approximately zero mean over the pre-training dataset. The encoder processes this representation through a small stem of two 1D convolutional layers (filter width 3, GELU activations; Hendrycks & Gimpel, 2016) where the second has stride 2, followed by sinusoidal position embeddings and a stack of Transformer blocks with pre-activation residual connections (Child et al., 2019) and a final layer normalization. The decoder uses learned position embeddings and tied input–output token representations (Press & Wolf, 2017). Encoder and decoder have equal width and depth.

Five model sizes were trained, summarized in Table 1. English-only models use the byte-level BPE tokenizer from GPT-2 (Sennrich et al., 2015; Radford et al., 2019); multilingual models refit the vocabulary (at the same size) to reduce fragmentation in other languages.

**Table 1. Whisper model family architecture details.**

| Model   | Layers | Width | Heads | Parameters |
|---------|--------|-------|-------|------------|
| Tiny    | 4      | 384   | 6     | 39M        |
| Base    | 6      | 512   | 8     | 74M        |
| Small   | 12     | 768   | 12    | 244M       |
| Medium  | 24     | 1024  | 16    | 769M       |
| Large   | 32     | 1280  | 20    | 1550M      |

### 2.3 Multitask Training Format

Rather than training separate models for each speech processing task, Whisper uses a single model for transcription, translation, voice activity detection, language identification, and timestamp prediction. All tasks and conditioning information are encoded as a sequence of tokens fed to the decoder before prediction begins.

The decoder receives the following sequence of special tokens at inference time. First, a `<|startoftranscript|>` token signals the beginning of prediction. The model then predicts the spoken language from a set of 99 language tokens sourced from the VoxLingua107 detector. If no speech is detected in the 30-second window, the model predicts `<|nospeech|>` instead. Next, a task token specifies either `<|transcribe|>` or `<|translate|>`, followed by an optional `<|notimestamps|>` token. When timestamps are enabled, time tokens (quantized to the nearest 20 milliseconds) are interleaved with caption tokens: a start-time token precedes each segment's text and an end-time token follows it. Finally, `<|endoftranscript|>` closes the sequence. When the transcript preceding the current audio window is available, it is provided as previous-text context to the decoder with 50% probability during training.

This unified format allows a single model to replace many components of traditional speech processing pipelines, eliminating the need for separate voice activity detectors, language identifiers, and inverse text normalization modules.

### 2.4 Training Details

Models are trained with data parallelism using FP16 precision with dynamic loss scaling and activation checkpointing. The optimizer is AdamW (Loshchilov & Hutter, 2017) with gradient norm clipping (Pascanu et al., 2013), a linear learning rate decay to zero following a warmup over the first 2,048 updates, and a batch size of 256 thirty-second segments. Models are trained for 2²⁰ updates, corresponding to roughly two to three passes over the full dataset. With only a few epochs over this large dataset, overfitting is not a primary concern; no data augmentation or regularization is used, relying instead on the inherent diversity of the dataset for generalization.

A fine-tuning step is applied to suppress a tendency of larger models to hallucinate speaker names: models are briefly fine-tuned on the subset of transcripts that exclude speaker annotations.

An improved Large V2 model was subsequently trained for 2.5× more epochs with SpecAugment (Park et al., 2019), Stochastic Depth (Huang et al., 2016), and BPE Dropout (Provilkov et al., 2019) added for regularization. Results in this paper use the Large V2 model unless otherwise noted.

---

## 3. Evaluation Setup

### 3.1 Zero-Shot Protocol

The defining evaluation setting for Whisper is zero-shot transfer: no training data from any evaluation dataset is used. This contrasts with the standard protocol for most ASR benchmarks, which assume access to the training split of the evaluation dataset for fine-tuning. The zero-shot setting is more representative of real-world deployment conditions, where a practitioner needs reliable performance on a new distribution without additional supervision.

### 3.2 Text Normalization

Word error rate (WER), the standard ASR metric, measures string edit distance against a reference transcript and penalizes all differences, including innocuous formatting variations such as differences in punctuation, capitalization, or numeric expression style. Zero-shot models that have never seen a specific dataset's transcript conventions are particularly sensitive to such penalties.

To address this, the authors developed a text normalizer applied before WER calculation. For English, it removes parenthetical annotations, converts contractions to full forms, standardizes numeric and monetary expressions (e.g., "sixty-eight million dollars" → "$68 million"), converts British to American spellings, and removes punctuation that does not affect meaning. A simpler normalizer (lowercasing, removing punctuation and symbols) is applied for non-English languages. A comparison against an independently developed normalizer from the FairSpeech project (Koenecke et al., 2020) confirms that the custom normalizer behaves consistently across Whisper and other open-source models on most datasets, with larger gains only on datasets (CallHome, Switchboard, WSJ) that contain many contractions or numeric expressions in the references.

---

## 4. Results

### 4.1 English Speech Recognition and Robustness

The central claim is that zero-shot training on a large, diverse corpus produces models that are substantially more robust to distribution shift than fine-tuned models trained on a single dataset. To test this, LibriSpeech (Panayotov et al., 2015) serves as the reference distribution (due to its central role in modern ASR research), and 12 other academic datasets serve as out-of-distribution targets.

The best zero-shot Whisper model (Large V2) achieves a WER of 2.5% on LibriSpeech test-clean, roughly comparable to supervised models from mid-2019 and the mid-range of current supervised baselines. However, when both the best zero-shot Whisper model and a supervised wav2vec 2.0 Large model with nearly identical LibriSpeech performance are evaluated on the 12 other datasets, a striking divergence appears. Despite matching on the reference distribution (both achieving 2.7% WER on LibriSpeech test-clean), the zero-shot Whisper model achieves an average **relative error reduction of 55.2%** across the other datasets (Table 2).

**Table 2. Effective robustness comparison (WER %).**

| Dataset           | wav2vec 2.0 Large | Whisper Large V2 | RER (%) |
|-------------------|-------------------|------------------|---------|
| LibriSpeech Clean | 2.7               | 2.7              | 0.0     |
| LibriSpeech Other | 6.2               | 5.2              | 16.1    |
| Common Voice      | 29.9              | 6.2              | 79.3    |
| Fleurs En         | 14.6              | 4.4              | 69.9    |
| TED-LIUM          | 10.5              | 4.0              | 61.9    |
| CHiME-6           | 65.8              | 25.5             | 61.2    |
| VoxPopuli En      | 17.9              | 7.3              | 59.2    |
| CORAAL            | 35.6              | 16.2             | 54.5    |
| AMI IHM           | 37.0              | 16.9             | 54.3    |
| Switchboard       | 28.3              | 13.8             | 51.2    |
| CallHome          | 34.8              | 17.6             | 49.4    |
| WSJ               | 7.7               | 3.9              | 49.4    |
| AMI SDM1          | 67.6              | 36.4             | 46.2    |
| **Average**       | **29.3**          | **12.8**         | **55.2** |

Even the smallest Whisper model (Tiny, 39M parameters, 6.7% WER on LibriSpeech test-clean) is roughly competitive with the best supervised LibriSpeech model when evaluated on other datasets.

**Comparison with human performance.** Whisper models, like humans, are trained broadly rather than on any specific evaluation distribution; they should therefore be compared to humans on an equal footing. A human transcriber (Alec), whose LibriSpeech performance is approximately matched by the best Whisper models, was used as a reference. The best zero-shot Whisper models roughly match this human's accuracy and robustness frontier across the suite of 12 out-of-distribution datasets. In contrast, supervised LibriSpeech models make roughly twice as many errors as the human on those other datasets despite matching them on LibriSpeech, demonstrating that high performance on a held-out set of a training distribution should not be equated with human-level capability in general.

This finding highlights a systematic evaluation problem: machine learning systems that are fine-tuned on the evaluation distribution are measuring in-distribution generalization, while humans are demonstrating out-of-distribution generalization. Whisper's zero-shot evaluation aligns these two conditions, enabling more meaningful human–machine comparisons.

### 4.2 Multilingual Speech Recognition

Performance on multilingual speech recognition is assessed on two low-data benchmarks, Multilingual LibriSpeech (MLS; Pratap et al., 2020b) and VoxPopuli (Wang et al., 2021), as well as the broader Fleurs dataset (Conneau et al., 2022) covering 102 languages (Table 3).

**Table 3. Multilingual speech recognition WER (%).**

| Model              | MLS  | VoxPopuli |
|--------------------|------|-----------|
| VP-10K + FT        | 10.9 | 15.3      |
| XLS-R (1B)         | 9.7  | 10.6      |
| mSLAM-CTC (2B)     | —    | 9.1       |
| Maestro            | 7.3  | 8.1       |
| Zero-Shot Whisper  | 10.9 | 13.6      |

On MLS, zero-shot Whisper surpasses the XLS-R (Babu et al., 2021), mSLAM (Bapna et al., 2022), and Maestro (Chen et al., 2022b) baselines. On VoxPopuli, however, Whisper falls short of prior work, likely because other models heavily use VoxPopuli as an unsupervised pre-training source and VoxPopuli provides approximately 10× more supervised training data per language than MLS.

Across the 67 languages covered in both the Whisper training set and Fleurs, there is a strong squared correlation coefficient of **r² = 0.83** between the log of WER and the log of training data per language. The regression implies that WER halves for every 16× increase in training data. Languages with unique scripts or greater typological distance from the predominantly Indo-European training data (e.g., Hebrew, Telugu, Chinese, Korean) consistently underperform relative to the trend, pointing to potential issues with tokenization or transfer distance rather than purely data volume.

### 4.3 Speech-to-English Translation

Translation performance is evaluated on the X→English subset of CoVoST2 (Wang et al., 2020b), which covers 21 language pairs. Zero-shot Whisper achieves a new state of the art of **29.1 BLEU** without using any CoVoST2 training data (Table 4), attributed to 68,000 hours of X→English translation data in pre-training. The improvement is especially pronounced at the low-resource end of the benchmark, where Whisper exceeds mSLAM by 6.7 BLEU. On the highest-resource languages, however, Whisper does not surpass Maestro or mSLAM, where those models benefit from directly supervised fine-tuning on the relevant distributions.

**Table 4. X→English speech translation BLEU on CoVoST2.**

| Model             | High | Mid  | Low  | All  |
|-------------------|------|------|------|------|
| XMEF-X            | 34.2 | 20.2 | 5.9  | 14.7 |
| XLS-R (2B)        | 36.1 | 27.7 | 15.1 | 22.1 |
| mSLAM-CTC (2B)    | 37.8 | 29.6 | 18.5 | 24.8 |
| Maestro           | 38.2 | 31.3 | 18.4 | 25.2 |
| Zero-Shot Whisper | 36.2 | 32.6 | 25.2 | **29.1** |

The correlation between per-language training data volume and translation BLEU on Fleurs is weaker than for transcription (r² = 0.24), partly because language identification errors in data collection can produce spurious "translation" data. Welsh, for example, appears to have 9,000 hours of translation data but inspection reveals most of it is English audio mislabeled as Welsh, resulting in much worse than expected translation performance.

### 4.4 Language Identification

Language identification accuracy on Fleurs is 64.5% for the best zero-shot Whisper model, compared to 71.4% for w2v-bert-51 and 77.7% for mSLAM (Table 5). However, Whisper is significantly disadvantaged: the training dataset contains no speech data for 20 of the 102 Fleurs languages, creating a hard ceiling of 80.4% accuracy. On the 82 languages where Whisper has training data, the best model achieves 80.3% accuracy, suggesting it is near the ceiling imposed by its training coverage.

**Table 5. Language identification accuracy (%) on Fleurs.**

| Model              | Fleurs |
|--------------------|--------|
| w2v-bert-51 (0.6B) | 71.4   |
| mSLAM-CTC (2B)     | 77.7   |
| Zero-Shot Whisper  | 64.5   |

### 4.5 Noise Robustness

Noise robustness is tested by adding white noise and pub noise (ambient crowd noise from a crowded restaurant or pub, drawn from the Audio Degradation Toolbox; Mauch & Ewert, 2013) at varying signal-to-noise ratios (SNRs) to LibriSpeech test-clean audio, then measuring WER against 14 LibriSpeech-trained baselines.

At low noise levels (high SNR), many supervised LibriSpeech models outperform the zero-shot Whisper model, as expected since those models are specifically trained on LibriSpeech. However, as noise becomes more severe, all supervised models degrade rapidly. Under pub noise at SNR below 10 dB, all 14 compared models perform worse than Whisper. This pattern highlights that Whisper's robustness advantage is most pronounced under naturalistic distribution shifts, such as the background noise encountered in real-world deployment.

### 4.6 Long-Form Transcription

Whisper models process 30-second audio segments and thus require a buffering strategy for longer audio. Transcription of the subsequent window is conditioned on predicted timestamps from the current window, creating the risk of cascading errors.

A set of decoding heuristics was developed to improve reliability (Table 6): beam search with 5 beams, temperature fallback (starting at 0 and increasing by 0.2 to a maximum of 1.0 when log-probability falls below −1 or gzip compression ratio exceeds 2.4), voice activity detection that combines no-speech token probability with average log-probability thresholds, conditioning on the previous window's text when temperature is below 0.5, and constraining the initial timestamp token to between 0.0 and 1.0 seconds.

**Table 6. Incremental improvement from long-form decoding heuristics (average WER %).**

| Strategy                       | Avg WER |
|--------------------------------|---------|
| Greedy decoding only           | 11.0    |
| + Beam search                  | 10.6    |
| + Temperature fallback         | 10.6    |
| + Voice activity detection     | 10.2    |
| + Previous text conditioning   | 10.0    |
| + Initial timestamp constraint | 10.0    |

Long-form performance is evaluated on seven datasets spanning minutes to hours of audio (TED-LIUM3 full talks, The Late Show segments ("Meanwhile"), podcast benchmarks Rev16 and Kincaid46, earnings calls Earnings-21 and Earnings-22, and full-length interviews from CORAAL). Whisper outperforms the best open-source model (NVIDIA STT Conformer-CTC Large) on all seven datasets and competes with or outperforms four commercial ASR services on most of them.

**Comparison with professional human transcribers.** On a subset of 25 Kincaid46 recordings spanning scripted and unscripted broadcast, telephone and VoIP calls, and meetings, transcripts from 5 professional services were collected (one computer-assisted, four entirely human). The computer-assisted service achieves the lowest aggregate WER, 1.15 percentage points better than Whisper. Pure human transcription performance is only a fraction of a percentage point better than Whisper, indicating that English ASR performance is very close to human-level accuracy.

---

## 5. Analysis

### 5.1 Model Scaling

To characterize how performance changes with model capacity, zero-shot performance was measured across the five model sizes on English speech recognition, multilingual speech recognition (Fleurs), X→English translation (CoVoST2), and language identification (Fleurs). Across all tasks except English speech recognition, performance continues to improve reliably with model size. The apparent saturation in English speech recognition is consistent with the finding that even the largest Whisper model is very close to human-level error rates on that task, suggesting that further improvement is constrained by the irreducible difficulty of the data rather than model capacity.

Notably, multitask and multilingual models scale better with compute than English-only models trained for equivalent FLOPs on English data. For small models, joint training causes negative transfer, reducing English speech recognition performance relative to an English-only model of the same effective compute. But for large models, the joint models outperform their English-only counterparts, demonstrating positive transfer from multilingual and multitask training at scale.

### 5.2 Dataset Scaling

To measure the contribution of dataset size, a series of medium-sized models were trained on subsets ranging from 0.5% to 100% of the full 680,000-hour dataset (Table 7).

**Table 7. Performance as a function of dataset size.**

| Dataset size (hours) | English WER (↓) | Multilingual WER (↓) | X→En BLEU (↑) |
|----------------------|-----------------|----------------------|----------------|
| 3,405                | 30.5            | 92.4                 | 0.2            |
| 6,811                | 19.6            | 72.7                 | 1.7            |
| 13,621               | 14.4            | 56.6                 | 7.9            |
| 27,243               | 12.3            | 45.0                 | 13.9           |
| 54,486               | 10.9            | 36.4                 | 19.2           |
| 681,070              | 9.9             | 29.2                 | 24.8           |

All increases in dataset size improve performance on all tasks. English speech recognition improves rapidly up to 13,000 hours, then slows. Multilingual speech recognition follows a power-law trend up to 54,000 hours before also slowing. X→English translation performance is near zero until around 7,000 hours, then improves roughly log-linearly until 54,000 hours. The general pattern of diminishing returns between 54,000 and 680,000 hours suggests that current Whisper models may be undertrained relative to dataset size, and further improvements may be achievable with longer training on larger models or through better characterization of scaling laws for speech recognition.

---

## 6. Related Work

**Scaling supervised speech recognition.** Deep learning approaches to speech recognition have consistently benefited from scale. Early systems showed that model depth and size improve performance and that the benefit grows with training data (Mohamed et al., 2009; Seide et al., 2011). Weakly supervised data augmentation was first demonstrated at scale in Liao et al. (2013) and further developed in Deep Speech 2 (Amodei et al., 2015). Semi-supervised approaches (Narayanan et al., 2018) and large-scale self-supervised pre-training (Baevski et al., 2020; Hsu et al., 2021a) have since extended coverage to hundreds of thousands and millions of hours of speech, respectively. Whisper differs by focusing on the supervised regime but at an unprecedented scale and breadth of coverage.

**Multitask learning.** Multitask learning (Caruana, 1997) has been applied to speech for over a decade, including multilingual speech recognition with shared models (Schultz & Kirchhoff, 2006; Toshniwal et al., 2018) and massive multilingual models for 50 languages (Pratap et al., 2020a). The use of task-specifying tokens in a shared encoder-decoder was demonstrated for machine translation by Johnson et al. (2017). The "text-to-text" framework (McCann et al., 2018; Raffel et al., 2020) and its application to language modeling (Radford et al., 2019) popularized this approach in NLP. MUTE (Wang et al., 2020c) and mSLAM (Bapna et al., 2022) extended joint training over both speech and text language tasks.

**Robustness.** The problem of distribution shift in machine learning has been extensively studied. Torralba & Efros (2011) documented dataset bias and poor cross-dataset generalization over a decade ago; many subsequent works have replicated the finding across NLP (Jia & Liang, 2017; Hendrycks et al., 2020), computer vision (Barbu et al., 2019; Recht et al., 2019), and question answering (Miller et al., 2020). Taori et al. (2020) introduced the concept of effective robustness used in this paper's analysis. Multi-domain training as a path to robustness has been demonstrated in speech (Narayanan et al., 2018; Chan et al., 2021) and computer vision (Radford et al., 2021).

---

## 7. Limitations and Future Work

The analysis identifies several areas for further improvement.

**Decoding reliability in long-form settings.** Many remaining errors in long-form transcription are not perceptual in nature. They include sequence-to-sequence failure modes such as repetition loops, hallucinated text unrelated to the audio, and failure to transcribe the first or last few words of a segment. These are addressed only partially by the heuristics in Section 4.6; fine-tuning on high-quality supervised data or reinforcement learning optimized for decoding quality may reduce them further.

**Low-resource language coverage.** As Figure 3 of the source paper shows, WER on many languages remains high and is strongly predicted by training data volume. The current dataset is heavily English-biased due to the English-centric regions of the internet that were sampled. A targeted effort to collect more data for low-resource languages could yield large gains in multilingual performance with modest increases in total dataset size.

**Zero-shot only evaluation.** The robustness focus of this work leads to evaluating exclusively in the zero-shot setting. Fine-tuning on high-quality in-distribution data likely improves performance further and would enable direct comparison with prior work that uses the standard fine-tuning protocol.

**Role of the decoder.** It remains unclear whether Whisper's robustness advantage stems from the encoder, the decoder, or both. Since Whisper's decoder is a language model conditioned on audio, it may capture long-range context that CTC-based decoders lack. Isolating decoder contributions—for example, by pairing existing speech encoders such as wav2vec 2.0 with a separately trained language model—is identified as an important avenue for understanding the source of robustness gains.

**Lack of unsupervised pre-training.** Whisper achieves strong performance without any self-supervised or self-training objectives that are standard in recent large-scale ASR work. It is possible that incorporating such objectives could further improve performance.

---

## 8. Conclusion

Whisper demonstrates that the simple approach of scaling weakly supervised pre-training for speech recognition has been underappreciated relative to unsupervised pre-training methods. By training an off-the-shelf encoder-decoder Transformer on 680,000 hours of diverse, internet-sourced audio with transcripts, and evaluating in a zero-shot transfer setting, models are obtained that approach human-level accuracy and robustness across a wide range of English benchmarks and languages. The key finding—that zero-shot Whisper models achieve 55.2% average relative error reduction over supervised LibriSpeech-trained models on out-of-distribution datasets while matching them on LibriSpeech—highlights the importance of distinguishing in-distribution from out-of-distribution generalization when comparing machine and human performance. A unified multitask format supporting transcription, translation, voice activity detection, language identification, and timestamp prediction across 99 languages makes Whisper directly applicable to diverse real-world deployment conditions without any dataset-specific adaptation.

---

## References

Amodei, D. et al. Deep speech 2: end-to-end speech recognition in English and Mandarin. arXiv:1512.02595, 2015.

Babu, A. et al. XLS-R: Self-supervised cross-lingual speech representation learning at scale. arXiv:2111.09296, 2021.

Baevski, A., Zhou, H., Mohamed, A., and Auli, M. wav2vec 2.0: A framework for self-supervised learning of speech representations. arXiv:2006.11477, 2020.

Baevski, A., Hsu, W.-N., Conneau, A., and Auli, M. Unsupervised speech recognition. *Advances in Neural Information Processing Systems*, 34:27826–27839, 2021.

Bapna, A. et al. mSLAM: Massively multilingual joint pre-training for speech and text. arXiv:2202.01374, 2022.

Barbu, A. et al. ObjectNet: A large-scale bias-controlled dataset for pushing the limits of object recognition models. *Advances in Neural Information Processing Systems*, 32, 2019.

Caruana, R. Multitask learning. *Machine Learning*, 28(1):41–75, 1997.

Chan, W. et al. SpeechStew: Simply mix all available speech recognition data to train one large neural network. arXiv:2104.02133, 2021.

Chen, G. et al. GigaSpeech: An evolving, multi-domain ASR corpus with 10,000 hours of transcribed audio. arXiv:2106.06909, 2021.

Chen, Z. et al. Maestro: Matched speech text representations through modality matching. arXiv:2204.03409, 2022b.

Child, R., Gray, S., Radford, A., and Sutskever, I. Generating long sequences with sparse Transformers. arXiv:1904.10509, 2019.

Collobert, R. et al. Natural language processing (almost) from scratch. *Journal of Machine Learning Research*, 12:2493–2537, 2011.

Conneau, A. et al. Fleurs: Few-shot learning evaluation of universal representations of speech. arXiv:2205.12446, 2022.

Del Rio, M. et al. Earnings-21: a practical benchmark for ASR in the wild. arXiv:2104.11348, 2021.

Galvez, D. et al. The People's Speech: A large-scale diverse English speech recognition dataset for commercial usage. arXiv:2111.09344, 2021.

Geirhos, R. et al. Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2(11):665–673, 2020.

Ghorbani, B. et al. Scaling laws for neural machine translation. arXiv:2109.07740, 2021.

Hendrycks, D. and Gimpel, K. Gaussian error linear units (GELUs). arXiv:1606.08415, 2016.

Hendrycks, D. et al. Pretrained Transformers improve out-of-distribution robustness. arXiv:2004.06100, 2020.

Hernandez, F. et al. TED-LIUM 3: twice as much data and corpus repartition for experiments on speaker adaptation. In *SPECOM*, 2018.

Hsu, W.-N. et al. HuBERT: Self-supervised speech representation learning by masked prediction of hidden units. *IEEE/ACM Transactions on Audio, Speech, and Language Processing*, 29:3451–3460, 2021a.

Huang, G. et al. Deep networks with stochastic depth. In *ECCV*, pp. 646–661, 2016.

Jia, R. and Liang, P. Adversarial examples for evaluating reading comprehension systems. arXiv:1707.07328, 2017.

Johnson, M. et al. Google's multilingual neural machine translation system: Enabling zero-shot translation. *Transactions of the Association for Computational Linguistics*, 5:339–351, 2017.

Koenecke, A. et al. Racial disparities in automated speech recognition. *Proceedings of the National Academy of Sciences*, 117(14):7684–7689, 2020.

Kolesnikov, A. et al. Big Transfer (BiT): General visual representation learning. In *ECCV*, pp. 491–507, 2020.

Likhomanenko, T. et al. Rethinking evaluation in ASR: Are our models robust enough? arXiv:2010.11745, 2020.

Liao, H., McDermott, E., and Senior, A. Large scale deep neural network acoustic modeling with semi-supervised training data for YouTube video transcription. In *IEEE ASRU*, pp. 368–373, 2013.

Loshchilov, I. and Hutter, F. Decoupled weight decay regularization. arXiv:1711.05101, 2017.

Luong, M.-T. et al. Multi-task sequence to sequence learning. arXiv:1511.06114, 2015.

Mahajan, D. et al. Exploring the limits of weakly supervised pretraining. In *ECCV*, pp. 181–196, 2018.

Mauch, M. and Ewert, S. The audio degradation toolbox and its application to robustness evaluation. In *ISMIR*, 2013.

McCann, B. et al. The natural language decathlon: Multitask learning as question answering. arXiv:1806.08730, 2018.

Miller, J. et al. The effect of natural distribution shift on question answering models. In *ICML*, 2020.

Mohamed, A.-r., Dahl, G., and Hinton, G. Deep belief networks for phone recognition. In *NIPS Workshop on Deep Learning for Speech Recognition*, 2009.

Narayanan, A. et al. Toward domain-invariant speech recognition via large scale training. In *IEEE SLT*, pp. 441–447, 2018.

Panayotov, V. et al. LibriSpeech: an ASR corpus based on public domain audio books. In *ICASSP*, pp. 5206–5210, 2015.

Park, D. S. et al. SpecAugment: A simple data augmentation method for automatic speech recognition. arXiv:1904.08779, 2019.

Pascanu, R., Mikolov, T., and Bengio, Y. On the difficulty of training recurrent neural networks. In *ICML*, pp. 1310–1318, 2013.

Polyak, B. T. and Juditsky, A. B. Acceleration of stochastic approximation by averaging. *SIAM Journal on Control and Optimization*, 30(4):838–855, 1992.

Pratap, V. et al. Massively multilingual ASR: 50 languages, 1 model, 1 billion parameters. *arXiv:2007.03001*, 2020a.

Pratap, V. et al. MLS: A large-scale multilingual dataset for speech research. arXiv:2012.03411, 2020b.

Press, O. and Wolf, L. Using the output embedding to improve language models. In *EACL*, pp. 157–163, 2017.

Provilkov, I., Emelianenko, D., and Voita, E. BPE-Dropout: Simple and effective subword regularization. arXiv:1910.13267, 2019.

Radford, A. et al. Language models are unsupervised multitask learners. 2019.

Radford, A. et al. Learning transferable visual models from natural language supervision. arXiv:2103.00020, 2021.

Raffel, C. et al. Exploring the limits of transfer learning with a unified text-to-text Transformer. *Journal of Machine Learning Research*, 21(140):1–67, 2020.

Recht, B. et al. Do ImageNet classifiers generalize to ImageNet? In *ICML*, pp. 5389–5400, 2019.

Russakovsky, O. et al. ImageNet large scale visual recognition challenge. *International Journal of Computer Vision*, 115(3):211–252, 2015.

Schultz, T. and Kirchhoff, K. *Multilingual Speech Processing*. Elsevier, 2006.

Seide, F. et al. Feature engineering in context-dependent deep neural networks for conversational speech transcription. In *IEEE ASRU*, pp. 24–29, 2011.

Sennrich, R., Haddow, B., and Birch, A. Neural machine translation of rare words with subword units. arXiv:1508.07909, 2015.

Sutskever, I., Vinyals, O., and Le, Q. V. Sequence to sequence learning with neural networks. *Advances in Neural Information Processing Systems*, 27, 2014.

Taori, R. et al. Measuring robustness to natural distribution shifts in image classification. *Advances in Neural Information Processing Systems*, 33:18583–18599, 2020.

Torralba, A. and Efros, A. A. Unbiased look at dataset bias. In *CVPR*, pp. 1521–1528, 2011.

Toshniwal, S. et al. Multilingual speech recognition with a single end-to-end model. In *ICASSP*, pp. 4904–4908, 2018.

Valk, J. and Alümäe, T. VoxLingua107: a dataset for spoken language recognition. In *IEEE SLT*, pp. 652–658, 2021.

Vaswani, A. et al. Attention is all you need. In *Advances in Neural Information Processing Systems*, pp. 5998–6008, 2017.

Wang, C. et al. CoVoST 2 and massively multilingual speech-to-text translation. arXiv:2007.10310, 2020b.

Wang, C. et al. Multitask training with text data for end-to-end speech recognition. arXiv:2010.14318, 2020c.

Wang, C. et al. VoxPopuli: A large-scale multilingual speech corpus for representation learning, semi-supervised learning and interpretation. arXiv:2101.00390, 2021.

Zhang, Y. et al. BigSSL: Exploring the frontier of large-scale semi-supervised learning for automatic speech recognition. arXiv:2109.13226, 2021.
