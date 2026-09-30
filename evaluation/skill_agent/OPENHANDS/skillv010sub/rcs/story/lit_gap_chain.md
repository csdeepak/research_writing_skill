# Literature -> Gap -> Question chain

```
DIMENSION: general-purpose open agent frameworks (SRC-003 AutoGen, SRC-004 LangChain/LangGraph,
           SRC-005 AutoGPT, SRC-006 MetaGPT)
  ACHIEVES: composable interaction/coordination abstractions for building LLM-driven agents {C019}
  SHARED ASSUMPTION: providing *an* interaction or execution primitive is the main engineering task;
    depth of that primitive (statefulness, sandboxing) is secondary
  EVIDENCE OF SHALLOWNESS: AutoGen adds Python/bash execution "though with stateless command
    execution" (SRC-003, as characterized in paper.txt Appendix C) -- 1 source, explicitly named
  UNRESOLVED: whether a persistent, safely sandboxed session plus a broad, ready-made cross-domain
    evaluation harness change what a generalist agent built on top can achieve (no retrieved source
    in project/paper.txt combines and tests this)

DIMENSION: specialized software-engineering agents (SRC-002 SWE-Agent, SRC-024 AutoCodeRover,
           SRC-025 Aider)
  ACHIEVES: strong, reproducible results on one benchmark family (SWE-Bench Lite: 18.0-26.7%) by
    pairing a carefully designed, task-specific Agent-Computer Interface with a fixed prompt {C018}
  SHARED ASSUMPTION: the interface and prompt should be optimized for the target task category
  EVIDENCE OF NARROWNESS: none of SRC-002/024/025 is evaluated, in project/paper.txt, on any
    benchmark outside the software-engineering category -- 3 sources, all absent from the web and
    miscellaneous-assistance tables (Tables 5-6)
  UNRESOLVED: whether a *single* agent design, without per-category tuning, can remain competitive
    once the task category changes

GAP (scoped to project/paper.txt's own citations and comparison tables): "Among the systems compared
  in project/paper.txt, general frameworks are characterized as providing execution/interaction
  primitives at limited depth (e.g. stateless execution), while the strongest single-category
  results come from agents built and prompted specifically for that category; no system in the
  comparison set is shown evaluated, with one fixed design, across software engineering, web
  browsing, and miscellaneous reasoning/tool-use tasks at once."

QUESTION (= story/story_graph.json node N05): "Can one open platform, and one generalist agent
  built on it with a single fixed prompt, remain competitive across software engineering, web
  browsing, and miscellaneous reasoning/tool-use tasks at once?"
```

## Chain rules check
- The "achieves" and "shared assumption" parts each rest on >=1 named source per dimension (2 and 3
  sources respectively), and both dimensions are drawn directly from the authors' own characterizations
  in project/paper.txt (Appendix C, §2.1, §2.3), not from outside knowledge.
- "Evidence of shallowness/narrowness" points to a specific, sourced statement in each case, not an
  unqualified "no prior work".
- The GAP statement is explicitly scoped to "the systems compared in project/paper.txt" -- it does not
  claim to have searched the wider literature (no web access in this run; see state.json AR005), and it
  is not phrased as "no prior work" or "first ever" (B1 anti-pattern).
- The QUESTION follows from the GAP: answering it (finding one platform/one agent competitive across
  categories) directly narrows the stated gap.
