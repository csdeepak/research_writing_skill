# OpenHands: An Open Platform for AI Software Developers as Generalist Agents

*Wang et al. — Published at ICLR 2025*

---

## Abstract

Developing AI agents that can autonomously solve real-world tasks requires shared infrastructure for safe execution, extensible tools, and systematic evaluation — yet the current ecosystem is fragmented across incompatible, single-purpose frameworks. We present OpenHands (formerly OpenDevin), a community-driven open platform in which agents interact with computing environments through the same interfaces a human developer uses: writing and executing code, running shell commands, and browsing the web. The platform provides an event-stream architecture that decouples agent logic from environment details, a Docker-sandboxed runtime for safe code execution, an extensible skill library, multi-agent delegation, and a unified evaluation framework spanning 15 established benchmarks across software engineering, web interaction, and general assistance tasks. We evaluate agents on these benchmarks and show that a single generalist agent — CodeActAgent, which uses code as its primary action modality — achieves competitive performance across all three task categories without task-specific modification: 26.0% on SWE-Bench Lite (comparable to open-source software engineering specialists), 15.5% on WebArena (competitive with domain-general web agents), and 52.0% on the GPQA graduate-level question-answering benchmark (surpassing GPT-4 few-shot chain-of-thought at 38.8%; the OpenHands agent uses claude-3-5-sonnet rather than GPT-4, so the gain reflects both tool access and the choice of backbone). Released under the MIT license with over 188 contributors, OpenHands provides an open foundation for advancing generalist agent research.

---

## 1. Introduction

Large language models (LLMs) have enabled a new class of AI systems called *agents*: programs that perceive their environment, plan, and take actions to complete multi-step tasks (Jimenez et al., 2024; Zhou et al., 2023a; Wang et al., 2024b). Unlike a standard LLM that produces a single text response, an agent operates in a loop — taking an action, observing the result, and deciding what to do next. Recent work has applied agents to tasks that once required significant human effort: resolving GitHub bug reports, navigating commercial websites, answering graduate-level scientific questions by searching the web, and writing executable code for machine learning pipelines.

The most powerful way humans currently interact with the world is through software. A skilled programmer can, with a few lines of code, automate repetitive processes, orchestrate complex workflows, and interface with virtually any digital service. This observation motivates using software itself — code execution, command-line tools, and web browsers — as the primary action space for AI agents. Software-based actions are expressive enough to represent any tool use; code execution inside a sandboxed environment is reliably reproducible, although individual runs can vary due to network calls, non-deterministic LLM sampling, or test flakiness. Together, these properties make software a well-suited universal interface for agents.

Despite rapid progress in LLM capabilities, the infrastructure for building and evaluating software-acting agents is immature. Existing frameworks address pieces of the problem: some provide multi-agent communication (Wu et al., 2023; Hong et al., 2023), some target software engineering specifically (Yang et al., 2024), and some focus on web browsing (Zhou et al., 2023a). None combines safe sandboxed code execution, modular extensibility, multi-agent delegation, and systematic evaluation across a broad set of benchmarks. This fragmentation makes it difficult to compare approaches, measure genuine progress, or reuse components across projects.

This raises a concrete empirical question: can a single generalist agent — operating through code as its primary action space and without task-specific modification — achieve competitive performance simultaneously across software engineering, web browsing, and general-assistance tasks, categories that existing specialist frameworks treat separately?

We introduce **OpenHands** (formerly OpenDevin), a community-driven open platform designed to address these infrastructure gaps. OpenHands provides:

1. An **event-stream architecture** that records all agent actions and environment observations, allowing agents to be implemented as simple functions that map history to the next action.
2. A **Docker-sandboxed runtime** with a bash shell, Jupyter IPython server, and Playwright-powered web browser, enabling safe execution of agent-generated code on arbitrary operating system images.
3. An **AgentSkills library** of extensible Python utilities that agents can call when direct code generation is insufficient.
4. **Multi-agent delegation**, allowing a generalist agent to hand off subtasks to specialists.
5. An **evaluation framework** integrating 15 benchmarks spanning software engineering, web browsing, and miscellaneous assistance tasks.

