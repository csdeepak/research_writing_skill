# 01 — Foundation Analysis

**Input theory:** *OOMD — Technical Writing*, Units 1–4 (PES University course slides; source F0).
**Method:** I read all four units in full (≈46k words). For each principle I extracted:
(1) what the course asserts, (2) whether it still holds, checked against current publishing
guidance and research (sources `S01`–`S30` in [SOURCES.md](SOURCES.md)), and (3) how it becomes
an **operational mechanism**: something an agent can execute, check, or fail.

The rule throughout: **keep the principle, replace the implementation where needed.**

---

## 1. What the course actually teaches (condensed map)

| Unit | Core content | Underlying principle |
|------|--------------|----------------------|
| 1 | Technical communication is reader-centered, accessible, efficient, and team-produced. Four pillars: clarity, conciseness, accuracy, audience focus. Process: Planning → Drafting → Revising → Editing (the "Glenn" memo case study). Primary, secondary, and tertiary audiences. Purpose types: inform, instruct, persuade. Tone, bias, inclusive language. | *Meaning is what the reader takes away, not what the writer intended.* |
| 2 | Research as critical thinking: define and refine the question (question trees), seek a balance of views, reach adequate depth (popular → trade → specialized literature), evaluate sources (currency, reputation, funding motives, cross-checks), hard vs soft evidence, framing, levels of certainty (conclusive, probable, inconclusive), hidden assumptions, reasoning errors (faulty generalization, faulty causation, statistical fallacies), validity and reliability, note-taking (paraphrase, quote, summarize), documentation (APA, IEEE, MLA), ethics (plagiarism, data honesty, misleading visuals, confidentiality), version control, collaboration. | *A claim is only as strong as its evidence. Say exactly how strong that is.* |
| 3 | Informative titles (the title is a promise), headings as hierarchy and forecast, lists with lead-ins, paragraphs (topic sentence first, "bottom line on top"), coherence devices (transitions, repeated key terms, demonstrative + noun), technical descriptions and instructions, visuals (choosing, constructing, labeling, integrating, captioning, ethics). | *Structure is how the reader navigates. Every visual must earn its place.* |
| 4 | Report types; standard components; IMRaD; title, abstract, keywords; literature review organization (chronological, thematic, methodological) and critique criteria; the thesis statement (declarative, specific, arguable, defensible); proposals; AI tools (drafting, augmentation, verification protocol, prompting, ethics: hallucination, bias, privacy, IP). | *Structure follows the reader's questions: Why? How? What? So what? AI assists; the human verifies.* |

---

## 2. Principles A–X: validity check and operationalization

Legend. **Status:** ✅ still valid as stated · 🔄 valid, but the implementation needs modernizing ·
⚠️ partly obsolete or context-dependent.
**Mechanism** = the component in `skill/` that implements the principle.

