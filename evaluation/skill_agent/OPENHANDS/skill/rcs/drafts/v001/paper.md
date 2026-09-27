# OpenHands: An Open Platform for Building and Evaluating Generalist AI Software Agents

**Wang et al., 2024 — Published at ICLR 2025**

---

## Abstract

Developing AI agents that can autonomously solve real-world tasks requires shared infrastructure for safe execution, extensible tools, and systematic evaluation — yet the current ecosystem is fragmented across incompatible, single-purpose frameworks. We present OpenHands (formerly OpenDevin), a community-driven open platform in which agents interact with computing environments through the same interfaces a human developer uses: writing and executing code, running shell commands, and browsing the web. The platform provides an event-stream architecture that decouples agent logic from environment details, a Docker-sandboxed runtime for safe code execution, an extensible skill library, multi-agent delegation, and a unified evaluation framework spanning 15 established benchmarks across software engineering, web interaction, and general assistance tasks. We evaluate agents on these benchmarks and show that a single generalist agent — CodeActAgent, using code as its primary action modality — achieves competitive performance across all three task categories without task-specific modification: 26.0% on SWE-Bench Lite (comparable to open-source software engineering specialists), 15.5% on WebArena (competitive with domain-general web agents), and 52.0% on the GPQA graduate-level question-answering benchmark (surpassing GPT-4 few-shot chain-of-thought at 38.8%). Released under the MIT license with over 188 contributors, OpenHands provides an open foundation for advancing generalist agent research. {C001}

---

## 1. Introduction

Large language models (LLMs) have enabled a new class of AI systems called *agents*: programs that perceive their environment, plan, and take actions to complete multi-step tasks (Jimenez et al., 2024; Zhou et al., 2023a; Wang et al., 2024b). Unlike a standard LLM that produces a single text response, an agent operates in a loop — taking an action, observing the result, and deciding what to do next. Recent work has applied agents to tasks that once required significant human effort: resolving GitHub bug reports, navigating commercial websites, answering graduate-level scientific questions by searching the web, and writing executable code for machine learning pipelines.

The most powerful way humans currently interact with the world is through software. A skilled programmer can, with a few lines of code, automate repetitive processes, orchestrate complex workflows, and interface with virtually any digital service. This observation motivates using software itself — code execution, command-line tools, and web browsers — as the primary action space for AI agents. Software-based actions are expressive enough to represent any tool use and reliable enough to execute deterministically, making them well-suited as a universal interface for agents. {C007}

Despite rapid progress in LLM capabilities, the infrastructure for building and evaluating software-acting agents is immature. Existing frameworks address pieces of the problem: some provide multi-agent communication (Wu et al., 2023; Hong et al., 2023), some target software engineering specifically (Yang et al., 2024), and some focus on web browsing (Zhou et al., 2023a). None combines safe sandboxed code execution, modular extensibility, multi-agent delegation, and systematic evaluation across a broad set of benchmarks. This fragmentation makes it difficult to compare approaches, measure genuine progress, or reuse components across projects.

We introduce **OpenHands** (formerly OpenDevin), a community-driven open platform designed to address these infrastructure gaps. OpenHands provides: {C001}

1. An **event-stream architecture** that records all agent actions and environment observations, allowing agents to be implemented as simple step functions that map history to the next action.
2. A **Docker-sandboxed runtime** with a bash shell, Jupyter IPython server, and Playwright-powered web browser, enabling safe execution of agent-generated code on arbitrary operating system images.
3. An **AgentSkills library** of extensible Python utilities that agents can call when direct code generation is insufficient.
4. **Multi-agent delegation**, allowing a generalist agent to hand off subtasks to specialists.
5. An **evaluation framework** integrating 15 benchmarks that span software engineering, web browsing, and miscellaneous assistance tasks.

The platform includes a hub of over 10 implemented agents. We focus evaluation on CodeActAgent — a generalist agent that acts primarily by executing code and shell commands — and demonstrate that it achieves competitive results across all three task categories without task-specific modification. {C005}

**Contributions.** (1) We describe the OpenHands platform and its architecture. (2) We present CodeActAgent, a generalist agent that uses executable code as its primary action modality. (3) We evaluate agents across 15 benchmarks and show that one generalist agent achieves competitive performance in software engineering, web interaction, and general assistance — domains that specialist baselines address individually.

---

## 2. Background: Agents, Environments, and Action Spaces

