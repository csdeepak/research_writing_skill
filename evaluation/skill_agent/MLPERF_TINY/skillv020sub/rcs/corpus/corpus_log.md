# Corpus log (step 7)

## Mode and scope
No web access is available in this run (TASK.md; recorded as accepted risk AR-003 in
`.rcs/state.json`). Literature mode is therefore restricted to works already cited in
`project/paper.txt`. No index was queried (no Crossref/OpenAlex/Semantic Scholar/etc. lookups
were performed); every source in `corpus/source_registry.json` is registered with
`verification.method = "user_supplied_file"` and `read_depth = "abstract"`, meaning: we trust
the bibliographic string in `project/paper.txt`'s own reference list, and we take what each
source "establishes" from how `project/paper.txt` itself describes or uses it, not from
independently reading the source.

## Selection
Of the 22 numbered references in `project/paper.txt`, 19 are registered (`SRC-001`..`SRC-019`)
because the new paper cites them for one of: (a) situating the Gap (CoreMark, MLMark, MLPerf
Inference), (b) naming a dataset or model the new paper describes (MSCOCO, Visual Wake Words,
MobileNets, CIFAR-10, the CIFAR-10-in-TinyML precedent, ResNet, Speech Commands, Hello
Edge/DS-CNN, ToyADMOS, MIMII, DCASE2020, TFLite Micro), (c) the energy motivation for on-device
inference (Bouguera et al.), (d) the impact/adoption claim (Micronets, the Edge Impulse
project), or (e) a one-clause gloss for an audience term (RISC-V).

Three references were **not** registered and are **not cited** in the new paper:
- `[1]` (TinyML foundation, a bare URL with no author or year) -- the term "TinyML" is used
  without a formal citation rather than fabricating missing bibliographic metadata.
- `[2]` (BrainChip, a company web page) -- only used in the source paper as a passing example
  of "novel architectures"; not load-bearing for this paper's argument.
- `[20]` (Torralba et al., 80 Million Tiny Images) -- only the etymology of CIFAR-10's parent
  dataset, one level removed from anything the new paper's claims depend on.

## Screening
No relevance/recency/type screening against an index was possible (no web). Screening here
means: does the new paper's argument actually need this citation to support a specific sentence
(per `citation_rules.md` step 3, "supports")? Each registered source's `establishes.support_quote`
in `corpus/source_registry.json` is the sentence from `project/paper.txt` that justifies keeping
it.

## Verification
Every registered source's existence, authors, and year come from `project/paper.txt`'s own
reference list (Level-0 evidence), not from an independent lookup. Two sources (`[16]` Moreau,
`[19]` Torelli and Bangale) give no year in that list; they are cited without inventing one
(accepted risk AR-005). No retraction check was possible (no web).

## Suspicious content
None found. No text in `project/paper.txt` or `project/README_1.md` is addressed to an AI
system, a reviewer, or contains hidden/injected instructions.

## Stopping reason
Registration stopped once every citation the new paper's argument needs (per the paper
architecture, step 8) had an entry. No snowballing or additional batches were attempted, per
the no-web constraint.
