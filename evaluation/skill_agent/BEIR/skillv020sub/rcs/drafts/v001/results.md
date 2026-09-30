## 5 Results

### 5.1 In-domain accuracy does not predict zero-shot performance

Our first finding answers our third question directly. On the in-domain MS MARCO test set, BM25 trails the nine neural systems we evaluate by 7-18 points nDCG@10. Averaged across the 18 BEIR datasets, however, BM25 outperforms six of those same nine neural systems {C004}. This reversal is the paper's central result: a system's rank on the field's dominant single-dataset benchmark does not predict its rank once evaluation moves outside that dataset {C005}. Table 1 places both numbers, together with each system's inference cost, side by side {C007}.

Table 1. In-domain accuracy does not predict zero-shot generalization, and the best zero-shot generalizers cost the most compute. nDCG@10 on MS MARCO (in-domain, single run, no seed variance); average zero-shot nDCG@10 relative to BM25 across the 18 BEIR datasets (single run per system); GPU query latency on 1M sampled documents.

| Architecture family | System | In-domain MS MARCO (nDCG@10) | Avg. zero-shot vs. BM25 (18 datasets) | GPU latency/query |
|---|---|---|---|---|
| Lexical | BM25 | 0.228 | 0% (reference) | not applicable (untrained) |
| Sparse | DeepCT | 0.296 | -27.9% | not reported |
| Sparse | SPARTA | 0.351 | -20.3% | not reported |
| Sparse | docT5query | 0.338 | +1.6% | not reported |
| Dense | DPR | 0.177 | -47.7% | under 20 ms |
| Dense | ANCE | 0.388 | -7.4% | under 20 ms |
| Dense | TAS-B | 0.408 | -2.8% | under 20 ms |
| Dense | GenQ | 0.408 | -3.6% | under 20 ms |
| Late-interaction | ColBERT | 0.401 | +2.5% | not separately reported |
| Re-ranking | BM25+CE | 0.413 | +11% | ~450 ms |

Looking at the average column alone, only three systems beat BM25 zero-shot: the cross-encoder re-ranker BM25+CE (+11%), the late-interaction model ColBERT (+2.5%), and the sparse document-expansion method docT5query (+1.6%) {C006}. The other six -- two more sparse methods and four dense bi-encoders -- all average below BM25, by margins as large as 47.7% for DPR {C006}.

These systems are not equally expensive to run. Re-ranking and late-interaction, the two best zero-shot generalizers on average, both score candidate documents with a cross-attention-like computation, and pay for it at query time: BM25+CE takes roughly 450 ms per query on a GPU (350 ms on CPU), compared with under 20 ms for the dense retrievers we tested here -- a 20-30x difference {C007}. Sparse methods are fastest of all on CPU, at 20-25 ms.

### 5.2 The architecture families diverge for different reasons

The two sparse methods that split most sharply illustrate why an in-domain number can mislead. DeepCT and SPARTA both learn to reweight terms with a neural network and both do well in-domain, but both underperform BM25 on nearly all 18 datasets zero-shot {C009}. docT5query, also a sparse method, instead expands each document with predicted queries before indexing it; it outperforms BM25 on 11 of the 18 datasets {C009}. Dense bi-encoders, which replace lexical matching with a single learned vector per query and per document, show a related but even sharper split.

Dense bi-encoders perform well on some BEIR datasets but drop sharply on others with a large shift in domain (for example BioASQ) or task type (for example Touche-2020) relative to their training data {C010}. DPR, the only one of the ten systems trained solely on question-answering data rather than MS MARCO, generalizes worst of all ten systems: it averages 47.7% below BM25 across the 18 datasets {C010}.

The two families with the best average, re-ranking and late-interaction, are not universal winners either. BM25+CE outperforms BM25 on 16 of the 18 datasets, failing only on ArguAna and Touche-2020, two argument-retrieval tasks whose queries differ sharply from MS MARCO's question-style queries {C011}. ColBERT, despite a positive average, outperforms BM25 on just 9 of 18 datasets {C011}. Cross-attention, or a cross-attention-like interaction between query and document, appears to matter for this kind of generalization among the systems we tested; comparing query and document through a single fixed vector, as a bi-encoder does, is where the pattern breaks down most often {C011}.

### 5.3 Why the best dense model still loses on two datasets

