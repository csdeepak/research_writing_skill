# OpenHands: An Open Platform for AI Agents That Act Through Code, Shell and Browser, and Its Evaluation on 15 Benchmarks

## Abstract

Software gives an AI agent a powerful way to act on the world, yet building and evaluating agents that write code, run shell commands and browse the web is hard. OpenHands is an open platform for such agents. It records every action and observation in an event stream, runs actions in a per-session Docker sandbox with a shell, Python and a browser, shares tools through a skills library, lets agents delegate subtasks, and integrates 15 benchmarks. This paper presents the authors' design and their evaluation for readers outside the agent subfield. The default CodeAct agent, without changes to its system prompt, scored 26.0% on SWE-bench Lite, a GitHub-issue-fixing benchmark (claude-3-5-sonnet), 79.3% on HumanEvalFix, a bug-fixing benchmark (gpt-4o), and 52.0% on GPQA diamond, a graduate-level question set (claude-3-5-sonnet), and the OpenHands browsing agent scored 15.5% on WebArena. The authors describe this as competitive across three categories and state that OpenHands agents may not achieve top performance in every category. Several listed reference systems score higher, for example 87.7% against 79.3% on HumanEvalFix and 91.1% against 40.8% on MiniWoB++. The authors state that current agents still struggle with complex tasks, and the reported numbers come without variance or matched baselines.

## 1 Introduction

In this paper an *agent* is a program driven by a large language model (LLM) that repeatedly chooses an *action* (for example, running code), receives an *observation* (the result), and continues until the task ends. The authors of OpenHands motivate their work by the power of software: given that power and the tooling around its development, use and deployment, they regard software as the ideal interface for agents to act on the world. They add that, as agents become able to tackle complex problems, developing and evaluating them has become challenging, and they pose three questions for agents that act through software: how to let agents create and modify code in complex systems, how to give them tools to gather information on the fly, and how to keep development safe for the user's system.

Open frameworks for building agents already exist. In the authors' description they generally include interfaces through which agents act, environments in which agents operate, and mechanisms for human-agent or agent-agent communication. The authors describe AutoGen (Wu et al., 2023) as executing Python and bash but with stateless command execution, and CrewAI (CrewAI, 2024) as offering sandboxed but limited code-interpreter features, while software-engineering systems such as SWE-Agent (Yang et al., 2024) and AutoCodeRover (Zhang et al., 2024b) target fixing GitHub issues. The gap, as the authors position it, is a single open platform that combines a sandboxed shell, Python and browser runtime with shared tools, the ability for one agent to hand a subtask to another, and a broad benchmark harness. Their comparison table lists twelve frameworks on such features, but the feature marks did not survive text extraction, so this paper presents the gap as the authors' positioning, not as a verified survey finding.

This paper asks two questions that follow from the authors' stated goal of general digital agents that interact with the world through software interfaces. The design question (RQ1): what infrastructure lets one open platform host community-built agents that act through code, a shell and a browser, run in isolation, and be evaluated on many tasks? The evaluation question (RQ2): how does a default generalist agent, one meant to handle several task categories, fare across software, web and assistance benchmarks when compared with open-source reproducible reference systems and without benchmark-specific prompt engineering? The authors do not phrase these questions themselves; they frame the authors' goal. The authors give a reason for the breadth of the evaluation: a software agent should excel not only in code editing but also in web browsing and auxiliary tasks.

OpenHands is the authors' answer. It combines an event stream that records what agents do, a sandboxed runtime in which actions execute, a shared tool library, agent delegation and a benchmark harness. Its agents act through a small set of programming-language primitives, which the authors chose to cover most tasks performed by human software engineers and analysts while staying flexible, reliable and easy to maintain.

The contributions, each with the place where its evidence sits, are:

1. The platform and the authors' stated rationale for its design (Section 3).
2. An evaluation of the platform's default agents on 15 benchmarks, reported beside reference systems and including rows where OpenHands scores lower (Sections 4 and 5).
3. An open release under an MIT license, with community activity reported by the authors as 32K GitHub stars, more than 2.1K contributions and over 188 contributors (Section 6).

The authors describe the outcome of the evaluation as competitive across categories but not top in every one. Section 2 covers related systems, Section 3 answers RQ1, Sections 4 and 5 address RQ2, and Sections 6 and 7 discuss and bound both answers.

