# Project Assessment — OPENHANDS

Basis: frozen snapshot only (`evaluation/external_projects/OPENHANDS/snapshot/`: `paper.txt`, `README__OpenHands__OpenHands.md`, `README__OpenHands__benchmarks.md`) plus `evaluation/manifests/source_snapshots.json` for pins. Venue status uses the paper's own self-declared header line (no external web search was performed for this pass; the paper text itself is sufficient and is cited below).

## Project description

The paper (arXiv 2407.16741v3, "OpenHands: An Open Platform for AI Software Developers as Generalist Agents") documents **OpenHands** (f.k.a. OpenDevin): a community-driven, open-source platform for building and evaluating AI agents that act on the world through software — writing code, executing bash/Python in a sandboxed Docker environment, and browsing the web. It provides an event-stream interaction architecture, an "AgentHub" of community-contributed agent implementations (CodeActAgent, BrowsingAgent, GPTSwarm, Micro Agents), an extensible `AgentSkills` tool library, multi-agent delegation, and an evaluation framework integrating 15 benchmarks spanning software engineering, web browsing, and miscellaneous assistance (paper.txt lines 7, 17-21, 123, 255-266).

## Official repository (URL, pinned commit)

Two repositories are in the snapshot, and they are **not interchangeable**:

- `OpenHands/OpenHands` (paper's own cited code link is `https://github.com/All-Hands-AI/OpenHands`, the org's earlier name — `README__OpenHands__OpenHands.md` is pinned at commit `b0906809b3e8777491519c386d55ce32d7f4daa4`, per `source_snapshots.json`).
- `OpenHands/benchmarks`, pinned at commit `405bae7140d7e961a75f4910a0b2e7069731db96` (per `source_snapshots.json`) — a separate repository not mentioned anywhere in the paper (the paper predates it).

**Critical divergence found:** the current README of `OpenHands/OpenHands` does **not** describe the platform in the paper. It describes **"Agent Canvas"** — "The self-hosted developer control center for coding agents and automations," a frontend/control-center product that connects to pluggable agent backends (the OpenHands agent, but also third-party agents like Claude Code, Codex, Gemini, or any ACP-compatible agent) (README__OpenHands__OpenHands.md lines 1-11, 33-46). The README explicitly states the system has been split into multiple repositories: `OpenHands/OpenHands` (Agent Canvas frontend), `OpenHands/software-agent-sdk` (the actual "Python SDK, Agent Server, agents, tools, conversations, workspaces, events, and the canonical server API" — i.e., the successor to what the paper calls the "platform"), `OpenHands/typescript-client`, and `OpenHands/automation` (README lines 139-150). None of the paper's core technical vocabulary — event stream, AgentHub, CodeAct, Docker sandbox action-execution API, AgentSkills — appears in this README. This is a real repository/product evolution, not a snapshot artifact.

## Paper/report

