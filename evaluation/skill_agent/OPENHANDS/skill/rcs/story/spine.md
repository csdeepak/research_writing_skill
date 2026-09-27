# Paper Spine — OpenHands

**Problem:** AI agents powered by LLMs are increasingly capable of performing complex real-world tasks, but building, evaluating, and comparing them remains fragmented across incompatible frameworks with limited reproducibility and safety guarantees.

**Gap:** Existing agent frameworks either target narrow domains (e.g., pure software engineering) or lack the infrastructure for safe code execution, systematic multi-benchmark evaluation, and modular extensibility that generalist agent research requires.

**Question:** Can a unified, open platform provide the shared infrastructure — event-stream abstraction, sandboxed runtime, extensible skills, and a broad evaluation suite — needed to develop and assess generalist AI agents that act through software?

**Approach:** OpenHands provides (1) an event-stream architecture that decouples agent logic from environment, (2) a Docker-sandboxed runtime supporting code execution and web browsing, (3) an extensible AgentSkills library, (4) multi-agent delegation, and (5) a framework integrating 15 established benchmarks.

**Key finding:** The platform's generalist CodeActAgent, using code as its primary action modality and without task-specific modification, achieves competitive results across software engineering (26.0% on SWE-Bench Lite), web interaction (15.5% on WebArena), and general assistance (52.0% on GPQA diamond) — spanning task categories that specialist baselines address individually. {C003}{C005}{C006}

**Meaning:** Software-grounded action spaces provide a flexible and powerful interface for general-purpose agents; open, multi-benchmark platforms are a necessary infrastructure for measuring and advancing agent generality. {C001}{C007}

**Main limit:** Results lack variance estimates; generality is demonstrated but not systematically compared to a single agent trained or fine-tuned on all benchmarks; long-file editing and automated workflow generation remain open challenges. {C010}
