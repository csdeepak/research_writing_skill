# Corpus log

## Mode: literature (closed corpus, no web -- run-specific constraint)

No search queries were issued (no web access this run). The candidate corpus is exactly the
22-entry reference list already present in `project/paper.txt`. Every source below was
screened for whether it is **load-bearing** in the restructured paper (i.e. whether a sentence
in this paper's Background, Related Work, or Methods actually depends on it), not for topical
relevance via search, since there was no search.

**Verification method for all sources: `user_supplied_file`.** The reference's existence and
metadata are known only because `project/paper.txt`'s own bibliography lists it; no independent
DOI/index lookup or retraction check was possible (no web). **Read depth: `abstract` for all
sources** -- none of the 22 cited works themselves were read; every `establishes` statement in
`source_registry.json` quotes what *MLPerf Tiny's own authors* say about that source, not an
independent reading of the source. This is the literature-mode override specified by this run's
TASK.md, which takes precedence over `citation_rules.md`'s general preference for full-text
reading.

## Screening decisions (all 22 references)

| Ref | Registered? | Reason |
|-----|-------------|--------|
| [1] TinyML Foundation | No | No author or year given anywhere in the entry; cannot be cited in the required "(FirstAuthor et al., Year)" form without inventing a year. "TinyML" is used in this paper as a plain field name, uncited. |
| [2] BrainChip | No | No personal/organizational author-year combination strong enough to carry a load-bearing sentence in the restructured paper; the "event-based neural processor" aside it supports is cut for length and is not essential to any claim. |
| [3] Asanović & Patterson, 2014 | Yes -- SRC-003 | Supports the RISC-V description in the Results/Evaluation section. |
| [4] Banbury et al., 2021 | Yes -- SRC-004 | Supports the Impact/Discussion sentence about reuse in later TinyML research. |
| [5] Bouguera et al., 2018 | Yes -- SRC-005 | Supports the Introduction's aside on wireless communication's energy cost vs. on-device compute. |
| [6] Chowdhery et al., 2019 | Yes -- SRC-006 | Visual Wake Words dataset/task definition. |
| [7] David et al., 2020 | Yes -- SRC-007 | TFLite Micro, the reference runtime. |
| [8] Fedorov et al., 2019 | Yes -- SRC-008 | Supports "prior TinyML work has used CIFAR-10" continuity claim. |
| [9] Gal-On & Levy, 2012 | Yes -- SRC-009 | CoreMark -- key Related Work / Gap source. |
| [10] He et al., 2016 | Yes -- SRC-010 | ResNet, the Image Classification model family. |
| [11] Howard et al., 2017 | Yes -- SRC-011 | MobileNetV1, the Visual Wake Words model. |
| [12] Koizumi et al., 2019 | Yes -- SRC-012 | ToyADMOS dataset component. |
| [13] Koizumi et al., 2020 | Yes -- SRC-013 | DCASE2020 task definition for Anomaly Detection. |
| [14] Krizhevsky et al., 2009 | Yes -- SRC-014 | CIFAR-10 dataset. |
| [15] Lin et al., 2014 | Yes -- SRC-015 | MSCOCO, the base of the VWW dataset. |
| [16] Moreau (Edge Impulse) | No | No year given anywhere in the entry; the "public projects on a dev platform" point it supports is dropped from the main text rather than cited without a recoverable year (see missing_evidence.json MISS-005). |
| [17] Purohit et al., 2019 | Yes -- SRC-017 | MIMII dataset component. |
| [18] Reddi et al., 2019 | Yes -- SRC-018 | MLPerf Inference -- key Related Work / Gap source. |
| [19] Torelli & Bangale, n.d. | Yes -- SRC-019 | MLMark -- key Related Work / Gap source; cited as "n.d." rather than inventing a year (no year given in the reference list). |
| [20] Torralba et al., 2008 | Yes -- SRC-020 | 80 Million Tiny Images, CIFAR-10's parent dataset. |
| [21] Warden, 2018 | Yes -- SRC-021 | Speech Commands v2 dataset. |
| [22] Zhang et al., 2017 | Yes -- SRC-022 | The keyword-spotting DS-CNN model. |

**Stopping reason:** the candidate list is closed (exactly the 22 references in paper.txt); every
entry was screened once. No snowballing was attempted (no web).

## Suspicious/anomalous content

- `project/paper.txt`, Section 2 "Hardware Heterogeneity" (line 23): the phrase "...or memory
  compute citekim20191" contains an unresolved LaTeX citation key (`citekim20191`) that does not
  match any of the 22 numbered entries in the reference list. This reads as leftover source
  markup from the PDF-to-text extraction, not as content directed at a reader or at an AI system.
  It is not used as a citable source (see missing_evidence.json MISS-006) and is not otherwise
  acted on.
- No instruction-like text aimed at models or reviewers (e.g. "ignore previous instructions",
  "as an AI reviewer...") was found anywhere in `project/paper.txt` or `project/README_1.md`.
