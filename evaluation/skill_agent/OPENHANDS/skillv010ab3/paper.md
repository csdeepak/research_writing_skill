# OpenHands: An Open Platform for AI Software Developers as Generalist Agents

## Abstract

Language-model agents that write code, run shell commands and browse the web are usually built on ad hoc infrastructure, which makes them hard to develop, compare and run safely. OpenHands is an open, community-developed platform released under the MIT license. It provides an abstraction in which an agent maps a history of actions and observations to its next action, a docker-sandboxed runtime with a bash shell, a Python interpreter and a web browser, an extensible tool library, delegation between agents, and an evaluation harness that integrates 15 benchmarks {C027} {C009}. This article presents the project for readers outside the agent-software subfield. Reported single-run success rates include 26.0% on SWE-Bench Lite (resolving real GitHub issues), 79.3% on HumanEvalFix, 15.5% on WebArena and 52.0% on GPQA diamond {C011} {C013} {C014} {C017}. Across the ten benchmarks summarised here, the best OpenHands configuration is below the best listed comparator on eight and above it on two (GAIA and the operating-system subset of AgentBench) {C020}. The authors interpret the results as showing that one general agent design is competitive across software, web and assistance tasks. The tables are consistent with that reading, but they rest on single values without variance estimates and on comparators that differ in model, prompting and training {C021} {L001} {L002}. The paper reports no empirical safety evaluation of the sandbox {L005}.

## 1 Introduction

**The problem.** An agent, in this article, is a program driven by a large language model that observes an environment and chooses actions in it. Agents that act through software (writing and editing code, running shell commands, browsing websites) can affect the world in complex ways, and the OpenHands authors argue that software is therefore an ideal interface for them {C001}. Building such an agent, however, means assembling several parts: an interface through which the agent acts, an environment in which the actions run without harming the user's machine, a mechanism for humans or other agents to interact with it, and benchmarks to measure it; the authors observe that open-source agent frameworks generally include such parts (Hong et al., 2023; Chen et al., 2024; Wu et al., 2023) {C001}. The authors also ask how agents can create and modify code in complex systems, gather information on the fly, and avoid negative side effects on users' systems {C001}.

**What is missing.** As the authors describe the frameworks they compare against, existing options provide general building blocks with basic runtime support, execute commands statelessly, offer only a limited sandboxed code interpreter, or concentrate on one domain, software engineering {C002}. Section 2 gives that account in detail. It is the authors' characterisation; this article did not verify it independently {L008}.

**The questions.** The paper poses two questions that organise this article. RQ1: can one open platform supply the shared abstraction, runtime, tools, delegation and evaluation needed to develop and evaluate agents {C027}? RQ2: is a single generalist agent (one agent design used across task categories) competitive on software, web and general-assistance benchmarks {C021}?

**What was done.** OpenHands offers five components: an event-stream interaction mechanism, a docker-sandboxed runtime, an agent interface for editing software, executing code and browsing, multi-agent delegation, and an evaluation framework {C027}. The authors report a hub of over 10 implemented agents, 15 integrated benchmarks, 32K GitHub stars and more than 2.1K contributions from over 188 contributors, without dating these figures {C008} {C009} {C010}.

**Contributions.** The article reports three things, each tied to evidence in later sections:

1. A description of the platform's design and implementation (Section 3) {C003} {C004} {C006} {C007}.
2. Evaluation results for OpenHands agents on 15 integrated benchmarks, of which ten are summarised here (Sections 4 and 5) {C009} {C011}.
3. A statement of what the results do and do not establish, including the benchmarks on which OpenHands agents trail a listed comparator (Sections 5.5 and 6) {C020} {L001}.

**Paper map.** Section 2 supplies vocabulary and the related-framework account. Section 3 answers RQ1 by describing the system. Sections 4 and 5 set up and report the experiments that bear on RQ2. Section 6 answers both questions, states limitations and lists the authors' next steps. Section 7 notes later repositories documented in the project's README files.

## 2 Background

