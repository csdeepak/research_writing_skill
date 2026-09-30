# Open issues: MLPerf Tiny presentation, draft v001

## Must resolve before submission
- [MISSING RESULT] Reference latency (inferences per second) and energy (micro-Joules per inference) values (the authors' Figure 5) are not in the project materials; Section 5.2 reports the authors' qualitative statement only; figure FIG-5 is blocked (ticket M001).
- [MISSING RESULT] No variance or interval for any accuracy or AUC value (M005); no measured values from the submission round (M006).
- Table 2 and Table 1 of the source are damaged by extraction: submission modification marks are omitted (M002); two model sizes (52.5 KB, 270 KB) come only from Table 1 (M003); the comparison table referred to in the source's related-work section is absent (M004).
- References [1], [2], [16] and [19] of the source (TinyML foundation, Brainchip, Moreau, Torelli and Bangale) have no year and are not cited in (Author, Year) form; MLMark is discussed by name only (M007).
- All 18 cited works are registered from the project's own reference list, unread (read_depth abstract); publication status is inferred from citation strings and not verified.

## Accepted risks (the run proceeded without a human)
- Author confirmation (G1) was not obtained; claims stated in the authors' own paper are marked confirmed, C035 (writer's arithmetic in Table 2) stays pending.
- Generic venue profile, all rules assumed; length limit set to 4500 words.
- G4 (blind review disposition) and G5 (final edit) are not run here; step 18 is external.
- No human visual usability review (V5) or human comprehension study.

## Assumed venue rules
- Generic research-article profile (plan/venue_profile.yaml); citation style (FirstAuthor et al., Year).

## Claims awaiting confirmation
- C035 (derived): gaps between reference values and targets (about 6, 1.5, 1.6 points; 0.03 and 0.01 AUC).
- C018 (interpretation): the authors' attribution of the submissions' variety to the modular design (confidence low).

## Notes on the run
- The step-7 corpus tool run was limited to works cited in the source paper.
- One file outside the project directory (an automatic tool-output overflow copy of the skill's own section_rules.md) was opened once by mistake early in the run; it contained no project evidence.