The platform includes a hub of over 10 implemented agents. We focus evaluation on CodeActAgent — a generalist agent that acts primarily by executing code and shell commands — and demonstrate that it achieves competitive results across all three task categories without task-specific modification.

**Contributions.** (1) We describe the OpenHands platform and its architecture. (2) We instantiate and evaluate CodeActAgent — built on the CodeAct action-space design (Wang et al., 2024a) — as the platform's primary generalist agent; its contribution here is integration and cross-domain evaluation, not the CodeAct design itself. (3) We evaluate agents across 15 benchmarks and show that one generalist agent achieves competitive performance in software engineering, web interaction, and general assistance — domains that specialist baselines address individually.

---

## 2. Background: Agents, Environments, and Action Spaces

An AI agent is a system that observes its environment, selects an action, and updates its state based on the result. This loop is familiar from reinforcement learning: in a Markov decision process an agent learns a policy that selects from a fixed, pre-enumerated action set (e.g., move-left, move-right). LLM-based agents follow the same observe–act–update loop, but the policy is a language model that generates each action as new code — any Python function, shell command, or web request the model can express becomes available. The agent's "state" is its chronological history of past actions and observations — the conversation so far. Because the action space is not pre-enumerated, LLM agents acting through code can in principle address any task expressible in software without pre-specifying which tools to support.

The choice of **action space** strongly shapes what an agent can do. Early LLM agents used structured API calls (fixed function signatures) as actions, which limits agents to predefined tools. The CodeAct approach (Wang et al., 2024a), which underpins OpenHands's primary agent, instead treats *executable code* as the action: the agent writes Python scripts or shell commands that the runtime executes, returning the output as the next observation. This design is powerful because code is Turing-complete — any tool, computation, or workflow expressible in software becomes available to the agent without pre-specification.

For web browsing, agents need a different kind of action: clicking, typing, and navigating in a browser. OpenHands integrates the BrowserGym action space (Drouin et al., 2024), which provides a domain-specific language for browser interaction, including navigation, clicking, typing, scrolling, and form submission. This vocabulary is surfaced in OpenHands through the BrowseInteractiveAction type described in §3.1.

Several existing frameworks create agent infrastructure. AutoGPT (Gravitas, 2023) and LangChain (Chase, 2022) offer general-purpose components but lack integrated sandboxed execution. MetaGPT (Hong et al., 2023) and AutoGen (Wu et al., 2023) focus on multi-agent communication. SWE-Agent (Yang et al., 2024) provides a carefully engineered agent-computer interface for GitHub issue resolution but is domain-specific. OpenHands aims to unify these concerns in a single extensible platform.

---

## 3. The OpenHands Platform

### 3.1 Agent Abstraction and the Event Stream

The core abstraction in OpenHands is simple: an agent is a function that takes the current **state** — a data structure containing the full history of actions and observations — and returns the next action. The state is organized around an **event stream**, a chronological list of all past action-observation pairs, including messages from the user. This design separates agent logic cleanly from execution details: an agent implementor only needs to write the `step` function; everything else (running the action, capturing the result, updating the stream) is handled by the platform.

Actions are a typed set of primitives. `IPythonRunCellAction` executes Python code in a persistent Jupyter kernel, maintaining variable state across steps. `CmdRunAction` runs a bash command. `BrowseInteractiveAction` sends browser commands in the BrowserGym domain-specific language introduced in §2. `MessageAction` lets the agent communicate with the user. `AgentDelegateAction` dispatches a subtask to another agent. Observations capture execution results: standard output and error, browser state (including HTML, DOM, and an accessibility tree), and user messages.

This architecture is also compatible with tool-calling agents that use JSON-formatted function calls: tool wrappers can be expressed as Python functions within the IPython environment, so agents that expect a function-calling API can operate within OpenHands with minimal adaptation.

### 3.2 Sandboxed Runtime

Every task session runs inside an isolated Docker container. The container exposes a REST API — the OpenHands action execution API — that the backend uses to send actions and receive observations. Inside the container, three components handle action execution: a persistent bash shell, a Jupyter IPython server, and a Playwright-backed Chromium browser.

A key feature is support for *arbitrary Docker images*: users can supply any base image (e.g., a pre-configured Python environment for a specific ML library), and OpenHands automatically installs its action execution API into that image. This makes it possible to evaluate agents in the exact software environment required by a task, without manual setup.