**Three ideas.** First, an agent in OpenHands is a function from an event history to an action, where the event history (the event stream) is the chronological list of past actions and observations, including user messages {C003}. Second, actions are expressed as code: the design follows CodeAct (Wang et al., 2024a), in which an agent acts by executing Python or bash, so that tools written as code functions are available to the agent {C004}. Third, performance is judged by success rate, the percentage of benchmark instances an agent solves; on SWE-Bench it is called the resolve rate {C011}.

**SWE-Bench in brief.** SWE-Bench (Jimenez et al., 2024) asks an agent to fix real GitHub issues, such as bug reports or feature requests, in a code repository. The modified repository is tested against a test suite that includes new tests added with the human developers' fixes {C011}. Each instance comes with hint text, natural-language suggestions for solving the problem; the OpenHands results below use none. SWE-Bench Lite is a canonical subset, which the authors use by default to save cost {C011}.

**How frameworks differ.** The authors' related-work account organises existing frameworks along two dimensions, runtime strength and domain scope {C002}. On runtime: LangChain provides building blocks with basic runtime support (Chase, 2022); AutoGen executes Python and bash but with stateless command execution (Wu et al., 2023); CrewAI orchestrates multi-agent communication and offers sandboxed but limited code interpreter features (CrewAI, 2024). On scope: SWE-Agent (Yang et al., 2024) and AutoCodeRover (Zhang et al., 2024b) target software engineering, the first through specialised editing tools and the second through code search and abstract syntax tree manipulation {C002}. The authors' Table 1 compares frameworks on ten axes, including a built-in sandbox, a built-in web browser, multi-agent collaboration, human-AI collaboration, an agent hub, an evaluation framework and quality control of the framework itself; the cell entries are not reproduced here because they are not legible in the text available for this article {C002}. This account motivates the platform: OpenHands aims to combine, in one general-purpose system, what these frameworks offer separately {C027}.

## 3 The platform

This section answers RQ1 by describing how OpenHands is built. All statements are descriptions of the authors' implementation, not measurements {C003}.

**3.1 Agents, state and the event stream.** The state is the data structure holding what an agent needs to act: the event stream plus auxiliary information such as the accumulated cost of language-model calls and metadata that tracks delegation between agents {C003}. To implement a new agent, a developer writes a step function that takes the state and returns an action; the authors give a minimal example whose step function builds a message list from the history, calls the model and parses the reply into an action {C003}. The intent is that developers concentrate on agent behaviour, not on how actions execute {C003}.

**3.2 Actions and the runtime.** An agent acts through three primitive actions: running a cell of Python in an interactive interpreter (IPython), running a bash command, and interacting with a web browser through the browsing language introduced by BrowserGym (Drouin et al., 2024) {C004}. The authors chose them to cover most tasks performed by human software engineers and analysts, and note that a programming-language action space is compatible with agents that expect a predefined tool list, because tools can be written as Python functions {C004}.

For each task session OpenHands starts a docker container, a securely isolated Linux environment, the sandbox, in which all actions run. A REST API server inside it (the action execution API) receives actions from the event stream and returns results as observations {C004}. That server maintains a bash shell, a Jupyter IPython server and a Chromium browser controlled through Playwright; browser observations include HTML, the DOM, the accessibility tree, a screenshot and the open tabs {C004}. A configurable workspace directory holding the user's files is mounted into the sandbox {C004}.

The runtime can be built on an arbitrary user-supplied docker image, into which OpenHands installs the action execution API {C005}. Images carry a hash-based tag, derived from the build folder and guaranteeing identical contents, and a generic tag naming the latest build for a base image; a build reuses an image with the same hash, otherwise rebuilds from the latest generic image, otherwise builds from scratch {C005}.

**3.3 AgentSkills.** AgentSkills is a Python package of utility functions that are imported automatically into the IPython environment, so any agent that can run Python can call them {C006}. The authors add a skill only when it is not readily achievable for the language model to write the code directly (for example, replacing certain lines of a file), or when it calls an external model, such as speech-to-text or a code-editing model {C006}. Examples include file-editing functions adapted from SWE-Agent (Yang et al., 2024) and Aider, scrolling functions for viewing files, and readers for images and PDFs {C006}. The stated rationale is that the model already knows widely used libraries, so wrapping them in new tools is unnecessary {C006}.

