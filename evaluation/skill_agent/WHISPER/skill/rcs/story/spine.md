# Paper Spine — Whisper (Radford et al., 2022)

**1 Problem** {C001}
Automatic speech recognition (ASR) systems trained on a single dataset distribution achieve very low error rates on that distribution but make far more errors than humans when applied elsewhere — a robustness gap that limits their reliability in real deployment settings.

**2 Gap** {C001}
Existing high-performing approaches either (a) rely on unsupervised audio pre-training followed by dataset-specific fine-tuning, which reintroduces distributional brittleness, or (b) combine high-quality supervised datasets totalling only ~5,000 hours — too small to learn broad robustness from diverse speech conditions.

**3 Question** {C002}
Can scaling weakly supervised pretraining — using 680,000 hours of diverse, noisily labeled internet audio — produce a single ASR model that generalizes zero-shot to diverse conditions without any dataset-specific fine-tuning?

**4 Approach** {C002} {C005}
Train an encoder-decoder Transformer (Whisper) on 680,000 hours of internet audio paired with transcripts, representing multilingual transcription, speech-to-English translation, voice activity detection, and language identification as a unified token sequence prediction task.

**5 Key Finding** {C003}
Despite matching a top supervised LibriSpeech model on its home benchmark (both at 2.7% word error rate), zero-shot Whisper achieves 55.2% average relative error reduction over that model on 13 other speech recognition datasets, approaching human levels of robustness and accuracy. {C004}

**6 Meaning** {C003} {C004}
The robustness gap between humans and ASR systems is not primarily a capacity problem but a distribution-coverage problem: training on sufficiently large and diverse supervised data, even if noisily labeled, produces a model that generalizes much as humans do across varied acoustic conditions.

**7 Main Limit** {L003} {L004} {L010}
The study evaluates only zero-shot transfer; fine-tuning is untested. Performance on low-resource languages remains poor, and the text normalization used to evaluate Whisper was developed alongside the model, introducing potential evaluation bias on some benchmarks.
