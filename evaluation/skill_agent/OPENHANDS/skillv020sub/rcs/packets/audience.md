Intended readers: machine-learning researchers from subfields other than LLM agents or software-engineering agents -- for example, someone working on vision, RL theory, or NLP evaluation methodology who does not follow the agents literature specifically.

They can be assumed to know: supervised and instruction-tuned large language models (GPT-4, Claude, etc.); prompting and zero-/few-shot inference in the general in-context-learning sense; train/test and held-out evaluation splits; standard statistics and how to read a comparison table against baselines; the general notion of an "agent" that takes actions in an environment (e.g. from reinforcement learning); ordinary software-engineering vocabulary (a bug, a function, a repository) at a layperson-technical level.

They cannot be assumed to know: what SWE-Bench, HumanEvalFix, WebArena, MiniWoB++, GAIA, GPQA, AgentBench, MINT, ProofWriter, or the Entity Deduction Arena specifically measure; "resolve rate" or "pass rate" as benchmark-specific metrics; the agent-computer-interface (ACI) concept; event-stream agent architectures or action/observation terminology; code-execution ("CodeAct"-style) action spaces versus fixed JSON tool-calling; sandboxed/containerized execution as a safety mechanism; or the landscape of prior agent frameworks (LangChain, AutoGen, CrewAI, MetaGPT, GPTSwarm, BrowserGym, DSPy, SWE-Agent, AutoCodeRover, etc.).

Binding reader types for this review: B (adjacent researcher) as primary; A (specialist in this exact subfield) and E (mixed-audience venue) as secondary binding personas, since a paper that works for the primary mode should not fail an expert reader either.

Venue type: report (standalone research write-up; no specific venue was named for this piece).
