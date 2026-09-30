# Citation Rules

A citation being **present** is not the same as it being **correct**. A citation is correct
only when the source exists, its metadata is right, it actually supports the sentence at that
strength, and it is the appropriate source to cite.

Why this is strict: LLMs fabricate references at high rates when working from memory (S06: 18%
fabricated with GPT-4; S25: 78–90% hallucinated citations for GPT-4o in their setting). Even
with web search, only about half of generated BibTeX entries were fully correct in S26. Human
authors also misquote sources at meaningful rates (S22).

---

## 1. Sources of citations (the only allowed ones)

1. `corpus/source_registry.json` entries with `verification` filled in.
2. References present in the user's own materials (Level 0). These still need verification
   before use.
3. Sources the user supplies during the session. These are verified and then registered.

**Never** cite from model memory. If you "know" a relevant paper, search for it, verify it,
register it, *then* cite it. If you can't verify it, write `[CITATION NEEDED: <what needs
support>]` and add it to `open_issues.md`.

---

## 2. The citation pipeline (every citation, step 16)

| Step | Check | Pass condition | On failure |
|------|-------|----------------|------------|
| 1 Exists | DOI/arXiv/ISBN/URL resolves to the stated work | Title and first author match | Remove; `UNVERIFIED_CITATION`; log as possible fabrication |
| 2 Metadata | Authors, year, venue, volume/pages | Match the index record (Crossref/OpenAlex/publisher) | Correct from the index. Never guess fields. |
| 3 Supports | A `support_quote` (≤40 words) or a precise location from the source backs *this* sentence | A reader of the quote would agree the sentence is supported | Rewrite the sentence to what the source says, or drop the citation |
| 4 Strength | The sentence's claim strength ≤ the source's own claim strength | E.g. the source "suggests" → the sentence doesn't say "showed" | Downgrade the sentence |
| 5 Status | publication_status disclosed where it matters | Preprints cited as preprints when load-bearing | Add "(preprint)" or find the published version |
| 6 Primary | Cite the originating source for findings, not a secondary summary, when available | A primary source is used, or the secondary one is cited as a review | Replace, or add the primary |
| 7 Purpose | The sentence states what the source contributes | Not decorative | Remove, or state its role |
| 8 Integrity | Not retracted (checked when tools allow) | — | Remove, or cite as retracted if discussing it |

Record the results in `audits/vNNN/citation_audit.json` (a row per citation instance).

## 3. Citation-use patterns

| Pattern | OK? | Note |
|---------|-----|------|
| "[S] reports that X under condition C." | ✅ | Attributed, scoped |
| "X [S1, S2, S3]." (all three support X) | ✅ | If all three were checked |
| "X is well known [S1–S9]." | ⚠️ | Citation dumping. Keep the 1–3 best, state their roles. |
| "Prior methods fail at Y [S]." | ⚠️ | Only if S shows failure at Y, not just that it didn't test Y |
| "No prior work addresses Y." | ❌ | Rewrite as search-scoped (§5) |
| "Our approach is inspired by [S]." | ✅ | If true and the user confirms it |
| Citing a paper for a claim found only in its related-work section | ❌ | Cite the original |

## 4. Literature organization: the dimension matrix

Build `corpus/literature_map.json` as a matrix, not a list:

| Source | Problem framing | Method family | Key assumption | Data/eval | Strength | Weakness/limit | Relation to us |
|--------|-----------------|---------------|----------------|-----------|----------|----------------|----------------|

Then group by **dimensions** (the columns), not by rows. Candidate dimensions: problem
dimensions, method families, assumptions, strengths, weaknesses, datasets, evaluation
strategies, unresolved contradictions. Choose the 2–4 that best explain *why the gap exists*.

## 5. Literature → Gap → Question chain

The Related Work (and the introduction's gap paragraph) must make the research question feel
**necessary**. Build this chain explicitly in `story/lit_gap_chain.md`:

```
DIMENSION: method family K (SRC-003, SRC-011, SRC-019)
  ACHIEVES: strong accuracy on in-distribution benchmarks {C002}
  SHARED ASSUMPTION: stationarity of input distribution (SRC-003 §3; SRC-011 eq.2)
  EVIDENCE OF FAILURE: SRC-019 reports degradation under shift (Table 4) — 1 source
  UNRESOLVED: whether failure is due to the assumption or to model capacity (no retrieved source isolates it)
GAP (scoped): "Among the 23 works retrieved (Semantic Scholar + ACL Anthology, 2019–2026), none isolates …"
QUESTION: RQ1 = "Does relaxing the stationarity assumption, at fixed capacity, reduce error under shift?"
```

**Chain rules**
- A GAP needs ≥2 sources for the "achieves" and "shared assumption" parts, or it's worded as
  resting on one study.
- "Evidence of failure" needs a source that *actually* shows the failure (pipeline step 3).
- The GAP statement is **scoped to the search** (`docs/02_RESEARCH_CORPUS_STRATEGY.md` §2). "No
  prior work", "first", and "for the first time" are allowed only when the search was
  systematic and the claim map records it as a `literature` + `derived` claim with the search
  log as evidence.
- The QUESTION must follow from the gap: answering it would close or narrow the gap.

## 6. Self-citation and the user's own prior work
Treated like any other source: verified, and its role stated. Prior results of the same
project that are reused must be cited, not re-presented as new.

## 7. Output hygiene
- `references.bib` (or the style the venue requires) is generated from the registry. Every
  field comes from the index record.
- The citation style is venue-injected. The skill enforces correctness, not formatting.

## 8. Titles as cited (v0.3)

Record the project's own citation text in `as_cited`. If the registry `title` differs, the
difference must come from a `doi_lookup`, `index_lookup`, or `publisher_page` verification;
otherwise the result is `TITLE_REPAIRED_FROM_MEMORY`. A garbled title you cannot verify stays as
cited, with `title_status: unverifiable`. Never repair it from memory, even when you are
confident.
