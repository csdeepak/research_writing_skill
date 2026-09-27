# Open Issues — Segment Anything Manuscript

*Generated after step 21 (v001, round 1 review). Items are grouped by severity.*

---

## High priority — must resolve before submission

**1. No figures in manuscript (review score 1/5 for figure_table dimension)**
The paper contains no architecture diagram, no qualitative mask examples, and no illustration of the ambiguity concept (subpart/part/whole). The task constraints for this run prohibited images; all figures are described verbally. For any real submission, the following figures are needed:
- Architecture overview: image encoder → embedding → prompt encoder + mask decoder pipeline
- Ambiguity illustration: one image with three valid masks at different scales
- Qualitative mask samples showing data engine stages and example SA-1B masks
- Qualitative edge/proposal/instance results

**2. Statistical significance of the 8.1 vs. 7.9 instance segmentation human-rating gap is unreported**
The manuscript now notes this result is "suggestive rather than definitively significant," but the underlying significance test should be supplied by the authors. If the difference is not significant, the claim in §5.5 and the conclusion needs to be weakened further.

---

## Medium priority — weakens argument but not blocking

**3. Metric mismatch in mask-quality comparison (§4.3)**
The comparison between SA-1B's 94% >90-IoU threshold-exceedance rate and the 85–91% mean inter-annotator IoU from prior work compares different statistics. The manuscript now includes a caveat, but a directly commensurable metric (e.g., computing mean IoU on the same 500-image sample) would make the comparison defensible rather than merely suggestive.

**4. Oracle–confidence gap causation uninvestigated (§5.2)**
The manuscript hedges the claim that the oracle-vs.-confidence gap is purely due to prompt ambiguity by adding "though confidence-head miscalibration could also contribute." No analysis has been run to apportion the gap. An ablation varying prompt-point location (to manipulate ambiguity) while holding confidence-head calibration constant would separate these causes.

**5. Annotation-bias causal story for AP shortfall (§5.5)**
The authors attribute SAM's AP shortfall despite human preference to annotation bias (LVIS polygon-only masks, COCO low-quality masks). The manuscript now flags this as "consistent with the observed pattern but not uniquely confirmed." A direct experiment — e.g., reannotating a random LVIS subset with richer masks and retesting AP — would confirm or refute this explanation.

**6. Text-to-mask proof of concept lacks quantitative characterization (§5.6)**
The CLIP embedding-swap approach is described qualitatively. The review flagged that adjacent readers want to know how reliably the swap transfers across concept types. At minimum, reporting the fraction of test phrases for which text-to-mask succeeds vs. requires a fallback point would ground the "proof of concept" framing.

---

## Low priority — presentation and clarity

**7. No median or typical mIoU gap versus RITM is reported (§5.2)**
The manuscript reports the maximum gap (~47 IoU points) and adds "on the 7 datasets where RITM leads, the margins are smaller." The median per-dataset gap across all 23 datasets would give a more representative picture. The underlying values were not available from the project files; authors should add this figure.

**8. Table 1 (edge detection) still lacks a Training column in the source data**
The revision added "Trained methods (top) / Zero-shot methods (bottom)" in the caption with an explicit row separator, but a formal "Training data" column would make the table self-contained without relying on caption text.

**9. Geographic representation of SA-1B is still imbalanced (§6)**
The manuscript reports and contextualizes the geographic skew honestly. This is not a problem introduced by the manuscript, but practitioners deploying SAM in Africa or Latin America should be aware that SA-1B's coverage of those regions, while larger in absolute terms than any prior dataset, is proportionally underrepresented. The manuscript already recommends awareness; no further revision required for the manuscript, but future dataset work should target these regions.

**10. Assumption log**
The following assumptions were recorded in lieu of human input during this run:
- Audience confirmed as **B (adjacent ML researcher)** from task instructions (no human available).
- Venue unknown; paper written as a generic conference/journal manuscript with standard ML structure.
- Literature mode limited to cited works in `project/paper.txt`: registered with `verification.method=user_supplied_file`.
- No figures produced (task constraints); key quantitative results reproduced in Markdown tables.
- Per-dataset mIoU values for Fig. 9a are not available in the project files; reported as ranges and counts only.
- Oracle mIoU values per dataset are not available; reported as summary statistics (16/23, all 23).