- arXiv 2407.16741v3, "Published as a conference paper at ICLR 2025" (self-declared on the paper's own header line, paper.txt line 3). Original submission is older (arXiv id implies mid-2024); v3 is dated 18 Apr 2025 (paper.txt line 1), consistent with a post-ICLR-2025-acceptance camera-ready revision.
- Peer-review status: stated by the paper itself as an ICLR 2025 conference paper; this was not independently re-verified against OpenReview/ICLR proceedings in this pass (no web search performed). Treat as **paper-stated, not independently confirmed**.
- Authors span UIUC, CMU, Yale, UC Berkeley, Contextual AI, KAUST, ANU, HCMUT, Alibaba, and All Hands AI (paper.txt line 5).

## Datasets

The paper uses 15 pre-existing third-party benchmarks (not a newly released dataset of its own): SWE-Bench / SWE-Bench Lite, HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA, WebArena, MiniWoB++, GAIA, GPQA, AgentBench (OS subset), MINT (math/code subsets), Entity Deduction Arena, ProofWriter (Table 2, paper.txt lines 259-271). Each is cited to its original source paper; OpenHands does not claim authorship of any of these datasets.

## Benchmark/evaluation material

- Paper §4 (evaluation) and Appendix G give benchmark descriptions, per-benchmark result tables (Tables 3–7), and per-instance counts.
- The `OpenHands/benchmarks` repo snapshot describes a **different, newer** evaluation harness ("V1"), explicitly mid-migration from "OpenHands V0" evaluation code to work with a new "OpenHands Software Agent SDK" (README__OpenHands__benchmarks.md lines 1-5). Its "Available Benchmarks" table lists: SWE-Bench, SWE-Bench Pro, GAIA, Commit0, OpenAgentSafety, ProgramBench (lines 9-16).
- **Overlap with the paper's 15 benchmarks: only 2 (SWE-Bench, GAIA).** SWE-Bench Pro, Commit0, OpenAgentSafety, and ProgramBench do not appear in the paper at all (they postdate it). The paper's other 13 benchmarks (HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA, WebArena, MiniWoB++, GPQA, AgentBench, MINT, Entity Deduction Arena, ProofWriter) are **absent** from the current benchmarks repo's active list. This repo is explicitly a work-in-progress successor harness, not an archive of the paper's evaluation.

## Available experimental evidence

The paper itself is the only source of experimental evidence for its own claims. It reports agent success rates on the 15 benchmarks against baseline agents/frameworks (SWE-Agent, AutoCodeRover, Aider, WebArena Agent, AutoGPT, etc.), broken out per model (gpt-4o-mini, gpt-4o, claude-3.5-sonnet, gpt-3.5-turbo variants), with per-instance average USD cost for many rows (Tables 3–7, paper.txt lines 280–651, 973–1046). Neither README contains experimental results; both are artifact/usage documentation only.

## Available result evidence

Headline results independently confirmed by both a table cell *and* corroborating prose (higher confidence):
- SWE-Bench Lite: CodeActAgent v1.8 + claude-3-5-sonnet resolves 26.0% (Table 3/4; text: "achieves a competitive resolve rate of 26%", paper.txt line 464).
- HumanEvalFix (Python): CodeActAgent (0-shot) fixes 79.3% of bugs, vs. SWE-Agent's 87.7% (1-shot demonstration) (Table 4; text lines 466, 530).
- GPQA diamond set: CodeActAgent v1.8 + claude-3-5-sonnet = 52.0% (Table 3/7 cross-checked, line 670; vs. expert human 81.3%, non-expert human 21.9%, line 658).
- AgentBench OS subset: CodeActAgent v1.5 + gpt-4o = 57.6% vs. baseline gpt-4 42.4% (lines 684, 678).
- MINT math subset: CodeActAgent v1.5 + gpt-4o = 77.3% vs. baseline gpt-4-0613 65.8% (lines 700, 696).
- ProofWriter: CodeActAgent v1.5 + gpt-4o = 78.8%, vs. Logic-LM (gpt4 + symbolic solver) 79.6% (lines 740, 736).
- Entity Deduction Arena: CodeActAgent v1.5 + gpt-4o = 38.0% (line 756).

Numbers in Tables 3, 4, 5, 6, and 7 exist for many additional rows (e.g. BIRD, ML-Bench, BioCoder, Gorilla APIBench, ToolQA, WebArena, MiniWoB++), but **pdftotext extraction has detached row labels from their numeric columns** for large stretches of these tables (see Risks below). Only numbers independently corroborated by adjacent prose are treated as reliable in the Gold Account; the rest are recorded with an explicit "table order ambiguous" caveat or omitted.

## Source quality (authoritative vs. secondary)

- **Paper.txt**: authoritative primary source for all research claims (problem, method, architecture, experiments, results, limitations). ICLR-published, author-written.
- **README__OpenHands__OpenHands.md**: authoritative only for facts about the *current* `OpenHands/OpenHands` repository as of the pinned commit — which is a **different downstream product (Agent Canvas)**, not the research platform in the paper. Must not be used to describe the paper's system.
- **README__OpenHands__benchmarks.md**: authoritative only for facts about the current benchmarks-repo tooling; it is a successor evaluation harness under active migration, not a record of the paper's own evaluation setup.

## Reproducibility / accessibility

The paper states OpenHands is MIT-licensed with 32K GitHub stars, 2.1K+ contributions, 188+ contributors at time of writing (paper.txt line 124), and gives a cost estimate for full SWE-Bench Lite (2294 instances) at ~$6.9k (footnote 2, line 467). It documents an integration-test framework with mocked LLM responses for deterministic regression testing (Appendix E). However, the snapshot alone does not let us verify that the code, at the paper-time commit, is still runnable: the current `OpenHands/OpenHands` repo has since been repurposed as "Agent Canvas," and the agent/runtime code the paper describes now appears to live in the separate `OpenHands/software-agent-sdk` repo, which is not in this snapshot.

## Suitability for this evaluation

- **Can methodology be reconstructed?** Yes, from the paper alone — §2 (architecture: event stream, actions/observations, Docker sandbox, AgentSkills, delegation), §3 (AgentHub agents), §4 (evaluation setup) are self-contained and detailed, including a minimal code listing (Fig. 3) and a runtime workflow diagram description (Appendix F).
- **Are experiments & results identifiable?** Yes for the headline numbers cross-confirmed by prose; partially for the remaining table cells, where pdftotext has scrambled row/column alignment.
- **Can a factual Gold Account be written without guessing?** Yes, provided the Gold Account (a) draws System/method/Architecture/Results almost entirely from `paper.txt`, (b) uses the READMEs only for present-day artifact facts (license, install commands, current repo structure), and (c) explicitly flags the README/paper divergence rather than silently blending them.

## Risks

1. **Repository diverged sharply from the paper (major, evaluation-relevant).** `OpenHands/OpenHands`'s current README documents "Agent Canvas," a different, later product built around a multi-repo architecture (frontend / SDK / typescript-client / automation) that did not exist in the form described by the paper. A reconstruction reader who consults only the current README would form an incorrect picture of the paper's system. This is the single biggest risk for this evaluation and must be preserved as an explicit conflict in the Gold Account, not silently merged.
2. **Benchmarks repo is not the paper's evaluation harness.** `OpenHands/benchmarks` overlaps the paper's 15-benchmark suite in only 2 benchmarks (SWE-Bench, GAIA), adds benchmarks that postdate the paper (SWE-Bench Pro, Commit0, OpenAgentSafety, ProgramBench), and is self-described as "Migration in Progress." It cannot be used as evidence of the paper's own evaluation setup.
3. **pdftotext table damage.** Table 1 (framework feature-comparison matrix, paper.txt lines 209-249) lost all its checkmark/bullet cell contents during extraction — only framework names and column headers survive, with no way to recover which framework has which feature. Tables 3-7 have row labels and numeric columns separated into disjoint text blocks by the extractor; most rows are only recoverable by manual alignment or cross-checking against prose, and several remain ambiguous.
4. **Author-authorship note:** the "Author Contributions" section (paper.txt lines 878-883) is itself evidence of a large multi-institution collaborative effort tracked by PR count — useful context, not a scientific claim.
5. Results are from mid-2024-era models (gpt-4o-2024-05-13, claude-3-5-sonnet-20240620, etc.); absolute numbers are time-bound and not necessarily representative of current model performance, though this is a normal limitation of any benchmark paper, not a defect of the snapshot.

## Recommendation: ACCEPT WITH CAVEATS

The paper is complete, self-contained, ICLR-published, and gives exact, mostly-recoverable numbers with clear methodology — sufficient to build a rigorous Gold Account and 12-question reconstruction test. The caveat is structural, not about paper quality: **the official repository snapshot has diverged into an unrelated downstream product, and the benchmarks-repo snapshot is a disjoint successor evaluation harness.** Both facts are themselves valuable signal for a "does the reader correctly distinguish paper claims from repo-of-record claims" style question, but they must be handled explicitly (Section 15/17 of the Gold Account, and dedicated nuggets in `gold_story.json`) rather than treated as ordinary supplementary documentation. Any scoring rubric built on this project should expect that a reader who conflates "Agent Canvas" or the "benchmarks" repo's V1 harness with the paper's system is making a factual error, and should be scored accordingly.