Image management uses a dual-tagging scheme. A hash-based tag encodes the MD5 of the build context, guaranteeing that identical hashes mean identical images. A human-readable tag records the OpenHands version and base image. This combination supports both reproducibility (share the hash, get the same environment) and convenience (pull the latest version of a configuration).

### 3.3 AgentSkills: An Extensible Tool Library

While code execution provides a powerful foundation, some operations are awkward to implement from scratch in a single LLM-generated snippet: for example, viewing a specific line range of a large file, or extracting text from an image using a vision-language model. OpenHands addresses this with the **AgentSkills** library, a Python package of utility functions that are automatically imported into the agent's IPython session.

The addition criterion is deliberate: a new skill is added only when (1) LLMs reliably fail to generate the equivalent code directly, or (2) the operation requires calling an external model. Current skills include file editing primitives adapted from SWE-Agent (Yang et al., 2024) and Aider (`edit_file`, `scroll_up`, `scroll_down`), and multi-modal parsing utilities (`parse_pdf`, `parse_image` using a vision-language model, `parse_audio` using a speech-to-text model). This design avoids wrapping well-known libraries unnecessarily while providing access to capabilities beyond a single LLM call.

### 3.4 Multi-Agent Delegation

OpenHands supports heterogeneous multi-agent systems through `AgentDelegateAction`. When a generalist agent encounters a subtask requiring specialized expertise — for example, extended web navigation — it can delegate that subtask to a specialist agent with appropriate tools and prompting. The specialist runs to completion and returns its result as an observation to the calling agent. This pattern allows composing specialized capabilities without requiring a single monolithic agent to handle all tasks equally well.

---

## 4. The Agent Hub

OpenHands ships with a hub of more than 10 implemented agents. The three most relevant for evaluation are:

**CodeActAgent** is the default generalist agent, built on the CodeAct framework (Wang et al., 2024a). At each step, it may converse with the user, execute Python code, run bash commands, or browse the web. No task-specific prompt modification is made across evaluations.

**BrowsingAgent** is a generalist web agent using zero-shot prompting, designed as a baseline for web-interaction benchmarks. It uses the full BrowserGym action set (Drouin et al., 2024) and produces accessibility-tree-based observations.

**GPTSwarm** (Zhuge et al., 2024) implements an optimizable multi-agent graph, where nodes represent operations and edges represent communication pathways. It is evaluated on the GAIA general-assistant benchmark.

The platform also supports **Micro Agents**: lightweight wrappers that extend a generalist agent with a specialized system prompt, lowering the barrier for community members to contribute task-specific behavior without implementing a full agent from scratch.

---

## 5. Evaluation Framework and Setup

To assess agent generality, OpenHands integrates **15 benchmarks** across three categories:

- **Software engineering** (7 benchmarks): SWE-Bench (GitHub issue resolution; Jimenez et al., 2024), HumanEvalFix (iterative bug fixing with test feedback; Muennighoff et al., 2024), BIRD (text-to-SQL on real-world databases; Li et al., 2023b), BioCoder (bioinformatics code generation across domain-specific APIs; Tang et al., 2024c), ML-Bench (running ML pipelines from repository-level code; Tang et al., 2024b), Gorilla APIBench (API selection from natural language descriptions; Patil et al., 2023), ToolQA (question answering requiring external tool calls over structured data; Zhuang et al., 2024)
- **Web browsing** (2 benchmarks): WebArena (multi-step tasks on realistic self-hosted websites; Zhou et al., 2023a), MiniWoB++ (structured form-completion and navigation tasks on synthetic web interfaces; Liu et al., 2018)
- **Miscellaneous assistance** (6 benchmarks): GAIA (multi-modal general reasoning requiring web search, coding, and file parsing; Mialon et al., 2023), GPQA (graduate-level "Google-proof" science questions; Rein et al., 2023), AgentBench OS (bash task completion inside a virtual operating system environment; Liu et al., 2023), MINT (multi-turn problem solving with up to five iterations of tool-oracle feedback; Wang et al., 2024b), Entity Deduction Arena (multi-turn "20 questions" identification game; Zhang et al., 2024a), ProofWriter (multi-hop deductive reasoning over natural language facts; Tafjord et al., 2021)

