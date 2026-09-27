# Gold Account v1 — OPENHANDS (verified)

Sources: `evaluation/external_projects/OPENHANDS/snapshot/paper.txt` (arXiv 2407.16741v3, "Published as a conference paper at ICLR 2025", L1-3), `README__OpenHands__OpenHands.md`, `README__OpenHands__benchmarks.md`. The pinned repository commits (`b0906809…`, `405bae71…`) come from the evaluation manifest and cannot be verified from the snapshot. **The paper is authoritative for every research claim. The READMEs are used only for artifact facts (§19).** Line numbers (`L`) refer to `paper.txt`.

## Changes from draft

1. **GAIA 32.1% reassigned.** It belongs to OH GPTSwarm v1.0 + gpt-4o, not CodeActAgent v1.8 + claude. CodeActAgent has no GAIA result (Table 6, L642-650; Table 3, L455-459).
2. **GPQA 52.0% re-sourced** to Table 6 (L666-670) and Table 3. Table 7 contains only CodeActAgent **v1.5** rows (diamond: 27.9 / 51.8 / 53.1). Table 3's "∗53.1" is the v1.5 + gpt-4o value.
3. **Research-gap statement rewritten.** The draft said "no framework combines all features" and attributed this to the paper, but no legible text states it. §3 now gives only what the text states: L11 and the specific Appendix C shortcomings (L902).
4. **HumanEvalFix 79.3% now names CodeActAgent v1.5 + gpt-4o-2024-05-13.** The v1.5 + gpt-3.5 result, 20.1%, was added.
5. **Author-stated limitations added:** "may not achieve top performance in every category" (L461), and agents "lack the ability to perform complex, long-horizon tasks … reliably" (L896).
6. **Scope attached to the generality claim.** CodeActAgent's WebArena number comes through delegation to BrowsingAgent v1.0 (Table 5, L578).
7. **Results added from cleanly extracted tables:** Table 5 (WebArena, MiniWoB++) and Table 6 (GAIA). Table 4 BIRD/ML-Bench/BioCoder/Gorilla/ToolQA rows added as **medium-confidence** reconstructions.
8. **Paper-internal conflicts recorded:** SWE-Bench Lite gpt-4o-mini 6.3 (Table 3) vs 7.0 (Table 4). GPQA expert 81.3 is relabeled as Table 6 (not "§4.4 text") vs 81.2 in Table 7. BrowserInteractiveAction vs BrowseInteractiveAction.
9. **README material moved out of the research sections** into §19, "Artifact notes". The README-based nugget Q12c was removed from `gold_story.v1.json`.
10. **Minor fixes:** AgentSkills inclusion-criterion examples; evidence line ids; "32K" quoted exactly; Q9c reworded to the authors' own stated scope; confidence basis stated for each table.

## 1. Problem
Building agents that effectively develop software is hard. The paper names three questions (§1, L17). How can agents create and modify code in complex software systems? How can they get tools to gather information on the fly, for debugging or for task needs? How can development be kept safe, without negative side effects on users' systems?

## 2. Motivation
Software is "one of the most powerful tools" humans have (Abstract, L7). The authors argue that "the most powerful way in which humans currently interact with the world is through software" (L12). Because of that, and because of the existing tooling around software, it "provides the ideal interface for AI agents to interact with the world in complex ways" (L17). LLM progress has driven fast growth in agents, which makes their development and evaluation challenging (L10-11).

## 3. Research gap
Many open-source agent frameworks exist, for example MetaGPT, AutoAgents, and AutoGen. They generally provide (1) interfaces through which agents act (JSON function calls or code execution), (2) environments, and (3) human-agent or agent-agent interaction mechanisms (L11). Table 1 compares frameworks on these features: GUI, standardized tool library, built-in sandbox and code execution, built-in web browser, multi-agent collaboration, human-AI collaboration, AgentHub, evaluation framework, and agent QC (L209-249). **The table cells were lost in extraction**, so this snapshot cannot say which framework has which feature. The legible text names these specific shortcomings:
- AutoGen implements Python and bash execution "with stateless command execution".
- CrewAI offers "sandboxed but limited code interpreter features".
- LangChain and LangGraph provide "basic runtime support" (App. C, L902).
- Building, maintaining, and distributing agent-computer-interface tools across agent implementations is "a daunting engineering challenge" (§2.3, L196).

