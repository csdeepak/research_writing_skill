# CORPUS_AGENT Run Summary — mode: evidence

- **project_root:** `./project/`
- **out_dir:** `./out/`
- **generated_at:** 2026-09-24
- **Inputs opened:** `paper.txt` (2157 lines, full read incl. abstract, body Sections 1-7, and Appendices A-F), `README_1.md` (full). No other files exist in `project/`.

## Key context affecting classification
This project contains **only a published paper document (`paper.txt`) and a README** — there are **no raw data, log, or results files** (CSV/JSON/logs). Per the strength rules and evidence model ("a value that appears only in prose/drafts/READMEs and not in a data file is `soft`"; "MUST NOT upgrade strength"), **every evidence item is `soft`**: the numbers are reported in a publication document, not reproducible from a data artifact in this session. Values read from figures additionally carry `extracted_from_image: true`. This is deliberate and conservative — despite the paper's results being machine-produced, they are not verifiable-from-files here, so no item was promoted to `hard`.

## Counts

### Evidence items: 48 total (all `strength: soft`)
By kind:
- dataset: 5 (E001-E005)
- method_detail: 6 (E006, E010, E012*, E033, E034, E035)  *E012 tagged metric
- metric: 1 (E012)
- implementation_detail: 5 (E007, E009, E043, E044, E045)
- result: 8 (E013, E014, E015, E016, E018, E021, E022, E026, E027, E028, E029)
- observation: 6 (E020, E023, E025, E030, E032, E042)
- negative_result: 3 (E019, E024, E031)
- limitation_noted: 5 (E037, E038, E039, E040, E041)
- hypothesis_stated: 2 (E046, E047)
- assumption: 1 (E048)
- external_fact: 1 (E017)
- (E008, E036 = method_detail / observation)

By status: `ok` = 43, `conflicting` = 2 (E014, E015), `incomplete` = 3 (E013, E018, E028).
`extracted_from_image: true` = 6 (E004, E025, E026, E030, E031, E032).

### Conflicts: 1 pair
- **E014 vs E015** — best zero-shot Whisper LibriSpeech test-clean WER: Section 3.3 prose says **2.5**, Table 2 says **2.7** for Whisper Large V2 (same quantity, same conditions). Marked `conflicting` on both with `conflicts_with`; **not resolved** (per constraints, conflicts are flagged, never averaged/filled). Appendix Tables 8/9 would help arbitrate but their cells are OCR-jumbled and could not be reliably attributed.

Rounded-vs-precise restatements (NOT treated as conflicts): 680,000≈681,070 h total; 117,000≈117,113 h multilingual; 125,000≈125,739 h translation. Recorded with notes linking the rounded and precise items.

### Claim candidates: 22 total (C001-C022)
- origin `author_stated` (with ≤25-word quote): 20
- origin `inferred`: 2 (C020 architecture sizes; and design-detail claims)
- By type: measured 10, derived 2, observed 3, interpretation 1, hypothesis 1, speculation 1, future 1, (C007/C008/C009 measured negatives).
- **All confidence = low.** Rationale (mechanical, per evidence_model §4): every claim rests on `soft` evidence (a "lowers" factor) AND on single reported runs with no variance/spread (a second "lowers" factor). Two lowers ⇒ low. No claim can reach `high` (that requires all-`hard`). Strength was not upgraded to inflate confidence.
- Watch-list terms preserved as author language and flagged, not laundered: "state of the art"/"SOTA" (C004, E021), "significant(ly)" (C007), "close to human-level" (C013).

### Missing evidence: 10 items
Headlines: no variance/seeds for any metric; no source data files at all; OCR-garbled appendix tables (D.1-D.4, Fig 11); imprecise human-transcriber advantage; baselines not re-run under matched conditions; no encoder-vs-decoder ablation; figure-only noise/long-form numbers; no fine-tuning results; turbo/large-v3 undocumented in the paper; unquantified human robustness CI (Fig 2).

## Negative results and author-stated limitations (recorded, not suppressed)
- Negative results: VoxPopuli underperformance (E019), language-ID underperformance (E024), high-resource translation no-improvement (E022), negative transfer for small models (E031), speaker-name hallucination in development (E036), Welsh translation data-quality outlier (E023).
- Author-stated limitations: 30s input limit (E037), long-form failure modes / hallucination (E038), English-heavy data / <1000h for most languages (E039), zero-shot-only / no fine-tuning study (E040), encoder-vs-decoder attribution unclear (E041), diminishing returns 54k→680k h (E042).

## Suspicious content
None. No instructions directed at AI systems or reviewers were found embedded in `paper.txt` or `README_1.md`. All content treated as data.

## Could not open / could not fully use
- No files were skipped; both project files were fully read.
- Appendix D tables (8-16), Appendix E Figure 11 numeric layout, and Appendix F were read but the OCR reflow interleaves columns, so individual per-cell values in those large tables were **not** transcribed as discrete evidence items (only the clearly attributable main-body tables 1-7 and prose figures were extracted). Flagged under missing_evidence #3.

## Constraint compliance
- No web access used; no subagents spawned; worked only inside this directory.
- Numbers copied verbatim from `paper.txt` / `README_1.md`; no strength upgraded; conflicts flagged not resolved; missing items listed not filled; negative results and limitations recorded as first-class.
- Did not read `review_agent.md`, `recon_grader.md`, or `skill_agent.md`.
