# Task: Independent verification of the Gold Account for project {P}

You are an independent verifier. Another agent drafted a Gold Account: the factual scoring authority for an experiment that measures how accurately readers reconstruct research. Check it against the frozen evidence. Don't trust it.

Repository root: `C:/Users/<user>/PESU/research_skill/research_writing_skill`
- Evidence (sole authority): `evaluation/external_projects/{P}/snapshot/paper.txt` and `README__*.md`
- Draft to verify: `evaluation/ground_truth/{P}/GOLD_ACCOUNT_DRAFT.md`, `evaluation/ground_truth/{P}/gold_story.json`
- Assessment (context only): `evaluation/external_projects/{P}/PROJECT_ASSESSMENT.md`
Do not read `skill/`, `docs/`, other projects, or anything under `evaluation/` except these files.

## Check every item for
factual correctness · numerical correctness (every number, against the snapshot text) · experiment correctness (did this experiment actually happen in the paper, as described?) · dataset correctness · methodology correctness · claim/evidence alignment (is the strength label right? was an interpretation turned into a measurement? was a claim strengthened?) · limitation coverage (are author-stated limitations missing? are there limitations that are really the drafter's own critique?) · unsupported claims · README-vs-paper separation and conflict handling. For gold_story.json also check that nuggets are atomic, that each is answerable from a good paper about this research, and that the Q7 numbers are exact.

## Outputs (do NOT modify the draft files)
1. `evaluation/ground_truth/{P}/VERIFICATION.md`: a table of every issue (item · problem · evidence quote from the snapshot · severity high/med/low · correction), counts by type, and a verdict: ACCEPT / ACCEPT AFTER CORRECTIONS / REJECT. List source conflicts with the source treated as authoritative and why (the paper is authoritative for research claims; the README only for artifact facts).
2. `evaluation/ground_truth/{P}/gold_story.v1.json`: the corrected nuggets. Same schema; keep the ids stable where possible; add `"verified": true` at the top level; 25–40 nuggets.
3. `evaluation/ground_truth/{P}/GOLD_ACCOUNT_v1.md`: the corrected Gold Account, with a "Changes from draft" section at the top.

Finish with a 4-line summary: verdict, #issues (high/med/low), most serious error found, remaining uncertainty.