All OpenHands evaluations compare against open-source baselines that do not perform manual prompt engineering targeted at specific benchmarks. Each OpenHands agent is evaluated in zero-shot mode (no task demonstrations) unless otherwise stated. Evaluations are performed without hint text on SWE-Bench.

For brevity and cost management, the default SWE-Bench configuration uses the 300-instance Lite subset; running the full 2,294-instance benchmark costs approximately $6,900 with gpt-4o.

---

## 6. Results

### 6.1 Software Engineering

**SWE-Bench Lite** (Jimenez et al., 2024) evaluates agents on real GitHub issue resolution: given a repository and an issue description (e.g., a bug report), the agent must modify the code so that the repository's test suite passes. The *resolve rate* is the fraction of issues for which the modified code passes all tests. This benchmark reflects real-world software engineering difficulty; issues are drawn from popular open-source Python projects and require understanding code structure, error messages, and repository conventions.

**Table 1: SWE-Bench Lite and HumanEvalFix results (selected agents)**

| Agent | Model | SWE-Bench Lite (%) | HumanEvalFix Python (%) |
|---|---|---|---|
| SWE-Agent (Yang et al., 2024) | gpt-4-1106-preview | 18.0 | 87.7 (1-shot) |
| AutoCodeRover (Zhang et al., 2024b) | gpt-4-0125-preview | 19.0 | — |
| Aider (Gauthier) | gpt-4o + claude-3-opus | 26.3 | — |
| Agentless (Xia et al., 2024) | gpt-4o | 27.3 | — |
| StarCoder2-15B — non-agentic | — | — | 48.6 |
| OH CodeActAgent v1.8 | gpt-4o-mini | 6.3 | — |
| OH CodeActAgent v1.8 | gpt-4o | 22.0 | — |
| OH CodeActAgent v1.8 | claude-3-5-sonnet | 26.0 | — |
| OH CodeActAgent v1.5 (0-shot) | gpt-4o | — | 79.3 |

CodeActAgent v1.8 with claude-3-5-sonnet achieves 26.0% on SWE-Bench Lite, above SWE-Agent (18.0%) and AutoCodeRover (19.0%), and within 0.3 percentage points of Aider (26.3%). All results in this paper are single runs without variance estimates (see §7 Limitations), so sub-1% differences — such as the gap with Aider — should not be treated as meaningful performance distinctions. The gap between the smallest backbone (gpt-4o-mini, 6.3%) and the strongest (claude-3-5-sonnet, 26.0%) spans a factor of four, illustrating how the same infrastructure makes LLM choice the dominant variable when framework differences are held constant.

**HumanEvalFix** (Muennighoff et al., 2024) evaluates bug fixing: the agent is given a function and failing test cases, and must modify the function until all tests pass. Pass rate measures the fraction of bugs successfully fixed. CodeActAgent achieves 79.3% in zero-shot mode, nearly doubling non-agentic StarCoder2-15B (48.6%), which cannot iterate on feedback from test execution. SWE-Agent reaches 87.7%, but does so with a one-shot demonstration — a full, successful trajectory for a sample problem — whereas the OpenHands result uses no demonstration at all.

Additional software benchmarks extend this picture. On **ML-Bench** (Tang et al., 2024b) — evaluating agents' ability to run machine learning code across 18 GitHub repositories — CodeActAgent (gpt-4o) reaches 64.4%, outperforming SWE-Agent (42.6%) on the same tasks. On **Gorilla APIBench** (Patil et al., 2023) — API selection from natural language descriptions — CodeActAgent achieves 47.2% (gpt-4o), compared to 36.4% for the Gorilla fine-tuned model. On **BIRD** (Li et al., 2023b), a text-to-SQL benchmark where the agent receives database schema and a natural language question and must produce an executable SQL query, multi-turn interaction allows self-correction; CodeActAgent reaches 47.3% on 300 development instances.

### 6.2 Web Browsing

**WebArena** (Zhou et al., 2023a) is a self-hosted benchmark with 812 human-curated task instructions across realistic web environments — shopping sites, developer forums, content management systems, and social platforms. Agents must freely navigate sites to complete tasks; correctness is evaluated by execution of the completed action (e.g., verifying that an order was placed or a post was created). Success rate measures the fraction of tasks completed correctly.

