# OpenHands: An Open Platform for Running and Evaluating One Generalist Agent Across Coding, Web, and Reasoning Tasks

## Abstract

Systems that let a large language model act on real software interfaces - writing and running code, issuing shell commands, and browsing the web - are usually built and evaluated one benchmark family at a time, each with its own harness. This makes it hard to tell whether an agent's behavior is a property of the agent or of the harness it was tested in. We report on OpenHands, an open, MIT-licensed platform that gives agents a small, common action interface (running code, running a shell command, or interacting with a browser) and a reproducible, containerized runtime, and that integrates fifteen established benchmarks spanning software engineering, web browsing, and miscellaneous assistance tasks {C001,C011}. Using this platform, the same generalist agent, CodeActAgent (with a BrowsingAgent variant for web tasks), is evaluated without per-domain prompt changes across all three categories {C006}. On SWE-Bench Lite (300 real GitHub issues, no hint text), the agent reaches a 26.0% resolve rate with claude-3.5-sonnet, next to baselines up to 26.3% {C002}; the same setup with gpt-4o-mini reaches only 6.3%, a roughly four-fold difference driven entirely by the backend model {C003}. On the HumanEvalFix Python subset the agent fixes 79.3% of bugs zero-shot {C004}. On the 812-instance WebArena benchmark it reaches 8.5-15.5% depending on the backend model {C007}, and on the 198-question GPQA diamond set it reaches 52.0% accuracy, compared with 81.3% for expert humans {C008}. These results are consistent with a single, minimal agent interface being sufficient to obtain interpretable, cross-domain evaluation numbers, but the size of every number depends heavily on the underlying model, and most figures come from reduced-size benchmark subsets chosen for cost reasons {L001,L002}. As of writing, the project has attracted 32K GitHub stars and more than 2.1K contributions from over 188 contributors {C012}.

## 1. Introduction

Getting a large language model to do more than answer a question - to write code, run it, read the error, fix it, and then check a file, in a loop, on a real repository or a real website - requires infrastructure well beyond the model itself: an environment in which actions actually execute, a way to observe what happened, and a harness for each benchmark used to measure success. Building this infrastructure from scratch is expensive, and running it at benchmark scale is expensive again; a conservative per-instance estimate puts the cost of evaluating one agent configuration on the full 2,294-instance SWE-Bench suite at roughly $6.9k {C020}, which is one reason researchers often report on smaller, curated subsets rather than complete benchmarks. Throughout this paper, we use "agent" in the sense the underlying work uses it: not a reinforcement-learning policy, but a loop that observes the state of an environment and repeatedly chooses one action from a small, fixed set - here, running code, running a shell command, or interacting with a browser - until the task is judged done.

Several agent systems that operate this way already exist. Among the systems reported in the evidence available for OpenHands, SWE-Agent, AutoCodeRover, and Aider are each evaluated on SWE-Bench Lite, a 300-instance benchmark of real GitHub issues, and the WebArena Agent (Zhou et al., 2023a) is evaluated on WebArena, an 812-instance benchmark of web tasks {C001}. Each of these systems is paired with its own benchmark harness, built to test that system on that benchmark family. What is not shown, within this evidence, is any one of these systems evaluated - without per-domain changes to its prompt or design - across software-engineering, web-browsing, and general-assistance tasks together, inside a single open framework that other researchers could reuse for a different agent or a different benchmark.

This raises a question that adjacent-field readers can recognize by analogy: it is the same question a shared benchmark suite (like GLUE for language understanding) answers for a family of tasks, but asked of the agent's *action interface* rather than of a fixed input-output format. Concretely: can one open platform, exposing a small common action interface, host a single generalist agent - one that is not re-prompted or re-designed per domain - and produce measurable, reportable performance across software-engineering, web-browsing, and miscellaneous-assistance tasks?

