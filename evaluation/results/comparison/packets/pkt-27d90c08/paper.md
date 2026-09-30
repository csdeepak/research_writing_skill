# OpenHands: One Open Platform, One Generalist Agent, Three Task Categories

## Abstract

Building an AI agent that acts on the world through real software -- writing code, running a shell, browsing the web -- currently means assembling an interaction mechanism, a safe execution environment, an extensible tool library, multi-agent support, and an evaluation harness from separate, largely incompatible frameworks. OpenHands is an open, MIT-licensed platform that supplies all five pieces through one event-stream architecture: three core actions execute inside a Docker-sandboxed runtime, an AgentSkills library adds a tool only when a model cannot already write the needed code, agents can delegate subtasks to one another, and an integrated harness spans 15 established benchmarks across three categories. Its evaluation asks whether a single generalist agent, run with no per-benchmark change to its prompt, is competitive with baselines built and tuned for one category at a time. The same CodeActAgent reaches a 26.0% resolve rate on SWE-Bench Lite, fixes 79.3% of HumanEvalFix bugs zero-shot, scores 52.0% on GPQA, and reaches 32.1% on GAIA, matching or exceeding most baselines reported for these and seven further benchmarks spanning software engineering, web browsing, and other tool-use and reasoning tasks. Performance scales strongly with the backbone model, suggesting the residual gap to specialists tracks the model at least as much as the platform. The pattern is not universal: on MiniWoB++, a trained reinforcement-learning specialist outperforms every prompted agent shown, OpenHands included, by a wide margin, and the platform's own authors note that current agents, their own included, still struggle with complex tasks.

## 1 Introduction

Software is the main channel through which a skilled human developer acts on the world: writing code, running commands, and browsing for information. Building an artificial agent -- a system that repeatedly perceives its environment's state and produces an action for it, receiving an observation back -- that acts the same way means solving several problems together: how the agent and its tools communicate, how its code and commands run without harming the user's own machine, what tools it has beyond raw code, how several agents can work together, and how to tell whether any of this actually works. Today, building such an agent means assembling these five pieces from separate frameworks that were not designed to fit together.

The choice to build around software specifically is not incidental. Software is one of the most powerful tools available to a person for affecting the world, and the tooling already built around writing, running, and deploying it is extensive. Because that tooling already exists, software is also, in the same sense, an unusually complete interface for an artificial agent: whatever a human developer can reach through a terminal, an editor, or a browser, an agent that shares those same channels can in principle reach too.

Existing open agent frameworks each address part of this problem. General orchestration libraries such as LangChain and LangGraph (Chase, 2022) compose language-model calls and tools into chains or graphs but provide only basic runtime support; AutoGen (Wu et al., 2023) adds real code execution but keeps it stateless between calls; CrewAI (CrewAI, 2024) offers a sandboxed code interpreter that is explicitly limited in scope. A second group specializes in one capability instead of generalizing: BrowserGym (Drouin et al., 2024) targets web browsing, and DSPy (Khattab et al., 2024) targets prompt optimization, neither offering a sandbox, a tool library, or multi-agent support. A third group specializes by task: SWE-Agent (Yang et al., 2024), AutoCodeRover (Zhang et al., 2024b), and Agentless (Xia et al., 2024) resolve GitHub issues well, building on the finding that a carefully designed agent-computer interface (ACI) -- the specific tools an agent is given for acting on its environment -- changes how well the same underlying model performs, independently of the model itself (Yang et al., 2024), an insight this paper's platform generalizes into a shared, extensible library rather than a one-off interface. None of these frameworks, individually, combines a general sandbox, an extensible tool library, multi-agent delegation, and a matching evaluation harness.

This paper asks two connected questions. First, can one open platform supply, together, the interaction mechanism, safe execution, extensible tooling, multi-agent support, and evaluation that existing frameworks provide only piecemeal? Second, once such a platform exists, can a single generalist agent built on it -- with no change to its prompt from one benchmark to the next -- perform competitively across qualitatively different task categories: software engineering, web browsing, and other tool-use and reasoning assistance?

