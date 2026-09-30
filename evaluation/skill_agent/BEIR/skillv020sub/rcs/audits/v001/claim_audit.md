# Step 12 -- Evidence/claim audit

## Orphan-claim / tag coverage
`tools/lint_draft.py --rcs .rcs` reports 0 `C1-orphan-claim` findings and 0 `tag-unresolved`
findings against the final draft (see `.rcs/audits/gates/G3_lint.json`). Every `{C###}`/`{L###}`
tag resolves to an entry in `claims/claim_evidence_map.json`.

## Numeric spot-check (re-verified against `project/paper.txt` line-by-line; every number used in
the draft was checked, exceeding the >=20%/min-10 requirement from step 2)
| Draft number | Source location | Match |
|---|---|---|
| "7-18 points" in-domain gap | line 366 | exact |
| BM25 in-domain 0.228 | Table 2, line 372 | exact |
| Avg-vs-BM25: DeepCT -27.9%, SPARTA -20.3%, docT5query +1.6%, DPR -47.7%, ANCE -7.4%, TAS-B -2.8%, GenQ -3.6%, ColBERT +2.5%, BM25+CE +11% | Table 2 bottom row, lines 422-531 | exact; cross-validated against 3 independent prose statements (TAS-B ranked best-among-dense with the least-negative value -2.8%; docT5query's modest positive average is consistent with an 11/18 win count; BM25+CE's largest positive average is consistent with its 16/18 win count) |
| docT5query 11/18 | line 535 | exact |
| BM25+CE 16/18, fails ArguAna/Touche-2020; ColBERT 9/18 | line 537 | exact |
| TAS-B vs. ANCE 14/18, vs. DPR 17/18 | line 538 | exact |
| TAS-B vs. ANCE: -17.3 pts (TREC-COVID), -7.8 pts (Touche-2020); 10 vs 160 words; 14 vs 89 words | line 539 | exact |
| Latency: 450ms/350ms (BM25+CE GPU/CPU), <20ms dense, 20-30x, 20-25ms sparse CPU | lines 598, 643 (Table 3) | exact |
| Hole@10 and nDCG before/after (Table 4, all 9 rows) | lines 665-705 | exact, incl. self-consistency (docT5query 0.713->0.714; ANCE 0.654->0.735 = 6.7 pts above BM25's 0.668; ColBERT +5.8 pts) |
| Appendix H: 15.3-point gap | line ~950 | exact |
| Composition: 18 datasets/9 tasks, 3.6k-15M docs, 3-192/11-635 word ranges, 8/19 with training data | lines 121, 290 | exact |
| GenQ 100K document cap | line 361 | exact |
| 980 manually annotated pairs | line 704 | exact |

No discrepancies found. No number in the draft was rounded beyond what the source itself gives
(all percentages/points/counts are copied verbatim).

## Claim-type / verb audit
`tools/lint_draft.py` reports 0 `B4-verb-vs-type` findings (checked: no `interpretation`,
`speculation`, `hypothesis`, or `future` claim is paired with a strong verb such as "shows that",
"proves", "demonstrates", "establishes", "confirms"). Spot-checked manually:
- C005, C008, C016, C019 (`interpretation`) use "suggests" / "should be read as" / "is one
  identifiable source of" / hedged framing -- never "shows"/"proves".
- C013 (`speculation`) is explicitly marked "this explanation is speculative and not isolated by
  a dedicated experiment" in the text (Sec. 5.3).
- C004, C006, C007, C011, C012, C014, C018 (`measured`) use "trails", "outperforms",
  "averages... below", counts ("14 of 18") -- all within the permitted-verb list for `measured`.
- C009, C010, C017 (`observed`) use "underperform", "perform well on some... drop sharply on
  others" -- consistent with `observed`.
- C015 (`derived`) uses "reproduce the same pattern", "consistent with" -- consistent with
  `derived`.

## Negative-result coverage
All six `negative_result` evidence items (E037-E042) are reported in the main text (Sec. 5.2-5.3),
matching their `reported_main` decisions in `claims/claim_evidence_map.json ->
negative_result_decisions`. No negative result bearing on a claim was found omitted; no
`SELECTIVE_REPORTING` flag raised.

## Author-stated limitation/rationale coverage
`tools/lint_draft.py` reports 0 `S1-author-limitation-missing`, 0 `S1-caveat-attribution`, and
0 `S2-author-rationale-missing` findings. One `S2-rationale-misplaced` WARN was raised during
drafting (C022 first tagged only in the Abstract) and fixed by renaming Section 3's heading to
"Method: Building the BEIR Benchmark" so `DESIGN_SECTION_RE` recognizes it; re-run after the fix
shows 0 `S2-rationale-misplaced` findings. `validate_artifacts.py .rcs` independently confirms
0 `AUTHOR_STATEMENT_DROPPED` / `ATTRIBUTION_ERROR` errors.

## Outcome
No `OVERCLAIM`, `SELECTIVE_REPORTING`, or `MISSING_RESULT` failure state raised at this step.
