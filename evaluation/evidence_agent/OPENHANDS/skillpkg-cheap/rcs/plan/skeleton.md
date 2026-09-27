# Research skeleton (one sentence per paragraph slot)

## Introduction
I.1 Building agents that act through code execution, a terminal, and a browser requires infrastructure that most projects re-implement, and evaluating one agent across many benchmarks is expensive {C020}.
I.2 Several agent systems already exist, but each is built and evaluated inside its own narrow-benchmark harness {C001}.
I.3 Within the evidence available for this platform, no single open system integrates one common agent interface with a broad set of benchmarks spanning software engineering, web browsing, and general assistance {C001,C011}.
I.4 This raises the question: can one open platform, exposing a small common action interface, host a single generalist agent evaluated without per-domain prompt changes across these three categories, and does that agent reach measurable performance in each {no claim: question}?
I.5 OpenHands answers this by providing a minimal three-action interface, a reproducibly-tagged containerized runtime, deterministic LLM-mocked integration tests, and harnesses for 15 benchmarks {C001,C011,C018,C019}.
I.6 The paper's contribution is this open, MIT-licensed platform together with a demonstration that one generalist agent, unmodified, is evaluated across all three categories {C001,C011,C012}.
I.7 The rest of the paper is organized by these three task categories, in the order software engineering, web browsing, and miscellaneous assistance, followed by what these results do and do not establish.

## Related Work
RW.1 SWE-Agent, AutoCodeRover, and Aider are evaluated on SWE-Bench Lite with their own harnesses, and the WebArena Agent ({SRC-001}) is evaluated on WebArena with its own harness {no new claim: background}.
RW.2 OpenHands differs from these by integrating many benchmarks under one shared agent interface rather than pairing one bespoke harness with one benchmark family {C001,C011}.

## Platform and Method
M.1 An OpenHands agent is a loop that observes environment state and emits one of three action types: running code, running a shell command, or interacting with a browser {C001}.
M.2 The runtime is containerized and uses a dual-tagging scheme, a hash-based tag for exact reproducibility and a generic tag for the latest version, to balance reproducibility with flexibility {C018}.
M.3 An integration-test framework mocks LLM calls against exact prompt matches so behavior can be checked deterministically without incurring live model costs {C019}.
M.4 Fifteen benchmarks are integrated across three categories: seven in software engineering, two in web browsing, and six in miscellaneous assistance {C011}.

## Experimental Setup
ES.1 The same CodeActAgent configuration (a BrowsingAgent variant for the two web benchmarks) is run without system-prompt changes across all benchmark categories, and reduced-size subsets are used for some benchmarks because full-scale evaluation is costly {C006,C020}.

## Results
R.1 On SWE-Bench Lite (300 instances, no hint text), CodeActAgent v1.8 reaches 26.0% with claude-3.5-sonnet, 22.0% with gpt-4o, and 6.3% with gpt-4o-mini, against baselines up to 26.3% {C002,C003}.
R.2 On the HumanEvalFix Python subset (164 instances), CodeActAgent v1.5 fixes 79.3% of bugs 0-shot using multi-turn self-debugging {C004,C005}.
R.3 On WebArena (812 instances) and the full MiniWoB++ set (125 environments, some requiring vision), BrowsingAgent v1.0 reaches 8.5-15.5% and 40.8% respectively, depending on the backend model {C007}.
R.4 On miscellaneous-assistance benchmarks, the agent reaches 52.0% on GPQA diamond (vs. 81.3% for expert humans), 77.3% on MINT math, 78.8% on the challenging ProofWriter subset, and 57.6% on AgentBench OS {C008,C009,C010}.

## Discussion
D.1 Because the same unmodified agent produces interpretable numbers in every category, these results are consistent with a shared agent interface being sufficient for cross-domain evaluation, though effect sizes depend heavily on the backend model {C006,C003}.
D.2 A shared open platform lets researchers compare agents and run systematic risk evaluation across domains instead of building bespoke per-benchmark harnesses {C015}.

## Limitations
Lim.1 Performance depends strongly on the backend model, with roughly a 4x swing on the same SWE-Bench Lite setup {L001}.
Lim.2 Most reported numbers come from reduced-cost benchmark subsets rather than full benchmarks {L002}.
Lim.3 Agents built on the platform still struggle with complex tasks and editing long files, and building new agent workflows still requires substantial handcrafted effort {L003,L004}.

## Conclusion
C.1 OpenHands shows that one open platform and one generalist agent can be measured, without per-domain modification, across software engineering, web browsing, and general-assistance tasks, with backend-model choice and evaluation cost as the main open questions going forward {C001,C006,C011}.

## Abstract (written last, from the finished spine)
Compresses lines 1-7 of the spine with the headline numbers from R.1-R.4.
