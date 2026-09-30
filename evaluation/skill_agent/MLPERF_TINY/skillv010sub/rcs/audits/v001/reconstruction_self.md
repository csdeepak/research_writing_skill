# Step 11 -- Reader reconstruction self-test (draft v001)

Method: re-read `.rcs/drafts/v001/paper.md` top to bottom as if encountering it for the first
time (tags visually ignored during the read, per the self-test's intent), answer Q1-Q12, then
diff against `story/spine.md` and `claims/claim_evidence_map.json`. Isolation note: this is the
same context that wrote the draft (no fresh-context runtime available this session), so this is
a self-test, not a substitute for the external blind review the run constraints defer to step 18.

| # | Answer from the draft alone | Location | Matches spine/claim map? |
|---|---|---|---|
| Q1 Problem | TinyML lacks a way to compare hardware/software fairly on accuracy+latency+energy together | Intro P1-P3 | yes (spine line 1) |
| Q2 Why it matters | every layer of the deployment stack must be co-optimized; without a shared yardstick, isolating any one gain, or comparing solutions, is hard | Intro P2 | yes |
| Q3 What's missing | CoreMark isn't ML; MLMark/MLPerf Inference are ML but wrong hardware scale / no power | Intro P3, Related Work | yes (spine line 2) |
| Q4 What they did | built + fielded MLPerf Tiny: 4 reference benchmarks, 3-metric protocol, closed/open divisions | Intro P5, Methods | yes (spine line 4) |
| Q5 Why this method | division split trades comparability vs. flexibility; target margins absorb quantization noise | Methods (quality-target and division paragraphs) | yes |
| Q6 Experiments | the v0.5 community submission round (June 2021) | Results P1 | yes |
| Q7 Strongest result | 5 submissions, both divisions, 5 hardware/software categories | Results P2, Table 2 | yes (spine line 5) |
| Q8 What it establishes | the design can accommodate real, heterogeneous submitters while a subset (closed) stays comparable | Results P5, Discussion P1 | yes (spine line 6) |
| Q9 What it does NOT establish | generality beyond 1 round/n=5; stability of the accuracy figures under retraining; full architecture coverage; the streaming/feature-extraction tension | Results P5, Discussion Limitations | yes (spine line 7) |
| Q10 Primary contribution | a fielded, gap-closing, 3-metric MCU benchmark suite | Intro contributions paragraph, Discussion P1-P2 | yes |
| Q11 Main limitations | single round; unreplicated reference accuracies; narrow closed-division architectures; unresolved streaming/feature-extraction measurement tension | Discussion Limitations (4 paragraphs) | yes |
| Q12 One-day-later takeaway | MLPerf Tiny is the suite that finally measures accuracy+latency+energy together on real MCU hardware, and its first round showed diverse real submitters could use it, within the bounds of one round's evidence | Abstract, Conclusion | yes |

**Result: 12/12 answerable, no mismatches against the spine or the claim map.** No distortion
(overstated/contradicted) found. No intrusions (facts not in the evidence) found.

## Question-debt check
Every question raised in the Introduction (per `story/question_ledger.json`) is answered later in
the draft; the only two forward deferrals (what closed/open mean in full, and whether the design
actually worked) are within the <=3 allowance and are both resolved by Methods/Results
respectively.

## Note on isolation
Because no fresh context or subagent runtime is available this session, this self-test carries
the residual risk that the AUTHOR "reads into" the draft what it already knows from the artifacts
rather than what the text alone says. Mitigation used: every answer above cites a draft location,
not an artifact file, and was checked against the artifact only afterward (as the comparison
column, not the source of the answer).