**3.4 Delegation and the agent hub.** A special action, AgentDelegateAction, lets an agent hand a subtask to another. In the authors' example, the generalist CodeActAgent, whose web-browsing ability is limited, delegates browsing to the specialised BrowsingAgent {C007}. AgentHub collects community-contributed agents: CodeActAgent, the default generalist based on CodeAct; BrowsingAgent, a generalist web agent using only zero-shot prompting, similar to the agent in WebArena (Zhou et al., 2023a) but with improved observations and actions; GPTSwarm, which builds agent systems from optimizable graphs (Zhuge et al., 2024); and micro agents, which reuse a generalist's implementation with specialised prompts {C008}.

**3.5 Interface and quality control.** A graphical interface shows the agent's commands, code and browser activity and lets the user interrupt the agent at any moment to give feedback {C023}. For quality control, the project uses integration tests (Leung & White, 1990): each test gives an agent a task, such as fixing typos in a file, and compares the outcome with a gold file. Because model outputs are non-deterministic and costly, the framework answers model calls from stored prompt-response pairs matched exactly to the prompt, regenerating them with real models after breaking changes {C023}. Tests run on every pull request and main-branch commit, across several platforms and sandbox types {C023}.

## 4 Evaluation setup

RQ2 asks whether a single generalist agent is competitive across categories. The hypothesis implicit in the design goal is that a general action space suffices. A large shortfall relative to open-source comparators on the same benchmark would count against it; this criterion is the article's framing and is not one the authors state {C021}. To test this, the authors integrated 15 benchmarks in three categories and compare OpenHands with open-source reproducible baselines that do not use manual prompt engineering specific to the benchmark's content {C009}. Table 1 lists them; results for ten are reported in Section 5, because the rows for the other five are not reliably legible in the text available for this article.

**Table 1. Fifteen benchmarks in three categories are integrated; the setup notes below shape how the results in Section 5 should be read.**

| Category | Benchmark (instances used) | What it measures | Setup notes |
|---|---|---|---|
| Software | SWE-Bench Lite (300) | fixing real GitHub issues | no hint text; agent edits and runs code; tests include those from human fixes |
| Software | HumanEvalFix (164) | fixing an injected bug in a function | Python subset; pass@k (Chen et al., 2021); self-debugging over turns with test feedback; 0-shot |
| Software | BIRD (300) | text-to-SQL | dev-set samples; multi-turn allowed |
| Software | BioCoder | bioinformatics code generation | original context-carrying prompts removed |
| Software | ML-Bench | machine-learning tasks on repositories | quarter subset |
| Software | Gorilla APIBench | API use | correct API domain |
| Software | ToolQA | external tool use | easy subset |
| Web | WebArena (812) | realistic web tasks | self-hosted; execution-based |
| Web | MiniWoB++ (125) | synthetic web interfaces | full set, including vision-dependent environments |
| Assistance | GAIA (53, Level 1 validation) | tool use, browsing, multi-modality | 466 tasks overall |
| Assistance | GPQA (198, diamond) | graduate-level science questions | other subsets in the original paper's Table 7 |
| Assistance | AgentBench OS (144) | operating-system tasks in bash | multi-turn |
| Assistance | MINT (225 math, 136 code) | multi-turn tool use with feedback | up to five iterations, two chances to propose solutions |
| Assistance | ProofWriter (600) | deductive reasoning | five-hop subset; logical forms from Logic-LM |
| Assistance | Entity Deduction Arena (200) | strategic questioning, state tracking | two datasets of 100, averaged |

