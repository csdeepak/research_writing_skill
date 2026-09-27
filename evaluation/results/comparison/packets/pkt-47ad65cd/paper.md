# OpenHands: A Generalist Agent Platform for Software, Web, and Tool-Use Tasks, and What Evaluating It Across Domains Shows

## Abstract

A large language model (LLM) can be wrapped in an interaction loop — observe, act, repeat — to
form an *agent* that operates real software environments: it can edit a repository, click through
a website, or call external tools. Building the sandboxing, tool interfaces, and multi-benchmark
evaluation harness such an agent needs is normally redone by every project that tries this.
OpenHands packages this infrastructure as an open platform released under the MIT license (a
permissive open-source license allowing commercial use): an "agent hub" of more than ten
implemented agents and an evaluation framework integrating 15 established benchmarks across three
digital-task categories — software engineering, web interaction, and miscellaneous
tool-use/reasoning assistance. We report what happens when the same
general-purpose agent, CodeActAgent, is run without per-domain modification across this suite,
alongside a dedicated browsing agent for the web category. The agent reaches a 26.0% resolve rate
on SWE-Bench Lite and fixes 79.3% of HumanEvalFix (Python) bugs; on
miscellaneous-assistance tasks it exceeds its reported baseline on four of six benchmarks,
including GAIA (32.1% vs. 13.2%) and AgentBench OS (57.6% vs. 42.4%), while
trailing it on two (MINT-code, Entity Deduction Arena); on web-interaction
benchmarks it trails systems built specifically for the target benchmark, most sharply on
MiniWoB++ (40.8% vs. 91.1% for a trained specialist). We read this mixed pattern, together
with the platform's openness, as evidence for a reusable generalist-evaluation contribution
rather than a claim of leading every individual benchmark. Every reported number is
a single run with no variance reported, and two pairs of numbers conflict internally in the
source material; we disclose both.

## 1. Introduction

A language model that only answers questions in a chat window cannot, by itself, fix a bug in a
code repository or complete a multi-step task on a website. Doing either requires wrapping the
model in a loop: observe the current state of an environment, choose one action, execute it, and
repeat until the task is judged complete or a limit is reached. We call a system built this way
an *LLM agent*. Constructing an agent for a new task domain is not just a prompting
exercise — it requires a sandboxed environment to execute the agent's actions safely, an
interface between the model and that environment (a browser, a shell, a code editor), and,
crucially, a way to measure whether the agent actually succeeded, usually against an existing
benchmark with its own instance format and scoring rule. A project that wants to test one agent
idea across several kinds of tasks — say, code repair and web browsing — has historically had to
build or adapt this infrastructure once per domain.

This duplication has a direct cost for adjacent researchers: even if a lab has a promising agent
design, evaluating it broadly enough to know whether the design is a genuinely general improvement
or an artifact of one benchmark's quirks means re-implementing sandboxing and harnesses for every
benchmark family it wants to test on. The evidence available for this paper documents the
resulting practice: evaluation for agents is organized as separate families of established
benchmarks and their own baseline systems — non-agentic or lightly agentic code-repair pipelines
such as Agentless (Xia et al., 2024), domain-general prompted agents such as AutoGPT (Gravitas,
2023), and benchmark-trained specialists such as CC-NET (Humphreys et al., 2022) — each reported
and compared within its own domain. We do not have access, in the evidence available to this run,
to a verified feature-by-feature comparison of OpenHands against other end-to-end agent
frameworks (the source paper's own comparison table did not survive the text extraction this
evidence package was built from), so we make no claim here about how OpenHands's platform design
compares to alternative platforms. What the available evidence does support is a narrower,
answerable question, and this paper asks it directly: **can one general-purpose agent, run
without per-domain modification, be evaluated end to end across software-engineering,
web-interaction, and miscellaneous-assistance tasks through a single open platform and harness,
and what does the resulting pattern of results look like?**

OpenHands answers the infrastructure half of this question directly: it is an open-source
platform containing an *agent hub* — a library of more than ten implemented agents that share the
same environment interfaces — and an evaluation framework that integrates 15 established
benchmarks spanning the three task categories above. The two agents whose results we
report here are **CodeActAgent**, a general-purpose agent that represents its actions as
executable code, and **BrowsingAgent**, an agent specialized for interacting with a web browser.
OpenHands is released under the MIT license, and at the time the evidence for this paper was
written, the project reported more than 2.1K contributions from over 188 contributors and 32K
GitHub stars — self-reported, time-varying figures about project adoption, not benchmark scores.

