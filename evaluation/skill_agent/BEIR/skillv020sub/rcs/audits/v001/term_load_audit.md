# Step 14 -- Terminology / cognitive-load audit

## Term ledger compliance
Checked every entry in `story/term_ledger.json` against the draft: `defined_at` precedes or
equals `first_used_at` for every registered term (BEIR and BM25 are both glossed at their first
use in the Abstract itself; nDCG@10, the architecture-family taxonomy, bi-encoder/cross-encoder,
ColBERT, DPR, and Hole@10 are each defined at first use in the section the ledger specifies). No
registered term is later replaced by a synonym (checked "BM25" is never called "lexical baseline"
alone without also using "BM25"; "nDCG@10" is never shortened to "score" or "accuracy" once
introduced -- it is consistently "nDCG@10").

## Lint acronym findings (`tools/lint_draft.py`, 21 `A3-undefined-acronym` WARNs) -- reviewed
individually:
- **BEIR, IR, BM25**: functionally glossed at first use in the Abstract ("BEIR (Benchmarking-IR)",
  "the untrained lexical baseline BM25"); the lint's parenthetical-expansion pattern does not
  recognize a functional gloss, so this WARN is a known false-positive of the mechanical check
  (documented in `story/term_ledger.json -> acronym_scope_note`). No fix needed.
- **ANCE, SPARTA, TAS(-B), CE, DPR (partially)**: proper names of specific systems, described
  functionally at first use in Sec. 4. `project/paper.txt` itself never spells out what the
  letters in ANCE/SPARTA/TAS-B stand for, so no expansion is asserted (fabricating one would
  violate the no-invention rule). DPR and ColBERT *are* expanded, because their expansions are
  directly evidenced by the cited works' own titles (`corpus/source_registry.json` SRC-004,
  SRC-007). Accepted.
- **BERT, GPU, CPU, MSE**: general ML/CS vocabulary the audience profile (`plan/audience_profile.json
  -> assumed_known`) already treats as known to mode B/C readers; consistent with
  `audience_model.md`'s allowance for "well-known field acronyms" to be registered without a full
  first-principles definition. Accepted.
- **MS, MARCO, KILT, TREC, COVID**: parts of proper dataset names (MS MARCO, KILT, TREC-COVID),
  tokenized separately by the lint's regex; not true acronyms requiring expansion. Accepted.
- **ACM, SIGIR, NAACL, HLT, EMNLP**: venue abbreviations inside the References list only (lines
  137-165), which is bibliographic, not prose the target audience needs to parse conceptually;
  outside the main-text word count and outside the term ledger's scope. Accepted.

## Term budget (mode B: <=2 new technical terms/paragraph)
Spot-checked the two most term-dense paragraphs:
- Sec. 4 P1 (architecture-family paragraph) introduces 5 named families in one paragraph, over
  the nominal budget. This is treated as SUPPORTING/CORE reference material for a paragraph whose
  entire job is to define the taxonomy the rest of the paper uses (a glossary-like paragraph),
  which `audience_model.md` Section 5 treats as a diagnostic threshold, not a hard quota; splitting
  it into 5 one-family paragraphs would fragment a single coherent list the reader needs to hold
  together for comparison. Kept as one paragraph; flagged here rather than silently ignored.
- Sec. 5.3 (TAS-B/length-preference paragraph) introduces "Margin-MSE loss", "cosine similarity",
  "dot product" in close succession; each is glossed in the same sentence it appears in framing
  the loss/similarity function is a well-known ML concept per the audience profile (contrastive-
  style losses, embeddings), so only "Margin-MSE" itself is genuinely new, and it is not reused
  later, so it is not registered in the term ledger as a load-bearing term.

## Sentence length
46 sentences exceed 35 words (`A-long-sentence`, INFO). Reviewed each: the great majority use a
colon or em-dash to present a claim followed by its own supporting enumeration or magnitude in the
same breath (e.g. "...trails ANCE by 17.3 points nDCG@10, and on Touche-2020 by 7.8 points; these
are the two datasets where..."), which keeps the claim and its evidence adjacent rather than
splitting them across sentences and forcing the reader to hold the claim in memory. Kept as-is
with this reason recorded, per `information_design.md`'s "keep them with a reason" option; none
exceed 70 words.

## Information density
No DISTRACTING content identified (no project history, tool trivia, or abandoned ideas appear).
No SUPPLEMENTARY material was deferred to an appendix/supplement, because none of the reproducibility
detail needed relocating to stay within the length gate (final main text: 3,670 words against a
4,500-word limit; see `.rcs/audits/gates/G3_lint.json`).
