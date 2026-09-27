# Scaling Weakly Supervised Data for Robust, Zero-Shot Speech Recognition and Translation

## Abstract

Automatic speech recognition (ASR) systems built around self-supervised pretraining typically still need a decoder that is fine-tuned on each target dataset before it can produce usable transcripts, and even fine-tuned systems can lose much of their accuracy once the input audio distribution shifts away from what they were tuned on {C021}. This makes it hard to tell whether a system is genuinely robust to new conditions or merely well matched to the one benchmark it was measured on — a distinction sharpened by the possibility that machine transcription is usually evaluated in-distribution while human transcription is effectively evaluated out-of-distribution {C017}. We examine whether scaling weakly supervised training data alone, without self-supervised pretraining or any dataset-specific fine-tuning, can close this gap. We study Whisper, a single encoder-decoder Transformer trained end-to-end on 680,000 hours of multitask, multilingual audio-transcript data spanning 96 languages, and evaluate it zero-shot across a broad suite of speech benchmarks {C001}. Matched to a supervised model on LibriSpeech, zero-shot Whisper reduces average word error rate (WER, the fraction of words a transcript gets wrong) by 55.2% across 12 other English datasets (29.3 to 12.8) {C002}, approaches professional human transcription accuracy on long-form audio {C013}, and reaches 29.1 BLEU (a standard translation-quality score) on CoVoST2 speech translation into English, which the original authors report as a new state of the art for that benchmark {C004}. Gains from additional training data diminish sharply beyond roughly 54,000 hours, however, and multilingual recognition, language identification, and translation on the highest-resource languages still trail specialized supervised systems {C007, C008, C009, C014}; every reported figure in the underlying evidence is a single run without a variance estimate {L001}. The results support the interpretation that scale of weakly supervised data, rather than self-supervised representation learning, is a substantial and comparatively simple driver of cross-distribution robustness in speech systems {C016}.

## 1. Introduction

Speech recognition systems that are trained and then fine-tuned on a single dataset's distribution routinely reach very low error rates on that dataset's held-out test set, but their accuracy can fall sharply when the input audio comes from a different distribution — a different recording setup, accent mix, background noise level, or topic {C021}. Because most deployed uses of a speech system involve exactly this kind of shift (new speakers, new microphones, new recording conditions), a model's in-distribution test score is a weak proxy for how useful it will actually be.

One influential route to more general speech models is self-supervised pretraining on large amounts of unlabeled audio, which learns high-quality internal representations without needing transcripts. In the available evidence, however, such encoders still require a decoder fine-tuned on labeled, in-distribution data before they produce transcripts, so their behavior without any fine-tuning is not directly characterized. Separately, the field has long noted a substantial gap between human and machine transcription accuracy. The available evidence records a specific hypothesis for that gap: it may be inflated by how the comparison is usually made, since machine systems are typically evaluated in-distribution (fine-tuned and tested on the same benchmark) while humans are, in effect, evaluated out-of-distribution (given audio they never specifically prepared for) {C017}. If so, a fairer comparison — holding both humans and machines to a genuinely zero-shot setting — should narrow the apparent gap.

This paper asks: **can scaling weakly supervised (audio, transcript) pairs alone, with no self-supervised pretraining step and no fine-tuning on any target dataset, produce a single speech model that generalizes zero-shot across datasets, languages, and acoustic conditions?** "Weakly supervised" here means the audio-transcript pairs are collected from existing sources rather than hand-verified by annotators, so individual pairs may be noisy, but the pairing itself gives the model direct supervision on the transcription task from the start, unlike a self-supervised encoder that never sees transcripts during pretraining.

The paper answers this question with Whisper, a single off-the-shelf encoder-decoder Transformer trained end-to-end on 680,000 hours of audio paired with transcripts and translations, collected from the internet and covering 96 languages {C001}. Training examples specify which task to perform (transcribe in the source language, translate into English, detect the language, or predict timestamps) as part of the input sequence, so one model handles several tasks without task-specific architectures. The resulting models are evaluated **zero-shot**: without using any of the training data belonging to the benchmark being tested, and without fine-tuning on it.

