# Role: AUTHOR (round-2 revision, workflow steps 19-21)
Same working directory and hard rules as before. The round-2 blind review of v005 is in `.rcs/diagnostics/v005_1/`
(it was run through `rce/tools/rce_roles.py review`; you cannot see the reviewer's prompt and must not look for it).

1. For EVERY blocking finding (score <= 2; evidence_traceability / claim_evidence_alignment / unsupported_inference < 4)
   and EVERY inference issue, write `.rcs/revisions/v005_1/dispositions.json` (fixed + where | declined + reason >= 20
   chars | deferred + listed in open_issues.md). Treat findings on their merits; never state a fact the evidence does
   not support or an open checkpoint (Q-003, Q-005) blocks.
2. Revise into `.rcs/drafts/v006/paper.md` (tags kept). The main text must stay <= 4,500 words by the lint (v005 is at
   4,497): offset every addition by relocating supplementary material to the appendix. Check
   `python rce/tools/claim_invariance.py .rcs/drafts/v005/paper.md .rcs/drafts/v006/paper.md` (explain every change it
   reports in the dispositions). Write the final manuscript without tags to `paper/paper.md`.
3. Run `python rce/tools/run_workflow.py gates .rcs --project-root . --draft .rcs/drafts/v006/paper.md --round v005_1 --revised .rcs/drafts/v006/paper.md --final paper/paper.md --before .rcs/drafts/v005/paper.md --edited .rcs/drafts/v006/paper.md`
   and report the effective gates. Record everything as AUTHOR. Reply DONE with the disposition counts, word counts
   (all/prose) and the effective gates.