Among the dense bi-encoders, TAS-B generalizes best, outperforming ANCE on 14 of the 18 datasets and DPR on 17 of 18 {C012}. The authors attribute this to TAS-B's training setup -- in-batch negatives combined with a Margin-MSE loss distilled from a cross-encoder/ColBERT ensemble -- though this explanation is speculative and not isolated by a dedicated experiment {C013}.

TAS-B's two losses to ANCE are better understood. On TREC-COVID it trails ANCE by 17.3 points nDCG@10, and on Touche-2020 by 7.8 points {C014}; these are the two datasets where the two models retrieve documents of the most different length (a median of 10 words for TAS-B versus 160 words for ANCE on TREC-COVID) {C014}. A separate, controlled comparison isolates one source of this length preference: two otherwise identical models trained on MS MARCO, differing only in whether they compare query and document vectors by cosine similarity or by dot product, reproduce the same pattern -- the cosine variant favors shorter documents and the dot-product variant favors longer ones, with a 15.3-point nDCG@10 gap between the two variants on TREC-COVID {C015}. This is consistent with a simple explanation the authors offer: dot-product similarity grows with a vector's length, so a longer document can score higher by that measure alone, while cosine similarity does not carry this effect {C015}. The similarity function used during training is therefore one identifiable source of a dense retriever's document-length preference, though a length preference is not itself an error: which document length is actually relevant to a query varies by dataset {C016}.

Domain adaptation is not uniformly beneficial either. GenQ, which further fine-tunes TAS-B on synthetic queries generated for each target dataset, outperforms TAS-B on specialized domains such as scientific publications, finance, and community question-answering, but underperforms it on broader, more generic domains such as Wikipedia-sourced datasets {C017}.

### 5.4 A case study: are the benchmark's own judgments neutral?

The comparisons above assume the benchmark's relevance judgments are themselves neutral across architecture families. We checked this assumption on one dataset. TREC-COVID's original judgments (Voorhees et al., 2021) were built by pooling the top results from many participating systems, most of them lexical; a document that no pooled system had retrieved was treated as irrelevant by default. We manually judged the 980 (query, document) pairs that our ten systems retrieved in their top 10 results but that the original pool had never scored -- each system's "holes" -- following the original task's guidelines and blinded to which system had retrieved each pair {C018}. Table 2 reports the resulting Hole@10 rates and rescored nDCG@10 values.

Table 2. TREC-COVID's original judgment pool undercounted non-lexical systems' top hits. Hole@10 is the share of a system's top-10 hits absent from the original judgments; nDCG@10 is shown before and after 980 missing judgments were added.

| System | Family | Hole@10 | nDCG@10 before | nDCG@10 after |
|---|---|---|---|---|
| docT5query | Sparse | 2.8% | 0.713 | 0.714 |
| BM25 | Lexical | 6.4% | 0.656 | 0.668 |
| SPARTA | Sparse | 12.4% | 0.538 | 0.624 |
| ColBERT | Late-interaction | 12.4% | 0.677 | 0.735 |
| ANCE | Dense | 14.4% | 0.654 | 0.735 |
| DeepCT | Sparse | 19.4% | 0.406 | 0.472 |
| DPR | Dense | 30.6% | 0.332 | 0.445 |
| TAS-B | Dense | 31.8% | 0.481 | 0.555 |

Hole@10 is far higher for dense systems (14.4% for ANCE, 31.8% for TAS-B) than for lexical or document-expansion systems (6.4% for BM25, 2.8% for docT5query) {C018}. After scoring the missing pairs, the lexical and document-expansion systems' scores barely moved (docT5query: 0.713 to 0.714), while the dense systems' scores rose sharply: ANCE's score rose from 0.654 to 0.735, which is 6.7 points above BM25's own re-scored value of 0.668, and ColBERT's own score rose by a comparable 5.8 points {C018}. The original judgment pool, in other words, was itself biased toward the kind of system used to build it {C019}.

This case study does not overturn our main comparison -- lexical retrieval's zero-shot robustness is also visible across the other 17 datasets, which were not re-annotated -- but it means the exact size of the gap between lexical and non-lexical systems on TREC-COVID, and possibly on other similarly built collections, should be read as an upper bound on the true difference in retrieval quality, not as an exact one {C019}.
