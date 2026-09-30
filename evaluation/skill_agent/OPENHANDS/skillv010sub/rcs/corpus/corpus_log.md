# Corpus log (CORPUS_AGENT modes: literature, patterns)

## Scope and constraint
Run-specific instruction: no web access. Literature mode is limited to works already cited in
`project/paper.txt`. No index (Crossref/OpenAlex/Semantic Scholar/DBLP/arXiv/etc.) was queried;
"verification" for every registered source uses `method: user_supplied_file` and `read_depth:
abstract`, meaning: the source's existence, authors, year, and venue were read from
`project/paper.txt`'s own reference list (a Level-0 artifact), and what each source "establishes"
is the *citing paper's own characterization* of it, not an independent reading of the source
itself. This is recorded per source in `corpus/source_registry.json`.

## Queries
No search queries were run (no web access). Instead, every in-text citation and reference-list
entry in `project/paper.txt` was read in full (two passes: (1) full-text read of the paper body
and appendices, lines 1-1334; (2) full read of the References section, lines 782-874).

## Selection
Of the ~80 works in `project/paper.txt`'s reference list, 28 were selected for
`corpus/source_registry.json` -- those needed to (a) name and credit the benchmarks reused in
Evaluation Setup/Results, (b) support the Related-Work/gap argument about prior agent frameworks
and specialized SWE agents, or (c) name a specific baseline system discussed individually in the
Results narrative. Works appearing only in the reference list with no distinguishing
characterization in the running text (the large majority) were not registered, since there is
nothing in project/paper.txt to attribute to them beyond their title.

Two named systems were deliberately **not** given a formal (Author, Year) citation:
- **Devin (Cognition.ai)**: no year is given anywhere in `project/paper.txt`, in-text or in the
  reference list.
- **Moatless Tools (Örwall)**: no year is given anywhere in `project/paper.txt` either.

Per the hard rule against inventing facts, no year was fabricated for either. Both are named in
`paper.md`, where relevant, as plain system names (matching how `project/paper.txt`'s own tables
cite them) rather than as formal citations. See `missing_evidence.json` M005 and `state.json`
accepted_risk AR006.

## Stopping reason
Saturation with respect to project/paper.txt's own text: every citation load-bearing for this
paper's Introduction, Related Work, Evaluation Setup, and Results has been registered. No
snowballing (reading a source's own references) was possible without web access.

## Mode: patterns
Scoped down per `state.json` accepted_risk AR005: no external exemplar corpus was available (no
web access), so `corpus/writing_patterns.json` and `corpus/anti_patterns.json` draw only on
`project/paper.txt` as a self-exemplar (two positive patterns worth imitating; two extraction-level
anti-patterns worth flagging rather than silently repairing).

## Suspicious content
None found. No instruction-like text aimed at AI systems or reviewers was present in
`project/paper.txt`, `project/README_1.md`, or `project/README_2.md`.

## RUN_SUMMARY
- Evidence items recorded: 46 (`evidence/research_evidence.json`), plus 6 missing-evidence entries.
- Conflicts detected: 1 (E004 vs. E001; resolved, see `state.json` AR003).
- Sources kept: 28, all `publication_status` disclosed (11 PEER-REVIEWED, 13 PREPRINT, 2
  DOCUMENTATION, 1 BLOG, plus benchmark-defining sources reused for provenance only).
- Sources excluded: the remainder of project/paper.txt's ~80-entry reference list, for lack of any
  distinguishing characterization in the citing text to attribute (see Selection, above).
- Two systems named without a formal citation for lack of a printed year (Devin/Cognition.ai;
  Moatless Tools/Örwall).
- Tables found unusable due to extraction damage: Table 1 (framework comparison, all cell values
  missing) and Table 7 (extended GPQA, alignment unrecoverable). Both recorded as
  `status: unverifiable` and excluded from claims.
- One cross-table numeric conflict found and resolved (see above).
- Nothing in project/ could not be opened; all three files were read in full.
