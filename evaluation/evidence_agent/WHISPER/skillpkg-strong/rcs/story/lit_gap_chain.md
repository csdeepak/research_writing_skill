# Literature -> Gap -> Question chain

DIMENSION: evaluation methodology (SRC-001)
  ACHIEVES: a principled way (effective robustness) to separate "more accurate on this test set" from "more robust to distribution shift" {C002 uses this framework}.
  SHARED ASSUMPTION: a reference in-distribution dataset can be matched across models to isolate the shift effect.
  EVIDENCE OF FAILURE: not applicable to this dimension (a methodology, not a claim under test).
  UNRESOLVED: whether models built on self-supervised pretraining plus fine-tuning (evidence: E040, E041 in the internal evidence map) actually achieve this kind of robustness without per-dataset fine-tuning, since only the fine-tuned setting is well studied.

DIMENSION: human performance reference (SRC-002, SRC-003)
  ACHIEVES: SRC-003 documents that supervised, in-distribution ASR error on LibriSpeech test-clean fell from 5.3% to 1.4% (73% relative), while SRC-002 put human-level error at 5.8% on the same benchmark.
  SHARED ASSUMPTION: progress measured in-distribution on a single benchmark tracks real-world, out-of-distribution usefulness.
  EVIDENCE OF FAILURE: the paper's own evidence notes this gap is confounded because machine performance is usually measured in-distribution while human performance is effectively measured out-of-distribution (E046) — i.e., the "gap" in the literature may be an artifact of how it is measured, not (only) a genuine capability gap.
  UNRESOLVED: no source in this evidence package isolates whether closing that measurement confound, rather than further in-distribution accuracy gains, is what would close the human-machine gap.

GAP (scoped to the sources available in this evidence package): among the works this project cites for evaluation methodology and human/supervised performance references, none directly tests whether a single model, trained without self-supervision or per-dataset fine-tuning, can match the robustness that the effective-robustness framework would expect from a truly generalizing system.

QUESTION: RQ = "Can scaling weakly supervised training data alone, with no self-supervised pretraining and no per-dataset fine-tuning, produce a model that is robust (in the effective-robustness sense) across many datasets, languages, and conditions, closing most of the measured human-machine gap?"

Chain rule check: with only three verifiable sources, the "achieves"/"shared assumption" parts above are scoped to those specific sources, not to "the field" in general; the broader claim that self-supervised-plus-fine-tuning is the field's dominant paradigm is carried instead by the project's own evidence items (E040, E041), and is presented in the paper as the authors' own framing rather than as an independently verified literature survey.
