# One Agent, Many Domains: Evidence for Cross-Category Generality from the OpenHands Platform

## Abstract

Large language models now drive agents that act on the world through software: writing code, running it, and browsing the web. Building and fairly evaluating such agents, however, has generally meant assembling separate infrastructure per agent or task category, and prior open agent frameworks tend to supply this infrastructure only piecemeal, while specialized agents built for one category are not evaluated outside it. This paper examines whether one open platform, and one generalist agent built on it with a single fixed prompt, can remain competitive across qualitatively different agentic task categories at once. OpenHands supplies an event-stream architecture, a Docker-sandboxed runtime for code execution and web browsing, an extensible agent-computer-interface tool library, multi-agent delegation, and an evaluation harness spanning 15 benchmarks, on top of which it instantiates a generalist, code-acting agent. Using one fixed prompt, this agent is above its comparison baseline on nine of the fifteen benchmarks, within about a point on two more, and below it on the rest -- for example, 26.0% on SWE-Bench Lite, 15.5% on WebArena, and 52.0% accuracy on GPQA -- and no single comparison baseline is evaluated across more than one category. This is consistent with a single general action space on one shared platform supporting broad, simultaneous cross-domain competence, rather than each domain requiring its own purpose-built agent, though no seed variance is reported for any of these numbers, the comparisons are not backbone-model-controlled, and no experiment isolates which platform component is responsible.

## Introduction

Software is, for most practical purposes, the most general interface through which anything -- human or machine -- can act on the world: writing code, running it, and browsing the web already cover an enormous range of tasks. As large language models have become capable enough to drive *agents* -- systems that repeatedly observe an environment and choose an action to take in it, rather than producing one fixed output -- a natural direction is to give such agents this same general interface, so that one agent design might act on many kinds of task rather than one. A platform built on this premise, OpenHands, is already in wide use: released under a permissive open-source license, it had accumulated more than 2,100 code contributions from over 188 contributors and 32,000 GitHub stars at the time it was described.

Building the platform, however, does not by itself answer whether one agent on it can act as a genuine generalist. Prior open agent frameworks provide some of the needed infrastructure -- an interface to act through, an environment to act in, a way for users and agents to communicate -- but at uneven depth: one framework, AutoGen (Wu et al., 2023), adds real code-execution capability to a conversational interface "though with stateless command execution," and others, such as LangChain (Chase, 2022), offer only "foundational building blocks with basic runtime support" {C019}. Separately, agents built for one demanding task category, such as resolving real GitHub issues, have shown that a carefully designed set of task-specific tools can matter a great deal (Yang et al., 2024) -- but that was shown, and those systems were evaluated, within a single task category, not across qualitatively different ones {C018}.

This paper asks the question that follows directly: can one open platform, and one generalist agent built on it with a single fixed prompt, remain competitive across software engineering, web browsing, and other reasoning/tool-use tasks at once, rather than requiring a bespoke agent per category?

OpenHands answers this with an event-stream architecture connecting users, agents, and the environment; a Docker-sandboxed runtime exposing a shell, a Python interpreter, and a browser; an extensible tool library (an *agent-computer interface*, or ACI); and the ability for agents to delegate subtasks to one another. On top sits a hub of more than ten community-contributed agents, including a generalist agent whose actions are themselves executable code or browser commands rather than calls to a fixed tool menu -- a design referred to as CodeAct (Wang et al., 2024a) {C017}. The platform's own harness tests this generalist agent, one fixed prompt, no benchmark-specific modification, on 15 benchmarks spanning software engineering, web browsing, and miscellaneous reasoning and tool-use assistance.

The headline finding: this single design is competitive -- though, as we show, rarely the single best system on any one benchmark -- in every category at once. It resolves 26.0% of SWE-Bench Lite issues (Jimenez et al., 2024), within the range of specialized open coding agents {C001}; completes 15.5% of WebArena's browsing tasks (Zhou et al., 2023a) {C004}; and reaches 52.0% accuracy on GPQA's graduate-level science questions (Rein et al., 2023), above both non-expert humans and the language-model baselines shown {C006}. No comparison baseline in the paper's own tables is evaluated across more than one category {C015}. We take this combination -- one unmodified design, evaluated everywhere, against baselines each evaluated once -- as evidence for the platform's stated goal of generality {C016}.