*Sources for benchmarks: SWE-Bench (Jimenez et al., 2024), HumanEvalFix (Muennighoff et al., 2024), BIRD (Li et al., 2023b), BioCoder (Tang et al., 2024c), ML-Bench (Tang et al., 2024b), Gorilla APIBench (Patil et al., 2023), ToolQA (Zhuang et al., 2024), WebArena (Zhou et al., 2023a), MiniWoB++ (Liu et al., 2018), GAIA (Mialon et al., 2023), GPQA (Rein et al., 2023), AgentBench (Liu et al., 2023), MINT (Wang et al., 2024b), Entity Deduction Arena (Zhang et al., 2024a), ProofWriter (Tafjord et al., 2021).* {C009}

Three features of the setup matter for interpretation. First, the OpenHands agent, its version and the underlying model differ across benchmarks: CodeActAgent v1.8 is used on SWE-Bench Lite and GPQA (diamond, Table 6), v1.5 on HumanEvalFix, AgentBench, MINT, ProofWriter and Entity Deduction Arena, BrowsingAgent on the web benchmarks (with CodeActAgent v1.8 delegating to it in a second configuration), and GPTSwarm on GAIA {C021}. Second, comparators are listed from other systems; their tuning budgets are not described, and some are trained specialists {L002}. Third, the paper reports one success rate per configuration and does not report seeds or confidence intervals {L001}.

## 5 Results

Each subsection states its question, the numbers with reference points, and what they do not show. Table 2 and Table 3 carry the full comparisons.

**Table 2. OpenHands scores on software and web benchmarks fall inside the range of listed comparators (all values are single reported success rates, %).**

| Benchmark | OpenHands configuration (score) | Listed comparators (score) |
|---|---|---|
| SWE-Bench Lite, 300 | CodeActAgent v1.8: claude-3-5-sonnet 26.0; gpt-4o 22.0; gpt-4o-mini 7.0 | SWE-Agent gpt-4-1106-preview 18.0; AutoCodeRover 19.0; Aider 26.3; Moatless Tools 26.7; Agentless 27.3 |
| HumanEvalFix, 164 | CodeActAgent v1.5, 0-shot: gpt-4o 79.3; gpt-3.5-turbo-16k-0613 20.1 | BLOOMZ-176B 16.6; OctoCoder-15B 30.4; DeepSeekCoder-33B-Instruct 47.5; StarCoder2-15B 48.6; SWE-agent, 1-shot, gpt-4-turbo 87.7 |
| WebArena, 812 | BrowsingAgent v1.0: gpt-4o-mini 8.5; gpt-4o 14.8; claude-3-5-sonnet 15.5. CodeActAgent v1.8 delegating to it: 8.3; 14.5; 15.3 | Lemur 5.3; Patel et al. 9.4; AutoWebGLM 18.2; Auto Eval & Refine 20.2; WebArena agent gpt-3.5-turbo 6.2, gpt-4-turbo 14.4 |
| MiniWoB++, 125 | BrowsingAgent v1.0: gpt-3.5-turbo-0125 27.2; gpt-4o 40.8. CodeActAgent v1.8 delegating: gpt-4o 39.8 | Workflow Guided Exploration 34.6; CC-NET 91.1 (both trained specialist models) |

*Note. Table 3 of the original paper gives 6.3 for the gpt-4o-mini SWE-Bench Lite row; its Table 4 gives 7.0. Moatless Tools used claude-3.5-sonnet and Agentless (Xia et al., 2024) gpt-4o. Comparator systems: Lemur (Xu et al., 2023), Patel et al. (2024), AutoWebGLM (Lai et al., 2024), Auto Eval & Refine (Pan et al., 2024), Workflow Guided Exploration (Liu et al., 2018), CC-NET (Humphreys et al., 2022), StarCoder2 (Lozhkov et al., 2024).* {C011} {C013} {C014} {C015}