This data-scaling approach yields three main contributions: (1) matched to a supervised baseline on LibriSpeech, zero-shot Whisper cuts average error by more than half on 12 other English datasets {C002}; (2) it gets close to human transcription accuracy on long, unsegmented audio {C013}; and (3) it reaches a new reported state-of-the-art BLEU score on speech translation {C004} — while still trailing specialized systems on some multilingual benchmarks and showing diminishing returns to further data scale {C007, C008, C009, C014}. Together, these contributions support data scale, rather than self-supervision or fine-tuning, as a substantial contributor to cross-distribution robustness {C016}. Section 2 describes the model, data, and evaluation framework; Section 3 presents results for English recognition, noise and long-form robustness, translation, and multilingual recognition, then the scaling analysis that helps explain them; Section 4 discusses what these results do and do not establish; Section 5 concludes.

## 2. Method

### 2.1 Model and training data

Whisper is an off-the-shelf encoder-decoder Transformer {C020}. Audio is resampled to 16,000 Hz and converted into an 80-channel log-magnitude Mel spectrogram computed over 25-millisecond windows with a 10-millisecond stride, which is the only input representation the encoder receives. The model family spans five sizes built from the same architecture, summarized in Table 1.

**Table 1. Whisper model family.** Parameter count and Transformer width for each of the five original model sizes.

| Model | Layers | Width | Attention heads | Parameters |
|---|---|---|---|---|
| Tiny | 4 | 384 | 6 | 39M |
| Base | 6 | 512 | 8 | 74M |
| Small | 12 | 768 | 12 | 244M |
| Medium | 24 | 1024 | 16 | 769M |
| Large | 32 | 1280 | 20 | 1550M |

*Non-conclusion: this table describes architecture only; accuracy as a function of size is reported separately in Section 3.5.*

The training set totals 680,000 hours of audio-transcript pairs {C001}; a more precise count from the paper's own dataset-scaling analysis puts the full set at 681,070 hours {E005}, broken down by task as 438,218 hours (65%) of English speech recognition data, 117,113 hours (17%) of multilingual speech recognition data covering the other 95 languages, and 125,739 hours (18%) of X-to-English translation data {E004}. All of it is weakly supervised: transcripts and translations are taken as found, filtered by automated heuristics that detect likely machine-generated transcripts, and by an audio-language detector (itself fine-tuned on an existing language-identification dataset) that checks the spoken language against the transcript's stated language {E035}. Training runs for only two to three passes over this large dataset, so the authors treat over-fitting as a minor concern for the original models and use no data augmentation or regularization {C001, E048}; a later variant (Large V2, used for most headline results below) instead trains for 2.5 times as many effective epochs and adds SpecAugment, stochastic depth, and BPE dropout, since the added training time reintroduces some over-fitting risk {E008}.

Each decoder input sequence begins with special tokens that specify the language (one of 99 language tokens) and the task (transcription, translation, or others), and timestamps are represented as tokens quantized to the nearest 20 milliseconds when the task calls for them {E034}. This multitask token format is what lets one decoder serve several tasks without separate output heads.

### 2.2 Evaluation: zero-shot and effective robustness

Every benchmark reported in this paper is evaluated **zero-shot**: no part of the target dataset's training split is used, either for pretraining or for fine-tuning {C001 scope; E010}. This is a deliberate departure from the usual practice of fine-tuning a pretrained model on each target dataset, and it is the condition under which the paper's central question can be answered: if scale of weakly supervised data is doing the work, a model with no dataset-specific adaptation should still generalize.

To separate genuine robustness to distribution shift from ordinary in-distribution skill, the paper adopts the **effective robustness** framework (Taori et al., 2020), which compares models after first matching their performance on a reference, in-distribution dataset. Here, LibriSpeech — a widely used, clean, read-speech benchmark — serves as the reference, and a suite of 12 other academic speech-recognition datasets, chosen to vary in recording condition, accent, and domain, serves as the out-of-distribution suite {E011}. A model that is simply "more accurate overall" would improve on both the reference and the out-of-distribution suite together; a model that is specifically more *robust* improves disproportionately on the out-of-distribution suite once it is matched to a comparison model on the reference. All WER values below are computed after applying the same text normalizer to model output and references, which standardizes formatting differences (such as punctuation and number formatting) that would otherwise inflate error counts without reflecting genuine transcription mistakes.

## 3. Results

### 3.1 English speech recognition is substantially more robust than a matched supervised baseline

**Table 2. Average WER (%) on LibriSpeech and 12 other datasets.** wav2vec 2.0 Large, fine-tuned on LibriSpeech, versus zero-shot Whisper Large V2, after the shared text normalizer. RER = relative error reduction.

