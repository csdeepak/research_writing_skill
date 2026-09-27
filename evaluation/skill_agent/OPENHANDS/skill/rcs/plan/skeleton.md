# Paper Skeleton — OpenHands

## Title
OpenHands: An Open Platform for Building and Evaluating Generalist AI Software Agents

## Abstract
[One paragraph: problem + gap + approach + 3 key results + main limit]

## 1. Introduction
- AI agents powered by LLMs are being applied to complex real-world tasks including coding, web browsing, and scientific research, but the ecosystem is fragmented. {C001}
- Human developers interact with the world primarily through software: code, command line, and browser — this is the interface space where agents can be most powerful. {C007}
- Existing frameworks target narrow domains or lack safe execution infrastructure and systematic evaluation. {C001}
- We introduce OpenHands: a unified platform with event-stream architecture, Docker-sandboxed runtime, extensible skills, multi-agent delegation, and 15-benchmark evaluation. {C001}{C009}
- Contributions: (1) the platform architecture, (2) the agent hub including CodeActAgent, (3) evaluation across 15 benchmarks showing one generalist agent achieves competitive performance across three task categories. {C003}{C005}

## 2. Background and Motivation
- LLM agents act by perceiving environment state and selecting actions; this paper-loop mirrors RL but with language models as policy. {C007}
- Software as an action space: code is Turing-complete and can express any computation, making it a universal interface for tool use. {C007}
- Prior work comparison: AutoGPT, LangChain, MetaGPT, AutoGen, SWE-Agent — each addresses a subset; Table 1 comparison.
- The missing piece: no framework combines all of safe execution, extensibility, multi-agent, and multi-benchmark evaluation.

## 3. OpenHands Platform Architecture
### 3.1 Agent Abstraction and Event Stream
- Agent = step function: State → Action; State wraps a chronological event stream of actions and observations. {C007}
- Actions cover code execution (IPythonRunCell, CmdRun) and web browsing (BrowseInteractive), drawn from the CodeAct design.
- New agents are implemented by overriding the step function; minimal boilerplate. {C001}

### 3.2 Sandboxed Runtime
- Each session runs in an isolated Docker container with a bash shell, Jupyter IPython server, and Playwright browser. {C002}
- OpenHands installs its action execution API into arbitrary user-provided Docker images, enabling task-specific software environments.
- Hash-based image tagging ensures reproducibility. {C002}

### 3.3 AgentSkills: Extensible Tool Library
- AgentSkills is a Python package of utility functions automatically imported into the agent's IPython environment.
- Addition criterion: only when direct LLM code generation would fail or when an external model is required. {C001}
- Current skills: file editing, scrolling, PDF/image parsing via vision-language models.

### 3.4 Multi-Agent Delegation
- AgentDelegateAction lets a generalist agent hand off subtasks to specialists. {C008}
- Example: CodeActAgent delegates complex web browsing to BrowsingAgent. {C008}

## 4. Agent Hub
- Over 10 implemented agents; key ones: CodeActAgent (generalist, CodeAct-based), BrowsingAgent (web), GPTSwarm, Micro Agents.
- CodeActAgent's action space: converse, execute code/bash, browse — same prompt, zero-shot across tasks. {C005}

## 5. Evaluation Framework
- 15 benchmarks across three categories: software engineering, web browsing, miscellaneous assistance. {C009}
- Comparison principle: open-source reproducible baselines without manual prompt engineering.
- Cost note: SWE-Bench Lite with gpt-4o costs ~600 USD per full run. {E039}

## 6. Results
### 6.1 Software Engineering
- SWE-Bench Lite: CodeActAgent v1.8 (claude-3-5-sonnet) achieves 26.0%, competitive with Aider (26.3%) and Moatless Tools (26.7%). {C003}
- HumanEvalFix: 79.3% at 0-shot, nearly doubling StarCoder2-15B (48.6%); below SWE-Agent's 87.7% but that used 1-shot with demonstration. {C004}
- ML-Bench: 64.4% (gpt-4o), outperforming SWE-Agent (42.6%) on ML coding tasks. {E012}{E013}
- Additional: BIRD text-to-SQL 47.3%, BioCoder 27.5%, Gorilla APIBench 47.2%, ToolQA 43.1%. {E011}{E014}{E015}{E016}

### 6.2 Web Browsing
- WebArena: BrowsingAgent reaches 15.5% (claude-3-5-sonnet), comparable to WebArena Agent (14.4%) and AutoWebGLM (18.2%). {C005}{E017}{E019}{E020}
- MiniWoB++: BrowsingAgent reaches 40.8% (gpt-4o), versus specialist CC-NET at 91.1% (trained with RL + human annotation). {E021}

### 6.3 Miscellaneous Assistance
- GPQA diamond: CodeActAgent 52.0% with tool use vs GPT-4 few-shot CoT 38.8%; above non-expert humans (21.9%), below experts (81.3%). {C006}
- GAIA L1: GPTSwarm 32.1% vs AutoGPT 13.2%. {E026}{E027}
- AgentBench OS: 57.6% vs baseline 42.4%. {E028}{E029}
- MINT math: 77.3% vs baseline 65.8%. {E030}{E031}
- ProofWriter: 78.8% near Logic-LM (79.6%). {E032}{E033}

## 7. Discussion
- Generality finding: the same agent, unchanged, achieves competitive performance across three task categories. {C005}
- Tool use amplifies LLM capability: GPQA result shows agents with Python/search access substantially outperform non-agentic prompting. {C006}
- Design lessons: code as action space unifies diverse tools; sandbox enables safe iteration; extensibility lowers barrier to contribution.
- Limitations: no variance estimates; long-file editing struggles; workflows need manual design; transfer to production untested. {C010}

## 8. Related Work
- Agent frameworks: AutoGPT, LangChain, MetaGPT, AutoGen, XAgent, OpenAgents — general purpose but lacking sandboxed execution.
- Software engineering agents: SWE-Agent, AutoCodeRover, ChatDev, AgentCoder — domain-specific.
- Web browsing agents: AutoWebGLM, Reflexion-based approaches — narrow scope.
- OpenHands unifies all three, provides open evaluation infrastructure.

## 9. Conclusion
- OpenHands is a community-driven open platform that demonstrates a generalist agent can achieve competitive performance across software engineering, web browsing, and general assistance through a unified code-based action space.
- The platform, MIT-licensed with 32K stars and 188+ contributors, provides shared infrastructure for the field. {E034}
- Open challenges: safe long-horizon autonomy, automated workflow design, stronger training signals. {C010}
