# Research Story

A paper is not a collection of sections. It is a **connected reasoning structure** that the
sections carry. This file defines that structure and the ledgers that keep the reader inside it.

---

## 1. The Paper Spine (`story/spine.md`)

Seven lines. Each is ≤2 sentences in plain words, readable by the paper's primary audience, and
each carries claim tags.

| Line | Answers | Example shape (fill from evidence; don't copy wording) |
|------|---------|----------------------------------------------------------|
| 1 Problem | What is hard or unknown, and for whom? | "Practitioners who need X cannot currently Y because Z." |
| 2 Gap | What exactly do existing approaches fail to do? | "Existing methods of kind K assume A, which fails when B {C002}." |
| 3 Question | What does this paper ask? | "Can a method that relaxes A match K on standard data and outperform it under B?" |
| 4 Approach | What did we do, in one idea? | "We replace A with …, and test it on …" |
| 5 Key finding | The single most important result, with its size | "Under B, error fell by 12% {C007}; on standard data it matched K within noise {C008}." |
| 6 Meaning | What changes in understanding or practice | "This suggests A, not model capacity, drives the failure under B {C011}." |
| 7 Main limit | The most important boundary on 5–6 | "Tested on two datasets at one scale; causal role of A inferred, not isolated {L002}." |

**Spine tests** (all must pass before G1):
- *Tell-a-colleague test:* read lines 1–7 aloud. Would an adjacent researcher know what you did
  and why it matters?
- *Chain test:* each line follows from the previous one. Gap → Question: does answering the
  question close the gap? Finding → Meaning: does the meaning follow from the finding, or does
  it need extra evidence?
- *Honesty test:* line 7 limits line 5 or 6 specifically. It is not generic.
- *One-contribution test:* line 5 names one central finding. If there are three co-equal
  findings, choose which one organizes the paper. The others become supporting results (S02:
  one central contribution per paper).

The spine is the paper's **one-day memory** (Q12). The abstract, the last paragraph of the
introduction, and the conclusion are each derived from it.

---

## 2. The Research Story Graph (`story/story_graph.json`)

### Node types
`PROBLEM · SIGNIFICANCE · KNOWN · GAP · RQ · HYPOTHESIS · OBJECTIVE · APPROACH · DESIGN ·
OBSERVATION · RESULT · INTERPRETATION · CONTRIBUTION · LIMITATION · IMPLICATION · FUTURE ·
BACKGROUND_CONCEPT`

(`BACKGROUND_CONCEPT` holds definitions and concepts the reader must have. Each one is attached
to the first node that needs it.)

### Node fields
`id`, `type`, `text` (one sentence), `claims` [C…], `evidence` [E…] (for RESULT/OBSERVATION),
`sources` [SRC…] (for KNOWN/GAP), `audience_note` (what the reader must know first).

### Edge types
| Edge | From → To | Meaning |
|------|-----------|---------|
| `motivates` | PROBLEM/SIGNIFICANCE → RQ | why the question is worth asking |
| `establishes` | KNOWN → GAP | the literature that locates the gap |
| `addresses` | RQ → GAP | the question targets this gap |
| `operationalizes` | HYPOTHESIS/OBJECTIVE → RQ | the testable form |
| `implements` | APPROACH → HYPOTHESIS/OBJECTIVE | |
| `tests` | DESIGN → HYPOTHESIS | the experiment that could falsify it |
| `produces` | DESIGN → OBSERVATION/RESULT | |
| `supports` / `contradicts` | RESULT → INTERPRETATION | |
| `answers` | INTERPRETATION → RQ | |
| `grounds` | RESULT → CONTRIBUTION; GAP → CONTRIBUTION | the contribution closes the gap with evidence |
| `limits` | LIMITATION → RESULT/INTERPRETATION/CONTRIBUTION | |
| `implies` | INTERPRETATION → IMPLICATION | |
| `opens` | LIMITATION/IMPLICATION → FUTURE | |
| `requires` | any → BACKGROUND_CONCEPT | concept order |

### Graph validity (checked by `tools/validate_artifacts.py`)
1. Every `RQ` has ≥1 incoming `addresses`, and ≥1 `answers` from an INTERPRETATION.
2. Every `CONTRIBUTION` has `grounds` from ≥1 RESULT **and** ≥1 GAP.
3. Every `LIMITATION` has ≥1 outgoing `limits`.
4. Every `DESIGN` has `tests` or `produces`.
5. Every `RESULT` has evidence IDs.
6. No `INTERPRETATION` is grounded only in SPECULATION-typed claims unless it is typed as
   speculation.
7. There is a path PROBLEM → … → CONTRIBUTION.

### Paragraph mapping
In `paper_architecture.md`, each paragraph slot lists ≥1 node ID. A paragraph that maps to no
node must be (a) removed, (b) moved to where its node lives, or (c) justified in writing (e.g.
a venue-required statement).

---

## 3. Experiment Narrative Chains

Experiments are presented in the order of the **questions** they answer, never in the order
they were run (unless that order *is* the logic, e.g. iterative design).

For each experiment `X`:

```
RQ        : which question (RQ id)
HYPOTHESIS: what we expected, and what result would count AGAINST it (falsifier)
DESIGN    : minimal description: data, conditions, comparison, metric, n/seeds
            + WHY this design tests the hypothesis (design rationale, Q5)
OBSERVATION: what happened (E ids)
INTERPRETATION: what it means for the hypothesis (C ids), and alternatives considered
CLAIM     : the claim it licenses, at which strength
LIMITATION: what this experiment cannot show (L ids)
NEXT      : why the next experiment follows (the reader's next question)
```

The `NEXT` field is what turns a list of experiments into a narrative. Typical links:
"establishes the effect → rules out the obvious confound → locates the mechanism (ablation) →
tests the boundary (generalization/stress)". If an experiment's `NEXT` is empty, and it is
neither the last one nor a stand-alone RQ, the order is wrong or the experiment is an orphan.

---

## 4. The Question Ledger (`story/question_ledger.json`)

Readers carry questions. Text that raises a question and doesn't answer it (or at least say
when it will) causes the "lost" feeling.