What follows describes the platform and the evaluation's protocol, presents results by category, and draws them into one cross-category pattern. The Discussion returns to where the agent is not best, and to what the platform does and does not establish about the safety of more autonomous agents; the Limitations return to the statistical status of these numbers and to how much the codebase evaluated here has since changed.

## The OpenHands Platform

We use *agent* here in the now-common sense: software that repeatedly observes the state of an environment and chooses an action to take in it, rather than producing one fixed output for one fixed input. OpenHands is a platform for building and running such agents when the environment is a computer: a repository to edit, a shell to run commands in, or a web page to interact with.

**State and actions.** An OpenHands agent's state is centered on an *event stream*: a chronological record of every action and observation, including the user's own messages, plus bookkeeping such as accumulated LLM cost -- an agent is, in essence, a function from this history to the next action. Three action types cover most of what a human developer or analyst does at a computer: running Python code, running a bash command, and interacting with a web browser through a vocabulary of navigation, clicking, typing, and scrolling actions contributed by a separate project, BrowserGym (Drouin et al., 2024). This design is described as *CodeAct*: the agent's action is executable code or a browser command, not a call to one of a fixed menu of predefined tools {C017}. The stated rationale is flexibility -- a programming-language action space can express a tool in whatever form it already exists in (a Python function, a REST call, a shell script) without a bespoke wrapper for each one {C017} -- while remaining compatible with conventional predefined-tool-calling, since a tool can simply be written as a function in the same language.

**A sandboxed runtime.** Actions run inside an isolated Docker container started fresh for each session, with a configurable workspace directory mounted in. Inside it, a server exposes a bash shell, a Jupyter/IPython interpreter, and a Chromium browser automated via Playwright; browser observations include the page's HTML, DOM, accessibility tree, and a screenshot. Because the container is built from any user-supplied base image, an agent can be given exactly the software environment a task requires.

**An extensible agent-computer interface.** A general action space is not by itself enough: prior work on specialized coding agents (Yang et al., 2024) found that a carefully designed set of task-specific tools -- an *agent-computer interface (ACI)* -- matters for solving complex tasks {C018}. OpenHands adds such tools through a Python library, AgentSkills, auto-imported into the agent's IPython session; several file-editing functions are themselves adapted from that same specialized agent and from a related coding assistant, Aider (Gauthier, 2024). The stated inclusion rule is narrow: add a tool only when plain code cannot readily do the job (e.g. editing one range of lines in a large file) or when the task needs an external model (e.g. transcription, or reading a PDF or image) -- aimed at genuine gaps, not at re-implementing what an LLM can already write.

**Delegation and the agent hub.** An agent can hand a subtask to a different, differently specialized agent through a dedicated delegation action -- the paper's own example is a coding agent delegating browsing to a browsing specialist. OpenHands ships an "AgentHub" of more than ten community-contributed agents: the generalist CodeAct agent evaluated below, a zero-shot browsing specialist, an agent that represents itself as an optimizable graph of operations (GPTSwarm; Zhuge et al., 2024), and lightweight "micro agents" that reuse a generalist implementation with a task-specific prompt. An integration-test suite, which replays stored prompt-response pairs for deterministic, inexpensive checks, runs on every code change to catch regressions as the platform grows.

## Evaluation Setup

