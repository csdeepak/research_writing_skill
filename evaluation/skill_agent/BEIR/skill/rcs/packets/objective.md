# Paper Objective

## One-sentence statement
Present the BEIR benchmark to an adjacent ML audience: explain why zero-shot IR generalisation is a meaningful problem, what BEIR is and how it was constructed, what 10 retrieval systems of five architectural families achieve on it, and what the annotation bias study reveals about evaluation validity.

## What the reader must believe after reading
1. Evaluating retrieval models only in-domain systematically overstates their generalisability.
2. BEIR provides a principled, diverse, standardised testbed for zero-shot IR evaluation.
3. Classical BM25 is a harder baseline than its MS MARCO score suggests once out-of-distribution evaluation is applied.
4. Cross-attention (re-ranking, ColBERT) is currently the most reliable path to zero-shot generalisation, at a latency cost; dense models are faster but less robust.
5. Annotation selection bias is a real and measurable problem that inflates lexical model scores on existing benchmarks.

## What the reader must NOT take away
- That BM25 is always better than neural models (it is not; neural models win on many individual datasets and in-domain).
- That the annotation bias analysis corrects all datasets (it corrects one, TREC-COVID, as a case study).
- That BEIR is final or complete (it is explicitly limited to English and current architecture styles).
- That dense retrieval is fundamentally broken (it generalises better than term-weighting approaches; TAS-B is close to BM25 on average).

## Key numbers to convey accurately
- 18 datasets, 9 task types, 10 models, 5 architecture families
- BM25 MS MARCO in-domain gap: 7–18 nDCG@10 points below best neural models
- BM25+CE average zero-shot improvement: +11% over BM25
- DPR average zero-shot degradation: −47.7% vs BM25
- ColBERT index for BioASQ (15M docs): ~900GB vs BM25 18GB
- ANCE Hole@10 corrected improvement: 0.654 → 0.735 (+8.1 points)
- 980 query-document pairs manually annotated

## Deliverable
Standalone Markdown research paper, 3,000–4,500 words, with abstract, introduction, background, benchmark description, experimental setup, results, analysis, limitations, conclusion, and references.
