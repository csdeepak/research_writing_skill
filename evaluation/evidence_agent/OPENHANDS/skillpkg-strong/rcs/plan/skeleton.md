# Research skeleton (one topic sentence per paragraph slot)

**I.1** Making an AI agent act usefully on real digital tasks — repairing code, browsing a
website, answering a research question with tools — requires wrapping a language model in a loop
that observes, acts, and repeats, plus the sandboxing and interfaces that loop needs {C017}.

**I.2** Building and evaluating such a loop is normally done separately for each task family, so
software-repair agents, web agents, and tool-use agents are compared within their own domains but
rarely against a single shared measurement of one agent across domains.

**I.3** This raises the question this paper addresses: can one general-purpose agent, unmodified
across domains, be evaluated end to end on software, web, and miscellaneous digital tasks through
a single open platform and harness?

**I.4** OpenHands answers this with an agent hub of more than ten implemented agents and an
evaluation framework integrating 15 established benchmarks across three task categories,
released under the MIT license {C017}.

**I.5** The paper's contributions, and its headline findings at their reported strength, are
listed, and the introduction closes with a map of the sections that follow.

**B.1** Before the results can be read, three conventions from this subfield are defined: the
agent loop, the "resolve rate" convention for repository-fix tasks, and the 0-shot/1-shot
distinction that affects comparability.

**B.2** The systems OpenHands is compared against fall into three families — non-agentic or
lightly agentic code-repair pipelines, domain-general prompted agents, and benchmark-trained
specialists — and each family's assumption is stated before results are shown {C001}{C009}{C010}.

**P.1** OpenHands itself is described concretely: the agent hub, the two agents used in the
reported results (CodeActAgent, BrowsingAgent), and the evaluation framework's structure.

**S.1** Each of the three evaluated categories is described with its benchmarks, instance counts,
and shot settings, so the results that follow can be read against a known setup.

**R.1** On software-engineering benchmarks, CodeActAgent reaches 26.0% on SWE-Bench Lite and
79.3% on HumanEvalFix, each interpreted against its nearest baselines and its shot setting
{C001}{C002}{C003}{C018}.

**R.2** On web-interaction benchmarks, BrowsingAgent reaches 15.5% on WebArena and 40.8% on
MiniWoB++, in both cases below systems built specifically for the benchmark {C009}{C010}.

**R.3** On miscellaneous-assistance benchmarks, OpenHands agents exceed their baseline on four of
six tasks (GAIA, GPQA, AgentBench OS, MINT-math, ProofWriter) and fall below it on two
(MINT-code, Entity Deduction Arena) {C004}-{C008}{C011}-{C013}{C020}.

**D.1** Read together, the three categories show a mixed rather than uniformly superior pattern,
which is interpreted as evidence for a shared, reusable platform rather than a single-benchmark
state-of-the-art claim {C014}{C015}.

**D.2** The authors' own stated next steps — closing the HumanEvalFix gap and reducing handcrafted
workflow engineering — are given as future directions, not results {C016}.

**L.1** The claims above are bounded by five things: no run has reported variance; two pairs of
numbers conflict in the source tables; some benchmark rows could not be safely attributed; budget
parity with baselines is not stated; and several comparisons cross training paradigms.

**C.1** The paper closes by restating, at its evidenced strength, what one general OpenHands agent
was shown to do across three digital-task categories, and what remains open.
