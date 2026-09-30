# ASMOS: results excerpt (Stage 2 acceptance)

## Results

Figure 1 compares answer quality. RAG reached the highest token-F1, 0.751 (95% CI 0.612 to 0.891), and ASMOS-memory the lowest, 0.416 (95% CI 0.283 to 0.548). The paired bootstrap puts RAG's advantage over ASMOS-memory at +0.336 token-F1 (95% CI +0.149 to +0.523).

The two quality metrics disagree, as Figure 2 shows: ASMOS+RAG answered 62.5% of questions exactly but had a token-F1 of only 0.433.

Figure 3 shows the latency cost. Mean latency rose from 1.50 s without memory to 1.99 s for ASMOS+RAG.


**Figure 1.** RAG has the highest token-F1 (0.751) and ASMOS-memory alone the lowest (0.416); RAG's 95% confidence interval lies above the means of the other three systems. Dots are means over n = 24 RULER QA questions, whiskers are 95% confidence intervals, all systems use gpt-4o-mini. [figure: Dot plot with confidence whiskers of token-F1 for four systems; RAG is highest at 0.75 and ASMOS-memory lowest at 0.42.]

**Figure 2.** ASMOS+RAG answers 62.5% of questions exactly yet has the second-lowest token-F1 (0.433), so the two metrics rank the systems differently. Means over n = 24 questions with 95% confidence intervals for exact match and token-F1. [figure: Paired dot plot of exact match and token-F1 for four systems; ASMOS+RAG is high on exact match but low on token-F1.]

**Figure 3.** Mean latency rises from 1.50 s without memory to 1.99 s for ASMOS+RAG. Mean seconds per question over n = 24 questions; the source records no latency interval. [figure: Horizontal bar chart of mean latency in seconds for four systems, from 1.50 s for No-Memory to 1.99 s for ASMOS+RAG.]