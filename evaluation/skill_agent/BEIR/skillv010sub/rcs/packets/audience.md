Intended readers: machine-learning researchers from subfields other than information retrieval — they know general ML, deep learning, standard evaluation practice, and statistics, but not information retrieval's own terminology, datasets, or prior work.

They can be assumed to know: supervised fine-tuning of pretrained Transformer encoders (e.g. BERT); the standard train/dev/test evaluation protocol and the general idea of a benchmark suite; zero-shot evaluation as a general ML concept; general ML/statistical evaluation practice (e.g. why single-run comparisons are weaker evidence than replicated ones); basic ranking/contrastive-loss intuition from representation learning.

They cannot be assumed to know: information-retrieval-specific terminology (qrels, pooling, bi-encoder vs. cross-encoder, late interaction, the lexical gap, Hole@k); information-retrieval evaluation metrics (nDCG@k, MRR, MAP) and why they differ from classification metrics; the specific datasets and architectures being compared (BM25, DPR, ANCE, TAS-B, ColBERT, etc.); prior information-retrieval benchmarks (MultiReQA, KILT) and how this benchmark differs from them.

Binding reader types for this review: A (specialist in an ML subfield adjacent to IR) and B (the primary target: adjacent ML researcher, not an IR specialist) and E (a mixed venue reader, layered from accessible to more precise).

Venue type: standalone research report (no specific venue or reviewer pool was specified for this piece).