**Table 2: WebArena and MiniWoB++ results (selected agents)**

| Agent | Model | WebArena (%) | MiniWoB++ Full (%) |
|---|---|---|---|
| Lemur (Xu et al., 2023) | 70B chat | 5.3 | — |
| AutoWebGLM (Lai et al., 2024) | Trained 7B | 18.2 | — |
| Auto Eval & Refine (Pan et al., 2024) | GPT-4 + Reflexion | 20.2 | — |
| WebArena Agent (Zhou et al., 2023a) | gpt-4-turbo | 14.4 | — |
| CC-NET (Humphreys et al., 2022) | RL + human annotation | — | 91.1 |
| Workflow Guided Exploration (Liu et al., 2018) | Trained specialist | — | 34.6 |
| OH BrowsingAgent v1.0 | gpt-4o-mini | 8.5 | 27.2 |
| OH BrowsingAgent v1.0 | gpt-4o | 14.8 | 40.8 |
| OH BrowsingAgent v1.0 | claude-3-5-sonnet | 15.5 | — |

BrowsingAgent with claude-3-5-sonnet reaches 15.5% on WebArena, competitive with the WebArena baseline agent (14.4%) that uses a substantially similar approach. It does not reach the 20.2% of Auto Eval & Refine (Pan et al., 2024), which uses GPT-4V as a reward model for retry-on-error, nor the 18.2% of AutoWebGLM, which trains on specialized human-annotated data. These gaps are expected given the zero-shot setting.

**MiniWoB++** (Liu et al., 2018) provides 125 synthetic web interfaces with built-in reward functions. Tasks are shorter and more structured than WebArena — closer to filling out forms and clicking buttons than to multi-step web research. BrowsingAgent (gpt-4o) reaches 40.8% on the full 125-environment set (results are reported on the complete set, unlike some prior work that omits vision-dependent tasks). Specialist trained models using reinforcement learning with human demonstrations reach 91.1% (CC-NET, Humphreys et al., 2022) — a different training regime that is not directly comparable to zero-shot LLM-based agents.

### 6.3 Miscellaneous Assistance

**GPQA** (Rein et al., 2023) presents graduate-level, "Google-proof" questions in biology, chemistry, and physics — questions designed so that non-expert web search does not trivially yield the answer. The diamond subset (198 instances) is the hardest. Agents with access to Python execution and web search can perform precise computations and retrieve specialized knowledge beyond their parametric knowledge, making this benchmark particularly informative about the value of agentic tool use.

**Table 3: GPQA Diamond Set and GAIA L1 results (selected agents)**

| Agent | Model | GPQA Diamond (%) | GAIA L1 (%) |
|---|---|---|---|
| Non-expert human | — | 21.9 | — |
| Few-shot CoT (Rein et al., 2023) | gpt-3.5-turbo-16k | 29.6 | — |
| Few-shot CoT (Rein et al., 2023) | gpt-4 | 38.8 | — |
| Expert human | — | 81.3 | — |
| AutoGPT (Gravitas, 2023) | gpt-4-turbo | — | 13.2 |
| OH GPTSwarm v1.0 | gpt-4o | — | 32.1 |
| OH CodeActAgent v1.8 | claude-3-5-sonnet | 52.0 | — |

CodeActAgent with tool use achieves 52.0% on the GPQA diamond set, above GPT-4 few-shot chain-of-thought (38.8%) and substantially exceeding the non-expert human baseline (21.9%). Expert human performance (81.3%) remains a clear ceiling. The two baselines differ in both backbone (claude-3-5-sonnet vs. GPT-4) and tool access, so the 13-point gap cannot be attributed to tool use alone; the Discussion addresses this limitation. What the numbers do establish is that CodeActAgent's ability to run Python for precise calculations and retrieve domain-specific information from the web is well matched to the demands of graduate-level science problems.

On **GAIA** Level 1 (Mialon et al., 2023) — a benchmark requiring reasoning, multi-modal understanding, web browsing, and coding across 466 tasks — OpenHands's GPTSwarm agent achieves 32.1% (gpt-4o) compared to AutoGPT's 13.2%, demonstrating the benefit of structured multi-agent coordination for general-purpose tasks.

