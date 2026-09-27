# Step 11 — Reader Reconstruction Self-Test

Answering Q1-Q12 from the draft alone:

Q1 What is the problem? → Image segmentation lacks a foundation model enabling zero-shot generalization. ✓
Q2 Why does it matter? → Segmentation underlies many vision tasks; a promptable model enables composable pipelines without per-task retraining. ✓
Q3 What is already known? → NLP/vision-language foundation models (GPT-3, CLIP) work; segmentation datasets are tiny relative to text. ✓
Q4 What is the gap? → Masks are not web-abundant; no promptable segmentation model or large-scale mask dataset exists. ✓
Q5 What is the RQ? → Can a promptable task, capable model, and data engine together enable zero-shot segmentation generalization? ✓
Q6 What was done? → Designed promptable task; built SAM (image encoder + prompt encoder + decoder); ran 3-stage data engine; collected SA-1B. ✓
Q7 What was measured? → mIoU on 23 datasets; human quality ratings; edge detection metrics; AR@1000 proposals; instance seg AP. ✓
Q8 What was found? → SAM outperforms RITM on 16/23 auto (all 23 oracle); human raters prefer SAM masks; competitive with supervised. ✓
Q9 What does it mean? → Promptable segmentation enables composable module use; foundation model for segmentation is feasible. ✓
Q10 What are the limits? → Fine structures; heavy encoder not real-time; text prompting not robust; no clear semantic/panoptic prompting; domain specialists may still win. ✓
Q11 What's next? → Community builds on released model + dataset; text prompting improvable. ✓
Q12 What is the contribution? → Task definition + SAM architecture + SA-1B (400x largest); data engine approach. ✓

All 12 answerable. Gate G2 equivalent passed.

Issues to fix for final:
- Add key results tables (Tables 3, 4, 5 from paper) — currently results are prose only
- "SAM guarantees a valid output" → soften to "aims to produce a valid output"
- Remove Kirillov et al. 2023 self-citation from References
- Spell out OIS metric fully
- Note Canny 1986 is a classical algorithm for non-CV readers
