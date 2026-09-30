## Results

### Software engineering

The first question is the most direct one: can a generalist agent, using general-purpose code-execution and file-editing actions with no benchmark-specific prompting, resolve real software-engineering tasks at a rate comparable to agents built specifically for this category?

On SWE-Bench Lite, a 300-instance subset of real GitHub issues that an agent resolves by editing a repository until a held-out test suite passes, OpenHands' CodeActAgent (v1.8) resolved 26.0% of instances with a claude-3.5-sonnet backbone, 22.0% with gpt-4o, and 7.0% with gpt-4o-mini, all zero-shot and without the benchmark's optional hint text {C001}. Table 1 places these next to five reproducible open baselines evaluated the same way: SWE-Agent (18.0%; Yang et al., 2024), AutoCodeRover (19.0%; Zhang et al., 2024b), Aider (26.3%; Gauthier, 2024), Moatless Tools (26.7%), and Agentless (27.3%; Xia et al., 2024). OpenHands' best configuration falls inside this 18.0-27.3% range rather than leading or trailing it {C002}; none of these six numbers comes with a reported seed count or variance, so the ranking among them is a single-run snapshot, not a statistically separated one. Table 1 also reports cost: OpenHands' cheapest configuration averaged $0.01 per instance and its gpt-4o configuration $1.72, next to SWE-Agent's $1.67; the authors separately estimate that evaluating the complete, 2,294-instance SWE-Bench would cost on the order of $6,900, against the cost-motivated "Lite" subset used throughout.

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

A second software-engineering benchmark sharpens this picture and adds a caveat. HumanEvalFix asks an agent to fix a bug in a short function using test-execution feedback over several turns. Zero-shot, OpenHands' agent (v1.5, gpt-4o) fixed 79.3% of the Python-split bugs {C003} -- above every non-agentic code-language-model baseline reported (16.6-48.6%), which generate a fix without iterating against test feedback. It is, however, below a SWE-Agent configuration that reached 87.7%, but that configuration was given one worked example of a full successful fix ("1-shot"), where OpenHands' run was zero-shot {C003}. The gap is therefore at least partly a gap in guidance, not only in capability -- a first instance of a pattern this paper returns to: OpenHands is competitive, but rarely the single best system in any one table.

The remaining software benchmarks are more one-sided, with one sharp exception. On BIRD (text-to-SQL), BioCoder (bioinformatics code completion), and ML-Bench (ML-repository code generation), OpenHands' best configuration exceeded every general-purpose prompting baseline shown: 47.3% vs. 18.3-31.3% on BIRD, 27.5% vs. 11.0-12.7% on BioCoder, and 76.5% vs. 11.0-26.2% (prompting) and 42.6-64.4% (agentic baselines SWE-Agent, Aider) on ML-Bench {C014}. On Gorilla APIBench (API-call selection), OpenHands' 36.4% likewise exceeded prompted general-purpose baselines (8.7-29.7%), though it remained well below a model fine-tuned specifically for this benchmark's task (75.0%) {C014} -- narrow, task-specific training can still beat a general-purpose agent on its own turf. Finally, on ToolQA (tool-augmented question answering), OpenHands' gpt-4o configuration reached 47.2%, the highest value reported for this benchmark, while its gpt-3.5-turbo configuration reached only 2.3% {C013} -- far below a same-tier ReAct baseline (Yao et al., 2023) using a comparable backbone (36.8%) {C013}. We report this low value because it bears on how far the platform's competitiveness generalizes across backbone models, not only across tasks: a weaker backbone did not merely reduce performance smoothly here, it collapsed it.

### Web browsing

Software engineering exercises the platform's code-execution path. Web browsing exercises a different action space and is a more independent test of whether the same design choices carry over.

