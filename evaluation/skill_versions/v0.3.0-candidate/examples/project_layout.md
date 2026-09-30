# Example project-folder structure

The skill accepts **any** structure. CORPUS_AGENT inventories whatever it finds. This layout
just makes evidence easier to locate and cite.

```
my_project/
├── README.md                    # what the project is (Level 0, soft)
├── problem.md                   # problem definition, intended contribution in your words
├── notes/                       # lab notes, observations, decisions, TODOs (soft evidence)
├── literature/                  # PDFs or a .bib you already trust (to be verified)
├── data/                        # datasets or pointers + data cards
├── configs/                     # experiment configs (hard evidence for method details)
├── code/                        # implementation (evidence of method; not of results)
├── results/                     # machine-written logs, CSV/JSON metrics (hard evidence)
│   ├── main/
│   ├── ablations/
│   └── failed/                  # keep failed/negative runs. The skill reports them.
├── figures/                     # figure images + the scripts that made them
├── drafts/                      # previous drafts (communication history)
├── reviews/                     # reviewer feedback, rejection letters
└── .rcs/                        # created by the skill
    ├── config.yaml              # audience, venue, model bindings, data policy
    ├── state.json               # workflow step, gates, open failure states
    ├── evidence/                # project_inventory, research_evidence, missing_evidence
    ├── claims/                  # claim_candidates, claim_evidence_map
    ├── story/                   # spine.md, story_graph.json, question_ledger, term_ledger, lit_gap_chain.md
    ├── corpus/                  # source_registry, literature_map, writing_patterns, anti_patterns, corpus_log
    ├── plan/                    # audience_profile, venue_profile, paper_architecture, skeleton, figure_cards/
    ├── drafts/v001/ …           # tagged drafts
    ├── audits/v001/ …           # lint.json, citation_audit.json, reconstruction_self.md, …
    ├── packets/review_v001_1/   # the only reviewer-visible directory
    ├── diagnostics/v001_1/      # diagnostics.json, reconstruction.json
    ├── evaluation/              # gold_story.json, grading.json, prereg_*.md
    └── private/                 # reviewer_notes.private.md (never read by AUTHOR/SKILL_AGENT)
```

What helps the most:
1. **Machine-written results files.** Numbers typed into notes are `soft`.
2. **A failed/negative-results folder.** The skill can only report what it can find.
3. **`problem.md` in your own words.** It anchors spine lines 1–3 and reduces
   `CONTRIBUTION_UNCLEAR` round-trips.
4. **Figure scripts next to the figures**, so figure cards can point at their data.

See `demo_project/` for a small, fully worked (synthetic) instance.