To test whether this design supports one competitive generalist agent rather than many specialized ones, the platform's harness integrates 15 benchmarks in three categories: software engineering (SWE-Bench, already introduced; HumanEvalFix, Muennighoff et al., 2024; BIRD, Li et al., 2023b; ML-Bench, Tang et al., 2024b; BioCoder, Tang et al., 2024c; Gorilla APIBench, Patil et al., 2023; ToolQA, Zhuang et al., 2024), web browsing (WebArena, already introduced; MiniWoB++, Liu et al., 2018), and miscellaneous reasoning/tool-use assistance (GAIA, Mialon et al., 2023; GPQA, already introduced; AgentBench, Liu et al., 2023; MINT, Wang et al., 2024b; ProofWriter, Tafjord et al., 2021; Entity Deduction Arena, Zhang et al., 2024a). Each keeps its own automated success criterion -- a passing test suite, an exact-match or multiple-choice answer, execution accuracy, or a task-specific reward function -- so "resolve rate" or "success rate" below always means that benchmark's own check, not a measure invented for this comparison.

A few protocol choices apply throughout and are worth stating once rather than repeating per result. Prompting is zero-shot unless stated otherwise. SWE-Bench is evaluated without its optional natural-language hint text. Three benchmarks use a reduced subset for cost reasons: SWE-Bench's "Lite" 300-instance split, a "quarter" subset of ML-Bench, and an "easy" subset of ToolQA, the last two following the original benchmarks' own reduced-scale protocols. Comparison-baseline numbers throughout are drawn from the papers that introduced each baseline system, not re-run by OpenHands' authors under identical hardware or sampling conditions {L004}. None of the sources report a seed count, number of repeated runs, or variance for any success-rate number, for OpenHands' agents or for the baselines {L001}.

## Results

### Software engineering

The first question is the most direct one: can a generalist agent, using general-purpose code-execution and file-editing actions with no benchmark-specific prompting, resolve real software-engineering tasks at a rate comparable to agents built specifically for this category?

On SWE-Bench Lite, a 300-instance subset of real GitHub issues resolved by editing a repository until a held-out test suite passes, OpenHands' CodeActAgent (v1.8) resolved 26.0% of instances with claude-3.5-sonnet, 22.0% with gpt-4o, and 7.0% with gpt-4o-mini, zero-shot and without the benchmark's optional hint text {C001}. Table 1 places these next to five reproducible open baselines evaluated the same way: SWE-Agent (18.0%; Yang et al., 2024), AutoCodeRover (19.0%; Zhang et al., 2024b), Aider (26.3%; Gauthier, 2024), Moatless Tools (26.7%), and Agentless (27.3%; Xia et al., 2024). This means OpenHands' best configuration falls inside the specialized baselines' own range rather than leading or trailing it {C002}; none of these six numbers comes with a reported seed count or variance, so the ranking is a single-run snapshot, not a statistically separated one. Table 1 also reports cost: OpenHands' cheapest configuration averaged $0.01 per instance and its gpt-4o configuration $1.72, next to SWE-Agent's $1.67; the authors separately estimate that the complete, 2,294-instance SWE-Bench would cost on the order of $6,900, against the cost-motivated "Lite" subset used throughout.

**Table 1. SWE-Bench Lite (300 instances, no hint text, 0-shot): resolve rate and average per-instance cost.**

| Agent | Backbone | Resolve rate (%) | Cost ($/instance) |
|---|---|---|---|
| SWE-Agent | gpt-4-1106-preview | 18.0 | 1.67 |
| AutoCodeRover | gpt-4-0125-preview | 19.0 | -- |
| Aider | gpt-4o & claude-3-opus | 26.3 | -- |
| Moatless Tools | claude-3.5-sonnet | 26.7 | -- |
| Agentless | gpt-4o | 27.3 | -- |
| OpenHands CodeActAgent v1.8 | gpt-4o-mini | 7.0 | 0.01 |
| OpenHands CodeActAgent v1.8 | gpt-4o | 22.0 | 1.72 |
| OpenHands CodeActAgent v1.8 | claude-3.5-sonnet | 26.0 | 1.10 |

*"--" marks a value not reported in the source. No seed or repeated-run variance is reported for any entry (Limitation L001).*

