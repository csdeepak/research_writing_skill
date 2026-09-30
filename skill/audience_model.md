# Audience Model

The course's three-tier audience model (F0 Unit 1) is adapted to research papers and combined
with five reader modes. **Science stays invariant; explanation adapts.**

---

## 1. Tiers (who reads which layer)

| Tier (course) | In a research paper | Layer that must serve them |
|---------------|--------------------|-----------------------------|
| Primary: acts on the document | The target research community reading to learn, use, or build on the result | Title, abstract, introduction, figures + captions, discussion. **The first read (§4).** |
| Secondary: evaluates for accuracy | Reviewers, replicators, and methodologists checking claims | Methods, experimental setup, statistics, supplement, code/data availability |
| Tertiary: later reference | Future readers, adjacent fields, meta-analysts, practitioners, students | Keywords, definitions, limitations, data/code links, a self-contained abstract, the notation table |

A paper fails its secondary tier if claims can't be verified. It fails its tertiary tier if
the abstract and limitations don't stand alone.

---

## 2. Reader modes

| Mode | Reader | Assumes | Needs |
|------|--------|---------|-------|
| **A** Specialist | Works in this subfield | Field vocabulary, standard methods, benchmark conventions | Precise delta vs prior work; full rigor; project-specific terms still defined |
| **B** Adjacent researcher | Same broad field, different subfield | General field vocabulary; not subfield terms | Subfield terms defined; why the gap exists; intuition for the method |
| **C** Technical generalist | Quantitatively trained, different field | General science and statistics | Plain-language problem; concepts before notation; one worked example |
| **D** Educated non-specialist | Science-literate public, policy, press | Everyday language | Plain summary; significance and uncertainty stated explicitly; no unexplained numbers |
| **E** Mixed | Venue with A–D readers (e.g. broad journals) | — | Layered: every section opens accessible (C level), then deepens to A level; glossary; plain-language summary if the venue allows |

Default binding personas for evaluation: A→{A,E}; B→{A,B,E}; C→{B,C,E}; D→{C,D}; E→{A,B,C,E}
(+D if the venue requires lay summaries).

---

## 3. What may change between modes (and what may not)

| May change | May NOT change |
|------------|----------------|
| Depth of background (which BACKGROUND_CONCEPT nodes are shown) | Any claim statement, type, scope, or confidence |
| Terminology (spelled out vs term of art), with the ledger updated | Which results are reported, including negative ones |
| Ordering of explanation (intuition before formalism) | Limitations that bear on claims |
| Examples and analogies (marked as analogies; they add no claims) | Numbers, units, uncertainty |
| Where detail lives (main text vs supplement) | Citations supporting claims |

**Content-invariance check:** after producing a mode-adapted version, re-extract the claims and
diff them against the claim map. Any difference fails the check.

**Analogy rule:** an analogy must be labeled ("as an analogy, …"), must be correct for the
property it illustrates, and must be followed by the precise statement. Narrative helps
non-experts (S29), but it also persuades, so analogies can't carry evidential weight.

---

## 4. The first read

A reasonably informed reader of the target mode should get these from **title + abstract +
introduction + figure captions alone**: the problem, why it matters, what is new, how it was
tested, what was found, and why that matters.

Operational checks:
- Q1, Q2, Q3, Q4, Q10, and Q12 of the reconstruction test are answerable from the first-read
  subset (the step 11 self-test runs on this subset first).
- The introduction contains no implementation detail that isn't needed to understand the
  contribution (density class CORE only).
- Figure 1 (if it exists) is understandable from its caption and conveys either the problem,
  the approach, or the key result.

---

## 5. Term budget

A soft limit on *new* technical terms (excluding those known to the mode):

| Mode | New terms per paragraph | Acronyms in abstract |
|------|------------------------|----------------------|
| A | ≤3 (project-specific terms only) | ≤2, all defined |
| B | ≤2 | ≤1 |
| C | ≤1–2, each with a plain gloss | 0 |
| D | ≤1, with a plain gloss and example | 0 |
| E | as C in section openings; as A deeper in | 0–1 |

This is a diagnostic threshold, not a quota. Exceeding it triggers a review in step 14.
Evidence behind it: jargon lowers processing fluency and acceptance (S13), correlates with
lower citation (S12), and acronym density in ML has grown sharply (S27).

---

## 6. `audience_profile.json`

```json
{
  "mode": "B",
  "primary": "ML researchers working on robustness who are not specialists in time-series",
  "secondary": "reviewers at venue V; replicators",
  "tertiary": "practitioners deploying forecasting models",
  "assumed_known": ["supervised learning", "train/test split", "MAE"],
  "not_assumed": ["distribution shift taxonomy", "the specific benchmark suite"],
  "binding_personas": ["A", "B", "E"],
  "term_budget": {"per_paragraph": 2, "abstract_acronyms": 1},
  "source": "user-specified 2026-09-24"
}
```

---

## Reader knowledge model (v0.3 Stage 3, M02)

Personas A–E become checkable in `.rcs/plan/reader_model.json` (schema
`schemas/reader_model.schema.json`, template `templates/reader_model.json`):

- `known_terms`: what this reader already knows. An expert in one field is **not** assumed to
  know an adjacent field's jargon: list what they know, and everything else must be explained.
- `prerequisite_concepts`: `{concept, needs[]}`. The paper must introduce `needs` before
  `concept`.
- `likely_misconceptions`: `{misconception, trigger_terms, corrective_point, corrective_terms}`.
  If a trigger appears, the corrective point must appear too.
- `reader_questions`: what this reader will ask; each must be answered somewhere.
- `new_term_budget`: new terms per paragraph (default 2 for modes B–E).

`tools/audit_reader.py` checks the draft against it (and flags excess precision and term-ledger
synonym drift even without a reader model). Findings are flags. Fix them by explaining or
reordering, never by changing a claim.
