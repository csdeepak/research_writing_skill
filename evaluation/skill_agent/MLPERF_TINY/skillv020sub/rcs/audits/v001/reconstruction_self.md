# Step 11: Reader reconstruction self-test (draft v001, tags-in-place reading)

No subagent/fresh context is available in this run (AR-002), so this self-test is done by
re-reading `drafts/v001/paper.md` top to bottom as a reader would, answering Q1-Q12 from the
draft text alone (not from memory of building it), then comparing each answer against
`story/spine.md` and `claims/claim_evidence_map.json`. This is the cheap pre-screen; it does not
replace the isolated blind review the skill assigns to step 18, which TASK.md defers to an
external process (AR-009).

| # | Question | Answer from the draft | Location | Matches spine/claim map? |
|---|----------|------------------------|----------|---------------------------|
| Q1 | What problem is this paper solving? | TinyML lacks a widely accepted, reproducible benchmark for comparing ultra-low-power ML systems | Abstract; Intro P1 | Yes -- spine line 1, C033 |
| Q2 | Why does this problem matter? | On-device inference avoids wireless transmission's energy cost and enables always-on, private, battery-powered use, but only if systems can be compared | Intro P1, Background P1 | Yes -- spine line 1, C001 |
| Q3 | What is missing from existing approaches? | CoreMark isn't ML-representative; MLMark and MLPerf Inference assume far more memory, and MLMark also has no power measurement | Intro P3, Background P3-4 | Yes -- spine line 2, C003-C006 |
| Q4 | What exactly did the authors do? | Built 4 fixed reference benchmarks with a shared latency/accuracy/energy harness and closed/open divisions | Section 3, all paragraphs | Yes -- spine line 4, C007-C010 |
| Q5 | Why did they choose this method? | Modularity isolates one stack layer per submitter (P1 of Sec.3); closed/open balances comparability and flexibility (P2); each per-task choice has a stated reason (P5-P8) | Section 3 | Yes -- C008, C009, C011, C013-C015, C017-C018, C020-C023, C025 |
| Q6 | What experiments were performed? | Running the reference implementations on one board; opening the suite to a first external submission round | Results P1-P3 | Yes -- story graph N14-N16, experiment_chains |
| Q7 | What are the strongest results? | All four reference implementations met target; the first round drew five results across five hardware classes | Results P2-P3 | Yes -- C026, C027 |
| Q8 | What do those results actually establish? | The design is usable end to end and produces comparable results from very different stacks | Discussion P1-P2 | Yes -- C030 |
| Q9 | What do they NOT establish? | That practice will become data-centric, that the design holds beyond one round, or exact per-submission scores | Results P4 (negative result), Discussion P3, Limitations "Additional caveats" | Yes -- C029, L004, L005 |
| Q10 | What is the primary contribution? | An open, modular, three-metric TinyML benchmark suite, validated by reference runs and a first real submission round | Intro P5 (contributions), Conclusion | Yes -- spine line 4-5, C007, C027 |
| Q11 | What are the main limitations? | Streaming/pre-processing measurement unresolved; closed division limited to FC/CNN; dual-use/e-waste caveat; single-round evidence with no per-submission scores/variance | Limitations, all paragraphs | Yes -- L001-L005 |
| Q12 | What should the reader remember one day later? | MLPerf Tiny made ultra-low-power ML systems comparable on accuracy, latency, and energy at once; its first round showed this works across very different hardware, but not yet that it changes what data TinyML researchers use | Conclusion | Yes -- spine lines 5-6 |

## Mismatches found

None at the level of claim strength, scope, or content. Two small **wording** observations, both
fixed in this pass rather than left as open defects:

1. The Results section originally named the "NUCLEO-L4R5ZI reference board" before the Method
   section had introduced it, so a first-time reader hit an unglossed board name before the
   general architecture description. Fixed: Method paragraph 1 (Section 3) now names the board
   and cites TensorFlow Lite Micro (David et al., 2020) before Results refers back to it.
2. Q10's "primary contribution" is stated in the Introduction as three numbered points rather
   than as a single sentence naming one contribution; this matches the spine's own structure
   (the spine's "Approach" and "Key finding" lines are also compound), so it is not treated as a
   defect, but it is flagged here for the flow audit (step 13) to double-check that the three
   points read as one argument rather than three disconnected claims.

## Distortion check (spine vs. draft, all 33 claims + 5 limitations)

Every claim tag `{C001}`-`{C033}` used in the draft was cross-checked against
`claims/claim_evidence_map.json` for statement, type, and confidence; every limitation tag
`{L001}`-`{L005}` was checked the same way. No claim is stated more strongly in the draft than
its `claim_type`/`permitted_verbs` allow (this is re-verified mechanically in the overclaim audit,
step 17, and by `lint_draft.py`'s `B4-verb-vs-type` check, which reports 0 errors). No distortion
(overstated or contradicted) was found.