OpenHands answers the first question. It is an open, MIT-licensed platform whose event-stream architecture connects an agent to a Docker-sandboxed runtime through three core actions, inspired by CodeAct (Wang et al., 2024a): running Python code, running shell commands, and interacting with a browser. This code-execution action space was chosen over fixed, pre-defined tool calls because it is flexible enough to express any task while staying reliable and easy to maintain, and every session runs inside its own isolated container so that agent-issued code cannot affect the user's own system. An extensible tool library, multi-agent delegation, a hub of ready-to-use agents, and an integrated 15-benchmark evaluation harness complete the platform.

This gives two contributions. First, an open platform that combines, in one codebase, the five pieces Section 2 shows no single prior framework combines. Second, and the paper's central finding: the same CodeActAgent, run unmodified, reaches a 26.0% resolve rate on SWE-Bench Lite, fixes 79.3% of HumanEvalFix bugs, scores 52.0% on GPQA, and reaches 32.1% on GAIA, matching or exceeding most of the baselines built for one category at a time, across 9 of the 11 benchmarks whose scores could be recovered with confidence.

Section 2 positions OpenHands against prior frameworks by the pieces each one supplies. Section 3 describes the platform. Section 4 details the evaluation protocol. Section 5 reports results by category. Section 6 asks what the pattern means and where it holds. Section 7 states the limitations, the authors' own conceded ones first.

## 2 Related Work

Rather than survey frameworks one at a time, this section groups them by which of the five pieces identified above -- interaction mechanism, safe execution, tool library, multi-agent support, evaluation -- each one supplies.

General orchestration frameworks compose language-model calls into pipelines. LangChain and LangGraph (Chase, 2022) provide foundational building blocks with basic runtime support; AutoGen (Wu et al., 2023) goes further by adding real Python and bash execution, though its command execution is stateless between calls; CrewAI (CrewAI, 2024) adds a code interpreter that is explicitly limited. None of the three adds a browser, a standardized tool library beyond its own, or an evaluation harness spanning multiple task categories.

A second group of frameworks specializes in one capability instead. BrowserGym (Drouin et al., 2024), whose action space OpenHands itself reuses for browsing, targets web interaction specifically; DSPy (Khattab et al., 2024) targets prompt optimization. Neither is an execution platform in the sense used here: excelling at one piece does not, by itself, supply the other four.

A third group focuses on how multiple agents collaborate rather than on what any one agent can do. MetaGPT (Hong et al., 2023) standardizes team-like operating procedures for software generation; GPTSwarm (Zhuge et al., 2024) represents an agent system as an optimizable graph and is itself one of the agents available through OpenHands' own agent hub. The comparison also runs the other way: next to GPTSwarm's automatically optimized graphs, OpenHands' own authors concede that building a new agent workflow on their platform still takes considerable manual engineering.

A fourth group specializes by task rather than by capability. SWE-Agent (Yang et al., 2024), AutoCodeRover (Zhang et al., 2024b), ChatDev (Qian et al., 2023), AgentCoder (Huang et al., 2024), and Agentless (Xia et al., 2024) each resolve GitHub issues well within that one task family -- SWE-Agent, AutoCodeRover, and Agentless reach 18.0%, 19.0%, and 27.3% respectively on SWE-Bench Lite (Jimenez et al., 2024) -- but none is evaluated, in the sources surveyed here, outside software engineering.

## 3 Method

OpenHands connects an agent to its environment through an event stream: a chronological record of every past action and every observation returned for it, which together form the agent's working state. Three actions, inspired by CodeAct (Wang et al., 2024a), cover most of what a human developer does: running Python code, running shell commands, and interacting with a browser through a domain-specific language adapted from BrowserGym (Drouin et al., 2024). Each session executes inside a Docker sandbox -- an isolated container separate from the host machine -- built from any base image the user supplies, so the same platform can target different operating systems and toolchains.

