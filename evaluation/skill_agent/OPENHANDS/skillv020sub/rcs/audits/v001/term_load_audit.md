# Step 14 -- Terminology / cognitive-load audit

## Term ledger check
Checked every entry in `story/term_ledger.json` against the draft for `defined_at <=
first_used_at` and "one term per concept" (no synonym drift):
- **21 of 23 terms**: defined at or before first use, and used consistently (no synonym drift --
  e.g. "sandbox" is never called "container" as a stand-in term; "AgentSkills" is never called
  "tool library" after its own introduction).
- **2 exceptions, both accepted as a scope trade-off, not fixed**: GAIA and GPQA are named with
  their headline numbers in the Abstract (and again in the Introduction's contributions
  paragraph) before they are glossed in Results Section 5. A fully rigorous fix would gloss every
  benchmark at its very first mention, including inside the Abstract, but that would add a
  one-clause definition for four separate benchmark names inside an already-dense ~230-word
  abstract. Given that (a) abstracts conventionally name benchmarks tersely even for
  non-specialist readers (the audience already expects unfamiliar proper nouns attached to
  numbers in an abstract), (b) both terms are fully defined at their first *substantive* prose
  use in Section 5, only a few hundred words later, and (c) the numbers themselves are still
  interpretable in the Abstract without the gloss (percentage, higher-is-better, compared with
  named baselines), this is judged a defensible, disclosed simplification rather than a
  cognitive-load failure. Recorded here rather than silently left unaddressed.

## New-term rate (mode B: <=2 new terms/paragraph)
Sampled the Introduction and Method paragraphs (the densest sections for new vocabulary):
- Introduction para 1: 1 new term (agent, defined inline).
- Introduction para 3 (the gap paragraph): introduces ACI plus several framework proper nouns.
  Proper nouns (LangChain, AutoGen, CrewAI, BrowserGym, DSPy, SWE-Agent, AutoCodeRover,
  Agentless) are not counted as "technical concepts" under `audience_model.md`'s term budget
  (they are named entities, glossed by the clause that follows each, not stand-alone concepts
  the reader must retain and reuse) -- but the paragraph is still dense. This is judged
  appropriate for a Related-Work-style gap paragraph specifically (per `section_rules.md`, this
  is exactly where multiple prior systems must be named), not for a random paragraph elsewhere.
- Method paras 1-4: 1 new defined term per paragraph (event stream; ACI/sandbox reinforcement;
  AgentSkills; delegation/AgentHub) -- within budget.

## Sentence length (`A-long-sentence`, INFO, >35 words)
The lint flagged ~25 sentences over 35 words (see `audits/gates/G3_lint.json`). Reviewed each
class:
- **Parallel semicolon-delimited lists** (the Results section's six-benchmark gloss sentence,
  ~124 words, and its matching six-result numbers sentence, ~93 words; the Introduction's
  four-framework gap sentence, ~85 words): kept, with reason. Each list item is short, uses
  parallel grammatical form (`information_design.md` section 3, "parallel structure"), and is
  delimited by semicolons that function as visual paragraph breaks. Splitting these into 5-6
  separate short sentences was tried mentally and judged to read *more* choppily for an
  enumerated comparison than one long, clearly-punctuated sentence, and would re-introduce the
  "3+ consecutive numeric sentences with no interpretive clause" anti-pattern (A6) that the
  Result Interpretation Chain structure elsewhere in the paper is designed to avoid.
- **All other flagged sentences** (36-66 words): single-clause explanatory sentences with one
  qualifying subordinate clause (e.g., "..., though not unconditionally: ..."). Reviewed and kept
  as legitimate research-prose sentence shapes carrying one idea each; none bundle two unrelated
  points with "and also" (the specific failure `information_design.md` section 1 warns against).

## Information density (density classes)
- SUPPLEMENTARY material named in `plan/paper_architecture.md`'s checklist (Docker image-tagging
  mechanics, the full AgentSkills/BrowserGym API lists, GPQA's per-subset breakdown, per-instance
  cost tables) was never drafted into the main text at all -- omitted at the architecture stage,
  not cut after the fact.
- No DISTRACTING content (project history, tool trivia) appears in the draft.
- Every OPTIONAL-tier detail that did make it in (e.g., footnote-level cost figures) was in fact
  excluded rather than relegated to a footnote, since this deliverable is a single Markdown file
  with no footnote/appendix mechanism.

**Result: no `A3` (term-before-concept), `A4` (acronym soup), or `A5` (synonym drift) failure
found beyond the one disclosed, accepted GAIA/GPQA placement trade-off above.** Proceeding to
step 15.