Our contribution, at the strength the evidence supports, is the following. First, a single agent
platform and evaluation harness lets one general agent be measured across 15 benchmarks in three
categories without rebuilding infrastructure per domain, providing later researchers a shared
basis for comparison. Second, we report what that measurement shows: CodeActAgent, run
unmodified, reaches results the source material describes as competitive on several
software-engineering and miscellaneous-assistance benchmarks, while both
CodeActAgent and BrowsingAgent trail specialized or benchmark-trained systems on others,
particularly in the web-interaction category. We report every one of these results,
including the ones where OpenHands is outperformed, because the negative results bear directly on
how broad the generalist claim can be read. The rest of the paper proceeds by category:
Section 2 gives the background an adjacent reader needs and locates the compared systems; Section
3 describes the platform; Section 4 describes the evaluation setup; Section 5 reports results by
task category, each interpreted against its nearest baseline; Section 6 discusses what the overall
pattern does and does not establish; Section 7 states the limitations of every claim above; and
Section 8 concludes.

## 2. Background and Related Evaluation Methods

Readers outside this subfield need three conventions before the results in Section 5 are
readable. First, for repository-level code-fix tasks, success is usually reported as a **resolve
rate**: the fraction of issues for which the agent's proposed patch passes that issue's own,
held-out test suite — not a similarity score against a reference patch. Second, **shot setting**
matters: a *0-shot* evaluation gives the agent only the task description, while a *1-shot*
evaluation gives it one full worked example first; the two are not directly comparable even on
the same benchmark. Third, the miscellaneous-assistance category in this paper covers tasks with
different reward structures — from multiple-choice science questions to interactive word games —
so "success rate" and "accuracy" are used depending on what the underlying benchmark defines.

The systems OpenHands is compared against in Section 5 fall into three families, distinguished by
what each assumes is sufficient to solve its task. The first family treats code repair as a
largely structured pipeline: Agentless (Xia et al., 2024) separates localization from patch
generation without an open-ended agent loop, and reaches the highest reported SWE-Bench Lite
score among the compared systems, 27.3% with gpt-4o. Two further code-repair systems, Moatless
Tools and Aider, are reported by name as baselines in the same tables (26.7% and 26.3% on
SWE-Bench Lite respectively) but are not accompanied by a citable year in the available evidence,
so we name them without a formal citation. The second family is domain-general prompted agents —
systems, including OpenHands's own agents, that use one loop and one model across many kinds of
tasks without training on the target benchmark; AutoGPT (Gravitas, 2023) is the representative
baseline in this family for the GAIA benchmark. The third family is benchmark-trained
specialists: systems trained, often with reinforcement learning or human demonstrations,
specifically on the target benchmark's distribution. CC-NET (Humphreys et al., 2022) and Workflow
Guided Exploration (Liu et al., 2018) are both members of this family for MiniWoB++, and their
comparison to OpenHands should be read with that difference in training regime in mind. For
logical inference, Logic-LM (Pan et al., 2023) is a hybrid: an LLM paired with a symbolic solver
operating on logical forms already extracted from the problem text. For multi-turn code and math
tasks, the MINT benchmark (Yuan et al., 2024) supplies both the task subsets and a baseline agent
allowed the same number of interaction turns as OpenHands. Two further benchmarks used in the
evaluation, Gorilla APIBench (Patil et al., 2023) and ToolQA (Zhuang et al., 2024), define
tool-use tasks that OpenHands was evaluated on, though, as noted in Section 7, this evidence
package cannot safely attribute OpenHands's specific scores on those two benchmarks to a
particular row of the source table.

## 3. The OpenHands Platform

OpenHands is organized around two parts: the agent hub and the evaluation framework. The **agent
hub** is a library of more than ten implemented agents that share a common set of environment
interfaces (a sandboxed shell, a code editor, a web browser), so that a new agent design can reuse
these interfaces instead of re-implementing them. Two agents from this hub produce the
results reported in Section 5. **CodeActAgent** is the platform's general-purpose agent: rather
than choosing from a fixed menu of actions, it represents each action as a snippet of executable
code, which is run in the sandbox and whose output becomes the next observation. CodeActAgent is
the agent used, unmodified in its system prompt, across the software-engineering and
miscellaneous-assistance categories reported below. **BrowsingAgent** is a second agent,
specialized for operating a web browser, used for the web-interaction category; in some reported
configurations CodeActAgent delegates browsing sub-tasks to BrowsingAgent rather than acting on
the browser directly.