**5.1 Software engineering: SWE-Bench Lite.** Question: how does a generalist agent do on real-issue repair against software-engineering specialists? CodeActAgent v1.8 with claude-3-5-sonnet resolved 26.0% of the 300 instances, against 22.0% with gpt-4o and 7.0% with gpt-4o-mini, at average costs per instance of 1.10, 1.72 and 0.01 (USD) {C011}. The 26.0% figure lies 0.3 to 1.3 points below Aider (26.3), Moatless Tools (26.7) and Agentless (27.3), and 7.0 to 8.0 points above SWE-Agent (18.0) and AutoCodeRover (19.0), which places it inside the range of the listed systems {C012}. The authors describe this as competitive with other open-source software-engineering specialists {C012}. What this does not show: whether differences of a few tenths of a point exceed run-to-run variation, which the paper does not report {L001}; or that the comparators were run under the same conditions {L002}. For scale, the authors estimate the complete 2294-instance SWE-Bench set at $6.9k at a conservative $3 per instance, and a SWE-Bench Lite run with gpt-4o at around 600 USD {C011}.

**5.2 Software engineering: HumanEvalFix.** With gpt-4o, CodeActAgent v1.5 fixed 79.3% of the 164 bugs 0-shot, compared with 48.6% for StarCoder2-15B and 47.5% for DeepSeekCoder-33B-Instruct, two non-agentic models, a gap of about 30 points {C013}. It is below the 87.7% of SWE-agent, which received a full demonstration of a successful trajectory on one of the test bugs (1-shot) whereas OpenHands received none {C013}. The authors note that the benchmark's bugs were carefully validated by humans, so that 100% is feasible, and they aim for it in future versions {C013}. The gap to SWE-agent cannot be attributed to the platform, since the shot count differs {L002}.

**5.3 Web browsing.** Question: does the browser action set support competitive web agents, and does delegation from the generalist cost much? On WebArena, BrowsingAgent scored 8.5% (gpt-4o-mini), 14.8% (gpt-4o) and 15.5% (claude-3-5-sonnet-20240620) {C014}. When CodeActAgent v1.8 delegated to it, scores were 8.3%, 14.5% and 15.3%, within 0.3 points of the dedicated agent in each pairing {C014}. Among listed comparators, the WebArena baseline agent with gpt-4-turbo scored 14.4% and trained or refined systems reached 18.2% (AutoWebGLM) and 20.2% (Auto Eval & Refine), above every OpenHands configuration {C014}. The authors call BrowsingAgent competitive among agents using language models with domain-general prompting {C021}. On MiniWoB++ (125 synthetic interfaces, with easier tasks, fewer steps and step-by-step directions), BrowsingAgent scored 27.2% with gpt-3.5-turbo-0125 and 40.8% with gpt-4o, and delegation from CodeActAgent 39.8% {C015}. That is above Workflow Guided Exploration (34.6%) but 50.3 points below CC-NET (91.1%), which was trained with reinforcement learning and human-annotated data (behavioural cloning) {C015}. Neither web benchmark comparison controls for training: several comparators are trained specialists {L002}.

**5.4 General assistance.** Question: do the same tools and runtime carry over to tool use, reasoning and question answering? Table 3 gives the results.

**Table 3. On assistance benchmarks OpenHands is ahead of the listed baseline on four comparisons and behind on three (single reported values, %).**

| Benchmark, instances | OpenHands (score) | Listed baselines (score) |
|---|---|---|
| GAIA Level 1 validation, 53 | GPTSwarm v1.0: gpt-4-0125-preview 30.2; gpt-4o 32.1 | AutoGPT gpt-4-turbo 13.2 |
| GPQA diamond, 198 | CodeActAgent v1.8, claude-3-5-sonnet-20240620: 52.0 | few-shot chain-of-thought gpt-3.5-turbo-16k 29.6; gpt-4 38.8; non-expert humans 21.9; expert humans 81.3 |
| AgentBench OS, 144 | CodeActAgent v1.5: gpt-4o 57.6; gpt-3.5-turbo-0125 11.8 | gpt-4 42.4; gpt-3.5-turbo 32.6 |
| MINT math, 225 | gpt-4o 77.3; gpt-3.5-turbo-16k-0613 33.8 | gpt-4-0613 65.8 |
| MINT code, 136 | gpt-4o 50.0; gpt-3.5-turbo-16k-0613 5.2 | gpt-4-0613 59.6 |
| ProofWriter, 600 | gpt-4o 78.8 | few-shot chain-of-thought gpt4 68.1; Logic-LM gpt4 with symbolic solver 79.6 |
| Entity Deduction Arena, 200 | gpt-4o 38.0; gpt-3.5-turbo-16k 24.0 | zero-shot gpt-4-0314 40.0; gpt-3.5-turbo-0613 27.0 |

