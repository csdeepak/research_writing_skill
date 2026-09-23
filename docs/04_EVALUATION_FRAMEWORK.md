# 04 — Evaluation Framework

**Success criterion (from the brief):** *the reader's mental model of the paper is closer to
the actual research.* Everything else is diagnostic.

So evaluation has one **primary outcome** (reconstruction fidelity against a gold story derived
from Level-0 evidence) and many **secondary diagnostics** (20 dimensions, rigor and traceability
metrics, readability signals). The secondary metrics explain failures. They are never
optimized directly.

---

## 1. The gold reference story

Before any paper is evaluated, the project needs a **gold story** (`gold_story.json`):

- The 12 reconstruction answers (§2), each decomposed into **atomic key points** ("nuggets").
  Example for Q8 ("what do results establish?"): `["method reduces error on dataset D by
  ~X relative to baseline B", "effect holds across 3 seeds", "only tested at scale S"]`.
- Each nugget has an `evidence_ids` list pointing into `research_evidence.json`.
- Each nugget has a `strength` label (same ladder as claims: measured … speculation), so a
  reader's answer can be checked for **strength distortion** as well as presence.
- It is written by AUTHOR from the claim map and **approved by the researcher**. Without that
  approval, the evaluation is labeled `provisional`.

The gold story is never shown to REVIEW_AGENT.

---

## 2. Audience reconstruction test

REVIEW_AGENT answers these after reading, using only the paper:

| # | Question | Tests |
|---|----------|-------|
| Q1 | What problem is this paper solving? | Problem |
| Q2 | Why does this problem matter? | Motivation |
| Q3 | What is missing from existing approaches? | Gap |
| Q4 | What exactly did the authors do? | Approach |
| Q5 | Why did they choose this method? | Design rationale |
| Q6 | What experiments were performed? | Experimental design |
| Q7 | What are the strongest results? | Results |
| Q8 | What do those results actually establish? | Interpretation |
| Q9 | What do they NOT establish? | Scope and non-conclusions |
| Q10 | What is the primary contribution? | Contribution |
| Q11 | What are the main limitations? | Limitations |
| Q12 | What should the reader remember one day later? | Take-home message |

Each answer must cite the paper locations it relied on. "Cannot determine from the paper" is a
valid and informative answer.

### Grading (RECON_GRADER)

A separate, narrow grading call. Its input is only `gold_story.json` plus
`reconstruction.json`. It never sees the paper, so it can't be swayed by how the paper reads.
Humans spot-check ≥20% of gradings.

For each gold nugget *n* and each reader answer:
- `present`: the answer contains *n* with compatible meaning and strength.
- `weakened`: present, but stated more weakly than the evidence supports.
- `overstated`: present, but stated more strongly or more generally than the evidence supports.
- `contradicted`: the answer asserts the opposite.
- `absent`.

The grader also lists **intrusions**: points in the answer that are not in the gold story. Each
intrusion is tagged `benign_elaboration` or `unsupported_belief`.

### Primary metrics

| Metric | Definition | Direction |
|--------|------------|-----------|
| **Reconstruction Recall (RR)** | (present + 0.5·weakened) / total nuggets | ↑ |
| **Distortion Rate (DR)** | (overstated + contradicted) / total nuggets | ↓ (target 0) |
| **Intrusion Rate (IR)** | unsupported_belief intrusions / total nuggets | ↓ |
| **Mental-Model Fidelity (MMF)** | RR − DR − 0.5·IR (range clipped to [−1, 1]) | ↑ |
| **Core RR** | RR restricted to Q1, Q4, Q7, Q10, Q11 (the "first read" core) | ↑ |

DR gets its own metric because an *overstated* understanding is worse than a missing one. A
reader who can't tell what was found is better off than a reader who believes something
false.

---

## 3. Comprehension diagnostics: 20 dimensions

Each is scored 0–5 (0 absent/incomprehensible … 5 excellent). Anchor descriptions are in
`skill/evaluation_rubric.md`. Every score must come with this record:

```json
{"dimension": "result_comprehension", "score": 2,
 "location": {"section": "Results", "paragraph": 3},
 "observed_problem": "Table 2 reported with no statement of which RQ it answers",
 "reader_struggle": "reader cannot tell whether 0.81 vs 0.79 is meaningful",
 "likely_consequence": "Q7/Q8 answered with the wrong 'strongest result'",
 "revision_principle": "state the takeaway and effect size before the table; link to RQ2",
 "persona": ["C", "E"]}
```

| # | Dimension | Group |
|---|-----------|-------|
| 1 | Problem comprehension | Orientation |
| 2 | Motivation comprehension | Orientation |
| 3 | Research-question comprehension | Orientation |
| 4 | Contribution comprehension | Orientation |
| 5 | Method comprehension | Content |
| 6 | Experiment comprehension | Content |
| 7 | Result comprehension | Content |
| 8 | Interpretation comprehension | Content |
| 9 | Limitation comprehension | Content |
| 10 | Overall narrative coherence | Coherence |
| 11 | Terminology accessibility | Load |
| 12 | Logical flow | Coherence |
| 13 | Evidence traceability | Rigor |
| 14 | Figure/table comprehension | Content |
| 15 | Claim-to-evidence alignment | Rigor |
| 16 | Unsupported inference (5 = none) | Rigor |
| 17 | Redundancy (5 = none harmful) | Load |
| 18 | Cognitive load (5 = well managed) | Load |
| 19 | Reader orientation (signposting, paper map, where-am-I) | Coherence |
| 20 | "So what?" clarity | Orientation |

**Personas.** Every dimension is scored from the persona(s) it applies to: A (domain expert),
B (adjacent-domain researcher), C (technically competent, unfamiliar with the topic), D
(educated non-specialist), E (verifying reviewer). The report gives a per-persona profile. A
specialist paper is *expected* to score lower for D on terminology. The target audience
profile tells you which personas are binding.

**No single overall score.** Reports show the dimension vector and the per-group minimum. Any
dimension ≤2 is a **blocking defect**, whatever the average.

---

## 4. Scientific rigor and claim–evidence metrics (automated plus audited)

These come from artifacts and `tools/`, not from the reviewer's impression.

| Metric | Definition | Target |
|--------|------------|--------|
| Traceability rate | Significant claims in the draft with a resolvable `{C###}` whose evidence locators exist | 100% |
| Orphan claim count | Claim-like sentences (numbers, comparatives, causal verbs) without a claim tag | 0 |
| Strength-language match | Claims whose verbs fall within the permitted set for their `claim_type` | 100% |
| Overclaim flags | Hits for the lint patterns: *prove, first, state-of-the-art, significantly* (without a test), *always, novel* (without a basis), causal verbs on correlational evidence | 0 unresolved |
| Citation existence | Cited sources with verified identifiers | 100% (or marked `[CITATION NEEDED]`) |
| Citation support | Citations whose `support_quote` is present and judged to support the sentence | ≥95%; the remainder flagged |
| Negative-result coverage | Negative or failed experiments relevant to a claim that are reported or explicitly excluded with a reason | 100% |
| Uncertainty reporting | Quantitative results with a variance/CI and a stated source of variability, where the data allows | 100% of main-claim results |
| Numeric fidelity | Numbers in the draft that match their evidence value exactly (after declared rounding) | 100% |
| Claim invariance | Claim map before vs after line editing | identical |

---

## 5. Coherence metrics (structural, from the story graph)

| Metric | Definition | Target |
|--------|------------|--------|
| Paragraph role coverage | Paragraphs mapped to a story-graph node | 100% (unmapped paragraphs are moved, cut, or justified) |
| RQ closure | Research questions with ≥1 RESULT node and ≥1 INTERPRETATION node answering them | 100% |
| Contribution grounding | CONTRIBUTION nodes with edges from both GAP and RESULT | 100% |
| Limitation linkage | LIMITATION nodes linked to ≥1 claim | 100% |
| Question debt | Reader questions raised but not answered or explicitly deferred | 0 at section end |
| Term-before-definition | Terms used before definition (term ledger) | 0 |
| Forward-reference load | Forward references ("see §5") in the introduction beyond the paper map | ≤3 |
| Section-role leakage | Introduction paragraphs containing method detail; Results containing unlabelled speculation; Conclusion adding new results | 0 |

