# Open issues: ASMOS paper ("Learning Which Agent to Ask"), after blind reviews v001_1 and v005_1 and checkpoint answers Q-001, Q-002, Q-004 (drafts v002 to v006, paper/paper.md)

This is a draft, not a final paper: paper/paper.md still contains unresolved [CITATION NEEDED] and [ASK AUTHOR] markers, and it was written and revised with no human available. The project owner (csdeepak, via chat, 2026-09-30) answered checkpoints Q-001, Q-002 and Q-004; Q-003 and Q-005 are still open.

## Must resolve before submission

### Checkpoints answered by the authors (checkpoints/answers.json; applied by the AUTHOR in draft v004)
- Q-001 (C020, C021): the authors decided to use only the checkable result, -22.09% (n=50, N=10, CI 17.93 to 26.27). C001 is confirmed; C020 and C021 (the 11-query -23.84% +/- 0.15 and +39.14-token figures) are rejected and stay out of the paper. No paper text changed: the paper already reported only this result.
- Q-002 (C023, C024): the authors decided to report accuracy as measured (A1 slightly below A0 in every recorded seed, no significance test) and to make no "equal accuracy" or "saturation" claim. C007 is confirmed; C023 and C024 are rejected. C024 carried the authors' earlier stated reason for foregrounding cost and answerability (E111, "accuracy saturates under parametric knowledge"); by the authors' decision it is not restored in the Introduction. The lint still reports C024 as `S1/S2-author-statement-withheld` (WARN) with the message "must be restored once the checkpoint is answered": that wording is stale, because the lint keys on status BLOCKED and does not read author_confirmation "rejected". The tool was not edited.
- Q-004 (C022): the authors decided to claim "zero retraining" only and to report labels_consumed = 10 as recorded, not "zero added labels". C022 is narrowed to that statement (evidence E058, E062, E059, E063; VERIFIED; confirmed) and appears in Section 4.4 as one added sentence. The labels_consumed counter's definition remains undocumented (Section 3.4 still says so).

### Open human checkpoints (in .rcs/checkpoints/pending.json; the AUTHOR did not answer them)
- Q-003 (blocks C016, C017, C018, C019): README rows for the MiniLM E2 regimes, the E7 cross-model replication, the convergence result and the multi-agent run cite absent artifacts. None of their values is in the paper. The authors' own caveats about the convergence test and the multi-agent validation are carried (L005, L007) without any result.
- Q-005 (blocks no claim; from review finding:4 and related items): method details the package does not contain. Each appears in the paper as an [ASK AUTHOR] marker and is stated as undocumented; nothing was reconstructed. (1) what a claim and a verification outcome are and how outcomes are produced; (2) topic assignment; (3) ownership update rule and prior; (4) whether ownership is learned before or during the 50 evaluation queries; (5) what a candidate is; (6) what the seeds randomize at temperature 0; (7) the route@1 denominator and the criterion for "routed the new topic" in a seed; (8) answerability definition, accuracy grading, and the query classes Q1-Q5; (9) the cost run's embedder; (10) classifier input features and tuning, and the number of agents in the new-topic runs; (11) why A2 never routes and differs slightly from A0; (12) the exact-match and token-F1 definitions in the four-system run.