The **evaluation framework** is the second part of the platform: it integrates 15 established
benchmarks, organized by the source material into three categories — seven software-engineering
benchmarks, two web-interaction benchmarks, and six miscellaneous-assistance benchmarks.
Framing this as one framework, rather than one script per benchmark, is what lets a single agent
be run across all three categories with the same harness and reporting conventions, which is the
platform-level claim this paper evaluates. OpenHands is released under the MIT license, a
permissive license that allows commercial use and redistribution. We do not have verified
evidence in this package describing the platform's lower-level implementation (the specific
sandboxing technology, for instance), so we do not report implementation details beyond what is
stated above.

## 4. Evaluation Setup

Table 1 summarizes the benchmarks whose results we report in Section 5, organized by the three
categories the source material defines. Each is a pre-existing, independently published benchmark
that OpenHands is evaluated *on*, not something OpenHands introduces: SWE-Bench Lite and
HumanEvalFix test repository- and function-level bug fixing; WebArena and MiniWoB++ test,
respectively, open-ended and short structured web-browser tasks; GAIA tests open-ended
tool-use assistance; GPQA tests graduate-level multiple-choice science questions; AgentBench's
operating-system (OS) subset tests issuing shell commands to complete a stated goal; MINT tests
multi-turn math and coding problems solved with tool feedback; ProofWriter tests multi-hop
logical inference; and the Entity Deduction Arena tests an interactive twenty-questions-style
guessing game. For every benchmark, we report the number of evaluated instances, the shot setting
where specified, and the comparison systems named in Section 2. Several further
software-engineering benchmarks (ML-Bench, a suite of machine-learning coding tasks; BioCoder;
Gorilla APIBench; and ToolQA) are part of OpenHands's evaluation set but are excluded from Table 1
and from Section 5 because the mapping between reported numeric cells and the specific agent/model
row could not be recovered from the source material without risking a misattributed number; we
return to this in Section 7.

**Table 1. Benchmarks reported in this paper, by category.**

| Category | Benchmark | Instances | Shot setting | Compared systems (Section 2) |
|---|---|---|---|---|
| Software engineering | SWE-Bench Lite | 300 | 0-shot, w/o hint | Agentless, Moatless Tools, Aider |
| Software engineering | HumanEvalFix (Python) | 164 | 0-shot, self-debug over turns | SWE-Agent (1-shot), StarCoder2-15B |
| Web interaction | WebArena | 812 | zero-shot | Auto Eval & Refine, AutoWebGLM |
| Web interaction | MiniWoB++ | 125 (full set, incl. vision tasks) | — | CC-NET, Workflow Guided Exploration |
| Misc. assistance | GAIA (L1 validation) | 53 | — | AutoGPT |
| Misc. assistance | GPQA (diamond set) | 198 | — | Few-shot CoT gpt-4, human expert/non-expert |
| Misc. assistance | AgentBench (OS/bash subset) | 144 | — | AgentBench baseline agent |
| Misc. assistance | MINT (math and code subsets) | 225 / 136 | up to 5 turns, 2 solution attempts | MINT baseline agent |
| Misc. assistance | ProofWriter (5-hop subset) | 600 | uses Logic-LM logical forms | Logic-LM, Few-shot CoT gpt-4 |
| Misc. assistance | Entity Deduction Arena | 200 (2 x 100, averaged) | — | Zero-shot prompting (gpt-4-0314) |

*SWE-Bench Lite is a 300-instance canonical subset of the full 2,294-instance SWE-Bench, used by
default in this evaluation for cost; the source material estimates that running the complete
SWE-Bench set would cost about $6.9k at a conservative $3 per instance, and that a
SWE-Bench Lite evaluation with gpt-4o costs around $600.* GAIA as a whole comprises 466 curated
tasks across three difficulty levels; the 53-instance figure above is the L1 validation subset
that OpenHands was evaluated on, not the full benchmark. Entity Deduction Arena evaluates two
datasets, "Things" and "Celebrities," 100 instances each, and reports their average.