## 2 Related work

*General agent frameworks.* As the authors describe them, MetaGPT (Hong et al., 2023) emphasizes standardized operating procedures, AutoGen (Wu et al., 2023) provides a conversation framework for interactive systems, and AutoAgents (Chen et al., 2024) offers customizable agent architecture; Auto-GPT (Gravitas, 2023) decomposes user goals into executable steps, and LangChain (Chase, 2022) and CrewAI (CrewAI, 2024) supply building blocks and orchestration of multi-agent communication. For code execution the authors call AutoGen stateless and CrewAI limited.

*Software-engineering agents.* SWE-Agent (Yang et al., 2024) highlights the importance of a carefully crafted agent-computer interface, meaning specialized tools for particular tasks, and AutoCodeRover (Zhang et al., 2024b) addresses GitHub issues through code search and abstract syntax tree manipulation. Both appear as reference rows on SWE-bench Lite, together with Aider, Moatless Tools and Agentless (Xia et al., 2024).

*Web agents.* WebArena references include Lemur (Xu et al., 2023), a trained 72B model (Patel et al., 2024), AutoWebGLM (Lai et al., 2024) and Auto Eval & Refine (Pan et al., 2024), which pairs Reflexion-style prompting (Shinn et al., 2024) with a reward model; MiniWoB++ references include workflow-guided exploration (Liu et al., 2018) and CC-NET (Humphreys et al., 2022).

The relation to OpenHands is the authors' claim. Their Table 1 compares frameworks on domain, graphical interface, tool library, sandboxed code execution, web browser, multi-agent collaboration, human-AI collaboration, agent hub, evaluation framework and quality control; only the domain column survives, listing AutoCodeRover and SWE-Agent as software engineering and the other frameworks, OpenHands included, as general. Which framework has which feature cannot be reported here.

## 3 Method: the OpenHands platform

**Event stream and agents.** OpenHands keeps a *state* for each session. Its key part is the *event stream*: a chronological record of past actions and observations, including the agent's own actions and the user's instructions and feedback. The state also carries auxiliary data such as the accumulated cost of LLM calls and metadata for delegation. An agent is a function from the event history to an action, and the *runtime* maps each action to an observation; a new agent is written by implementing a step function that receives the state and returns an action.

**Runtime.** Actions execute in a securely isolated Docker container started for each task session. A REST API server inside the container receives actions and returns observations, and a configurable workspace directory holding the user's files is mounted into it. The server maintains a bash shell, a Jupyter IPython server for interactive Python, and a Chromium browser driven through Playwright. Browser observations include the page HTML, the DOM, the accessibility tree (a structured description of page elements), a screenshot and the open tabs. Agents choose among three core action types: run Python, run a bash command, or act in the browser through the browsing language of BrowserGym (Drouin et al., 2024). The authors chose programming-language primitives to give a comprehensive yet flexible set that covers most tasks of human software engineers and analysts, and they state that such an action space is flexible while being reliable and easy to maintain (Wang et al., 2024a).

The runtime can be built on an arbitrary user-provided Docker image: OpenHands installs its client into that image and tags each build with a hash of the build folder (identical hashes mean identical source code and Dockerfile) and with a generic tag for the latest build of that base image. The authors state that this lets agents run on arbitrary operating systems with different software environments.

**Skills.** The authors introduce this layer after citing SWE-Agent's emphasis on carefully crafted interfaces. The AgentSkills library is a Python package whose functions are imported automatically into the IPython environment. It includes file-editing utilities adapted from SWE-Agent and Aider, scrolling functions for viewing other parts of a file, and readers for images, PDFs and other file types. The authors give three reasons: creating, maintaining and distributing tools across agent implementations is a daunting engineering challenge; defining a tool as a Python function lowers the barrier for contributors; and a skill is added only when the model cannot readily write the code itself (for example, replacing certain lines) or when the skill calls an external model.

**Delegation and the agent hub.** An agent can hand a subtask to another agent through a special action type, AgentDelegateAction. The example is the generalist CodeActAgent, with limited web-browsing support, delegating browsing to the specialized BrowsingAgent. AgentHub holds over 10 agents: CodeActAgent, the default generalist based on the CodeAct framework (Wang et al., 2024a); BrowsingAgent, prompted zero-shot; a GPTSwarm agent built on optimizable graphs (Zhuge et al., 2024); and micro agents that reuse a generalist's implementation with specialized prompts, which the authors designed to lower the barrier to agent development.