OpenHands answers this with a platform built around three pieces. First, a minimal agent-action abstraction: an OpenHands agent can only run code, run a shell command, or interact with a browser {C001}. Second, a containerized runtime that uses a dual-tagging scheme - a hash-based tag that pins an exact, reproducible environment and a generic tag that tracks the latest version - to balance reproducibility with day-to-day flexibility {C018}, together with an integration-test framework that mocks LLM calls against exact prompt matches so the platform's own behavior can be checked deterministically, without paying for live model calls on every test run {C019}. Third, harnesses for fifteen established benchmarks, split by the platform's own accounting into seven software-engineering benchmarks, two web-browsing benchmarks, and six miscellaneous-assistance benchmarks {C011}.

The contribution we report on is this combination: an open, MIT-licensed platform with a common action interface and a reproducible runtime, demonstrated by running one generalist agent, CodeActAgent, and a browsing variant of it, across all fifteen benchmarks without per-domain prompt modification {C001,C011,C012}. The rest of the paper follows the same order the evidence itself uses to organize results. Section 2 places OpenHands next to the narrower systems named in the available evidence. Section 3 describes the platform's action interface, runtime, and testing approach. Section 4 describes the shared evaluation setup. Section 5 reports results in the three task categories in turn - software engineering, web browsing, and miscellaneous assistance - and Section 6 discusses what these results do and do not establish, followed by the limitations that bound them.

## 2. Related Work

The evidence available for this paper names four systems for comparison, each evaluated on one benchmark family. On SWE-Bench Lite, SWE-Agent with gpt-4-1106-preview reaches an 18.0% resolve rate, AutoCodeRover with gpt-4-0125-preview reaches 19.0%, and Aider with gpt-4o and claude-3-opus reaches 26.3% - the strongest of the three baselines reported. On WebArena, the WebArena Agent (Zhou et al., 2023a) with gpt-3.5-turbo reaches 6.2%. Table 1 collects these baselines as they appear in the evidence.

**Table 1. Baseline systems named in the available evidence.**

| System | Benchmark | Model | Score |
|---|---|---|---|
| SWE-Agent | SWE-Bench Lite (300 instances) | gpt-4-1106-preview | 18.0% |
| AutoCodeRover | SWE-Bench Lite (300 instances) | gpt-4-0125-preview | 19.0% |
| Aider | SWE-Bench Lite (300 instances) | gpt-4o & claude-3-opus | 26.3% |
| WebArena Agent (Zhou et al., 2023a) | WebArena (812 instances) | gpt-3.5-turbo | 6.2% |

Each of these systems is reported next to a single benchmark family, with a harness purpose-built for it. This is a reasonable design when the research question is about the agent itself, but it means that comparing agents across domains, or reusing the harness for a new benchmark, requires new integration work each time. What the available evidence attributes to OpenHands instead is a platform-level choice: build one action interface and one runtime, then attach benchmark harnesses to it, so that the same generalist agent can be pointed at any of them {C001,C011}. We are not aware, from this evidence alone, of a prior system evaluated this way across all three task categories; we therefore scope our framing of this gap to the systems named in the available evidence rather than to a claim about the field as a whole.

## 3. The OpenHands Platform

**Action interface.** An OpenHands agent is a loop: at each step it observes the current state of its environment and emits exactly one action, chosen from a small fixed set, rather than free-form text describing what it would like to happen. The evidence documents three such action types: running a cell of code, running a shell command, and interacting with a browser {C001}. Restricting the agent to a small, typed action set is what allows the platform to log, replay, and score an agent's behavior the same way regardless of which underlying language model is driving it, and it is what allows the same agent implementation to be pointed at a coding benchmark one day and a web benchmark the next, without redesigning the interface between the model and the world.

**Runtime.** Each benchmark run needs an environment - a container with the right filesystem state, tools, and network access - that can be recreated later. OpenHands' runtime addresses this with a dual-tagging system for its container images: a hash-based tag that fixes an exact image for reproducing a specific run, and a generic tag that always points at the current, most up-to-date image for everyday use {C018}. This lets a researcher reproduce a past evaluation exactly (using the hash-based tag) while still being able to develop against the newest platform version day to day (using the generic tag).

