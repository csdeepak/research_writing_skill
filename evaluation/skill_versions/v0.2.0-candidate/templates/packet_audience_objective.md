# Templates for review-packet inputs

Write these two files in plain language. They are the reviewer's only context besides the paper.
Don't include evidence IDs, file names, source lists, or anything about how the paper was made.

## audience.md
```
Intended readers: <one or two sentences, e.g. "machine-learning researchers who work on
robustness but not on time-series forecasting">.
They can be assumed to know: <list>.
They cannot be assumed to know: <list>.
Binding reader types for this review: <A/B/C/D/E with one-line descriptions>.
Venue type: <journal / conference / workshop / thesis>.
```

## objective.md
```
In the authors' words, this paper is meant to <one paragraph: the problem, what the paper asks,
and what a reader should come away understanding>.
```

## open_issues.md (given to the user at the end)
```
# Open issues: <paper>, draft v<NNN>
## Must resolve before submission
- [MISSING RESULT] …  (where: §3.2 ¶2; why it matters: bounds claim C002)
- [CITATION NEEDED] … (where; what kind of source would support it)
- [ASK AUTHOR] …
## Accepted risks (you chose to proceed)
- …
## Assumed venue rules (no official source found)
- …
## Claims awaiting your confirmation
- C005 (interpretation): "…" (inferred by the agent, not stated in your notes)
```

## disclosure.md (draft for the authors; adapt to venue policy)
```
During preparation of this manuscript the authors used <tool/model, version> to <organize
research notes into an argument structure, draft sections from author-verified evidence
maps, and check terminology and claim consistency>. All results, numbers, and citations were
verified by the authors against the original data and sources. The authors take full
responsibility for the content.
```