No variance, standard deviation, or seed count accompanies any result cell we report below; every
value is a single run, a point we return to in Section 7. We also could not determine from the
available material whether the baseline systems in Table 1 were tuned with a compute or prompt
budget comparable to OpenHands's own agents; comparisons should be read with that caveat.

## 5. Results

### 5.1 Software engineering

On SWE-Bench Lite, CodeActAgent v1.8 with claude-3-5-sonnet resolves 26.0% of the 300 evaluated
instances, 0-shot and without hint text. Against the compared systems in Table 1, this
places CodeActAgent below Agentless (27.3%, Xia et al., 2024) and Moatless Tools (26.7%), and
close to Aider (26.3%). The gap to the strongest baseline is 1.3 percentage points on a 300-item
test, and with no variance reported for any of the four systems, we cannot say whether this
difference is distinguishable from run-to-run noise. CodeActAgent v1.8 with gpt-4o-2024-05-13
reaches 22.0% under the same conditions. For a weaker model, gpt-4o-mini-2024-07-18, the source
material reports two different values for the identical configuration: 6.3% in one table and 7.0%
in another; we report both rather than choosing one, since nothing in the available evidence
adjudicates between them.

On HumanEvalFix (Python), CodeActAgent v1.5 with gpt-4o-2024-05-13 fixes 79.3% of the 164
evaluated bugs, 0-shot, using self-debug over multiple turns. This is below SWE-Agent's
87.7% on the same benchmark, but SWE-Agent's result uses one full worked demonstration (1-shot)
where OpenHands's evaluation is 0-shot; the two numbers are not a like-for-like comparison,
and the 8.4-point gap should not be read as a design difference in isolation. Both agentic systems
are well above the non-agentic StarCoder2-15B baseline, which fixes 48.6% of the same bugs — the
source material describes OpenHands's result as almost double this baseline. With a weaker model,
gpt-3.5-turbo-16k-0613, the same agent version reaches 20.1% on the same task, underlining that
much of the difference between the 79.3% and 20.1% results tracks the underlying model rather than
the agent scaffold alone.

### 5.2 Web interaction

On WebArena, BrowsingAgent v1.0 with claude-3-5-sonnet-20240620 completes 15.5% of the 812
evaluated tasks under zero-shot prompting. This is below both compared systems in Table 1:
AutoWebGLM, a trained 7B model, reaches 18.2%, and Auto Eval & Refine, which combines GPT-4 with a
reflexion loop and a GPT-4V reward model, reaches 20.2%. With gpt-4o-2024-05-13, BrowsingAgent
reaches 14.8%; when CodeActAgent delegates browsing sub-tasks to BrowsingAgent instead of using
BrowsingAgent directly, the claude-3-5-sonnet configuration reaches a comparable 15.3%. All three
OpenHands configurations trail both baselines by 3 to 6 percentage points, and this is the
clearest below-baseline pattern in the categories we report, which we return to as a bound on the
generalist-performance interpretation in Section 6.

On MiniWoB++, a benchmark of 125 short, structured web environments including tasks that require
vision, BrowsingAgent v1.0 with gpt-4o reaches 40.8% on the full set. This is far below
CC-NET, a specialist model trained with reinforcement learning and human-annotated behavior
cloning, at 91.1% (Humphreys et al., 2022), though it is above Workflow Guided Exploration, a
trained agent that explores the environment during training, at 34.6% (Liu et al., 2018). When CodeActAgent
delegates to BrowsingAgent with gpt-4o, the result is 39.8%, essentially unchanged from direct use.
The roughly 50-point gap to CC-NET reflects, at least in part, a difference in training paradigm:
CC-NET is trained specifically on this benchmark's distribution, while OpenHands's agents are
prompted zero-shot with no benchmark-specific training.

### 5.3 Miscellaneous assistance

Across the six miscellaneous-assistance benchmarks we can safely attribute to specific rows, four
show OpenHands agents exceeding their compared baseline and two show them falling short. On GAIA's
53-instance L1 validation subset, OpenHands's GPTSwarm agent with gpt-4o-2024-05-13 reaches 32.1%,
more than double AutoGPT's 13.2% with gpt-4-turbo (Gravitas, 2023); with gpt-4-0125-preview,
the same agent reaches 30.2%. On AgentBench's OS (bash) subset (144 instances), CodeActAgent v1.5
with gpt-4o reaches 57.6%, above the AgentBench baseline agent's 42.4% with gpt-4; with the
weaker gpt-3.5-turbo-0125, the same agent falls to 11.8%. On the MINT math subset (225 instances),
CodeActAgent v1.5 with gpt-4o reaches 77.3%, above the MINT baseline agent's 65.8% with gpt-4-0613
(Yuan et al., 2024). On ProofWriter's 600-instance, 5-hop subset, the same agent reaches
78.8%, just below Logic-LM's 79.6% (Pan et al., 2023) and above a Few-shot Chain-of-Thought gpt-4
baseline's 68.1%; this comparison is qualified because OpenHands, like Logic-LM, is given
Logic-LM's already-extracted logical forms rather than parsing the problem itself.

