# OpenHands: An Open Platform for AI Software Developers as Generalist Agents

**Wang et al., 2025 (Published at ICLR 2025)**

---

## Abstract

As large language models (LLMs) become capable of complex reasoning and code generation, a critical question arises: can these models be turned into autonomous agents that interact with the real world through software? We present **OpenHands** (formerly OpenDevin), an open-source platform for building and evaluating AI agents that interact with the world the way a human software developer does — by writing and executing code, running shell commands, and browsing the web. OpenHands provides four core capabilities: (1) a flexible event-stream architecture that connects agents, environments, and user interfaces; (2) a Docker-sandboxed runtime environment that safely executes arbitrary agent-generated code; (3) an extensible library of reusable agent skills; and (4) multi-agent delegation for cooperative task solving. To measure progress systematically, the platform integrates 15 established benchmarks spanning software engineering, web browsing, and general assistance. Across these benchmarks, the platform's default CodeAct agent achieves competitive performance — including a 26% resolve rate on SWE-Bench Lite and 52% accuracy on GPQA (graduate-level Q&A) — without task-specific prompt engineering. Released under the MIT license with over 2.1K contributions from 188+ community members, OpenHands serves as both a research platform and a shared infrastructure for advancing agentic AI systems.

---

## 1. Introduction

Software is arguably the most powerful medium through which humans currently shape the world: nearly every domain of human activity — from scientific research to everyday logistics — runs on code. A natural question therefore follows: if we can build AI systems that develop, debug, and deploy software autonomously, can we unlock qualitatively new levels of automation across many domains simultaneously?

The rise of capable LLMs such as GPT-4 (OpenAI et al., 2024) has brought this question within reach. Recent work demonstrates that LLM-backed agents can already solve real-world GitHub issues (Jimenez et al., 2024), navigate live websites (Zhou et al., 2023a), conduct laboratory experiments (Boiko et al., 2023), and assist with scientific research (Tang et al., 2024a). Yet despite this rapid progress, the field lacks a shared, open infrastructure for building, comparing, and extending these agents. Individual research systems are often brittle, narrowly scoped, or too expensive to reproduce, which fragments the research community and slows cumulative progress.

This paper describes OpenHands (formerly OpenDevin), a community-driven open platform designed to address this gap. OpenHands treats software — specifically an LLM-backed agent's ability to write and execute code — as the universal interface through which an agent interacts with the world. The design choice is not arbitrary: programming languages are expressive enough to call any API, orchestrate any tool, and manipulate any digital artifact, making them a natural general-purpose action space for agents.

Prior frameworks for building agents each address part of the problem. LangChain (Chase, 2022) provides modular building blocks but limited runtime support. AutoGen (Wu et al., 2023) enables multi-agent conversation but uses stateless command execution. SWE-Agent (Yang et al., 2024) defines a strong Agent-Computer Interface for software tasks but is narrowly focused on software engineering. None of these combines a safe sandboxed execution environment, a reusable skill library, multi-agent collaboration, a graphical user interface, and a broad evaluation framework in a single system. OpenHands fills that gap.

The platform's key technical contributions are:

- An **event-stream architecture** that decouples agents, environments, and interfaces, making each interchangeable and extensible.
- A **Docker-sandboxed runtime** that safely executes arbitrary agent-generated code (Python, bash, browser interactions) and supports any arbitrary base operating system image.
- An **AgentSkills library** that provides reusable utilities — file editing, multi-modal parsing, code search — that any agent implementation can call.
- A **multi-agent delegation mechanism** allowing specialized agents to collaborate on subtasks.
- An **evaluation framework** currently spanning 15 established benchmarks, enabling systematic tracking of agent progress.

Beyond these technical contributions, OpenHands is significant as a community artifact: as of writing, it has 32K GitHub stars and more than 2.1K contributions from over 188 contributors across academia and industry.

---

## 2. The OpenHands Architecture

OpenHands is organized around three tightly integrated components: an **agent abstraction** that defines how agents observe and act, a **runtime environment** that executes those actions safely, and a **skill library** that extends the agent's capabilities. A fourth component supports **multi-agent delegation**. Together, these define what the paper calls the OpenHands architecture.

