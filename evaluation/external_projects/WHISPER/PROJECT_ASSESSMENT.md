# Project Assessment — WHISPER

Snapshot basis: `evaluation/external_projects/WHISPER/snapshot/` (`paper.txt`, `README__openai__whisper.md`). Pins from `evaluation/manifests/source_snapshots.json`. Line references ("L##") refer to `paper.txt` line numbers (pdftotext output; roughly one paragraph/block per line, with figures/tables badly fragmented — see Risks).

## 1. Project description
Whisper is a speech-processing system (encoder–decoder Transformer, §2.2, L47) trained to predict raw transcripts of audio scraped from the internet, scaled to 680,000 hours of multilingual, multitask (weakly) supervised data (Abstract, L8; §1, L25–26). The paper studies whether simple scale of weakly supervised pre-training, without fine-tuning, yields a single model that generalizes zero-shot across speech recognition, X→English translation, language identification, and voice activity detection (§1–§2.3). It is a **method + large-scale empirical study paper**: one off-the-shelf architecture (L47, "off-the-shelf architecture to avoid confounding our findings with model improvements"), trained at several sizes, evaluated zero-shot on ~12+ existing academic benchmarks plus long-form and human-comparison studies (§3), with ablations on model size, dataset size, multitask/multilingual transfer, text normalization, and decoding heuristics (§4).

## 2. Official repository
- Repo: `openai/whisper` — https://github.com/openai/whisper
- Pinned commit: `86098128c0b4f24f0e2aa2994de830614b474227`
- Snapshot README URL: https://github.com/openai/whisper/blob/86098128c0b4f24f0e2aa2994de830614b474227/README.md (sha256 `38c180c2…d5a0f4b65f288`)
- README (161 lines): install instructions, available model table (tiny…large **and `turbo`**), CLI/Python usage examples, license (MIT).

## 3. Paper / report
- arXiv: **2212.04356v1** (6 Dec 2022), eess.AS. PDF sha256 `6337bde0…83594566`; `paper.txt` 17,054 words.
- Venue (confirmed via web search, outside snapshot): published as a poster at the **40th International Conference on Machine Learning (ICML 2023)** — https://icml.cc/virtual/2023/poster/24519 — i.e., peer-reviewed. The arXiv snapshot (v1, Dec 2022) predates and is not necessarily identical to the camera-ready ICML version; the Gold Account uses only the arXiv v1 snapshot text.
- Snapshot itself carries no "under review"/preprint banner text in the extracted lines; venue status could not be confirmed from the snapshot alone.

## 4. Datasets
- **Training data**: constructed by the authors from audio+transcript pairs scraped from the internet (§2.1, L34), 680,000 hours total, of which 117,000 hours cover 96 non-English languages and 125,000 hours are X→en translation pairs (§1, L26). This dataset is **not released**; the paper states only "We are releasing models and inference code" (Abstract, L8; also §1, L27, links only to the GitHub repo). Training-data-per-language statistics appear in Figure 11 (Appendix E, L1957–2107) but the extracted text is scrambled/interleaved (numbers and language names run together) — not usable as a reliable source of specific per-language hour counts.
- **Evaluation datasets**: entirely pre-existing, publicly documented third-party datasets, listed by name and preprocessing recipe in Appendix A (L1179–1222): LibriSpeech, TED-LIUM 3, Common Voice 5.1/9, Artie bias corpus, CallHome/Switchboard (LDC), WSJ (LDC), CORAAL, CHiME-6, AMI-IHM/SDM1 (short-form, §A.1); long-form sets TED-LIUM3 (concatenated), Meanwhile, Rev16, Kincaid46, Earnings-21/22, CORAAL (§A.2); multilingual sets MLS, Fleurs, VoxPopuli, Common Voice 9, CoVoST 2 (§A.3). Availability: paper states these are standard public academic/LDC datasets; some (WSJ, CallHome, Switchboard) require LDC licenses, which the paper does not restate as a caveat.
- **Comparison models**: a fixed list of 14 public HuggingFace checkpoints, itemized in Appendix B (L1223–1228), all noted as "entirely or partly trained on LibriSpeech."

