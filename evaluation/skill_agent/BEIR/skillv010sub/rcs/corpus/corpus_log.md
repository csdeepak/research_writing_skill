# Corpus log

## Mode: literature

**Run-specific constraint in force:** no web access. Literature mode is limited to works cited in
`project/paper.txt`. No index was queried (no Crossref/OpenAlex/Semantic Scholar/DBLP/ACL
Anthology access in this runtime). No snowballing was performed.

- **Query facets planned** (per `docs/02_RESEARCH_CORPUS_STRATEGY.md` §2, method + gap terms):
  zero-shot information retrieval benchmark; dense vs. lexical retrieval generalization;
  retrieval test-collection annotation bias. **Not executed** -- no web/index access.
- **Source pool used instead:** the 79-entry reference list of `project/paper.txt` itself. Every
  entry in `corpus/source_registry.json` (35 sources) is drawn from this list, matched to where
  it is actually cited in the paper's prose (Introduction, Related Work, Section 4 method
  descriptions, Section 6 bias discussion, Appendix D dataset descriptions).
- **Selection rule:** registered a source only if it is cited at a location this paper's story
  actually uses (background concept, an evaluated architecture, a compared prior benchmark, a
  dataset introduced in the results/table, or the annotation-bias discussion). Of the 79 entries,
  the ~44 not registered are either purely IR-implementation citations not load-bearing for this
  paper's narrative (e.g. Anserini, faiss, Transformers library, Universal Sentence Encoder), or
  background citations for tasks this paper does not single out (e.g. open-domain QA framing
  papers, individual multilingual-retrieval pointers in Appendix B).
- **Verification performed:** `verification.method = "user_supplied_file"`, `read_depth =
  "abstract"` for every source, as instructed for this run. This means: each source's existence,
  title, authors and year were checked against `project/paper.txt`'s own reference-list entry and
  against its in-text citation context; no independent DOI/index lookup, retraction check, or
  full-text reading of the cited work itself was performed. `publication_status` was inferred from
  the venue string given in the reference-list entry (e.g. "arXiv preprint" -> PREPRINT; a named
  peer-reviewed proceedings/journal -> PEER-REVIEWED; a TREC track overview or PhD thesis ->
  TECHNICAL_REPORT); where the reference-list entry gives no venue string at all, `PREPRINT` was
  used as the conservative default and `peer_review_known: false` was set. This is noted so a
  human author can correct any misclassification before submission.
- **Stopping reason:** all sources needed for this paper's story (per `story/story_graph.json` and
  `story/lit_gap_chain.md`) are registered; no further search was possible under the no-web
  constraint.

## Mode: patterns

**Run-specific constraint:** no web access, so no external exemplar corpus (recent papers at a
target venue) could be assembled. `project/paper.txt` itself was used as the one available
full-text Level-0 exemplar, per `agents/corpus_agent.md` mode `patterns` -- its own rhetorical
moves were described (not copied) into `corpus/writing_patterns.json`, and one structural feature
worth adapting (rather than copying) for this paper's different audience was logged into
`corpus/anti_patterns.json`. This is a narrower base than the skill's usual patterns workflow and
is recorded as an accepted limitation of this run (see `.rcs/state.json` -> `accepted_risks`).

## Suspicious content

None found. Both files in `project/` (`paper.txt`, `README_1.md`) were read in full. Neither
contains hidden text, encoded instructions, or language directed at an AI system, reviewer, or
grader (checked per Hard Rule 6 and failure state `INJECTION_DETECTED`).
