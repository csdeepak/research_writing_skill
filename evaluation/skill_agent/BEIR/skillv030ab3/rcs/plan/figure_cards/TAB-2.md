# Card TAB-2 (Table 2)

```yaml
id: TAB-2
purpose: "Give exact zero-shot nDCG@10 for every system and dataset so readers can see where BM25 wins."
rq: "RQ1, RQ2"
takeaway: "No system wins on every dataset; BM25+CE is above BM25 on 16 of 18 datasets and the learned sparse and dense systems are below BM25 on many."
claims: [C030, C031, C032, C033, C034, C035, C036, C043]
evidence: [E050, E052, E060, E061, E062, E063, E064, E065, E066, E067, E068, E069]
source_data: [project/paper.txt]
type: table
comparison_the_eye_must_make: "compare systems within a row/column"
uncertainty_shown: "none: single runs, no variance reported (author-stated limitation L007)"
baseline_or_reference: "BM25 column/row"
non_conclusions: "does not show run-to-run variance, other languages or long documents"
placement: "Section 5.1"
caption: "see paper"
```
