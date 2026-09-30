# Corpus log (Step 7)

## Scope and constraint
Per run-specific constraints, this run has **no web access**. Literature mode is therefore
restricted to works already cited in `project/paper.txt` (and one work described only in
`project/README_1.md`'s citation block). No index (Semantic Scholar, Crossref, OpenAlex, ACL
Anthology, etc.) was queried; no snowballing beyond the citing paper's own reference list was
performed; no exemplar/anti-pattern corpus beyond `project/paper.txt` itself was available.

## "Queries" (in the sense used here: which reference-list entries were screened)
Rather than search-engine queries, the discovery step was: read every one of the 79 reference-list
entries in `project/paper.txt` (lines 715-803) and every citation block in `project/README_1.md`
(lines 404-433), and select those that (a) are actually used as background/method attribution or
gap-establishing evidence in the adapted draft, and (b) have enough information in the citing
document itself (title, authors, year, and a description of what the work does) to register with
`verification.method: user_supplied_file`, `read_depth: abstract`.

- Screened: 79 paper.txt reference entries + 2 README_1.md citation blocks.
- Kept and registered: 15 (`corpus/source_registry.json`, SRC-001..SRC-015).
- Excluded (reasons):
  - The majority of the 79 references (roughly 60) were not used because the adapted draft, aimed
    at an adjacent-ML audience, does not need a citation for every one of the 18 datasets' origin
    papers or every architectural variant mentioned only in passing (avoiding citation-dumping,
    `citation_rules.md` Section 3 / anti-pattern A9/B14).
  - Two reference-list entries ([24] Hofstatter et al. 2021b, cross-architecture knowledge
    distillation; [47] Nogueira, Lin, "AI Epistemic" 2019, "From doc2query to docTTTTTquery") were
    read but deliberately not registered as separate sources: both would collide, in the required
    `(FirstAuthor et al., Year)` citation form, with another already-registered same-first-author,
    same-year source ([23] Hofstatter et al. 2021a / TAS-B, and [48] Nogueira et al. 2019 /
    document expansion, respectively). Rather than introduce a/b-suffixed citation forms not
    requested by the task, the corresponding implementation details are described in the draft as
    plain method detail without a second citation (see `evidence/research_evidence.json` E025 for
    [24]'s content, folded into the BM25+CE method description).
  - Reference [45] MS MARCO's own venue is listed oddly in the source ("choice, 2640:660" --
    apparently a citation-index artifact of the extraction) and could not be resolved to a
    specific journal/venue name from the text alone; registered anyway (SRC-015) with venue left
    unspecified and `publication_status: PREPRINT` as the conservative default, per
    `agents/corpus_agent.md`'s rule to never treat an unclear source as peer-reviewed.
- Snowballing: none performed (requires web access).
- Stopping reason: budget is the project folder itself, not a query budget; stopped once every
  citation actually used in the draft was registered and verified against the citing document's
  own text.

## Suspicious content
None found. Both `project/paper.txt` and `project/README_1.md` were read in full; no hidden/
zero-width characters, no instructions addressed to an AI system or reviewer, and no requests to
rate the work favorably were present in either file.

## Known coverage gap (recorded, not resolved)
Because `writing_patterns.json` and `anti_patterns.json` could only be mined from
`project/paper.txt` itself (the sole full-text document available), rather than from a
broader verified corpus of comparable papers, the craft guidance for drafting relies primarily on
the skill's own built-in `anti_patterns.md`, `information_design.md`, and `section_rules.md`
rather than on externally-mined exemplars. This is recorded in `state.json -> accepted_risks`
(AR003).
