# Step 15 — Figure/table audit

No images are used, per TASK.md ("Tables may be written in Markdown. No images."). One table is
used in the main text: **Table 1** (§4, benchmark summary).

**Card (retrospective, per `figure_table_rules.md` §1):**
```
id: TABLE-1
purpose: let the reader look up, per benchmark, the instance count, shot setting, and the named
         comparison systems before any result number is given
rq: N05 (the paper's single RQ)
takeaway: "OpenHands is evaluated on nine safely-attributable benchmarks across three categories,
          each against named baselines already established in the literature."
claims: [C001,C002,C004,C005,C006,C007,C009,C010,C011,C012,C013]
evidence: [E010,E017,E020,E030,E040,E050,E053,E060,E070,E080,E090,E100,E102]
type: lookup table (per figure_table_rules.md §2: exact values / many attributes -> table)
comparison_the_eye_must_make: which benchmarks belong to which category, and which named systems
                               each OpenHands result is compared against in §5
non_conclusions: "does not itself show OpenHands's scores; scores are in the §5 prose, per benchmark"
honesty_checks: {all_conditions_shown: true (all 9 safely-attributable benchmarks listed;
                 4 excluded ones stated explicitly with a reason), cherry_picked: false}
placement: "§4 Evaluation Setup, introduced by name ('Table 1 summarizes...') before the table"
caption: "Benchmarks reported in this paper, by category."
```

**Integration check.** Table 1 is referred to by number before it appears ("Table 1 summarizes the
benchmarks..."), and is referenced again by number in §5.1 ("Against the compared systems in Table
1...") and §5.2. Its takeaway (which systems are compared, by category) is stated in prose in the
paragraph introducing it. No `FIGURE_NOT_EXPLAINED` raised.

**Table 1 mechanics (figure_table_rules.md §6).** Numbered, descriptive caption; columns are the
attributes a reader compares (category, benchmark, instances, shot setting, compared systems);
missing/unspecified shot settings marked "—"; abbreviations (OS) spelled out in the preceding
prose paragraph, not only in the table.