| # | Principle (course) | Status | Current-practice check | Operational mechanism (skill) |
|---|--------------------|--------|------------------------|-------------------------------|
| A | **Reader-centered communication.** Readers' needs come first; documents help them learn, do, or decide. | ✅ | Gopen & Swan (S01): meaning is what the reader interprets. Mensh & Kording (S02): structure for the reader. | Reader Question Ledger: every paragraph slot declares the reader question it answers. The Reconstruction Test measures success from the reader's side. |
| B | **Audience analysis** (who, what they know, what they need, culture, medium). | ✅ | Still standard. Jargon research (S12, S13, S27) shows the cost of misjudging the audience. | `audience_profile.json` is required before drafting (failure state `UNCLEAR_AUDIENCE`). |
| C | **Primary / secondary / tertiary audiences.** | 🔄 | The course frames these as workplace roles (decision maker, reviewer, archive). For papers they map to (1) the target community, (2) reviewers and verifiers, (3) future readers, adjacent fields, and replicators. | Audience model: the three tiers map to paper layers. Abstract and introduction serve tier 1, methods and supplement serve tier 2, and keywords, definitions, and data availability serve tier 3. |
| D | **Clarity** (simple direct language, define jargon, logical structure, analogies). | 🔄 | Valid, but "use headings and bullets" is not enough for papers. Clarity failures in LLM drafts are mostly *structural*: concepts appear before they are defined, and old/new information is placed badly (S01). | Term Ledger (define before use, one term per concept). Old→new information check. Topic/stress-position check in the line-edit phase. |
| E | **Conciseness** (cut wordy phrases, no repetition, inverted pyramid). | 🔄 | Valid, but raw word-cutting can delete method details needed for reproducibility (S18). Conciseness means *minimum cognitive load with no loss of reproducibility*. | Density classes (CORE / SUPPORTING / OPTIONAL / SUPPLEMENTARY / DISTRACTING) with *relocation* rules instead of deletion rules. |
| F | **Accuracy** (verify numbers, cite, proofread, second opinion). | ✅ | Now more urgent: LLMs fabricate citations (S06, S25, S26) and over-generalize results (S05). | Claim–Evidence Graph. Every significant claim carries an evidence ID that resolves to a file location. The Numbers Audit re-reads every number from source. |
| G | **Purpose-driven writing** (inform / instruct / persuade; the thesis statement). | 🔄 | A paper informs *and* persuades. Persuasion must be bounded by evidence (S23, S29). The "thesis statement" becomes the **contribution statement**. | Paper Spine: 7 lines (problem, gap, question, approach, key finding, meaning, limit), each bound to claim IDs. Every section must trace back to the spine. |
| H | **Logical organization** (outline, headings, general → specific, IMRaD). | 🔄 | IMRaD is still the default, but many fields (CS/ML, theory) use other structures. The invariant is the *reasoning order*, not the section names. | Research Story Graph (reasoning order) is kept separate from the venue section template (injected). |
| I | **Anticipating reader questions** (Glenn's "anticipated reader's questions"). | ✅ | This is the core mechanism that LLM drafting skips. | Question Ledger with **question debt**: any question the text raises must be answered or explicitly deferred with a pointer. Open debt at the end of a section is a defect. |
| J | **"So what?" reasoning** ("500 MPa makes it suitable for…"). | ✅ | Missing "so what" is the most common problem with LLM result sections. | Result Interpretation Chain (RIC): measure → observation → magnitude → robustness → meaning → link to the research question → non-conclusions. |
| K | **Appropriate technical detail** (expert / novice / mixed). | 🔄 | The course says experts can take undefined jargon and acronyms. Current evidence says otherwise: jargon costs even specialist communication (S12, S27), and acronym density has become a recognized problem. | Term budget per audience mode. Acronyms need a use-count justification. Specialists still get definitions for project-specific terms. |
| L | **Effective visuals** (purpose, simple, labeled, near the text, introduced and explained). | ✅ | Matches S24. Missing from the course: uncertainty display, accessible color, and showing distributions rather than only means. | Figure/Table Card (purpose, takeaway, RQ link, non-conclusions, honesty checks, accessibility). |
| M | **Planning before drafting** (audience, purpose, scope, format, outline, gather resources). | ✅ | This is the step single-pass LLM generation skips. | Workflow steps 1–9 must produce artifacts before any prose. The drafting gate stays locked until the spine, story graph, claim map, and architecture validate. |
| N | **Drafting** (follow the outline, write in chunks, start with methods/results, don't self-edit). | 🔄 | "Start with Methods/Results" is still right. "Don't worry about perfection" is dangerous for LLMs, because fluent drafts hide gaps. | Draft section by section, results first, with inline claim tags `{C###}` that must resolve. Tags are stripped only at the final edit. |
| O | **Structural revision** ("to see again": clarity, logical flow, audience, completeness). | ✅ | The course correctly separates revision from editing. LLMs tend to collapse the two. | Revision Loop: structural audits (reconstruction, claims, flow, terms, figures, citations, overclaim) run *before* line editing. Line editing is gated. |
| P | **Line-level editing** (grammar, word choice, format, numbers and units). | 🔄 | Still needed, but it comes *last*. Current risk: LLM "polish" adds style markers (S10) and can strengthen claims without anyone noticing (S05). | Final edit runs a **claim-invariance check**: the claim map before and after editing must be identical. |
| Q | **Evidence evaluation** (sufficiency, hard vs soft, balance, framing). | ✅ | Matches the spin literature (S23). | Evidence items carry `strength` (hard/soft), `sufficiency_note`, and `framing_risk`. Claim confidence is derived from these, not asserted. |
| R | **Source reliability** (currency, reputation, refereed status, funding motive, cross-check). | 🔄 | The course heuristics use domain suffixes (.com/.org/.edu), About.com, and print indexes. These are outdated. Modern signals: peer-review status, venue, DOI resolution, retraction status, preprint versioning, conflict-of-interest statements. | `source_registry.json` with a mandatory `publication_status` enum (PEER-REVIEWED, PREPRINT, EDITORIAL, GUIDELINE, TECHNICAL REPORT, BLOG, DOCUMENTATION, COMMENTARY, OPINION) and a `verification` block. |
| S | **Research depth** (surface → trade → specialized literature). | ✅ | Still valid. arXiv is a layer of its own: specialist but unrefereed. | The corpus hierarchy (Levels 0–4) sets how much weight each source gets. Preprints can't be the only support for a literature claim unless they are labeled as preprints. |
| T | **Cross-checking evidence** (seek consensus, no single study). | ✅ | — | Any claim of type `literature` that is load-bearing for the gap needs ≥2 independent sources, or it must be worded as "one study reports". |
| U | **Ethical representation of data** (report unfavorable results, give context). | ✅ | Matches the NeurIPS checklist (S18) and CONSORT-style reporting. | Negative-results inventory is mandatory. A failed experiment that bears on a claim must appear (main text or supplement) or be justified as excluded. `SELECTIVE_REPORTING` flag. |
| V | **Citation and documentation** (APA/IEEE/MLA mechanics, no plagiarism). | 🔄 | Citation style is venue-specific, so it gets injected. The course's style details are dated (APA 6 "et al." rules, MLA "Medium" field). The *principle* now includes **citation correctness** (does the source support the statement? S22) and **existence** (S06, S25, S26). | Citation Audit: existence (DOI/index lookup) → metadata → support (quoted passage) → strength match → primary vs secondary. Unverified citations get `[CITATION NEEDED: …]`, never an invented reference. |
| W | **Avoiding misleading visuals** (truncated axes, cherry-picking). | ✅ | Add: hidden variance, dual axes, 3-D charts (the course praises 3-D bars in one slide and criticizes them in another; current guidance says avoid them), color misuse, and pie charts for small differences. | Visual Honesty checklist inside the Figure/Table Card. |
| X | **Explain according to audience knowledge** (analogies, examples, glossary). | ✅ | Narrative helps non-experts (S29) but also persuades, so analogies must be marked as analogies and must not add claims. | Audience modes A–E. The **content invariance rule**: the claim map is identical across modes. Only the explanation layer changes. |

---

## 3. Obsolete or context-bound assumptions

| Course assumption | Why it no longer holds as stated | Replacement |
|-------------------|----------------------------------|-------------|
| Domain type (.com/.org/.edu/.gov) signals reliability. | Weak signal. Predatory journals, paper mills, and preprint servers all look credible. | Check publication status, venue indexing, DOI resolution, retraction databases, and author conflicts. |
| About.com, print bibliographies, Readers' Guide, CD-ROM databases. | Discontinued or marginal. | Crossref, Semantic Scholar, OpenAlex, PubMed, DBLP, ACL Anthology, IEEE Xplore, ACM DL, arXiv (labeled as preprint). |
| APA "list 3–5 authors on first citation" and MLA "include medium". | These are APA 6 and MLA 7 rules, since superseded. More importantly, citation style belongs to the venue. | Style is supplied by the venue profile. The core skill only enforces *correctness and support*. |
| Results = "no interpretation"; Discussion separate. | True for biomedical IMRaD, false for most CS/ML and physics venues, where results and discussion interleave. | The core rule is that **every result must be interpreted somewhere nearby, with no dangling numbers**. Where the interpretation goes is a venue rule. |
| Methods in passive voice. | Many journals now prefer the active "we". Nature Portfolio says so explicitly (S31). | Voice comes from the venue profile. The core rule is only that the actor must be unambiguous. |
| "Emphasize the positive" and diplomatic softening (Glenn memo). | Right for workplace persuasion, harmful in science. Negative results must not be softened. | Tone rules apply to *interpersonal* framing only. They are never applied to findings. |
| AI should draft the "fluff": abstract, introduction, transitions. | The abstract and introduction are the highest-stakes sections for reader orientation. LLM transitions ("Moreover", "Furthermore") often *assert* logical relations that aren't there. | The AI drafts from a validated spine. Transitions must name a real logical relation (see the coherence rules). |
| Public AI tools "use your prompts for training". | Depends on the tool and contract. The principle (data governance) stands. | An adapter-level `data_policy` setting. Confidential project data only goes to approved endpoints. |
| Paragraph length 75–125 words. | A heuristic, and the course itself says not to let it override purpose. | Only a diagnostic signal. Paragraphs are judged by their *role* in the story graph. |
| Abstract: "no abbreviations, citations, figures"; 150–300 words. | Venue-specific. | Venue profile. |
| Grammarly score targets. | The course already warns "do not chase 100%". The same applies to readability formulas. | Readability metrics are secondary signals and are never optimized directly (see 04). |

---

## 4. Concepts missing from the foundation

These are needed for scientific papers (as opposed to workplace documents) or are specific to
LLM-based writing.

1. **Claim–evidence traceability** as a data structure, not only a moral principle.
2. **Graded claim language.** The course has three certainty levels (conclusive, probable,
   inconclusive). Papers need finer grades: measured, observed, derived, literature-supported,
   interpretation, hypothesis, speculation, future direction. Each grade needs permitted verbs.
3. **Reader-expectation mechanics** (S01): topic position, stress position, old→new information
   flow, and keeping subject and verb close together. These explain *why* correct text is hard
   to read.
4. **Research-story structure** (S02, S03): context → content → conclusion at every scale, and
   OCAR. The course has IMRaD (sections) and the thesis statement (one sentence). It has nothing
   in between: no structure that links sections into one argument.
5. **Experimental design narrative.** Why this experiment answers this question, and what
   result would have counted against the hypothesis.
6. **Statistical reporting norms** (S18): effect sizes, uncertainty intervals, what the error
   bars capture, number of runs and seeds, multiple comparisons, and baselines tuned as
   carefully as the proposed method.
7. **Reproducibility and open science** (S18, S19): code and data availability, preregistration
   where relevant, domain reporting guidelines (EQUATOR family), and AI-use disclosure (S14–S17).
8. **Spin and overclaiming** as a named, detectable category (S23, S30), and LLM generalization
   bias (S05).
9. **Citation *correctness*** (S22), separate from citation *presence* and citation *format*.
10. **Cognitive-load management.** Concept introduction order, a limit on new terms per
    paragraph, and forward references.
11. **Evaluation by reconstruction.** Success is measured by whether the reader's mental model
    matches the research, not by how the prose sounds.
12. **Adversarial robustness of LLM evaluation** (S21). Text passed to an evaluator is data and
    may contain injected instructions. Evaluators are also biased by disclosed limitations.
13. **Accessibility.** Color-vision-safe palettes, alt text, and font sizes readable at print
    scale.
14. **Negative-results handling and selective-reporting detection.**

---

## 5. Diagnosis: why LLM-generated papers "dump information"

Combining the course principles with the LLM literature gives a causal account. Each cause has
a matching countermeasure in the architecture.

| Symptom (from the brief) | Root cause | Countermeasure |
|--------------------------|------------|----------------|
| Motivation unclear; research question appears late | The model drafts section by section from a template, so no global argument exists *before* the prose. | Paper Spine + Story Graph built before drafting (course principle M). |
| Contribution buried | Contributions get listed as features, not as answers to the gap. | Contribution nodes must have an edge from the GAP node and from a RESULT node. |
| Terms used before explained | The writer (model) knows the project from its notes, a "curse of knowledge" with perfect recall. | Term Ledger with first-use and definition locations, plus a lint check. |
| Experiments disconnected | Experiments are copied from logs in chronological order, not ordered by the question each one answers. | Experiment Narrative Chains: each experiment must hang off a research question or hypothesis. |
| Results listed, not interpreted | The model can read numbers but not their significance to the argument. | Result Interpretation Chain, required for every major result. |
| Tables without purpose | The "papers have tables" template prior. | Figure/Table Card with a takeaway sentence written *before* the figure exists. |
| Discussion disconnected from the question | Nothing forces the answer back to the question. | Discussion contract: each research question node must receive an answer node. |
| Limitations disconnected from claims | Limitations get written as a generic list. | Each limitation must attach to specific claims (an edge in the claim graph). |
| Conclusion repeats | Summarizing is the default operation. | Conclusion contract: synthesize (what changes in understanding), don't repeat. Overlap with the abstract is measured. |
| Assumes reader knows the project | Private context leaks into the prose. | Blind reviewer sees only the paper. Reconstruction errors expose the leakage. |
| Dense, not clear | Fluency gets optimized, not orientation. | Audience modes, density classes, cognitive-load audit. |
| Stronger claims than the evidence | Generalization bias (S05), plus "polish" editing. | Claim strength ladder, claim-invariance check across edits, overclaim audit. |
| Fabricated or misattributed citations | Generating from memory (S06, S25, S26). | Retrieval-only citations, existence and support verification, `UNVERIFIED_CITATION` state. |

---

## 6. Proposed architecture (summary; full detail in 03 and 05)

```
                    ┌──────────────────────────────────────────────┐
 PROJECT FOLDER ──► │ WRITING WORKFLOW (the skill; run by any LLM) │ ──► PAPER + AUDIT TRAIL
                    │  Plan → Draft → Revise → Edit  (from the course)
                    │  artifacts: evidence map, claim graph, story graph,
                    │  audience profile, venue profile, architecture, skeleton
                    └──────┬─────────────────────────────▲─────────┘
                           │ uses                         │ versioned rules
          ┌────────────────▼───────┐  ┌────────────────┐  │
          │ CORPUS_AGENT           │  │ REVIEW_AGENT   │  │
          │ evidence + exemplars   │  │ blind reader   │  │
          └────────────┬───────────┘  └──────┬─────────┘  │
                       │ structured knowledge │ diagnostics│
                       └──────────┬───────────┘            │
                           ┌──────▼────────┐               │
                           │ SKILL_AGENT   │───────────────┘
                           │ optimizer     │  (changes rules, never papers)
                           └───────────────┘
```

Two loops run on this structure:

- **Inner loop (per paper).** The workflow drafts. REVIEW_AGENT evaluates blind. The workflow
  revises. This improves *one paper*.
- **Outer loop (per skill version).** SKILL_AGENT turns aggregated diagnostics into rule
  changes. The changes are tested against a frozen benchmark and versioned. This improves *the
  skill*.

**Design invariants**

1. **Evidence before prose.** No sentence may carry a claim that is missing from the claim map.
2. **Structure before style.** Line editing is gated behind the structural audits.
3. **Reasoning is invariant; voice is free.** The story and claim graphs are fixed across
   audience modes and venues. Surface form is not.
4. **Missing means marked.** Gaps become failure states, never invented content.
5. **Evaluation is blind and structured.** Only diagnostics cross agent boundaries.
6. **The skill changes only through versioned, tested amendments.**
