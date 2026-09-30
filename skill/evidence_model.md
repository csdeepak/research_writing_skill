# Evidence Model

Evidence is what happened. Claims are what we say about it. They are separate objects, joined
by explicit links. Schemas: `schemas/research_evidence.schema.json`,
`schemas/claim_evidence_map.schema.json`.

---

## 1. Evidence items (`E###`)

| Field | Meaning |
|-------|---------|
| `id` | `E` + 3+ digits, stable across runs |
| `kind` | `result` · `experiment` · `dataset` · `baseline` · `metric` · `observation` · `negative_result` · `limitation_noted` · `rationale_stated` · `assumption` · `hypothesis_stated` · `method_detail` · `implementation_detail` · `external_fact` |
| `summary` | One neutral sentence. No adjectives of quality ("strong", "impressive"). |
| `value` | Verbatim value(s) as found: `{"metric":"F1","value":0.812,"unit":null,"n":5,"spread":{"type":"std","value":0.004}}` |
| `conditions` | Dataset, split, scale, hyperparameters, environment: whatever qualifies the value |
| `locator` | `{"path":"results/table2.csv","anchor":"row=method_x;col=f1"}`. Must resolve. |
| `strength` | `hard` (measured, logged, reproducible from files) · `soft` (notes, recollection, a single unlogged run, an unverified statement) |
| `status` | `ok` · `conflicting` (with `conflicts_with`) · `incomplete` (e.g. no variance) · `unverifiable` |
| `derived_from` | For calculated values, the input E-ids and the formula |
| `notes` | Anything the author wrote about it, quoted |

**Rules**
- Copy numbers **verbatim**. Rounding happens only in the draft and must be declared
  (`rounding: 2dp`).
- A value that appears only in prose (notes or drafts) and not in a data file is
  `strength: soft`.
- A result without a variance/spread, where multiple runs were possible, gets `status:
  incomplete` and a `missing_evidence` entry.
- **Negative results are first-class.** Failed runs, abandoned approaches with a recorded
  reason, and ablations where the component didn't help are all recorded.
- **The authors' own statements are first-class too.** Each limitation the authors state is a
  `limitation_noted` item. Each motivation or design reason they give ("we chose X because Y")
  is a `rationale_stated` item. Quote them verbatim in `notes`. Record broad statements too:
  whether they are "generic" is not the extractor's call.

---

## 2. Claim types: the evidence ladder

Each claim `C###` has exactly one `claim_type`:

| Type | Meaning | Minimum evidence |
|------|---------|------------------|
| `measured` | A value directly measured under stated conditions | ≥1 `hard` result item |
| `observed` | A qualitative pattern seen in the data or outputs | ≥1 observation item + the examples' locators |
| `derived` | Computed from measured values (a difference, ratio, significance test) | `derived_from` with its inputs, plus a reproducible calculation |
| `literature` | Established by others | ≥1 verified source with a support quote (`citation_rules.md`) |
| `interpretation` | What the results mean; an explanation of *why* | ≥1 measured/observed/derived claim + a stated reasoning link. Alternatives considered. |
| `hypothesis` | A proposition the work tested or proposes to test | Labeled as a hypothesis; if tested, linked to the result |
| `speculation` | A plausible but untested explanation | Labeled as untested; never placed in the abstract as a finding |
| `future` | A direction not pursued | — |

**Composite sentences** carrying two claim types need two tags, or should be split.

---

## 3. Permitted and forbidden language

| Type | Permitted verbs / frames | Forbidden |
|------|-------------------------|-----------|
| measured | "X achieved/reached/was Y (± s, n=…)", "we measured" | "proves", "demonstrates superiority" (unless a comparison is also measured + derived) |
| observed | "we observed", "in N of M cases", "the outputs showed" | "always", "consistently" (unless all cases were checked, and then give the count) |
| derived | "a difference of", "significant at α=… (test)", "corresponds to" | "significant" without a named test; "large" without a reference point |
| literature | "[Src] reports/found/proposed" | Stronger verbs than the source uses; "it is well known" without a source |
| interpretation | "suggests", "is consistent with", "one explanation is", "we interpret this as" | "shows that" / "proves" / "establishes" / causal verbs without causal design |
| hypothesis | "we hypothesize", "we expected", "we test whether" | Present-tense assertion as fact |
| speculation | "a possible (untested) explanation", "may", "we speculate" | Placement in the abstract or conclusion as a finding |
| future | "future work could", "remains open" | Promises ("will solve") |

**Global watch-list** (the lint flags these; each needs a justification or a rewrite): *prove,
proof* (outside a mathematical proof), *first* / *novel* / *unprecedented* (needs a
search-scoped basis), *state-of-the-art* / *SOTA* (needs a named benchmark, the comparison set,
and a date), *significant(ly)* (needs a test), *always / never / all* (needs complete
enumeration), *dramatically / remarkably / substantially* (give the number instead), *clearly /
obviously* (delete), *causes / leads to / drives* (needs causal design), *generalizes* (needs
evidence outside the training distribution).

---

## 4. Confidence (derived, never asserted)

`confidence ∈ {high, moderate, low}`, computed from:

