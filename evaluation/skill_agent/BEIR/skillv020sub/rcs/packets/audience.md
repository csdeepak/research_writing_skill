Intended readers: machine-learning researchers from other subfields (adjacent researchers) --
they know general ML, deep learning, standard evaluation practice, and statistics, but not this
subfield's (information retrieval's) specific terminology, datasets, or prior work.

They can be assumed to know: supervised fine-tuning of pre-trained Transformer encoders; train/
dev/test splits and in-domain vs. out-of-distribution evaluation as a general ML concept;
embeddings and dense vector representations; contrastive/ranking-style losses at the level of
"pulls matching pairs together, pushes non-matching pairs apart"; knowledge distillation;
standard statistics vocabulary (variance, significance, point estimate).

They cannot be assumed to know: the information-retrieval task setup (corpus, query, relevance
judgment / qrels); nDCG@10 and why rank-aware, graded metrics differ from Precision/Recall/MRR/
MAP; BM25 and lexical retrieval; the specific architecture taxonomy (sparse-neural vs. dense
bi-encoder vs. late-interaction vs. cross-encoder re-ranking); the specific benchmark suite (18
datasets, 9 tasks) or the prior resources it responds to; annotation "pooling" and Hole@k bias in
test collections.

Binding reader types for this review: A (specialist in this subfield) and B (adjacent
researcher, the primary target) and E (mixed audience, treated as reducing to A/B here since no
lay-audience requirement applies).

Venue type: journal (generic; no specific venue or guideline was specified for this piece).
