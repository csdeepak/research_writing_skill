# Corpus log

## Run-specific constraints in effect (override the skill's default literature protocol)
- No web access. Literature mode is limited to works already cited in `project/paper.txt`.
- Every registered source (`corpus/source_registry.json`) is filed with `verification.method =
  "user_supplied_file"` and `read_depth = "abstract"`, because the original works themselves
  cannot be opened. Concretely, this means every `establishes[].support_quote` is drawn from
  **paper.txt's own characterization** of the cited work (i.e. what the citing paper says that
  source does/found), not from the source's own text. This is disclosed here once rather than
  in every registry entry. No DOI/index lookup was performed; any `doi` field recorded is copied
  verbatim from paper.txt's own reference list and was not independently resolved.
- `level` is set to `2` (verified only via the citing document, not independently retrieved) for
  every registered source, since the schema's enum has no "Level 0 / user-supplied" value. This
  is an explicit assumption, recorded here and in `state.json -> accepted_risks`.

## "Queries" (facets used to decide what to register)
Because there is no search step, the "query facets" below describe how sources already present
in paper.txt were selected for registration, not search strings sent to an index.
1. Facet: **framework-gap** dimension for spine lines 1-2 / story-graph node N04. Selected every
   framework paper.txt's own Related Work appendix (§C) characterizes with a specific capability
   or limitation sentence: LangChain/LangGraph, AutoGen, CrewAI, BrowserGym, DSPy, MetaGPT,
   GPTSwarm, SWE-Agent, AutoCodeRover, Agentless, ChatDev, AgentCoder, AutoGPT. -> SRC-001-010,
   023-026 (CodeAct and AutoGPT also serve this facet).
2. Facet: **benchmark identity** for every benchmark actually cited with a number in the draft:
   SWE-Bench, HumanEvalFix, WebArena, MiniWoB++, GAIA, GPQA, AgentBench, MINT, ProofWriter,
   Entity Deduction Arena. -> SRC-011, 012, 013, 014, 016, 017, 018, 019, 020, 022.
3. Facet: **named comparator baseline** for every non-OpenHands agent that appears by name with a
   number in a table used in the draft: Logic-LM (ProofWriter), CC-Net (MiniWoB++), Lemur, the
   trained-72B agent of Patel et al. (2024), AutoWebGLM, and Auto Eval & Refine (all WebArena).
   -> SRC-015, 021, 027, 028, 029, 030.

## Screening / exclusions
- **Aider (Gauthier)** and **Moatless Tools (Örwall)**: appear as SWE-Bench Lite baselines in
  paper.txt's own tables, but neither has a publication year anywhere in paper.txt's reference
  list. `source_registry.schema.json` requires `year` as an integer, and the hard rule against
  inventing bibliographic fields forbids guessing one. **Excluded** from the registry and from
  the draft's SWE-Bench Lite comparison (which already has three citable comparators: SWE-Agent,
  AutoCodeRover, Agentless). See `evidence/missing_evidence.json` (MISS-005).
- **Devin (Cognition.ai)**: named in paper.txt only as the naming inspiration for OpenHands
  (f.k.a. OpenDevin); also undated in the reference list. Not needed for any claim in the draft
  (the "f.k.a. OpenDevin" fact itself is taken directly from the abstract, which needs no
  citation), so it is simply not registered or cited.
- **Reflexion (Shinn et al., 2024)**: appears only as a component *inside* Auto Eval & Refine
  (SRC-030); not cited on its own in the draft, so not separately registered.
- **BIRD, ML-Bench, BioCoder, Gorilla APIBench, ToolQA** (Table 2's remaining software
  benchmarks): mentioned descriptively in the draft (task type only, from the undamaged Table 2)
  because their scores live in Table 4's column-flattened block, whose row alignment could not be
  recovered with confidence for those four/five sub-tables (see `evidence/missing_evidence.json`,
  MISS-002). No sources specific to those benchmarks were registered, since no number attributed
  to them appears in the draft.

## Suspicious content
None found. No instruction-like text aimed at models/reviewers was present in `project/paper.txt`
or `project/README_*.md`.

## Stopping reason
All sources needed to support every citation planned for the draft (framework-gap dimension +
every benchmark/baseline named with a number) are registered. Since no further search is
possible (no web) and no further citable material exists in the two project files, registration
is complete; this is a hard stop, not a saturation judgment.
