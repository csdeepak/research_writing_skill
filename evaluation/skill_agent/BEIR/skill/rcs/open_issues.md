# Open Issues — BEIR Paper (run beir_rce_001, after step 19)

Issues are ordered by severity. **HIGH** items should be resolved before submission; **MEDIUM** items weaken specific claims; **LOW** items are minor clarifications.

---

## HIGH

### 1. Jaccard overlap heatmap / statistics missing (§3.3)
**Marker in paper:** `[MISSING: pairwise Jaccard overlap summary statistics (e.g., median cross-domain similarity value) are not reported in the source materials; the heatmap figure is not reproduced here.]`

**What is needed:** The paper asserts that cross-domain vocabulary overlap is "predominantly low," which is the evidence supporting the claim that BEIR requires genuine cross-domain generalisation rather than vocabulary transfer. This claim is currently supported only by a verbal description of a figure that cannot be reproduced here. Authors should either (a) provide the heatmap figure, or (b) report at minimum the median pairwise Jaccard similarity across different-domain dataset pairs and note any exceptions.

**Evidence ID:** none with specific Jaccard values — authors must supply from original analysis.

---

## MEDIUM

### 2. Cross-attention generalisation explanation is correlational (§7)
**Location:** §7 ¶2 ("Why do cross-attention models generalise better?")

**What is needed:** The explanation that inference-time token-level comparison explains the generalisation advantage of BM25+CE and ColBERT is explicitly flagged as correlational. Confounds include model size (MiniLM-L6 vs. bi-encoders of similar or larger size), distillation training, and the quality of BM25's 100-candidate pool. An ablation isolating cross-attention from these factors — e.g., a fixed-checkpoint version of a bi-encoder re-ranked with a cross-encoder vs. with dot product — would allow a causal claim.

**Impact:** The current explanation is the most prominent causal narrative in the Discussion. Its correlational status is now disclosed but weakens the paper's explanatory contribution.

---

### 3. TAS-B training-objective advantage is correlational (§5.1)
**Location:** §5.1 ¶4 ("Training setup matters within the dense family")

**What is needed:** The claim that TAS-B's combined training objective (topic-aware sampling + Margin-MSE + in-batch negatives + distillation) explains its superior zero-shot performance relative to ANCE and DPR is correlational. TAS-B also differs in backbone (DistilBERT vs. RoBERTa for ANCE) and number of training steps. A controlled experiment varying only the training objective while holding backbone and steps constant is needed to establish causality.

**Impact:** Currently disclosed as correlational; weakens the actionable guidance about training regime choice.

---

### 4. Annotation bias analysis covers only one dataset (§6, §8)
**Location:** §6, §8 ("Annotation selection bias" limitation)

**What is needed:** The Hole@10 analysis and manual re-annotation are restricted to TREC-COVID. The paper reports Hole@10 rates implying similar bias likely exists in other BEIR datasets (e.g., datasets built with BM25-only pooling), but does not quantify it. A systematic Hole@10 analysis across all 18 datasets would allow a benchmark-wide bias assessment.

**Impact:** The conclusion now correctly scopes the bias finding to TREC-COVID. The broader claim that annotation bias "systematically penalises" non-lexical models rests on a single-dataset demonstration. The word "systematically" in the abstract and §6 may overstate generality given this scope.

---

### 5. DPR in-domain marker on NQ is potentially misleading (Table 2)
**Location:** Table 2, NQ row, DPR column (0.474‡)

**What is needed:** The ‡ marker in Table 2 indicates in-domain performance on MS MARCO. However, DPR was trained on NQ (among other QA datasets), not MS MARCO. The ‡ marker on DPR's NQ score (0.474) therefore signals a different kind of in-domain condition — DPR on one of its own training datasets — rather than in-domain MS MARCO performance. This creates potential confusion about whether DPR's NQ score should be treated as a zero-shot or in-domain result.

**Resolution options:** (a) Apply a distinct marker (e.g., §) to DPR's NQ score to indicate it is DPR-in-domain but not MS-MARCO-in-domain; (b) add a table footnote explaining the distinction; (c) exclude DPR's NQ score from zero-shot averages with a note.

---

## LOW

### 6. ColBERT GPU latency not reported (Table 3)
**Location:** Table 3, ColBERT row, GPU Latency column (shows "—")

**What is needed:** It is unclear whether GPU latency for ColBERT was not measured, or whether it was unavailable at time of evaluation. A note clarifying this distinction (e.g., "GPU evaluation not performed at this scale" vs. "measurement unavailable") would help readers assess whether the latency gap is real or an experimental gap.

---

### 7. GenQ claim tag C026 not defined in claim_evidence_map.json
**Location:** `.rcs/claim_evidence_map.json` — claim ID C026 referenced in draft but not registered.

**What is needed:** During the draft phase, a claim about GenQ ("outperforms TAS-B on specialised domains, underperforms on broad domains") was tagged C026, but this claim was not registered in the claim–evidence map. Authors should verify the evidence for this claim (Table 2 row comparisons) and register it, or confirm it is covered by C007/C008.

---

## Resolved in this revision (step 19)

The following issues raised by the external blind review (step 18) were addressed:

| Diagnostic finding | Action taken |
|---|---|
| Abstract overgeneralises bias correction | Scoped to "case study on TREC-COVID" |
| Conclusion restates bias result without dataset caveat | Added explicit single-dataset qualifier |
| Abstract understates dense model range | Replaced "frequently fall substantially below" with TAS-B/DPR range |
| No explicit research question in §1 | Added RQ sentence before BEIR introduction |
| MultiReQA/KILT gap not quantitative | Added dataset counts and domain coverage specifics |
| SPARTA 30k-dimension intuition missing | Added vocabulary-size explanation |
| nDCG@10 not intuitively defined | Added gain/discount/normalization intuition |
| Corpus scale not contextualised | Added comparison to NLP benchmark scale norms |
| TAS-B attribution stated causally | Changed to explicitly correlational framing |
| §5.2 lacks connection to generalisation thesis | Added transition sentence |
| §6 lacks connection to §5 results | Added transition sentence |
| Cross-attention causal attribution | Added confound list and correlational disclaimer |
| Conclusion re-derives rather than synthesises | Conclusion now leads with implication, not numbers |
| Table 1 caption mismatch (‡/score columns) | Already corrected in paper.md prior to this step |
| `{C009, E018}` placeholder in §5.2 | Already removed in paper.md prior to this step |
| ColBERT BioASQ 900GB figure not tabulated | Added to Table 3 ColBERT row as annotation |