This code-execution action space was chosen over a fixed list of pre-defined tool calls because it is a comprehensive, flexible set of primitives that stays reliable and easy to maintain, while remaining compatible with tool-calling agents built the conventional way. The sandbox answers a design question OpenHands' authors raise directly: how to let an agent modify a real system without risking the user's own machine. Inside it, an action-execution server exposes a bash shell, a Jupyter server, and a Playwright-driven browser whose observations include the page's HTML, its accessibility tree (a structured, text-like description of the page's elements), and a screenshot.

A general action space is not, by itself, enough: some tasks need capabilities an agent cannot reach by writing ordinary code, such as parsing a PDF or calling a vision-language model on an image. OpenHands packages these as AgentSkills, a library of Python functions the agent can call directly. Its authors state an explicit inclusion rule -- a skill is added only if a language model cannot already write the needed code itself, or if the skill must call an external model -- precisely to avoid re-teaching an agent things it already knows.

Agents can also hand work to one another through a dedicated delegation action. The default generalist agent, CodeActAgent, has only limited native support for web interaction, so it delegates browsing subtasks to a specialized Browsing Agent; a GPTSwarm-based agent (Zhuge et al., 2024) is available for tasks that benefit from an optimized multi-agent graph; and "micro agents" reuse a generalist agent's implementation but narrow its prompt to one recurring use case, explicitly to lower the barrier for the community to contribute specialized behavior without writing a new agent from scratch.

Because agents are complex software and language-model outputs are not deterministic, OpenHands also runs an integration-test suite that intercepts every model call and replays a cached response for an exact prompt match, giving repeatable, low-cost regression tests on every code change.

## 4 Experimental Setup

