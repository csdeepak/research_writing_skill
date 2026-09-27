# Open Issues

Generated after step 21 (final language edit, tag strip). These items remain genuinely unresolved and are retained in the manuscript as markers or noted here.

---

## 1. [CITATION NEEDED] — Deployment-pressure motivating claim

**Location:** §1, paragraph 1
**Marker in paper:** `[CITATION NEEDED: quantified statistic on LM deployment in software development]`
**Issue:** The claim that LMs are "increasingly deployed" as coding assistants is accepted as background fact but no citation quantifying scale was available in the project corpus.
**Required action:** Authors should supply a citation (e.g., a survey or usage report) or soften to qualitative framing.

---

## 2. Undisclosed per-model context limits in Table 3

**Location:** §3.1, §4.1, Table 3
**Issue:** The best BM25 resolve rate is reported per model but the specific context limit (13k / 27k / 50k) used for each model's reported number is not disclosed. This makes cross-model comparisons in Table 3 sensitive to a tuning choice readers cannot inspect.
**Reviewer note (diagnostics score 4):** "Report the chosen context limit per model in Table 3 or show all limits."
**Required action:** Authors should add a footnote to Table 3 or a column specifying the chosen limit, or report all three limits in an appendix table.

---

## 3. Reconciliation of 74.5-line vs. 32.8-line gold patch means

**Location:** §4.4
**Issue:** The mean gold patch across all 2,294 instances is 32.8 lines (Table 1), yet the mean gold patch over the applied-patch subset is reported as 74.5 lines. The paper now notes this difference and offers two possible explanations (subset difficulty, different line-counting convention), but does not resolve which explanation is correct.
**Required action:** Authors should verify whether 74.5 uses the same counting convention as Table 1 (net edited lines vs. total diff lines including context), and either harmonize the metrics or state the definitional difference explicitly.

---

## 4. Temporal analysis — two-bucket limitation

**Location:** §4.6
**Issue:** The memorization check uses only two time buckets (before/after January 2023) with no instance counts, no variance, and the retrieval setting is not disclosed. The paper now explicitly notes that this is not a formal memorization test.
**Assumption recorded:** The framing is softened to "no evidence that older instances are easier" rather than "no correlation."
**Required action:** A finer temporal analysis (quarterly buckets, counts, one-sided confidence intervals) would substantially strengthen this claim.

---

## 5. Oracle (non-collapsed) result for Claude 3 Opus is missing

**Location:** Table 4
**Issue:** The oracle (non-collapsed) cell for Claude 3 Opus is blank. This means the headline oracle-collapsed number (9.39%) has no within-model oracle comparison to show how much the collapse step helped for the best model.
**Assumption recorded:** Cell annotated as "not evaluated" rather than left silently blank.
**Required action:** Authors should run and report this condition, or provide a brief explanation of why it was skipped (e.g., compute budget).

---

## 6. Oracle-collapsed results for SWE-Llama not available

**Location:** Table 4
**Issue:** Oracle-collapsed conditions were not evaluated for SWE-Llama 7b and 13b. Given that SWE-Llama suffers severe BM25 distribution shift, an oracle-collapsed comparison would be informative.
**Assumption recorded:** Cells annotated as "not evaluated."
**Required action:** Run these conditions or note in the paper that SWE-Llama training on oracle-retrieved files makes the oracle-collapsed setting less meaningful for diagnosing distribution shift.

---

## 7. Qualitative patch analysis — sample size and selection

**Location:** §4.4 (and previously §5 in v001)
**Issue:** The qualitative patterns (primitive code, greedy symptom-fixing, no structural improvements) rest on a small number of hand-selected instances; selection criteria and representativeness are not established. The paper now labels this "illustrative only."
**Required action:** Either provide selection criteria and a systematic sample, or move this discussion to a "preliminary observations" framing and reduce the strength of the behavioral claims.

---

## 8. Complexity metrics analysis — corpus-wide quantification absent

**Location:** §5.2
**Issue:** The Cyclomatic / Halstead complexity analysis is presented as a single illustrative case (requests/HTTPAdapter). The general claim — that test passage underestimates the quality gap — is supported only by this example.
**Assumption recorded:** Framing downgraded to "illustrative case" with explicit note that corpus-wide analysis is needed.
**Required action:** Extend the complexity analysis to the full set of applied patches and report the distribution of Δcomplexity (model − gold) to substantiate or refute the general claim.

---

## 9. Missing evidence: variance / confidence intervals

**Location:** §7 (Limitations), Table 3, Table 4
**Issue:** Greedy decoding (Pass@1) was used throughout; no variance across seeds is available (missing evidence M001). The denominator for many results is small (e.g., GPT-4 on 25% subset = 574 instances; Claude 3 Opus resolves ~87 of 2,294 instances at 3.79%).
**Assumption recorded:** No-variance caveat added to §7 and inline note added to §4.1.
**Required action:** At minimum, report the raw resolved-instance counts alongside percentages so readers can compute approximate binomial confidence intervals independently.

---

## 10. SWE-bench Lite filtering criteria not fully described

**Location:** §2.4
**Issue:** The criteria for selecting the 300 Lite instances ("more self-contained, focused on functional bug fixes") are not specified beyond this brief description (missing evidence M002; Appendix A.7 was incomplete in the source text).
**Required action:** Authors should add the sampling or filtering rules used to select Lite instances, or cite the appendix section where they appear.

---

*Issues 1, 2, 3, 5, 6, 9, 10 require author action or additional experiments. Issues 4, 7, 8 are mitigated in the current manuscript by softened framing but would be strengthened by additional analysis.*