## 5. Benchmark / evaluation material
- §3.2 defines the WER metric and the authors' custom text normalizer (used before WER calc); full normalizer rules given in Appendix C (L1234–1248), and the Python code is stated to be released as part of the code (L1248).
- §3.1 states the zero-shot evaluation protocol (no use of any dataset's own train split).
- §4.5 (L967–1000) and Table 7 (L976–998) describe the long-form decoding heuristics (beam search, temperature fallback, VAD via no-speech + avg-logprob thresholds, previous-text conditioning, initial timestamp constraint) as an ablation-style evaluation.
- Appendix D (L1254–1951) contains large raw per-dataset, per-model performance tables (English transcription greedy/beam, multilingual transcription on 4 benchmarks, translation on 2 benchmarks, long-form transcription) — see Risks re: extraction quality.
- Appendix F (L2127–2155) gives full training hyperparameters (updates, batch size, optimizer, LR schedule, etc.) and Large-V2-specific hyperparameter changes.

## 6. Available experimental evidence (in snapshot)
- Zero-shot English ASR robustness study vs. supervised LibriSpeech models and vs. a human (Alec), §3.3, Figure 2, Table 2.
- Multilingual ASR on MLS and VoxPopuli (§3.4, Table 3) and on Fleurs with a language-ID and training-data-size correlation analysis (Figure 3, r²=0.83).
- X→en translation on CoVoST2 (§3.5, Table 4) and Fleurs-as-translation (Figure 4, r²=0.24).
- Language identification on Fleurs (§3.6, Table 5).
- Additive-noise robustness vs. 14 LibriSpeech-trained models (§3.7, Figure 5).
- Long-form transcription vs. 4 commercial ASR services + NVIDIA STT on 7 datasets (§3.8, Figure 6).
- Human-transcriber comparison on 25 Kincaid46 recordings vs. 4 commercial services + 5 transcription services (§3.9, Figure 7).
- Ablations: model-size scaling (§4.1, Figure 8), dataset-size scaling with a controlled medium-model subsampling study (§4.2, Table 6), multitask/multilingual transfer vs. compute (§4.3, Figure 9), text-normalizer sensitivity vs. FairSpeech's normalizer (§4.4, Figure 10), long-form decoding heuristic ablation (§4.5, Table 7).
- All of the above are paper-reported experiments; the README describes none of these — it only documents installation and inference usage. Per task rules, README content (e.g., the `turbo` model, model table with a `large-v3`-based figure) must be kept separate and is **not** paper experimental evidence.

## 7. Available result evidence (numbers legible in snapshot)
Representative exact figures (see Gold Account §10 for the full ledger):
- LibriSpeech test-clean WER: best zero-shot Whisper (Large V2) **2.7%** greedy / reported as "2.5" in prose (§3.3 L279) — note: prose says "relatively unremarkable LibriSpeech clean-test WER of 2.5" while Table 8/9 report 2.7/4.2-range numbers for different decoding settings; both are legible but not identical, so both are recorded rather than reconciled.
- Table 2: zero-shot Whisper makes "55.2% less errors on average" vs. a matched wav2vec 2.0 model on 11 OOD datasets (L395).
- Table 3: MLS WER 7.3 (Whisper) vs. 9.7 (Maestro); VoxPopuli WER 13.6 (Whisper) vs. 8.1 (Maestro, best).
- Table 4: CoVoST2 X→en "All" BLEU 29.1 (Whisper) vs. 25.2 (Maestro, best) — new SOTA claimed (L710).
- Table 5: Fleurs language-ID accuracy 64.5% (Whisper) vs. 77.7% (mSLAM-CTC); 80.3% on 82-language overlapping subset (L715), upper bound 80.4% due to 20 unseen languages.
- Table 6: dataset-scaling from 3,405h→681,070h drops English WER 30.5→9.9, multilingual WER 92.4→29.2, raises X→en BLEU 0.2→24.8.
- Table 7: long-form decoding heuristics reduce average WER 11.0 (greedy) → 10.0 (full heuristic stack) across 7 datasets.
- Figure 7 prose: computer-assisted human service WER is "1.15% point better than Whisper's"; pure-human performance "only a fraction of a percentage point better" (L760) — exact pure-human number NOT IN SNAPSHOT (only in the figure image).
- Model family table (Table 1, L222–237): Tiny 39M…Large 1550M parameters, exact layer/width/head counts.
- Much of Appendix D's large per-language/per-dataset numeric tables (Tables 8–16) are legible as space-separated number runs but their column headers are transposed/interleaved by pdftotext (see Risks) — usable only with caution and cross-checking against row/column counts.

## 8. Source quality
- **Authoritative:** `paper.txt` (official arXiv v1 text by the Whisper authors) for all research claims, experiments, and results.
- **Authoritative for artifact facts only:** README at pinned commit (install instructions, license, model-name table) — per task rule, never used for paper research claims.
- **Secondary / outside snapshot:** ICML 2023 poster page (used only for venue confirmation in this assessment, not folded into the Gold Account's research content).

## 9. Reproducibility / accessibility
- Code and model weights are released (README, MIT license); inference code only, no training code, and the 680,000-hour training dataset itself is not released (paper Abstract, L8).
- Text-normalizer code stated as released (Appendix C, L1248).
- Long-form decoding heuristics (§4.5) are described in enough prose detail to reconstruct as a procedure, though exact thresholds (temperature step 0.2, no-speech threshold 0.6, avg-logprob threshold −1, compression-rate threshold 2.4, initial timestamp window 0–1.0s) are all explicit numbers in text (L968, L1000).
- Several evaluation datasets require LDC licenses (WSJ, CallHome, Switchboard) or are not freely redistributable in full (CORAAL, Earnings-21/22 via third-party repo) — this is an accessibility observation by this assessment, not a claim made in the paper.
- Not re-executed for this assessment.

## 10. Suitability for this evaluation
- **Methodology reconstructable?** Yes. Data construction/filtering pipeline (§2.1), model architecture and tokenizer (§2.2), multitask token format (§2.3, Figure 1), and training details (§2.4, Appendix F) are all described in enough prose/table detail to reconstruct the method conceptually (not to literally retrain it, since the dataset is private).
- **Experiments & results identifiable?** Yes, extensively — nine distinct experiment/ablation sections (§3.1–3.9, §4.1–4.5) each with at least one exact, legible top-line number, even where large supporting tables are partly garbled.
- **Gold Account without guessing?** Yes. The paper is long and numerically dense; many exact numbers are recoverable, and where a number exists only in a figure image (e.g., precise pure-human WER in Fig. 7, Figure 5 noise-robustness curve values, Figure 11 per-language hour counts) this assessment and the Gold Account explicitly mark it NOT IN SNAPSHOT rather than estimate it.
- Evaluation value: high — a widely known, high-impact paper (useful realism check for readers) with a genuine README/paper divergence (turbo, large-v3, model-count changes) that tests whether reconstructions correctly separate paper-era claims from later repo evolution.

## 11. Risks
1. **README reflects a much later repo state than the paper.** The pinned README lists six-model-plus-`turbo` and a `large-v3`/`large-v2` comparison figure; the paper (arXiv v1, Dec 2022) only ever discusses Tiny/Base/Small/Medium/Large and, via a footnote (L216), an added "Large V2" trained after the original release. `turbo` and `large-v3` are **not in the paper at all** — this is a clear, explicit paper/README conflict that must be flagged, not silently merged.
2. **pdftotext damage to multi-column tables/figures.** Appendix D's dense per-language WER/BLEU tables (Tables 8–16) have their header rows and data rows visually reordered/concatenated by column-major extraction; Figure 11 (training-data-per-language, L1957–2107) is essentially unreadable as extracted (language names and digits interleaved character-by-character in places, e.g. L1961–2107). Numbers from these were only used above when a table caption plus surrounding prose independently confirms the value (e.g., Table 3, 4, 5, 6, 7 have prose cross-references); raw Table 8–16/Figure 11 values are treated as illustrative, not independently verified, and are excluded from the Gold Account's core claim/evidence table unless individually legible and self-consistent.
3. **Figure-only results.** Figures 2, 5, 6, 7, 8, 9, 10 convey quantitative relationships (e.g., robustness frontier, noise-degradation curves, per-model WER distributions) with only some values restated in prose; exact figure-only numbers are recorded as NOT IN SNAPSHOT.
4. **Two slightly different LibriSpeech-clean numbers for the same model** appear in prose ("2.5", L279) vs. Table 8/9 (2.7 / 4.2 depending on decoding and tiny vs. large model) — likely because the prose figure refers to a different checkpoint/decoding setting than the table row being read; both are recorded distinctly in the Gold Account rather than reconciled by inference.
5. **Superseded/updated reporting within the paper itself:** footnote 3 (L216) states results are updated to use "Large V2" (trained after original release with added regularization) "unless otherwise specified" — so Table 2/3/4/5 "Large" numbers may already be V2 numbers under a different label; this ambiguity is preserved rather than resolved.
6. **Dataset not released**: reconstructing the *exact* training corpus is not possible from the snapshot (by design — this is stated as a fact, not treated as a paper weakness).

## 12. Recommendation: **ACCEPT WITH CAVEATS**
Reasons:
- The paper is long, well-structured, and unusually rich in exact, legible experimental numbers across nine distinct evaluation axes; a rigorous, mostly-complete factual Gold Account can be built without guessing.
- Caveats: (a) the pinned README is far newer than the paper and introduces artifacts (`turbo`, `large-v3`) absent from the paper — these must never be attributed to the paper; (b) several appendix tables and one appendix figure are extraction-damaged and are excluded or flagged rather than used as primary evidence; (c) the paper's own footnote about "Large V2" superseding "Large" results in later tables introduces an internal versioning ambiguity that the Gold Account records rather than resolves; (d) the explicit Limitations and Future Work section (§6, L1008–1021) is unusually clear and directly supports Q9/Q11 scoring.

Sources used for venue/peer-review confirmation:
- https://icml.cc/virtual/2023/poster/24519
- https://arxiv.org/abs/2212.04356