### Blind review v005_1 (packet pkt-b96117a8, draft v005): items deferred to the authors
Dispositions are in .rcs/revisions/v005_1/dispositions.json (7 fixed, 3 deferred, 0 declined); the revision is draft v006.
- finding:4 (method, score 2): the core mechanism (claims and verification outcomes, topic assignment, update rule and prior, whether ownership is learned before or during evaluation, what a candidate is) is still undocumented. Deferred to the authors as open checkpoint Q-005. Partial fix: the Conclusion no longer asserts that ownership was "learned from verified outcomes"; it says the mechanism is undocumented.
- finding:13 (evidence_traceability, score 3): the reference list is empty (no verified source registry, M015), several numbers rest on absent result files (seeds 11 to 55, other models' percentage reductions; M001, M002, M008), and the corpus, code and figure source data are not available (M013). Only the authors can supply these. The "stray spaces before periods" the reviewer saw come from building the packet with --strip-markers; the manuscript keeps the markers visible.
- inference:6 (selective_presentation): secondary measures for seeds 11 to 55, percentage reductions for the other answering models, and the convergence and multi-agent result files are absent (the latter two also behind open checkpoint Q-003). Partial fix: Section 6.1 now states the authors' multi-agent caveat (one seedless run with an imposed partition) and why no result is reported, instead of "withheld".
- Non-blocking items left for the authors: the title still foregrounds learning (finding:9; retitling is the authors' call); Figure 3 shows no seed variability although the source records standard deviations (finding:14; needs a registry change and re-render); the unit of analysis for the 50-pair test (per query averaged over seeds or otherwise) is not documented (finding:6); answerability and "candidate" remain undefined (findings 10 and 11; Q-005).

### Blind review v001_1: items deferred to the authors
- finding:4 (method, score 2): core mechanics missing (learning signal, update rule, train/evaluate separation, candidate, topic, seed randomness). Deferred: the package does not contain them; asked as Q-005. The paper now states what is recorded and marks the rest.
- inference:4 (selective_presentation, no online-updated classifier baseline): the omission is now disclosed in Sections 3.4, 4.4, 6.2 and 7 (disposition: fixed); running an online-updated classifier given the same labels is an experiment only the authors can add.
- finding:17 (evidence_traceability): fixed by labelling seed bases and stating that route@1 denominators and the "routed" criterion are not recorded; supplying the denominators needs the authors (Q-005 item 7).
- finding:13 (narrative_coherence, non-blocking): partly declined. The skill requires the authors' own limitations and rationale to be attributed to them, so "the authors state" remains in Limitations and for design reasons; other third-party phrasing was removed.

### Markers left in the paper
- [ASK AUTHOR] Section 3.1: claim and verification source, topic assignment, update rule and prior, separation of learning from evaluation queries, definition of a candidate; why A2 does not route and why it differs slightly from A0.
- [ASK AUTHOR] Section 3.2: description of the five query classes; what the seeds randomize; embedder of the cost run; how accuracy is graded; operational definition of answerability.
- [ASK AUTHOR] Section 3.4: number of agents in the new-topic runs; classifier input features and tuning.
- [ASK AUTHOR] Section 3.5: metric definitions in the four-system run.
- [ASK AUTHOR] Availability and disclosure: data and code availability statement; AI-use disclosure wording.
- [CITATION NEEDED] Introduction: prior work on routing among agents and multi-agent memory.
- [CITATION NEEDED] Section 2 (two): retrieval-augmented and memory-augmented baselines; expert finding and reputation from verified outcomes.
- [CITATION NEEDED] Section 3.3: Kerby (2014), named only in the project's correction record.
- [CITATION NEEDED] Section 5: comparison with prior routing and memory work.
- No source registry exists (missing evidence M015), so the paper has no verified citations and makes no novelty claim.

### Missing results that bound claims
- The five-seed file behind seeds 11 to 55 is absent; per-seed accuracy, answerability, route@1, context tokens and candidate-set size exist only for seeds 66 to 110 (M001, M002, M008).
- No paired test of the accuracy difference and no A1 versus A2 test, per-seed gap or interval exists (M008, M009); the accuracy grading procedure is not documented.
- No arm with static but informative ownership exists, so the ablation cannot separate ownership learning from any above-threshold ownership.
- No cost is recorded for embeddings, ownership updates or producing verification outcomes, so no whole-system net saving can be stated (L021).
- Percentage token reductions for the qwen3-30b-a3b and qwen-2.5-72b runs are recorded nowhere; only their corrected signed-rank statistics are (M002).
- The corpus, query set, agent partition, classifier tuning and code are not in the package (M013).
- Four-system metric definitions are undocumented (exact match equals containment in every row; ASMOS+RAG has token-F1 below its exact match, which standard definitions do not allow) and no p-values exist (M005, M006).

## Decisions the AUTHOR made that a person should review
- C031 (the placeholder that said the authors' reason is withheld) was removed after the lint change; C024 carries the rationale and was rejected by the authors in answering Q-002.
- Round v005_1: new writer-derived caveat L026 (the pre-registration the authors cite has no registry entry, date or protocol in the package; the other runs' signed-rank tests are uncorrected) and missing-evidence item M018. L007 restated to give the authors' multi-agent caveat in their terms. The abstract, Section 4.5 heading and Conclusion now scope the static question-answering result to one small run and give the positioning as the authors' statement (C015). The pair count 43/5/2 (C002) moved to Appendix A to offset additions.
- C022 narrowing (Q-004): E090 (a soft, unverifiable README drift row) was dropped from its evidence, and the README's classifier wording "1-6 retrains or fails" is not part of the narrowed claim; the recorded classifier results remain in C009 and C010.
- C005 was narrowed: the ablation is a routing-versus-no-routing contrast (A2 never routes) and is "consistent with the saving requiring routing on learned ownership", not evidence that ownership evolution produces it. The README calls the cause attribution "SUPPORTED"; the paper does not.
- New writer-derived claims: C039 (embedder mapping, including that the cost file records no embedder) and C040 (speculation: memory context may displace or distract from the model's own answer; explicitly untested). New writer-derived limitations L021 to L025.
- C034 (separability check), C035 (5-to-10-seed shift) and C038 (memory contract) are no longer used in the paper (over-precision or jargon the argument does not need); they remain in the claim map.
- The effect-size correction (C030), the other-model signed-rank statistics (C036) and the MiniLM values of the single stationary run (C012) moved to Appendix A to meet the length limit; the lexical-hash negative result stays in the main text.
- L005 (convergence test) and the multi-agent clause of L007 report the authors' own caveats without the results.
- Claims still NEEDS_REVIEW and used in the paper: C005, C012, C014, C029, C039, C040.
- Apart from C001, C007 and C022 (confirmed through the checkpoint answers) every claim has author_confirmation pending; no spine or full claim list was confirmed by a person.
- The README statement "Single LLM; N=5, N>=10 pending" (evidence E105) is superseded by the N=10 result file and by three other cost runs; the paper does not use it.

## Evidence problems noted (CORPUS artifacts were not edited)
- The pytest counts in README (342 passed) and REPRODUCIBILITY.md (412 passed) conflict and remain unreconciled; the paper reports no test result.
- E098 and the 80 to 85 percent implementation-coverage figure are unverifiable and unused.
- The README says the cost headline is -23.8% at equal accuracy and answerability; the present result file shows A1 accuracy 0.68 to 0.70 against 0.72 for A0. The authors resolved this in answering Q-002: accuracy is reported as measured, with no equal-accuracy claim.

## Accepted risks (workflow only; see state.json)
- Unattended run: claims unconfirmed by a person.
- No verified source registry: related work left as markers.
- Venue unknown: the generic profile was used.

## Assumed venue rules (no official source found)
- Section template, US spelling, numeric citation style, unstructured abstract of at most 250 words, 4500-word main-text limit, required data/code availability and AI-use statements. All marked assumed in plan/venue_profile.yaml.

## Gate status (effective, from `run_workflow.py gates` on draft v006, round v005_1 and paper/paper.md, 2026-09-30)
- G1 PASSED (validate_artifacts 0 errors; the first run after the change recorded G1 as failed because state.json still marked G4 passed; the second run records it as passed). G3 PASSED (lint 0 errors, verify_numbers 0 errors on drafts/v006). V1-V4 and V6 PASSED; V5 NOT_RUN (needs a recorded human review; never self-certified); G2 PENDING (no executable check).
- G4 FAILED, on the isolation check only: g4_check reports 6 G4_ISOLATION errors ("reviewer read audience.md outside its packet", and the same for objective.md, paper.md and figures/V001-V003.svg). Those six names are exactly the packet's own files: reviewer_log.json lists them relative to the packet, and g4_check resolves each name against the working directory rather than the packet directory, so every packet file looks outside it. This looks like a tool defect, not a reviewer leaving its packet. It needs a fix in g4_check.py (resolve files_read against the packet directory) or an absolute-path reviewer log; the AUTHOR may edit neither the tool nor the reviewer's diagnostics. All 10 required dispositions are present (7 fixed, 3 deferred, 0 declined), and g4_check reports no G4_UNADDRESSED error.
- G5 FAILED: `lint_draft.py paper/paper.md --final` reports 17 errors, all `marker` (the [ASK AUTHOR] and [CITATION NEEDED] markers listed above, kept on purpose); no S4-over-length error. validate_artifacts 0 errors, verify_numbers 0 errors, claim_invariance (v005 to v006) 0 errors and 1 warning (CLAIM_ADDED L026, required by review item inference:3).
- Length: draft v006 is 4,487 words by the lint's "all" count (prose + headings + table cells) and 4,259 prose-only, against 4,500; the untagged paper/paper.md is 4,365 (all) and 4,137 (prose). Abstract 250 words.
- paper/disclosure.md is a draft AI-use statement for the authors to edit.

## Claims awaiting your confirmation
- All live claims except C001, C007 and C022 (confirmed through checkpoint answers) are pending. The claims written by the writer rather than stated by the authors (origin writer_derived) include C004, C006 to C012, C033 to C037, C039 and C040.
- Blocked (open Q-003): C016 to C019. Rejected by the authors: C020, C021 (Q-001), C023, C024 (Q-002).