### 2.1 Agent Abstraction and Event Stream

At the heart of OpenHands is a shared data structure called the **event stream** — an ordered log of every action taken and every observation received during a task session. Actions represent decisions made by the agent (or user); observations represent the outcomes of executing those actions in the environment.

An agent in OpenHands is defined by a single function: it takes the current state (which includes the full event stream, accumulated cost of LLM calls, and other metadata) and returns a single action. This simple interface is intentionally minimal so that researchers can implement new agent behaviors without touching low-level execution infrastructure.

The **action space** is defined by three core primitives:

- `IPythonRunCellAction` — execute arbitrary Python code in an interactive Jupyter kernel running inside the sandbox.
- `CmdRunAction` — execute arbitrary bash commands in a shell.
- `BrowseInteractiveAction` — interact with a full Chromium browser using a domain-specific language provided by BrowserGym (Drouin et al., 2024), supporting navigation, clicking, form filling, file upload, scrolling, and more.

These three primitives cover the vast majority of tasks performed by human software engineers. Because all tools are ultimately expressed as Python functions or bash commands, agents can also *create* new tools at runtime — for example, by writing a Python helper function that wraps a REST API — without requiring the system to be aware of those tools in advance (Yuan et al., 2023). This makes the action space practically unbounded while remaining well-defined and safe to execute.

When human users need to interact with a running agent, they inject `MessageAction` events directly into the event stream, and the agent naturally processes these as part of its context on the next step. This same mechanism enables multi-turn human-agent collaboration: the user can interrupt the agent at any time to provide feedback or redirect it.

### 2.2 Runtime Environment

Executing arbitrary agent-generated code safely requires careful isolation. OpenHands achieves this through a **Docker-sandboxed runtime**: for every task session, the platform spins up a fresh Docker container and mounts only the files the user explicitly wants the agent to access. Inside the container, OpenHands installs a lightweight REST API server (the *OpenHands Action Execution API*) that accepts action requests and returns observations. The container hosts three internal services:

1. A **bash shell** connected to the operating system for command execution.
2. A **Jupyter IPython server** for interactive Python execution and stateful notebook-style workflows.
3. A **Playwright Chromium browser** for web interactions, including HTML/DOM access, accessibility tree inspection, screenshots, and multi-tab management.

A distinctive feature of the runtime is its support for **arbitrary Docker images**. Rather than requiring agents to use a predefined operating system, OpenHands accepts any user-provided Docker image, automatically wraps it by installing the action execution API, and launches it as the execution environment. This allows agents to work in specialized software environments — for example, a repository-specific environment for a software engineering task — without any configuration changes to the agent itself.

To manage build efficiency, OpenHands uses a dual-tagging scheme for runtime images: a hash-based tag (derived from an MD5 hash of the build context) guarantees exact reproducibility, while a generic tag provides a convenient pointer to the latest compatible version of a given base image configuration. When launching a new session, the system checks whether an image with the exact hash already exists; if not, it attempts to rebuild from the most recent generic image to avoid redundant dependency installation.

### 2.3 AgentSkills: An Extensible Agent-Computer Interface

SWE-Agent (Yang et al., 2024) demonstrated that a carefully crafted Agent-Computer Interface (ACI) — specialized tools tailored to a particular task — can substantially improve agent performance on complex tasks. However, creating and maintaining such tools for every task type is a significant engineering burden, and tools built for one agent implementation are often not reusable by another.

OpenHands addresses this through the **AgentSkills library**, a Python package that is automatically imported into the Jupyter IPython environment at session start. Because skills are plain Python functions, any agent that issues `IPythonRunCellAction` calls can use them without further setup.

The inclusion philosophy is conservative: a skill is only added to the library when the corresponding capability is either too difficult for an LLM to implement correctly from scratch, or requires calling an external model. Under this criterion, the current library includes:

