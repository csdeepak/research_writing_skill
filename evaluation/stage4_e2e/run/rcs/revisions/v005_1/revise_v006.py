"""AUTHOR, round v005_1 (workflow step 19): v005 -> v006. Fixes for the round-2 blind review, with each addition offset by
relocation to Appendix A or by tightening untagged text, so the main text stays <= 4,500 words by the lint."""
t = open('.rcs/drafts/v005/paper.md', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in t else '\n'
t = t.replace('\r\n', '\n')
def rep(a, b):
    global t
    assert t.count(a) == 1, a[:90]
    t = t.replace(a, b)

# ---------------- fixes ----------------
# inference:0 -- positioning stated as the authors' statement, not as an inference from the QA result
rep("On static question answering, ASMOS-memory scored below a no-memory baseline and retrieval-augmented generation, so ASMOS is a routing and cost tool {C015}.",
    "In one static question-answering run, ASMOS-memory scored below a no-memory baseline and retrieval-augmented generation; the authors state it is not a question-answering method {C015}.")
# inference:2 -- the 10.0 belongs to the frozen classifier
rep("against 4.8 to 10.0 for scheduled classifier routers over 5 seeds, untested {C009, C010}.",
    "against 4.8 for the best retrained classifier and 10.0 for a frozen one over 5 seeds, untested {C009, C010}.")
# abstract length offsets (abstract stays <= 250 words)
rep("a system must decide whose memory to consult for each query; consulting all (global search) costs tokens on every query {C032}.",
    "a system must decide whose memory to consult per query; consulting all (global search) costs tokens every time {C032}.")
rep("on a deliberately constructed corpus with two agents {C033}.", "on a deliberately constructed two-agent corpus {C033}.")
# inference:3 -- pre-registration record and 'single comparison' scope (new writer caveat L026)
rep("No multiplicity correction is applied because the analysis is a single comparison of A0 with A1 {C028}.",
    "No multiplicity correction is applied because the analysis is a single comparison of A0 with A1 {C028}. The package holds no registry entry or dated protocol for the cited pre-registration, and the other runs' tests (Appendix A) are uncorrected {L026}.")
# inference:5 -- keep the limits adjacent to the 'lowest mean regret' statement
rep("so ASMOS had the lowest mean regret of the routers in this run {C009}.",
    "so ASMOS had the lowest mean regret of the routers in this run, in an untested and unmatched comparison {C009}.")
# inference:4 -- the boundary is one small run, not static QA in general
rep("### 4.5 Boundary: ASMOS-memory does not help on static question answering",
    "### 4.5 Boundary: in one static question-answering run, ASMOS-memory did not help")
rep("and ASMOS-memory does not improve static question answering {L004, C015}.",
    "and ASMOS-memory did not improve static question answering in a single small run {L004, C015}.")
# inference:7 and objective discrepancy -- 'nearly disappeared', untested, consistent with the abstract and Section 4.3 body
rep("### 4.3 RQ3: with ownership frozen, the router did not route and the saving disappeared",
    "### 4.3 RQ3: with ownership frozen, the router did not route and the saving nearly disappeared")
rep("With ownership frozen the router did not route and the saving disappeared, which is consistent",
    "With ownership frozen the router did not route and the saving nearly disappeared (untested), which is consistent")
# inference:1 -- the conclusion no longer asserts the undocumented learning mechanism as shown
rep("routing on ownership learned from verified outcomes used 22.1% fewer",
    "routing on ASMOS's learned ownership (mechanism undocumented) used 22.1% fewer")
# finding:8 / inference:6 -- state the authors' multi-agent caveat instead of 'withheld'
rep("and that a multi-agent validation caveat applies, whose result is withheld here {L007}",
    "and that their multi-agent validation is one seedless run with an imposed partition, not reported here because its result file is missing {L007}")

# ---------------- offsets ----------------
pairs = "Of the 50 pairs, 43 favoured routing, 5 favoured global search and 2 were identical {C002}."
rep(" " + pairs, "")                                     # relocated verbatim to Appendix A
rep("favouring global search, so r runs from -1 to 1 and r = 1 means that every non-zero pair favoured routing {C025}.",
    "favouring global search, so r runs from -1 to 1 and r = 1 means that every non-zero pair favoured routing {C025}. " + pairs)
rep("Tokens per query are pooled over all 10 seeds. ", "")   # stated in Table 1 caption and Section 4.1
rep("We compare four arms on the same queries. Global search (A0) consults every candidate.",
    "The four arms run on the same queries. Global search (A0) consults every candidate.")
rep("Points are the reduction in LLM total tokens per query of A1 relative to A0 in each of 10 seeds; the last row pools all 10 seeds.",
    "Points: reduction in LLM total tokens per query, A1 relative to A0, per seed; the last row pools all 10 seeds.")
rep("Each point is one arm in one seed over 50 queries (seeds 66 to 110); no paired test is available.",
    "Each point is one arm in one seed over 50 queries (seeds 66 to 110).")
rep("or 0.2 (bge-m3) at step 0; classifier lines", "or 0.2 (bge-m3); classifier lines")
rep("The next questions are whether the saving survives an organic workload, larger teams and other answering models, what a paired accuracy test shows, and how ASMOS compares with an online-updated classifier given the same labels.",
    "Next questions: does the saving survive an organic workload, larger teams and other answering models; what does a paired accuracy test show; and how does ASMOS compare with an online-updated classifier given the same labels?")

# abstract offset
rep("For a new topic, ASMOS reached a cumulative regret (", "For a new topic, ASMOS had cumulative regret (")
# further main-text offsets (untagged text only)
rep("We ask four research questions and check one boundary.", "We ask four research questions.")
rep("The boundary check asks whether ASMOS memory helps", "A boundary check asks whether ASMOS memory helps")
rep("The saving's practical weight depends on what is not measured. In absolute terms it is",
    "In absolute terms the saving is")
rep("The gap is one of measurement: what learned ownership saves relative to global search, what it costs in answer quality, and how it behaves when topics change.",
    "The gap is one of measurement: what learned ownership saves against global search, costs in answer quality, and does when topics change.")
rep("what a claim is and how verification outcomes are produced, how topics are assigned, the update rule and prior, whether ownership is learned before or during evaluation, or what a candidate is",
    "what a claim is, how verification outcomes arise, how topics are assigned, the update rule and prior, when ownership is learned relative to evaluation, or what a candidate is")

open('.rcs/drafts/v006/paper.md', 'w', encoding='utf-8', newline='').write(t.replace('\n', nl))
print("ok")
