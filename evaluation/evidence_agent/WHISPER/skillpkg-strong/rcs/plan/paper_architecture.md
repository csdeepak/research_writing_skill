# Paper Architecture

Story pattern: question_led (with an IMRaD-like section shell, per the generic venue profile).
Audience mode: B (adjacent ML researcher) · Binding personas: A, B, E · Venue profile: plan/venue_profile.yaml (generic, assumed_rules: structure, limits, style, required_statements = 4)

| # | Section | Story node(s) | Reader question | Point | Claims | Density | Table | New terms |
|---|---------|---------------|------------------|-------|--------|---------|-------|-----------|
| I.1 | Introduction | N01,N02 | Problem/why care | Speech systems tuned to one distribution need fine-tuning and degrade under shift | C021 | CORE | - | zero-shot |
| I.2 | Introduction | N03,N04 | What's missing | Self-supervised encoders still need fine-tuned decoders; human-machine gap may be a measurement artifact | C017 | CORE | - | - |
| I.3 | Introduction | N05,N06 | The question | Can scaling weak supervision alone give robust zero-shot transfer? | - | CORE | - | weak supervision |
| I.4 | Introduction | N07 | The approach | One Transformer trained on 680k hours across tasks/languages | C001,C020 | CORE | - | - |
| I.5 | Introduction | N18 | Contribution + map | Contributions list + paper map by question | C002,C004,C013,C016 | CORE | - | - |
| M.1 | Method | N07 | What exactly was built | Architecture, data, multitask format | C001,C020,C021 | CORE | Table 1 (model sizes) | WER |
| M.2 | Method | N08 | How is robustness measured | Zero-shot protocol + effective-robustness framework | - | CORE | - | effective robustness |
| R.1 | Results | N09 | English ASR robustness | 55.2% relative error reduction; the 2.5/2.7 conflict disclosed | C002,C003 | CORE | Table 2 | - |
| R.2 | Results | N10 | Noise & long-form | Noise robustness + long-form beats open-source, near-human | C010,C011,C012,C013 | CORE | Table 3 (decoding ablation) | long-form transcription |
| R.3 | Results | N11 | Translation | 29.1 BLEU SOTA claim, high-resource shortfall | C004,C009 | CORE | Table 4 | BLEU |
| R.4 | Results | N12 | Multilingual/lang ID | Mixed: beats MLS, underperforms VoxPopuli/Fleurs lang ID | C007,C008 | CORE | Table 5 | - |
| R.5 | Results | N13,N14 | What drives it: scale | Data-scaling ablation + per-language correlation | C005,C006,C014,C015 | CORE | Table 6 | - |
| D.1 | Discussion | N15,N16,N17 | So what does it mean | Interpretation: scale drives robustness; gap may be measurement artifact; saturation | C016,C017,C018 | CORE | - | - |
| D.2 | Discussion/Limitations | N19 | What's the catch | Diminishing returns, zero-shot only, English-heavy data, no variance | L001-L004 | CORE | - | - |
| D.3 | Conclusion | N18,N20,N21 | What follows | Contribution restated; implication; future work | C016,C019 | CORE | - | - |

## Checks
- [x] Every story-graph node appears in >=1 row (N01-N21; N22 background concept folded into first-use definitions, not a standalone row).
- [x] The single RQ has result rows (R.1-R.5), interpretation rows (D.1), and discussion rows (D.1-D.2).
- [x] No row without a story node.
- [x] Question ledger: 0 debt at end of each section (see story/question_ledger.json).
- [x] Term ledger: defining row precedes first-use row for every term.
- [x] No images (task constraint); Tables 1-6 replace the paper's figures/tables using markdown; each has a card below.
- [x] Negative results (E019, E022, E024, E031, E038) placed per negative_result_decisions (all reported_main).
