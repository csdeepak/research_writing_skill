# Role: AUTHOR (length fix + second review round, workflow steps 20-21)
Same working directory and hard rules as before (TASK_AUTHOR_ANSWERS.md). Tools were updated by the orchestrator:
the lint counts headings and table text for guardrail-v0.3 projects (so paper/paper.md is 4,620 words against 4,500),
G4 is now STALE because v004 states C022, which no blind review covered, and author statements the authors rejected are
no longer reported as withheld.

1. Fit the limit: write `.rcs/drafts/v005/paper.md` (tags kept) from v004 by relocating SUPPLEMENTARY material to the
   appendix (or tightening wording) until `python rce/tools/lint_draft.py .rcs/drafts/v005/paper.md --rcs .rcs` reports
   no S4-over-length. Never cut a claim, an author-stated limitation, an author rationale, a number's interval or
   denominator. Check `python rce/tools/claim_invariance.py .rcs/drafts/v004/paper.md .rcs/drafts/v005/paper.md`: 0 errors,
   and no claim dropped.
2. Build the round-2 blind review packet:
   `python rce/tools/build_review_packet.py .rcs/drafts/v005/paper.md --out .rcs/packets/review_v005_1 --audience .rcs/packets/audience.md --objective .rcs/packets/objective.md --strip-markers`
   (it now copies and hashes the linked figures itself). Record what you wrote. Then STOP and reply DONE with the v005
   word count (all/prose), the invariance summary and the packet id. Do not write a review yourself.