- **File editing utilities** (`edit_file`, `open_file`, `scroll_up`, `scroll_down`, `goto_line`, `search_dir`, `search_file`, `find_file`) — adapted from SWE-Agent (Yang et al., 2024) and Aider (Gauthier) — for navigating and editing large code files without loading their entire contents into the context window.
- **Multi-modal document parsing** (`parse_pdf`, `parse_docx`, `parse_latex`, `parse_audio`, `parse_image`, `parse_video`, `parse_pptx`) — which call external vision-language or speech-to-text models (e.g., GPT-4V) to extract information from non-text files.
- **Code creation and file management** (`create_file`).

By lowering the barrier for community contributions — adding a new tool requires only writing a Python function — the library grows organically as the community identifies repeated failure modes.

### 2.4 Multi-Agent Delegation

Not all tasks are best solved by a single agent. OpenHands supports multi-agent collaboration through a special action type, `AgentDelegateAction`, which allows a running agent (the *orchestrator*) to hand off a subtask to a different specialist agent (the *delegate*). The orchestrator provides a task description and a context budget; the delegate runs to completion and returns its result to the orchestrator's event stream.

This mechanism enables, for example, a general-purpose coding agent with limited web-browsing capability to call a specialized web-browsing agent for research tasks that require navigating complex real-world websites. The architecture is recursive: delegates can themselves delegate further, allowing arbitrary compositions of specialists.

---

## 3. AgentHub: Community-Contributed Agents

OpenHands includes a hub of pre-implemented agents that serve as ready-to-use baselines and starting points for research.

**CodeActAgent** is the default generalist agent, built on the CodeAct framework (Wang et al., 2024a). At each step it either converses in natural language (to ask for clarification or confirmation) or executes code (Python, bash, or browser actions). Because it uses a general-purpose action space without task-specific prompt engineering, the same agent can be applied to software engineering tasks, web browsing tasks, and general question-answering tasks without modification. This generality is one of the paper's main claims, validated empirically across 15 benchmarks (§4).

**BrowsingAgent** is a dedicated web agent inspired by the WebArena baseline (Zhou et al., 2023a), enhanced with improved observations and actions from BrowserGym (Drouin et al., 2024). It serves as a simple yet effective baseline for web-task benchmarks.

**GPTSwarm Agent** integrates the GPTSwarm framework (Zhuge et al., 2024), which represents agent systems as optimizable graphs where nodes are operations and edges define communication paths. This design supports automatic optimization of both node behaviors and their coordination structure.

**Micro Agents** are lightweight specializations of existing agents. A micro agent re-uses most of a generalist agent's implementation but applies a specialized prompt for a particular use case, lowering the barrier for practitioners to share task-specific configurations with the community.

---

## 4. Evaluation

### 4.1 Benchmark Suite

To track agent progress systematically, OpenHands integrates 15 established benchmarks organized into three categories:

| Category | Benchmarks |
|---|---|
| Software Engineering | SWE-Bench, HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA |
| Web Browsing | WebArena, MiniWoB++ |
| Miscellaneous Assistance | GAIA, GPQA, AgentBench, MINT, Entity Deduction Arena, ProofWriter |

The breadth is intentional: the same agent (CodeActAgent) is evaluated on all benchmarks without task-specific modifications, testing the claim that a software-centric action space generalizes across diverse tasks.

All comparisons in this section are against open-source reproducible baselines that do not perform manual prompt engineering specifically based on benchmark content.

### 4.2 Software Engineering Results

**SWE-Bench** (Jimenez et al., 2024) requires agents to resolve real-world GitHub issues (bug reports and feature requests) by modifying a code repository, after which automated tests verify correctness. The standard evaluation uses 300 instances from the "Lite" subset (the full 2,294-instance set costs roughly $6,900 at approximately $3 per instance). All results are reported without the optional "hint text" that provides natural language hints toward a solution.

| Agent | Model | SWE-Bench Lite (%) |
|---|---|---|
| SWE-Agent (Yang et al., 2024) | gpt-4-1106-preview | 18.0 |
| AutoCodeRover (Zhang et al., 2024b) | gpt-4-0125-preview | 19.0 |
| Aider (Gauthier) | gpt-4o & claude-3-opus | 26.3 |
| Moatless Tools (Örwall) | claude-3.5-sonnet | 26.7 |
| Agentless (Xia et al., 2024) | gpt-4o | 27.3 |
| **OH CodeActAgent v1.8** | gpt-4o-mini-2024-07-18 | **6.3** |
| **OH CodeActAgent v1.8** | gpt-4o-2024-05-13 | **22.0** |
| **OH CodeActAgent v1.8** | claude-3-5-sonnet | **26.0** |

