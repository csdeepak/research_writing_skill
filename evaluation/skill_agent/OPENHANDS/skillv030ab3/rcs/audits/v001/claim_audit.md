# Step 12: evidence and claim audit (draft v001)

- Tag coverage: all 45 claims and 15 limitations appear as tags; every tag resolves (lint: 0 errors).
- Numbers: tools/verify_numbers.py --strict: 0 errors, 0 warnings (every number traces to an evidence value or a project file). No p-values in the draft.
- Manual re-reads against project/paper.txt: values in Tables 2 and 3 and the prose were compared with the evidence items; the conflict pairs (SWE-bench Lite gpt-4o-mini 7.0 vs 6.3; GPQA expert humans 81.3 vs 81.2) are reported with the chosen value and the discrepancy disclosed (Sections 5.1 and 5.3, caveat L013).
- Wording fixes made at this step: "scrolling functions for long files" (source: viewing other parts of a file), "hidden tests" (source: test suite from developers' fixes), "science questions" (source: graduate-level), "behavior cloning" (source: BC, not expanded), "retrieval" for BM25 (removed). All restored to the source's level.
- Claim types vs verbs: interpretation claims use "the authors describe/state"; no "shows that/demonstrates". Measured claims use "scored/reached".
- Negative results: the negative_result items (decisions in the claim map) are reported in the main text (Sections 5.1-5.4). No SELECTIVE_REPORTING.
- C033 remains NEEDS_REVIEW (row alignment inferred) and is reported with that caveat; lint WARN accepted (workflow risk AR1).