| Factor | Raises | Lowers |
|--------|--------|--------|
| Evidence strength | all `hard` | any `soft` |
| Replication | ≥3 seeds/runs/sites with spread reported | single run |
| Consistency | no conflicting items | `conflicting` status present |
| Scope match | claim scope ⊆ evidence conditions | claim broader than the conditions |
| Controls/baselines | baselines tuned with a comparable budget; ablations | untuned or missing baselines |
| Alternative explanations | considered and addressed | not considered |

Rule of thumb: **high** needs all six on the "raises" side. Any two on the "lowers" side mean
**low**. Low-confidence claims can't appear in the abstract except as explicitly hedged
statements.

---

## 5. Claim record

```json
{
  "id": "C007",
  "statement": "On dataset D (test split), method M reduced mean absolute error relative to baseline B by 12% (0.81 → 0.71; 5 seeds, std ≤ 0.01).",
  "claim_type": "derived",
  "evidence": ["E014", "E015"],
  "scope": {"datasets": ["D"], "conditions": "test split, default hyperparameters"},
  "confidence": "moderate",
  "confidence_reasons": ["5 seeds", "baseline not re-tuned (E022)"],
  "limitations": ["L003"],
  "negative_results": ["E031"],
  "permitted_verbs": ["reduced", "a 12% lower"],
  "author_confirmation": "pending",
  "used_in": []
}
```

**Attribution fields.** `origin` (`author_stated` | `writer_derived`) records who asserts a
claim. `rationale` (`motivation` | `design_choice`) marks a claim that carries the authors'
reason for the work or for a design choice. A rationale claim is always `origin: author_stated`
and cites a `rationale_stated` item.

Limitations are also objects (`L###`), with `affects_claims`, a required `origin`, and
`evidence`. An `author_stated` limitation cites ≥1 `limitation_noted` item, and every live
`limitation_noted` item is cited by one. A `writer_derived` limitation usually cites
`negative_result` items or a gap between claim scope and evidence
conditions).

---

## 6. Negative-result inventory

For every `negative_result` item, the author must choose, and the choice is recorded:
- `reported_main`: in the main text, near the claim it qualifies
- `reported_supplement`: in the supplement, with a pointer in the main text
- `excluded`: with a reason (e.g. "run crashed; no metric produced", "superseded by corrected
  implementation E040")

An exclusion reason that amounts to "it didn't support our claim" is not accepted.
`SELECTIVE_REPORTING` is raised.

---

## 7. What CORPUS_AGENT must never do with evidence

- Turn `soft` into `hard` by restating it confidently.
- Merge conflicting values into an average or "typical" value.
- Infer a result from code or a config that was never run.
- Fill a missing variance with an assumed one.
- Read a figure image and extract numbers without marking `extracted_from_image: true,
  strength: soft`.

---

## 8. Truth guardrail fields (v0.3)

**Evidence items** may carry `quantity` (what the value measures, e.g. `num_datasets`),
`run_id`, and `source_hash` (`sha256:…` of the file read). Two live items with the same
`quantity` (or the same metric + conditions + `run_id`) and different values are a conflict. Mark
both `status: conflicting` with `conflicts_with`, and record on one of them:

```json
"resolution": {"chosen": "E002", "reason": "the manifest enumerates every dataset; the README count is a summary", "by": "agent"}
```

Until then, every claim citing either item is `BLOCKED_BY_CONFLICT`. A claim that cites the
rejected side is `CITES_REJECTED_EVIDENCE`.

**Claims** gain a *provenance* axis, separate from the epistemic `claim_type`:

| Field | Values | Rule |
|---|---|---|
| `basis` | project_file · code · user_confirmed · literature · none | measured/observed/derived with `none` = `UNSUPPORTED_FACT` |
| `status` | VERIFIED · NEEDS_REVIEW · BLOCKED | BLOCKED claims never appear in the draft |
| `licenses` | `[{"type": …, "evidence": [E…]}]` | required for licensed wording (below) |

Mapping from the vNext spec's single list: OBSERVED → `measured`/`observed`; DERIVED → `derived`;
LITERATURE → `literature`; METHOD_FROM_CODE → `basis: code`; USER_CONFIRMED →
`basis: user_confirmed`; HYPOTHESIS → `hypothesis`; PROPOSED → `future`/`speculation`;
UNRESOLVED → `status: BLOCKED`. `interpretation` has no spec equivalent and stays.

**Licensed wording.** These words are allowed only when a tagged claim holds the license, and the
license's evidence qualifies (`tools/truth_guardrail.py` `LICENSES`):

| Wording | License | Evidence must record |
|---|---|---|
| significant(ly) | `significance_test` | a named test and a p-value or CI |
| state of the art / SOTA | `sota_comparison` | benchmark, complete comparison set, date |
| robust | `stress_test` | a stress/perturbation evaluation |
| real-time | `latency_measured` | measured latency and target hardware |
| clinically validated | `clinical_study` | the study type |
| generalizes | `ood_eval` | an out-of-distribution evaluation |
| novel / first | `literature_search` | a bounded, logged literature search |
| causes / leads to | `causal_design` | randomized, controlled, ablation or intervention design |
| outperforms / beats | `matched_evaluation` | matched/tuned baselines under one protocol |
| always / never | `complete_enumeration` | the enumerated cases (lint WARN only) |

A claim map that contains a `licenses` key anywhere switches the lint to fail-closed (ERROR);
legacy claim maps get WARN. Negated or hypothesis/speculation/future/limitation uses are exempt.