| Model | LibriSpeech test-clean WER | Average WER, 12 other datasets | RER on the 12 other datasets |
|---|---|---|---|
| wav2vec 2.0 Large (supervised) | 2.7 | 29.3 | — |
| Zero-shot Whisper Large V2 | 2.7 | 12.8 | 55.2% |

Matched to wav2vec 2.0 Large on LibriSpeech test-clean — both models reach 2.7% WER there — zero-shot Whisper Large V2 reaches an average WER of 12.8% on the 12 other datasets, against 29.3% for the matched supervised model, a 55.2% relative reduction in errors {C002}. Because the two models are equal on the reference dataset, this gap is attributable to robustness rather than to Whisper simply being the more accurate model overall: it is disproportionately better once the input distribution shifts away from LibriSpeech. This is the paper's central empirical result and the main basis for its central claim.

One number in the underlying evidence does not fully agree with this table: prose elsewhere states that the best zero-shot Whisper model reaches a LibriSpeech test-clean WER of 2.5%, rather than the 2.7% shown in Table 2 for the same quantity {C003}. Both values are reported in the source material and neither could be reconciled from the evidence available for this paper (the appendix tables that might resolve it were not machine-readable), so we report both here rather than silently choosing one [MISSING RESULT: a reconciled LibriSpeech test-clean WER for the best Whisper model]. The discrepancy does not change the qualitative comparison in Table 2, which uses the same value (2.7%) for both models on the reference dataset {C003}.

The pattern also holds at the small end of the model family: the smallest Whisper model, with only 39 million parameters, reaches a LibriSpeech test-clean WER of 6.7%, which the underlying evidence describes as roughly competitive with the best fully supervised LibriSpeech model on other datasets — that is, even a small zero-shot model can match a much more specialized, fine-tuned system's out-of-distribution behavior, though the smallest model is well behind Whisper Large V2 on the in-distribution benchmark itself {C002, C020}.

For context on how far in-distribution, fully supervised progress has gone on this benchmark: the state of the art on LibriSpeech test-clean fell from 5.3% to 1.4%, a further 73% relative drop, while reported human-level error on the same benchmark is 5.8% (Amodei et al., 2015; Zhang et al., 2021). These figures indicate that specialized, fine-tuned systems now clear both the older human-level estimate and Whisper's zero-shot accuracy by a wide margin on the reference dataset itself; the claim in this paper is about robustness under distribution shift, not about matching the best in-distribution specialist.

### 3.2 Robustness extends to additive noise and long, unsegmented audio

Under additive background noise, zero-shot Whisper remains more accurate than all 14 compared models trained on LibriSpeech once the noise is loud relative to the speech — specifically, under additive pub noise below 10 dB signal-to-noise ratio (SNR). At low noise levels (around 40 dB SNR, i.e. relatively clean audio), several of the LibriSpeech-trained models instead outperform Whisper {C010}. This crossover is consistent with the same robustness story: Whisper is not simply the best model everywhere, but it degrades more gracefully as conditions worsen.

A separate, common real-world condition is **long-form transcription**: audio recordings much longer than a single utterance, such as podcasts or meetings. Whisper's models are trained on 30-second audio chunks and cannot consume a longer recording in one pass, so long-form transcription requires a buffered strategy that slides the model across the recording and stitches the outputs together {C021}. Across seven long-form English datasets, this approach outperforms the best open-source alternative system on every dataset, and beats commercial automatic transcription services in most, though not all, cases {C011}.

**Table 3. Effect of long-form decoding heuristics on average WER (%).** Averaged over seven long-form datasets (TED-LIUM3, Meanwhile, Kincaid46, Rev16, Earnings-21, Earnings-22, CORAAL), heuristics added incrementally.

| Decoding configuration | Average WER |
|---|---|
| Greedy decoding only | 11.0 |
| + Beam search | 10.6 |
| + Temperature fallback | 10.6 |
| + Voice activity detection | 10.2 |
| + Previous-text conditioning | 10.0 |
| + Initial timestamp constraint | 10.0 |

Each heuristic added to the decoding procedure reduces the seven-dataset average further, from 11.0 with plain greedy decoding to 10.0 with the full set {C012}. This reduction is not uniform across the seven datasets — on some individual datasets, an added heuristic increases WER even as the average falls — so Table 3 should be read as a net effect across a heterogeneous set of recordings rather than a uniform improvement {C012}.

