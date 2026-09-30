# Step 12 - evidence/claim audit

- tools/verify_numbers.py (G3_numbers.json): 0 errors, 0 warnings; three DERIVED_MATCH infos (1.5, 1.5, 1.6) are the Table 2 gaps of claim C035 (86.5 - 85, 91.6 - 90), confirmed.
- tools/lint_draft.py (G3_lint.json): 0 errors. Remaining warnings are undefined-acronym warnings for product and dataset names (NUCLEO, MBED, GCC, ARM, LPM01A, JS110, UNO, DCASE2020, MIMII, MSCOCO, CIFAR, RISC, README, and reference-list acronyms). They are kept because they are the authors' names for hardware or datasets; each is glossed in the text where it matters.
- Every number was re-read against project/paper.txt or the README by the numbers tool (traces to evidence items cited by the tagged claims).
- Claim types and verbs: interpretation claims (design reasons, C018, C002) use "the authors state / attribute / read"; measured claims use "reaches"; the one derived claim (C035) is labelled "our arithmetic" in Table 2.
- Negative results: the evidence map holds none. Absences are reported as caveats L005-L008, not hidden: no variance, no Figure 5 values, no submission measurements.
- Fixed in this pass: 'generalization' wording (unlicensed ood_eval) replaced by a paraphrase of the authors' reason; strong verbs on interpretation claims changed to 'show'; L008 removed from the Conclusion's author-limitation sentence; VWW 'about 86%' kept as 'about'.
