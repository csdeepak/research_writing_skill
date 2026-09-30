# Step 17 -- Scientific overclaim audit (draft v001)

Checked every item in `anti_patterns.md` section B against the draft. For each flag found, the
repair applied was always (a) downgrade the language or (b) add the missing scope -- never (c)
search for post-hoc support or strengthen the evidence.

| ID | Check | Found in draft? | Action |
|----|-------|------------------|--------|
| B1 Exaggerated novelty | "novel/first/unprecedented" without search-scoped basis | Found once in an early revision ("is the first to make... comparable"); rewritten to "closing a gap left by all three prior efforts examined" (Intro), and Background's "novel accelerator architectures" changed to "non-standard" | Fixed (2 instances) |
| B2 Unsupported superiority | "outperforms/superior/better" without a measured comparison | None found -- the draft makes no cross-submission performance ranking (the source evidence has no comparable per-submission accuracy/latency/energy numbers to rank; see missing_evidence.json MISS-001) | none |
| B3 Unbacked SOTA | "state-of-the-art"/SOTA without benchmark+set+date | Word never used in the draft | none |
| B4 Proof language | "prove(s)/demonstrate conclusively/establish" for empirical results | 2 instances caught by lint (`shows that`, `demonstrate`) on the C006 interpretation claim; both rewritten to "is consistent with" / "show" (non-`that` form) -- see claim_audit.md | Fixed |
| B5 Causal from correlational | causal verbs on observational evidence | "because" used only for methodological/logical consequence, not for an unearned causal claim about the field (checked in flow_audit.md); no instance of "causes/leads to/drives/due to" describing the v0.5 results | none |
| B6 Over-generalization | claim scope > evidence conditions | C006 and C012 explicitly scope to "the case actually tested" / "the three benchmarking efforts examined"; Results P5 explicitly states 3 things the round does NOT establish (L001, L005); Conclusion repeats the single-round scope | none outstanding |
| B7 Selective reporting | negative results omitted | None omitted -- see claim_audit.md's negative-result-coverage section | none |
| B8 Benchmark cherry-picking | subset shown with no selection rule | Table 1 shows all 4 benchmarks, Table 2 shows all 5 submissions -- both complete enumerations, stated as such in their captions | none |
| B9 Vague significance | "significant(ly)" without a test; unquantified intensifiers | The word "significant(ly)" is never used anywhere in the draft (the source evidence has no statistical test to name, so the word is avoided entirely rather than used loosely). No unquantified intensifier ("dramatically/substantially/huge/massive") appears; every magnitude claim gives the actual number instead | none |
| B10 Unequal baselines | proposed method tuned, baselines at defaults | Not applicable -- this paper reports a benchmark suite's own first-round adoption, not a proposed-method-vs-baseline comparison | n/a |
| B11 Explanation vs. speculation blur | mechanistic "because" with no isolating experiment | The one mechanistic attribution (the accelerator vendor's own account of its microarchitecture) is explicitly marked as "which the authors attribute to..." rather than presented as this paper's own verified mechanism | none |
| B12 Unattributed gains | bundled changes, gain attributed to one idea without ablation | Not applicable -- no ablation-style comparison is made anywhere in the draft | n/a |
| B13 Invented reviewer expectations | "reviewers will expect/the community agrees" | Not present | none |
| B14 Decorative/misattributed citation | citation doesn't support the sentence | Checked in `citation_audit.json` -- 0 found | none |
| B15 Spin in abstract | abstract emphasizes secondary positives over a null primary result | The Abstract's primary result (5 submissions, both divisions, 5 categories) is exactly the paper's central finding (spine line 5), not a secondary one; the Abstract's own last sentence states the single-round scope limit rather than omitting it | none |
| B16 Mathiness | equations adding notation without precision | No equations in the draft | n/a |
| B17 Hedge inflation | every sentence hedged so real uncertainty can't be told apart | Hedging ("is consistent with", "suggests") is used specifically for the 2 claims typed `interpretation`/`derived` (C002, C006, C012); the `measured` claims (C001, C003, C004, C005) are stated plainly, without hedges, since their evidence supports that strength -- hedging is differential, not blanket | none |

## Generalization-scope check (population / dataset / scale / conditions)
Re-read every sentence carrying C005, C006, C007, C008, or C012 (the claims resting on the v0.5
round) and confirmed the stated scope never exceeds "the v0.5 round" / "the case tested" / "the
three benchmarking efforts examined" -- no sentence generalizes to "TinyML benchmarks in general"
or "all future rounds."

**Result: 2 flags found and fixed (B1 x2, B4 x2 counted once each under their rule); repaired by
downgrading language in both cases; 0 flags left open; 0 cases resolved by strengthening
evidence.**