**Interface and quality control.** A chat-based interface shows the agent's actions and lets the user interrupt it at any moment. Integration tests compare outputs with gold files and answer LLM calls from stored prompt-response pairs, because, the authors state, full evaluations for every code change are prohibitively slow and expensive and mocking addresses non-determinism and cost.

**Safety framing.** The authors expect OpenHands to help mitigate agent risks by enabling systematic evaluation that can find and address risks before wide deployment, by facilitating human-agent interaction instead of unsupervised autonomy, and by giving researchers a suite of agents for safety research. The paper reports no safety evaluation, and the authors note that safe and reliable agents remain a challenge.

## 4 Experimental setup

The evaluation harness integrates 15 benchmarks in three categories (Table 1). Software engineering benchmarks ask an agent to fix or write code, for example SWE-bench (Jimenez et al., 2024), in which the agent edits a real repository to resolve a GitHub issue and a test suite built from the developers' fixes decides the outcome. Web benchmarks ask it to complete tasks on web pages. Assistance benchmarks (GAIA, GPQA, AgentBench, MINT, ProofWriter and Entity Deduction Arena) cover question answering, tool use and reasoning.

**Table 1.** The suite spans seven software, two web and six assistance benchmarks; instance counts are those the authors used.

| Category | Benchmarks (instances used) |
|---|---|
| Software | SWE-bench Lite (300); HumanEvalFix, Python (164); BIRD (300); BioCoder, Python (157); ML-Bench, quarter subset (68); Gorilla APIBench (1775); ToolQA, easy subset (800) |
| Web | WebArena (812); MiniWoB++ (125 environments) |
| Assistance | GAIA, Level-1 validation (53); GPQA, diamond (198); AgentBench, OS subset (144); MINT, math (225) and code (136); ProofWriter (600); Entity Deduction Arena (200) |

The authors compare OpenHands with open-source reproducible reference systems that do not use manual prompt engineering specific to the benchmark, and use SWE-bench Lite as the default subset for cost saving. No result uses SWE-bench hint text. HumanEvalFix (Muennighoff et al., 2024), scored with pass@k (Chen et al., 2021), is run 0-shot (no demonstration in the prompt) with multi-turn self-debugging on test feedback; MiniWoB++ is reported on the full set; MINT allows up to five iterations with two chances to propose solutions. The authors estimate the complete 2294-instance SWE-bench at 6.9k US dollars (USD; a conservative 3 USD per instance) and a Lite run with gpt-4o at around 600 USD. Three adaptations come with stated reasons: BioCoder context prompts were removed to test context retrieval, ProofWriter uses the logical forms supplied by Logic-LM (Pan et al., 2023) to limit the effect of semantic-parsing errors, and the WebArena prompt asks for a concise answer string so that extra text does not fail exact-match checks.

*Reading the scores.* Each benchmark defines its own score: a resolve rate on SWE-bench Lite (the share of instances whose tests pass), a share of bugs fixed on HumanEvalFix, a success rate on most others. An "OpenHands agent" means an agent plus a base model. Reference rows are values listed in the source tables, from systems that differ in base model, prompting and number of demonstrations; the paper does not state that they were re-run under one matched protocol.

## 5 Results

Results bear on RQ2. No score has a reported variance, so "below" and "above" compare single reported numbers.

### 5.1 Software benchmarks

On SWE-bench Lite (Table 2), CodeActAgent v1.8 resolved 26.0% of instances with claude-3-5-sonnet at an average cost of 1.10 USD per instance, 22.0% with gpt-4o at 1.72 USD, and 7.0% with gpt-4o-mini in Table 4 of the source; its Table 3 lists 6.3% for the last case, and this paper reports the full-table value. The listed references are SWE-Agent at 18.0%, AutoCodeRover at 19.0%, Aider at 26.3%, and, in Table 3 alone, Moatless Tools at 26.7% and Agentless at 27.3%. The best OpenHands score sits above the first two references and below the last three. The authors call it a competitive resolve rate against other open-source software-engineering specialists. The closeness of 26.0 and 26.3 cannot be judged without reported variation.

