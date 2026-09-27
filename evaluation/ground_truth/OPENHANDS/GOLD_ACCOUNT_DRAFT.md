# Gold Account Draft — OPENHANDS

Snapshot-only factual ledger. Source files: `evaluation/external_projects/OPENHANDS/snapshot/paper.txt` (arXiv 2407.16741v3, ICLR 2025), `README__OpenHands__OpenHands.md` (repo `OpenHands/OpenHands` @ `b0906809b3e8777491519c386d55ce32d7f4daa4`), `README__OpenHands__benchmarks.md` (repo `OpenHands/benchmarks` @ `405bae7140d7e961a75f4910a0b2e7069731db96`). Per the task rule: **the paper is authoritative for research claims; README material is used only for artifact facts**, and is explicitly flagged wherever it conflicts with or diverges from the paper.

## 1. Problem

Building AI agents that can effectively interact with the world through software — writing code, executing it, and browsing the web — is hard: it requires enabling agents to create/modify code in complex systems, gather information on the fly to debug, and do so safely without negative side effects on users' systems (paper §1, paper.txt ¶ "However, building agents that can effectively develop software comes with its own unique challenges...", line 17).

## 2. Motivation

Software is described as one of the most powerful tools available to humans, letting a skilled programmer affect the world in complex ways; improvements in LLMs have produced rapid growth in AI agents that interact with and change their environment (paper Abstract, line 7). Software provides, in the authors' view, "the ideal interface for AI agents to interact with the world in complex ways," given existing tooling for its development, use, and deployment (paper §1, line 17).

## 3. Research gap

Numerous open-source agent frameworks already exist (AutoGPT, LangChain, MetaGPT, AutoGen, AutoAgents, etc.), each generally offering: (1) interfaces for agents to act on the world, (2) environments for the agent to operate in, (3) interaction mechanisms for human-agent or agent-agent communication (paper §1, line 11). The paper's own Table 1 attempts to compare these frameworks on features (GUI, standardized tool library, built-in sandbox, built-in web browser, multi-agent collaboration, human-AI collaboration, AgentHub, evaluation framework, agent QC) — **however, the cell contents of Table 1 were lost during pdftotext extraction** (only framework names and column headers survive; see §10 and §17). The qualitative gap the authors assert (but for which the comparison table itself is illegible in this snapshot) is that no single framework combines all of: standardized tool library + sandboxed code execution + web browser + AgentHub + evaluation framework + agent QC, in a way general enough for both software-engineering and general-purpose tasks (paper §1 intro to Table 1, line 11).

## 4. Research question / objective

To build a community-driven, general platform ("OpenHands," f.k.a. OpenDevin) for developing generalist and specialist AI agents that interact with the world through software, providing: an event-stream interaction mechanism, a sandboxed runtime environment, a human-developer-like environment interface, multi-agent delegation, and an evaluation framework, all as an "immediately usable implementation," not just a conceptual framework (paper §1, line 17).

## 5. System / method

- **Event stream architecture**: a chronological list of past Actions and Observations forms the agent's "State"; the agent maps event history to a new Action, and the Runtime maps Actions to Observations (paper §2.1, lines 128-130, 141-181; Fig. 2/3).
- **Action space**: `IPythonRunCellAction` and `CmdRunAction` (execute Python/bash in the sandbox), `BrowseInteractiveAction` (browser DSL from BrowserGym) — inspired by CodeAct (Wang et al., 2024a) (paper §2.1, line 131).
- **Agent implementation**: minimal agent = a `step(state)` function returning an Action; example given in Fig. 3 (paper §2.1, lines 141-181).
- **Runtime**: for each task session, a Docker-sandboxed container is spun up; OpenHands connects via a REST "action execution API" inside the container that hosts a bash shell, a Jupyter IPython server, and a Playwright/Chromium browser using BrowserGym action primitives (paper §2.2, lines 184-193). Arbitrary user-provided Docker base images are supported by building an "OH runtime image" on top of them (paper §2.2, line 194; Appendix F).
- **AgentSkills library**: a Python toolbox auto-imported into the IPython environment, adding tools only when (1) not readily achievable by an LLM writing code directly, and/or (2) an external model call is required (e.g. speech-to-text, PDF/DOCX/LaTeX parsing, image/video/pptx parsing) (paper §2.3, lines 195-199; full function list Appendix I).
- **Multi-agent delegation**: `AgentDelegateAction` lets one agent hand off a subtask to another, e.g. a generalist CodeActAgent delegating web browsing to a specialized BrowsingAgent (paper §2.4, line 201).
- **AgentHub agents**: CodeActAgent (default generalist, based on CodeAct), BrowsingAgent (zero-shot web baseline, similar to WebArena's agent but improved observations/actions), GPTSwarm Agent (optimizable-graph agent integration), and Micro Agents (lightweight, task-specialized agents reusing a generalist agent's implementation) (paper §3, lines 202-253).
- **Quality control**: an end-to-end integration-test framework that mocks LLM calls with stored prompt-response pairs for deterministic regression testing, run across platforms/sandboxes on every PR and main-branch commit (paper Appendix E, lines 910-911).

