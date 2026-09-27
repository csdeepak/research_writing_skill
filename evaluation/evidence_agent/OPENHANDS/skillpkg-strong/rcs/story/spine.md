# Paper Spine

1. Problem: Building an AI agent that can act on real digital tasks (fixing code, browsing the web, using tools) requires researchers to separately build sandboxing, tool interfaces, and multi-benchmark evaluation harnesses before they can test an idea {C017}.
2. Gap: Evaluation practice is organized as separate per-domain benchmark families with their own harnesses and baselines {C001}{C009}{C010}, and this evidence package contains no verified cross-framework comparison (the source paper's framework table is unreadable here).
3. Question: Can one general-purpose agent, unmodified across domains, be evaluated end to end across software, web, and misc.-assistance tasks through a single open platform and harness {C017}?
4. Approach: OpenHands provides an agent hub of implemented agents and an evaluation framework integrating 15 benchmarks across three categories, MIT-licensed {C017}.
5. Key finding: The same CodeAct agent reaches 26.0% resolve rate on SWE-Bench Lite {C001}, 79.3% on HumanEvalFix {C002}, and 52.0% accuracy on GPQA-diamond {C004}, while trailing baselines on WebArena {C009} and MiniWoB++ {C010}.
6. Meaning: One general agent, unmodified across domains, reaches results described as competitive in several categories without leading every benchmark, consistent with a generalist-platform contribution {C014}{C015}.
7. Main limit: Every number is a single run with no variance {L001}, and two pairs of numbers conflict internally in the source material and are reported, not adjudicated {L002}{C018}{C020}.