**Table 2.** OpenHands software and web scores lie above some listed references and below others; scores are percentages, reference rows are as listed in the source.

| Benchmark | OpenHands agent, base model | Score | Listed reference rows |
|---|---|---|---|
| SWE-bench Lite | CodeActAgent v1.8, claude-3-5-sonnet | 26.0 | SWE-Agent 18.0; AutoCodeRover 19.0; Aider 26.3; Moatless Tools 26.7; Agentless 27.3 |
| | CodeActAgent v1.8, gpt-4o | 22.0 | |
| | CodeActAgent v1.8, gpt-4o-mini | 7.0 | |
| HumanEvalFix | CodeActAgent v1.5, gpt-4o, 0-shot | 79.3 | SWE-agent 1-shot gpt-4-turbo 87.7; StarCoder2-15B 48.6; DeepSeekCoder-33B-Instruct 47.5 |
| | CodeActAgent v1.5, gpt-3.5-turbo-16k-0613 | 20.1 | |
| WebArena | BrowsingAgent v1.0, claude-3-5-sonnet | 15.5 | Auto Eval & Refine 20.2; AutoWebGLM 18.2; WebArena agent gpt-4-turbo 14.4 |
| | BrowsingAgent v1.0, gpt-4o | 14.8 | |
| MiniWoB++ | BrowsingAgent v1.0, gpt-4o | 40.8 | CC-NET 91.1; workflow-guided exploration 34.6 |

HumanEvalFix asks an agent to fix a bug in a provided function using provided test cases. CodeActAgent v1.5 fixed 79.3% of bugs with gpt-4o and 20.1% with gpt-3.5-turbo-16k-0613, against 16.6% for BLOOMZ-176B, 30.4% for OctoCoder-15B, 47.5% for DeepSeekCoder-33B-Instruct and 48.6% for StarCoder2-15B. SWE-agent reaches 87.7% with gpt-4-turbo, but it received a full demonstration of a successful trajectory for one of the test bugs (1-shot), whereas OpenHands is 0-shot. The authors add that, because the bugs were created by humans and carefully validated, reaching 100% is entirely feasible and a goal for future iterations.

Five further software benchmarks come from a table damaged in extraction, so they are low-confidence and their row alignment is inferred. With gpt-4o, CodeActAgent v1.5 scored 47.3% on BIRD (text-to-SQL, run with BM25), 76.5% on ML-Bench, 27.5% on BioCoder (Python), 36.4% on Gorilla APIBench and 47.2% on ToolQA; under the inferred alignment the finetuned Gorilla row is 75.0%.

Read together, the software rows fit the authors' word "competitive" for the strongest base models and sit below the best listed reference in several rows. They do not isolate whether the OpenHands scaffolding or the base model accounts for the scores, because the paper reports no ablation.

### 5.2 Web benchmarks

WebArena (Zhou et al., 2023a) asks an agent to complete tasks on self-hosted websites (shopping, forums, developer platforms, content management), with execution-based scoring over 812 tasks. BrowsingAgent v1.0 succeeded on 8.5% with gpt-4o-mini, 14.8% with gpt-4o and 15.5% with claude-3-5-sonnet, at average costs of 0.01, 0.15 and 0.10 USD; CodeActAgent v1.8 delegating to it reached 8.3%, 14.5% and 15.3%. Listed references range from 5.3% (Lemur) and 6.2% (WebArena agent, gpt-3.5-turbo) up to 14.4% (WebArena agent, gpt-4-turbo), 18.2% (AutoWebGLM, a trained 7B model) and 20.2% (Auto Eval & Refine, GPT-4 with a reward model and retry). The authors describe BrowsingAgent as competitive among agents that use LLMs with domain-general prompting; the two higher references use training or a reward model, so the comparison class matters.

MiniWoB++ has 125 synthetic minimalist web interfaces. BrowsingAgent reached 27.2% with gpt-3.5-turbo-0125 and 40.8% with gpt-4o, and CodeActAgent delegating to it reached 39.8% with gpt-4o. Workflow-guided exploration scored 34.6%, and CC-NET, listed as a trained specialist (reinforcement learning plus human-annotated data, per the source table), scored 91.1%. OpenHands lies above one trained specialist and far below the other.

