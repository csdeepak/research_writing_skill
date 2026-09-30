# Research skeleton (one topic sentence per paragraph slot; step 9)

**Title.** OpenHands: one open platform for software-interacting agents, and one generalist agent that is competitive across it {C013}.

**Abstract.**
AB.1 Building agents that act on the world through real software requires an interaction mechanism, safe execution, a tool library, multi-agent support, and evaluation together {C021}.
AB.2 Existing open frameworks each supply only some of these pieces.
AB.3 OpenHands supplies all five, and this paper asks whether one agent built on it, unmodified across tasks, is then competitive with specialists.
AB.4 The same CodeActAgent reaches 26.0% on SWE-Bench Lite, 79.3% on HumanEvalFix, 52.0% on GPQA, and 32.1% on GAIA {C001}{C003}{C008}{C007}, matching or exceeding most compared baselines {C013}.
AB.5 This suggests a sufficiently general interaction interface, not per-task engineering, drives the result, though the pattern is not universal and the authors themselves flag remaining limits {L002}{L008}.

**Introduction.**
I.1 Building an agent that acts through code, a shell, and a browser currently means assembling the interaction mechanism, a safe runtime, a tool library, multi-agent support, and evaluation from separate, incompatible frameworks.
I.2 Software is already humans' most general, powerful interface for acting on the world, which is why the authors chose it as the substrate for agents {C030}.
I.3 Prior frameworks each cover part of this space but, dimension by dimension, none combines general sandboxed execution, an extensible tool library, delegation, and evaluation in one open platform {C021}.
I.4 This paper asks: can one platform supply all five pieces together (RQ1), and can a single generalist agent built on it, unmodified across benchmarks, then be competitive across qualitatively different task categories (RQ2)?
I.5 OpenHands answers RQ1 with an event-stream architecture connecting one agent to a Docker-sandboxed runtime through three actions, chosen for being flexible, reliable, and easy to maintain {C031}{C032}{C033}.
I.6 Its contributions are the platform itself and the empirical finding that one unmodified CodeActAgent reaches specialist-range scores across software, web, and other assistance benchmarks {C013}{C001}{C003}{C007}{C008}.
I.7 The rest of the paper positions this against prior frameworks, describes the platform, then answers RQ2 with results from all three categories before discussing what the pattern means and where it breaks.

**Related Work.**
RW.1 Rather than list frameworks one by one, this section organizes them by which of the five needed pieces each one supplies {C021}.
RW.2 General orchestration frameworks give basic runtime support, stateless execution, or a limited code interpreter, never a full sandbox plus browser.
RW.3 Single-capability specialists excel at one piece (browsing, or prompt optimization) and supply none of the rest.
RW.4 Collaboration-pattern frameworks optimize how agents work together, not the execution substrate each one acts through, and OpenHands' own workflow remains comparatively handcrafted next to them {L005}.
RW.5 Software-engineering specialist agents resolve GitHub issues well within their own task family, and their insight that a crafted interface matters is exactly what OpenHands generalizes into a shared tool library {C031}.

**Method.**
M.1 OpenHands connects an agent to a Docker-sandboxed runtime (a bash shell, an IPython server, and a browser) through an event stream and three core actions.
M.2 This code-execution action space was chosen over fixed tool-calling for being comprehensive, flexible, reliable, and easy to maintain, and the sandbox isolates every session so agent-written code cannot damage the user's system {C032}{C033}.
M.3 The AgentSkills tool library adds a skill only when the LLM cannot already write the needed code, or the skill must call an external model {C034}.
M.4 Agents can delegate subtasks to one another, and the AgentHub packages this into ready-to-use agents, including generalist, browsing, graph-optimized, and task-specialized "micro" agents {C037}.
M.5 A mocked-LLM integration-test suite gives deterministic, low-cost regression checks on every change {C035}.

**Experimental Setup.**
ES.1 One CodeActAgent -- delegating browser subtasks to BrowsingAgent, and orchestrated by GPTSwarm for GAIA -- is run zero-shot, with no benchmark-specific prompt changes, across 15 benchmarks in three categories, against each benchmark's own published baselines {C036}.
ES.2 For software engineering specifically, the evaluation defaults to the smaller SWE-Bench Lite subset and withholds its optional hint text, for cost and realism {C036}.