*Note. The original paper's Table 7 lists the expert-human GPQA diamond score as 81.2, and CodeActAgent v1.5 with gpt-4o at 53.1 (diamond), 49.3 (main) and 52.8 (extended); the 53.1 is marked in Table 3 of the original paper as reported from v1.5. Baselines: AutoGPT (Gravitas, 2023), GPQA (Rein et al., 2023), AgentBench (Liu et al., 2023), MINT (Wang et al., 2024b), Logic-LM (Pan et al., 2023), Entity Deduction Arena (Zhang et al., 2024a).* {C016} {C017} {C018} {C019}

On GAIA, the GPTSwarm-based agent is above AutoGPT (32.1% and 30.2% against 13.2%) {C016}. On the GPQA diamond set, OpenHands scores 52.0%, above few-shot chain-of-thought GPT-4 (38.8%) and non-expert humans (21.9%), and 29.3 points below expert humans (81.3%), so the agent beats model-only prompting but not experts {C017}. On AgentBench OS, gpt-4o reaches 57.6% against 42.4% for the gpt-4 baseline agent, whereas with gpt-3.5-turbo-0125 the score is 11.8% against 32.6% for the gpt-3.5-turbo baseline, so the ranking depends on the model used {C018}. On MINT, gpt-4o gets 77.3% on math (baseline gpt-4-0613: 65.8%) and 50.0% on code (baseline: 59.6%) {C018}. On ProofWriter, 78.8% is 0.8 points below Logic-LM (79.6%), which pairs gpt4 with a symbolic solver, and 10.7 points above chain-of-thought prompting {C019}. On Entity Deduction Arena, OpenHands scores 38.0% (gpt-4o) against 40.0% for zero-shot gpt-4-0314, and 24.0% (gpt-3.5-turbo-16k) against 27.0% for gpt-3.5-turbo-0613 {C019}. Because the model differs between OpenHands and baseline in several rows (gpt-4o against gpt-4, for example), a lead does not isolate the platform's contribution {L002}.

**5.5 Where OpenHands does not lead.** In the tables, the best OpenHands configuration is below the best listed comparator on eight of the ten benchmarks summarised here: SWE-Bench Lite, HumanEvalFix, WebArena, MiniWoB++, MINT code, ProofWriter, Entity Deduction Arena, and GPQA if expert humans count. It is above the best listed comparator on GAIA and AgentBench OS, and on the math subset of MINT, whose code subset counts among the eight {C020}. With the weaker gpt-3.5-turbo family, OpenHands is below the same-family baseline on AgentBench OS and Entity Deduction Arena {C020}. The authors themselves write that OpenHands agents may not achieve top performance in every category {C021}. These are negative results for RQ2 as they bear on the strongest reading of the hypothesis.

## 6 Discussion

**Answers to the questions.** RQ1, whether one open platform can supply the abstraction, runtime, tools, delegation and evaluation, is answered by the description in Section 3: each of the authors' five components is implemented and documented, and the platform hosts 15 benchmarks {C027} {C009}. This is an answer by construction, not by measurement; no test of the sandbox's protection against side effects is reported {L005}. RQ2, whether a single generalist agent is competitive across categories, is answered by the authors affirmatively: the same CodeAct agent, without changes to its system prompt, is competitive across software development, web interaction and miscellaneous tasks {C021}. The tables are consistent with that reading. Scores fall within the range of listed comparators on SWE-Bench Lite and WebArena, exceed the listed baseline on GAIA, AgentBench OS and MINT math, and trail the best listed comparator on HumanEvalFix, MiniWoB++, ProofWriter and MINT code {C020} {C021}.