**Quality control.** Running an agent against a live model on every code change would be slow and expensive. The platform's integration-test framework instead intercepts LLM calls and returns predefined responses keyed to exact prompt matches, so that platform behavior can be checked deterministically and repeatedly without incurring model costs on each test {C019}. This is a software-engineering choice about the platform itself, not about the agents it evaluates, but it is one of the pieces that makes the fifteen-benchmark evaluation in Section 5 practical to maintain.

**Benchmark integration.** The platform integrates fifteen established benchmarks, organized into three categories: seven in software engineering, two in web browsing, and six in miscellaneous assistance {C011}. Table 2 summarizes this organization; the specific benchmarks within each category are introduced where their results appear in Section 5.

**Table 2. Benchmark categories integrated into OpenHands.**

| Category | Number of benchmarks | Example benchmarks (Section 5) |
|---|---|---|
| Software engineering | 7 | SWE-Bench Lite, HumanEvalFix |
| Web browsing | 2 | WebArena, MiniWoB++ |
| Miscellaneous assistance | 6 | GPQA, MINT, ProofWriter |

## 4. Experimental Setup

The evaluation reported here uses one agent configuration, CodeActAgent, across the software-engineering and miscellaneous-assistance benchmarks, and a BrowsingAgent variant of the same design across the two web-browsing benchmarks; in both cases the same system prompt is used across every benchmark within its category, without per-benchmark tuning {C006}. This is the design choice the rest of the paper depends on: because the agent is not re-prompted per domain, a difference in score between benchmarks is more informative about the benchmark and the backend model than it would be if the agent had also been redesigned each time.

Several benchmarks in the evidence are evaluated on reduced-size subsets rather than in full - for example, SWE-Bench Lite's 300 instances rather than the full SWE-Bench's 2,294, and MINT's math and code splits at 225 and 136 instances respectively. The evidence gives a concrete reason for at least one of these choices: a conservative estimate puts the cost of running the full SWE-Bench suite at approximately $6.9k per full evaluation, which motivates evaluating on a smaller, still-substantial subset instead {C020}. Where a benchmark modification changes what is being tested, we say so explicitly: for BIRD, a text-to-SQL benchmark, the evidence records that the authors extended the usual single-turn setting to allow the agent multiple turns, so it can revise a SQL query using execution feedback rather than submitting a single guess {C017}. We report this modification because it changes the comparison being made, even though we do not have baseline numbers under the original single-turn setting for a direct comparison.

## 5. Results

We report results in the same three categories the platform itself uses to organize its fifteen benchmarks, in the order software engineering, web browsing, and miscellaneous assistance, and we return in Section 6 to what these three categories jointly show about a single generalist agent.

### 5.1 Software engineering

On SWE-Bench Lite - 300 real GitHub issues, evaluated without hint text - CodeActAgent v1.8 reaches a 26.0% resolve rate when backed by claude-3.5-sonnet {C002}. The same agent configuration, changing only the backend model, reaches 22.0% with gpt-4o and 6.3% with gpt-4o-mini {C003}. Measured against the baselines in Table 1, the claude-3.5-sonnet configuration sits just below Aider's 26.3% and above AutoCodeRover's 19.0% and SWE-Agent's 18.0%; the gpt-4o-mini configuration falls well below all three. The gap between the strongest and weakest backend model on the identical agent and benchmark - 26.0% versus 6.3%, a difference of 19.7 percentage points - is not a property of the agent's design, since the design did not change; it is a property of which language model the agent is built on {C003}. We report this negative result for gpt-4o-mini explicitly, rather than only the best configuration, because it bears directly on how the "same agent, different domains" claim in Section 6 should be read: the platform makes cross-domain, cross-model comparison possible, but it does not remove the underlying models' capability differences.

**Table 3. Software-engineering benchmark results (CodeActAgent).**

| Benchmark | Instances | Model | Score |
|---|---|---|---|
| SWE-Bench Lite | 300 | claude-3.5-sonnet | 26.0% |
| SWE-Bench Lite | 300 | gpt-4o-2024-05-13 | 22.0% |
| SWE-Bench Lite | 300 | gpt-4o-mini | 6.3% |
| HumanEvalFix (Python) | 164 | generalist agent, 0-shot | 79.3% |
| BIRD (text-to-SQL, multi-turn) | 300 | gpt-4o | 76.5% |
| ML-Bench | 68 | gpt-4o | 29.7% |
| BioCoder (Python) | 157 | gpt-4o | 27.5% |
| Gorilla APIBench | 1,775 | gpt-4o | 47.2% |
| ToolQA (easy) | 800 | gpt-4o | 36.4% |