*The paper does not explicitly state, in legible text, that no framework combines all of these features. Do not score readers on that claim.*

## 4. Objective
The objective is to build OpenHands (formerly OpenDevin), a community-driven platform for developing generalist and specialist agents that interact with the world through software. It has five parts: an event-stream interaction mechanism, a Docker-sandboxed runtime, a developer-like interface (AgentSkills), multi-agent delegation, and an evaluation framework. It is delivered as "a comprehensive and immediately usable implementation", "not just a conceptual framework" (L17-20).

## 5. System / method
- **State and event stream.** The state holds a chronological event stream of actions and observations, including user messages. It also holds auxiliary information such as accumulated LLM cost and delegation metadata (§2.1, L130).
- **Actions.** Inspired by CodeAct, the actions are `IPythonRunCellAction`, `CmdRunAction`, and a browser action. The browser action is spelled `BrowserInteractiveAction` in §2.1 (L131) and `BrowseInteractiveAction` in Fig. 2/3 (L98, L173). It uses BrowserGym's browsing DSL. A PL-based action space is compatible with tool-calling agents and lets agents create their own tools (L131-161).
- **Agent abstraction.** An agent implements `step(state) -> Action`. Fig. 3 gives a minimal agent (L140-181).
- **Runtime.** Each task session gets its own Docker container sandbox. A REST "action execution API" server inside it maintains a bash shell, a Jupyter IPython server, and a Playwright Chromium browser with BrowserGym primitives. Browser observations include HTML, DOM, accessibility tree, and screenshots. A configurable workspace directory is mounted into the sandbox (§2.2, L185-193). Arbitrary user Docker images are supported by building an "OH runtime image" on top of them (L194; App. F).
- **AgentSkills.** A Python package that is auto-imported into IPython. A skill is added only if (1) an LLM cannot readily write the code directly (e.g. edit and replace lines), and/or (2) it calls an external model (e.g. speech-to-text, or a code-editing model) (L197-198). The listed skills include open_file, goto_line, scroll_up/down, create_file, edit_file, search_dir/file, find_file, parse_pdf/docx/latex/audio/image/video/pptx (App. I, L1049-1112, "as of OpenHands v0.6").
- **Delegation.** `AgentDelegateAction`. For example, CodeActAgent has limited web-browsing support and delegates browsing to BrowsingAgent (§2.4, L201).
- **AgentHub** (§3, L202-253):
  - CodeActAgent is the default generalist. It can converse, or act by executing bash, Python, or browser code.
  - BrowsingAgent is a zero-shot generalist web agent, "similar to that in WebArena" but with improved observations and actions.
  - GPTSwarm Agent builds agents as optimizable graphs.
  - Micro Agents reuse a generalist agent's implementation with specialized prompts.
  - §1 says there are "over 10 implemented agents" (L20).
- **Quality control.** End-to-end integration tests mock the LLM by exact prompt match to get deterministic behavior. They run on every PR and every main-branch commit, on Linux and Mac, and in local, SSH, and exec sandboxes (App. E, L911).
- **UI.** A chat-based web GUI connected to the event stream. The user can interrupt at any time (L20, App. D, L909).

## 6. Architecture
The system has three components (Fig. 2, L121): (1) the agent abstraction, with implementations contributed to agenthub; (2) the event stream; (3) the runtime (action to observation). The runtime is client-server: the backend (`runtime.py`) communicates over REST with a "runtime client" inside the container (App. F.1, L918-926). Runtime images use two tags (App. F.2.1, L931-947). One is a hash tag, the MD5 of the build folder (source plus Dockerfile), which provides reproducibility. The other is a generic tag, `oh_v{VERSION}_{BASE_IMAGE}_tag_{IMAGE_TAG}`, which points to the latest build.

## 7. Data
The paper introduces no new dataset. It uses 15 existing benchmarks (Table 2, L259-271):
- **Software:** SWE-Bench, HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA.
- **Web:** WebArena, MiniWoB++.
- **Misc. assistance:** GAIA, GPQA, AgentBench, MINT, Entity Deduction Arena, ProofWriter.

