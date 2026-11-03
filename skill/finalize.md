# Finalize: format, disclose, package

This is P7, steps 20–22, gate G5. Step 19 (the line edit) is in `workflow.md`, and step 20 (final
integrity) is in `integrity.md` §5. This file covers what happens once the words are settled.

The rule of this phase: **formatting changes appearance, never content.** If a format step would
change a claim, a number or a citation, stop and go back to step 19.

---

## 1. Step 21: references

`paper/references.bib` is generated from `corpus/source_registry.json`. Every field comes from the
index record, so nothing is typed or tidied by hand.

- A source with `title_status: as_cited` or `unverifiable` keeps the project's own text, and it is
  listed in `open_issues.md`.
- An `unresolvable` source appears with whatever the registry holds, and stays listed.
- A citation with no registry entry stops the format step. By now that is a defect, because the
  lint should have caught it (`C5-citation-unregistered`).

Citations stay author-year in the drafts, which is the form the lint checks. At step 21,
`tools/format_paper.py` maps each one to its registry key, so Pandoc can restyle it. A citation that
does not map to exactly one key stops the step.

---

## 2. Step 21: formats and styles

```
python tools/format_paper.py paper/paper.md --rcs .rcs --to latex,docx,pdf
```

The citation style comes from `--csl`, `plan/venue_profile.yaml`, or `paper_config.citation_style`.
Pandoc applies it with `--citeproc` and a CSL file (S39, S40). CSL files live in `.rcs/cache/csl/`.
With `--online`, a named style is fetched from the CSL styles repository. A profile that says only
`numeric` or `author-year` is treated as IEEE or APA, and the report records that as assumed. With no
style at all the step stops, because Pandoc's default style would be a silent choice.

`--bib-only` writes `references.bib` and stops. For a venue's own LaTeX class, pass a Pandoc template
with `--template`. The tool does not write one.

| Output | Route | Needs |
|---|---|---|
| Markdown | The stripped manuscript | Nothing |
| LaTeX | Pandoc | Pandoc |
| DOCX | Pandoc | Pandoc |
| PDF | Pandoc **through LaTeX** | Pandoc and tectonic or pdflatex |

- **PDF goes through LaTeX, never through HTML.** HTML-to-PDF output is not an acceptable substitute.
- **A missing tool stops that output and only that output.** Raise `FORMAT_TOOL_MISSING`, name the
  tool and list what was not produced. Never substitute a different route silently.
- **Check that nothing moved.** After conversion, the tool confirms that every number in
  `paper/paper.md` and every cited work appears in the output. It reads LaTeX and DOCX directly, and
  PDF only if `pdftotext` is installed. If it cannot read an output, the report says so, and you
  inspect that output by hand. Only cited works are written to `references.bib`.

**Render and inspect at final size.** Recheck visuals, cross-references and readability, and retain
source and export paths and hashes. If rendering or a human check is unavailable, say which checks
were not performed. A clean text lint is not a layout certificate (`representation_design.md`
§§6–7).

---

## 3. Step 22: disclosure

```
python tools/disclosure.py .rcs --out disclosure.md
```

`disclosure.md` is a draft for the authors to edit. They are responsible for it, and an AI cannot be
an author (S15–S17).

- **The rules come from the venue profile.** Use `ai_policy` in `plan/venue_profile.yaml`, which
  records the official page and the retrieval date (step 11). Policies change, so never state one
  from memory. With no policy on file, write a generic statement, mark it `assumed` and raise
  `VENUE_UNKNOWN`.
- **The facts come from the run.** Which roles were automated, what they produced and what people
  checked come from `.rcs/provenance.jsonl`, `.rcs/models.json` and the checkpoint answers. Facts
  the record does not hold become `[ASK AUTHOR: …]`.
- **Say what was verified, and how.** "All numbers were traced to project files by a deterministic
  tool" is a true sentence when the G5 reports exist. Do not imply checks that did not run.
- **Place it where the venue requires** (`required_statements.ai_use_disclosure`).

---

## 4. Step 22: statements and the submission checklist

Fill only what the evidence and the authors supply.

| Item | Source | If missing |
|---|---|---|
| Author contributions (CRediT, S35) | The authors | `[ASK AUTHOR: …]` |
| Funding, conflicts of interest | The authors | `[ASK AUTHOR: …]` |
| Data and code availability | Project files and the authors | `[ASK AUTHOR: …]` |
| Ethics approval | The authors | `[ASK AUTHOR: …]` |
| Reporting guideline checklist (S36) | `plan/venue_profile.yaml` | Named in `open_issues.md` |

Write `paper/submission_checklist.md` from the venue's required statements, limits and formats, and
mark each item done, not done or not applicable. A venue requirement the skill cannot check is
marked `not checked`, not done.

---

## 5. Step 22: the package

```
open_issues.md                  delivered first
paper/paper.md                  the manuscript, no internal tags
paper/references.bib
paper/paper.tex, .docx, .pdf    those that were produced
paper/response_letter.md        revise mode only
paper/submission_checklist.md
disclosure.md
process_record.md               optional
.rcs/                           the audit trail
```

`open_issues.md` holds everything unresolved, in plain language: remaining markers, `unresolvable`
and `disputed` sources, integrity warnings and recorded decisions, deferred findings, and any check
that did not run. **A paper with unresolved `[MISSING …]` markers is a draft, not a final paper. Say
so.**

**`process_record.md` (optional).** What the people decided and what the AI did: the mode, the
checkpoints with their named answers, the roles and models, the gate history, and the history of
each integrity mode, including any decision to proceed. Build it from the ledgers, not from memory.

---

## 6. Gate G5

G5 runs after the step 21 outputs exist:

```
python tools/validate_artifacts.py .rcs --out .rcs/audits/gates/G5_validate.json
python tools/lint_draft.py paper/paper.md --rcs .rcs --final --out .rcs/audits/gates/G5_lint.json
python tools/verify_numbers.py paper/paper.md --rcs .rcs --out .rcs/audits/gates/G5_numbers.json
python tools/validate_artifacts.py .rcs
```

Together with the `claim_invariance.py` report from step 19, all must report 0 errors, and GI must
be passed with `stage: final`. The last `validate_artifacts.py` re-checks every gate marked passed.
A passed G5 means the checks ran and came back clean. It does not mean the paper is correct, and it
does not predict acceptance.
