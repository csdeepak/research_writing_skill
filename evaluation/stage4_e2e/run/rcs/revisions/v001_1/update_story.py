"""AUTHOR, step 19 (round v001_1): update the story graph and spine before regenerating prose."""
import json
from pathlib import Path

p = Path(".rcs/story/story_graph.json")
g = json.loads(p.read_text(encoding="utf-8"))
N = {n["id"]: n for n in g["nodes"]}
N["N01"]["text"] = ("When LLM agents share a memory, a system must decide for each query which agent's memory to consult; "
                    "the study tests this with two agents.")
N["N04"]["claims"] = ["C033"]
N["N07"]["text"] = "RQ3: Does the saving depend on ownership having moved from its prior (frozen-ownership ablation)?"
N["N08"]["text"] = ("RQ4: When a new topic appears, how quickly (cumulative regret in route@1) does ownership-based routing "
                    "reach the new owner, compared with supervised classifier routers?")
N["N09"]["claims"] = ["C032", "C039"]
N["N13"]["claims"] = [c for c in N["N13"]["claims"] if c != "C035"]
N["N18"]["claims"] = ["C030", "C036"]
N["N21"]["text"] = ("The frozen-ownership ablation collapses to global search, so it shows that the saving requires routing on "
                    "ownership above the threshold, not that the evolution process itself is needed (RQ3 answered at low confidence).")
N["N22"]["text"] = ("In the tested new-topic runs ASMOS reached the new owner with no retraining and had the lowest mean regret of "
                    "the routers tried, without a test and without a like-for-like online baseline; it is not a question-answering method.")
N["N25"]["text"] = ("Accuracy is lower under routing by 1 to 2 of 50 questions per seed, untested and with undocumented grading; the "
                    "ablation contrasts routing with no routing. (limitations L012, L013, L023)")
N["N26"]["text"] = ("Author-listed caveats (tau tuned in-corpus, descoped items, unconfirmed early embedder, interval set by query "
                    "heterogeneity) and scope caveats: two agents, token accounting of the answering call only, no online classifier "
                    "baseline. (limitations L001, L006, L007, L008, L021, L022, L024)")
N["N27"]["text"] = ("Where a workload has topic-specific owners and an accuracy cost of unknown size is acceptable, learned ownership "
                    "is a candidate way to lower per-query LLM usage; the whole-system cost ledger is not measured.")
p.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

Path(".rcs/story/spine.md").write_text("""# Paper spine (AUTHOR, draft v002 after blind review v001_1; audience mode B)

1. **Problem.** When LLM agents share a memory, a system must decide for each query which agent's memory to consult; consulting all of them (global search) costs tokens on every query. The study measures this with two agents. {C032} {C033} {L024}
2. **Gap.** Whether routing on ownership learned from verified outcomes cuts that cost, and at what cost in answer quality, has not been measured against global search; no verified literature is available, so related work is marked as missing. {C033}
3. **Question.** Does routing queries to a learned owner cut LLM token usage relative to global search, what does it do to accuracy and answerability, does the saving depend on ownership having moved from its prior, and how quickly does routing reach the owner of a new topic? {C001} {C007} {C005} {C009}
4. **Approach.** Compare four routing arms (global search, learned ownership, ownership frozen at its prior, similarity routing) on a constructed 50-query two-agent corpus over 10 seeds, with a bootstrap interval and a one-sided signed-rank test, then a new-topic run against scheduled classifier routers and a static question-answering check. {C032} {C004} {C009} {C013}
5. **Key finding.** On the constructed corpus, learned-ownership routing used 22.1% fewer LLM tokens per query than global search (95% CI 17.9% to 26.3%); answerability was equal, and accuracy was lower in every recorded seed by an amount that cannot be bounded. {C001} {C002} {C006} {C007}
6. **Meaning.** The saving requires routing on ownership above the threshold (the frozen-ownership ablation collapses to global search); ASMOS reached a new topic's owner without retraining in the tested runs; it is a routing and cost tool, not a question-answering method. {C005} {C009} {C015}
7. **Main limit.** The corpus is deliberately constructed and has two agents, so the saving is not a rate for organic or larger workloads; the accuracy difference is untested; the ablation cannot single out ownership evolution. {L004} {L024} {L012} {L013}
""", encoding="utf-8")
print("ok")