## 8. Experimental setup
- **Comparison scope.** OpenHands is compared with "open-source reproducible baselines that do not perform manual prompt engineering specifically based on the benchmark content" (L257).
- **SWE-Bench Lite.** 300 instances, without hint text. Lite is used for cost; the full 2294-instance set is estimated at $6.9k at $3 per instance (L464, L467, Table 4 L478). A gpt-4o Lite run costs about 600 USD (footnote 4, L912).
- **HumanEvalFix.** Python subset, 164 instances. Multi-turn self-debugging with test feedback, pass@k following Muennighoff et al. OpenHands is 0-shot; SWE-Agent is 1-shot (L466, L483).
- **BIRD.** 300 dev samples, execution accuracy. Multi-turn SQL correction is allowed (L617).
- **ML-Bench.** Quarter subset, 68 instances (L550, L497).
- **BioCoder.** Python, 157 instances. The benchmark has 157 Python and 50 Java functions. Context was removed from prompts to test retrieval (L556, L616, L506).
- **Gorilla APIBench.** 1775 instances. A call counts as correct if it is in the correct API domain (L552, L511).
- **ToolQA.** Easy subset, 800 instances (L554, L518).
- **WebArena.** 812 tasks (L621).
- **MiniWoB++.** Full set of 125 environments. Only full-set baselines are compared (L622).
- **GAIA.** L1 validation set, 53 instances. The benchmark has 466 tasks overall (L626, L638).
- **GPQA.** Diamond set, 198 instances. Main and extended sets are in Table 7 (L652, L973-986).
- **AgentBench.** OS (bash) subset, 144 instances (L672, L771).
- **MINT.** Math, 225 instances; code, 136 instances. Up to 5 iterations and 2 solution proposals (L690, L708, L772).
- **ProofWriter.** 600 five-hop instances, using Logic-LM's logical forms (L726, L773).
- **Entity Deduction Arena.** "Things" and "Celebrities", 100 instances each, averaged (L744, L774).

## 9. Metrics
The metric is success rate (%). Specific forms are resolve rate (SWE-Bench), bugs fixed (HumanEvalFix), execution accuracy (BIRD), and accuracy (GPQA). Most tables also report average cost per instance in USD (Tables 4-7).

## 10. Results
Confidence basis:
- **High:** Table 6 and Table 7 (clean extraction). Table 5 (value counts match row counts). The SWE-Bench Lite and HumanEvalFix rows of Table 4 (matched by prose). Table 3 columns (checked against Tables 4-6).
- **Medium:** the other Table 4 rows (aligned by counting values against model lists).
- **Not recoverable:** Table 1 cells.

**Software (Table 4, L472-546; Table 3)**
- SWE-Bench Lite (300, w/o hint): SWE-Agent gpt-4-1106-preview 18.0; AutoCodeRover gpt-4-0125-preview 19.0; Aider gpt-4o & claude-3-opus 26.3; **OH CodeActAgent v1.8: gpt-4o-mini 7.0 (6.3 in Table 3, a paper-internal conflict); gpt-4o-2024-05-13 22.0; claude-3-5-sonnet@20240620 26.0** (L529; L464 "competitive resolve rate of 26%"). Table 3 only: Moatless Tools claude-3.5-sonnet 26.7, Agentless gpt-4o 27.3 (L306-316). Average cost per instance: SWE-Agent 1.67; OH mini 0.01, gpt-4o 1.72, claude 1.10 (L539-540).
- HumanEvalFix (164): BLOOMZ-176B 16.6; OctoCoder-15B 30.4; DeepSeekCoder-33B-Instruct 47.5; StarCoder2-15B 48.6; SWE-agent 1-shot gpt-4-turbo 87.7; **OH CodeActAgent v1.5, 0-shot: gpt-3.5-turbo-16k-0613 20.1; gpt-4o-2024-05-13 79.3** (L530; L466).
- *(medium confidence)* BIRD (300): CodeLlama-7B-Instruct 18.3; CodeQwen-7B-Chat 31.3; OH v1.5 + BM25 gpt-4-1106-preview 42.7, gpt-4o 47.3 (L531).
- *(medium confidence)* ML-Bench (68): prompting gpt-3.5-turbo 11.0, gpt-4-1106 22.1, gpt-4o 26.2; SWE-Agent gpt-4-1106 42.6; Aider gpt-4o 64.4; OH v1.5 gpt-4o 76.5, gpt-4-1106 58.8, gpt-3.5-16k 13.2 (L532).
- *(medium confidence)* BioCoder Python (157): gpt-3.5-turbo 11.0; gpt-4-1106 12.7; OH v1.5 gpt-4o 27.5 (L533).
- *(medium confidence)* Gorilla APIBench (1775): claude-v1 8.7; gpt-4-0314 21.2; gpt-3.5-turbo-0301 29.7; Gorilla llama-7b (fine-tuned) 75.0; OH v1.5 gpt-3.5-turbo-0125 21.6, gpt-4o 36.4 (L534-535).
- *(medium confidence)* ToolQA easy (800): ChatGPT+CoT 5.1; ChatGPT 5.6; Chameleon 10.6; ReAct gpt-3.5-turbo 36.8, gpt-3 43.1; OH v1.5 gpt-3.5-turbo-0125 2.3, gpt-4o 47.2 (L536).

