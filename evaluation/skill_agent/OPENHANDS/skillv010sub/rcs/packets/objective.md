In the authors' words, this paper is meant to explain what OpenHands is and what its evaluation
shows: an open-source platform that lets a large-language-model agent act on the world the way a
human developer does -- writing and running code, using a command line, and browsing the web --
inside a safe, sandboxed environment, with an extensible library of task-specific tools and the
ability for agents to hand off subtasks to one another. The paper asks whether a single
generalist agent built on this platform, using one fixed prompt with no per-benchmark tuning,
can remain competitive across three very different kinds of task -- software engineering, web
browsing, and a range of other reasoning and tool-use problems -- rather than needing a separate,
purpose-built agent for each. A reader should come away understanding: what the platform actually
provides (an event-stream interface, a sandboxed action space, an agent-computer interface, and a
15-benchmark evaluation harness); the headline pattern in the results (the same agent design is
usually competitive, and occasionally not, across all three task categories, while every
comparison system it is measured against appears in only one category); and the specific,
disclosed boundaries on that finding (no statistical replication, no backbone-model-controlled
comparison, several benchmarks where the agent is not the top performer, no ablation isolating
which part of the platform matters, and a version of the platform that has since been superseded
by a later, restructured system).