**What the results do not establish.** The tables do not show that the platform's design caused any score, since no ablation isolates a component. They do not show that differences of a point or two are real. Across benchmarks the agent, version and model differ (Section 4), so the phrase "the same CodeAct agent" describes a design family rather than a single fixed artifact {L001} {L002}.

**Limitations.** Each limitation below is linked to the claims it bounds, ordered by impact on the main claim.

- *Single values without spread.* Every success rate is one reported number with no seeds or confidence intervals. This bounds every comparison in Section 5, especially SWE-Bench Lite, where the gaps to Aider, Moatless Tools and Agentless are 0.3 to 1.3 points. A repeated-run study would resolve it {L001}.
- *Uncontrolled comparisons.* Comparators use different models, shots (SWE-agent 1-shot against OpenHands 0-shot on HumanEvalFix), training (trained web specialists) and unreported tuning budgets. A gap in either direction cannot be attributed to the platform. Matched-model, matched-budget comparisons would resolve it {L002}.
- *Weak absolute performance on hard tasks.* The authors state that current agents struggle with complex tasks and suffer a lot when editing long files; the best SWE-Bench Lite score here is 26.0% {L003}.
- *No safety evaluation.* The sandbox and human-in-the-loop design are presented as risk mitigation, but the paper reports no empirical safety measurement; the claim is a design intent {L005}.
- *Handcrafted workflow.* The authors state that OpenHands's workflow still requires substantial handcrafted work {L004}.
- *Internal discrepancies.* The gpt-4o-mini SWE-Bench Lite score is 6.3 in one table of the original paper and 7.0 in another, and the expert-human GPQA score is 81.3 and 81.2; both pairs differ by less than one point and both values are reported above {L006}.

**Implications and next steps.** The authors envision OpenHands as a catalyst for research and applications, and their conclusion states that it accelerates research innovations {C022}. The only supporting evidence in the paper is the adoption statistics, which are undated {L009}, so this remains an expectation and not a finding {C022}. Their ethics statement argues that the platform can mitigate risks by enabling systematic evaluation, facilitating human-agent interaction instead of unsupervised autonomy, and giving researchers access to agents for safety research {C025}. Listed next steps are principled multi-modality, integrating Auto Eval & Refine (a retry-on-error strategy using Reflexion prompts (Shinn et al., 2024) and task-completion reward models) into the browsing agent, stronger agents through training and inference-time techniques, better long-file editing, and graph-based automatic workflow generation {C024}.

## 7 Later repositories

The project's README files, which describe a later state than the paper, are documentation and not measurement {L007}. One describes a benchmarks repository that lists SWE-Bench, SWE-Bench Pro, GAIA, Commit0, OpenAgentSafety and ProgramBench as active, is migrating benchmarks from the earlier codebase to a newer Agent SDK, and supports local docker workspaces and a remote workspace with pre-built images for parallel runs (the README gives 32+ concurrent workers as an example) {C026}. The other describes Agent Canvas, a self-hosted control center whose frontend connects to one or more Agent Servers, each a REST API for running multiple agents, and can also run third-party agents through the Agent-Client Protocol {C026}. They add no results to this article.

## 8 Conclusion

OpenHands packages an event-stream agent abstraction, a docker runtime with bash, Python and browser, a skill library, delegation and a 15-benchmark harness in one open platform {C027}. On the ten benchmarks summarised here, the best OpenHands configuration is above the best listed comparator on GAIA and AgentBench OS and below it on eight benchmarks, counting MINT through its code subset and GPQA against expert humans {C020}. The authors read this as competitiveness of one general design across categories; the evidence is consistent with that reading and limited by single values, heterogeneous comparators and the absence of a safety evaluation {C021} {L001} {L002} {L005}. Open questions are whether the differences survive repeated runs and matched baselines, and whether the design's protections hold in practice {L001} {L005}.

## References

