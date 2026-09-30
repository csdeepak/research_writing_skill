# Step 12 claim/evidence audit

- Lint with tags: 0 errors; the remaining orphan warnings are reference-list lines.
- Numeric fidelity: Table 3 (19 rows x 10 columns) and Table 5 (9 rows) compared programmatically with evidence items E011, E026, E027: 0 mismatches. About 36 prose numbers were grepped in project/paper.txt and all were found (17.3, 7.8, 14/18, 17/18, 16/18, 11/18, 9/18, 6.7, 5.8, 980, 15.3, 42k of 171k, 493.5, 3.6k, 532,761, ~900GB, 18GB, 20-30x, 20-25ms, > 350 ms, 8 of 19, medians 10/160/14/89, hardware, 100K, 2,000, 40, 600K, 300K, 14 cross-encoders, k=0.9, 31.8%, 30.6%, 1.6%, 0.4GB).
- Derived numbers computed by the AUTHOR (skill role) and recorded in the claim map: Table 4 differences (+15.3, -1.8, +1.5) in C012; Table 5 differences TAS-B +7.4, DPR +11.3, BM25+CE +0.3 in C018.
- Claim types vs verbs: interpretations use suggests, may, is consistent with; speculation marked (C015); untested mechanisms flagged (L010).
- Negative results E015, E017, E023 are reported in the main text (Secs 5.1, 5.2). Also reported: GenQ non-uniformity (SCIDOCS), Signal-1M cosine above dot product.
- Fixed during audit: C024 originally implied that the best generalizers were the slowest and largest; docT5query (above BM25 on average, 0.4GB index) contradicts a blanket statement, so the wording was narrowed to the two best-averaging systems.
- Table 2 decode risk (M001) is disclosed in the text.
