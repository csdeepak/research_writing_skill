# ASMOS: results excerpt (Stage 2 acceptance)

Section headings:
- Results

## Figure 1

[figure: Dot plot with confidence whiskers of token-F1 for four systems; RAG is highest at 0.75 and ASMOS-memory lowest at 0.42.]

*Figure 1.* RAG has the highest token-F1 (0.751) and ASMOS-memory alone the lowest (0.416); RAG's 95% confidence interval lies above the means of the other three systems. Dots are means over n = 24 RULER QA questions, whiskers are 95% confidence intervals, all systems use gpt-4o-mini.

## Figure 2

[figure: Paired dot plot of exact match and token-F1 for four systems; ASMOS+RAG is high on exact match but low on token-F1.]

*Figure 2.* ASMOS+RAG answers 62.5% of questions exactly yet has the second-lowest token-F1 (0.433), so the two metrics rank the systems differently. Means over n = 24 questions with 95% confidence intervals for exact match and token-F1.

## Figure 3

[figure: Horizontal bar chart of mean latency in seconds for four systems, from 1.50 s for No-Memory to 1.99 s for ASMOS+RAG.]

*Figure 3.* Mean latency rises from 1.50 s without memory to 1.99 s for ASMOS+RAG. Mean seconds per question over n = 24 questions; the source records no latency interval.
