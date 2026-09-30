# AI-use disclosure (draft)

`./paper.md` is a machine-generated re-presentation of the MLPerf Tiny Benchmark research
(Banbury et al., the source project in `./project/`) for a machine-learning audience outside its
own subfield. It was produced by Claude, using Anthropic's Research Communication Engine skill,
from the project's own paper text and README, with no other source of information: no web access
and no other project files were used or available.

The process built a verifiable evidence map (`.rcs/evidence/`), a claim-evidence graph
(`.rcs/claims/`), and a research-story graph (`.rcs/story/`) from the source material before
drafting any prose, then ran a series of structural, citation, and overclaim audits
(`.rcs/audits/v001/`) against the draft. Every quantitative figure in `./paper.md` is traceable to
a specific location in `project/paper.txt` or `project/README_1.md` via these artifacts. No
number, citation, or claim was invented; where the source material was incomplete (e.g., Figure 5's
underlying chart values did not survive text extraction), this is marked explicitly in the text
with a `[MISSING RESULT: ...]` note rather than filled in.

No human reviewer was available during this run (see `.rcs/state.json -> accepted_risks`), so the
usual human-in-the-loop confirmation of the spine and claim map did not occur, and the workflow's
blind-review step (step 18) has been deferred to an external process rather than performed here.
Anyone using `./paper.md` should treat it as an audited draft, not a final, human-approved
manuscript: `./open_issues.md` lists everything that remains open, and the original authors of
the MLPerf Tiny project take no responsibility for this derived presentation of their work.
