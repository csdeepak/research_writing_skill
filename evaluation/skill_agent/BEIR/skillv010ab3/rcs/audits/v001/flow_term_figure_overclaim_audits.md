# Steps 13-15 and 17 audits (draft v001)

## Step 13 logical flow
- The introduction states the RQs in its fourth block, gives a contribution list and a paper map. The zero-shot question is foreshadowed in block 2. Question-ledger debt is 0; the label question is deferred to Section 5.4 with a pointer (RQ3).
- Each Results subsection opens with its RQ (5.1-5.4). The Discussion opens with per-RQ answers.
- Connectives checked: "whereas", "so", "therefore" appear only where a contrast or inference holds. No "moreover/furthermore" chains.
- Transitions: 5.1 to 5.2 (which architectures), 5.2 to 5.3 (cost), 5.3 to 5.4 (label reliability), each carried by a linking sentence.
- Fixes applied: long abstract sentences split; interpretive clauses added after numeric runs (lint A6).

## Step 14 terms and load
- Ledger: zero-shot (abstract, in place), in-domain (Sec 1), query/document/corpus (Sec 1), BM25 (abstract, Sec 1), five families (Sec 2), nDCG@10 (Sec 3), qrels (Sec 3), pooling (Sec 4), Hole@10 (Sec 4), MS MARCO (abstract).
- Acronyms still flagged by lint are proper names of datasets, systems and venues; each system is introduced in Sec 2 or Table 2 before the results. ANCE appears once in the abstract with a gloss (dense system).
- One term per concept: "system" for a retrieval model or configuration, "family" for architecture group, "in-domain" vs "zero-shot" never swapped.
- Sentences over 35 words were reviewed; those that remain list parameters or hardware and are kept with that reason.
- Section 2 carries several system names per paragraph; each is glossed in one clause and needed later. Accepted with reason.

## Step 15 tables
Six planned tables (cards in plan/figure_cards); the paper contains five (the experiment plan was merged into prose). Each is introduced in prose before it appears, has its takeaway stated in prose (Table 3: reversal and win counts; Table 4: 15.3-point change on TREC-COVID; Table 5: gain tracks hole size), and carries a caption saying what is compared. No bold or underline marks (lost in extraction, disclosed). No images. No uncertainty is shown because none exists (disclosed, L005). No source-paper figure values are used (M006).

## Step 17 overclaim
- Watch-list: no "novel", "first", "state-of-the-art", "prove", "demonstrate". "Significant" removed (the source used it without a test). "Clearly" removed.
- "Generalize" is used for the tested comparison with scoping ("in this comparison", "for these systems"); the RQ1 answer states it is not a general claim.
- Causal wording: "accounts for" replaced by "leaves open"; length, cross-attention and loss explanations are typed interpretation or speculation and hedged.
- Abstract contains only claims of confidence at least moderate (C001, C002, C004-C007, C016-C019) plus the variance limitation; C013, C014, C015, C020 (low) appear only in the body, hedged.
- Scope statements ("ten systems", "these checkpoints", "TREC-COVID only", "1M-document DBPedia sample") sit next to every claim that could be over-read.
- Flag resolved by downgrade: "best generalizers were the slowest or largest" became "the two best-averaging systems were the slowest", with the docT5query exception.