The evaluation asks whether one agent, run without any benchmark-specific change to its prompt, is competitive with agents built for one benchmark at a time. Concretely: one CodeActAgent -- delegating browsing subtasks to Browsing Agent, and in one case (GAIA) run through the GPTSwarm agent instead -- is evaluated zero-shot on 15 established benchmarks spanning three categories: software engineering, web browsing, and other tool-use and reasoning tasks. Each benchmark keeps its own metric and its own published baselines, so every comparison below is to numbers each benchmark's own authors, or the compared systems' own authors, originally reported. Success is reported as a resolve rate (the percentage of SWE-Bench issues whose hidden tests pass after the agent's patch), a pass rate (the percentage of tasks solved in a single attempt), or an accuracy/success rate, depending on the benchmark.

For software-engineering evaluation specifically, the platform defaults to the 300-instance SWE-Bench Lite subset rather than the full 2,294-instance set, and withholds the benchmark's optional natural-language hint text, for cost and to keep the setting realistic.

## 5 Results

**Software engineering.** On SWE-Bench Lite (Jimenez et al., 2024), OpenHands' CodeActAgent v1.8 resolves 22.0% of issues with gpt-4o and 26.0% with claude-3-5-sonnet (Table 1). That places it inside the range covered by three specialist agents evaluated on the same 300 instances: SWE-Agent (Yang et al., 2024) at 18.0%, AutoCodeRover (Zhang et al., 2024b) at 19.0%, and Agentless (Xia et al., 2024) at 27.3%.

Each of these numbers is a single run, with no seed or repeat-trial variance reported, so the exact size of any gap between rows should be read as a point estimate rather than a precise difference. What the comparison does show is that swapping only the backbone model, with everything else held fixed, moves OpenHands' own score by four points -- close to the full spread between the three specialist agents. This answers the software half of the second question posed above: without modification, the agent lands among specialists built specifically for this one task.

On HumanEvalFix (Muennighoff et al., 2024), OpenHands' CodeActAgent v1.5 fixes 79.3% of 164 Python bugs zero-shot with gpt-4o, well ahead of the strongest non-agentic baseline reported, StarCoder2-15B at 48.6%, and ahead of its own gpt-3.5-turbo-16k configuration at 20.1% (Table 1). Only SWE-Agent (Yang et al., 2024), at 87.7%, scores higher -- but, as OpenHands' authors note directly, SWE-Agent was given a full worked demonstration of a successful fix before attempting the benchmark, while OpenHands was evaluated with no demonstration at all. This one exception is therefore evidence of an unequal comparison the authors chose to disclose, not necessarily of a clean architectural shortfall.

**Table 1.** OpenHands' CodeActAgent reaches specialist-range scores on both software-engineering benchmarks tested here, trailing only a differently-shot comparison on HumanEvalFix. Resolve rate on SWE-Bench Lite (300 instances, no hint text) and pass rate on HumanEvalFix (164 Python instances, single attempt); OpenHands' own rows are in bold. Source: Jimenez et al. (2024); Muennighoff et al. (2024).

| Benchmark | Agent | Backbone model | Score |
|---|---|---|---|
| SWE-Bench Lite | SWE-Agent (Yang et al., 2024) | gpt-4-1106-preview | 18.0% |
| SWE-Bench Lite | AutoCodeRover (Zhang et al., 2024b) | gpt-4-0125-preview | 19.0% |
| SWE-Bench Lite | **OpenHands CodeActAgent v1.8** | **gpt-4o** | **22.0%** |
| SWE-Bench Lite | **OpenHands CodeActAgent v1.8** | **claude-3-5-sonnet** | **26.0%** |
| SWE-Bench Lite | Agentless (Xia et al., 2024) | gpt-4o | 27.3% |
| HumanEvalFix | **OpenHands CodeActAgent v1.5 (0-shot)** | **gpt-3.5-turbo-16k** | **20.1%** |
| HumanEvalFix | StarCoder2-15B (non-agentic) | -- | 48.6% |
| HumanEvalFix | **OpenHands CodeActAgent v1.5 (0-shot)** | **gpt-4o** | **79.3%** |
| HumanEvalFix | SWE-Agent (1-shot demonstration) (Yang et al., 2024) | gpt-4-turbo | 87.7% |

**Web browsing.** On WebArena (Zhou et al., 2023a), OpenHands' Browsing Agent reaches 15.5% with claude-3-5-sonnet and its CodeActAgent reaches 15.3% via delegation to the same agent, both at or above the prior domain-general-prompting baseline, WebArena Agent with gpt-4-turbo, at 14.4% (Table 2). Trained systems span a wider range around this: two score below OpenHands (Lemur at 5.3% (Xu et al., 2023); a 72B model trained with self-improvement synthetic data at 9.4% (Patel et al., 2024)), while two score above it (AutoWebGLM at 18.2% (Lai et al., 2024); Auto Eval & Refine, which combines a retry loop with a learned reward model, at 20.2% (Pan et al., 2024)).

On MiniWoB++ (Liu et al., 2018), the pattern changes. OpenHands' best configuration reaches 40.8% with gpt-4o, well above its own weaker-backbone configuration at 27.2%, but CC-Net (Humphreys et al., 2022), a system trained with reinforcement learning and human-annotated demonstrations specifically for this benchmark, reaches 91.1% (Table 2). This is the evaluation's plainest negative result: a trained specialist outperforms every prompted agent shown here, OpenHands included, by a wide margin, and no swap between OpenHands' own backbone models closes more than a small fraction of that gap.

**Table 2.** OpenHands' web agent is at or above a prior domain-general baseline on WebArena, but a trained reinforcement-learning specialist outperforms it by a wide margin on MiniWoB++. Success rate on WebArena (812 instances) and MiniWoB++ (125 environments, full set); OpenHands' own rows are in bold. Source: Zhou et al. (2023a); Liu et al. (2018).

| Benchmark | Agent | Backbone model | Score |
|---|---|---|---|
| WebArena | Lemur (Xu et al., 2023) | Lemur-chat-70b | 5.3% |
| WebArena | Trained 72B, self-improvement (Patel et al., 2024) | -- | 9.4% |
| WebArena | WebArena Agent (domain-general) | gpt-4-turbo | 14.4% |
| WebArena | **OpenHands CodeActAgent (delegated)** | **claude-3-5-sonnet** | **15.3%** |
| WebArena | **OpenHands Browsing Agent** | **claude-3-5-sonnet** | **15.5%** |
| WebArena | AutoWebGLM, trained 7B (Lai et al., 2024) | -- | 18.2% |
| WebArena | Auto Eval & Refine (Pan et al., 2024) | GPT-4 + Reflexion + reward model | 20.2% |
| MiniWoB++ | **OpenHands Browsing Agent** | **gpt-3.5-turbo-0125** | **27.2%** |
| MiniWoB++ | Workflow-Guided Exploration (Liu et al., 2018) | trained specialist | 34.6% |
| MiniWoB++ | **OpenHands Browsing Agent** | **gpt-4o** | **40.8%** |
| MiniWoB++ | CC-Net (Humphreys et al., 2022) | trained RL + human demonstrations | 91.1% |

**Beyond code and browsers.** Six further benchmarks test reasoning, tool use, and planning, with little in common with either code editing or web navigation: GAIA (Mialon et al., 2023) poses real-world assistant tasks that need browsing and reasoning together; GPQA (Rein et al., 2023) is a graduate-level, multiple-choice science benchmark; AgentBench's (Liu et al., 2023) operating-system subset requires completing tasks through direct bash interaction rather than through code editing or a browser; MINT (Wang et al., 2024b) gives an agent up to five rounds of tool use with feedback simulated by another language model; ProofWriter (Tafjord et al., 2021) is a synthetic deductive-reasoning benchmark; and the Entity Deduction Arena (Zhang et al., 2024a) has an agent deduce a hidden entity through strategic yes/no questioning.

OpenHands' CodeActAgent, again unmodified, exceeds or matches each benchmark's own baseline agent in five of the six (Table 3): 32.1% against AutoGPT's (Gravitas, 2023) 13.2% on GAIA; 52.0% against a gpt-4 few-shot chain-of-thought baseline's 38.8% on GPQA's diamond set -- above non-expert human accuracy (21.9%) though well below expert accuracy (81.3%); 57.6% against AgentBench's own 42.4%; 77.3% against MINT's 65.8% on its math subset; and 78.8% on ProofWriter's hardest, five-hop subset, above plain chain-of-thought at 68.1% and just under Logic-LM's (Pan et al., 2023) neuro-symbolic pipeline at 79.6%.

The sixth case is the exception: on MINT's code subset, OpenHands reaches 50.0% against the benchmark's own baseline's 59.6%, joining MiniWoB++ as evidence that the competitive pattern is common but not universal. On the Entity Deduction Arena, OpenHands' 38.0% sits within two points of zero-shot prompting's 40.0%, too close to call either way without repeated runs.

**Table 3.** Across six benchmarks that share neither code editing nor browsing as their primary skill, OpenHands' agent matches or exceeds each one's own baseline in five of six cases. Success/accuracy rate; OpenHands' own rows are in bold. Source: Mialon et al. (2023); Rein et al. (2023); Liu et al. (2023); Wang et al. (2024b); Tafjord et al. (2021); Zhang et al. (2024a).

| Benchmark | Agent | Backbone model | Score |
|---|---|---|---|
| GAIA (L1 validation) | AutoGPT (Gravitas, 2023) | gpt-4-turbo | 13.2% |
| GAIA (L1 validation) | **OpenHands GPTSwarm agent** | **gpt-4o** | **32.1%** |
| GPQA (diamond) | Non-expert human | -- | 21.9% |
| GPQA (diamond) | Few-shot chain-of-thought | gpt-4 | 38.8% |
| GPQA (diamond) | **OpenHands CodeActAgent** | **claude-3-5-sonnet** | **52.0%** |
| GPQA (diamond) | Expert human | -- | 81.3% |
| AgentBench (OS subset) | Baseline agent | gpt-4 | 42.4% |
| AgentBench (OS subset) | **OpenHands CodeActAgent** | **gpt-4o** | **57.6%** |
| MINT (math subset) | Baseline agent | gpt-4-0613 | 65.8% |
| MINT (math subset) | **OpenHands CodeActAgent** | **gpt-4o** | **77.3%** |
| MINT (code subset) | **OpenHands CodeActAgent** | **gpt-4o** | **50.0%** |
| MINT (code subset) | Baseline agent | gpt-4-0613 | 59.6% |
| ProofWriter (5-hop) | Few-shot chain-of-thought | gpt-4 | 68.1% |
| ProofWriter (5-hop) | **OpenHands CodeActAgent** | **gpt-4o** | **78.8%** |
| ProofWriter (5-hop) | Logic-LM + symbolic solver (Pan et al., 2023) | gpt-4 | 79.6% |
| Entity Deduction Arena | **OpenHands CodeActAgent** | **gpt-4o** | **38.0%** |
| Entity Deduction Arena | Zero-shot prompting | gpt-4 | 40.0% |

## 6 Discussion

Across the 11 benchmarks whose scores could be recovered with confidence from the source tables, the same unmodified CodeActAgent matches or exceeds a relevant baseline in 9 of 11 cases, spanning all three categories. That directly answers the paper's second question, though not unconditionally: the agent is competitive on the majority of the benchmarks tested, not on every one of them.

The most direct explanation for the remaining gap to specialists is the backbone language model, not the task category. Holding the agent and its prompt fixed and swapping only the model moves scores by tens of points within a single benchmark -- from 11.8% to 57.6% on AgentBench's OS subset, and from 5.2% to 50.0% on MINT's code subset -- more than the gap between OpenHands and most of the specialist baselines it is compared against. An alternative explanation, that the architecture itself is tuned differently per category, is harder to sustain here, because the prompt does not change between benchmarks; what changes, when it changes at all, is only the backbone model or which AgentHub agent handles delegation.

This also speaks to the first question. Each of the five pieces earlier frameworks split across separate projects -- an interaction mechanism, a sandboxed runtime, an extensible tool library, multi-agent delegation, and an evaluation harness -- is present in this one platform, and the 15-benchmark run above is itself a demonstration that all five work together rather than only on paper.

This is consistent with the dimension-by-dimension picture in Section 2: general orchestration frameworks lacked a full sandbox, single-capability frameworks lacked the rest of the platform, and task-specific agents were not shown operating outside their own task. It also extends one specific idea from that section -- that a carefully designed agent-computer interface can change performance independently of the underlying model (Yang et al., 2024) -- from a single task's bespoke interface into a general, reusable library with its own inclusion rule.

Beyond the benchmark numbers, OpenHands is released under the MIT license and had, at the time of writing, more than 2.1 thousand contributions from over 188 contributors. The project's own repositories show continued growth since publication: an updated software-agent SDK, an expanded benchmark suite, and a separate control-center interface that now runs third-party agents alongside OpenHands' own. This is consistent with, though it does not by itself establish, the idea that open, extensible infrastructure lowers the practical barrier to this kind of agent research.

## 7 Limitations

OpenHands' authors state several limitations of their own. Multi-modal file handling -- images, video, office documents -- is not yet integrated in a principled way through the platform's standard channels, only through individually predefined skills. More broadly, and most directly bounding the paper's central finding, they write that current agents, their own included, still struggle with complex tasks. They also report that the current agent performs poorly when editing long files, and that building a new agent workflow on the platform still takes considerable hand engineering, unlike the automatically optimized graphs of frameworks such as GPTSwarm.

One further author-stated limitation concerns a specific number reported above: the HumanEvalFix comparison to SWE-Agent's 87.7% is not a matched comparison, because SWE-Agent was given a full worked demonstration that OpenHands was not. This bounds how the 79.3%-versus-87.7% gap should be read, as a difference in what each system was shown as much as a difference in what either system can do.

Additional caveats. Two further caveats follow from the evidence itself rather than from the authors' own statements. First, the 15-benchmark comparison is not a controlled, single-variable test of the architecture alone: compared systems differ in backbone model, in how many worked examples they were given, and in whether they were prompted, fine-tuned, or trained with reinforcement learning, so the competitive pattern reflects the platform-and-backbone combination as evaluated rather than an isolated architectural effect. Second, no benchmark cell reports seed or repeat-trial variance, so small gaps -- such as the two points separating OpenHands from zero-shot prompting on the Entity Deduction Arena -- cannot be distinguished from run-to-run noise with this evidence. Read together with MiniWoB++ and the MINT code subset, the central finding is best stated as a typical, majority pattern with visible exceptions, not as uniform parity or superiority across all 15 benchmarks.

## 8 Conclusion

A single, unmodified generalist agent, built on one open platform, is competitive with baselines built for one task category at a time across most of the 15 benchmarks examined here, spanning software engineering, web browsing, and other assistance tasks. The more direct explanation on offer is that a sufficiently general interaction interface, together with a shared execution runtime, does much of the work that per-task engineering would otherwise have to do, since the clearest driver of the remaining gap to specialists is the backbone model rather than the category.

The boundary on this finding is concrete, not generic: a trained specialist still wins on MiniWoB++, a baseline agent still wins narrowly on MINT's code subset (an exception recorded in Section 7's additional caveats), and the platform's own authors state, in their broadest concession, that current agents still struggle with complex tasks. The authors point to three next steps: stronger agents through both training- and inference-time techniques, automatic workflow generation through graph-based frameworks, and principled multi-modal support through the platform's own standard channels rather than one-off skills.