A second benchmark sharpens this picture and adds a caveat. HumanEvalFix asks an agent to fix a bug in a short function using test-execution feedback over several turns. Zero-shot, OpenHands' agent (v1.5, gpt-4o) fixed 79.3% of the Python-split bugs {C003} -- above every non-agentic code-language-model baseline reported (16.6-48.6%), which generate a fix without iterating against test feedback. It is, however, below a SWE-Agent configuration that reached 87.7%, given one worked example of a full successful fix ("1-shot"), where OpenHands' run was zero-shot {C003}. The gap is thus at least partly a gap in guidance, not only capability -- a first instance of a pattern this paper returns to: OpenHands is competitive, but rarely the single best system in any one table.

The remaining software benchmarks are more one-sided, with one sharp exception. On BIRD (text-to-SQL), BioCoder (bioinformatics code completion), and ML-Bench (ML-repository code generation), OpenHands' best configuration exceeded every general-purpose prompting baseline shown: 47.3% vs. 18.3-31.3% on BIRD, 27.5% vs. 11.0-12.7% on BioCoder, and 76.5% vs. 11.0-26.2% (prompting) and 42.6-64.4% (agentic baselines SWE-Agent, Aider) on ML-Bench {C014}. On Gorilla APIBench (API-call selection), 36.4% likewise exceeded prompted general-purpose baselines (8.7-29.7%), though it remained well below a model fine-tuned specifically for this task (75.0%) {C014} -- narrow, task-specific training can still beat a general-purpose agent on its own turf. On ToolQA (tool-augmented question answering), OpenHands' gpt-4o configuration reached 47.2%, the highest value reported, while its gpt-3.5-turbo configuration reached only 2.3% {C013} -- far below a same-tier ReAct baseline (Yao et al., 2023) on a comparable backbone (36.8%) {C013}. We report this low value because it bears on how far the platform's competitiveness generalizes across backbones, not only tasks: a weaker backbone did not merely reduce performance here, it collapsed it.

### Web browsing

Software engineering exercises the platform's code-execution path. Web browsing exercises a different action space and is a more independent test of whether the same design choices carry over.

On WebArena, free-form browsing tasks (shopping, forums, developer platforms, content management) on realistic, self-hosted websites, OpenHands' best configuration (BrowsingAgent v1.0, claude-3.5-sonnet) completed 15.5% of 812 tasks {C004} -- above two of four specialized/trained baselines shown (Lemur, 5.3%, Xu et al., 2023; a model trained with self-improvement synthetic data, 9.4%, Patel et al., 2024) and below the other two (AutoWebGLM, 18.2%, Lai et al., 2024; Auto Eval & Refine, 20.2%, Pan et al., 2024) {C004}, and above a zero-shot baseline using the same family of general-purpose LLMs (6.2-14.4%). OpenHands' generalist CodeActAgent, delegating the browsing subtask rather than acting on the browser directly, reached a nearly identical 15.3% {C004} -- delegation cost essentially nothing here.

MiniWoB++ complicates the picture: 125 short, synthetic web micro-tasks with a built-in reward function, which makes it possible to train a policy directly on the task distribution. OpenHands' best configuration reached 40.8% {C005} -- above one exploration-trained baseline (34.6%) but far below CC-NET (91.1%; Humphreys et al., 2022), a specialist trained with reinforcement learning and human-annotated behavioral cloning directly on these tasks {C005}. This is the sharpest case in the paper of a general-purpose agent losing decisively to a narrow, purpose-trained specialist on its own distribution: "competitive across categories" does not mean competitive with every possible system, only with baselines that share the agent's own general-purpose design.

### Miscellaneous assistance

The final category shares the least with the code- and browser-centric action spaces the platform was built around, making it the strongest test of whether cross-category competitiveness is genuine breadth or an artifact of the first two categories.

On GAIA, real-world assistant tasks mixing reasoning, browsing, and tool use, OpenHands' GPTSwarm agent -- which represents an agent as an optimizable graph of operations -- solved 32.1% of 53 validation-level tasks with gpt-4o (30.2% with an earlier gpt-4 variant), well above an AutoGPT baseline's 13.2% (Gravitas, 2023) {C007}. On GPQA, graduate-level science questions designed to resist simple web look-up, OpenHands' CodeActAgent reached 52.0% accuracy on the "diamond" subset {C006}, best read against the benchmark's own calibration points: 81.3% for expert humans, 21.9% for non-experts, and 29.6-38.8% for two few-shot chain-of-thought baselines {C006} -- well above non-experts and both LLM baselines, but well below experts. "Competitive with reported baselines" is narrower than "expert-level."

