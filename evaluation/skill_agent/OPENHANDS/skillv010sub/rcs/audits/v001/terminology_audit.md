# Step 14 -- Terminology / cognitive-load audit

**Term ledger compliance.** Checked every entry in `story/term_ledger.json` against the draft:
"agent", "event stream", "sandbox", "agent-computer interface (ACI)", "CodeAct", "multi-agent
delegation", "generalist vs. specialized agent", and "resolve/success rate" are each defined at
or before their first substantive use, in dependency order (agent -> action/observation -> event
stream -> sandbox -> ACI -> CodeAct -> delegation), matching `plan/paper_architecture.md`'s
term-introduction column. No registered term is later replaced by a synonym (checked "sandbox"
vs. "container" -- "container" is used only after "sandbox" is defined and as a plain synonym
for the Docker container itself, not a competing concept name).

**Acronyms.** ACI is used >=3 times after its definition (qualifies for the acronym form per
`research_story.md` S5). Benchmark names (SWE-Bench, GPQA, GAIA, BIRD, MINT, etc.) are proper
nouns for specific benchmarks, not word-acronyms the reader needs expanded; each one actually
discussed in prose gets a one-clause gloss of what it measures at first use (e.g. GPQA:
"graduate-level science questions designed to resist simple web look-up"), consistent with
`plan/audience_assumptions.json`'s plan to introduce the long tail collectively rather than
expand every letter. `lint_draft.py`'s acronym warnings on `SWE`, `GPQA`, `BIRD`, `GAIA`, `MINT`,
`ML`, `SDK`, `LLMs`, `REST`, `HTML`, `DOM` were reviewed individually: all are either standard
technical vocabulary safe for mode B (REST, HTML, DOM, SDK, LLM) or benchmark proper nouns
handled by contextual gloss rather than letter-expansion (accepted, not fixed). Acronym warnings
inside the References section (GPT, ICML, ICLR, ACL, IJCNLP, SOTA, APIs, QU, BIg, SQLs, AI) are
artifacts of the lint reading cited paper titles as prose; titles are quoted verbatim and must
not be altered.

**Term budget (mode B, audience_model.md S5: <=2 new terms/paragraph).** Spot-checked the three
densest paragraphs (Platform "State and actions"; Platform "An extensible agent-computer
interface"; Evaluation Setup's benchmark list). The benchmark-list paragraph exceeds a literal
per-paragraph count of 2 new names, which is a deliberate, disclosed exception: it is structured
as an enumerated list with a citation per item (a reference table in prose form), not a chain of
concepts the reader must integrate to follow the argument -- consistent with
`information_design.md`'s guidance to move long enumerations to a table-like construct rather
than force them into the argument's main line. All other paragraphs are within budget.

**Sentence length.** `lint_draft.py` flags 19 sentences >35 words (INFO, not WARN/ERROR). Each
was reviewed: all are single-idea sentences carrying a list of parallel benchmark results or a
qualified claim whose qualifying clause cannot be detached without creating an orphan claim
elsewhere (e.g. the SWE-Bench Lite headline sentence, which reports three backbone-model results
in one breath because they are one experiment). Kept as-is with this recorded reason, per
`information_design.md` S3's "keep with a reason" option.

**Result: PASS**, with the two disclosed, reasoned exceptions above (benchmark-list paragraph
density; long qualified sentences).
