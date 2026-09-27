# Audience Profile

**Mode:** B — Adjacent researcher

**Primary audience:** Machine-learning researchers from subfields other than AI agents or software engineering automation. They are familiar with:
- Large language models (LLMs) and transformer architectures
- Standard ML evaluation practice (benchmarks, train/val/test, metrics)
- Basic concepts from reinforcement learning (agents, environments, actions, observations) at a conceptual level
- General software engineering concepts (APIs, code execution, version control) at a user level
- Docker containers at a conceptual level

**They are NOT familiar with:**
- SWE-Bench, WebArena, HumanEvalFix, GPQA, GAIA, or other domain-specific evaluation benchmarks
- The CodeAct framework or agent-computer interface (ACI) design
- The specific technical challenges of building sandboxed agent runtimes
- The existing landscape of agent frameworks (AutoGPT, LangChain, SWE-Agent, etc.) and their limitations

**Secondary audience:** Systems researchers interested in evaluation infrastructure; ML practitioners choosing an agent framework.

**Binding persona for evaluation:** An NLP researcher who has worked with LLM prompting and fine-tuning, understands that "agentic" means multi-step tool use, but has not built or evaluated a software engineering agent before. They are reading to understand whether this work is relevant to their own research and what the state of the art is.

**Explanation depth required:** Define all benchmarks on first use; explain evaluation metrics; connect to concepts the audience already knows (e.g., "like a gym environment, but the agent writes code instead of choosing from a fixed action set").