The remaining four benchmarks continue the same competitive-but-uneven pattern. OpenHands exceeded its comparison baseline on AgentBench's operating-system subset (57.6% vs. 42.4%) {C008} and on MINT's math subset, a multi-turn tool-and-feedback benchmark (77.3% vs. 65.8%) {C009}, and matched the strongest baseline on ProofWriter within about a point (78.8% vs. 79.6% for a solver-augmented baseline, Logic-LM, Pan et al., 2023) {C011}. It fell below its baseline on MINT's code subset (50.0% vs. 59.6%) {C010} and on Entity Deduction Arena, a twenty-questions-style benchmark (38.0% vs. 40.0%) {C012}; we report both shortfalls as they stand because they bear on the scope of the cross-category claim developed next.

### Cross-category synthesis

Fifteen benchmarks and dozens of numbers raise an obvious question: what is the one thing to take from all of this? The answer is not any single number but a structural fact about how the numbers were produced. In every benchmark above, the system scored under the "OpenHands" label is the same generalist design -- CodeActAgent, CodeActAgent delegating to BrowsingAgent for web tasks, or GPTSwarm for GAIA -- carrying one fixed prompt with no benchmark-specific modification. Not one of the sixteen comparison baseline systems named above appears in more than one category table {C015}. Table 2 lays out all fifteen benchmarks side by side to make this visible directly.

**Table 2. OpenHands' best configuration versus one named comparison baseline, all fifteen evaluated benchmarks.**

| Category | Benchmark | OpenHands best (%) | Comparison baseline (%) | Relative to baseline |
|---|---|---|---|---|
| Software | SWE-Bench Lite | 26.0 | Aider, 26.3 | within range |
| Software | HumanEvalFix | 79.3 | StarCoder2-15B (non-agentic), 48.6 | above |
| Software | BIRD | 47.3 | CodeQwen-7B-Chat, 31.3 | above |
| Software | ML-Bench | 76.5 | Aider, 64.4 | above |
| Software | BioCoder | 27.5 | prompting (gpt-4-1106-preview), 12.7 | above |
| Software | Gorilla APIBench | 36.4 | prompting (gpt-3.5-turbo-0301), 29.7 | above |
| Software | ToolQA | 47.2 (gpt-4o) / 2.3 (gpt-3.5-turbo) | ReAct (gpt-3.5-turbo), 36.8 | above / far below |
| Web | WebArena | 15.5 | Auto Eval & Refine, 20.2 | below |
| Web | MiniWoB++ | 40.8 | CC-NET, 91.1 | far below |
| Misc. | GAIA | 32.1 | AutoGPT, 13.2 | above |
| Misc. | GPQA (diamond) | 52.0 | Few-shot CoT (gpt-4), 38.8 | above |
| Misc. | AgentBench (OS) | 57.6 | AgentBench baseline, 42.4 | above |
| Misc. | MINT (math) | 77.3 | MINT baseline, 65.8 | above |
| Misc. | MINT (code) | 50.0 | MINT baseline, 59.6 | below |
| Misc. | ProofWriter | 78.8 | Logic-LM, 79.6 | within range |
| Misc. | Entity Deduction Arena | 38.0 | Zero-shot (gpt-4-0314), 40.0 | below |

*No comparison baseline recurs across rows. No seed/replicate variance is reported for any entry (Limitation L001). ToolQA shows both OpenHands configurations because they diverge sharply.*