On the HumanEvalFix Python subset (164 instances), CodeActAgent v1.5 fixes 79.3% of bugs using a zero-shot, multi-turn setup in which the agent debugs its own attempted fix across several turns rather than being shown a worked example first {C004}. The evidence describes this figure as better than non-agentic approaches to the same task and close to double the pass rate of a specific non-agentic baseline, StarCoder2-15B, though the evidence package used for this paper does not include StarCoder2-15B's own logged score, so we report this comparison at the confidence the evidence supports - as the authors' own characterization - rather than as an independently verified number {C005}. HumanEvalFix's scoring allows a maximum of 100%, so 79.3% reflects a remaining capability gap rather than a ceiling imposed by the benchmark itself {L005}. Table 3 also lists results on BIRD, ML-Bench, BioCoder, Gorilla APIBench, and ToolQA, which round out the seven software-engineering benchmarks; scores on these range from 27.5% (BioCoder) to 76.5% (BIRD), reflecting how much the task itself - fixing a bug, writing a correct SQL query, or calling the right API among 1,775 candidates - shapes what a given resolve or accuracy rate means, more than any single number can convey on its own.

### 5.2 Web browsing

On WebArena - 812 instances of realistic web tasks, evaluated zero-shot with domain-general prompting rather than prompting tuned to WebArena specifically - BrowsingAgent v1.0 reaches 8.5% with gpt-4o-mini, 14.8% with gpt-4o, and 15.5% with claude-3.5-sonnet {C007}. As in the software-engineering results, the gap here is between backend models on an unchanged agent design, and it is smaller in absolute terms (8.5-15.5%, a 7-point range) than the SWE-Bench Lite gap, though the WebArena Agent baseline (Zhou et al., 2023a) with gpt-3.5-turbo reaches only 6.2%, below all three BrowsingAgent configurations. On the MiniWoB++ full evaluation set - 125 environments, including a portion that requires visual (not just textual) interpretation of the page to solve - BrowsingAgent v1.0 with gpt-4o reaches 40.8% {C007}. Because this figure spans the full environment set rather than a text-only subset that some other evaluations report, part of the 40.8% figure reflects the agent's ability to handle vision-dependent tasks, and this should be kept separate from its ability to plan and execute browsing actions in the text-only environments {L006}. Table 4 lists all five web-browsing figures together.

**Table 4. Web-browsing benchmark results (BrowsingAgent).**

| Benchmark | Instances | Model | Score |
|---|---|---|---|
| WebArena | 812 | gpt-4o-mini | 8.5% |
| WebArena | 812 | gpt-4o | 14.8% |
| WebArena | 812 | claude-3.5-sonnet | 15.5% |
| WebArena Agent baseline (Zhou et al., 2023a) | 812 | gpt-3.5-turbo | 6.2% |
| MiniWoB++ (full set, includes vision tasks) | 125 | gpt-4o | 40.8% |

### 5.3 Miscellaneous assistance