Additional benchmarks further characterize the agents. **AgentBench OS** (Liu et al., 2023) evaluates bash command-driven task completion: CodeActAgent reaches 57.6% versus the baseline agent's 42.4%. **MINT math** (Wang et al., 2024b) evaluates multi-turn problem solving with up to five iterations; CodeActAgent reaches 77.3% versus 65.8% for the baseline. **ProofWriter** (Tafjord et al., 2021) evaluates deductive reasoning over 5-hop logical chains; CodeActAgent reaches 78.8%, near Logic-LM's 79.6% (Pan et al., 2023), which uses a specialized symbolic solver. On **Entity Deduction Arena** (Zhang et al., 2024a), a multi-turn "20 questions" game, CodeActAgent reaches 38.0% — slightly below the GPT-4 zero-shot baseline (40.0%) — representing one of the few cases where the agentic approach does not improve over direct prompting.

---

## 7. Discussion

**A generalist agent can be competitive across task categories.** The central finding is that CodeActAgent, without any change to its system prompt or architecture, achieves competitive results in software engineering, web browsing, and general assistance. Specialist baselines in each category are often fine-tuned or engineered specifically for that domain; a zero-shot generalist reaching comparable performance is a meaningful data point. The authors attribute this to the expressive power of code-based actions: any tool, computation, or web request can be expressed as code, which means the agent's action vocabulary is effectively unlimited without pre-specification of tools. This interpretation is consistent with the results, but no ablation in the paper isolates the action-space contribution from backbone strength or scaffold design; the attribution remains an explanatory hypothesis.

**Tool use amplifies LLM capability on knowledge-intensive tasks.** The GPQA result is consistent with this: GPT-4 few-shot chain-of-thought achieves 38.8%; CodeActAgent with claude-3-5-sonnet and tool access reaches 52.0%. This comparison involves two differences simultaneously — backbone model (claude-3-5-sonnet vs. GPT-4) and tool access — which cannot be isolated from a single comparison. However, the nature of the tasks makes tool access a plausible contributor: GPQA questions require precise computation and retrieval of domain-specific information (protein structures, reaction mechanisms) that demonstrably exceed parametric knowledge. For ML researchers evaluating LLMs on knowledge or reasoning benchmarks, this result suggests that non-agentic baselines may substantially underestimate the practical capability of these systems when equipped with tools.

**Infrastructure enables cleaner scientific comparisons.** The four-fold range on SWE-Bench Lite (6.3% for gpt-4o-mini, 26.0% for claude-3-5-sonnet) illustrates why shared infrastructure matters: cross-framework comparisons conflate framework quality with model quality, while swapping only the backbone within OpenHands holds the framework constant — though prompt–scaffold interactions that differ across models mean LLM capability is not fully isolated even within this setting. The platform's integration testing framework, which mocks LLM calls for deterministic behavior during development, further supports this by providing regression detection as the codebase evolves.

**Limitations.** The evaluation results are reported without variance estimates across random seeds or LLM sampling runs; given the stochastic nature of LLM decoding, performance differences smaller than a few percentage points should be interpreted cautiously. Current agents struggle when editing long files, as the context window limits how much of a file the agent can view and process at once. Workflow design — deciding which agents to invoke in what sequence — requires substantial handcrafting, though graph-based frameworks like GPTSwarm point toward automation. Evaluation is performed on benchmarks; transfer to production software systems or private codebases is not tested.

---

## 8. Related Work

**General-purpose agent frameworks.** AutoGPT (Gravitas, 2023) and LangChain (Chase, 2022) provide foundational components for LLM-based agents but lack integrated sandboxed execution. MetaGPT (Hong et al., 2023) introduces standardized operating procedures for multi-agent software development teams. AutoGen (Wu et al., 2023) provides a conversation framework enabling Python and bash execution, though with stateless command execution that cannot maintain session state across turns. OpenHands differs from all of these by combining sandboxed stateful execution, a standardized tool library, and a multi-benchmark evaluation framework.

