# 02 — Research-Corpus Strategy

The corpus is **not training data**. It is a structured, provenance-tracked knowledge base that
the skill *consults*. It answers three different questions, and they must never be mixed up:

| Question | Answered by | Authority |
|----------|-------------|-----------|
| *What actually happened in this research?* | Level 0 (the user's project) | **Ground truth.** Nothing overrides it. |
| *What does this venue require?* | Level 1 (target venue) | Binding for format. Not binding on scientific content. |
| *What does clear communication look like here, and what makes readers get lost?* | Levels 2–4 (exemplars and anti-exemplars) | Advisory. Only **patterns** are extracted, never prose. |

External exemplars can never supply facts about the user's research. The only thing that may
flow from Levels 2–4 into a draft is a *structural or rhetorical pattern*.

---

## 1. Source hierarchy

### Level 0 — User's project evidence (highest priority)

Examples: results files (CSV/JSON/logs), benchmark tables, figure sources, notebooks, configs,
code, lab notes, README/MD files, problem statements, prior drafts, reviewer comments,
accepted/rejected versions, and failed-experiment notes.

Rules:
- Every Level-0 item gets a stable ID (`E###`) and a **locator** (file path plus line, cell,
  row, or key).
- Numbers are copied **verbatim with units and provenance**. They are never re-typed from
  memory.
- When two files disagree, record `CONFLICTING_EVIDENCE` and quote both. Never pick one silently.
- Previous drafts and reviewer feedback are **Level 0 for communication history**, not for
  scientific facts. A number that appears only in a draft is `UNSUPPORTED` until it is traced
  to data.
- Reviewer feedback is split into (a) scientific concerns, which go to the claim map, and (b)
  communication concerns, which go to diagnostics.

### Level 1 — Target venue

Collect: author guidelines, templates, page limits, required statements (data/code
availability, AI use, ethics, limitations), reviewer forms and checklists (e.g. S18), domain
reporting guidelines (EQUATOR family, e.g. S19), and 5–15 recent papers from the venue on
similar questions or methods.

Rules:
- All venue rules go into `venue_profile.yaml`. The core skill reads the profile and never
  hard-codes a venue.
- Every rule records the URL and retrieval date. If no official source is found, the rule is
  `assumed: true`, which triggers `VENUE_UNKNOWN` handling (see failure states).

### Level 2 — Domain exemplars

Strong recent papers from the same research domain.

Selection priority (all must hold):
1. Peer-reviewed at a recognized venue. Preprints are allowed only if flagged, and never make
   up more than 30% of the exemplar set.
2. Methodological transparency: code or data available, or a reporting checklist completed.
3. **Judged by a communication rubric, not by citations.** Citation count is recorded as
   metadata but is never a selection criterion (citations measure attention, not clarity; cf.
   S12, where the jargon effect is itself confounded with citations).
4. Diversity: at least 3 different author groups, so no single house style dominates.

### Level 3 — Communication exemplars (section-level)

Excerpts chosen because one *section* handles a specific job well: an abstract that states
the gap in one sentence, a figure caption that states the takeaway, a limitations paragraph
tied to specific claims, a related-work section organized by method families, a discussion
that returns to the research questions. They can come from any field, since good structure
transfers. Sources also include editorial guidance (S02, S03, S24, S31).

### Level 4 — Negative examples (anti-patterns)

What makes readers get lost. The main sources:
- **Deliberately degraded versions** of good text (controlled perturbations; see 04). These are
  the safest negatives: the content is fixed, so the defect is isolated.
- Documented patterns from the literature: S04 (troubling trends), S23 (spin taxonomy), S05
  (LLM over-generalization), S10 (LLM style markers), S11–S13 and S27 (jargon and readability),
  S22 (citation misattribution).
- **Earlier AI-generated drafts from the user's own projects.** This is the most relevant
  negative data there is, because it shows how *this* pipeline fails.
- Public peer reviews that name communication failures, e.g. OpenReview reviews saying
  "contribution unclear" or "results not interpreted". Quote only minimal spans and record the
  URL.

**Ethics for negative examples.** Never publish a named paper as a "bad example". Store
negative patterns as *abstracted descriptions* with private provenance. Prefer synthetic or
self-authored degradations for anything that ships with the skill.

---

## 2. Discovery protocol

```
1. SCOPE     → from the Level-0 story graph, derive the query facets:
               {problem terms, method family, dataset/benchmark names, evaluation metrics,
                venue, time window (default: last 5 years + seminal works)}
2. SEARCH    → run every facet combination on ≥2 indexes. Primary ones:
               Crossref, OpenAlex, Semantic Scholar (general); PubMed (biomed);
               DBLP, ACL Anthology, ACM DL, IEEE Xplore (CS/EE); arXiv (preprints, flagged);
               venue proceedings pages (Level 1).
               Log each query: string, index, date, hit count.
3. SCREEN    → title/abstract screening against the inclusion criteria (§3). Record the
               reason for each exclusion. (This is PRISMA-style screening, simplified.)
4. VERIFY    → resolve DOI or arXiv ID; confirm title, authors, year, venue; check
               retraction status (Retraction Watch / Crossref) when available;
               set publication_status.
5. READ      → full text where possible. Abstract-only sources get
               `read_depth: abstract` and cannot support method or result claims.
6. EXTRACT   → fill the extraction schema (§4). Patterns, not prose.
7. SNOWBALL  → one level of backward and forward citation chasing from the top items.
8. SATURATE  → stop when two consecutive batches add no new method family or gap dimension,
               or when the budget is reached. Record the stopping reason.
```

**Search-scope honesty.** The literature review may only claim what the search supports. "We
found no prior work that X" must be written as "Among the N works retrieved from [indexes] up
to [date], none reported X" unless an exhaustive systematic review was done. This rule directly
blocks the "first-ever" overclaim.

---

## 3. Quality filters

| Filter | Pass condition | If it fails |
|--------|----------------|-------------|
| Existence | DOI/arXiv/URL resolves and the metadata matches | Discard. Log as possible hallucination if it came from a model. |
| Publication status | Classified into the 9-way enum | Classification required before use |
| Relevance | Matches ≥1 story-graph node (problem, method, dataset, metric) | Exclude |
| Recency | Within the window, or marked `seminal` with a reason | Exclude unless seminal |
| Read depth | Full text for any method or result claim | Downgrade the permitted use |
| Independence | For consensus claims, ≥2 independent author groups | Reword as "one study reports" |
| Integrity | Not retracted; no expression of concern | Exclude, or cite *as* retracted if relevant |
| Conflict of interest | Funding and affiliation noted when disclosed | Record; weigh (the course's "funding motive" rule) |
| Communication quality (Levels 2–3 only) | Scores ≥4 on the relevant exemplar rubric items (§5) | Not used as an exemplar. May still be cited for content. |

---

## 4. Extraction schema

Full JSON Schemas are in `skill/schemas/`. The fields below are the conceptual core.

### 4.1 Source record (`source_registry.json`)

```yaml
id: SRC-017
title: …
authors: [ … ]
year: 2024
venue: …
doi: 10.xxxx/…          # null if none. NEVER invented.
url: …
publication_status: PEER-REVIEWED | PREPRINT | EDITORIAL | GUIDELINE | TECHNICAL_REPORT |
                    BLOG | DOCUMENTATION | COMMENTARY | OPINION
peer_review_known: true | false
domain: …
paper_type: empirical | method | theory | survey | benchmark | position | replication
level: 1 | 2 | 3 | 4
verification: {method: doi_lookup|index_lookup|publisher_page|manual, date: YYYY-MM-DD,
               verified_by: agent|human, retraction_checked: bool}
read_depth: full | partial | abstract
why_useful: …
demonstrates: [ writing behaviors, e.g. "gap stated as measurable deficiency" ]
informs_sections: [ introduction, results, … ]
evidence_quality: high | medium | low
limitations: …
permitted_use: [ content_citation, pattern_exemplar, negative_pattern ]
```

### 4.2 Writing pattern (`writing_patterns.json`)

This is extracted per exemplar and per section. No sentences are copied. A pattern is a
*sequence of rhetorical moves*.

```yaml
id: PAT-031
source: SRC-017           # provenance (hidden from REVIEW_AGENT)
section: introduction
rhetorical_purpose: "establish the gap as a measurable deficiency of existing methods"
move_sequence: [CONTEXT, PROBLEM, EXISTING_APPROACHES, SPECIFIC_DEFICIENCY_WITH_NUMBER,
                QUESTION, APPROACH_ONE_SENTENCE, CONTRIBUTIONS_LIST, PAPER_MAP]
reader_question_answered: "Why can't existing methods already do this?"
assumed_knowledge: adjacent-researcher
transition_behavior: "each paragraph opens with the previous paragraph's stress-position concept"
evidence_placement: "the deficiency is supported by a citation plus one number in the same sentence"
result_interpretation_pattern: null
figure_table_integration: "Fig. 1 previews the gap visually before the related work"
limitation_framing: null
contribution_framing: "contributions phrased as answers to the gap, each with a forward pointer"
length_profile: {paragraphs: 5, avg_sentences: 4}
paraphrase_only: true     # quotes forbidden unless explicitly permitted
```

### 4.3 Anti-pattern (`anti_patterns.json`)

```yaml
id: ANT-008
name: result_dumping
signature: "≥3 consecutive sentences reporting numbers with no interpretive clause"
detection: {automatic: "regex+heuristic in tools/lint_draft.py", manual: "RIC check"}
reader_effect: "reader cannot tell which result answers which question"
consequence: "contribution misremembered; reconstruction Q7/Q8 fail"
source_kind: synthetic_degradation | literature | prior_ai_draft | public_review
provenance: private
repair_principle: "apply the Result Interpretation Chain; one result, one paragraph"
```

### 4.4 Level-0 evidence item, claim, and story node

See `skill/evidence_model.md` and `skill/research_story.md`.

---

## 5. Exemplar communication rubric (Levels 2–3)

A candidate exemplar is scored 0–5 on the items relevant to its section. It qualifies at ≥4.
Two independent scorings are required (two model runs with different seeds or models, or one
human plus one model). Disagreements ≥2 points go to a human.

1. The research question is recoverable from the first page.
2. The gap is stated as a specific deficiency, not as "little work exists".
3. Each contribution maps to evidence in the paper.
4. Terms are defined before, or at, first use.
5. Each major result has an interpretation and a link to the research question.
6. Figures and tables have takeaway captions.
7. Limitations are tied to specific claims.
8. The discussion returns to the research question.
9. Claim language matches the evidence strength.
10. The paper can be understood without reading the appendix.

---

## 6. Positive and negative example sets (to build per domain)

| Set | Size target | Content | Use |
|-----|-------------|---------|-----|
| `pos/intro` | 8–12 | Introductions scoring ≥4 on items 1–3 | Move sequences for introductions |
| `pos/results` | 8–12 | Results sections with full interpretation chains | RIC calibration |
| `pos/captions` | 20+ | Takeaway-first captions | Caption rules |
| `pos/limitations` | 8+ | Claim-tied limitation paragraphs | Limitation framing |
| `pos/related` | 6+ | Dimension-organized related work | Literature → gap chain |
| `neg/synthetic` | 5 variants × each base text | Controlled degradations (04 §6) | Reviewer calibration and skill tests |
| `neg/prior_ai` | all available | The user's earlier LLM drafts plus their reviews | Project-specific failure modes |
| `neg/literature` | abstracted | Patterns from S04, S05, S22, S23 | Anti-pattern catalog |

The skill ships only with **synthetic** examples (`skill/tests/perturbations/`). Domain sets
are built per project by CORPUS_AGENT and stay in the project's `.rcs/corpus/` directory.

---

## 7. Evaluation datasets

1. **Perturbation benchmark.** Base texts × controlled variants (clear / poor ordering /
   jargon / result dumping / unsupported interpretation / buried contribution / citation
   misuse). Ground truth is known by construction. Used to *calibrate the reviewer* before the
   reviewer is used to *evaluate the skill*.
2. **Project benchmark.** For each real project: the Level-0 evidence, a gold **reference
   story** (research question, key claims, their evidence, limitations) written or approved by
   the researcher, a baseline LLM paper, and a skill-generated paper. The gold story is the
   target that reconstruction answers are scored against.
3. **Human-draft set.** Human-written drafts of the same projects, where available, as a
   non-LLM reference.
4. **Held-out set.** ≥30% of projects and perturbation bases that SKILL_AGENT never sees
   diagnostics from. Used only for release gating.

---

## 8. Research sources for the design itself

The design choices trace to these groups (full list in [SOURCES.md](SOURCES.md)):

- **Reader cognition and structure:** S01, S02, S03, S29, S31.
- **Jargon and readability:** S11, S12, S13, S27.
- **Reporting integrity and spin:** S18, S19, S22, S23, S30, S04.
- **Figures:** S24.
- **LLM scientific writing failure modes:** S05 (generalization), S06/S25/S26 (citations),
  S10 (style markers), S08/S09/S28 (auto-research systems), S21 (evaluator manipulation), S07
  (usefulness and limits of LLM feedback), S20 (blind-evaluation design).
- **Publication policy on AI use:** S14–S17.

Not every relevant paper was verified in this phase. When the skill runs on a project,
CORPUS_AGENT extends the list with verification records. The design documents cite only what
is in SOURCES.md.
