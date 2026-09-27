# Paper Architecture

Pattern: Method-first (Problem → Gap → Method → Properties/Experiments → Discussion)
Venue: Generic journal/conference (adjacent ML audience, Mode B)

## Section 1: Abstract (~250 words)
- Compress spine lines 1-7
- State problem (ASR robustness gap), approach (680k hours, multitask Transformer), key finding (55.2% RER, human-level robustness), and main limit

## Section 2: Introduction (~700 words)
Slots:
- P1: Hook — the paradox of superhuman ASR that fails in the wild [N01, N02; C001]
- P2: Why current approaches fail — in-distribution focus, fine-tuning brittleness [N03, N04; C001]
- P3: CV analogy — weak supervision at scale improves robustness [N05; SRC005, SRC006]
- P4: Gap and this work's answer [N06, N07; C002]
- P5: Contributions and scope (multitask, multilingual) [N08, N11; C005]
- P6: Paper map

## Section 3: Background (~400 words)
Slots:
- P1: Define ASR and WER for adjacent readers; explain why WER is tricky to compare across distributions
- P2: Unsupervised pretraining paradigm (wav2vec 2.0, etc.) and its limitation: fine-tuning required
- P3: Multi-domain supervised training and its scale limitations (~5k hours best prior)
- P4: Effective robustness as an evaluation concept (Taori et al., 2020)

## Section 4: Method (~600 words)
Slots:
- P1: Training data construction — internet audio-transcript pairs, 680k hours, filtering pipeline [E001, E028]
- P2: Dataset composition and tasks [E001, E003]
- P3: Model architecture — encoder-decoder Transformer, Mel spectrogram input, model family sizes [E002]
- P4: Multitask training format — token-based task specification, 4 tasks unified [E003]
- P5: Training details [E029, E030]

## Section 5: Results (~1000 words)
Sub-sections:
5.1 English speech recognition robustness [C003; E004, E005, E031]
  - P1: In-distribution parity on LibriSpeech
  - P2: 55.2% RER on OOD datasets; table/figure summary
  - P3: Even smallest Whisper competitive with best supervised on OOD
5.2 Human-level accuracy [C004, C009; E008, E015]
  - P1: Figure 2 interpretation (robustness frontier)
  - P2: Kincaid46 human comparison
5.3 Multilingual recognition [C012; E009, E010]
  - P1: MLS and VoxPopuli results
  - P2: Data-performance scaling law across languages
5.4 Translation and language identification [C010, C013; E011, E012]
  - P1: CoVoST2 BLEU results
  - P2: Language ID limitations
5.5 Long-form transcription [C011; E014, E019]
  - P1: Setup and heuristics
  - P2: Comparison with commercial services

## Section 6: Analysis and Ablations (~700 words)
Sub-sections:
6.1 Model scale [C006; E016]
6.2 Data scale [C007; E017]
6.3 Multitask and multilingual transfer [C008; E018]
6.4 Noise robustness [E013]
6.5 Text normalization validity [E027; L004]

## Section 7: Discussion (~500 words)
Slots:
- P1: Why does zero-shot diversity beat in-distribution specialization? [N19; C003]
- P2: The human comparison reframing — what 'superhuman' on LibriSpeech really means [C001]
- P3: Relationship to weak supervision in CV [SRC005, SRC006, SRC007]
- P4: Limitations — fine-tuning not studied, normalizer development, low-resource gaps [N21; L003, L004, L010]

## Section 8: Related Work (~300 words)
Slots:
- P1: Scaling in ASR — deep learning history
- P2: Self-supervised and unsupervised pretraining
- P3: Multitask learning in speech
- P4: Robustness in ML generally

## Section 9: Conclusion (~200 words)
- Compress spine lines 4-7
- The promise of simple scaling with diverse supervision
- Open questions
