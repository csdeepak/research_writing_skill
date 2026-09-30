import json, re

def norm(s):
    s = s.replace('’', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', s).strip()

TXT = norm(open('project/paper.txt', encoding='utf-8').read())

# key, authors (first author as cited), year, title as cited, venue as cited, status, quote, location, why
S = [
 ('hong', ['Sirui Hong', 'et al.'], 2023, 'Metagpt: Meta programming for a multi-agent collaborative framework', 'The Twelfth International Conference on Learning Representations (as cited)', 'PEER-REVIEWED',
  'MetaGPT Hong et al. (2023) emphasizing standardized operating procedures', 'paper.txt L901 (App.C)', 'multi-agent framework in the authors\' related work'),
 ('wu', ['Qingyun Wu', 'et al.'], 2023, 'Autogen: Enabling next-gen llm applications via multi-agent conversation framework', 'arXiv preprint arXiv:2308.08155 (as cited)', 'PREPRINT',
  'AutoGen Wu et al. (2023) providing a conversation framework for interactive systems', 'paper.txt L901 (App.C)', 'general agent framework compared in Table 1; execution features characterized in App.C'),
 ('chen24', ['Guangyao Chen', 'et al.'], 2024, 'Autoagents: A framework for automatic agent generation', None, 'PREPRINT',
  'AutoAgents Chen et al. (2024) offer new paradigms for customizable agent architecture', 'paper.txt L901 (App.C)', 'general agent framework'),
 ('yang', ['John Yang', 'et al.'], 2024, 'Swe-agent: Agent-computer interfaces enable automated software engineering', None, 'PREPRINT',
  'SWE-Agent (Yang et al., 2024) highlights the importance of a carefully crafted Agent-Computer Interface (ACI, i.e., specialized tools for particular tasks) in successfully solving complex tasks.', 'paper.txt L196 (Sec.2.3)', 'software-engineering agent and reference system; source of edit utilities'),
 ('zhang24b', ['Yuntong Zhang', 'et al.'], 2024, 'Autocoderover: Autonomous program improvement', None, 'PREPRINT',
  'AutoCodeRover Zhang et al. (2024b) addresses GitHub issues via code search and abstract syntax tree manipulation', 'paper.txt L907 (App.C)', 'software-engineering agent and reference system'),
 ('jimenez', ['Carlos E Jimenez', 'et al.'], 2024, 'SWE-bench: Can Language Models Resolve Real-world Github Issues?', 'The Twelfth International Conference on Learning Representations (as cited)', 'PEER-REVIEWED',
  'SWE-Bench (Jimenez et al., 2024) is designed to assess agents’ abilities in solving real-world GitHub issues, such as bug reports or feature requests.', 'paper.txt L464 (Sec.4.2)', 'benchmark description'),
 ('wang24a', ['Xingyao Wang', 'et al.'], 2024, 'Executable Code Actions Elicit Better LLM Agents', 'ICML (as cited)', 'PEER-REVIEWED',
  'Inspired by CodeAct (Wang et al., 2024a), OpenHands connects an agent with the environment through a core set of general actions.', 'paper.txt L131 (Sec.2.1)', 'CodeAct framework underlying the default agent'),
 ('wang24b', ['Xingyao Wang', 'et al.'], 2024, 'MINT: Evaluating LLMs in Multi-turn Interaction with Tools and Language Feedback', 'ICLR (as cited)', 'PEER-REVIEWED',
  'MINT (Wang et al., 2024b) is a benchmark designed to evaluate agents’ ability to solve challenging tasks through multi-turn interactions using tools and natural language feedback simulated by GPT-4.', 'paper.txt L772 (Sec.4.4)', 'benchmark description'),
 ('zhou23a', ['Shuyan Zhou', 'et al.'], 2023, 'Webarena: A realistic web environment for building autonomous agents', 'The Twelfth International Conference on Learning Representations (as cited)', 'PEER-REVIEWED',
  'WebArena (Zhou et al., 2023a) is a self-hostable, execution-based web agent benchmark that allows agents to freely choose which path to take in completing their given tasks.', 'paper.txt L621 (Sec.4.3)', 'web benchmark; also the reference agent'),
 ('drouin', ['Alexandre Drouin', 'et al.'], 2024, 'Workarena: How capable are web agents at solving common knowledge work tasks?', None, 'PREPRINT',
  'a domain-specific language for browsing introduced by BrowserGym (Drouin et al., 2024)', 'paper.txt L131 (Sec.2.1)', 'source of the browsing action language (title exactly as the project cites it; unverifiable)'),
 ('muen', ['Niklas Muennighoff', 'et al.'], 2024, 'Octopack: Instruction tuning code large language models', None, 'PREPRINT',
  'HumanEvalFix (Muennighoff et al., 2024) tasks agents to fix a bug in a provided function with the help of provided test cases.', 'paper.txt L466 (Sec.4.2.1)', 'benchmark description'),
 ('liu18', ['Evan Zheran Liu', 'et al.'], 2018, 'Reinforcement learning on web interfaces using workflow-guided exploration', 'International Conference on Learning Representations (ICLR) (as cited)', 'PEER-REVIEWED',
  'MiniWoB++ (Liu et al., 2018) is an interactive web benchmark, with built-in reward functions.', 'paper.txt L622 (Sec.4.3)', 'web benchmark'),
 ('liu23', ['Xiao Liu', 'et al.'], 2023, 'Agentbench: Evaluating llms as agents', 'arXiv preprint arXiv: 2308.03688 (as cited)', 'PREPRINT',
  'AgentBench (Liu et al., 2023) evaluates agents’ reasoning and decision-making abilities in a multiturn, open-ended generation setting.', 'paper.txt L771 (Sec.4.4)', 'benchmark description'),
 ('mialon', ['Grégoire Mialon', 'et al.'], 2023, 'GAIA: a benchmark for general AI assistants', 'CoRR, abs/2311.12983 (as cited)', 'PREPRINT',
  'GAIA (Mialon et al., 2023) evaluates agents’ general task-solving skills, covering different real-world scenarios.', 'paper.txt L626 (Sec.4.4)', 'benchmark description'),
 ('rein', ['David Rein', 'et al.'], 2023, 'GPQA: A Graduate-Level Google-Proof Q&A Benchmark', 'arXiv preprint arXiv:2311.12022 (as cited)', 'PREPRINT',
  'GPQA (Rein et al., 2023) evaluates agents’ ability for coordinated tool use when solving challenging graduate-level problems.', 'paper.txt L627 (Sec.4.4)', 'benchmark description and source of human and prompting reference rows'),
 ('tafjord', ['Oyvind Tafjord', 'et al.'], 2021, 'ProofWriter: Generating implications, proofs, and abductive statements over natural language', 'Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021 (as cited)', 'PEER-REVIEWED',
  'ProofWriter (Tafjord et al., 2021) is a synthetic dataset created to assess deductive reasoning abilities of LLMs.', 'paper.txt L773 (Sec.4.4)', 'benchmark description'),
 ('pan23', ['Liangming Pan', 'et al.'], 2023, 'Logic-lm: Empowering large language models with symbolic solvers for faithful logical reasoning', 'arXiv preprint arXiv:2305.12295 (as cited)', 'PREPRINT',
  'Same as Logic-LM (Pan et al., 2023), we focus on the most challenging subset, which contains 600 instances requiring 5-hop reasoning.', 'paper.txt L773 (Sec.4.4)', 'reference system with a symbolic solver'),
 ('zhang24a', ['Yizhe Zhang', 'et al.'], 2024, 'Probing the multi-turn planning capabilities of llms via 20 question games', None, 'PREPRINT',
  'Entity Deduction Arena (EDA) (Zhang et al., 2024a) evaluates agents’ ability to deduce unknown entities through strategic questioning, akin to the 20 Questions game.', 'paper.txt L774 (Sec.4.4)', 'benchmark description'),
 ('li23b', ['Jinyang Li', 'et al.'], 2023, 'Can LLM already serve as a database interface? a BIg bench for large-scale database grounded text-to-SQLs', 'Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track (as cited)', 'PEER-REVIEWED',
  'BIRD (Li et al., 2023b) is a benchmark for text-to-SQL tasks (i.e., translate natural language into executable SQL) aimed at realistic and large-scale database environments.', 'paper.txt L617 (Sec.4.2)', 'benchmark description'),
 ('tang24b', ['Xiangru Tang', 'et al.'], 2024, 'ML-Bench: Evaluating large language models and agents for machine learning tasks on repository-level code', None, 'PREPRINT',
  'ML-Bench (Tang et al., 2024b) evaluates agents’ ability to solve machine learning tasks across 18 GitHub repositories.', 'paper.txt L550 (Sec.4.2)', 'benchmark description'),
 ('tang24c', ['Xiangru Tang', 'et al.'], 2024, 'BioCoder: a benchmark for bioinformatics code generation with large language models', 'Bioinformatics, 40 (Supplement_1) (as cited)', 'PEER-REVIEWED',
  'BioCoder (Tang et al., 2024c) is a repository-level code generation benchmark that evaluates agents’ performance on bioinformatics-related tasks', 'paper.txt L556 (Sec.4.2)', 'benchmark description'),
 ('patil', ['Shishir G. Patil', 'et al.'], 2023, 'Gorilla: Large language model connected with massive apis', 'arXiv preprint arXiv:2305.15334 (as cited)', 'PREPRINT',
  'Gorilla APIBench (Patil et al., 2023) evaluates agents’ abilities to use APIs.', 'paper.txt L552 (Sec.4.2)', 'benchmark description and finetuned reference row'),
 ('zhuang', ['Yuchen Zhuang', 'et al.'], 2024, 'Toolqa: A dataset for llm question answering with external tools', 'Advances in Neural Information Processing Systems, 36 (as cited)', 'PEER-REVIEWED',
  'ToolQA (Zhuang et al., 2024) evaluates agents’ abilities to use external tools.', 'paper.txt L554 (Sec.4.2)', 'benchmark description'),
 ('zhuge24', ['Mingchen Zhuge', 'et al.'], 2024, 'Language agents as optimizable graphs', 'arXiv preprint arXiv:2402.16823 (as cited)', 'PREPRINT',
  'GPTSwarm (Zhuge et al., 2024) pioneers the use of optimizable graphs to construct agent systems, unifying language agent frameworks through modularity.', 'paper.txt L252 (Sec.3)', 'source of the GPTSwarm agent'),
 ('xia', ['Chunqiu Steven Xia', 'et al.'], 2024, 'Agentless: Demystifying llm-based software engineering agents', 'arXiv preprint (as cited)', 'PREPRINT',
  'Agentless (Xia et al., 2024)', 'paper.txt Tab.3 (L312)', 'reference system on SWE-Bench Lite'),
 ('pan24', ['Jiayi Pan', 'et al.'], 2024, 'Autonomous evaluation and refinement of digital agents', 'arXiv preprint arXiv:2404.06474 (as cited)', 'PREPRINT',
  'Auto Eval & Refine Pan et al. (2024), an agent retry-on-error strategy with Reflexion Shinn et al. (2024) prompts and task completion reward models', 'paper.txt L893 (App.A)', 'reference system on WebArena and planned browsing component'),
 ('lai', ['Hanyu Lai', 'et al.'], 2024, 'Autowebglm: Bootstrap and reinforce a large language model-based web navigating agent', 'arXiv preprint arXiv:2404.03648 (as cited)', 'PREPRINT',
  'Trained 7B with human/agent hybrid annotation', 'paper.txt Tab.5 (L568)', 'trained reference system on WebArena'),
 ('xu', ['Yiheng Xu', 'et al.'], 2023, 'Lemur: Harmonizing natural language and code for language agents', 'arXiv preprint arXiv:2310.06830 (as cited)', 'PREPRINT',
  'Lemur-chat-70b', 'paper.txt Tab.5 (L568)', 'reference system on WebArena'),
 ('patel', ['Ajay Patel', 'et al.'], 2024, 'Large language models can self-improve at web agent tasks', 'arXiv preprint arXiv:2405.20309 (as cited)', 'PREPRINT',
  'Trained 72B with self-improvement synthetic data', 'paper.txt Tab.5 (L568)', 'trained reference system on WebArena'),
 ('humph', ['Peter C Humphreys', 'et al.'], 2022, 'A data-driven approach for learning to control computers', 'International Conference on Machine Learning, pp. 9466-9482. PMLR (as cited)', 'PEER-REVIEWED',
  'Trained specialist model with RL and human annotated BC', 'paper.txt Tab.5 (L586)', 'trained specialist reference on MiniWoB++ (CC-NET)'),
 ('chen21', ['Mark Chen', 'et al.'], 2021, 'Evaluating large language models trained on code', 'arXiv preprint arXiv:2107.03374 (as cited)', 'PREPRINT',
  'We follow the setup from Muennighoff et al. (2024) using pass@k (Chen et al., 2021).', 'paper.txt L466 (Sec.4.2.1)', 'metric definition source'),
 ('shinn', ['Noah Shinn', 'et al.'], 2024, 'Reflexion: Language agents with verbal reinforcement learning', 'Advances in Neural Information Processing Systems, 36 (as cited)', 'PEER-REVIEWED',
  'Auto Eval & Refine Pan et al. (2024), an agent retry-on-error strategy with Reflexion Shinn et al. (2024) prompts', 'paper.txt L893 (App.A)', 'prompting method inside a reference web agent'),
 ('gravitas', ['Significant Gravitas'], 2023, 'Auto-gpt: An autonomous gpt-4 experiment', None, 'DOCUMENTATION',
  'Notable works such as Auto-GPT Gravitas (2023) harness LLMs for task completion by decomposing user goals into executable steps.', 'paper.txt L901 (App.C)', 'general agent and GAIA reference system'),
 ('chase', ['Harrison Chase'], 2022, 'LangChain', None, 'DOCUMENTATION',
  'LangChain and LangGraph Chase (2022) provide foundational building blocks with basic runtime support', 'paper.txt L902 (App.C)', 'agent framework'),
 ('crewai', ['CrewAI'], 2024, 'CrewAI', None, 'DOCUMENTATION',
  'CrewAI CrewAI (2024) focuses on orchestrating multi-agent communications', 'paper.txt L902 (App.C)', 'agent framework'),
]

srcs = []
ids = {}
for i, (k, au, yr, title, venue, status, quote, loc, why) in enumerate(S, 1):
    assert norm(quote) in TXT, 'quote not found for ' + k + ': ' + quote[:70]
    sid = 'SRC-%03d' % i
    ids[k] = sid
    srcs.append({
        'id': sid, 'title': title, 'as_cited': title, 'title_status': 'as_cited' if k != 'drouin' else 'unverifiable',
        'authors': au, 'year': yr, 'venue': venue, 'doi': None, 'url': None,
        'publication_status': status, 'peer_review_known': status == 'PEER-REVIEWED', 'domain': 'LLM agents',
        'level': 2, 'verification': {'method': 'user_supplied_file', 'date': '2026-09-29', 'verified_by': 'agent', 'retraction_checked': False},
        'read_depth': 'abstract',
        'establishes': [{'statement': 'How the OpenHands paper describes this work: ' + why, 'support_quote': quote, 'location': loc, 'strength': 'description by the citing authors only'}],
        'why_useful': why,
        'informs_sections': ['Introduction', 'Related work', 'Method', 'Results'],
        'evidence_quality': 'low',
        'limitations': 'Registered from the project\'s own reference list and text; the cited work itself was not read (no web). Publication status is taken from the project\'s citation, or set conservatively to PREPRINT when the project gives no venue. Cite only for how the OpenHands paper describes it.',
        'permitted_use': ['content_citation'],
        'citation_count': None,
    })
json.dump({'sources': srcs}, open('.rcs/corpus/source_registry.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(ids, open('.rcs/_src_ids.json', 'w'), indent=1)
print(len(srcs), 'sources')
