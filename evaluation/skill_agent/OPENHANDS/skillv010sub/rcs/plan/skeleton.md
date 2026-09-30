# Research skeleton (one topic sentence per paragraph slot; step 9)

## Introduction
I.1 Software is the most general interface through which an AI agent can act on the world, and a platform built on that idea is already used widely {C015 context}.
I.2 Prior open agent frameworks and specialized software-engineering agents each solve one piece of the needed infrastructure -- interaction depth, or one task category -- but not the whole set together {C018,C019}.
I.3 This raises the question: can one platform, and one generalist agent on it with a single fixed prompt, be competitive across software engineering, web browsing, and miscellaneous tasks at once?
I.4 OpenHands answers this with an event-stream interface, a sandboxed general action space, an extensible tool interface, and delegation, topped with a generalist CodeAct-based agent evaluated on 15 benchmarks {C017}.
I.5 Using one prompt, the agent is competitive -- rarely best -- in all three categories at once {C001,C004,C006,C015}; the paper returns later to where it is not best, to statistical caveats, and to safety.

## The OpenHands Platform
P.1 The agent's state is a chronological event stream of actions and observations plus bookkeeping.
P.2 Actions are executable code/bash or a browser command (CodeAct) rather than calls to a fixed tool menu, chosen for flexibility across task forms {C017}.
P.3 Each session runs in an isolated Docker sandbox exposing bash, IPython, and a browser, and can wrap any user-supplied base image.
P.4 An AgentSkills library forms an extensible agent-computer interface (ACI), added only when plain code cannot do the job or an external model is needed {C018}.
P.5 Agents may delegate subtasks to each other, an AgentHub of 10+ implementations includes a generalist agent, a browsing agent, a graph-based agent, and task-specialized micro agents, and a mocked-LLM integration-test suite guards quality as the codebase changes.

## Evaluation Setup
S.1 Fifteen benchmarks spanning software engineering, web browsing, and miscellaneous reasoning/tool-use are integrated unmodified, each with its own automated success check.
S.2 Evaluations mostly use 0-shot prompting, exclude SWE-Bench's optional hint text, use cost-motivated subsets for three benchmarks, and draw baseline numbers from the cited original papers rather than re-running them.

## Results: Software Engineering
R.SW.1 On SWE-Bench Lite the agent resolves 26.0% of issues (best backbone), inside the 18.0-27.3% range of five reproducible open SWE baselines {C001,C002; TAB-1}.
R.SW.2 On HumanEvalFix the agent fixes 79.3% of bugs 0-shot, beating every non-agentic baseline shown but trailing a 1-shot baseline given a full worked example {C003}.
R.SW.3 Across BIRD, ML-Bench, BioCoder, and Gorilla APIBench the agent's best configuration beats the non-agentic baselines shown; on ToolQA one backbone tops the table while another collapses to near-chance {C014,C013}.

## Results: Web Browsing
R.WEB.1 On WebArena the best web configuration reaches 15.5%, above two specialized baselines and below two others {C004}.
R.WEB.2 On MiniWoB++ the same agent (40.8% best) trails a reinforcement-learning-trained specialist (91.1%) by a wide margin {C005}.

## Results: Miscellaneous Assistance
R.MISC.1 On GAIA the agent more than doubles an AutoGPT baseline, and on GPQA-diamond it reaches 52.0%, above both LLM baselines and non-expert humans but below expert humans {C006,C007}.
R.MISC.2 The agent beats its comparison baseline on AgentBench, MINT-math, and ProofWriter, and falls below it on MINT-code and Entity Deduction Arena {C008,C009,C010,C011,C012}.

## Results: Cross-category Synthesis
R.SYN.1 The identical, unmodified agent is the one scored in every table, and no comparison baseline appears in more than one category -- a structural fact, not just a collection of individually strong numbers {C015; TAB-2}.