## References

Chase, H. (2022). *LangChain*. https://github.com/langchain-ai/langchain

CrewAI. (2024). *CrewAI*. https://github.com/crewAIInc/crewAI

Drouin, A., Gasse, M., Caccia, M., Laradji, I. H., Del Verme, M., Marty, T., Boisvert, L., Thakkar, M., Cappart, Q., Vazquez, D., Chapados, N., & Lacoste, A. (2024). WorkArena: How capable are web agents at solving common knowledge work tasks?

Gravitas, S. (2023). *Auto-GPT: An autonomous GPT-4 experiment*. https://github.com/Significant-Gravitas/Auto-GPT

Hong, S., Zhuge, M., Chen, J., Zheng, X., Cheng, Y., Wang, J., Zhang, C., Wang, Z., Yau, S. K. S., Lin, Z., et al. (2023). MetaGPT: Meta programming for a multi-agent collaborative framework. In *The Twelfth International Conference on Learning Representations*.

Huang, D., Bu, Q., Zhang, J. M., Luck, M., & Cui, H. (2024). AgentCoder: Multi-agent-based code generation with iterative testing and optimisation.

Humphreys, P. C., Raposo, D., Pohlen, T., Thornton, G., Chhaparia, R., Muldal, A., Abramson, J., Georgiev, P., Santoro, A., & Lillicrap, T. (2022). A data-driven approach for learning to control computers. In *International Conference on Machine Learning*, pp. 9466-9482. PMLR.

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. R. (2024). SWE-bench: Can language models resolve real-world GitHub issues? In *The Twelfth International Conference on Learning Representations*.

