# Open issues: OpenHands paper, draft v001

## Must resolve before submission
- [MISSING RESULT] Table 1 feature marks (which framework has which feature) are lost in the extracted text (missing_evidence M001). Where: Introduction para 2, Related work. Bounds the gap claim (C005).
- [MISSING RESULT] Row-to-value alignment and costs for BIRD, ML-Bench, BioCoder, Gorilla APIBench, ToolQA are inferred (M002). Where: Section 5.1, 5.4. Claim C033 is NEEDS_REVIEW.
- [MISSING RESULT] No variance, seeds or intervals for any result (M003); no ablations (M004); reference tuning budgets unknown (M007). Bounds C030-C042.
- [MISSING RESULT] No measurement of integration effort or human-agent collaboration outcomes (M005). Where: Section 5.3.
- [MISSING RESULT] Source Figures 1, 2, 4, 5 are not in the extracted text (M006).
- [ASK AUTHOR] Date and method of the community statistics (M008).
- [ASK AUTHOR] Confirm that the two questions (design, evaluation) fairly frame the stated goal; the paper states no research questions (M009).
- [CITATION NEEDED] None open; all 30 cited works come from the project's own reference list, registered at abstract depth (described by the citing authors only; not read).

## Accepted risks (unattended run; kind workflow)
- AR1 pending author confirmation for C033, C040, C041; AR2 two evidence conflicts resolved by the agent (Table 4 over Table 3 for 7.0 vs 6.3; Table 6 over Table 7 for 81.3 vs 81.2), both disclosed in the paper; AR3 generic venue profile; AR4 gap scoped to the authors' characterization (no web); AR5 framing of the two questions.

## Claims awaiting confirmation
- C033 (observed): other software benchmarks, alignment inferred. C040, C041 (observed, writer-derived): patterns read from the tables.

## Gates
- G1, G3 passed by tool report. G2 recorded by audit file. G4 and G5 are not run (step 18 blind review is external). Visual gates not applicable (no figures).
