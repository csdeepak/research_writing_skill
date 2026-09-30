# Stage 3 M13 proxy run: ASMOS results excerpt

**What this is:** an end-to-end execution of `tools/comprehension_kit.py` with **LLM proxy readers**
(Claude Opus, isolated subagents, one per packet) and **two independent LLM graders** (Claude Sonnet),
on the Stage 2 ASMOS acceptance project (the user's real results). **It is not human evidence.** The
spec's Stage 3 acceptance requires blinded human reconstruction results (`templates/human_study_protocol.md`).

Answer key: `comprehension_key.json` (pre-declared from the claim map, hash-frozen before any reader
saw a packet): FOUND 4, UNCERTAIN 2, DATA 1 nuggets. DONE and LIMITS are unscorable, because the
excerpt's claim map records no method or limitation items (reported as such rather than invented).

| Run | Condition | RR | DR | IR | MMF | Graders agree (α) |
|---|---|---|---|---|---|---|
| run2 (valid) | full paper | 0.786 | 0 | 0.286 | **0.643** | 1.0 |
| run2 (valid) | visual-only (headings, figures, captions) | 0.571 | 0 | 0.0 | **0.571** | 1.0 |
| run1 (defective, archived) | full | 0.786 | 0 | 0.43–0.57 | 0.50–0.57 | — |
| run1 (defective, archived) | visual-only | 0.500 | 0 | 0.43–0.71 | 0.14–0.29 | — |

n = 1 proxy reader per condition, so no interval is reported. Treat these as a pipeline check and a
weak signal, not an effect estimate.

**What the run found (about the tooling, not the paper):**
1. *Run 1 was invalid.* The graders' reference text was the paper excerpt without the figure
   captions, so true statements that readers took from the captions (e.g. "all systems use
   gpt-4o-mini") were counted as unsupported beliefs. This is D-24's evaluator defect reappearing
   in the new kit. Fix: the reference is now the full packet, i.e. everything any reader could see.
2. *Text-only readers saw less than sighted ones.* The Markdown packet gave LLM readers only alt
   text, while a sighted reader sees the plotted values. Fix: packets now include the values as
   drawn. This still slightly favours LLM readers on bar charts, where humans read values off an
   axis (limitation).
3. *CI bug.* The first scoring bootstrapped over gradings; two graders of one answer are not two
   readers. Fix: average graders per response, then bootstrap over readers (none with n = 1).

**What it suggests about the paper (weak, proxy, n = 1):** the figures and captions alone carry most
of the findings (RR 0.571 vs 0.786). The gap is concentrated in the paired-bootstrap result
(RAG − ASMOS +0.336, CI +0.149 to +0.523), which appears only in the prose. That result could go into a
caption if the authors want the figures to stand alone.

Files: `run2/` (packets, SEALED map, responses, grading sheet, grader outputs, report.json),
`run1_defective_reference/` (kept for the record).