**Software engineering agents.** SWE-Agent (Yang et al., 2024) integrates a custom agent-computer interface for GitHub issue resolution, emphasizing that the design of the interface — how the agent views and edits files — matters substantially for performance. AutoCodeRover (Zhang et al., 2024b) uses code search and abstract syntax tree manipulation. Agentless (Xia et al., 2024) demonstrates that a simple, non-iterative approach can also achieve competitive results. OpenHands provides infrastructure within which these designs can be compared under controlled conditions.

**Web browsing agents.** AutoWebGLM (Lai et al., 2024) trains a specialized 7B model for web navigation using human-annotated demonstrations. Auto Eval & Refine (Pan et al., 2024) applies Reflexion-style retry with GPT-4V as a reward model. BrowserGym (Drouin et al., 2024) provides the action primitives that OpenHands's BrowsingAgent builds on. OpenHands makes web browsing capabilities available within the same event-stream framework as code execution, enabling agents that seamlessly combine the two.

**Multi-agent systems.** GPTSwarm (Zhuge et al., 2024) represents agent systems as optimizable directed graphs in which nodes are operations and edges are communication pathways. MetaGPT (Hong et al., 2023) and AutoGen (Wu et al., 2023) explore role-playing and conversational multi-agent designs. OpenHands's multi-agent delegation mechanism uses a caller/callee pattern rather than peer communication, integrating naturally with the event-stream architecture.

---

## 9. Conclusion

OpenHands addresses a fundamental infrastructure gap in the agent research ecosystem: the absence of a shared, open platform that combines safe sandboxed code execution, a unified action space, extensible tools, multi-agent delegation, and systematic multi-benchmark evaluation. The platform is the primary contribution; the empirical evaluation — showing that one unmodified generalist agent (CodeActAgent) is simultaneously competitive across software engineering, web browsing, and general assistance — validates that the infrastructure supports the breadth of capability its design targets.

These findings carry three implications. First, software-grounded action spaces are more general than domain-specific alternatives: any tool or workflow expressible in code is available to the agent without pre-specification, and the benchmarks show this generalizes across three qualitatively different task categories. Second, shared infrastructure is a precondition for measuring agent generality: the four-fold performance range across backbone models within the same framework shows that cross-framework comparisons systematically conflate platform quality with model quality, obscuring genuine capability differences. Third, the platform is designed for low-overhead reuse: providing a custom Docker image is sufficient to evaluate agents on a new benchmark, and the AgentHub pattern means contributing a new agent requires implementing only a single step function.

OpenHands is released under the MIT license, with 32K GitHub stars and over 188 contributors as of publication. Active open challenges include robust long-file editing, automated agent workflow generation, and developing stronger agents through training-time techniques.

---

## References

- Chase, 2022. LangChain. GitHub repository.
- Drouin et al., 2024. WorkArena: How capable are web agents at solving common knowledge work tasks? Preprint.
- Gauthier. Aider: How aider scored SOTA 26.3% on SWE-bench Lite. Blog post.
- Gravitas, 2023. Auto-GPT: An autonomous GPT-4 experiment. GitHub repository.
- Hong et al., 2023. MetaGPT: Meta programming for a multi-agent collaborative framework. ICLR 2024.
- Humphreys et al., 2022. A data-driven approach for learning to control computers. ICML 2022.
- Jimenez et al., 2024. SWE-bench: Can language models resolve real-world GitHub issues? ICLR 2024.
- Lai et al., 2024. AutoWebGLM: Bootstrap and reinforce a large language model-based web navigating agent. Preprint.
- Li et al., 2023b. Can LLM already serve as a database interface? A BIg bench for large-scale database grounded text-to-SQLs. NeurIPS 2023 D&B Track.
- Liu et al., 2018. Reinforcement learning on web interfaces using workflow-guided exploration. ICLR 2018.
- Liu et al., 2023. AgentBench: Evaluating LLMs as agents. Preprint.
- Mialon et al., 2023. GAIA: A benchmark for general AI assistants. Preprint.
- Muennighoff et al., 2024. OctoPack: Instruction tuning code large language models. ICLR 2024.
- Pan et al., 2023. Logic-LM: Empowering large language models with symbolic solvers for faithful logical reasoning. Preprint.
- Pan et al., 2024. Autonomous evaluation and refinement of digital agents. Preprint.
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