The OpenHands CodeActAgent using claude-3-5-sonnet achieves 26.0%, competitive with specialized SWE systems, while using the same unmodified agent that is also deployed on web browsing and other tasks.

**HumanEvalFix** (Muennighoff et al., 2024) tests whether agents can fix bugs in Python functions when given failing test cases as feedback. OpenHands evaluates CodeActAgent in a zero-shot, multi-turn setting where the agent runs tests and iteratively debugs based on their output.

| Agent | Success Rate (%) |
|---|---|
| BLOOMZ-176B | 16.6 |
| OctoCoder-15B | 30.4 |
| DeepSeekCoder-33B-Instruct | 47.5 |
| StarCoder2-15B | 48.6 |
| SWE-Agent, 1-shot (Yang et al., 2024) | 87.7 |
| **OH CodeActAgent v1.5, 0-shot (gpt-3.5-turbo)** | **20.1** |
| **OH CodeActAgent v1.5, 0-shot (gpt-4o)** | **79.3** |

With GPT-4o, OpenHands achieves 79.3%, significantly outperforming all non-agentic approaches. The 87.7% of SWE-Agent uses a one-shot demonstration with a full example trajectory from the test set, while the OpenHands evaluation is zero-shot.

**BIRD** (Li et al., 2023b) evaluates text-to-SQL translation on realistic, large-scale database environments (300 instances from the dev set). OpenHands allows multi-turn execution: the agent can inspect SQL outputs and correct mistakes iteratively. OH CodeActAgent v1.5 with GPT-4o achieves 47.3%, compared to 18.3% for CodeLlama-7B-Instruct.

**ML-Bench** (Tang et al., 2024b) requires agents to solve machine learning tasks by generating bash or Python code across 18 GitHub repositories. OH CodeActAgent v1.5 with GPT-4o achieves 76.5%, compared to 42.6% for GPT-4o prompting alone and 64.4% for SWE-Agent.

**BioCoder** (Tang et al., 2024c) evaluates repository-level code generation for bioinformatics tasks. In the OpenHands evaluation, the original context (providing relevant code snippets) is deliberately removed to test the agent's ability to perform context retrieval on its own. OH CodeActAgent with GPT-4o achieves 27.5%.

**Gorilla APIBench** (Patil et al., 2023) tests whether agents can select the correct API call given a task description, covering TorchHub, TensorHub, and HuggingFace. OH CodeActAgent v1.5 with GPT-4o achieves 47.2% compared to 36.4% for the Gorilla fine-tuned LLaMA-7B.

**ToolQA** (Zhuang et al., 2024) tests tool use over diverse domains (flight data, restaurant reviews, etc.) using text, database, math, graph, and code tools. OH CodeActAgent v1.5 with GPT-4o achieves 43.1% on the easy subset, compared to 36.8% for ReAct (Yao et al., 2023) with GPT-3.

### 4.3 Web Browsing Results

**WebArena** (Zhou et al., 2023a) is a self-hosted, realistic web-browsing benchmark with 812 human-curated task instructions across domains including shopping, software forums, and content management systems. Agents must plan goal-directed sequences of browser interactions.

| Agent | Model | Success Rate (%) |
|---|---|---|
| Lemur (Xu et al., 2023) | Lemur-chat-70b | 5.3 |
| Patel et al. (2024) | Trained 72B (synthetic data) | 9.4 |
| AutoWebGLM (Lai et al., 2024) | Trained 7B | 18.2 |
| Auto Eval & Refine (Pan et al., 2024) | GPT-4 + GPT-4V | 20.2 |
| WebArena Agent (Zhou et al., 2023a) | gpt-4-turbo | 14.4 |
| **OH BrowsingAgent v1.0** | gpt-4o-mini | **8.5** |
| **OH BrowsingAgent v1.0** | gpt-4o | **14.8** |
| **OH BrowsingAgent v1.0** | claude-3-5-sonnet | **15.5** |
| **OH CodeActAgent v1.8** | gpt-4o | **14.5** |
| **OH CodeActAgent v1.8** | claude-3-5-sonnet | **15.3** |