### 5.3 Assistance benchmarks

**Table 3.** OpenHands scores on assistance benchmarks lie above some listed references and below others; scores are percentages.

| Benchmark | OpenHands agent, base model | Score | Listed reference rows |
|---|---|---|---|
| GAIA (L1, 53) | GPTSwarm v1.0, gpt-4o | 32.1 | AutoGPT gpt-4-turbo 13.2 |
| GPQA diamond | CodeActAgent v1.8, claude-3-5-sonnet | 52.0 | few-shot CoT gpt-4 38.8; non-expert 21.9; expert 81.3 |
| AgentBench OS | CodeActAgent v1.5, gpt-4o | 57.6 | baseline gpt-4 42.4 |
| | CodeActAgent v1.5, gpt-3.5-turbo-0125 | 11.8 | baseline gpt-3.5-turbo 32.6 |
| MINT math | CodeActAgent v1.5, gpt-4o | 77.3 | gpt-4-0613 65.8 |
| MINT code | CodeActAgent v1.5, gpt-4o | 50.0 | gpt-4-0613 59.6 |
| ProofWriter | CodeActAgent v1.5, gpt-4o | 78.8 | CoT gpt4 68.1; Logic-LM 79.6 |
| Entity Deduction Arena | CodeActAgent v1.5, gpt-4o | 38.0 | gpt-4-0314 40.0 |

GAIA (Mialon et al., 2023) tests general assistance across reasoning, browsing and coding, and on the Level-1 validation set the GPTSwarm agent scored 30.2% with gpt-4-0125-preview and 32.1% with gpt-4o, against 13.2% for AutoGPT with gpt-4-turbo. These rows differ in agent design and base model, so the comparison is between packages. The authors state that the runtime and tools make integrating GAIA, traditionally hard to set up, much simpler; no measurement of integration effort is reported.

GPQA (Rein et al., 2023) poses graduate-level questions. On the diamond set (198 questions) CodeActAgent v1.8 with claude-3-5-sonnet scored 52.0%, at an average cost of 0.065 USD, against 38.8% for few-shot chain-of-thought gpt-4 and 29.6% for gpt-3.5-turbo-16k, 21.9% for non-expert humans and 81.3% for expert humans; the source's Table 7 lists 81.2% for experts. With CodeActAgent v1.5 the diamond, main and extended results are 27.9, 23.4 and 26.1 (gpt-3.5-turbo), 51.8, 47.4 and 42.4 (gpt-4-turbo), and 53.1, 49.3 and 52.8 (gpt-4o).