Counting benchmarks rather than table rows: OpenHands' best configuration is above its comparison baseline on nine of the fifteen, within about a point of it on two more (SWE-Bench Lite, ProofWriter), mixed on one (MINT: above on math, below on code), and below it on the remaining three (WebArena, MiniWoB++, Entity Deduction Arena) {C015}. No category is swept, and none is a wash. What is unusual is not any individual number but that one unmodified agent design produced this entire pattern by itself, across three categories that share very little required skill {C015}. What that pattern is evidence for, and what it is not, is taken up in the Discussion.

## Discussion

The question we opened with was whether one open platform and one generalist agent, built on it with a single fixed prompt, could remain competitive across software engineering, web browsing, and miscellaneous reasoning/tool-use tasks at once. The answer suggested by Results is yes, with real qualifications: the same agent design was competitive -- above its comparison baseline on most benchmarks, within a point of it on two more, and behind it on a few -- in every category tested, and no single comparison baseline was shown to do the same {C016}. This is consistent with a single general action space, on one shared, safely sandboxed platform, being sufficient for broad cross-domain competence, rather than each domain requiring its own purpose-built agent {C016}. We say "consistent with" deliberately: the evidence is a pattern across many single-run benchmark scores, not a controlled experiment that isolates generality as a variable.

One reason this pattern is informative is that the design, not the backbone model, is what stayed fixed. OpenHands' own results already vary by backbone within a single benchmark -- gpt-4o-mini, gpt-4o, and claude-3.5-sonnet spanned 7.0-26.0% on SWE-Bench Lite alone {C001} -- yet the same platform and agent were resubmitted, unmodified, to each new category regardless of backbone. That the pattern of competitiveness, not any specific score, held up across this range is some evidence the platform's contribution is separable from any one model's capability, though Limitations explains why this cannot be stated more strongly. Read this way, the result extends an observation made for a single-category specialist agent -- that a carefully designed agent-computer interface matters for solving complex tasks (Yang et al., 2024) {C018} -- from one category to three.

If this holds up under more controlled comparison, it points to a practical implication: effort spent on one general, well-integrated platform -- a flexible action space, a safe sandbox, an extensible tool interface, a broad evaluation harness -- may substitute for effort spent building a separate bespoke agent per task category {C016}, a different allocation of engineering effort than the specialized-agent pattern several of the strongest single-category baselines in Results follow.

A more attentive audience for this claim is the one the introduction deferred: as agents gain autonomy over real systems, what stops generality from simply making mistakes faster across more domains at once? The paper's own answer is not empirical but architectural and procedural: systematic evaluation before deployment, a design that keeps a human able to interrupt and redirect the agent rather than assuming full autonomy, and open access to the same agent suite for other researchers to probe {C020}. That is a stated intention, not a measured safety property, and no safety-specific benchmark is among the 15 evaluated -- a boundary worth stating plainly.

## Limitations and Future Work

Four limitations bound how far the central finding travels. First, no seed count, repeated run, or variance estimate is reported for any success-rate number, for OpenHands' agents or any baseline {L001}; every comparison above is a single-run point estimate. Second, comparisons are not backbone-model-controlled -- OpenHands is shown at several backbones while many baselines use one, sometimes older or smaller, model or a specialist trained model {L002} -- so platform design and model capability are confounded throughout. Third, OpenHands is not the top performer on several individual benchmarks (WebArena, MiniWoB++, HumanEvalFix against a 1-shot baseline, MINT's code subset, Entity Deduction Arena, one ToolQA configuration) {L003}, and benchmark subsets, excluded hint text, and baseline numbers taken from their original papers rather than re-run under identical conditions further limit comparability across rows {L004}. Fourth, no experiment here varies one platform component -- event stream, sandbox, tool library, delegation -- while holding the others fixed, so which part is responsible for the cross-category pattern is not established {L006}.

A fifth caveat concerns currency, not validity: the versions evaluated are a specific, dated snapshot. Later project material describes a reorganized system built around a separate software development kit and a distinct front-end product, with an SDK change dated as late as November 2025, so implementation details here should not be assumed current, even though the underlying design principles are unlikely to have been abandoned {L005}.