The six remaining benchmarks cover graduate-level question answering, mathematical and coding reasoning with tool feedback, logical deduction, general-assistant tasks, and operating-system command use. On the GPQA diamond set - 198 graduate-level, deliberately hard-to-search multiple-choice science questions - CodeActAgent v1.8 with claude-3.5-sonnet reaches 52.0% accuracy {C008}. The evidence reports this next to two reference points measured under the same benchmark: expert humans at 81.3% and GPT-4 with web search at 38.8% {C008}. Read against these references, the agent's 52.0% sits above a non-agentic baseline that scores 38.8 percentage points lower (GPT-4 with search) and 29.3 percentage points below the human-expert reference, which bounds how much weight the GPQA result alone can carry as evidence of general reasoning ability {C008}. On MINT, a benchmark that allows up to five rounds of tool use and feedback per problem, CodeActAgent v1.5 with gpt-4o reaches 77.3% on the math subset (225 instances) and 50.0% on the code subset (136 instances) {C009}. On the ProofWriter benchmark's challenging subset, which requires five-hop deductive reasoning over stated facts and rules, the same configuration reaches 78.8% on 600 instances {C010}. On AgentBench's operating-system subset (144 instances, requiring the agent to use shell commands to complete file- and process-management tasks), it reaches 57.6% {C011}. On GAIA (a benchmark of general-assistant tasks) at its first difficulty level (53 instances), a different agent design built on the same platform, GPTSwarm, reaches 32.1% with gpt-4o {C011} - included here because it illustrates that the platform's benchmark harnesses are usable by more than one agent implementation, not only by CodeActAgent. On the Entity Deduction Arena, averaged over two 100-instance sub-datasets, CodeActAgent v1.5 with gpt-4o reaches 38.0% {C011}. Table 5 lists all of these miscellaneous-assistance figures alongside the two GPQA reference points.

**Table 5. Miscellaneous-assistance benchmark results.**

| Benchmark | Instances | Agent / Model | Score |
|---|---|---|---|
| GPQA (diamond) | 198 | CodeActAgent v1.8 / claude-3.5-sonnet | 52.0% |
| GPQA (diamond), expert human reference | 198 | - | 81.3% |
| GPQA (diamond), GPT-4 with search reference | 198 | - | 38.8% |
| MINT (math) | 225 | CodeActAgent v1.5 / gpt-4o | 77.3% |
| MINT (code) | 136 | CodeActAgent v1.5 / gpt-4o | 50.0% |
| ProofWriter (5-hop, challenging) | 600 | CodeActAgent v1.5 / gpt-4o-2024-05-13 | 78.8% |
| AgentBench (OS subset) | 144 | CodeActAgent v1.5 / gpt-4o | 57.6% |
| GAIA (level 1) | 53 | GPTSwarm v1.0 / gpt-4o-2024-05-13 | 32.1% |
| Entity Deduction Arena | 200 | CodeActAgent v1.5 / gpt-4o | 38.0% |

Across all three categories, no benchmark in the evidence reports a variance, seed count, or confidence interval alongside its point estimate; every score in Tables 3-5 is a single reported number rather than an average over repeated runs. This is a property of the evidence available for this paper, not something we can resolve by re-analysis, and it means that small differences between configurations (for example, the 1.5-point gap between AutoCodeRover and SWE-Agent in Table 1) should not be read as reliably distinguishable, even though larger differences (such as the roughly four-fold model-driven gap in Section 5.1) are unlikely to be explained by run-to-run noise alone.

## 6. Discussion

Section 5's central pattern is that the same generalist agent - unmodified between benchmarks within a category, and following the same three-action design across all of them - produces a distinct, interpretable score on every benchmark in every category, from 6.3% to 79.3% depending on the task and the backend model. This is consistent with the platform's small, common action interface being sufficient to support meaningful cross-domain evaluation: nothing in the results suggests that the interface itself becomes a bottleneck specific to one domain, since the agent's scores track known task difficulty (for instance, GPQA's expert-human reference of 81.3% versus the agent's 52.0%) rather than collapsing to near-zero or near-ceiling uniformly {C006}. We read this as an answer to the question posed in Section 1: within this evidence, one open platform and one generalist agent configuration can be evaluated, without per-domain prompt changes, across software-engineering, web-browsing, and miscellaneous-assistance tasks, and the resulting numbers are informative enough to compare against named baselines and reference points in each domain.

At the same time, the size of every one of these numbers - not just their presence - depends heavily on the backend model, and this dependence is itself one of the two largest effects visible in Section 5, alongside the differences between benchmarks. A roughly four-fold change in resolve rate from switching only the backend model {C003} means that a platform-level claim about "the agent's" performance is incomplete without naming which model was behind it; this is why every table in Section 5 keeps the model name attached to each score, rather than presenting a single method-level number as the field sometimes does. Practically, this suggests that a platform of this kind is most useful as a way to hold the harness, action interface, and task fixed while varying the model or the agent design - a controlled comparison that would be harder to run if each benchmark required its own bespoke integration.