An AI agent is a system that observes its environment, selects an action, and updates its state based on the result. This loop is familiar from reinforcement learning, where an agent in a Markov decision process learns a policy mapping states to actions. LLM-based agents follow the same pattern, but the policy is a language model that generates text describing the next action, which a runtime then executes. The agent's "state" is typically its history of prior actions and observations — the conversation so far. {C007}

The choice of **action space** strongly shapes what an agent can do. Early LLM agents used structured API calls (fixed function signatures) as actions, which limits agents to predefined tools. The CodeAct approach (Wang et al., 2024a), which underpins OpenHands's primary agent, instead treats *executable code* as the action: the agent writes Python scripts or shell commands that the runtime executes, returning the output as the next observation. This design is powerful because code is Turing-complete — any tool, computation, or workflow expressible in software becomes available to the agent without pre-specification.

For web browsing, agents need a different kind of action: clicking, typing, and navigating in a browser. OpenHands integrates the BrowserGym action space (Drouin et al., 2024), which provides a domain-specific language for browser interaction.

Several existing frameworks create agent infrastructure. AutoGPT (Gravitas, 2023) and LangChain (Chase, 2022) offer general-purpose components but lack integrated sandboxed execution. MetaGPT (Hong et al., 2023) and AutoGen (Wu et al., 2023) focus on multi-agent communication. SWE-Agent (Yang et al., 2024) provides a carefully engineered agent-computer interface for GitHub issue resolution but is domain-specific. OpenHands aims to unify these concerns in a single extensible platform.

---

## 3. The OpenHands Platform

### 3.1 Agent Abstraction and the Event Stream

The core abstraction in OpenHands is simple: an agent is a function that takes the current **state** — a data structure containing the full history of actions and observations — and returns the next action. The state is organized around an **event stream**, a chronological list of all past action-observation pairs, including messages from the user. This design separates agent logic cleanly from execution details: an agent implementor only needs to write the `step` function; everything else (running the action, capturing the result, updating the stream) is handled by the platform. {C007}

Actions are a typed set of primitives. `IPythonRunCellAction` executes Python code in a persistent Jupyter kernel. `CmdRunAction` runs a bash command. `BrowseInteractiveAction` sends browser commands. `MessageAction` lets the agent communicate with the user. `AgentDelegateAction` dispatches a subtask to another agent. Observations capture execution results: standard output, browser state (including HTML, DOM, and an accessibility tree), and user messages.

This architecture is also compatible with tool-calling agents that use JSON-formatted function calls: tool wrappers can be expressed as Python functions within the IPython environment, so agents that expect a function-calling API can operate within OpenHands with minimal adaptation.

### 3.2 Sandboxed Runtime

Every task session runs inside an isolated Docker container. The container exposes a REST API — the OpenHands action execution API — that the backend uses to send actions and receive observations. Inside the container, three components handle action execution: a persistent bash shell, a Jupyter IPython server, and a Playwright-backed Chromium browser. {C002}

A key feature is support for *arbitrary Docker images*: users can supply any base image (e.g., a pre-configured Python environment for a specific ML library), and OpenHands automatically installs its action execution API into that image. This makes it possible to evaluate agents in the exact software environment required by a task, without manual setup.

Image management uses a dual-tagging scheme. A hash-based tag encodes the MD5 of the build context, guaranteeing that identical hashes mean identical images. A human-readable tag records the OpenHands version and base image. This combination supports both reproducibility (share the hash, get the same environment) and convenience (pull the latest version of a configuration). {C002}

### 3.3 AgentSkills: An Extensible Tool Library

While code execution provides a powerful foundation, some operations are awkward to implement from scratch in a single LLM-generated snippet: for example, viewing a specific line of a large file, or extracting text from an image using a vision-language model. OpenHands addresses this with the **AgentSkills** library, a Python package of utility functions that are automatically imported into the agent's IPython session.

The addition criterion is deliberate: a new skill is added only when (1) LLMs reliably fail to generate the equivalent code directly, or (2) the operation requires calling an external model. Current skills include file editing primitives adapted from SWE-Agent (Yang et al., 2024) and Aider (`edit_file`, `scroll_up`, `scroll_down`), and multi-modal parsing utilities (`parse_pdf`, `parse_image` using a vision-language model, `parse_audio` using a speech-to-text model). This design avoids wrapping well-known libraries unnecessarily while providing access to capabilities beyond a single LLM call.

### 3.4 Multi-Agent Delegation