OpenHands' BrowsingAgent achieves competitive performance among agents using domain-general prompting, including a 15.5% success rate with claude-3-5-sonnet. Notably, the general-purpose CodeActAgent (delegating to BrowsingAgent) achieves comparable performance, illustrating that the same agent architecture generalizes from code tasks to web tasks through delegation.

**MiniWoB++** (Liu et al., 2018) uses 125 synthetic minimalist web interfaces with built-in reward functions. Unlike WebArena, tasks are shorter and provide step-by-step directions, but a portion requires visual understanding. Results are reported on the full 125-environment set (some prior work reports on subsets only). OH BrowsingAgent with GPT-4o achieves 40.8%, and with delegation from CodeActAgent, 39.8%, compared to 34.6% for workflow-guided exploration (Liu et al., 2018) and 91.1% for a specialist model trained with reinforcement learning and human-annotated behavioral cloning (Humphreys et al., 2022).

### 4.4 Miscellaneous Assistance Results

**GAIA** (Mialon et al., 2023) evaluates general task-solving across 466 tasks requiring reasoning, multi-modal understanding, web browsing, and coding combined. OH GPTSwarm v1.0 achieves 32.1% on Level 1 of the validation set, compared to 13.2% for AutoGPT (Gravitas, 2023).

**GPQA** (Rein et al., 2023) tests agents on 198 "Google-proof" graduate-level science questions (the Diamond subset), where even human domain experts score 81.2% and non-expert PhDs average 21.9%. Tool use (Python execution, web search) is often essential since these questions require precise calculations and external knowledge beyond what is memorized by the LLM. Results across subsets:

| Agent | Diamond Set (%) | Main Set (%) | Extended Set (%) |
|---|---|---|---|
| Expert humans | 81.2 | 72.5 | 65.4 |
| Non-expert humans | 21.9 | 30.5 | 33.9 |
| Few-shot CoT, GPT-4 | 38.8 | 39.7 | 38.7 |
| GPT-4 + search | 38.8 | 41.0 | 39.4 |
| **OH CodeActAgent v1.8, claude-3-5-sonnet** | **52.0** | — | — |
| OH CodeActAgent v1.5, GPT-4o | 53.1 | 49.3 | 52.8 |

OpenHands CodeActAgent with GPT-4o achieves 53.1% on the Diamond subset, substantially exceeding GPT-4 chain-of-thought prompting (38.8%) by leveraging code execution for precise calculations.

**AgentBench** (Liu et al., 2023) tests multi-turn decision making in an OS bash environment (144 tasks). OH CodeActAgent with GPT-4o achieves 57.6%, compared to 42.4% for the AgentBench baseline with GPT-4.

**MINT** (Wang et al., 2024b) evaluates agents on math and coding challenges through multi-turn tool use with simulated natural language feedback (up to 5 interactions). On the math subset (225 instances), OH CodeActAgent with GPT-4o achieves 77.3% vs. 65.8% for the MINT baseline. On the code subset (136 instances), it achieves 50.0% vs. 59.6% for the baseline.

**ProofWriter** (Tafjord et al., 2021) evaluates 5-hop deductive reasoning over natural language (600 instances). OH CodeActAgent with GPT-4o achieves 78.8%, nearly matching Logic-LM (Pan et al., 2023) at 79.6% (which uses a symbolic solver) and well above pure chain-of-thought GPT-4 at 68.1%.

**Entity Deduction Arena** (Zhang et al., 2024a) tests strategic question-asking to identify unknown entities over multi-turn conversations (200 instances). OH CodeActAgent with GPT-4o achieves 38.0%, comparable to zero-shot GPT-4 at 40.0%.

### 4.5 Summary