The two exceptions run the other way. On the MINT code subset (136 instances), CodeActAgent v1.5
with gpt-4o reaches 50.0%, below the MINT baseline agent's 59.6% — a result that bears
directly on the generalist claim and is reported here rather than omitted, since it is the same
agent and model that succeeded on the math subset of the same benchmark. On the Entity Deduction
Arena (200 instances, averaged across two 100-instance datasets), the same agent reaches 38.0%,
below a zero-shot gpt-4-0314 baseline's 40.0%.

On GPQA's 198-instance diamond set, CodeActAgent v1.8 with claude-3-5-sonnet reaches 52.0%
accuracy, and CodeActAgent v1.5 with GPT-4o reaches 53.1%; with GPT-4-turbo, the
same v1.5 agent reaches 51.8%. All three sit between the benchmark's own reference points: a
non-expert human baseline of 21.9% and a few-shot Chain-of-Thought gpt-4 baseline of 38.8% below
OpenHands, and an expert-human baseline above it (Rein et al., 2023). That expert-human value is
itself reported inconsistently in the source material — 81.3% in one table and 81.2% in
another — and we report both without resolving which is correct. The source material also
reports GPQA results by a main set and an extended set in addition to the diamond set, but we do
not attribute those additional cells to specific methods here, for the same reason given in
Section 4 for the excluded software-engineering benchmarks.

## 6. Discussion

Reading Sections 5.1-5.3 together, the same CodeAct-style agent, run without any change to its
system prompt across three different task categories, reaches results the source material
describes as competitive in several of them — resolving over a quarter of SWE-Bench Lite issues,
exceeding baseline agents on four of six miscellaneous-assistance benchmarks, and roughly doubling
a non-agentic baseline on HumanEvalFix — while trailing specialized or benchmark-trained systems
in others, most clearly on the two web-interaction benchmarks and on two of the six
miscellaneous-assistance benchmarks. We read this pattern as supporting a claim about the
*platform*, not about any single benchmark: the contribution demonstrated here is that one general
agent and one harness can produce this whole cross-domain picture at once, not that this agent is
the best-performing system on any particular benchmark in Table 1. The clearest counter-evidence to a
broader "OpenHands's agents are competitive everywhere" reading is the web-interaction category,
where both WebArena and MiniWoB++ results trail every compared baseline, sometimes considerably
(the roughly 50-point gap to CC-NET on MiniWoB++). Some of this gap is attributable to a
difference in kind rather than a shared weakness across the platform: CC-NET and Workflow Guided
Exploration are trained specifically for MiniWoB++'s distribution using reinforcement learning and
demonstrations, while BrowsingAgent is a zero-shot prompted agent with no such training.
This qualification bounds the interpretation without erasing the result: a generalist,
zero-shot agent is not yet a substitute for a benchmark-trained specialist on structured web
micro-tasks, even though the same style of agent is closer to specialized systems on code-repair
and several reasoning tasks.

The cost figures reported alongside these benchmarks are worth noting for readers considering
using this platform themselves: the source material estimates the complete 2,294-instance
SWE-Bench set would cost about $6.9k to run at a conservative $3-per-instance estimate, and a
SWE-Bench Lite pass with gpt-4o costs around $600. These are explicitly labeled estimates,
not measured totals, but they indicate that the evaluation framework's breadth (15 benchmarks) is
paired with a real, non-trivial compute cost, which is itself a practical constraint on how
often such a full evaluation can be re-run — relevant to interpreting why every result we report
is a single run rather than an average over several.

The authors of the source material state that reaching 100% on HumanEvalFix is feasible and name
it as a target for future iterations; we report this as a stated intention, not as evidence
that it has been achieved or attempted. This forward-looking framing is consistent with reading
the present results as a snapshot of a platform under active development rather than a final,
closed evaluation.

