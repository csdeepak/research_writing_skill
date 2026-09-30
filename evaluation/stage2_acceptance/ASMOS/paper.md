# ASMOS: results excerpt (Stage 2 acceptance)

## Results

Figure 1 compares answer quality. RAG reached the highest token-F1, 0.751 (95% CI 0.612 to 0.891), and ASMOS-memory the lowest, 0.416 (95% CI 0.283 to 0.548) {C001}. The paired bootstrap puts RAG's advantage over ASMOS-memory at +0.336 token-F1 (95% CI +0.149 to +0.523) {C004}.

The two quality metrics disagree, as Figure 2 shows: ASMOS+RAG answered 62.5% of questions exactly but had a token-F1 of only 0.433 {C002}.

Figure 3 shows the latency cost. Mean latency rose from 1.50 s without memory to 1.99 s for ASMOS+RAG {C003}.