## 6. Architecture

Three main components per Fig. 2 (paper.txt line 121): (1) **Agent abstraction** — pluggable agent implementations contributed to "agenthub"; (2) **Event stream** — tracks the history of actions/observations; (3) **Runtime** — executes actions into observations via the Docker sandbox and action execution API. The Runtime build/tagging system uses a dual-tag scheme: a hash-based tag (MD5 of build folder/source+Dockerfile, guarantees reproducibility) and a generic tag (`oh_v{VERSION}_{BASE_IMAGE}_tag_{IMAGE_TAG}`, tracks the latest build for a base-image/version combo) (paper Appendix F.2.1, lines 931-947).

## 7. Dataset / data

No new dataset is introduced. The paper integrates 15 pre-existing third-party benchmarks as its evaluation material (Table 2, paper.txt lines 259-271): SWE-Bench (incl. SWE-Bench Lite), HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA (software); WebArena, MiniWoB++ (web); GAIA, GPQA, AgentBench, MINT, Entity Deduction Arena, ProofWriter (misc. assistance).

## 8. Experimental setup

- SWE-Bench Lite: 300 instances, without hint text; full 2294-instance set costs an estimated $6.9k, so Lite is used for cost reasons (paper §4.2, lines 464, 467).
- HumanEvalFix: Python subset, 164 instances; agent allowed multi-turn self-debug using test-execution feedback; OpenHands evaluated 0-shot vs. SWE-Agent's 1-shot (line 466).
- ML-Bench: quarter subset, 68 instances, following the original paper's setup (line 550).
- Gorilla APIBench: 1775 instances, correctness = whether the API call is in the correct domain (line 552).
- ToolQA: easy subset (of easy/hard split) used (line 554).
- BioCoder: 157 Python (+50 Java) functions; relevant-context prompt portion removed to test OpenHands's own context retrieval (lines 556, 616).
- BIRD: 300 samples from the dev set; extended with multi-turn interaction allowing the agent to correct SQL based on execution feedback (line 617).
- WebArena: 812 human-curated task instructions (line 621).
- MiniWoB++: 125 environments, full set reported, only baselines evaluated on the full set included for comparison (line 622).
- GAIA: L1 validation set, 53 instances used for the headline Misc. table (Table 6); 466 curated tasks across 3 levels described overall (lines 626, 638).
- GPQA: diamond set (198 instances) is the headline subset; main/extended subsets also reported in Appendix G, Table 7 (lines 652, 973-1046).
- AgentBench: OS (bash) subset, 144 instances (line 672).
- MINT: math subset 225 instances, code subset 136 instances; agent gets up to 5 iterations with 2 chances to propose a solution (lines 690, 708, 772).
- ProofWriter: 600-instance 5-hop-reasoning subset; logical forms from Logic-LM reused to reduce parsing error impact (line 726, 773).
- Entity Deduction Arena: "Things" and "Celebrities" datasets, 100 instances each, average success rate reported over both (line 744, 774).

## 9. Metrics

Success/resolve rate (%) is the primary metric throughout (e.g. SWE-Bench "resolve rate," HumanEvalFix "% bugs fixed," BIRD "execution accuracy," GAIA/GPQA/AgentBench/MINT/ProofWriter/EDA "success rate" / "accuracy"). Many result tables also report **average USD cost per instance** ($ Avg. Cost columns, Tables 3-7).

## 10. Results (exact numbers, with table/section)

Numbers below are restricted to those independently corroborated by prose next to the relevant table (see PROJECT_ASSESSMENT.md Risk 3 — pdftotext detached many table rows from their numeric columns):

