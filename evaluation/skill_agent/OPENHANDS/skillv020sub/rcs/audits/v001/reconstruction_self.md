# Step 11 -- Reader reconstruction self-test

Read `.rcs/drafts/v001/paper.md` alone (mentally stripping `{C###}`/`{L###}` tags, as a final
reader would), then answered Q1-Q12 from the draft alone, and compared each answer with
`story/spine.md` and `claims/claim_evidence_map.json`. This is a pre-screen (does not replace
the blind review in step 18, which is out of scope for this run per TASK.md's run-specific
constraints).

| # | Question | Answer from the draft alone | Location | Matches spine/claim map? |
|---|----------|------------------------------|----------|---------------------------|
| Q1 | Problem | Agents that act through real software need 5 pieces (interaction mechanism, safe execution, tool library, multi-agent support, evaluation) that no single open framework combines | Introduction para 1, Related Work | Yes -- spine line 1 |
| Q2 | Why it matters | Software is already the most general, powerful interface humans have for acting on the world | Introduction para 2 | Yes -- spine line 1-2 (C030) |
| Q3 | What's missing | Existing frameworks each supply only some of the 5 pieces, or specialize by task without generalizing | Introduction para 3, Related Work | Yes -- spine line 2 |
| Q4 | What they did | Built OpenHands (event stream, 3 actions, sandbox, AgentSkills, delegation, AgentHub, integration tests); ran one CodeActAgent, 0-shot, on 15 benchmarks across 3 categories | Method, Experimental Setup | Yes -- spine line 4 |
| Q5 | Why this method | Code actions chosen for flexibility/reliability/maintainability; sandbox for safety; AgentSkills bounded by an inclusion rule to avoid redundant tools | Method paras 2-3 | Yes -- claims C032-C034 |
| Q6 | Experiments | SWE-Bench Lite + HumanEvalFix (software); WebArena + MiniWoB++ (web); GAIA, GPQA, AgentBench, MINT, ProofWriter, EDA (misc.) | Results | Yes -- matches Table 1-3 |
| Q7 | Strongest results | 26.0% SWE-Bench Lite; 79.3% HumanEvalFix; 52.0% GPQA; 32.1% GAIA | Abstract, Results | Yes -- spine line 5 |
| Q8 | What results establish | The same unmodified agent is competitive across all 3 categories on 9 of 11 confidently-measured benchmarks; residual gap tracks the backbone model more than the category | Discussion paras 1-2 | Yes -- spine line 5-6 |
| Q9 | What results do NOT establish | Not a controlled ablation of the architecture alone (backbones/shots/training regimes differ); no seed variance; not universal (MiniWoB++, MINT-code) | Limitations "Additional caveats" | Yes -- spine line 7 |
| Q10 | Primary contribution | The platform itself, and the cross-category competitiveness finding | Introduction contributions para, Conclusion para 1 | Yes -- spine line 4-5 |
| Q11 | Main limitations | Author-stated first (multi-modality, complex-task struggles, file editing, handcrafted workflows, the HumanEvalFix shot-count asymmetry), then the writer's additional caveats | Limitations | Yes -- L001-L008 |
| Q12 | One-day-later memory | One open platform; one unmodified agent competitive across categories; mechanism = interface generality, not per-task engineering; boundary = not universal, backbone-model-dependent | Conclusion | Yes -- spine lines 4-7 |

**Result: all 12 answerable from the draft alone, with no distortion (no answer is overstated or
contradicted relative to the spine/claim map).** No mismatches requiring a revision round were
found. Proceeding to step 12.