**Results.**
R.1 On SWE-Bench Lite, OpenHands reaches 26.0% with claude-3-5-sonnet, within the range of the compared specialist agents, and its score rises with backbone-model strength {C001}{C002}.
R.2 This result is a single run without seed variance, and its meaning is bounded to that scope, but it directly answers the software half of RQ2.
R.3 On HumanEvalFix, OpenHands fixes 79.3% of bugs zero-shot, clearly ahead of non-agentic baselines and behind only a specialist agent that -- as the authors themselves note -- was given a worked demonstration OpenHands was not {C003}{C004}{L004}.
R.4 On WebArena, OpenHands is at or above the prior domain-general-prompting baseline, though still behind trained specialists {C005}.
R.5 On MiniWoB++, by contrast, a trained reinforcement-learning specialist clearly outperforms every prompted agent shown, OpenHands included -- the paper's clearest negative result {C006}.
R.6 Across six more varied benchmarks (GAIA, GPQA, AgentBench, MINT, ProofWriter, Entity Deduction Arena), OpenHands matches or exceeds each one's own baseline in five of six cases {C007}{C008}{C009}{C010}{C011}{C012}.
R.7 The one exception, MINT's code subset, joins MiniWoB++ as evidence that the pattern is common but not universal {C010}{C014}.

**Discussion.**
D.1 Taken together, the same unmodified agent is competitive across all three categories on most of the benchmarks tested, answering RQ2 for the typical, not the universal, case {C013}.
D.2 The clearest driver of the remaining gap to specialists is the backbone LLM's own capability, not the task category, since swapping only the model moves scores far more than swapping category does {C014}.
D.3 RQ1 is answered by construction: every one of the five pieces prior frameworks split across projects is present, and demonstrated, in this one platform.
D.4 This confirms the dimension-by-dimension gap argued in Related Work, and extends the single-task ACI insight into a general, reusable tool library {C021}{C031}.
D.5 Beyond the numbers, an open, MIT-licensed platform with a large contributor base has continued to expand since publication, consistent with lowering the barrier to this kind of agent research {C040}{C041}.

**Limitations.**
Lim.1 The authors themselves concede that multi-modal support is not yet principled, that current agents (their own included) still struggle with complex tasks, that long-file editing is weak, and that workflows remain largely handcrafted {L001}{L002}{L003}{L005}.
Lim.2 They also flag, specifically, that the HumanEvalFix comparison is not matched, since the stronger baseline had a demonstration OpenHands did not {L004}.
Lim.3 Additional caveats: the 15-benchmark comparison is not a controlled ablation of the architecture alone, no run reports seed variance, and the competitive pattern has genuine exceptions {L006}{L007}{L008}.

**Conclusion.**
Con.1 A single, unmodified generalist agent built on one open platform is competitive with category specialists across most of 15 benchmarks spanning software, web, and other assistance tasks {C013}.
Con.2 This points to the interaction interface itself, more than bespoke per-task engineering, as a direct route to generality {C014}.
Con.3 The boundary is real: the pattern has exceptions, and the authors' own broadest concession is that current agents still struggle with complex tasks {L002}{L008}.
Con.4 The authors point to stronger training/inference-time techniques, automatic workflow generation, and principled multi-modality as what should follow.

## G2 self-reconstruction check (read the skeleton alone, top to bottom, then answer)
Q1 problem: agents that act through software need 5 pieces no single open framework combined -- answerable (I.1).
Q2 motivation: software is already the most general interface humans have -- answerable (I.2).
Q3 RQ: can one platform supply all 5 pieces, and is one unmodified agent then competitive across categories -- answerable (I.4).
Q4 what they did: built OpenHands (event stream + sandbox + 3 actions + AgentSkills + delegation + AgentHub), ran one CodeActAgent across 15 benchmarks -- answerable (I.5, M.1-M.4, ES.1).
Q5 why this method: code actions for flexibility/reliability; sandbox for safety; AgentSkills' inclusion rule to avoid bloat -- answerable (M.2, M.3).
Q6 experiments: SWE-Bench Lite/HumanEvalFix (software), WebArena/MiniWoB++ (web), 6 more (misc) -- answerable (R.1-R.6).
Q7 strongest results: 26.0% SWE-Bench Lite, 79.3% HumanEvalFix, 52.0% GPQA, 32.1% GAIA -- answerable (R.1, R.3, R.6, AB.4).
Q8 what results establish: one unmodified agent is competitive across categories, tracking backbone capability -- answerable (D.1, D.2).
Q9 what they do NOT establish: not a controlled ablation; not universal (MiniWoB++, MINT-code); single runs only -- answerable (Lim.3, R.5, R.7).
Q10 primary contribution: the platform + the cross-category competitiveness finding -- answerable (I.6, Con.1).
Q11 main limitations: authors' own (multi-modality, complex tasks, file editing, handcrafted workflows, the HumanEvalFix asymmetry) then the writer's additional caveats -- answerable (Lim.1-Lim.3).
Q12 one-day-later memory: one open platform + one unmodified agent competitive across categories, mechanism = interface not per-task engineering, boundary = not universal -- answerable (Con.1-Con.3).
**All 12 answerable from the skeleton alone -> Gate G2 passes.** No return to step 8 needed.