Entry: `{id, question, raised_at (slot), answered_at (slot) | deferred_to (slot + pointer text),
reader_personas}`.

Sources of reader questions (from the course's anticipate-the-reader principle):
- A new term → "what is it?"
- A claim → "how do you know?"
- A number → "is that good? compared to what?"
- A design choice → "why this and not the obvious alternative?"
- A result → "so what? does it answer the question?"
- A limitation → "does it undermine the main claim?"

**Rules:** debt must be 0 at the end of each section, except deliberate forward deferrals with
an explicit pointer ("we return to this in §5.2"). The introduction may defer at most 3
questions beyond the paper map.

---

## 5. The Term Ledger (`story/term_ledger.json`)

Entry: `{term, kind: acronym|technical|project_specific|notation, definition, defined_at,
first_used_at, uses, audience_modes_requiring_definition, synonyms_forbidden: [...]}`.

**Rules**
- `defined_at` ≤ `first_used_at` for every mode that requires a definition.
- **One term per concept.** Once "adapter" is registered, don't write "module", "plug-in", or
  "component" for the same thing (F0 Unit 3: don't vary key terms).
- Acronyms: introduce one only if it's used ≥3 times after its definition. Otherwise spell it
  out. Well-known field acronyms (e.g. "CNN" for mode A) still go in the ledger, marked
  `known_to: [A]`.
- Project-specific names (internal code names, variable names) never appear in prose unless
  they are defined. Most should be replaced with descriptive names.
- Notation: every symbol is defined at first use and appears in a notation table if there are
  more than ~10 symbols.

---

## 6. Story patterns (reasoning orders the skill may choose)

The graph is invariant. The **presentation order** is chosen from these patterns according to
the paper type and venue. Pick one and record it in the architecture.

| Pattern | Order | Use when |
|---------|-------|----------|
| Classic IMRaD | Context → Gap → Q → Methods → Results → Discussion | single hypothesis, empirical |
| Question-led | Q1 → exp → answer → Q2 → exp → answer … → synthesis | several linked RQs (common in CS/ML) |
| Method-first | Problem → Method → Properties/theory → Experiments | new method or system |
| Finding-first | Surprising observation → explanation attempts → tests | observational or exploratory |
| OCAR (S03) | Opening → Challenge → Action → Resolution | a general narrative scaffold; fits all of the above |

Whatever the order, the **context → content → conclusion** unit (S02) applies at every scale:
paper, section, and paragraph.