Across all three categories, the most important finding is that a **single unmodified agent** — CodeActAgent — achieves competitive performance on software engineering, web browsing, and miscellaneous assistance benchmarks simultaneously. Purpose-built specialists (SWE-Agent for code, the WebArena Agent for web) often match or exceed it in their target domain, but they cannot be transferred. OpenHands' generalist agent pays a modest performance cost relative to specialists while achieving broad coverage, which is the right trade-off for a platform designed to serve as a general-purpose research infrastructure.

---

## 5. Quality Control and Testing

A noteworthy aspect of OpenHands as a software platform is its integration testing framework (Leung & White, 1990). Because agents are complex software systems where small bugs in prompt generation, message passing, or sandbox execution can silently degrade task performance, relying only on end-to-end benchmark evaluations (which cost hundreds to thousands of dollars per run) is impractical for routine development. Running a SWE-Bench Lite evaluation with GPT-4o costs approximately $600.

OpenHands addresses this with an **end-to-end agent test framework** that intercepts all LLM calls and replaces them with stored, pre-recorded responses matched to exact prompt strings. This converts inherently stochastic agent behavior into deterministic test execution, allowing:

- **Prompt regression testing**: Any change to a prompt that modifies LLM behavior triggers a test failure, surfacing unintended regressions before they affect benchmark results.
- **Multi-platform coverage**: Tests run automatically on every pull request across Linux and macOS, in local, SSH, and Docker execution modes.
- **Error localization**: The framework captures failures in prompt construction, action parsing, message passing, and sandbox execution separately, making it easier to identify root causes.

When new tests are added or prompts change substantially, stored prompt-response pairs are regenerated using real LLM calls; otherwise existing pairs are reused, keeping test costs low.

---

## 6. Related Work

The landscape of LLM-backed agent frameworks has grown rapidly. General-purpose systems include Auto-GPT (Gravitas, 2023), LangChain (Chase, 2022), MetaGPT (Hong et al., 2023), AutoGen (Wu et al., 2023), AutoAgents (Chen et al., 2024), and GPTSwarm (Zhuge et al., 2024). Software-engineering-specific systems include SWE-Agent (Yang et al., 2024), AutoCodeRover (Zhang et al., 2024b), and Agentless (Xia et al., 2024). Web-focused systems include OpenAgents (Xie et al., 2023).

OpenHands differentiates itself from all of these on two dimensions simultaneously: (a) it is the only system among those surveyed that combines a sandboxed code execution environment, a full web browser, a reusable tool library, multi-agent delegation, a graphical user interface, and an evaluation framework in a single open platform; and (b) it is community-driven and designed for extensibility, lowering the barrier for third-party agent contributions rather than optimizing a single agent for leaderboard performance.

---

## 7. Limitations and Future Work

The authors identify several open challenges. First, agents currently struggle with **long-file editing**: edits to large codebases often require the agent to load and process more context than LLMs handle reliably, suggesting that better file-editing strategies are needed. Second, **web browsing performance** remains substantially below human-level, partly because web tasks require precise low-level interactions (pixel coordinates, timing) and partly because long-horizon planning across many pages is difficult for current LLMs. Third, **multi-modal support** is currently handled through external model calls rather than natively through the agent's context, which introduces latency and limits integration. Fourth, **automatic workflow generation** — moving from handcrafted agent pipelines toward learned or optimized workflows — is identified as a promising future direction, with graph-based frameworks like GPTSwarm (Zhuge et al., 2024) as one candidate approach.

The authors also note that OpenHands agents, like all current LLM-backed agents, still struggle with complex long-horizon tasks and cannot yet reliably handle them in high-stakes production settings.

---

## 8. Conclusion

OpenHands is a community-driven open platform for building and evaluating AI agents that interact with the world through software. Its core insight is that programming languages provide a universal, expressive, and maintainable action space for AI agents: an agent that can write and execute code can accomplish nearly any digital task. The platform's architecture — event-stream-based agent abstraction, Docker-sandboxed runtime, extensible skills library, and multi-agent delegation — translates this insight into a practical research infrastructure.

