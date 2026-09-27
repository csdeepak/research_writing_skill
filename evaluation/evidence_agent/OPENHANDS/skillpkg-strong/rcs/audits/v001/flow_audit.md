# Step 13 — Logical-flow audit

**Paragraph level.** Each paragraph in §5 opens with the benchmark/category it reports on (topic
sentence first), gives the number, states the comparator, and (per the Result Interpretation
Chain) closes with a qualifying or interpretive clause. Two paragraphs (MiniWoB++ ¶, GPQA ¶) were
checked against `A6-result-dumping` lint flags; each contains an interpretive sentence
(e.g. "The roughly 50-point gap to CC-NET reflects, at least in part, a difference in training
paradigm") so the flag is a false positive from the lint's local window, not a real defect —
logged here rather than silently dismissed.

**Section level.** The introduction ends with the question, the contribution list, and a paper
map (§1, final two paragraphs). Each Results subsection (5.1-5.3) opens with the category it
answers. The Discussion (§6) opens by answering the paper's single RQ directly ("Reading Sections
5.1-5.3 together...") before adding qualification — satisfies A10 (no discussion amnesia).

**Transitions checked for a true relation:**
- "while... trailing" (Abstract, §6): contrast is real (verified opposite-direction results in the
  same paragraph).
- "though it is above" (§5.2, MiniWoB++): corrected from an earlier draft error where "though" was
  attached to a false direction; now verified against E042 (34.6% < 40.8%).
- "This qualification bounds the interpretation without erasing the result" (§6): a real logical
  move (narrowing scope, not negating the finding) — kept.
- No instance of "moreover/furthermore/additionally" chains was found (A15 not triggered).

**Old->new flow.** Spot-checked §5.1->§5.2->§5.3 transitions: each subsection's last sentence
introduces the next category implicitly via the running claim about "the same agent" (topic
carried forward), consistent with `information_design.md` §4.

**Result:** no structural flow defects requiring a rewrite. One local error found and fixed during
this audit (the MiniWoB++/Workflow-Guided-Exploration direction error noted above) — corrected in
the draft before this file was written.