- SWE-Bench Lite (Table 3/4, §4.2, line 464): CodeActAgent v1.8 + claude-3-5-sonnet = **26.0%** resolve rate ("a competitive resolve rate of 26%"). Baselines in the same table: SWE-Agent (gpt-4-1106-preview) 18.0%, AutoCodeRover (gpt-4-0125-preview) 19.0%, Aider (gpt-4o & claude-3-opus) 26.3%, Moatless Tools (claude-3.5-sonnet) 26.7%, Agentless (gpt-4o) 27.3% (Table 3, lines 294-316).
- HumanEvalFix, Python split, 164 instances (Table 4, §4.2.1, lines 466, 530): CodeActAgent (0-shot) = **79.3%**; SWE-Agent (1-shot, gpt-4-turbo) = **87.7%**. Non-agentic baselines in the same table: BLOOMZ-176B 16.6%, OctoCoder-15B 30.4%, DeepSeekCoder-33B-Instruct 47.5%, StarCoder2-15B 48.6% (text states OpenHands "almost doubling the performance of StarCoder2-15B" — 79.3 / 48.6 ≈ 1.63×, i.e. not quite double by strict arithmetic; recorded as stated by the authors, see §13).
- GPQA diamond set, 198 instances (Table 7, Appendix G, lines 652-670): expert human 81.3%(also reported as 81.2 in Table 7 header row — **numeric inconsistency between §4.4 text (81.3) and Table 7 (81.2); both recorded, location noted**), non-expert human 21.9%; few-shot CoT gpt-3.5-turbo 29.6%, gpt-4 38.8%; CodeActAgent v1.8 + claude-3-5-sonnet = **52.0%**.
- AgentBench OS subset, 144 instances (Table 6/text, lines 672-684): baseline gpt-4 42.4%, gpt-3.5-turbo 32.6%; CodeActAgent v1.5 + gpt-4o = **57.6%**; + gpt-3.5-turbo-0125 = 11.8%.
- MINT math subset, 225 instances (lines 690-702): baseline gpt-4-0613 65.8%; CodeActAgent v1.5 + gpt-4o = **77.3%**; + gpt-3.5-turbo-16k-0613 = 33.8%.
- MINT code subset, 136 instances (lines 708-724): baseline gpt-4-0613 59.6%; CodeActAgent v1.5 + gpt-4o = 50.0%; + gpt-3.5-turbo-16k-0613 = 5.2%.
- ProofWriter, 600 instances (lines 726-742): few-shot CoT gpt4 68.1%, Logic-LM (gpt4+solver) 79.6%; CodeActAgent v1.5 + gpt-4o = **78.8%**.
- Entity Deduction Arena, 200 instances (avg. of two 100-instance sets) (lines 744-760): zero-shot gpt-4-0314 40.0%, gpt-3.5-turbo-0613 27.0%; CodeActAgent v1.5 + gpt-4o = **38.0%**, + gpt-3.5-turbo-16k-0613 = 24.0%.
- Table 3 also gives WebArena and Misc. columns for the same agents (e.g. CodeActAgent v1.8 + claude-3-5-sonnet: WebArena 15.3%, GPQA 52.0%, GAIA 32.1% — read from the aligned final rows of Table 3, lines 372-459); these are recorded with lower confidence since Table 3's raw text block interleaves multiple columns (see PROJECT_ASSESSMENT.md Risk 3).
- 32K GitHub stars, 2.1K+ contributions, 188+ contributors (paper §1/Abstract, lines 7, 124) — project-scale facts, not experimental results.
- SWE-Bench Lite full-set cost estimate: ~$6.9k (2294 instances, ~$3/instance) (footnote 2, line 467).

**NOT IN SNAPSHOT**: full, unambiguous numeric extraction of every row of Tables 1, 3, 5, and 6 (framework-comparison checkmarks and several BIRD/ML-Bench/Gorilla/ToolQA/WebArena/MiniWoB++ result rows) — pdftotext detached labels from numbers; only the rows explicitly cross-checked against prose above are asserted.

## 11. Supported claims (directly measured/observed)

- CodeActAgent v1.8 + claude-3.5-sonnet resolves 26.0% of SWE-Bench Lite instances (measured, §4.2).
- CodeActAgent (0-shot) fixes 79.3% of HumanEvalFix Python bugs (measured, §4.2.1).
- CodeActAgent v1.8 + claude-3.5-sonnet scores 52.0% on GPQA diamond, vs. 21.9% for non-expert humans and 81.3%/81.2% for expert humans (measured, §4.4/Appendix G).
- CodeActAgent v1.5 + gpt-4o scores 57.6% on AgentBench's OS subset vs. baseline gpt-4's 42.4% (measured, §4.4).
- OpenHands integrates 15 benchmarks into a single evaluation framework (directly stated/implemented, §4, Table 2).
- The repository had 32K GitHub stars and 2.1K+ contributions from 188+ contributors as of writing (directly stated, §1).

