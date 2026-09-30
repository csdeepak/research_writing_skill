# Step 16 -- Citation audit

Scope: all 32 sources in `corpus/source_registry.json`, every one of which is cited at least once
in `drafts/v001/paper.md` (verified: every `(Author, Year)` key extracted from the draft resolves
to exactly one registry entry, and every registry entry's key is used at least once -- see the
extraction script output recorded in this session; two initially-registered, ultimately-unused
sources, Hong et al. 2023 and Shinn et al. 2024, were removed from the registry rather than left
dangling).

Pipeline (`citation_rules.md` S2), applied per source:

1. **Exists.** Every source's title/authors/year/venue was read directly from `project/paper.txt`'s
   own reference list (a Level-0 artifact) -- not from memory, not from a web search (none was
   available). No DOI/index re-resolution was possible without web access; this is disclosed as a
   scope limit, not silently skipped (`verification.method: user_supplied_file` on every entry).
2. **Metadata.** Authors, year, and venue were copied verbatim from `project/paper.txt`'s
   bibliography; two disambiguating year-suffixes (`2024a`/`2024b` for the two Wang et al. and two
   Zhang et al. sources actually cited; `2023a` for Zhou et al.) are reproduced exactly as
   `project/paper.txt` itself prints them.
3. **Supports.** Every `establishes[].support_quote` in the registry is a quotation or close
   paraphrase of what `project/paper.txt` itself says about that source (since read_depth=abstract,
   this is the only text available to judge "supports" against) -- e.g. the AutoGen quote
   ("though with stateless command execution") and the SWE-Agent characterization are both
   reproduced from `project/paper.txt`'s own running text, not invented.
4. **Strength.** Sentence claim strength checked against each source's own role: benchmark
   citations support only "defines/evaluates on" statements (not stronger); the two framework
   quotes (AutoGen, LangChain) are presented as the source's own or the citing paper's own
   characterization, in quotation marks, not upgraded to this paper's independent finding.
5. **Status.** `publication_status` is disclosed for all 32 (13 PEER-REVIEWED, 15 PREPRINT, 2
   DOCUMENTATION, 1 BLOG, plus one further PEER-REVIEWED added after dedup); none is presented as
   more authoritative than its status warrants; none is cited as if peer-reviewed when it is a
   preprint or a blog post.
6. **Primary.** Every citation is to the originating source of the fact it supports (the benchmark
   paper for its own benchmark, the system's own release note/paper for its own baseline number),
   never a secondary summary.
7. **Purpose.** Every citation instance states what the source contributes at that point (names a
   benchmark it defines, a system it introduces, or a specific characterization it makes) --
   no bare "[S1-S9]" citation dumps; the closest case (the Evaluation Setup benchmark list) still
   attaches one citation to one specific, distinct benchmark name each.
8. **Integrity.** Retraction status could not be checked (no web access); `retraction_checked:
   false` is recorded on every entry rather than assumed clean.

**Two sources deliberately left uncited-by-formula.** "Devin (Cognition.ai)" and "Moatless Tools
(Örwall)" are named in the draft (Introduction footnote context is not used in this paper; Moatless
Tools appears only as a Table 1 row label) without a `(Author, Year)` parenthetical, because
`project/paper.txt` itself gives no year for either -- see `missing_evidence.json` M005 and
`state.json` AR006. No year was invented.

**Result: PASS**, with the two disclosed scope limits above (no DOI re-resolution, no retraction
check -- both consequences of the no-web-access run constraint, not of skipped work) and the two
intentionally uncited proper names.