Chase, H. (2022). LangChain. Software repository.
Chen, G., et al. (2024). AutoAgents: A framework for automatic agent generation.
Chen, M., et al. (2021). Evaluating large language models trained on code. arXiv:2107.03374.
CrewAI. (2024). CrewAI. Software repository.
Drouin, A., et al. (2024). WorkArena: How capable are web agents at solving common knowledge work tasks?
Gravitas, S. (2023). Auto-GPT: An autonomous GPT-4 experiment. Software repository.
Hong, S., et al. (2023). MetaGPT: Meta programming for a multi-agent collaborative framework. ICLR 2024.
Humphreys, P. C., et al. (2022). A data-driven approach for learning to control computers. ICML 2022.
Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? ICLR 2024.
Lai, H., et al. (2024). AutoWebGLM: Bootstrap and reinforce a large language model-based web navigating agent. arXiv:2404.03648.
Leung, H. K. N., & White, L. J. (1990). A study of integration testing and software regression at the integration level. ICSM 1990.
Li, J., et al. (2023b). Can LLM already serve as a database interface? A big bench for large-scale database grounded text-to-SQLs. NeurIPS 2023 Datasets and Benchmarks Track.
Liu, E. Z., et al. (2018). Reinforcement learning on web interfaces using workflow-guided exploration. ICLR 2018.
Liu, X., et al. (2023). AgentBench: Evaluating LLMs as agents. arXiv:2308.03688.
Lozhkov, A., et al. (2024). StarCoder 2 and The Stack v2: The next generation.
Mialon, G., et al. (2023). GAIA: A benchmark for general AI assistants. CoRR abs/2311.12983.
Muennighoff, N., et al. (2024). OctoPack: Instruction tuning code large language models.
Pan, J., et al. (2024). Autonomous evaluation and refinement of digital agents. arXiv:2404.06474.
Pan, L., et al. (2023). Logic-LM: Empowering large language models with symbolic solvers for faithful logical reasoning. arXiv:2305.12295.
Patel, A., et al. (2024). Large language models can self-improve at web agent tasks. arXiv:2405.20309.
Patil, S. G., et al. (2023). Gorilla: Large language model connected with massive APIs. arXiv:2305.15334.
Rein, D., et al. (2023). GPQA: A graduate-level Google-proof Q&A benchmark. arXiv:2311.12022.
Shinn, N., et al. (2024). Reflexion: Language agents with verbal reinforcement learning. NeurIPS 2023.
Tafjord, O., et al. (2021). ProofWriter: Generating implications, proofs, and abductive statements over natural language. Findings of ACL-IJCNLP 2021.
Tang, X., et al. (2024b). ML-Bench: Evaluating large language models and agents for machine learning tasks on repository-level code. arXiv:2311.09835.
Tang, X., et al. (2024c). BioCoder: A benchmark for bioinformatics code generation with large language models. Bioinformatics 40(Supplement_1).
Wang, X., et al. (2024a). Executable code actions elicit better LLM agents. ICML 2024.
Wang, X., et al. (2024b). MINT: Evaluating LLMs in multi-turn interaction with tools and language feedback. ICLR 2024.
Wu, Q., et al. (2023). AutoGen: Enabling next-gen LLM applications via multi-agent conversation framework. arXiv:2308.08155.
Xia, C. S., et al. (2024). Agentless: Demystifying LLM-based software engineering agents.
Xu, Y., et al. (2023). Lemur: Harmonizing natural language and code for language agents. arXiv:2310.06830.
Yang, J., et al. (2024). SWE-agent: Agent-computer interfaces enable automated software engineering.
Zhang, Y., et al. (2024a). Probing the multi-turn planning capabilities of LLMs via 20 question games.
Zhang, Y., et al. (2024b). AutoCodeRover: Autonomous program improvement.
Zhou, S., et al. (2023a). WebArena: A realistic web environment for building autonomous agents. ICLR 2024.
Zhuang, Y., et al. (2024). ToolQA: A dataset for LLM question answering with external tools. NeurIPS 2023.
Zhuge, M., et al. (2024). Language agents as optimizable graphs. arXiv:2402.16823.
