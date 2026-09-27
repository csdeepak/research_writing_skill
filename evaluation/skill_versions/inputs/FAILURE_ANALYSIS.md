# Phase 8 — Failure Analysis (baseline: skill v0.1.0, evaluator v0.2)

Written after the Phase 5 baseline was complete for F1 (6/6 pairs) and partial for F2 (3–4/6 pairs). Every cluster below cites its evidence file. Origin codes (from the brief): **A** evidence acquisition · **B** reasoning/story construction · **C** drafting · **D** revision · **E** reviewer · **F** evaluation design.

Evidence files: `results/comparison/scores/per_review.json`, `results/comparison/scores/nugget_diff_F1.json`, `results/skill_process_audit.json`, `reviewer_validation/scores/*`, `logs/DECISIONS.md`.

## 1. Skill-side failure clusters

### S1 — Author-stated limitations replaced by writer-derived limitations  (origin **B/C**; highest impact)
- **Observation:** with the F1 (Claude Opus) reader, skill papers lost more Q11 "main limitations" nuggets than plain papers: net −7 across 6 projects (OpenHands −5: Q11a/c/d/e plus Q9b/Q9c; BEIR Q9b, Q11e; Whisper Q11d; SAM Q11c; MLPerf Q11b). With F2, net −1 (smaller sample).
- **Mechanism (verified in text):** the OpenHands skill paper's Limitations section consists of writer-derived methodological caveats ("results are single runs without variance estimates …") and omits the authors' own statements ("agents still struggle with complex tasks", "may not achieve top performance in every category"). Two skill rules push this way: `section_rules.md` LIMITATIONS "Must not: generic limitations … not attached to claims" and `failure_states.md` LIMITATION_MISSING "Draft the limitation from the claim graph". Author-stated but broad limitations are treated as "generic" and dropped; writer-generated caveats take their place.
- **Why it matters:** the reader's model of *what the authors concede* is lost, and writer-originated critique is presented in the authors' voice (an attribution error the skill's own P3/P11 principles should forbid).
- **Generalizes?** Yes: 5/6 projects under F1.

### S2 — Loss of the authors' motivation and design rationale  (origin **B**)
- **Observation (F1):** net −3 on Q2 (motivation) and −3 on Q5 (why this design). MLPerf lost Q2b, Q2d, Q5a–c, Q8b (all author rationale/interpretation); SAM lost Q1b (problem framing as three questions) and Q5b (why multi-mask); Whisper lost Q5b; SWE-bench lost Q2a.
- **Mechanism:** the skill's spine/claim map privileges evidence-bound claims; author rationale is typed `interpretation` or `context`, which the writer compresses or re-frames in its own terms ("the spine"). Interpretation-strength nuggets: lost 6 vs gained 2 (F1).
- **Generalizes?** 4/6 projects (F1). Not observed with F2 (net −1/0).

### S3 — Low process adherence: the skill as executed ≠ the skill as designed  (origin **C/D**, root cause in skill packaging)
- **Evidence:** `results/skill_process_audit.json`. Artifact coverage 0.38–0.69; question ledger, term ledger and lit→gap chain never built; validator and linter never run in any of 6 runs; `section_rules.md` (RIC, section contracts), `citation_rules.md`, `audience_model.md`, `information_design.md` never opened in any run; all runs self-certified gates G1–G5 as "passed"; produced artifacts violate the skill's own schemas (141–227 validator errors per run).
- **Implication:** the measured effect is the effect of `SKILL.md` + `workflow.md` + one external review round — not of the full design. Mechanisms placed in secondary files did not reach the writer. Gates are honor-system only.
- **Generalizes?** 6/6 runs.

### S4 — Length overruns  (origin **C/D**)
- Skill papers exceeded the 4,500-word limit in 2/6 (BEIR 5,071, Whisper 5,888) vs 0/6 plain. The skill adds sections/caveats; no length gate exists.

### S5 — Precision that reads as contradiction  (origin **C**)
- OpenHands skill paper correctly attributes web results to BrowsingAgent but keeps the authors' conclusion "CodeActAgent is competitive across categories"; the F1 reader resolved the tension against the authors' claim (Q8a/Q12b `contradicted`). Single case — watch-list only, no change.

### S6 — Results comprehension: mixed, possibly positive  (component: RIC / results rules)
- F2 reader: skill net +4 on Q7 (strongest results) and measured/derived nuggets lost 2 vs gained 9. F1 reader: measured/derived lost 11 vs gained 8. Reader-dependent; not a failure cluster, but the only signal that a v0.1.0 component helps.

## 2. Evaluator / evaluation-design failures (fixed or documented; NOT skill changes)

| ID | Failure | Origin | Status |
|----|---------|--------|--------|
| E1 | Reviewer ignored the defined 12 reconstruction questions (substituted its own sequence) | E/F | **Repaired** → evaluator v0.2 (D-13); all reviews re-run |
| E2 | Grader scored misaligned answers inconsistently | F | **Repaired** (whole-reconstruction search, D-13) |
| E3 | Clean benchmark item contains genuine defects ([CITATION NEEDED], text-only figure) | F | Documented (D-11); comparisons vs A still valid |
| E4 | EXPECTED.json over-specifies dimension drops (e.g., B "contribution") | F | Documented; attribution metric reported as provisional |
| E5 | Nemotron (F2) emits malformed JSON in ~3/19 outputs | E | Retry once; failures excluded, reported |
| E6 | Reviewer dimension scores favour skill papers (+0.56, F1) while reconstruction recall falls (−0.087) | E/F | **Key finding** — reviewer ratings are not a valid proxy for reader understanding in this setting; the primary metric must remain reconstruction |
| E7 | Reconstruction is insensitive to ordering/jargon/buried-contribution defects for a strong LLM reader (Phase 4 B, C, F ≈ 1.0) | F | Limitation: LLM readers under-detect comprehension costs that would affect humans |
| E8 | Reader-family disagreement on project-level effects (e.g., OpenHands F1 −0.35 vs F2 +0.01) | E | Report per family; no pooled claim without both |

## 3. Infrastructure failures (not attributable to skill or evaluator)
Codex/OpenAI model access revoked mid-run (D-10); Claude CLI credit exhausted (D-14); two session-limit interruptions (D-06, later); OpenRouter free-tier limits. None produced fabricated data; all failed runs are logged and excluded.

## 4. Candidate changes ranked for the engineering loop (Phase 9)

1. **S1 + S2 → attribution-preserving limitation/rationale rule** (artifact field + section-contract change): the claim map gains `origin: author_stated | writer_derived`; the Limitations contract requires every author-stated limitation in the evidence to be reported (attributed) and forbids presenting writer-derived caveats as the authors' statements (they go in a clearly labelled "Additional caveats" paragraph); Q2/Q5 author rationale must be preserved as attributed interpretation in Introduction/Method. Smallest mechanism addressing the two largest clusters.
2. **S3 → put the load-bearing rules where the writer reads them**: inline the RIC, section contracts summary and limitation/attribution rules into `SKILL.md`; make the tool gate executable (lint + validate must run and their output file must exist before G3/G5 may be marked passed).
3. **S4 → length gate** in step 21 (word count vs requirement; relocation, not deletion).
Changes to be tested on a held-out subset with the same writer/reader/grader protocol and compared with the frozen v0.1.0 baseline.