Khattab, O., Singhvi, A., Maheshwari, P., Zhang, Z., Santhanam, K., Vardhamanan, S., Haq, S., Sharma, A., Joshi, T. T., Moazam, H., Miller, H., Zaharia, M., & Potts, C. (2024). DSPy: Compiling declarative language model calls into self-improving pipelines.

Lai, H., Liu, X., Iong, I. L., Yao, S., Chen, Y., Shen, P., Yu, H., Zhang, H., Zhang, X., Dong, Y., et al. (2024). AutoWebGLM: Bootstrap and reinforce a large language model-based web navigating agent.

Liu, E. Z., Guu, K., Pasupat, P., Shi, T., & Liang, P. (2018). Reinforcement learning on web interfaces using workflow-guided exploration. In *International Conference on Learning Representations*.

Liu, X., Yu, H., Zhang, H., Xu, Y., Lei, X., Lai, H., Gu, Y., Ding, H., Men, K., Yang, K., Zhang, S., Deng, X., Zeng, A., Du, Z., Zhang, C., Shen, S., Zhang, T., Su, Y., Sun, H., Huang, M., Dong, Y., & Tang, J. (2023). AgentBench: Evaluating LLMs as agents.

Mialon, G., Fourrier, C., Swift, C., Wolf, T., LeCun, Y., & Scialom, T. (2023). GAIA: A benchmark for general AI assistants. *CoRR*, abs/2311.12983.