The authors' own next steps: richer multi-modality (images, video, and spreadsheets through the same browser/code-execution path), stronger agents via training and inference-time techniques, better long-file editing, browsing improvements via a planned retry-and-reflect integration, and reducing the hand-crafted engineering that building a new agent workflow requires, possibly through graph-based construction frameworks {C021}. We would add an empirical safety evaluation to accompany the platform's stated safety rationale {L007}, and a controlled ablation of the platform's own components.

## Related Work

Two families of prior systems, as characterized in the evaluated paper's own text, motivate treating cross-category generality as an open question. General-purpose open agent frameworks provide interaction and coordination abstractions but, on the source's own account, at uneven depth: AutoGen (Wu et al., 2023) adds real Python and bash execution to a conversational framework "though with stateless command execution," and others, such as LangChain/LangGraph (Chase, 2022), offer only "foundational building blocks with basic runtime support" {C019} -- neither implies a persistent, sandboxed session or an integrated, broad evaluation harness of the kind used here. Specialized software-engineering agents show the complementary half: a carefully designed, task-specific agent-computer interface was shown to matter within one task category, GitHub issue resolution (Yang et al., 2024) {C018}, but none of the specific reproducible systems built on that observation and compared against in Results -- SWE-Agent, AutoCodeRover (Zhang et al., 2024b), Aider (Gauthier, 2024) -- is evaluated, in the source material, outside software engineering. Together, these two families leave open exactly the question this paper's evaluation addresses: whether one platform and one agent design, rather than a shallow general interface or a deep single-category one, holds up once the task category itself changes.

## Conclusion

OpenHands packages a general action space -- code execution, shell commands, and browser control, run inside a safe sandbox -- with an extensible tool library, multi-agent delegation, and a 15-benchmark harness, into one open platform. On top of it, one generalist agent, carrying a single fixed prompt, was competitive with reproducible baselines across software engineering, web browsing, and miscellaneous reasoning/tool-use tasks at once, though it rarely led any individual benchmark and lost decisively to at least one narrow, purpose-trained specialist {C016}. What is new is not any one score but that a single, unmodified agent design produced a broadly competitive pattern across categories sharing little required skill. Whether that pattern reflects the platform's architecture specifically, rather than the backbone models tested on it, is a question a controlled ablation could answer but this evaluation does not.

## References

Chase, H. (2022). LangChain. Software/documentation.

Drouin, A., Gasse, M., Caccia, M., Laradji, I. H., Del Verme, M., Marty, T., Boisvert, L., Thakkar, M., et al. (2024). WorkArena: How Capable Are Web Agents at Solving Common Knowledge Work Tasks? Preprint.

Gauthier, P. (2024). How Aider Scored SOTA 26.3% on SWE Bench Lite. Blog post.

Gravitas, S. (2023). Auto-GPT: An Autonomous GPT-4 Experiment. Software/documentation.

Humphreys, P. C., Raposo, D., Pohlen, T., Thornton, G., Chhaparia, R., Muldal, A., Abramson, J., Georgiev, P., et al. (2022). A Data-Driven Approach for Learning to Control Computers. ICML.

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. R. (2024). SWE-bench: Can Language Models Resolve Real-world GitHub Issues? ICLR.

Lai, H., Liu, X., Iong, I. L., Yao, S., Chen, Y., Shen, P., Yu, H., Zhang, H., et al. (2024). AutoWebGLM: Bootstrap and Reinforce a Large Language Model-based Web Navigating Agent. Preprint.

Li, J., Hui, B., QU, G., Yang, J., Li, B., Li, B., Wang, B., Qin, B., et al. (2023). Can LLM Already Serve as a Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs. NeurIPS Datasets and Benchmarks Track.

Liu, E. Z., Guu, K., Pasupat, P., Shi, T., and Liang, P. (2018). Reinforcement Learning on Web Interfaces Using Workflow-Guided Exploration. ICLR.

Liu, X., Yu, H., Zhang, H., Xu, Y., Lei, X., Lai, H., Gu, Y., Ding, H., et al. (2023). AgentBench: Evaluating LLMs as Agents. Preprint.

