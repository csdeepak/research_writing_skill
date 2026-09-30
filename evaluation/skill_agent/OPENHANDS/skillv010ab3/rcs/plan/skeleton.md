# Skeleton (topic sentences)
Title: OpenHands: An Open Platform for AI Software Developers as Generalist Agents (for adjacent ML researchers)
I.1 Agents that write code, run commands and browse the web are increasingly capable, but each project must build its own interface, execution environment and evaluations {C001}.
I.2 As the authors describe existing frameworks, they provide building blocks with basic runtime support, limited or stateless code execution, or focus on software engineering {C002}.
I.3 The paper asks whether one open platform can supply what is needed to develop and evaluate agents (RQ1) and whether a single generalist agent on it is competitive across software, web and assistance benchmarks (RQ2) {C027} {C021}.
I.4 OpenHands combines five components and integrates 15 benchmarks {C027} {C009}; its agents score for example 26.0% on SWE-Bench Lite {C011} but trail at least one comparator on eight benchmarks {C020}.
I.5 Sections 2-3 give background and design, 4-5 the evaluation, 6 answers the questions, 7 records later repositories.
B.1 Three ideas carry the paper: agents as functions over an event stream, code as action space, and benchmark success rate as the yardstick {C003}.
B.2 Frameworks differ along runtime strength and domain scope {C002}.
P.1 An agent maps event history to an action; the runtime maps an action to an observation {C003}.
P.2 Three primitive actions run in a per-session docker sandbox behind a REST API {C004}.
P.3 Any docker image can host the runtime {C005}.
P.4 AgentSkills adds only tools that code alone cannot easily provide {C006}.
P.5 Delegation and a hub let agents compose and be shared {C007} {C008}.
P.6 A GUI and mocked-LLM integration tests support users and developers {C023}.
S.1 Fifteen benchmarks in three categories are run against open-source baselines {C009}.
S.2 Subsets and protocols differ per benchmark and shape how results are read {C009}.
R.1 On SWE-Bench Lite the best OpenHands configuration resolves 26.0% {C011}, a few tenths to about a point below three listed systems {C012}.
R.2 On HumanEvalFix the 0-shot agent fixes 79.3%, below a 1-shot SWE-agent at 87.7% {C013}.
R.3 On web tasks BrowsingAgent scores 15.5% on WebArena and 40.8% on MiniWoB++, below trained specialists on the latter {C014} {C015}.
R.4 On assistance tasks OpenHands is ahead of the listed baseline on four rows and behind on three {C016} {C017} {C018} {C019}.
R.5 Eight benchmarks show at least one comparator ahead {C020}.
D.1 RQ1 is answered by description; RQ2's answer is that the tables are consistent with competitiveness {C027} {C021}.
D.2 What the tables cannot show: causal role of design, variance, matched comparisons {L001} {L002}.
D.3 Limitations, each tied to claims {L001}-{L006}.
D.4 The authors expect community uptake to speed research; that is untested {C022}; listed next steps {C024}.
D.5 The READMEs describe a benchmarks repository and Agent Canvas {C026}.
K.1 OpenHands is a documented platform with broad but mixed benchmark evidence {C021} {C020}.

## Gate G2 self-reconstruction (from the skeleton only)
Q1 infrastructure burden for software-acting agents: yes. Q2 software is a powerful interface; safety: yes. Q3 runtime/scope limits per the authors: yes. Q4 platform with five components: yes. Q5 general action space, code as interface: yes (P.1-P.4). Q6 15 benchmarks: yes. Q7 26.0, 79.3, 52.0: yes (52.0 to be added to R.4). Q8 consistent with competitiveness: yes. Q9 variance, causal design, matched baselines: yes. Q10 platform + evaluation: yes. Q11 L001-L006: yes. Q12 one platform, competitive but not leading everywhere: yes. G2 passed.
