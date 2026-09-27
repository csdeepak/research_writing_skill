# Objective

## Paper being communicated

**Title:** OpenHands: An Open Platform for AI Software Developers as Generalist Agents  
**Authors:** Xingyao Wang et al.  
**Venue:** ICLR 2025  
**arXiv:** 2407.16741v3

## What this paper contributes

**Primary contribution:** A unified, open-source platform (OpenHands) that provides the shared infrastructure needed to develop and evaluate generalist AI agents that interact with the world through software interfaces.

**Secondary contributions:**
1. An event-stream architecture that cleanly separates agent logic from execution
2. A Docker-sandboxed runtime enabling safe execution of agent-generated code
3. An extensible AgentSkills tool library
4. Multi-agent delegation
5. An evaluation framework integrating 15 benchmarks

**Key empirical finding:** A single generalist agent (CodeActAgent), without task-specific modification, achieves competitive performance across three distinct task categories: software engineering (26.0% on SWE-Bench Lite), web interaction (15.5% on WebArena), and general assistance (52.0% on GPQA diamond), demonstrating that code-based action spaces support genuine generality.

## Contribution statement (one sentence)

OpenHands demonstrates that a unified open platform with a code-based action space enables a single generalist agent to achieve competitive performance across software engineering, web browsing, and general-assistance benchmarks, while providing the community with shared infrastructure for reproducible agent research.

## What the paper does NOT claim

- That OpenHands agents achieve state-of-the-art on any individual benchmark
- That code-based actions are superior to alternative action spaces on all tasks
- That the platform guarantees safety in production deployments
- Results with statistical significance guarantees (no variance reported)

## Open issues (accepted risks in this run)

- No variance estimates: individual run results; reader should weight gaps of <5% accordingly
- Literature mode limited to works cited in paper.txt (no web access)
- Step 18 (blind review) performed externally
