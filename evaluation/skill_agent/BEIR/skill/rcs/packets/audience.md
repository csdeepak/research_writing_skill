# Audience Profile

## Mode
B — Adjacent researcher

## Description
Machine-learning researchers from fields adjacent to information retrieval (IR). They have solid working knowledge of:
- General ML concepts: supervised learning, neural networks, pre-trained transformers, fine-tuning, transfer learning
- Deep learning architectures: BERT-style encoders, T5/sequence-to-sequence models, contrastive learning
- Standard evaluation practice: train/dev/test splits, held-out evaluation, metric choice, statistical significance
- General NLP: tokenisation, embeddings, classification, sequence-to-sequence tasks

They do NOT have working knowledge of:
- Information retrieval-specific terminology: BM25, BEIR datasets, nDCG, TREC evaluations, pooling for annotation, qrels, inverted index structures
- IR subfield datasets: MS MARCO, TREC-COVID, NFCorpus, BioASQ, Robust04, etc.
- IR evaluation conventions: Hole@10, relevance pools, multi-level relevance judgements, capped recall

## Explanation needs
- Define BM25 (the probabilistic term-frequency model) and contrast with neural approaches
- Explain nDCG@10 as a rank-quality metric and why it is preferred over precision/recall here
- Clarify what "zero-shot" means in the IR context (same as in NLP: no fine-tuning on target data)
- Explain annotation pooling and selection bias — a concept not widely known outside IR
- Explain Hole@10 as a diagnostic for annotation coverage
- Name the five architecture families (lexical, sparse, dense, late-interaction, re-ranking) and give one-sentence intuition for each before comparing them
- Contextualise dataset scale (millions of documents) relative to NLP evaluation norms

## Tone
Technical, precise, collegial. The reader is capable; they just need the domain vocabulary.
