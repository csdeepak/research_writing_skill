# Literature -> Gap -> Question chain

```
DIMENSION: scope of prior multi-dataset retrieval benchmarks (SRC-011 MultiReQA, SRC-012 KILT)
  ACHIEVES: a first look at cross-domain/cross-dataset retrieval evaluation, beyond a single
    train/test split {C002}
  SHARED LIMIT: each covers only one axis of diversity, not both task-type and domain breadth --
    MultiReQA is one task (answer retrieval) over mostly small, largely Wikipedia corpora;
    KILT spans five task types but retrieves only from Wikipedia and treats retrieval as
    secondary to the end task
  EVIDENCE OF THE LIMIT: the citing paper's own description of both works' coverage
    (project/paper.txt, Section 2, line 127) -- 2 sources
  UNRESOLVED: neither resource tests whether retrieval *architectures* (lexical vs. sparse vs.
    dense vs. late-interaction vs. re-ranking) generalize differently once both domain and task
    type vary together, or how much computational cost that generalization costs
GAP (scoped to the works cited in project/paper.txt): among the two prior multi-dataset retrieval
  resources described in the paper's own related work, neither tests broad, simultaneously
  cross-domain and cross-task, zero-shot generalization of retrieval architectures, nor its
  computational cost.
QUESTION: which retrieval architectures generalize best, zero-shot, across diverse tasks and
  domains, at what computational cost, and how much does in-domain accuracy predict this? {C003}
```

**Chain rules check**
- The "achieves"/"shared limit" parts rest on 2 sources (MultiReQA, KILT), not one -- satisfies
  the ">=2 sources" rule in `citation_rules.md` Section 5.
- "Evidence of the limit" is the citing paper's own stated characterization of each work's scope
  (a direct description of what each benchmark does and does not cover), not merely "it wasn't
  tried" -- satisfies pipeline step 3 (support) at the level available in this run (no web access
  to the original MultiReQA/KILT text; see `state.json` accepted_risk AR003 and
  `source_registry.json` SRC-011/SRC-012 `limitations` fields).
- The GAP statement is explicitly scoped ("among the two prior multi-dataset retrieval resources
  described in the paper's own related work"), not worded as an unscoped "no prior work" or
  "first" claim -- consistent with `citation_rules.md` Section 5 (such wording is licensed only by
  a systematic, logged search, which was not performed here).
- The QUESTION follows from the GAP: answering it (which architectures generalize, at what cost,
  and whether in-domain accuracy predicts it) directly closes the stated gap.
- No change to spine lines 1-3 was needed after building this chain; the gap statement in
  `story/spine.md` line 2 already matched this scoped wording.