On WebArena, a benchmark of free-form browsing tasks (shopping, forums, developer platforms, content management) on realistic, self-hosted websites, OpenHands' best configuration (BrowsingAgent v1.0, claude-3.5-sonnet) completed 15.5% of 812 tasks {C004} -- above two of four specialized/trained baselines shown (Lemur, 5.3%, Xu et al., 2023; a model trained with self-improvement synthetic data, 9.4%, Patel et al., 2024) and below the other two (AutoWebGLM, 18.2%, Lai et al., 2024; Auto Eval & Refine, 20.2%, Pan et al., 2024) {C004}, and above a zero-shot baseline using the same family of general-purpose LLMs (6.2-14.4%). OpenHands' generalist CodeActAgent, delegating the browsing subtask to BrowsingAgent rather than acting on the browser directly, reached a nearly identical 15.3% -- delegating to a specialist cost essentially nothing here.

MiniWoB++ complicates the picture. It replaces WebArena's open-ended tasks with 125 short, synthetic web micro-tasks with a built-in reward function, which makes it possible to train a policy directly on the task distribution. OpenHands' best configuration reached 40.8% {C005} -- above one exploration-trained baseline (34.6%) but far below CC-NET (91.1%; Humphreys et al., 2022), a specialist trained with reinforcement learning and human-annotated behavioral cloning directly on these tasks {C005}. This is the sharpest case in the paper of a general-purpose agent losing decisively to a narrow, purpose-trained specialist on the specialist's own distribution: "competitive across categories" does not mean competitive with every possible system, only with baselines that share the agent's own general-purpose design.

### Miscellaneous assistance

The final category shares the least with the code- and browser-centric action spaces the platform was built around, making it the strongest available test of whether cross-category competitiveness is genuine breadth or an artifact of the first two categories.

On GAIA, real-world assistant tasks mixing reasoning, browsing, and tool use, OpenHands' GPTSwarm agent -- which represents an agent as an optimizable graph of operations -- solved 32.1% of 53 validation-level tasks with gpt-4o (30.2% with an earlier gpt-4 variant), well above an AutoGPT baseline's 13.2% (Gravitas, 2023) {C007}. On GPQA, graduate-level science questions designed to resist simple web look-up, OpenHands' CodeActAgent reached 52.0% accuracy on the "diamond" subset {C006}. For calibration, the benchmark's own human baselines were 81.3% (expert) and 21.9% (non-expert); two few-shot chain-of-thought baselines reached 29.6% and 38.8% {C006}. OpenHands is thus well above non-expert humans and both LLM baselines, but well below experts -- "competitive with reported baselines" is narrower than "expert-level."

The remaining four benchmarks split three ways. OpenHands exceeded its comparison baseline on AgentBench's operating-system subset (57.6% vs. 42.4%) {C008} and on the math subset of MINT, a multi-turn tool-and-feedback benchmark (77.3% vs. 65.8%) {C009}. It matched, within about a point, the strongest baseline on ProofWriter, a synthetic deductive-reasoning benchmark at its hardest five-hop setting (78.8% vs. 79.6% for a solver-augmented baseline, Logic-LM, Pan et al., 2023, both above a plain chain-of-thought baseline at 68.1%) {C011}. It fell below its comparison baseline on MINT's code subset (50.0% vs. 59.6%) {C010} and on Entity Deduction Arena, a twenty-questions-style benchmark (38.0% vs. 40.0% for a zero-shot baseline on the same backbone) {C012}. We report both shortfalls as they stand, without adjustment, because they bear directly on the scope of the cross-category claim developed next.

### Cross-category synthesis

Fifteen benchmarks and dozens of numbers raise an obvious question: what is the one thing to take from all of this? The answer is not any single number but a structural fact about how the numbers were produced. In every benchmark above, the system scored under the "OpenHands" label is the same generalist design -- CodeActAgent, CodeActAgent delegating to BrowsingAgent for web tasks, or GPTSwarm for GAIA -- carrying one fixed prompt with no benchmark-specific modification. Not one of the sixteen comparison baseline systems named above appears in more than one of the three category tables {C015}. Table 2 lays out all fifteen benchmarks side by side to make this visible directly.

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