Muennighoff, N., Liu, Q., Zebaze, A., Zheng, Q., Hui, B., Zhuo, T. Y., Singh, S., Tang, X., von Werra, L., & Longpre, S. (2024). OctoPack: Instruction tuning code large language models.

Pan, J., Zhang, Y., Tomlin, N., Zhou, Y., Levine, S., & Suhr, A. (2024). Autonomous evaluation and refinement of digital agents.

Pan, L., Albalak, A., Wang, X., & Wang, W. Y. (2023). Logic-LM: Empowering large language models with symbolic solvers for faithful logical reasoning.

Patel, A., Hofmarcher, M., Leoveanu-Condrei, C., Dinu, M.-C., Callison-Burch, C., & Hochreiter, S. (2024). Large language models can self-improve at web agent tasks.

Qian, C., Cong, X., Liu, W., Yang, C., Chen, W., Su, Y., Dang, Y., Li, J., Xu, J., Li, D., Liu, Z., & Sun, M. (2023). Communicative agents for software development.

Rein, D., Hou, B. L., Stickland, A. C., Petty, J., Pang, R. Y., Dirani, J., Michael, J., & Bowman, S. R. (2023). GPQA: A graduate-level Google-proof Q&A benchmark.

Tafjord, O., Dalvi, B., & Clark, P. (2021). ProofWriter: Generating implications, proofs, and abductive statements over natural language. In *Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021*, pp. 3621-3634.

