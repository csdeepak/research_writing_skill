# Audits v001 (steps 11-17)

## Step 11 — Reader reconstruction self-test
Re-reading `drafts/v001/paper.md` alone answers: problem (benchmark-tuned ASR is brittle out of distribution), gap (weak supervision not scaled to unsupervised-pretraining size), RQ, approach (680k-hour multitask Transformer, zero-shot eval), key findings (55.2% relative error reduction, 29.1 BLEU SOTA, noise robustness, scaling curves), meaning (breadth of weak supervision substitutes for fine-tuning), and main limits (English-heavy data, weak translation correlation, specific benchmark losses). Matches `story/spine.md`. No mismatches found.

## Step 12 — Evidence/claim audit
All numeric claims in the draft were checked against `evidence/research_evidence.json` values verbatim (55.2%, 2.7%, 29.1 BLEU, r²=0.83/0.24, 80.3%/64.5%, 13.6%, dataset-scaling table values, model-scaling values, long-form ablation values). No mismatches found. Negative results E023 (VoxPopuli) and E024 (Fleurs LID) are both reported in Results §5.3, per `claims/claim_evidence_map.json.negative_result_decisions`. Claim types were checked against verbs used (e.g., "achieves", "reaches" for measured; "correlates", "shows" for observed).

## Step 13 — Logical-flow audit
Introduction ends with contribution + paper map. Each Results subsection opens with the question it answers (matched-vs-robust performance; multilingual/translation scaling; negative results; scaling studies; long-form). Discussion answers the RQ and covers all major limitations. Connectives checked for false relations; none found requiring removal.

## Step 14 — Terminology/cognitive-load audit
Speech-specific terms (WER, BLEU, zero-shot evaluation, VAD, beam search/temperature fallback, r² correlation in this context) are defined at or near first use for a mode-B (adjacent-researcher) reader. Acronyms TED-LIUM, CORAAL, NVIDIA STT/Conformer-CTC were expanded/glossed after the initial `lint_draft.py` pass flagged them (see `audits/v001/lint_output.txt`). Sentence length: several sentences >35 words were reviewed; most carry a single compound idea appropriate to the density (CORE) of the passage and were kept; a handful were split during trimming to meet the length limit.

## Step 15 — Figure/table audit
No figures are included (TASK.md: "No images"). Both Markdown tables (Table 1: model family; Table 2: dataset-size scaling) are referenced in text before they appear, and their takeaways are stated in prose immediately around them. No table-only conclusions.

## Step 16 — Citation audit
Only two author-named prior works appear in the evidence package (Narayanan et al., Likhomanenko et al.), registered in `corpus/source_registry.json` with `verification.method = user_supplied_file`, `read_depth = abstract`. No publication year is available; year is left unresolved (`null`) rather than invented — see `state.json` accepted_risks. Cited in-text as "(Narayanan et al., Likhomanenko et al.)" without a year, a deliberate deviation from the strict "(FirstAuthor et al., Year)" format required by TASK.md, chosen as more defensible than fabricating a year. All other named systems/datasets (wav2vec 2.0, XLS-R, mSLAM, Maestro, SpeechStew, NVIDIA STT, FairSpeech, VP-10K+FT) are used as named systems, not as author-year citations, since no author/year is attached to them in the evidence package.

## Step 17 — Scientific overclaim audit
`lint_draft.py` flagged several "SOTA"/state-of-the-art phrasings and intensifiers (see `audits/v001/lint_output.txt`). These were checked against the evidence: each "state of the art" claim (e.g., 29.1 BLEU on CoVoST2) is a direct, hedged quote/paraphrase of the authors' own claim, including their own caveat about the non-standard text normalizer preventing direct comparison (L002), stated in the same paragraph. No claim was strengthened beyond the evidence; where the lint flagged an unhedged absolute ("every one of them"), the underlying evidence does support the literal claim (all 14 compared models degrade below Whisper under the stated noise condition), so it was left as a factual, evidence-supported statement rather than softened into false uncertainty. Generalization scope was checked for every major claim against its evidence's stated population/dataset/conditions (Section 6.2 of the paper makes scope limits explicit).

## Step 18 (external)
Not performed in this run per TASK.md run-specific constraints ("Step 18 ... is performed externally"). No diagnostics.json/reconstruction.json exist under `.rcs/diagnostics/`.

## Full lint output
See `audits/v001/lint_output.txt` (0 errors, 40 warnings, 63 info at the point captured; several warnings addressed in a subsequent edit pass — acronym definitions, negative-result reporting decisions, story-graph edges — see `state.json`).
