# Step 15: figure/table audit

- No images are used. Three Markdown tables (Tables 1-3) each have a card in plan/figure_cards/ with evidence, source_data, takeaway and non-conclusions.
- Each table is referenced before it appears and its takeaway is stated in the prose. Captions open with the finding.
- validate_artifacts figure-card checks: 0 errors.
- Visual gates V1-V6 (tools/validate_visuals.py) are not applicable: no visual registry, no rendered figures. They are recorded as not run, never as passed. V5 needs a human review and is not claimed.
- Figures 1, 2, 4, 5 of the source are images not present in the extracted text (missing_evidence M006, NO_VALID_VISUAL). No substitute was drawn.
- Honesty: Tables 2 and 3 show OpenHands rows beside both higher and lower references, including negative rows; the selection rule is in the cards.
