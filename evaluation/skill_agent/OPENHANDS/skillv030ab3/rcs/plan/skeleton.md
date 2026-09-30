# Skeleton (one topic sentence per paragraph slot)

A.1 OpenHands is an open platform on which LLM agents act through code, a shell and a browser inside a sandbox, and the authors report its default agents' scores on 15 benchmarks: competitive with, but often below, the reference systems they list. {C010} {C024} {C042}
I.1 Building and evaluating agents that act through software is hard, and the authors see software as the ideal interface for agents to act on the world. {C001} {C002}
I.2 As the authors describe existing frameworks, general ones offer limited or stateless code execution and software-engineering systems are domain-specific. {C004} {C005}
I.3 The authors' goal of general agents yields two questions: what infrastructure lets one platform host community-built agents, and how does a default generalist agent fare across categories without benchmark-specific prompt engineering. {C003} {C026}
I.4 OpenHands answers with an event stream, a sandboxed runtime, a tool library, delegation and a benchmark harness, choosing a small set of programming-language actions for stated reasons. {C010} {C011} {C012}
I.5 The contributions are a platform, an evaluation on 15 benchmarks that includes rows below the references, and the platform's reported community activity. {C019} {C024} {C029} {C042}
I.6 Sections follow the two questions.
R.1 The frameworks the authors cite provide building blocks and multi-agent conversation, and AutoGen and CrewAI are described as limited in code execution. {C004} {C005}
R.2 Software-engineering and web agents matter here as reference rows and as sources of ideas such as the agent-computer interface. {C005} {C006}
R.3 The positioning against these systems is the authors' claim, and the table that would back it lost its feature marks. {C005}
M.1 An agent is a function from the event history to an action, and a runtime turns each action into an observation. {C010}
M.2 Actions run in a per-session Docker container that offers a shell, IPython and Chromium, built from any base image. {C011} {C013} {C014}
M.3 The authors chose three programming-language primitives to cover most tasks of software engineers and analysts. {C012}
M.4 A shared skills package adds tools the model cannot readily write itself, under stated inclusion criteria. {C015} {C016}
M.5 Delegation lets a generalist hand web tasks to a browsing agent, and the hub and micro agents lower the barrier to contribution. {C017} {C018} {C019} {C020}
M.6 A chat interface lets users interrupt the agent, and integration tests with mocked LLM calls guard against regressions. {C021} {C022} {C023}
M.7 The authors expect evaluation and human oversight to mitigate risk, but report no safety evaluation. {C027}
S.1 The suite spans seven software, two web and six assistance benchmarks. {C024} {C003}
S.2 The protocol compares with reproducible open-source references and adapts a few benchmarks for stated reasons. {C025} {C026} {C028}
S.3 Each benchmark defines its own score, and reference rows are reported values, not re-runs. {C025}
Rs.1 On software benchmarks the unmodified CodeAct agent reached 26.0% on SWE-bench Lite and 79.3% on HumanEvalFix, near or below the listed references. {C030} {C031} {C032} {C033}
Rs.2 On web benchmarks the best OpenHands scores were 15.5% on WebArena and 40.8% on MiniWoB++, below trained specialists. {C034} {C035} {C036}
Rs.3 On assistance benchmarks OpenHands scored 32.1% on GAIA and 52.0% on GPQA diamond, and was below a reference on some rows. {C037} {C038} {C039} {C043}
Rs.4 Scores depend strongly on the base model, and several rows sit below the best reference. {C040} {C041} {C044}
D.1 The design question is answered by the authors' description, and the evaluation question by "competitive, not consistently leading". {C042} {C031} {C036}
D.2 Later repository READMEs and community numbers describe growth and extensions but are not evaluation results. {C045} {C046} {C029}
D.3 Scores mix agent design, base model and version, so no single component is credited. {C042}
Lim.1 The authors concede that agents struggle with complex tasks, edit long files poorly and need handcrafted workflows, among other limits. {L001} {L002} {L003} {L004} {L005} {L006} {L007} {L008} {L009}
Lim.2 Additional caveats: no variance, unmatched references, no ablation, extraction damage. {L010} {L011} {L012} {L013} {L014} {L015}
Con.1 OpenHands offers a common base whose agents are competitive but not leading, and the authors point to multi-modality, stronger agents and better editing next. {C042} {C050}