The evaluation across 15 benchmarks demonstrates that a single generalist agent using this software-centric action space achieves competitive performance across software engineering, web browsing, and general assistance tasks without per-task customization. Key results include a 26% resolve rate on SWE-Bench Lite, 52% accuracy on GPQA Diamond, and 15.5% task success on WebArena — all with the same unmodified CodeActAgent.

By releasing OpenHands under a permissive MIT license and building it with community contributions from the start, the authors aim to make this platform a shared foundation for the research community to push the frontiers of agentic AI.

---

## References

Boiko, D. A., MacKnight, R., Kline, B., and Gomes, G. Autonomous chemical research with large language models. *Nature*, 624(7992):570–578, 2023.

Chase, H. LangChain, October 2022.

Chen, G., Dong, S., Shu, Y., Zhang, G., Sesay, J., Karlsson, B. F., Fu, J., and Shi, Y. Autoagents: A framework for automatic agent generation, 2024.

Drouin, A., Gasse, M., Caccia, M., Laradji, I. H., Del Verme, M., Marty, T., Boisvert, L., Thakkar, M., Cappart, Q., Vazquez, D., Chapados, N., and Lacoste, A. Workarena: How capable are web agents at solving common knowledge work tasks?, 2024.

Gauthier, P. How aider scored sota 26.3% on swe bench lite | aider.

Gravitas, S. Auto-GPT: An autonomous GPT-4 experiment, 2023.

Hong, S., Zhuge, M., Chen, J., Zheng, X., Cheng, Y., Wang, J., Zhang, C., Wang, Z., Yau, S. K. S., Lin, Z., et al. MetaGPT: Meta programming for a multi-agent collaborative framework. In *ICLR*, 2023.

Humphreys, P. C., Raposo, D., Pohlen, T., Thornton, G., Chhaparia, R., Muldal, A., Abramson, J., Georgiev, P., Santoro, A., and Lillicrap, T. A data-driven approach for learning to control computers. In *ICML*, pp. 9466–9482, 2022.

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. R. SWE-bench: Can language models resolve real-world GitHub issues? In *ICLR*, 2024.

Lai, H., Liu, X., Iong, I. L., Yao, S., Chen, Y., Shen, P., Yu, H., Zhang, H., Zhang, X., Dong, Y., et al. AutoWebGLM: Bootstrap and reinforce a large language model-based web navigating agent, 2024.

Leung, H. K. N. and White, L. J. A study of integration testing and software regression at the integration level. In *ICSM*, pp. 290–301, 1990.

Li, J., Hui, B., Qu, G., Yang, J., Li, B., Li, B., Wang, B., Qin, B., Geng, R., Huo, N., et al. Can LLM already serve as a database interface? A BIg bench for large-scale database grounded text-to-SQLs. In *NeurIPS Datasets and Benchmarks Track*, 2023b.

Liu, E. Z., Guu, K., Pasupat, P., Shi, T., and Liang, P. Reinforcement learning on web interfaces using workflow-guided exploration. In *ICLR*, 2018.

Liu, X., Yu, H., Zhang, H., Xu, Y., Lei, X., Lai, H., Gu, Y., Ding, H., Men, K., Yang, K., et al. AgentBench: Evaluating LLMs as agents, 2023.

Mialon, G., Fourrier, C., Swift, C., Wolf, T., LeCun, Y., and Scialom, T. GAIA: A benchmark for general AI assistants. *CoRR*, abs/2311.12983, 2023.

Muennighoff, N., Liu, Q., Zebaze, A., Zheng, Q., Hui, B., Zhuo, T. Y., Singh, S., Tang, X., von Werra, L., and Longpre, S. OctoPack: Instruction tuning code large language models, 2024.

OpenAI, Achiam, J., et al. GPT-4 technical report, 2024.

Pan, J., Zhang, Y., Tomlin, N., Zhou, Y., Levine, S., and Suhr, A. Autonomous evaluation and refinement of digital agents, 2024.

Pan, L., Albalak, A., Wang, X., and Wang, W. Y. Logic-LM: Empowering large language models with symbolic solvers for faithful logical reasoning, 2023.

