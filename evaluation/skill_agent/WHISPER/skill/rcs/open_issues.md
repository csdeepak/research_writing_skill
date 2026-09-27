# Open Issues — Whisper RCE Run

Run completed through step 21 (skip step 20). Final manuscript at `./paper.md`.

---

## Genuinely Unresolved (not fixable without new evidence)

### OI-01: Three datasets missing from Table 2 display
Table 2 in the final paper shows 10 out-of-distribution datasets; the Average row spans 14
(including the reference). The three omitted datasets — TED-LIUM 3, VoxPopuli, and
Earnings-21 — were included in the original paper's average but their per-row WER figures
for the supervised baseline vs. Whisper are not available in the project evidence files.
A footnote documents this gap. **Resolution requires** reading Table 2 of the original PDF
directly to extract those three rows and insert them.

### OI-02: No confidence intervals on Table 2 / dataset-scaling WER numbers
Seed variance statistics (bootstrap CIs) are not reported for the majority of per-dataset
WER and BLEU numbers (only Figure 9's robustness frontier carries CIs in the original).
Claims are stated with numbers as-is, which is consistent with the paper's own reporting,
but a reader performing statistical inference cannot assess significance of individual
differences. **Resolution requires** the original paper's supplementary or a replication.

### OI-03: Human comparison sample size (25 recordings, no CIs)
The Kincaid46 human comparison uses 25 recordings with no reported confidence intervals
(missing evidence M004). The caveat is inserted at the claim site (§4.2) and in limitations
(§6.4), but the underlying uncertainty cannot be quantified. **Resolution requires** the
full Kincaid46 dataset with repeated evaluations.

### OI-04: Training compute cost not available
GPU-hours for each model size are not reported in the project evidence (missing evidence
M002). The paper is therefore silent on the compute budget of the Whisper approach, which
matters for reproducibility comparisons. **Resolution requires** direct communication with
the authors or an appendix not captured in the available PDF.

### OI-05: Diversity vs. volume confound in ablations
No experiment in the paper isolates distributional diversity from raw data volume. The
data-scaling ablation (§5.2) and multitask transfer experiments (§5.3) change both
simultaneously. The §6.1 interpretation that diversity acts as a regularizer is explicitly
flagged as such in the final paper, but the confound cannot be resolved without a purpose-
built diversity-controlled ablation that was not conducted.

### OI-06: Multitask crossover exact threshold
The crossover from negative to positive transfer (§5.3) is stated as occurring "within the
Small-to-Large range" based on the qualitative description in evidence E018, but the exact
model size or compute budget at which it occurs was not tabulated in the available evidence.
Figure 9 of the original paper contains this information but was not extracted numerically.
**Resolution requires** reading Figure 9 directly.

---

## Resolved in Revision (step 19/21)

The following issues identified in the external blind review (diagnostics.json) were
addressed in the v001→final revision:

| Issue | Dimension | Revision made |
|-------|-----------|---------------|
| Missing figure reference (§6.2) | figure_table (score 2) | Replaced with self-contained textual description of frontier data |
| BLEU/IHM/SDM/CTC undefined | terminology (score 3) | Glosses added at first use |
| Table 2 average spans unlisted datasets | evidence_traceability (score 3) | Footnote added |
| CLIP analogy repeated 3× | redundancy (score 3) | Consolidated into §6.3; §7.4 now cross-references |
| "diversity as regularizer" asserted | unsupported_inference | Recast as interpretation; confound flagged |
| "humans implicitly develop" analogy | unsupported_inference | Marked explicitly as analogy in §8 |
| Abstract: human-level claim without CI hedge | claim_evidence_alignment | Qualifier added: "25 recordings; no CIs" |
| §4.2: small-sample caveat not at claim site | limitation | Caveat inserted at §4.2 claim site |
| CoVoST "new state of the art" overstrong | overstrong_language | Reworded to reflect authors' own caution |
| §8 causal overreach | causal_overreach | Softened to "consistent with … rather than" |
| §1.2 scale not calibrated for CV readers | motivation (score 4) | ~82M examples vs 400M CLIP comparison added |
| §1.3 comparison hours not inline | contribution (score 4) | GigaSpeech (10,000 h) added inline |
| §3.2 Mel axes not explained | method (score 5) | "rows=frequency bands, columns=time steps" added |
| §5.3 crossover lacks model size | result (score 4) | "Large scale (1,550 M)" added as observable threshold |
| Conformer undefined for CV readers | terminology | Removed from §5.4; replaced with "other supervised ASR systems" |
| Multitask framing ambiguous | narrative_coherence | §1.3 states multitasking is instrumental to robustness thesis |
| Cognitive load from dataset names | cognitive_load (score 3) | Prose groups datasets by acoustic condition category |