## 12. Derived claims (computed/comparative)

- "Almost doubling the performance of StarCoder2-15B" on HumanEvalFix (79.3% vs. 48.6%) — authors' comparative framing of two measured numbers (§4.2.1, line 466); arithmetically this is a ~1.63× ratio, recorded as the authors phrased it.
- CodeActAgent's SWE-Bench Lite score (26.0%) is presented as "competitive" against contemporaneous open-source SWE specialist baselines (18.0%-27.3% range) — a comparative framing, not a claim of state-of-the-art (§4.2).
- The same, unmodified CodeAct agent (same system prompt) performs competitively across software, web, and misc. categories simultaneously, which the authors contrast with baseline agents "typically designed and optimized for specific task categories" (derived/comparative claim, §4.1, line 461).

## 13. Interpretations (authors' explanations — label as interpretation)

- (Interpretation) The authors attribute OpenHands's cross-domain competitiveness to its generality-first design rather than task-specific optimization (§4.1, line 461).
- (Interpretation) The authors suggest that, because HumanEvalFix bugs are "carefully validated," achieving 100% is "entirely feasible," which they set as a goal for future iterations (§4.2.1, line 548) — a forward-looking interpretation, not a measured result.
- (Interpretation) The authors frame software as "the ideal interface for AI agents to interact with the world in complex ways" (§1, line 17) — a motivating claim/interpretation, not an experimental finding.
- (Interpretation) The authors describe OpenHands as helping "mitigate risks" of increasingly capable, deployed AI agents via systematic evaluation, human-agent interaction rather than full autonomy, and enabling frontier safety research (Ethics Statement, Appendix B, lines 896-899) — a stated position, not a measured outcome.

## 14. Hypotheses / speculation

- (Future work / speculation) Graph-based frameworks such as GPTSwarm and LangGraph "could serve as alternative solutions for building agents" and "lay the groundwork for promising solutions in automatic workflow generation in future versions" (Appendix A, line 894) — explicitly forward-looking, not demonstrated.
- (Future work) Enhanced multi-modality (viewing images/video via browser, processing XLSX via code), stronger agents via training/inference-time techniques, and improved long-file editing are all listed as future directions, not implemented/evaluated capabilities (Appendix A, lines 886-892).

## 15. Limitations

- Authors' own stated limitation: "Current agents still struggle with complex tasks" (Appendix A, "Stronger agents," line 887).
- Authors' own stated limitation: "Current agent suffers a lot when editing long files" (Appendix A, "Agent editing improvements," line 892).
- Authors' own stated limitation: OpenHands's workflow "still requires a substantial handcrafted workload" (automatic workflow generation is not yet solved) (Appendix A, line 894).
- Scope boundary (derived from stated conditions): SWE-Bench results are reported "without using hint text" throughout the paper (§4.2, line 464) — any comparison to hint-text-using systems is out of scope of these numbers.
- Scope boundary (derived from stated conditions): HumanEvalFix results for OpenHands are 0-shot, while the SWE-Agent comparison point (87.7%) is 1-shot with a full demonstration trajectory — the two numbers are not evaluated under identical prompting conditions (§4.2.1, line 466).
- Scope boundary (derived from stated conditions): the paper explicitly restricts to "open-source reproducible baselines that do not perform manual prompt engineering specifically based on the benchmark content" for comparison (§4, line 257) — results should not be read as a comparison against arbitrarily-tuned closed baselines.

## 16. Actual contribution

A single, general, open-source, MIT-licensed platform that (1) defines a reusable event-stream agent/runtime abstraction, (2) provides a safe Docker-sandboxed execution environment supporting arbitrary user base images, (3) ships an AgentSkills tool library and AgentHub of community agents (led by a CodeAct-based generalist), (4) supports multi-agent delegation, and (5) integrates 15 evaluation benchmarks into one framework, together with an empirical evaluation showing one unmodified generalist agent performing competitively across software-engineering, web-browsing, and miscellaneous-assistance tasks (§1, §5/Conclusion, line 777).

## 17. Unsupported or weakly supported claims (thin support in snapshot)