Table 3 also covers AgentBench OS (Liu et al., 2023), MINT (Wang et al., 2024b), ProofWriter (Tafjord et al., 2021) and Entity Deduction Arena (Zhang et al., 2024a). With gpt-4o, OpenHands is above the listed reference on AgentBench OS (57.6% against 42.4% for the benchmark's gpt-4 baseline) and MINT math (77.3% against 65.8% for gpt-4-0613), and below it on MINT code (50.0% against 59.6%) and Entity Deduction Arena (38.0% against 40.0% for gpt-4-0314). On ProofWriter it scored 78.8% against 68.1% for chain-of-thought gpt4 and 79.6% for Logic-LM (gpt4 with a symbolic solver); this result is a near tie with the symbolic-solver system. With gpt-3.5-class models the scores are 11.8% on AgentBench OS (baseline gpt-3.5-turbo 32.6%), 33.8% on MINT math, 5.2% on MINT code and 24.0% on Entity Deduction Arena.

### 5.4 Patterns across the tables, including negative results

Two patterns cut across the tables. First, scores depend strongly on the base model. Rows with gpt-3.5-class or gpt-4o-mini models are far below gpt-4o rows on the same benchmark: 20.1 against 79.3 on HumanEvalFix, 11.8 against 57.6 on AgentBench OS, 5.2 against 50.0 on MINT code and 7.0 against 22.0 on SWE-bench Lite. Under the inferred alignment, the gpt-3.5-class rows on ToolQA and ML-Bench read 2.3 and 13.2.

Second, several OpenHands rows are below the best listed reference: HumanEvalFix (79.3 against 87.7 for SWE-agent 1-shot), SWE-bench Lite (26.0 against 26.3, 26.7 and 27.3), WebArena (15.5 against 18.2 and 20.2), MiniWoB++ (40.8 against 91.1), MINT code (50.0 against 59.6), Entity Deduction Arena (38.0 against 40.0) and ProofWriter (78.8 against 79.6). On Gorilla APIBench the gpt-4o row (36.4) is below the finetuned Gorilla row (75.0) under the inferred alignment. These compare single reported values with references that differ in model and prompting, so they show where OpenHands rows fall and do not rank systems.

## 6 Discussion

**Answers to the two questions.** The design question is answered by the authors' description of the platform: an event stream, an isolated multi-tool runtime, a shared skills library, delegation and a hub of agents. The evaluation question is answered by the authors' own summary: the same CodeAct agent, without modification of its system prompt, is competitive across software, web and assistance tasks, whereas baseline agents are typically designed and optimized for one category, and OpenHands agents may not achieve top performance in every category. The tables fit that summary: the strongest-model rows are above several references (GPQA diamond 52.0 against 38.8 for few-shot chain-of-thought gpt-4; AgentBench OS 57.6 against 42.4) and below others.

Two cautions apply to this reading. Whether each platform component is needed is not tested, since the paper reports no ablation. And "same agent" holds loosely, because web rows use delegation to BrowsingAgent, GAIA uses the GPTSwarm agent, and versions 1.5 and 1.8 are mixed across rows.

**Later state of the project.** Two repository documentation files (READMEs) describe the project after the paper. The benchmarks repository lists six active benchmarks (SWE-Bench, SWE-Bench Pro, GAIA, Commit0, OpenAgentSafety and ProgramBench), notes a migration from OpenHands V0 to a software development kit (SDK), and offers a remote workspace with one isolated container per instance, for example with 32+ concurrent workers. The Agent Canvas README describes a self-hosted control center that runs OpenHands, Claude Code, Codex, Gemini or any Agent-Client-Protocol-compatible agent on local, remote or cloud backends, powered by the OpenHands Agent Server. This documentation and the community activity reported in the paper are consistent with continued development, but they are not evaluation results, and no user or productivity study is reported.

## 7 Limitations

The authors state that current agents still struggle with complex tasks, that the current agent suffers a lot when editing long files, and that OpenHands workflows still need a great deal of handcrafted work. Multi-modality is supported through predefined agent skills, and the authors want it to be principled through standard IPython and browser integration. In their words, most AI agents today are still research artifacts that cannot reliably perform complex, long-horizon tasks in the real world, and safe and reliable agents remain a challenge. OpenHands agents may not achieve top performance in every category, and the HumanEvalFix comparison with SWE-Agent is not like for like, since SWE-Agent used a 1-shot demonstration and OpenHands is 0-shot. The repository READMEs add that not every benchmarks version is compatible with every Agent SDK version, with a migration to the SDK in progress, and that running the agent server without a sandbox gives the agent full access to the machine's filesystem, with the project marked beta.

Effects on the claims: the first and fifth limits bound the central claim, so competitiveness says nothing about reliability on complex tasks. The sixth and seventh limit how row-by-row comparisons are read. The editing and workflow limits bear on the software-engineering scores and on how far delegation is automated. The safety expectations in Section 3 are hopes, since benchmark scores are not evidence of real-world reliability. Reproducing a result requires matching benchmark and SDK versions, and the isolation described in Section 3 applies only when a sandbox is used.

**Additional caveats.** These are this paper's inferences, not the authors' concessions. No variance, seeds, run counts or confidence intervals are reported, so small differences between rows cannot be told from run-to-run noise. Reference numbers come from systems that differ in model, prompting, shots and tuning budget, so the comparisons are between reported numbers and not controlled contrasts. The paper reports no ablation of the event stream, runtime, skills or delegation, so the scores do not isolate what any component contributes. The available text has extraction damage and discrepancies: lost Table 1 feature marks, inferred row alignment for several software benchmarks, 6.3 against 7.0 for SWE-bench Lite with gpt-4o-mini, and 81.3 against 81.2 for expert humans on GPQA diamond. Community figures are self-reported snapshots, and the READMEs document a later state. Finally, the tables mix agent versions and base-model snapshots, and some rows use delegation or the GPTSwarm agent, so the reading that one unmodified agent ran in every category holds only loosely.

## 8 Conclusion

OpenHands packages what an agent needs to act through software and lets community-built agents be run and compared in one place. On the evidence reported, its default agents are competitive across software, web and assistance benchmarks but below several listed references, and the reported numbers do not isolate what the platform itself contributes. The authors name next steps: principled multi-modality, stronger agents through training and inference-time techniques, better editing of long files, Auto Eval & Refine as an optional browsing component, graph-based workflow generation, and their HumanEvalFix goal.

## References

Works are listed as cited in the OpenHands paper; the cited works were not read for this presentation.

- Chase, H. (2022). LangChain.
- Chen, G., et al. (2024). Autoagents: A framework for automatic agent generation.
- Chen, M., et al. (2021). Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374.
- CrewAI (2024). CrewAI.
- Drouin, A., et al. (2024). Workarena: How capable are web agents at solving common knowledge work tasks? (title as cited by the project).
- Gravitas, S. (2023). Auto-gpt: An autonomous gpt-4 experiment.
- Hong, S., et al. (2023). Metagpt: Meta programming for a multi-agent collaborative framework. The Twelfth International Conference on Learning Representations.
- Humphreys, P. C., et al. (2022). A data-driven approach for learning to control computers. International Conference on Machine Learning, PMLR.
- Jimenez, C. E., et al. (2024). SWE-bench: Can Language Models Resolve Real-world Github Issues? The Twelfth International Conference on Learning Representations.
- Lai, H., et al. (2024). Autowebglm: Bootstrap and reinforce a large language model-based web navigating agent. arXiv preprint arXiv:2404.03648.
- Liu, E. Z., et al. (2018). Reinforcement learning on web interfaces using workflow-guided exploration. International Conference on Learning Representations.
- Liu, X., et al. (2023). Agentbench: Evaluating llms as agents. arXiv preprint arXiv:2308.03688.
- Mialon, G., et al. (2023). GAIA: a benchmark for general AI assistants. CoRR, abs/2311.12983.
- Muennighoff, N., et al. (2024). Octopack: Instruction tuning code large language models.
- Pan, J., et al. (2024). Autonomous evaluation and refinement of digital agents. arXiv preprint arXiv:2404.06474.
- Pan, L., et al. (2023). Logic-lm: Empowering large language models with symbolic solvers for faithful logical reasoning. arXiv preprint arXiv:2305.12295.
- Patel, A., et al. (2024). Large language models can self-improve at web agent tasks. arXiv preprint arXiv:2405.20309.
- Rein, D., et al. (2023). GPQA: A Graduate-Level Google-Proof Q&A Benchmark. arXiv preprint arXiv:2311.12022.
- Shinn, N., et al. (2024). Reflexion: Language agents with verbal reinforcement learning. Advances in Neural Information Processing Systems, 36.
- Tafjord, O., et al. (2021). ProofWriter: Generating implications, proofs, and abductive statements over natural language. Findings of ACL-IJCNLP 2021.
- Wang, X., et al. (2024a). Executable Code Actions Elicit Better LLM Agents. ICML.
- Wang, X., et al. (2024b). MINT: Evaluating LLMs in Multi-turn Interaction with Tools and Language Feedback. ICLR.
- Wu, Q., et al. (2023). Autogen: Enabling next-gen llm applications via multi-agent conversation framework. arXiv preprint arXiv:2308.08155.
- Xia, C. S., et al. (2024). Agentless: Demystifying llm-based software engineering agents. arXiv preprint.
- Xu, Y., et al. (2023). Lemur: Harmonizing natural language and code for language agents. arXiv preprint arXiv:2310.06830.
- Yang, J., et al. (2024). Swe-agent: Agent-computer interfaces enable automated software engineering.
- Zhang, Y., et al. (2024a). Probing the multi-turn planning capabilities of llms via 20 question games.
- Zhang, Y., et al. (2024b). Autocoderover: Autonomous program improvement.
- Zhou, S., et al. (2023a). Webarena: A realistic web environment for building autonomous agents. The Twelfth International Conference on Learning Representations.
- Zhuge, M., et al. (2024). Language agents as optimizable graphs. arXiv preprint arXiv:2402.16823.
