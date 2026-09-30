"""AUTHOR, round 2 step 21: v004 -> v005 length fit (relocation to Appendix A, repetition removal, tightening).
Claims, author-stated limitations, author rationale, intervals and denominators are kept; checked with claim_invariance.py."""
t = open('.rcs/drafts/v004/paper.md', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in t else '\n'
t = t.replace('\r\n', '\n')
def rep(a, b):
    global t
    assert t.count(a) == 1, a[:90]
    t = t.replace(a, b)

# --- relocations to Appendix A (text kept verbatim) ---
formula = ("Over the non-zero pairs, r = (T+ - T-)/(T+ + T-), where T+ and T- are the rank sums of the pairs favouring routing and "
           "favouring global search, so r runs from -1 to 1 and r = 1 means that every non-zero pair favoured routing {C025}.")
rep(formula + " ", "(Appendix A gives its definition.) ")
spec = ("The package does not diagnose why ASMOS-memory scored below No-Memory. One untested possibility is that the memory context it adds "
        "displaces or distracts from what the answering model would otherwise answer; whether a similar effect contributes to A1's lower "
        "accuracy is also untested {C040}.")
rep(" " + spec, " Why ASMOS-memory scored below No-Memory is not diagnosed (Appendix A).")
rep("No p-values are recorded for these comparisons {L016}.",
    "No p-values are recorded for these comparisons {L016}. " + spec + "\n\nEffect-size definition. " + formula)

# --- repetition removed (each statement remains elsewhere, tagged) ---
rep("The authors exclude one embedder cell (bge-small in a new-topic replication) because its run fell back to a hash embedder and produced a degenerate regret {L009}. ", "")  # kept in 6.1
rep(" The authors state that ownership asymmetry does not emerge organically because the corpus is deliberately constructed {L004}.", "")  # kept in Abstract, 6.1, 7
rep("Figure 2 shows A1 below A0 in each of the five seeds. ", "")

# --- tightening (no number, hedge or scope qualifier changed) ---
rep("When LLM agents share a semantic memory, every query raises a routing question: whose memory should be consulted? The default is global search, which consults every candidate.",
    "When LLM agents share a semantic memory, each query raises a question: whose memory to consult? The default, global search, consults every candidate.")
rep("On the test corpus used below, which has two agents, global search", "On the two-agent test corpus used below, global search")
rep("No verified literature was available for this paper, so we cannot place the work", "Without verified literature, we cannot place the work")
rep("RQ4: when a new topic appears, how quickly does ownership-based routing reach its owner, measured by cumulative regret in route@1, compared with supervised classifier routers?",
    "RQ4: how quickly does ownership-based routing reach the owner of a new topic (cumulative regret in route@1), compared with supervised classifier routers?")
rep("The package does not specify the remaining mechanics, and we do not reconstruct them: what counts as a claim and how verification outcomes are produced, how a query's topic is assigned, the update rule and prior, whether ownership is learned before or during the evaluation queries, and what a candidate is",
    "The package does not specify, and we do not reconstruct, what a claim is and how verification outcomes are produced, how topics are assigned, the update rule and prior, whether ownership is learned before or during evaluation, or what a candidate is")
rep("The classes are labelled Q1 to Q5 in the result file and are not described", "The classes, Q1 to Q5 in the result file, are not described")
rep("The four systems are No-Memory, RAG, ASMOS-memory alone and ASMOS combined with RAG, each run once on 24 question-answering items that the project draws from a benchmark it names RULER (its static single-agent question-answering set), with one uniform answering call and gpt-4o-mini {C013}.",
    "No-Memory, RAG, ASMOS-memory alone and ASMOS combined with RAG each ran once, with gpt-4o-mini and one uniform answering call, on 24 static single-agent question-answering items that the project draws from a benchmark it names RULER {C013}.")
rep("The vertical axis is route@1 on the new topic (0 to 1) and the horizontal axis is the step (0 to 10); lines are means over 5 seeds, and ASMOS starts at 0.0 (all-mpnet-base-v2) or 0.2 (bge-m3) at step 0; classifier lines are from the all-mpnet-base-v2 run and are the same in the bge-m3 run.",
    "Axes: route@1 on the new topic (0 to 1) against step (0 to 10); lines are means over 5 seeds; ASMOS starts at 0.0 (all-mpnet-base-v2) or 0.2 (bge-m3) at step 0; classifier lines, from the all-mpnet-base-v2 run, are the same with bge-m3.")
rep("Whether the saving matters in practice depends on what this study does not measure. ", "The saving's practical weight depends on what is not measured. ")
rep("Additional caveats are ours, not the authors' concessions.", "Additional caveats are ours, not the authors'.")

# --- round-2 tightening, second pass ---
rep(" The authors state that the ownership verification is deterministic and not judged by an LLM {L007}.", "")  # kept in 6.1
rep("a system must decide which agent's memory to consult for each query; consulting all of them (global search)",
    "a system must decide whose memory to consult for each query; consulting all (global search)")
rep("not a new method positioned against prior work. It makes four contributions, each tied to a result:",
    "not a new method positioned against prior work, and makes four contributions:")
rep("**Table 1.** Global search (A0) and ownership frozen at its prior (A2) cost about the same, learned-ownership routing (A1) costs fewer tokens per query with equal answerability but lower accuracy, and similarity routing (A3) is cheapest but answers far fewer queries.",
    "**Table 1.** A0 and A2 cost about the same; A1 costs fewer tokens per query with equal answerability but lower accuracy; A3 is cheapest but answers far fewer queries.")
rep("**Figure 2.** Learned-ownership routing (A1) answered 0.68 to 0.70 of questions correctly in each of five seeds, below global search (A0) at 0.72 in every seed, while ownership frozen at its prior (A2) matched A0 and similarity routing (A3) reached 0.54 to 0.56.",
    "**Figure 2.** Learned-ownership routing (A1) answered 0.68 to 0.70 of questions correctly in each of five seeds, below global search (A0) at 0.72 in every seed, while A2 matched A0 and A3 reached 0.54 to 0.56.")
rep("which standard definitions of the two metrics do not allow", "which standard definitions do not allow")
rep("How it scales with memory size and team size, and what verification, ownership updates and embeddings cost, are not measured",
    "Scaling with memory and team size, and the cost of verification, ownership updates and embeddings, are not measured")
rep("a convergence and sample-efficiency hypothesis that was tested; its result file is not in the package and its reporting is undecided",
    "a tested convergence and sample-efficiency hypothesis whose result file is not in the package and whose reporting is undecided")

# --- round-2 tightening, third pass ---
rep("Without any retraining, the share of new-topic queries that ASMOS sends first to the right owner rises gradually over the steps, whereas a frozen classifier stays at zero and the retrained classifiers stay at zero",
    "Without retraining, the share of new-topic queries ASMOS sends first to the right owner rises gradually, whereas a frozen classifier stays at zero and retrained classifiers stay at zero")
rep("Table 1 gives the four arms side by side.", "Table 1 compares the four arms.")
rep("because which agent is chosen and how many candidates are passed depend on similarity",
    "because the chosen agent and the number of candidates passed depend on similarity")
rep("The gap we address is one of measurement: what learned ownership saves relative to global search, what it costs in answer quality, and how it behaves when the set of topics changes.",
    "The gap is one of measurement: what learned ownership saves relative to global search, what it costs in answer quality, and how it behaves when topics change.")

open('.rcs/drafts/v005/paper.md', 'w', encoding='utf-8', newline='').write(t.replace('\n', nl))