- The framework-comparison Table 1 (paper.txt lines 209-249), which is meant to substantiate the "no existing framework combines all these features" gap claim, is **not evaluable from this snapshot** — pdftotext extraction dropped the cell contents (checkmarks/bullets), leaving only a list of framework names and a list of column headers with no visible mapping between them. The qualitative gap claim in §3 (Section header text) therefore rests on a table whose supporting content is illegible here; we cannot confirm or deny it from the snapshot.
- "Almost doubling the performance of StarCoder2-15B" (79.3% vs. 48.6%, a ~1.63× ratio) is a comparative characterization that is looser than the underlying numbers strictly support; recorded as authors' own framing, not strengthened (§4.2.1, line 466).
- The GPQA expert-human baseline is given as 81.3% in the §4.4 narrative area (line 658) but as 81.2% in Table 7 (line 988) — a minor internal numeric inconsistency in the paper itself (not a snapshot-extraction artifact, both numbers are legibly printed); recorded as a conflict, not resolved in the authors' favor of either value.

## 18. Claim → evidence → source table

| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| OpenHands is a platform for agents that interact via code, CLI, and browser | Contribution | Described in abstract | paper.txt line 7 | "a platform for the development of powerful and flexible AI agents that interact with the world" |
| CodeActAgent v1.8 + claude-3.5-sonnet resolves 26.0% of SWE-Bench Lite | Measured | Table 3/4 + prose | paper.txt line 464 | "achieves a competitive resolve rate of 26% compared to other open-source SWE specialists" |
| HumanEvalFix Python: CodeActAgent 0-shot = 79.3% | Measured | Table 4 + prose | paper.txt line 466 | "OpenHands CodeActAgent successfully fixes 79.3% of bugs in the Python split" |
| SWE-Agent 1-shot HumanEvalFix = 87.7% | Measured | Table 4 + prose | paper.txt line 466 | "SWE-Agent achieves 87.7%...provides the model a full demonstration" |
| GPQA diamond: CodeActAgent v1.8 + claude-3.5-sonnet = 52.0% | Measured | Table 7 | paper.txt line 670 | value listed in GPQA diamond-set results row for OH CodeActAgent v1.8 |
| AgentBench OS subset: CodeActAgent v1.5 + gpt-4o = 57.6% | Measured | §4.4 results block | paper.txt line 684 | value listed for OH CodeActAgent v1.5, gpt-4o-2024-05-13 |
| Full SWE-Bench Lite run costs ~$6.9k | Measured/stated | Footnote 2 | paper.txt line 467 | "Running the complete set of 2294 instances costs \$6.9k" |
| 15 benchmarks integrated | Contribution/stated | §4 intro | paper.txt line 257 | "we integrate 15 established benchmarks into OpenHands" |
| 32K GitHub stars, 2.1K+ contributions, 188+ contributors | Stated (project scale) | §1 | paper.txt line 124 | "32K GitHub stars and more than 2.1K contributions from over 188 contributors" |
| Current agents still struggle with complex tasks | Limitation (authors' own) | Appendix A | paper.txt line 887 | "Current agents still struggle with complex tasks" |
| Agents suffer editing long files | Limitation (authors' own) | Appendix A | paper.txt line 892 | "Current agent suffers a lot when editing long files" |
| Workflow generation still handcrafted | Limitation (authors' own) | Appendix A | paper.txt line 894 | "OpenHands's workflow still requires a substantial handcrafted workload" |
| GPTSwarm/LangGraph could enable automatic workflow generation | Speculation/future work | Appendix A | paper.txt line 894 | "could serve as alternative solutions for building agents" |
| Framework Table 1 feature comparison is illegible in snapshot | Extraction defect | Table 1 | paper.txt lines 209-249 | table lists framework names and column headers with no recoverable cell values |
| GPQA expert-human baseline stated as both 81.3% and 81.2% | Internal conflict | §4.4 text vs. Table 7 | paper.txt lines 658, 988 | "Expert human...81.3" (line 658) vs. Table 7 "Expert Human Validators...81.2" (line 988) |
| Current `OpenHands/OpenHands` README describes "Agent Canvas," not the paper's platform | Repo/paper conflict | README, artifact fact only | README__OpenHands__OpenHands.md lines 5-7 | "The self-hosted developer control center for coding agents and automations" |
| `OpenHands/benchmarks` repo overlaps paper's benchmark suite in only SWE-Bench and GAIA | Repo/paper conflict | README, artifact fact only | README__OpenHands__benchmarks.md lines 9-16 | "Migration in Progress...migrating the benchmarks from OpenHands V0...to work with...V1" |