---

## 6. Readability signals (secondary; never targets)

Readability formulas are weak proxies for scientific text: they penalize necessary technical
terms and reward choppy prose. They are reported only to **explain** diagnostic findings.

- Sentence length distribution (mean, share > 35 words)
- Acronym density per 1,000 words and acronyms used < 3 times (candidates for spelling out)
- New-term introductions per paragraph (flag > 2)
- Subject–verb distance (long gaps flagged; S01)
- Nominalization proxy (the rate of *-tion/-ment/-ance* nouns followed by "of")
- Flesch Reading Ease (reported only for trend comparison; S11, S27)
- Style-marker frequency (e.g. the LLM-associated vocabulary documented in S10), reported so
  that marker-heavy prose can be reviewed. Presence alone is not a defect.

---

## 7. Inner-loop exit criteria (per paper)

A draft may move to final line editing when all of these hold:

1. No failure state is open, except ones explicitly accepted by the user (recorded in
   `state.json`).
2. Automated audits pass: traceability 100%, orphan claims 0, term-before-definition 0, RQ
   closure 100%, unresolved overclaim flags 0.
3. REVIEW_AGENT: no dimension ≤2 for the binding personas. Dimensions 13, 15, and 16 are ≥4.
4. Reconstruction: Core RR ≥0.8. DR = 0 on nuggets with strength `interpretation` or stronger.
5. Iteration cap: at most 3 review rounds. If the criteria still fail, stop and report the
   remaining defects to the user. Do not loop until the scores look good.

---

## 8. Blind evaluation protocol (for comparing papers or skill versions)

**Design:** paired, within-project comparison. For each project *p*: paper X (baseline) and
paper Y (skill), or skill version *k* vs *k+1*.

1. **Pre-register** (write to `evaluation/prereg_<date>.md`) before running: the hypotheses,
   primary outcome (MMF; Core RR; DR), secondary outcomes, projects, reviewer models and seeds,
   and analysis plan.
2. **Blind labeling.** Papers get random IDs. Condition labels live in a sealed mapping file
   that is opened only after grading.
3. **Format normalization.** Both papers are rendered to the same Markdown format, with
   identical length limits from the venue profile. Claim tags, comments, and metadata are
   stripped. (This is analogous to S20's style normalization. Content is not rewritten, since
   rewriting could change claims.)
4. **Independent reviews.** Each paper is reviewed in a *fresh* context. A reviewer never sees
   both papers of a pair in one context (this avoids contrast effects). Use ≥2 reviewer model
   families × ≥3 seeds.
5. **Counterbalancing.** Where pairwise preference is collected separately, alternate order A/B
   and B/A.
6. **Hard isolation** (03 §2) for every run.
7. **Grading** by RECON_GRADER against the gold story, blind to condition.
8. **Analysis.** Per-project differences in MMF, Core RR, and DR. Report the mean difference
   with bootstrap 95% CIs and the Wilcoxon signed-rank test. With fewer than ~10 projects,
   report effect sizes and CIs and say the result is **underpowered**. Report the direction for
   every project, not just the mean.
9. **Reviewer calibration gate.** Before step 4, the reviewer must detect the planted defects in
   the perturbation benchmark (§9) with ≥90% sensitivity and ≤10% false-alarm rate on clean
   variants. If it fails, the evaluation is invalid.

---

## 9. Controlled perturbation benchmark

Build variants from a *clean base text* (see `skill/tests/perturbations/`) that keep the
scientific content fixed and change one communication property each:

| Variant | Manipulation | Expected detection |
|---------|--------------|--------------------|
| A — clean | — | High scores; no blocking defects |
| B — poor ordering | Research question moved after the methods; contribution list moved to the conclusion | Dims 3, 4, 12, 19 ↓; Q3/Q10 degrade |
| C — jargon | Undefined acronyms and specialist terms added; definitions removed | Dims 11, 18 ↓; persona C/D recall ↓ |
| D — result dumping | Interpretations removed; numbers listed; table without takeaway | Dims 7, 8, 14, 20 ↓; Q7/Q8 degrade |
| E — unsupported interpretation | Hedges upgraded ("suggests" → "proves"); causal claims on correlational evidence; scope generalized | Dims 15, 16 ↓; DR ↑ |
| F — buried contribution | Contribution stated only in the discussion | Dim 4 ↓; Q10 degrades |
| G — citation misuse | A citation attached to a claim it doesn't support; decorative citation list | Dim 13 ↓; citation audit flags |

Uses:
1. **Evaluator validation.** Does the reviewer detect what we planted? (§8 step 9.)
2. **Skill regression tests.** The skill's revision loop, given variant X, must restore the
   defective property without changing the claims.
3. **Mechanism attribution.** Which audit catches which defect, which tells us where the skill
   is weak.

---

## 10. Human-comprehension protocol (the validation that settles disagreements)

LLM scores are not sufficient evidence. Human results override LLM results when they disagree.

**Participants.** Recruit to match the personas: ≥3 readers per persona that is binding for the
paper's audience (e.g. for a specialist venue: A, B, E. For a mixed audience: A–D).

**Procedure (per participant, per paper; each participant sees only one condition per
project):**
1. **First-read task** (timed, ~10 min): title, abstract, introduction, figures and captions
   only. Then answer Q1, Q2, Q3, Q4, Q10, and Q12 in free text, without looking back.
2. **Full-read task:** the whole paper (an untimed cap, e.g. 60 min). Then:
   - What is the main point? What problem is solved?
   - What evidence supports it? (point to it)
   - What is uncertain? What does the paper *not* show?
   - What should you remember?
   - Confidence rating (1–5) for each answer.
3. **Delayed recall (optional, 24 h later):** Q12 and Q10 without the paper.
4. **Section probes (optional):** after each section, answer "What was the main point of this
   section?" This localizes where understanding breaks.

**Grading.** Two graders, blind to condition, score the answers against the gold nuggets using
the §2 categories. Inter-rater agreement is Krippendorff's α. Accept α ≥ 0.67 for tentative
conclusions and α ≥ 0.80 for firm ones. Resolve disagreements by discussion and record them.

**Calibration signal.** Compare human RR/DR with LLM-reviewer RR/DR on the same papers. A large
gap means the LLM reviewer is miscalibrated for this domain. Its scores are then downgraded to
"exploratory" for that domain.

**Ethics.** Informed consent. No personal data in artifacts. Institutional review if required
by the participants' institution. Participants can withdraw.

---

## 11. The final quality test (the skill's acceptance experiment)

For each of ≥5 real projects (≥10 preferred):

- **A:** baseline paper. The same CLI model gets the project folder and the instruction "write
  a research paper for [venue/audience]", with no skill.
- **B:** paper produced with the skill.

Run §8, with §10 on at least a subset. Declare success only if:

1. MMF(B) − MMF(A) > 0, with a 95% CI excluding 0 (or, if underpowered, consistent direction in
   ≥80% of projects and flagged as underpowered).
2. DR(B) ≤ DR(A) in every project (non-negotiable: the skill must never make readers believe
   false things more often).
3. Overclaim flags and citation-support failures are no higher in B.
4. Where human data exists, it agrees in direction.

**Not** success criteria: B "sounds better", B is longer, B scores higher on readability
formulas, or B wins pairwise preference while losing on MMF/DR.

---

## 12. Skill release gate (outer loop)

A candidate skill version *k+1* is accepted only if, on the **held-out** set:
- MMF is non-inferior to version *k* (margin 0.03) and improves on the targeted failure cluster;
- DR and overclaim counts do not increase;
- all regression tests pass (`skill/tests/`);
- reviewer calibration passes (§8 step 9).

The result and the numbers are recorded in `changelog.md`.
