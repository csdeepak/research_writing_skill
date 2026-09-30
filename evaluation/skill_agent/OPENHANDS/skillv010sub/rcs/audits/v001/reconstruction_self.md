# Step 11 -- Reader reconstruction self-test

Performed by AUTHOR against `.rcs/drafts/v001/paper.md` alone (tags read as present; no fresh
context available in this runtime -- no subagents -- so this is a same-session, tags-visible
re-read rather than a truly blind one; step 18's external review is where a blind read happens).

| # | Question | Answer drawn from the draft alone | Location |
|---|----------|-----------------------------------|----------|
| Q1 | Problem? | Building/evaluating agents that act through software has meant assembling separate infrastructure per project/category. | Introduction ¶1-2 |
| Q2 | Why care? | The platform is already widely used (2.1K+ contributions, 188+ contributors, 32K stars); increasingly capable agents raise both opportunity and risk. | Introduction ¶1; Discussion ¶4 |
| Q3 | What's missing? | Prior frameworks give interaction/execution pieces at uneven depth; specialized SWE agents aren't evaluated outside their category. | Introduction ¶2; Related Work |
| Q4 | What did they do? | Built OpenHands (event stream, sandbox, ACI/AgentSkills, delegation, AgentHub, 15-benchmark harness) and evaluated one generalist agent on it. | Introduction ¶4; The OpenHands Platform; Evaluation Setup |
| Q5 | Why this method? | A programming-language action space is flexible across tool forms; a carefully designed ACI matters (extends SWE-Agent's point to a broader library). | The OpenHands Platform ¶3; Discussion ¶2 |
| Q6 | Experiments? | 15 benchmarks across software engineering, web browsing, and miscellaneous assistance, mostly 0-shot, protocol stated once. | Evaluation Setup |
| Q7 | Strongest results? | Above baseline on 9/15 benchmarks, within ~1pt on 2 more; e.g. 26.0% SWE-Bench Lite, 79.3% HumanEvalFix, 76.5% ML-Bench, 52.0% GPQA, 57.6% AgentBench. | Results, all subsections |
| Q8 | What do results establish? | One fixed-prompt agent design, scored everywhere, is competitive across three unrelated categories at once; no comparison baseline is. | Results:Cross-category synthesis; Discussion ¶1 |
| Q9 | What do they NOT establish? | Not statistically characterized; not model-controlled; not top on several benchmarks; no ablation of platform components; safety claims unmeasured. | Limitations and Future Work; Discussion ¶4 |
| Q10 | Primary contribution? | One open platform + one generalist agent, competitive (not dominant) across categories that used to need separate agents. | Conclusion; Introduction ¶4-5 |
| Q11 | Main limitations? | No variance reported; backbone-model confound; not top performer everywhere; protocol heterogeneity; version snapshot; no ablation; safety unmeasured. | Limitations and Future Work |
| Q12 | One day later? | = Conclusion = spine lines 5-7: competitive breadth from one design, with real caveats. | Conclusion |

**Result: all 12 answerable from the draft alone; no "cannot determine."** No mismatch found
against `story/spine.md` or `claims/claim_evidence_map.json` (compared claim-by-claim while
answering Q7-Q11 above). No distortion (overstated/contradicted) detected.