## 7. Limitations

Five limitations bound every claim above, and we state them against the specific claims they
affect rather than as generic caveats.

**No variance is reported for any result.** Every success rate and accuracy figure in Sections
5.1-5.3 is a single run, with no standard deviation, seed count, or significance test given in the
source material. Differences we describe as "above" or "below" a baseline — including the
1.3-point SWE-Bench Lite gap to Agentless and the 0.8-point ProofWriter gap to Logic-LM — are raw
point differences, and none is established as statistically distinguishable from run-to-run noise.

**Two internal conflicts are unresolved.** The source material reports two different values for
CodeActAgent v1.8 with gpt-4o-mini on SWE-Bench Lite (6.3% and 7.0%) and two different values for
GPQA-diamond's expert-human baseline (81.3% and 81.2%). We disclose both values in
each case rather than choosing one, since nothing in the available evidence indicates which is
correct; averaging or silently picking one would misrepresent the source material's own
inconsistency.

**Some benchmark results could not be safely attributed.** Table 4 of the source material (in the
original numbering) reports success rates for ML-Bench, BioCoder, Gorilla APIBench, and ToolQA,
and Table 7 reports GPQA main-set and extended-set accuracies, but in both cases the mapping from
numeric cell to specific agent/model row could not be recovered from the evidence available to
this paper. We omit these specific numbers rather than guess at their attribution, which means
Section 5 under-reports OpenHands's full evaluated benchmark set.

**Baseline comparability is only partly known.** The evidence available does not state whether the
AgentBench and MINT baseline agents were run with a compute or prompt budget comparable to
OpenHands's agents, and the WebArena/MiniWoB++ baselines that outperform OpenHands include
systems trained specifically on their target benchmark (CC-NET, Workflow Guided Exploration),
which is a difference in method, not only in result. Both qualify how the head-to-head
comparisons in Section 5 should be read.

**The evidence package itself is text extracted from a paper, not the underlying logs.** No
result file, log, or configuration was available to this paper beyond the paper's own reported
numbers and two repository README files; nothing here was independently reproduced from raw data, and
a feature-by-feature comparison table against other agent frameworks, present in the source paper,
did not survive extraction and so could not be used to support any comparative platform claim.

## 8. Conclusion

OpenHands packages the infrastructure an LLM agent needs — a shared agent hub and an evaluation
framework spanning 15 benchmarks across software-engineering, web-interaction, and
miscellaneous-assistance tasks — as a single, MIT-licensed, openly available platform.
Run through this platform, one general-purpose agent reaches results the source material
describes as competitive on several benchmarks in two of the three categories, while trailing
specialized or benchmark-trained systems on the web-interaction category and on two of six
miscellaneous-assistance benchmarks. We read the contribution demonstrated by the
available evidence as the platform and the cross-domain measurement it enables, not as a claim
that any one OpenHands agent leads every benchmark it was evaluated on. Every number we report is
a single run with no reported variance, and two pairs of numbers conflict in the source material
without resolution; a reader building on these results should treat them as a first, unreplicated
snapshot of one agent's cross-domain behavior rather than a settled measurement.

## References

Gravitas, T. (2023). AutoGPT. [Baseline agent for GAIA, as cited in the source evidence.]

Humphreys, P. C. et al. (2022). CC-NET. [Trained specialist baseline for MiniWoB++, as cited in
the source evidence.]

Liu, E. Z. et al. (2018). Workflow Guided Exploration. [Trained specialist baseline for MiniWoB++,
as cited in the source evidence.]

Pan, L. et al. (2023). Logic-LM. [Baseline for ProofWriter, as cited in the source evidence.]

Patil, S. G. et al. (2023). Gorilla APIBench. [Benchmark used in the evaluation, as cited in the
source evidence.]

Rein, D. et al. (2023). GPQA. [Benchmark and human baselines, as cited in the source evidence.]

Xia, C. S. et al. (2024). Agentless. [Baseline for SWE-Bench Lite, as cited in the source
evidence.]

Yuan, X. et al. (2024). MINT. [Benchmark and baseline agent, as cited in the source evidence.]

Zhuang, Y. et al. (2024). ToolQA. [Benchmark used in the evaluation, as cited in the source
evidence.]

*Full bibliographic details (venue, volume, pages, DOI) are not available in the evidence package
supplied to this paper and are not invented here; see corpus/source_registry.json and
