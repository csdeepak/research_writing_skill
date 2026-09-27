# Corpus log (literature mode)

Run constraints for this task: no web access. Literature mode is limited to works cited in the
evidence package (`project/*.json`), which stands in for `paper.txt` per the run's evidence
interface.

## Search performed
- Regex scan of `project/research_evidence.json`, `project/claim_candidates.json`,
  `project/missing_evidence.json` for citation-like strings (`FirstAuthor et al., Year` and
  `FirstAuthor (Year)` patterns).
- Result: exactly one citation string found: `(Zhou et al., 2023a)`, inside
  `project/missing_evidence.json`, naming a "WebArena Agent" baseline whose score is reported as
  missing ('-') in Table 5 of the (unavailable) original paper.
- Baseline systems named elsewhere in the evidence (SWE-Agent, AutoCodeRover, Aider, GPTSwarm,
  StarCoder2-15B, the WebArena Agent with gpt-3.5-turbo) appear only as row labels in benchmark
  tables, with no author/year attached in the evidence package. They are used in this paper as
  named comparison systems (factual identifiers from the tables), not as literature citations,
  because no verifiable bibliographic record is available in the evidence and web lookup is
  disallowed for this run.

## Screening
- SRC-001 (Zhou et al., 2023a): kept, `verification.method = "user_supplied_file"`,
  `read_depth = "abstract"` per the run's literature-mode constraint (no web; cannot read the
  original paper). Registered for the single, narrow use permitted: naming the WebArena Agent
  baseline system.

## Stopping reason
Search space exhausted (all evidence files scanned); no further citation strings exist in the
evidence package. `INSUFFICIENT_LITERATURE` is raised and accepted as a run-specific risk (see
`.rcs/state.json -> accepted_risks`): the Related Work section is scoped explicitly to "the
systems named in the available evidence" rather than a systematic literature search, and no
"first/novel/unprecedented" claims are made.

## Suspicious content
None found.