On a 25-recording subset of one of these datasets (Kincaid46), where the same audio was also transcribed by four professional human services and one computer-assisted service, Whisper's aggregate WER is close to human-level: it trails the best computer-assisted service by 1.15 percentage points, and it trails the best pure-human service by only what the underlying evidence describes as "a fraction of a percentage point" — a precise figure is not available for the pure-human comparison {C013} [MISSING RESULT: an exact numeric value for the pure-human transcriber advantage on Kincaid46]. This is the most direct human-machine comparison available in the evidence, and it uses a genuinely zero-shot setting for the machine — supporting the hypothesis from Section 1 that measuring both sides under comparable, out-of-distribution conditions narrows the apparent gap {C017}.

### 3.3 Translation into English reaches a new reported state of the art, but not uniformly

On CoVoST2, a benchmark for translating speech in other languages into English text, zero-shot Whisper reaches 29.1 BLEU overall (Table 4), which the original authors report as a new state of the art for this benchmark, evaluated with a simple text standardizer against a comparison set that includes Maestro, mSLAM-CTC, and XLS-R systems, as of September 2022 {C004}. The authors attribute this partly to scale: Whisper's pretraining includes roughly 68,000 hours of X-to-English translation data, compared with CoVoST2's own 861-hour training set, and the margin over the next-best system (mSLAM) is largest — 6.7 BLEU — on the lowest-resource language grouping, where Whisper's data advantage is presumably largest relative to what a specialized system could have used {C004}.

**Table 4. CoVoST2 X-to-English BLEU by resource group.**

| System | High-resource | Mid-resource | Low-resource | All |
|---|---|---|---|---|
| XMEF-X | 34.2 | 20.2 | 5.9 | 14.7 |
| XLS-R (2B) | 36.1 | 27.7 | 15.1 | 22.1 |
| mSLAM-CTC (2B) | 37.8 | 29.6 | 18.5 | 24.8 |
| Maestro | 38.2 | 31.3 | 18.4 | 25.2 |
| Zero-shot Whisper | 36.2 | 32.6 | 25.2 | **29.1** |

This advantage does not hold in every resource group: on the highest-resource languages specifically, zero-shot Whisper (36.2 BLEU) does not improve over Maestro (38.2) or mSLAM-CTC (37.8) {C009}. The overall BLEU advantage is concentrated in the mid- and low-resource groups, where Whisper's scale-driven data advantage appears to matter more than the targeted supervision available to specialized systems on high-resource languages.

### 3.4 Multilingual recognition and language identification: a mixed picture

**Table 5. Multilingual results: WER (%, lower better) on MLS and VoxPopuli, and accuracy (%, higher better) on Fleurs language identification.**

| Benchmark | Best supervised/self-supervised baseline | Zero-shot Whisper |
|---|---|---|
| MLS (WER) | 9.7 (mSLAM-CTC 2B) | 7.3 |
| VoxPopuli (WER) | 8.1 (Maestro) | 13.6 |
| Fleurs language ID (accuracy) | 77.7 (mSLAM-CTC 2B) | 64.5 |

Zero-shot Whisper's multilingual results, summarized in Table 5, do not point in one direction {C007, C008}. On MLS, a multilingual speech-recognition benchmark, Whisper reaches 7.3 WER, lower (better) than the compared supervised and self-supervised baselines (9.7-10.9). On VoxPopuli, another multilingual benchmark, Whisper reaches 13.6 WER, worse than three of the four compared baselines (8.1, 9.1, 10.6) and ahead only of VP-10K+FT (15.3), a baseline fine-tuned on relatively little supervised data {C007}. On Fleurs, used here as a language-identification benchmark rather than a transcription benchmark, zero-shot Whisper reaches 64.5% accuracy, underperforming the supervised state of the art (77.7%) by 13.6 percentage points; part of this gap is structural, since 20 of the evaluated languages are unseen in Whisper's training data, which mathematically upper-bounds its accuracy at 80.4%, and on the 82 languages that do overlap with training, the best Whisper model reaches 80.3% accuracy {C008}. The available evidence attributes the VoxPopuli shortfall to the comparison systems having had more exposure to VoxPopuli's own audio distribution during their own pretraining or fine-tuning, together with more supervised data for that benchmark specifically, though this attribution is not independently tested in the material available here {L003}.

