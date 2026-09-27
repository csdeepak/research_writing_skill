# Paper Architecture: OpenHands, reported for an adjacent-ML audience

Story pattern: question_led
Audience mode: B (adjacent ML researcher) · Binding personas: A, B, E · Venue profile: `.rcs/plan/venue_profile.yaml` (generic, assumed rules: all; VENUE_UNKNOWN accepted risk)
No images permitted (task constraint); all visuals are Markdown tables.

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Link forward |
|---|---------|---------------|--------------------------|----------------------|--------|---------|--------|-----------|--------------|
| I.1 | Introduction | N01, N18 | What is OpenHands and what is an agent here? | Building and evaluating agents that act on real software interfaces is costly and fragmented infrastructure work. | C020 | CORE | - | agent | why this is worth solving |
| I.2 | Introduction | N02, N03 | Why does this matter, and what exists already? | Many separate agent systems exist, each with its own narrow-benchmark harness. | C001 | CORE | - | generalist agent | what's missing |
| I.3 | Introduction | N04 | What is missing? | No single open platform in the evidence integrates one agent interface with many benchmarks across domains. | C001, C011 | CORE | - | - | the question |
| I.4 | Introduction | N05 | What exactly do they ask? | Can one open platform and one generalist agent, unmodified, be evaluated across software engineering, web browsing, and misc. assistance? | - | CORE | - | - | approach |
| I.5 | Introduction | N06, N07 | What did they build? | OpenHands provides a minimal action interface, a reproducible runtime, and 15 benchmark harnesses. | C001, C011, C018, C019 | CORE | - | action abstraction | contributions |
| I.6 | Introduction | N14 | What is the contribution? | The paper's contribution is the open platform plus the demonstration that one generalist agent works across it. | C001, C011, C012 | CORE | - | - | paper map |
| I.7 | Introduction | (map) | Where is this shown? | Paper map by the three task categories and their results. | - | CORE | - | - | Related Work |
| RW.1 | Related Work | N03 | What do existing systems do and where do they stop? | SWE-Agent, AutoCodeRover, Aider (software) and the WebArena Agent [SRC-001] (web) each target one benchmark family with their own harness. | - | CORE | Table 1 (baselines) | - | why a shared platform differs |
| RW.2 | Related Work | N04 | How does OpenHands relate? | OpenHands differs by integrating many benchmarks under one agent interface rather than one harness per system. | C001, C011 | CORE | - | - | Platform section |
| M.1 | Platform and Method | N07, N18 | What is the action abstraction? | Agents in OpenHands emit one of three action types: running code, running a shell command, or interacting with a browser. | C001 | CORE | - | action abstraction | why this matters for reproducibility |
| M.2 | Platform and Method | N07 | How is the runtime kept reproducible? | A containerized runtime uses a dual-tagging scheme (hash-based and generic tags). | C018 | SUPPORTING | - | - | testing |
| M.3 | Platform and Method | N07 | How is correctness checked without live LLM cost? | Integration tests mock LLM calls with predefined responses keyed to exact prompts. | C019 | SUPPORTING | - | - | benchmark integration |
| M.4 | Platform and Method | N06 | What benchmarks are integrated and how are they organized? | 15 benchmarks are integrated across three categories: software engineering (7), web browsing (2), misc. assistance (6). | C011 | CORE | Table 2 (benchmark inventory) | - | experimental setup |
| ES.1 | Experimental Setup | N08 | How is the generalist-agent claim tested? | The same CodeActAgent (BrowsingAgent for web tasks) is run without prompt changes across all benchmarks; cost drives some subset choices. | C006, C020 | CORE | - | 0-shot, resolve rate | Results |
| R.1 | Results (software engineering) | N09 | RQ1, software-engineering slice: what happened on SWE-Bench Lite? | CodeActAgent v1.8 reaches 26.0% (claude-3.5-sonnet), 22.0% (gpt-4o), 6.3% (gpt-4o-mini) on 300 instances, next to baselines up to 26.3%. | C002, C003 | CORE | Table 3 (SWE-Bench Lite) | resolve rate, SWE-Bench Lite | HumanEvalFix |
| R.2 | Results (software engineering) | N10 | What happened on HumanEvalFix? | CodeActAgent v1.5 fixes 79.3% of Python bugs 0-shot with multi-turn self-debugging. | C004, C005 | CORE | - | 0-shot | move to web browsing |
| R.3 | Results (web browsing) | N11 | RQ1, web slice: what happened on WebArena/MiniWoB++? | BrowsingAgent v1.0 reaches 8.5-15.5% on WebArena (812 instances) and 40.8% on the full MiniWoB++ set (125 environments, some requiring vision). | C007 | CORE | Table 4 (web browsing) | - | misc. assistance |
| R.4 | Results (misc. assistance) | N12 | RQ1, reasoning slice: what happened on GPQA/MINT/ProofWriter/AgentBench? | CodeActAgent reaches 52.0% (GPQA diamond vs. 81.3% expert human), 77.3% (MINT math), 78.8% (ProofWriter challenging subset), 57.6% (AgentBench OS). | C008, C009, C010 | CORE | Table 5 (misc. assistance) | GPQA | Discussion |
| D.1 | Discussion | N13 | So what does this establish about RQ1? | One unmodified agent produces interpretable results across all three categories, but effect sizes depend heavily on the backend model. | C006, C003 | CORE | - | - | mechanism |
| D.2 | Discussion | N16 | What does this imply for practice? | A shared platform lets researchers compare agents and evaluate risk systematically instead of building bespoke harnesses. | C015 | CORE | - | - | limitations |
| Lim.1 | Limitations | N15 (L001) | Is the result fragile to model choice? | Performance swings ~4x with backend model on the same benchmark. | C003 | CORE | - | - | subset limitation |
| Lim.2 | Limitations | N15 (L002) | Are these full-benchmark numbers? | Most results use reduced-cost subsets, not full benchmarks. | C020 | CORE | - | - | capability limitation |
| Lim.3 | Limitations | N15 (L003, L004) | What can agents still not do? | Agents still struggle with complex tasks/long-file editing; building new workflows is still handcrafted. | C013, C014 | CORE | - | - | Conclusion |
| C.1 | Conclusion | N14, N17 | What should the reader remember? | OpenHands demonstrates that one open platform and one generalist agent can be measured across three different agentic domains, with model choice and evaluation cost as the main open questions. | C001, C006, C011 | CORE | - | - | (end) |
| Abs | Abstract | (spine) | one-paragraph miniature | derived last from the finished spine | C001,C002,C004,C006,C007,C008,C011 | CORE | - | - | - |

## Checks (ticked before Gate G2)
- [x] Every story-graph node appears in >=1 row (N01-N18 covered above; N02 folded into I.2, N17 folded into C.1)
- [x] RQ (N05) has result rows (R.1-R.4), interpretation rows (D.1), discussion rows (D.1-D.2)
- [x] No row without a story node
- [x] Question ledger: 0 planned debt beyond forward references resolved by end of paper (see question_ledger.json)
- [x] Term ledger: defining row precedes first-use row for every registered term
- [x] All visuals are tables with a stated takeaway (no figures; task forbids images)
- [x] No SUPPLEMENTARY items (short paper; task disallows a supplement)
- [x] Negative result E034 placed in Results R.1 per negative_result_decisions (reported_main)
