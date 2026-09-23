# Information Design

Paragraph engineering, information density, cognitive load, and coherence. These are
*diagnostic tools*, not molds. Don't force every paragraph into five sentences.

---

## 1. The paragraph model

Every paragraph should let the reader answer five questions:

| # | Reader question | Where it's usually answered |
|---|-----------------|------------------------------|
| 1 | Why am I reading this? | Opening clause: links to the previous point or to the section's question |
| 2 | What is the main point? | Topic sentence, first or second sentence ("bottom line on top", F0 Unit 3) |
| 3 | What evidence supports it? | Middle: data, citation, derivation, example |
| 4 | How does it connect to the previous point? | Opening + explicit relation word *that is true* |
| 5 | Why does it matter for the next point? | Closing sentence, often in stress position (S01) |

A useful default internal order is **CLAIM → CONTEXT → EVIDENCE → EXPLANATION → CONNECTION**.
Other orders are fine when they serve the reader (e.g. CONTEXT first in the introduction's
opening paragraph).

### Paragraph diagnostic (used in step 13)
For each paragraph, record: `role` (story node), `point` (one sentence), `evidence` (claim or
evidence IDs, or "none needed: transitional"), `link_back`, `link_forward`.

Fails when:
- `point` needs two sentences joined by "and also" → two paragraphs
- `evidence` is "none" but the point is a claim → an orphan claim
- `link_back` is empty and the paragraph is not a section opening → missing transition
- the point appears only in the last sentence (buried lede), unless the paragraph is a
  deliberate build-up in a narrative introduction
- it contains >2 new terms (mode B–E) → load problem

### Transitional paragraphs (F0 Unit 3)
Short paragraphs that close one point and open the next are legitimate. Use them at section
boundaries and between experiments (the `NEXT` field of the experiment chain).

---

## 2. Information density classes

For each unit of content (sentence, detail, table row), ask **"What does the reader need
here?"**

| Class | Definition | Placement |
|-------|-----------|-----------|
| CORE | The argument fails without it at this point | Main text, here |
| SUPPORTING | Strengthens or clarifies CORE for the binding personas | Main text, or a figure/table |
| OPTIONAL | Useful to some readers; not needed to follow the argument | Footnote, table note, or appendix |
| SUPPLEMENTARY | Needed for reproducibility or verification, not for understanding | Appendix/supplement, with a pointer in the main text |
| DISTRACTING | Neither aids understanding nor verification (project history, tool trivia, abandoned ideas that bear on no claim) | Remove |

**Relocation, not deletion:** reproducibility detail is never deleted to shorten the paper. It
moves to SUPPLEMENTARY with a pointer ("full hyperparameters in Appendix B"). Negative results
bearing on claims are never DISTRACTING.

Typical classifications:
- Hyperparameter grids → SUPPLEMENTARY (the chosen values and the selection procedure are CORE
  in Methods).
- Hardware and runtime → SUPPLEMENTARY unless efficiency is a claim (then CORE).
- The chronology of how the idea evolved → DISTRACTING, unless it explains a design choice
  (then SUPPORTING, one sentence).
- Every metric for every baseline → a table (SUPPORTING). The prose carries only the
  comparisons that answer an RQ.

---

## 3. Cognitive load

The reader has limited working memory. Load comes from new concepts, long dependency chains,
unresolved questions, and notation.

Controls:
- **Concept order.** Introduce concepts in dependency order (`requires` edges in the story
  graph). No forward use of undefined concepts.
- **New-concept rate.** See the term budget (`audience_model.md` §5).
- **Sentence shape.** Keep subject and verb close together; put the action in the verb (not
  "performed an optimization of" but "optimized"). One idea per sentence where the ideas are
  complex (S01).
- **Numbers.** In prose, give the one or two numbers that make the point, plus a comparator
  ("12% lower than B"). Leave the rest to tables.
- **Notation.** Words first, then symbols. Avoid defining a symbol used only once.
- **Signposting.** Section openings state the section's question. Long sections get a one-line
  roadmap.
- **Parallel structure.** Parallel ideas take parallel grammatical form (F0 Unit 3), e.g. the
  contributions list.

---

## 4. Coherence: old → new information (S01 + F0 Unit 3)

- **Topic position** (sentence start) holds *old* information: something the reader just saw.
  This is the link back.
- **Stress position** (sentence end) holds *new or important* information. Readers weight the
  end of a sentence.
- The next sentence usually picks up the previous sentence's stress-position concept in its
  topic position. That chain is what makes text feel connected.
- **Repeat key nouns** instead of drifting to synonyms (term ledger).
- **Demonstrative + noun**: "this reduction", not a bare "this" (F0 Unit 3).
- **Transitions must be true.** "However" needs a contrast. "Therefore" needs an inference that
  actually holds. "Moreover" needs a real addition in the same line of argument. LLM drafts
  often use connectives decoratively. Every connective is checked in step 13, and false ones are
  deleted rather than swapped for another.

---

## 5. Lists, headings, and navigation (F0 Unit 3, modernized)

- Headings **inform** (e.g. "4.2 Shift in covariates explains most of the error increase"),
  where the venue allows. Otherwise they are at least specific ("4.2 Error under covariate
  shift"). Avoid "Results 2".
- Every list has a lead-in that states what the list is and, where useful, how many items it
  has.
- Use numbered lists only for sequences or referenced items (e.g. contributions C1–C3 referenced
  later).
- In the introduction's paper map, each section is described by the question it answers, not
  only by its title.