Mialon, G., Fourrier, C., Swift, C., Wolf, T., LeCun, Y., and Scialom, T. (2023). GAIA: a Benchmark for General AI Assistants. Preprint.

Muennighoff, N., Liu, Q., Zebaze, A., Zheng, Q., Hui, B., Zhuo, T. Y., Singh, S., Tang, X., et al. (2024). OctoPack: Instruction Tuning Code Large Language Models. Preprint.

Pan, L., Albalak, A., Wang, X., and Wang, W. Y. (2023). Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning. Preprint.

Pan, J., Zhang, Y., Tomlin, N., Zhou, Y., Levine, S., and Suhr, A. (2024). Autonomous Evaluation and Refinement of Digital Agents. Preprint.

Patel, A., Hofmarcher, M., Leoveanu-Condrei, C., Dinu, M.-C., Callison-Burch, C., and Hochreiter, S. (2024). Large Language Models Can Self-Improve at Web Agent Tasks. Preprint.

Patil, S. G., Zhang, T., Wang, X., and Gonzalez, J. E. (2023). Gorilla: Large Language Model Connected with Massive APIs. Preprint.

Rein, D., Hou, B. L., Stickland, A. C., Petty, J., Pang, R. Y., Dirani, J., Michael, J., and Bowman, S. R. (2023). GPQA: A Graduate-Level Google-Proof Q&A Benchmark. Preprint.

Tafjord, O., Dalvi, B., and Clark, P. (2021). ProofWriter: Generating Implications, Proofs, and Abductive Statements over Natural Language. Findings of ACL-IJCNLP 2021.

Tang, X., Liu, Y., Cai, Z., Shao, Y., Lu, J., Zhang, Y., Deng, Z., Hu, H., et al. (2024b). ML-Bench: Evaluating Large Language Models and Agents for Machine Learning Tasks on Repository-Level Code. Preprint.

Tang, X., Qian, B., Gao, R., Chen, J., Chen, X., and Gerstein, M. B. (2024c). BioCoder: A Benchmark for Bioinformatics Code Generation with Large Language Models. Bioinformatics.

Wang, X., Chen, Y., Yuan, L., Zhang, Y., Li, Y., Peng, H., and Ji, H. (2024a). Executable Code Actions Elicit Better LLM Agents. ICML.

Wang, X., Wang, Z., Liu, J., Chen, Y., Yuan, L., Peng, H., and Ji, H. (2024b). MINT: Evaluating LLMs in Multi-turn Interaction with Tools and Language Feedback. ICLR.

Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., Li, B., Jiang, L., et al. (2023). AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework. Preprint.

Xia, C. S., Deng, Y., Dunn, S., and Zhang, L. (2024). Agentless: Demystifying LLM-based Software Engineering Agents. Preprint.

Xu, Y., Su, H., Xing, C., Mi, B., Liu, Q., Shi, W., Hui, B., Zhou, F., et al. (2023). Lemur: Harmonizing Natural Language and Code for Language Agents. Preprint.

Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., and Press, O. (2024). SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. Preprint.

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. R., and Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR.

Zhang, Y., Lu, J., and Jaitly, N. (2024a). Probing the Multi-turn Planning Capabilities of LLMs via 20 Question Games. Preprint.

Zhang, Y., Ruan, H., Fan, Z., and Roychoudhury, A. (2024b). AutoCodeRover: Autonomous Program Improvement. Preprint.

Zhou, S., Xu, F. F., Zhu, H., Zhou, X., Lo, R., Sridhar, A., Cheng, X., Ou, T., et al. (2023a). WebArena: A Realistic Web Environment for Building Autonomous Agents. ICLR.

Zhuang, Y., Yu, Y., Wang, K., Sun, H., and Zhang, C. (2024). ToolQA: A Dataset for LLM Question Answering with External Tools. NeurIPS.

Zhuge, M., Wang, W., Kirsch, L., Faccio, F., Khizbullin, D., and Schmidhuber, J. (2024). Language Agents as Optimizable Graphs. Preprint.