**Web (Table 5, L562-614)**
- WebArena (812): Lemur-chat-70b 5.3; Patel et al. 72B 9.4; AutoWebGLM 7B 18.2; Auto Eval & Refine 20.2; WebArena Agent gpt-3.5-turbo 6.2, gpt-4-turbo 14.4; **OH BrowsingAgent v1.0: gpt-4o-mini 8.5, gpt-4o 14.8, claude-3-5-sonnet 15.5**; **OH CodeActAgent v1.8 via delegation to BrowsingAgent v1.0: 8.3 / 14.5 / 15.3**. Authors: BrowsingAgent is "competitive … among agents that use LLMs with domain-general prompting techniques" (L621).
- MiniWoB++ (125 environments): Workflow Guided Exploration 34.6; CC-NET 91.1; OH BrowsingAgent v1.0 gpt-3.5-turbo-0125 27.2, gpt-4o 40.8; OH CodeActAgent v1.8 via delegation (gpt-4o) 39.8.

**Misc. assistance (Table 6, L633-769)**
- GAIA L1 validation (53): AutoGPT gpt-4-turbo 13.2; **OH GPTSwarm v1.0 gpt-4-0125-preview 30.2, gpt-4o 32.1**. No CodeActAgent result is reported.
- GPQA diamond (198): expert human 81.3 (Table 6; **81.2 in Table 7**); non-expert human 21.9; few-shot CoT gpt-3.5-turbo-16k 29.6, gpt-4 38.8; **OH CodeActAgent v1.8 claude-3-5-sonnet-20240620 52.0**.
- AgentBench OS (144): baseline gpt-4 42.4, gpt-3.5-turbo 32.6; **OH CodeActAgent v1.5 gpt-4o 57.6**; gpt-3.5-turbo-0125 11.8.
- MINT math (225): baseline gpt-4-0613 65.8; **OH v1.5 gpt-4o 77.3**; gpt-3.5-turbo-16k-0613 33.8.
- MINT code (136): baseline gpt-4-0613 59.6; OH v1.5 gpt-4o 50.0; gpt-3.5-turbo-16k-0613 5.2. OH is below the baseline here.
- ProofWriter (600): few-shot CoT gpt4 68.1; Logic-LM (gpt4 + symbolic solver) 79.6; OH v1.5 gpt-4o 78.8.
- Entity Deduction Arena (200): zero-shot gpt-4-0314 40.0, gpt-3.5-turbo-0613 27.0; OH v1.5 gpt-4o 38.0, gpt-3.5-turbo-16k-0613 24.0.

**GPQA full (Table 7, App. G, L979-1045)**, values for Diamond / Main / Extended:

| Method | Diamond | Main | Extended |
|---|---|---|---|
| Expert humans | 81.2 | 72.5 | 65.4 |
| Non-expert humans | 21.9 | 30.5 | 33.9 |
| Few-shot CoT Llama-2-70B-chat | 28.1 | 29.1 | 30.4 |
| Few-shot CoT GPT-3.5-turbo-16k | 29.6 | 28.0 | 28.2 |
| Few-shot CoT GPT-4 | 38.8 | 39.7 | 38.7 |
| GPT-4 with search | 38.8 | 41.0 | 39.4 |
| **OH CodeActAgent v1.5 + GPT-3.5-turbo** | **27.9** | **23.4** | **26.1** |
| **OH CodeActAgent v1.5 + GPT4-turbo** | **51.8** | **47.4** | **42.4** |
| **OH CodeActAgent v1.5 + GPT4o** | **53.1** | **49.3** | **52.8** |

Average cost for the three OH rows: 0.012 / 0.501 / 0.054.

**Project-scale facts (not experimental results):** "32K GitHub stars and more than 2.1K contributions from over 188 contributors" (L124). MIT license (L7, L124).

