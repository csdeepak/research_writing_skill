# Literature -> Gap -> Question chain

```
DIMENSION: general-purpose orchestration frameworks (SRC-001 LangChain/LangGraph, SRC-002 AutoGen, SRC-003 CrewAI)
  ACHIEVES: composing LLM calls, tools, and multi-agent conversations {C021}
  SHARED ASSUMPTION: a basic runtime, or one narrow code-interpreter tool, is enough execution power
  EVIDENCE OF LIMIT: SRC-001 gives only "basic runtime support" (no full sandbox); SRC-002 executes Python/bash
    but "stateless"; SRC-003's code interpreter is explicitly "limited" -- 3 sources, each independently
    characterized in project/paper.txt's own Related Work section
  UNRESOLVED: none of the three adds a browser, a standardized/extensible tool library, or an evaluation harness

DIMENSION: single-capability specialist frameworks (SRC-004 BrowserGym, SRC-005 DSPy)
  ACHIEVES: excelling at one piece -- browsing (SRC-004) or prompt optimization (SRC-005) {C021}
  SHARED ASSUMPTION: that one piece is the bottleneck worth solving in isolation
  EVIDENCE OF LIMIT: SRC-004 "specifically targets web browsing capabilities"; SRC-005 "emphasizes end-to-end
    prompt optimization" -- 2 sources, neither offers a sandbox, tool library, delegation, or a multi-category
    evaluation harness
  UNRESOLVED: whether a platform built around one such piece could still reach the other four; no retrieved
    source in project/paper.txt combines more than two of the five pieces

DIMENSION: multi-agent collaboration-pattern frameworks (SRC-006 MetaGPT, SRC-007 GPTSwarm)
  ACHIEVES: standardized team procedures (SRC-006) or automatically optimizable agent graphs (SRC-007) {C021}
  SHARED ASSUMPTION: the main lever for better agent systems is the collaboration/optimization pattern among
    agents, not the underlying execution substrate each agent acts through
  EVIDENCE OF LIMIT: neither source is characterized in project/paper.txt as supplying its own sandboxed
    code/browser execution or a general tool library; OpenHands' own authors concede their own workflow
    construction is comparatively handcrafted next to GPTSwarm's optimizable graphs {L005}
  UNRESOLVED: whether a collaboration pattern like GPTSwarm's could be layered onto a platform like OpenHands
    (the paper names this as future work, not a solved problem) {L005}

DIMENSION: software-engineering-issue-fixing specialists (SRC-008 SWE-Agent, SRC-009 AutoCodeRover,
    SRC-010 Agentless, SRC-025 ChatDev, SRC-026 AgentCoder)
  ACHIEVES: strong, purpose-built performance on GitHub-issue resolution specifically -- 18.0%/19.0%/27.3% on
    SWE-Bench Lite for the three with reported numbers {C001}
  SHARED ASSUMPTION: a task-specific agent-computer interface (or search+edit pipeline) built for this one task
    family is the right unit of specialization
  EVIDENCE OF LIMIT: none of the five is evaluated, in project/paper.txt, on web-browsing or the miscellaneous-
    assistance benchmarks used in this paper; SRC-008's own point (a carefully crafted ACI matters) is taken up
    by OpenHands as a general-purpose, extensible tool library rather than a one-off interface {C034}
  UNRESOLVED: whether a generalist agent could match this specialism without being purpose-built for it -- this
    is exactly RQ2

GAP (scoped to project/paper.txt's own citations): "Among the frameworks project/paper.txt itself surveys and
  compares, none combines a general (not domain-specific) sandboxed code-and-browser runtime, a standardized
  and extensible tool library, multi-agent delegation, and an integrated evaluation harness in one open
  platform; and none of the SWE-issue specialists is shown operating competitively outside its own task family." {C021}
QUESTION: RQ1 = "Can one open platform supply, together, the pieces these frameworks provide only piecemeal?"
  RQ2 = "Can a single generalist agent built on it, with no per-benchmark modification, then perform
  competitively across software engineering, web browsing, and other assistance tasks?" {C013}
```

**Chain rules check.** The "achieves" and "shared assumption" parts each rest on >=2 sources except the
single-capability dimension (SRC-004, SRC-005), which is worded accordingly ("excelling at one piece") rather
than claiming a broader pattern from two sources alone. "Evidence of limit" in every dimension is a specific
sentence from project/paper.txt's own Related Work section (§C) characterizing that exact source, not an
inference. The GAP statement is explicitly scoped to "the frameworks project/paper.txt itself surveys and
compares" -- no "first," "novel," or "no prior work" wording is used, consistent with the no-web constraint
(a systematic search was not possible, so no search-scoped novelty claim is licensed).