Wang, X., Chen, Y., Yuan, L., Zhang, Y., Li, Y., Peng, H., & Ji, H. (2024a). Executable code actions elicit better LLM agents. In *ICML*.

Wang, X., Wang, Z., Liu, J., Chen, Y., Yuan, L., Peng, H., & Ji, H. (2024b). MINT: Evaluating LLMs in multi-turn interaction with tools and language feedback. In *ICLR*.

Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., Li, B., Jiang, L., Zhang, X., & Wang, C. (2023). AutoGen: Enabling next-gen LLM applications via multi-agent conversation framework.

Xia, C. S., Deng, Y., Dunn, S., & Zhang, L. (2024). Agentless: Demystifying LLM-based software engineering agents.

Xu, Y., Su, H., Xing, C., Mi, B., Liu, Q., Shi, W., Hui, B., Zhou, F., Liu, Y., Xie, T., et al. (2023). Lemur: Harmonizing natural language and code for language agents.

Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., & Press, O. (2024). SWE-agent: Agent-computer interfaces enable automated software engineering.

Zhang, Y., Lu, J., & Jaitly, N. (2024a). Probing the multi-turn planning capabilities of LLMs via 20 question games.

Zhang, Y., Ruan, H., Fan, Z., & Roychoudhury, A. (2024b). AutoCodeRover: Autonomous program improvement.

Zhou, S., Xu, F. F., Zhu, H., Zhou, X., Lo, R., Sridhar, A., Cheng, X., Ou, T., Bisk, Y., Fried, D., et al. (2023a). WebArena: A realistic web environment for building autonomous agents. In *The Twelfth International Conference on Learning Representations*.

Zhuge, M., Wang, W., Kirsch, L., Faccio, F., Khizbullin, D., & Schmidhuber, J. (2024). Language agents as optimizable graphs.