## 11. Supported claims (measured/observed)
- CodeActAgent v1.8 + claude-3.5-sonnet resolves 26.0% of SWE-Bench Lite, without hint text.
- CodeActAgent v1.5 + gpt-4o fixes 79.3% of HumanEvalFix Python bugs, 0-shot.
- CodeActAgent v1.8 + claude-3.5-sonnet scores 52.0% on GPQA diamond. Non-expert humans score 21.9% and expert humans 81.3/81.2%.
- CodeActAgent v1.5 + gpt-4o scores 57.6% on AgentBench OS, against 42.4% for the gpt-4 baseline. On MINT math it scores 77.3% against 65.8%.
- BrowsingAgent v1.0 + claude-3.5-sonnet scores 15.5% on WebArena. GPTSwarm v1.0 + gpt-4o scores 32.1% on GAIA L1.
- The 15 benchmarks are integrated and evaluated in one framework.

## 12. Derived / comparative claims (authors' framing)
- 79.3% on HumanEvalFix is "significantly better than all non-agentic approaches, almost doubling the performance of StarCoder2-15B" (48.6) (L466). Arithmetically the ratio is about 1.63x. This is recorded as the authors' phrasing.
- 26% on SWE-Bench Lite is "competitive … compared to other open-source SWE specialists" (L464). It is below Aider (26.3), Moatless (26.7), and Agentless (27.3), so it is not a state-of-the-art claim.
- "The same CodeAct agent, without any modifications to its system prompt, demonstrates competitive performance across three major task categories" (L461). *Scope:* in Table 3, the web number for CodeActAgent (15.3) is obtained **via delegation to BrowsingAgent v1.0** (Table 5, L578). The Table 3 GAIA column for CodeActAgent is empty; GAIA 32.1 is GPTSwarm's.

## 13. Interpretations
- Cross-domain competitiveness is attributed to a design that puts generality first, as opposed to category-specific baselines (L461).
- Reaching 100% on HumanEvalFix is "entirely feasible" because the bugs are human-created and validated. This is a future goal (L466-548).
- Software is "the ideal interface" for agents (L17).
- OpenHands helps mitigate risks through systematic evaluation, human-agent interaction instead of unsupervised autonomy, and by enabling safety research (App. B, L896-899).
- OpenHands' infrastructure "simplifies the integration significantly" for GAIA (L626).

## 14. Hypotheses / future work
Future directions listed in App. A (L886-894): principled multi-modality (images and video via a browser, XLSX via code); stronger agents through training and inference-time techniques; better editing of long files; Auto Eval & Refine as an optional browsing component ("will be integrated"); GPTSwarm and LangGraph as possible routes to automatic workflow generation.

## 15. Limitations
**Author-stated:**
- "Current agents still struggle with complex tasks" (L887).
- "Current agent suffers a lot when editing long files" (L892).
- The workflow "still requires a substantial handcrafted workload" (L894).
- "OpenHands agents may not achieve top performance in every category" (L461).
- Most agents "lack the ability to perform complex, long-horizon tasks in the real world reliably" (L896).
- There are "challenges in developing safe and reliable agents" (L777).

**Scope conditions stated by the authors** (these are conditions, not critiques):
- All SWE-Bench results are without hint text (L464).
- HumanEvalFix compares OpenHands 0-shot with SWE-Agent 1-shot (L466).
- Comparisons use only open-source reproducible baselines without benchmark-specific prompt engineering (L257).
- MiniWoB++ includes environments that need vision, but the full set is reported (L622).

**Verifier-observed facts from the tables** (not claimed by the authors as limitations): OpenHands is below the baseline on MINT code (50.0 vs 59.6), ProofWriter (78.8 vs Logic-LM 79.6), EDA (38.0 vs gpt-4-0314 40.0), and HumanEvalFix (vs 1-shot SWE-Agent).

## 16. Actual contribution
An open-source, MIT-licensed, community-built platform that provides:
- an event-stream agent/runtime abstraction;
- a Docker-sandboxed runtime that supports arbitrary base images;
- the AgentSkills tool library;
- an AgentHub of more than 10 agents, led by the CodeAct-based generalist;
- multi-agent delegation;
- integration tests for agent QC;
- an evaluation framework covering 15 benchmarks.