At a finer grain, per-language speech-recognition accuracy on Fleurs correlates strongly with how much training data that language had: a squared correlation coefficient of 0.83 between the logarithm of WER and the logarithm of per-language training hours, corresponding to an estimate that WER halves for roughly every 16-fold increase in a language's training data {C005, C006}. The same relationship is much weaker for translation into English (squared correlation 0.24), and one outlier illustrates why: Welsh reaches only 13 BLEU despite reportedly having about 9,000 hours of translation data, which the authors trace to a data-quality problem rather than a translation-difficulty one — the majority of the audio labeled as Welsh in the training data is actually English audio that was mis-classified by the automated language detector {C005, C006}. This is a useful negative result: it shows that the scaling relationship is sensitive to label quality, not just label quantity, and that a language with abundant *nominal* data can still perform poorly if much of that data is mislabeled.

### 3.5 What drives these results: training-data and model scale

**Table 6. Effect of pre-training dataset size on three tasks (medium-sized model).** English WER is averaged over 12 datasets; multilingual WER is on an overlapping Fleurs subset; BLEU is on CoVoST2.

| Dataset size (hours) | English WER | Multilingual WER | X-to-English BLEU |
|---|---|---|---|
| 3,405 | 30.5 | 92.4 | 0.2 |
| 6,811 | 19.6 | 72.7 | 1.7 |
| 13,621 | 14.4 | 56.6 | 7.9 |
| 27,243 | 12.3 | 45.0 | 13.9 |
| 54,486 | 10.9 | 36.4 | 19.2 |
| 681,070 | 9.9 | 29.2 | 24.8 |

All three tasks improve steadily as training data grows across the first five points in Table 6, roughly doubling in size at each step {C014}. The last step is different in kind: moving from 54,486 to the full 681,070 hours — a further 12.5-fold increase — reduces English WER by only about one further percentage point, even though the two smaller preceding doublings each produced larger gains {C014}. This same pattern of diminishing-but-still-positive returns appears across model size as well as dataset size: with the exception of English speech recognition, zero-shot performance keeps increasing with model size across multilingual recognition, translation, and language identification, while English recognition shows earlier-onset diminishing returns {C014}. One caveat qualifies the model-scaling and joint-training pictures together: for smaller models trained with moderate compute, jointly training on all tasks and languages together shows *negative* transfer relative to training an English-only model of the same size — the joint model does worse on English recognition than the English-only one, even after adjusting for the fact that only 65% of the joint model's training compute is spent on English speech recognition {C015}. This negative-transfer pattern reverses at the largest scale studied, where the joint multitask, multilingual models outperform their English-only counterparts {C015}. Reporting this reversal, rather than only the largest-scale result, matters for the paper's central scaling claim: the benefit of joint multitask training over dedicated single-task training is itself scale-dependent, not universal {C015}.

## 4. Discussion

### 4.1 Interpretation

Taken together, the results in Section 3 are consistent with the interpretation that the scale of weakly supervised training data — not self-supervised representation learning, and not fine-tuning — is associated with Whisper's robustness to distribution shift and its near-human long-form accuracy {C016}. Three observations support this reading over a generic "the model is good" reading {C016}: the effective-robustness comparison (3.1), which holds in-distribution accuracy fixed and shows a large out-of-distribution advantage; the noise and long-form results (3.2), where the advantage grows as conditions depart further from clean, short, read speech; and the scaling curve (3.5), where the same three tasks improve together as the same kind of data is added, with no architecture change. This does not rule out a contribution from the architecture or training recipe, since no ablation in the available evidence holds data scale fixed while varying those factors.

The residual gap to human accuracy on long-form transcription (Section 3.2) is also consistent with the hypothesis raised in Section 1: that part of the traditionally reported human-machine gap reflects how the comparison is usually made, rather than how far machine accuracy genuinely lags {C017}. Because the human comparison here uses a zero-shot machine evaluation, and the machine trails only a fraction of a percentage point behind the best human transcribers, the finding is consistent with — though it does not, on its own, isolate — the idea that a fairer, matched-condition comparison narrows the historically reported gap. We flag this as an interpretation the paper's authors offer, not as a separately, directly tested causal claim, since no experiment in the available evidence manipulates the evaluation condition for human transcribers to test this hypothesis directly.