## Discussion
D.1 The research question's answer is yes, with qualifications: a single general action space on one shared platform supports simultaneous, competitive-but-rarely-best performance across categories {C016}.
D.2 This is consistent with the platform's own generality, not any one backbone model's strength alone, since the design is held fixed even as the model is swapped; it extends SWE-Agent's point that interface design matters, from one category to three {C016,C018}.
D.3 If confirmed with controlled comparisons, this suggests engineering effort may be better spent on one general, well-integrated platform than on separate per-domain agents {C016}.
D.4 The authors argue the platform mitigates some deployment risk through evaluation, human-agent interaction, and broadened access, though this is asserted, not benchmarked, here {C020}.

## Limitations and Future Work
LF.1 No seed or repeated-run variance is reported anywhere, and cross-agent comparisons vary the backbone model rather than holding it fixed {L001,L002}.
LF.2 OpenHands trails the best specialist on several individual benchmarks, and subset/protocol choices limit exact comparability across rows {L003,L004}.
LF.3 The evaluated versions are one snapshot of a fast-moving project since restructured around a separate SDK, and no experiment isolates which platform component drives the result {L005,L006}.
LF.4 The authors name five concrete next steps -- multi-modality, stronger agents, better long-file editing, browsing improvements, and automatic workflow generation -- and the safety framing of D.4 likewise remains to be tested empirically {C021,L007}.

## Related Work
W.1 General-purpose agent frameworks are characterized, in the source material, as providing execution and interaction primitives of varying depth -- for instance, execution without a persistent session {C019}.
W.2 Specialized software-engineering agents show that interface design matters within one category, but none of them is evaluated, in the source material, outside it {C018}.

## Conclusion
CN.1 OpenHands packages a general action space and its supporting infrastructure into one open platform on which one generalist agent is competitive, if rarely dominant, across categories that used to need separate agents -- with statistical, mechanistic, and currency caveats still open {C016}.

## Abstract (drafted last)
A one-paragraph miniature of the spine: context, gap, question, approach, key results with magnitudes, meaning, and scope.

## Title (drafted last)
A truthful promise naming the subject and the finding's shape.

---

## Gate G2 self-reconstruction (answer Q1-Q12 from the skeleton above, alone)

Q1 What problem is this paper solving? -> I.1-I.2: infrastructure for agents that act through software is fragmented across projects. **Answerable.**
Q2 Why does this problem matter? -> I.1 (already widely used) + I.2 (fragmentation is wasteful). **Answerable.**
Q3 What is missing from existing approaches? -> I.2, W.1-W.2: frameworks give pieces at varying depth; SWE agents don't test breadth. **Answerable.**
Q4 What exactly did the authors do? -> I.4, P.1-P.5: built an event-stream/sandbox/ACI/delegation platform + a generalist agent, evaluated on 15 benchmarks. **Answerable.**
Q5 Why did they choose this method? -> P.2 (flexibility across task forms), P.4 (contrast with SWE-Agent's ACI point). **Answerable.**
Q6 What experiments were performed? -> S.1-S.2, R.SW/R.WEB/R.MISC headers: 15 benchmarks across 3 categories, 0-shot mostly. **Answerable.**
Q7 What are the strongest results? -> I.5, R.SYN.1: cross-category competitiveness with one fixed prompt; specific numbers in R.SW.1/R.WEB.1/R.MISC.1. **Answerable.**
Q8 What do those results actually establish? -> D.1: a single general design can be competitive across domains at once. **Answerable.**
Q9 What do they NOT establish? -> LF.1-LF.3: not statistically characterized, not model-controlled, not the top performer everywhere, no ablation. **Answerable.**
Q10 What is the primary contribution? -> I.4/D.1/CN.1: one open platform + one generalist agent, shown competitive across categories simultaneously. **Answerable.**
Q11 What are the main limitations? -> LF.1-LF.4. **Answerable.**
Q12 What should the reader remember one day later? -> CN.1 (= spine lines 5-7). **Answerable.**

All 12 answerable from the skeleton alone. **Gate G2: passed.**
