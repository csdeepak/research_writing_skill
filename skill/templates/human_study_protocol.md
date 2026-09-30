# Human reading study: how to run it (vNext Stage 3 acceptance)

Stage 3 is accepted only with **blinded human** reconstruction results, reported even if they show no improvement
(`docs/06_VNEXT_SPEC.md` §12; `docs/04_EVALUATION_FRAMEWORK.md` §10). LLM "proxy readers" test the machinery.
They are **not** this evidence. This protocol turns the tools into a study you can run with real people.

## 0. Before anyone reads (freeze everything)
```
python tools/comprehension_kit.py key .rcs            # pre-declared answer key, hash-frozen
python tools/comprehension_kit.py packets .rcs --paper paper.md
python tools/comprehension_kit.py form .rcs
```
- Commit `.rcs/evaluation/comprehension_key.json` and `.rcs/comprehension_runs/SEALED.json` **before**
  recruiting. Scoring refuses a key that changed after freezing.
- Do not open `SEALED.json` until scoring. The packet ids (`cpk-…`) hide the condition
  (visual-only vs full).

## 1. Participants
- Match the binding persona in `.rcs/plan/reader_model.json`: ≥3 readers per binding persona.
  More readers give tighter intervals, and 3 is a floor, not a target.
- Each participant reads **one** packet per project. A second packet of the same project would
  teach them the answers.
- Consent: read the consent paragraph at the top of `participant_form.html`. Record an anonymous
  id only. If your institution requires ethics review for such studies, get it first.

## 2. Session (per participant)
1. Hand over one packet (`packet.html`, or a printout) with its time limit: visual-only 3 min,
   full 20 min.
2. When time is up, take the packet away.
3. They fill in `participant_form.html` from memory: 5 questions plus confidence 1–5.
   "Cannot tell" is a valid answer.
4. Enter the answers into `responses.csv` (template: `responses_template.csv`), one row per
   question, with `reader_type = human`.

## 3. Grading (two people, blind)
```
python tools/comprehension_kit.py sheets .rcs --responses .rcs/comprehension_runs/responses.csv
```
- Two graders each copy `grading_sheet.csv` to their own file (`grades_<name>.csv`) and fill in
  `label` (present / weakened / overstated / contradicted / absent) for every row, and
  `unsupported_beliefs_in_answer` (`;`-separated). These are claims **the paper does not
  support**; a correct detail the key omits is not one.
- Graders see response ids only, never participants or conditions. Don't discuss labels until
  both are done. Then resolve disagreements and record them.

## 4. Scoring
```
python tools/comprehension_kit.py score .rcs --grades grades_alice.csv grades_bob.csv
```
- The report shows per-condition MMF/RR with bootstrap 95% CIs and **Krippendorff's α**
  (α ≥ 0.80 firm, ≥ 0.67 tentative, below that the grading is unreliable and must be redone
  with clearer guidance).
- Report the result whatever its direction. A null or negative result is a finding.
- Compare with the LLM-proxy result on the same packets. A large gap means the proxy is
  miscalibrated for this domain (docs/04 §10 "calibration signal").

## 5. V5 (figure usability) in the same session
After the reading task, show each figure for about 1 s, 10 s and 1 min and ask: what is it about;
what is the takeaway; what is one detail. Then record it (a person runs this, never the agent):
```
python tools/record_review.py .rcs V001 --reviewer "<name>" --topic yes --takeaway yes --detail no
```
