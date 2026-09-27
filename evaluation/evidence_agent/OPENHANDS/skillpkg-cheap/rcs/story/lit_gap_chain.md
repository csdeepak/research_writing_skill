# Literature -> Gap -> Question chain

DIMENSION: task-specific agent systems (SWE-Agent, AutoCodeRover, Aider for software engineering;
WebArena Agent [SRC-001] for web browsing; GPTSwarm for general assistant tasks) as named in the
evidence package's benchmark tables (E009-E011, E020, E022).
  ACHIEVES: each reaches non-trivial performance on its own narrow benchmark family (e.g., Aider
    26.3% on SWE-Bench Lite, E011; WebArena Agent 6.2% with gpt-3.5-turbo, E020).
  SHARED PATTERN (as documented in the evidence): each is evaluated with its own harness on its
    own benchmark family; the evidence package does not show any of them evaluated, unmodified,
    across software engineering, web browsing, and miscellaneous-assistance tasks together.
  EVIDENCE OF THE GAP: the evidence package itself frames OpenHands' contribution as integrating
    15 benchmarks under one platform (E030, C011) and evaluating one generalist agent across three
    task categories without prompt modification (E041, C006) -- implying, in the authors' own
    framing, that this cross-domain, single-harness evaluation was not already standard practice.
  UNRESOLVED: whether a single open platform and a single generalist agent configuration can
    still produce measurable, interpretable results across such different domains, and how much
    those results depend on the backend LLM.
GAP (scoped): among the systems and benchmark tables named in this evidence package, none is
  shown evaluated across all three task categories through one open, common agent interface.
QUESTION: RQ1 = "Can one open platform with a common agent-action interface host a single
  generalist agent that is evaluated, without per-domain prompt changes, across software
  engineering, web browsing, and miscellaneous-assistance tasks, reaching measurable performance
  in each?"

Chain rule note: because literature mode had no web access and only one verifiable citation
string exists in the evidence (`SRC-001`), the "achieves" and "shared pattern" parts above rest on
the evidence package's own benchmark tables rather than on ≥2 independently retrieved sources.
This is recorded as an accepted risk (`INSUFFICIENT_LITERATURE`) in `.rcs/state.json`. The GAP
statement is worded as scoped to "the systems named in the available evidence", not as a
systematic-search claim, and no "first/novel/unprecedented" language is used in the draft.