OpenHands supports heterogeneous multi-agent systems through `AgentDelegateAction`. When a generalist agent encounters a subtask requiring specialized expertise — for example, extended web navigation — it can delegate that subtask to a specialist agent with appropriate tools and prompting. The specialist runs to completion and returns its result as an observation to the calling agent. This pattern allows composing specialized capabilities without requiring a single monolithic agent to handle all tasks equally well. {C008}

---

## 4. The Agent Hub

OpenHands ships with a hub of more than 10 implemented agents. The three most relevant for evaluation are:

**CodeActAgent** is the default generalist agent, built on the CodeAct framework (Wang et al., 2024a). At each step, it may converse with the user, execute Python code, run bash commands, or browse the web. No task-specific prompt modification is made across evaluations. This is the agent reported in most results below.

**BrowsingAgent** is a generalist web agent using zero-shot prompting, designed as a baseline for web-interaction benchmarks. It uses the full BrowserGym action set (Drouin et al., 2024) and produces accessibility-tree-based observations.

**GPTSwarm** (Zhuge et al., 2024) implements an optimizable multi-agent graph, where nodes represent operations and edges represent communication pathways. It is evaluated on the GAIA benchmark.

The platform also supports **Micro Agents**: lightweight wrappers that extend a generalist agent with a specialized system prompt, lowering the barrier for community members to contribute task-specific behavior without implementing a full agent from scratch.

---

## 5. Evaluation Framework and Setup

To assess agent generality, OpenHands integrates **15 benchmarks** across three categories {C009}:

- **Software engineering**: SWE-Bench (Jimenez et al., 2024), HumanEvalFix (Muennighoff et al., 2024), BIRD (Li et al., 2023b), BioCoder (Tang et al., 2024c), ML-Bench (Tang et al., 2024b), Gorilla APIBench (Patil et al., 2023), ToolQA (Zhuang et al., 2024)
- **Web browsing**: WebArena (Zhou et al., 2023a), MiniWoB++ (Liu et al., 2018)
- **Miscellaneous assistance**: GAIA (Mialon et al., 2023), GPQA (Rein et al., 2023), AgentBench (Liu et al., 2023), MINT (Wang et al., 2024b), Entity Deduction Arena (Zhang et al., 2024a), ProofWriter (Tafjord et al., 2021)

All OpenHands evaluations compare against open-source baselines that do not perform manual prompt engineering targeted at specific benchmarks. Each OpenHands agent is evaluated in zero-shot mode (no task demonstrations) unless otherwise stated. Evaluations are performed without hint text on SWE-Bench.

For brevity and cost management, the default SWE-Bench configuration uses the 300-instance Lite subset; running the full 2,294-instance benchmark costs approximately $6,900 with gpt-4o.

---

## 6. Results

### 6.1 Software Engineering

**SWE-Bench Lite** evaluates agents on real GitHub issue resolution: given a repository and an issue description (e.g., a bug report), the agent must modify the code so that the repository's test suite passes. The *resolve rate* is the fraction of issues for which the modified code passes all tests. Table 1 summarizes results for the main software engineering baselines.

**Table 1: SWE-Bench Lite and HumanEvalFix results (selected)**

| Agent | Model | SWE-Bench Lite (%) | HumanEvalFix Python (%) |
|---|---|---|---|
| SWE-Agent (Yang et al., 2024) | gpt-4-1106-preview | 18.0 | 87.7 (1-shot) |
| AutoCodeRover (Zhang et al., 2024b) | gpt-4-0125-preview | 19.0 | — |
| Aider (Gauthier) | gpt-4o + claude-3-opus | 26.3 | — |
| Agentless (Xia et al., 2024) | gpt-4o | 27.3 | — |
| StarCoder2-15B (non-agentic) | — | — | 48.6 |
| **OH CodeActAgent v1.8** | gpt-4o-mini | 6.3 | — |
| **OH CodeActAgent v1.8** | gpt-4o | 22.0 | — |
| **OH CodeActAgent v1.8** | claude-3-5-sonnet | **26.0** | — |
| **OH CodeActAgent v1.5** (0-shot) | gpt-4o | — | **79.3** |

CodeActAgent v1.8 with claude-3-5-sonnet achieves 26.0% on SWE-Bench Lite, comparable to Aider (26.3%) and Moatless Tools (26.7%), and above SWE-Agent (18.0%) and AutoCodeRover (19.0%). {C003} The gap between the smallest model (gpt-4o-mini, 6.3%) and the largest (claude-3-5-sonnet, 26.0%) spans 4× — a reminder that the same platform infrastructure can produce very different results depending on the underlying LLM.

