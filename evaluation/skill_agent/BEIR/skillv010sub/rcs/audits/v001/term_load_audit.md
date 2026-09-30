# Step 14 — Terminology / cognitive-load audit

## Term ledger compliance
Checked every entry in `story/term_ledger.json` against the final draft: `defined_at` precedes
`first_used_at` for all 10 tracked terms (zero-shot/OOD, BM25, lexical gap, the 5 architecture
families, nDCG@10, pooling, bi-encoder/cross-encoder, hard/in-batch negatives, document expansion,
Hole@k). No registered term is later replaced by a synonym (e.g. "zero-shot" is never switched to
"out-of-distribution" or "domain-shift" once introduced; "cross-attention" is used consistently for
the re-ranking/late-interaction mechanism rather than alternating with "full attention" or
"joint encoding").

`lint_draft.py` acronym findings, reviewed:
- `GPU` flagged as never defined: accepted as known to the mode-B audience (general ML
  infrastructure vocabulary; not IR-specific), consistent with audience_model.md §5's allowance
  for "well-known field acronyms... still go in the ledger, marked known_to". Adding
  `plan/audience_assumptions.json -> assumed_by_target_audience_and_not_redefined` coverage note
  rather than a definition in-text.
- `RT` (in "Signal-1M(RT)") flagged as rare: this is part of a proper dataset name, not a concept
  acronym; left as in the source's own naming.
- All remaining acronym flags (`ACM`, `SIGIR`, `CLEF`, `ECIR`, `ACL`, `EMNLP`, `WWW`, `NAACL`,
  `BMC`, `COLT`, `BIOASQ`, `NDCG`, `SPECTER`, `CLIMATE`, `FEVER`) fire inside the **References**
  section on venue names and title words, not in the paper's prose; the lint's acronym scanner does
  not exclude the bibliography. Reviewed and dismissed as not applicable -- reference-list entries
  are bibliographic records, not prose subject to first-use-definition rules.

## New-concept rate (mode B: <=2 new terms/paragraph target)
Checked the two densest paragraphs:
- Background §2 para 2 (the five-family taxonomy) introduces more than 2 new terms in one
  paragraph by design -- it is the single place all five families are defined together, structured
  as one bolded term per sentence so each concept gets its own sentence rather than being crowded
  into others. Treated as a deliberate, clearly-signposted exception (a glossary-style paragraph),
  not diffuse jargon buildup.
- All other paragraphs stay at or under the 2-new-term budget.

## Sentence length
`lint_draft.py` flagged 20 sentences over 35 words (all `INFO`, non-blocking). Reviewed all 20; the
three most extreme (>=50 words) were split during drafting (see draft history: the Section 5
closing sentence and the Discussion opening sentence were each split in two). The remaining
36-49-word sentences were kept as single sentences with a reason: each joins two clauses that share
one subject and one comparison (e.g. "TAS-B is the best-generalizing dense system... It still loses
to the weaker-on-average ANCE on two datasets: ..., where its top-ranked documents are much
shorter..."), and splitting them further would break the point-then-evidence unit the paragraph
model asks for. Judged acceptable rather than mechanically split.

## Information density
No DISTRACTING material is present (no project history, no tool trivia). SUPPLEMENTARY material
not needed for understanding (full per-dataset breakdowns for 3 systems, the latency/index-size
table, license/formula appendices) was excluded per `venue_profile.yaml`'s `supplement_allowed:
false`, rather than moved to an appendix, consistent with information_design.md §2's
relocation principle applied to a single-file deliverable with no supplement.