A second interpretation concerns the diminishing returns observed at the largest data scale (Section 3.5). The available evidence offers, and labels as untested, one possible explanation: as English speech recognition performance approaches an apparent ceiling near human-level accuracy, further gains may become harder to obtain regardless of additional data, a saturation effect {C018}. This is presented here as a stated possibility, not a confirmed mechanism, since the evidence does not include an experiment that isolates saturation from other candidate explanations (for instance, remaining label noise in the largest data increments, which is not separately measured).

### 4.2 Limitations

Four limitations bound how far these results can be read.

First, every headline number in this paper — the 55.2% relative error reduction, the 29.1 BLEU translation result, the LibriSpeech WER values, and each point on the data-scaling curve — is a single-run point estimate {L001}. No seeds, repeated runs, or variance figures are reported anywhere in the available evidence, so none of the comparisons above can be described as statistically significant in a formal sense, and the true run-to-run spread of these numbers is unknown {L001}.

Second, several robustness findings (the noise-robustness crossover, the long-form comparison, the negative-transfer curve, and the exact human-transcriber advantage on Kincaid46) are derived from reading figures rather than tabulated numbers, so they are reported here at the precision the source supports — direction and approximate magnitude — rather than to additional decimal places {L002}.

Third, most multilingual, translation, and language-identification comparisons use baseline numbers quoted from those systems' original publications rather than re-measured under Whisper's exact pipeline and normalization. The authors note this as limiting how directly the comparisons can be read as controlled, and it is the likeliest explanation offered for part of the VoxPopuli and high-resource-translation shortfalls, alongside the possibility that those systems simply suit those benchmarks better {L003}.

Fourth, and most directly bounding the central scaling claim: only zero-shot transfer is studied here. No fine-tuning setting is evaluated, so it is not known whether fine-tuning Whisper on a target dataset would close, maintain, or reduce its advantage over specialized systems, nor whether it would change the multilingual shortfalls in Section 3.4 {L004}. Relatedly, the training data remains heavily weighted toward English: most of the other 95 languages have under 1,000 hours of training audio, which plausibly explains much of the multilingual and low-resource-language shortfall, independent of the zero-shot protocol itself. Finally, it is not established how much of Whisper's robustness comes from its encoder (processing the audio), its decoder (behaving as a language model conditioned on that audio), or their combination — no ablation isolating these components' contributions is reported.

## 5. Conclusion

This paper asked whether scaling weakly supervised training data alone, without self-supervised pretraining or dataset-specific fine-tuning, could produce a speech model that generalizes zero-shot across datasets, languages, and conditions. The evidence supports a qualified yes: a single model trained this way narrows the measured gap between machine and human transcription accuracy on English speech, generalizes better than a matched supervised baseline as conditions depart from clean, in-distribution audio, and reaches a new reported state of the art on one translation benchmark, without ever seeing a training example from the datasets it is tested on {C002, C004, C013, C016}. This narrowing is not complete: it comes with diminishing returns past roughly 54,000 hours, and it does not extend evenly to multilingual recognition, language identification, or high-resource translation, where specialized systems still have an edge {C007, C008, C009, C014}.

Two directions follow directly from where the evidence stops. A targeted effort to collect more training data specifically for the lower-resource languages that currently have under 1,000 hours each could plausibly produce a large improvement in average multilingual recognition accuracy, given how strongly per-language accuracy tracks per-language data volume elsewhere in these results {C019}. And because only the zero-shot setting was studied here, a controlled comparison of zero-shot against fine-tuned performance — together with an ablation that isolates the encoder's and decoder's separate contributions to robustness — would directly test how much of the robustness demonstrated in this paper depends on staying zero-shot at all, questions the current evidence leaves open.

## References

Amodei et al. (2015). *[CITATION NEEDED: full bibliographic details; only first author and year are available in the evidence used for this paper. Cited there for a reported human-level LibriSpeech test-clean error rate of 5.8%.]*

Taori et al. (2020). *[CITATION NEEDED: full bibliographic details; only first author and year are available in the evidence used for this paper. Cited there as the origin of the effective-robustness evaluation framework used in Sections 2.2 and 3.1.]*

Zhang et al. (2021). *[CITATION NEEDED: full bibliographic details; only first author and year are available in the evidence used for this paper. Cited there for a reported supervised state-of-the-art LibriSpeech test-clean WER of 1.4%.]*