On HumanEvalFix — a benchmark where agents must fix a function so that previously-failing tests pass — CodeActAgent achieves 79.3% in zero-shot mode, nearly doubling non-agentic StarCoder2-15B (48.6%). {C004} SWE-Agent reaches 87.7%, but does so with a one-shot demonstration (a full successful trajectory for a sample problem), whereas the OpenHands result is zero-shot. The authors note that perfect performance (100%) is feasible given that HumanEvalFix bugs were carefully crafted by humans, and they aim for this in future work.

Additional software benchmarks tell a consistent story. On ML-Bench — evaluating agents' ability to run machine learning code across 18 GitHub repositories — CodeActAgent (gpt-4o) reaches 64.4%, outperforming SWE-Agent (42.6%) and Aider (76.5% is reported only for gpt-4o in the full table). On Gorilla APIBench (API selection from natural language descriptions), the agent achieves 47.2% (gpt-4o), compared to 36.4% for the Gorilla fine-tuned baseline. On BIRD (text-to-SQL with multi-turn SQL execution feedback), it achieves 47.3% on 300 development instances.

### 6.2 Web Browsing

**WebArena** (Zhou et al., 2023a) is a self-hosted benchmark with 812 human-curated task instructions across realistic web environments (shopping sites, forums, developer platforms, content management systems). Agents must freely navigate sites to complete tasks; correctness is evaluated by execution. A *success rate* measures the fraction of completed tasks.

**Table 2: WebArena and MiniWoB++ results (selected)**

| Agent | Model | WebArena (%) | MiniWoB++ (%) |
|---|---|---|---|
| Lemur (Xu et al., 2023) | 70B chat model | 5.3 | — |
| AutoWebGLM (Lai et al., 2024) | Trained 7B | 18.2 | — |
| Auto Eval & Refine (Pan et al., 2024) | GPT-4 + Reflexion | 20.2 | — |
| WebArena Agent (Zhou et al., 2023a) | gpt-4-turbo | 14.4 | — |
| Workflow Guided Exploration (Liu et al., 2018) | Trained specialist | — | 34.6 |
| CC-NET (Humphreys et al., 2022) | RL + human annotation | — | 91.1 |
| **OH BrowsingAgent v1.0** | gpt-4o-mini | 8.5 | 27.2 |
| **OH BrowsingAgent v1.0** | gpt-4o | 14.8 | **40.8** |
| **OH BrowsingAgent v1.0** | claude-3-5-sonnet | **15.5** | — |

BrowsingAgent with claude-3-5-sonnet reaches 15.5% on WebArena, competitive with the WebArena baseline agent (14.4%) and within the range of domain-general LLM-based agents (Lemur: 5.3%; AutoWebGLM: 18.2%). {C005} It does not reach the performance of trained specialist models with reinforcement learning or human annotation, which is expected given the zero-shot setup.

On MiniWoB++, a synthetic benchmark with 125 web interfaces, BrowsingAgent (gpt-4o) reaches 40.8%. Specialist trained models reach 91.1% (CC-NET), but these require reinforcement learning with human-annotated demonstrations — a substantially different training regime. Results are reported on the full 125-environment set, unlike some prior work that excludes vision-dependent tasks.

### 6.3 Miscellaneous Assistance

**GPQA** (Rein et al., 2023) presents graduate-level, Google-proof questions in biology, chemistry, and physics — questions designed so that non-expert internet search does not trivially yield the answer. Agents with access to Python and web search can perform precise calculations and retrieve specialized information beyond their parametric knowledge.

**Table 3: GPQA Diamond Set and GAIA L1 results (selected)**

| Agent | Model | GPQA Diamond (%) | GAIA L1 (%) |
|---|---|---|---|
| Few-shot CoT (Rein et al., 2023) | gpt-3.5-turbo-16k | 29.6 | — |
| Few-shot CoT (Rein et al., 2023) | gpt-4 | 38.8 | — |
| Non-expert human | — | 21.9 | — |
| Expert human | — | 81.3 | — |
| AutoGPT (Gravitas, 2023) | gpt-4-turbo | — | 13.2 |
| **OH CodeActAgent v1.8** | claude-3-5-sonnet | **52.0** | — |
| **OH GPTSwarm v1.0** | gpt-4o | — | **32.1** |