These come with an evaluation showing that one generalist agent, with no benchmark-specific prompts, is competitive across software, web, and miscellaneous tasks (§1, §5 L777).

## 17. Weakly supported / unverifiable in snapshot
- Table 1's feature comparison cannot be read from this snapshot (L209-249). Any gap claim that depends on it cannot be verified here.
- "Almost doubling" StarCoder2-15B is loose phrasing for a 1.63x ratio (L466).
- The generality claim depends in part on delegation to a specialist browsing agent (§12).

## 18. Claim → evidence table

| Claim | Type | Location | Quote (≤25 words) |
|---|---|---|---|
| Platform for agents that write code, use CLI, browse | Contribution | L7 | "a platform for the development of powerful and flexible AI agents that interact with the world" |
| SWE-Bench Lite 26.0 (v1.8, claude) | Measured | L464, L529 | "achieves a competitive resolve rate of 26% compared to other open-source SWE specialists" |
| HumanEvalFix 79.3 (v1.5, gpt-4o, 0-shot) | Measured | L466, L489-491, L530 | "OpenHands CodeActAgent successfully fixes 79.3% of bugs in the Python split" |
| SWE-Agent 87.7 is 1-shot | Measured + scope | L466 | "provides the model a full demonstration of a successful sample trajectory" |
| GPQA diamond 52.0 (v1.8, claude) | Measured | Table 6, L666-670 | "OH CodeActAgent v1.8 claude-3-5-sonnet-20240620 52.0" |
| GPQA diamond 53.1 (v1.5, gpt-4o) | Measured | Table 7, L984, L1036; Table 3 L451 | "OpenHands + CodeActAgent v1.5 + GPT4o" |
| GAIA 32.1 is GPTSwarm | Measured | Table 6, L642-650 | "OH GPTSwarm v1.0 … gpt-4o-2024-05-13 32.1" |
| AgentBench OS 57.6 vs 42.4 | Measured | Table 6, L672-684 | "AgentBench … OS (bash) subset, 144 instances" |
| WebArena BrowsingAgent 15.5; delegation 15.3 | Measured | Table 5, L574-602 | "OH CodeActAgent v1.8 via delegation to BrowsingAgent v1.0" |
| 15 benchmarks integrated | Contribution | L257 | "we integrate 15 established benchmarks into OpenHands" |
| Not top in every category | Limitation (author) | L461 | "OpenHands agents may not achieve top performance in every category" |
| Agents struggle on complex tasks | Limitation (author) | L887 | "Current agents still struggle with complex tasks" |
| Long-file editing weak | Limitation (author) | L892 | "Current agent suffers a lot when editing long files" |
| Workflow handcrafted | Limitation (author) | L894 | "still requires a substantial handcrafted workload" |
| Full SWE-Bench cost | Stated | L467 | "Running the complete set of 2294 instances costs $6.9k" |
| Expert-human 81.3 vs 81.2 | Paper-internal conflict | L658 vs L988 | Table 6 "81.3" vs Table 7 "81.2" |
| gpt-4o-mini SWE-Bench 6.3 vs 7.0 | Paper-internal conflict | L366 vs L529 | Table 3 "6.3" vs Table 4 "7.0" |

## 19. Artifact notes (README-derived, not research claims, not scored)
- `OpenHands/OpenHands` at the pinned commit is **"Agent Canvas"**, "the self-hosted developer control center for coding agents and automations" (README L5-7). It can run OpenHands, Claude Code, Codex, Gemini, or ACP agents (L10). The system is now split across `OpenHands/OpenHands` (frontend), `OpenHands/software-agent-sdk` (SDK, Agent Server, agents, tools, events), `OpenHands/typescript-client`, and `OpenHands/automation` (L139-150). None of these describe the paper's system.
- `OpenHands/benchmarks` is a V1 evaluation harness under "Migration in Progress" from "benchmarks from OpenHands V0" to the Software Agent SDK (L5). It lists SWE-Bench, SWE-Bench Pro, GAIA, Commit0, OpenAgentSafety, and ProgramBench (L9-16). Only SWE-Bench and GAIA overlap with the paper's 15 benchmarks.
- The paper's code link is `github.com/All-Hands-AI/OpenHands` (L8). The READMEs use the `OpenHands` org.
- **Authority rule:** wherever these conflict with the paper, the paper governs research content. The READMEs govern only facts about the current repositories. See VERIFICATION.md for the suitability judgement.