Patil, S. G., Zhang, T., Wang, X., and Gonzalez, J. E. Gorilla: Large language model connected with massive APIs, 2023.

Patel, A., Hofmarcher, M., Leoveanu-Condrei, C., Dinu, M.-C., Callison-Burch, C., and Hochreiter, S. Large language models can self-improve at web agent tasks, 2024.

Rein, D., Hou, B. L., Stickland, A. C., Petty, J., Pang, R. Y., Dirani, J., Michael, J., and Bowman, S. R. GPQA: A graduate-level Google-proof Q&A benchmark, 2023.

Tafjord, O., Dalvi, B., and Clark, P. ProofWriter: Generating implications, proofs, and abductive statements over natural language. In *Findings of ACL-IJCNLP 2021*, 2021.

Tang, X., Jin, Q., Zhu, K., Yuan, T., Zhang, Y., Zhou, W., Qu, M., Zhao, Y., Tang, J., Zhang, Z., et al. Prioritizing safeguarding over autonomy: Risks of LLM agents for science, 2024a.

Tang, X., Liu, Y., Cai, Z., Shao, Y., Lu, J., Zhang, Y., Deng, Z., Hu, H., An, K., Huang, R., et al. ML-Bench: Evaluating large language models and agents for machine learning tasks on repository-level code, 2024b.

Tang, X., Qian, B., Gao, R., Chen, J., Chen, X., and Gerstein, M. B. BioCoder: A benchmark for bioinformatics code generation with large language models. *Bioinformatics*, 40(Supplement_1):i266–i276, 2024c.

Wang, X., Chen, Y., Yuan, L., Zhang, Y., Li, Y., Peng, H., and Ji, H. Executable code actions elicit better LLM agents. In *ICML*, 2024a.

Wang, X., Wang, Z., Liu, J., Chen, Y., Yuan, L., Peng, H., and Ji, H. MINT: Evaluating LLMs in multi-turn interaction with tools and language feedback. In *ICLR*, 2024b.

Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., Li, B., Jiang, L., Zhang, X., and Wang, C. AutoGen: Enabling next-gen LLM applications via multi-agent conversation framework, 2023.

Xia, C. S., Deng, Y., Dunn, S., and Zhang, L. Agentless: Demystifying LLM-based software engineering agents, 2024.

Xie, T., Zhou, F., Cheng, Z., Shi, P., Weng, L., Liu, Y., Hua, T. J., Zhao, J., Liu, Q., Liu, C., et al. OpenAgents: An open platform for language agents in the wild, 2023.

Xu, Y., Su, H., Xing, C., Mi, B., Liu, Q., Shi, W., Hui, B., Zhou, F., Liu, Y., Xie, T., et al. Lemur: Harmonizing natural language and code for language agents, 2023.

Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., and Press, O. SWE-agent: Agent-computer interfaces enable automated software engineering, 2024.

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. R., and Cao, Y. ReAct: Synergizing reasoning and acting in language models. In *ICLR*, 2023.

Yuan, L., Chen, Y., Wang, X., Fung, Y. R., Peng, H., and Ji, H. CRAFT: Customizing LLMs by creating and retrieving from specialized toolsets, 2023.

Zhang, Y., Lu, J., and Jaitly, N. Probing the multi-turn planning capabilities of LLMs via 20 question games, 2024a.

Zhang, Y., Ruan, H., Fan, Z., and Roychoudhury, A. AutoCodeRover: Autonomous program improvement, 2024b.

Zhou, S., Xu, F. F., Zhu, H., Zhou, X., Lo, R., Sridhar, A., Cheng, X., Ou, T., Bisk, Y., Fried, D., et al. WebArena: A realistic web environment for building autonomous agents. In *ICLR*, 2023a.

Zhuang, Y., Yu, Y., Wang, K., Sun, H., and Zhang, C. ToolQA: A dataset for LLM question answering with external tools. In *NeurIPS*, 2024.

Zhuge, M., Wang, W., Kirsch, L., Faccio, F., Khizbullin, D., and Schmidhuber, J. Language agents as optimizable graphs, 2024.

Örwall, A. Moatless tools.