CodeActAgent with tool use achieves 52.0% on the GPQA diamond set, surpassing GPT-4 few-shot chain-of-thought (38.8%) and exceeding the non-expert human baseline (21.9%). {C006} This result illustrates a key value of agentic tool use: the agent can run Python for precise calculations and use web search to retrieve specialized information that GPT-4 cannot recall. Expert human performance (81.3%) remains substantially higher, establishing a clear ceiling.

On GAIA Level 1, GPTSwarm achieves 32.1% (gpt-4o) compared to AutoGPT's 13.2%, demonstrating the benefit of structured multi-agent coordination for general-purpose tasks requiring reasoning, browsing, and coding.

Additional benchmarks round out the picture: AgentBench OS subset (57.6% vs. baseline 42.4%), MINT math (77.3% vs. baseline 65.8%), and ProofWriter (78.8% vs. Logic-LM's 79.6%). On Entity Deduction Arena — a multi-turn "20 questions" game — CodeActAgent reaches 38.0%, slightly below GPT-4's zero-shot 40.0%.

---

## 7. Discussion

**A generalist agent can be competitive across task categories.** The central finding is that CodeActAgent, without any change to its system prompt or architecture, achieves competitive results in software engineering, web browsing, and general assistance. {C005} Specialist baselines in each category are often fine-tuned or engineered specifically for that task; a zero-shot generalist reaching comparable performance is notable. This suggests that the expressive power of code-based actions — which can implement any tool use — is a significant factor in agent generality.

**Tool use amplifies LLM capability on knowledge-intensive tasks.** The GPQA result makes this concrete: GPT-4 few-shot chain-of-thought achieves 38.8%, but the same underlying model equipped with Python execution and web search reaches 52.0% when used as the backbone of CodeActAgent. {C006} The gap closes substantially relative to expert humans (81.3%), though it does not close entirely. For ML researchers working on reasoning or knowledge-intensive tasks, this result suggests that evaluations that do not include tool use may underestimate the practical potential of LLM-based systems.

**Infrastructure enables research.** The comparison across models within the same framework is informative: on SWE-Bench Lite, gpt-4o-mini achieves 6.3% while claude-3-5-sonnet achieves 26.0% — a 4× range — within identical infrastructure. This isolates LLM capability as the variable, something that cross-framework comparisons cannot cleanly do. The platform's integration testing framework, which mocks LLM calls for deterministic behavior, provides regression detection as the codebase evolves.

**Limitations.** The evaluation results are reported without variance estimates across random seeds or LLM sampling — a limitation the paper acknowledges implicitly (no confidence intervals are reported) and which affects how much weight to place on small performance gaps. {C010} Current agents struggle when editing long files, as the context window constrains how much of a file the agent can view and modify simultaneously. Workflow design — deciding which agents to invoke in what sequence — remains largely manual, though graph-based frameworks like GPTSwarm offer promising directions toward automation. Evaluation is performed at the benchmark level; transfer to production software systems or private codebases is not tested.

---

## 8. Related Work

**General-purpose agent frameworks.** AutoGPT (Gravitas, 2023) and LangChain (Chase, 2022) provide foundational components for LLM-based agents but lack integrated sandboxed execution. MetaGPT (Hong et al., 2023) introduces standardized operating procedures for multi-agent software development teams. AutoGen (Wu et al., 2023) provides a conversation framework enabling Python and bash execution, though with stateless command execution that cannot maintain session state across turns.

**Software engineering agents.** SWE-Agent (Yang et al., 2024) integrates a custom agent-computer interface for GitHub issue resolution and serves as both an inspiration and a direct baseline for OpenHands's software engineering evaluation. AutoCodeRover (Zhang et al., 2024b) uses code search and abstract syntax tree manipulation. Agentless (Xia et al., 2024) takes a simpler, non-agent approach to the same task. OpenHands reproduces and extends these baselines within a unified framework.

**Web browsing agents.** AutoWebGLM (Lai et al., 2024) trains a specialized 7B model for web navigation. Auto Eval & Refine (Pan et al., 2024) applies Reflexion-style retry with GPT-4V as a reward model. BrowserGym (Drouin et al., 2024) provides the action primitives that OpenHands's BrowsingAgent builds on. OpenHands's contribution is making these capabilities available within the same event-stream framework as code execution.

**Multi-agent systems.** GPTSwarm (Zhuge et al., 2024) represents agent systems as optimizable graphs. CAMEL and related systems explore role-playing communication between agents. OpenHands's multi-agent delegation mechanism is simpler — a calling/callee pattern rather than peer communication — but integrates with the general event-stream architecture.

---

## 9. Conclusion

OpenHands is an open platform for developing and evaluating AI agents that interact with computing environments through software. Its event-stream architecture, Docker-sandboxed runtime, extensible skill library, and multi-benchmark evaluation framework address key infrastructure gaps in the agent research ecosystem. The platform demonstrates that a single generalist agent, using code as its primary action modality, can achieve competitive performance across software engineering, web browsing, and general-assistance tasks without task-specific modification. {C005}{C001}

These results carry two implications for the broader ML community. First, software-grounded action spaces provide a surprisingly powerful and general interface for LLM-based agents; researchers building agents for new domains should consider whether code-based actions cover their use case before designing specialized action spaces. Second, shared open infrastructure — including sandboxed execution and multi-benchmark evaluation — is a precondition for measuring and advancing agent generality; single-benchmark results may miss the breadth of capability that matters for deployment.

OpenHands is released under the MIT license, with 32K GitHub stars and over 188 contributors as of publication. Active open challenges include handling long files, automating workflow generation, and building stronger agents through training-time techniques. {C010} {E034}

---

## References

- Drouin et al., 2024. WorkArena: How capable are web agents at solving common knowledge work tasks? Preprint.
- Gauthier. Aider: How aider scored SOTA 26.3% on SWE-bench Lite. Blog post.
- Gravitas, 2023. Auto-GPT: An autonomous GPT-4 experiment.
- Hong et al., 2023. MetaGPT: Meta programming for a multi-agent collaborative framework. ICLR 2024.
- Humphreys et al., 2022. A data-driven approach for learning to control computers. ICML 2022.
- Jimenez et al., 2024. SWE-bench: Can language models resolve real-world GitHub issues? ICLR 2024.
- Lai et al., 2024. AutoWebGLM: Bootstrap and reinforce a large language model-based web navigating agent. Preprint.
- Li et al., 2023b. Can LLM already serve as a database interface? A BIg bench for large-scale database grounded text-to-SQLs. NeurIPS 2023 D&B Track.
- Liu et al., 2018. Reinforcement learning on web interfaces using workflow-guided exploration. ICLR 2018.
- Liu et al., 2023. AgentBench: Evaluating LLMs as agents. Preprint.
- Mialon et al., 2023. GAIA: A benchmark for general AI assistants. Preprint.
- Muennighoff et al., 2024. OctoPack: Instruction tuning code large language models. ICLR 2024.
- Pan et al., 2024. Autonomous evaluation and refinement of digital agents. Preprint.
- Pan et al., 2023. Logic-LM: Empowering large language models with symbolic solvers for faithful logical reasoning. Preprint.
- Patil et al., 2023. Gorilla: Large language model connected with massive APIs. Preprint.
- Rein et al., 2023. GPQA: A graduate-level Google-proof Q&A benchmark. Preprint.
- Tafjord et al., 2021. ProofWriter: Generating implications, proofs, and abductive statements over natural language. ACL-IJCNLP 2021 Findings.
- Tang et al., 2024b. ML-Bench: Evaluating large language models and agents for machine learning tasks on repository-level code. Preprint.
- Tang et al., 2024c. BioCoder: A benchmark for bioinformatics code generation with large language models. Bioinformatics, 40(S1).
- Wang et al., 2024a. Executable code actions elicit better LLM agents. ICML 2024.
- Wang et al., 2024b. MINT: Evaluating LLMs in multi-turn interaction with tools and language feedback. ICLR 2024.
- Wu et al., 2023. AutoGen: Enabling next-gen LLM applications via multi-agent conversation framework. Preprint.
- Xia et al., 2024. Agentless: Demystifying LLM-based software engineering agents. Preprint.
- Xu et al., 2023. Lemur: Harmonizing natural language and code for language agents. Preprint.
- Yang et al., 2024. SWE-agent: Agent-computer interfaces enable automated software engineering. Preprint.
- Zhang et al., 2024a. Probing the multi-turn planning capabilities of LLMs via 20 question games. Preprint.
- Zhang et al., 2024b. AutoCodeRover: Autonomous program improvement. Preprint.
- Zhou et al., 2023a. WebArena: A realistic web environment for building autonomous agents. ICLR 2024.
- Zhuang et al., 2024. ToolQA: A dataset for LLM question answering with external tools. NeurIPS 2024.
- Zhuge et al., 2024. Language agents as optimizable graphs. Preprint.
- Chase, 2022. LangChain. GitHub repository.