The broader implication we take from this evidence concerns evaluation infrastructure rather than agent capability as such: a shared, open platform that already integrates fifteen benchmarks lets a researcher compare a new agent design, or a new backend model, against reported baselines without first rebuilding fifteen separate harnesses {C015}. The evidence frames this capability explicitly as relevant to safety - the authors state that systematic evaluation of this kind can help identify and address risks in increasingly capable agents before they are deployed widely {C015} - though this is presented as a stated rationale for building the platform, not as a result the benchmark evaluations themselves produce, and we mark it accordingly as a hypothesis rather than a finding.

## 7. Limitations

**Model sensitivity.** The largest single effect in Section 5 is not between benchmarks but between backend models on the same benchmark: claude-3.5-sonnet outperforms gpt-4o-mini by roughly four times on SWE-Bench Lite under an identical agent configuration {L001}. Any claim about what "the agent" can do should be read as conditional on which model backs it, and generalizing a single model's score to the agent design in the abstract is not supported by this evidence.

**Benchmark scale.** Several headline results, including SWE-Bench Lite's 300 instances (versus the full 2,294-instance SWE-Bench) and MINT's 225- and 136-instance subsets, are evaluated on reduced-size subsets, motivated in the evidence by cost - a conservative estimate for the full SWE-Bench suite alone is approximately $6.9k {L002}. These subset results may not carry over unchanged to the full benchmarks, and readers who need full-scale numbers should treat the figures reported here as bounds from a smaller, though still substantial, sample rather than as final answers.

**Remaining agent capability.** Independent of the platform, the evidence states directly that current agents still struggle with complex tasks and specifically with editing long files {L003}. This limitation affects the ceiling of every result in Section 5.1 that depends on file editing, and it is a capability gap in the agents evaluated, not a property of the platform's action interface.

**Workflow construction.** Building a new agent workflow inside OpenHands still requires substantial handcrafted engineering, according to the evidence {L004}. This bounds how directly the "one platform, one action interface" contribution of this paper should be read as reducing effort for a new agent design; the platform standardizes the interface and the runtime, but constructing a working agent on top of it is not reported as fully automated.

**No repeated-run variance.** As noted in Section 5, no result in the evidence is reported with a seed count, standard deviation, or confidence interval. We treat only differences on the order of the model-driven gap in Section 5.1 (multiple tens of percentage points) as clearly attributable to a real effect rather than possible run-to-run variation, and we avoid describing smaller differences, such as those between individual baselines in Table 1, as reliably distinguishable.

## 8. Conclusion

We have reported on OpenHands, an open platform that gives agents a small, common action interface and a reproducible runtime, and that integrates fifteen benchmarks spanning software engineering, web browsing, and miscellaneous assistance. Within the evidence available, one generalist agent - evaluated without per-domain prompt changes - is shown to produce interpretable, benchmark-appropriate scores in every one of these categories, from a 26.0% resolve rate on SWE-Bench Lite with claude-3.5-sonnet to a 52.0% accuracy on GPQA diamond against an 81.3% expert-human reference {C001,C006,C011}. What should not be taken from this evidence is that the agent's capability is fixed or model-independent: the same design produces a roughly four-fold difference in outcome purely from a change of backend model, and most of the reported numbers reflect reduced-size, cost-driven benchmark subsets rather than complete evaluations. For an adjacent-ML reader, the most transferable takeaway is architectural rather than numerical: separating a small, fixed agent-action interface from the choice of backend model and the choice of benchmark makes it possible to hold two of those three factors fixed while studying the third, which is difficult to do when every agent-benchmark pairing requires its own bespoke harness. The evidence identifies file editing on long files and the handcrafted effort of constructing new agent workflows as the two areas the original authors point to for future improvement {C013,C014}.

## References

Zhou et al., 2023a. (WebArena Agent baseline, cited as it appears in the OpenHands evidence package; no further bibliographic metadata is available in the materials provided for this paper.)
