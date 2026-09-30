import json, re, hashlib

ROOT = '.'
SRC = {
    'p': 'project/paper.txt',
    'r1': 'project/README_1.md',
    'r2': 'project/README_2.md',
}
_txt = {}


def norm(s):
    s = s.replace('’', "'").replace('“', '"').replace('”', '"').replace('→', '->')
    return re.sub(r'\s+', ' ', s).strip()


def src_text(k):
    if k not in _txt:
        _txt[k] = norm(open(SRC[k], encoding='utf-8').read())
    return _txt[k]


def Q(k, *quotes):
    """verbatim quotes, asserted present in the source"""
    out = []
    for q in quotes:
        assert norm(q) in src_text(k), 'QUOTE NOT FOUND in %s: %s' % (k, q[:80])
        out.append('"' + q + '"')
    return 'Verbatim: ' + ' | '.join(out)


items = []
ids = {}


def E(key, kind, summary, loc, anchor, strength='soft', value=None, cond=None, notes='', status='ok', **extra):
    eid = 'E%03d' % (len(items) + 1)
    ids[key] = eid
    it = {'id': eid, 'kind': kind, 'summary': summary, 'locator': {'path': SRC[loc], 'anchor': anchor},
          'strength': strength, 'status': status}
    if value is not None:
        it['value'] = value
    if cond is not None:
        it['conditions'] = cond
    if notes:
        it['notes'] = notes
    it.update(extra)
    items.append(it)
    return eid


TAB_NOTE = ' Table read from extracted text; layout damaged by extraction, but row order is recoverable.'

# ---------------------------------------------------------------- rationale (motivation)
E('mot_ideal', 'rationale_stated', 'Authors motivate software as the interface through which AI agents act on the world.', 'p', 'L17 (Sec.1)',
  notes=Q('p', 'Given the power of software, as well as the existing tooling around its efficient development, use, and deployment, it provides the ideal interface for AI agents to interact with the world in complex ways.'))
E('mot_challenge', 'rationale_stated', 'Authors state that developing and evaluating agents has become challenging as agents become more capable, and pose three concrete questions: creating and modifying code in complex systems, gathering information on the fly, and keeping development safe for the user\'s system.', 'p', 'L11 (Sec.1)',
  notes=Q('p', 'As AI agents become capable of tackling complex problems, their development and evaluation have also become challenging.',
          'How can we enable agents to effectively create and modify code in complex software systems?',
          'How can we provide them with tools to gather information on-the-fly to debug problems or gather task-requisite information?',
          'How can we ensure that development is safe and avoids negative side effects on the users’ systems?'))
E('mot_evalbreadth', 'rationale_stated', 'Authors state their goal (general digital agents acting through software interfaces) and the reason for evaluating beyond software engineering: a software agent should also handle web browsing and auxiliary tasks.', 'p', 'L274 (Sec.4.1)',
  notes=Q('p', 'We recognize that a software agent should excel not only in code editing but also in web browsing and various auxiliary tasks, such as answering questions about code repositories or conducting online research.',
          'In OpenHands, our goal is to develop general digital agents capable of interacting with the world through software interfaces'))

# ---------------------------------------------------------------- rationale (design)
E('des_actions', 'rationale_stated', 'Authors state why the three core actions and a programming-language action space were chosen.', 'p', 'L131, L136 (Sec.2.1)',
  notes=Q('p', 'These actions were chosen to provide a comprehensive yet flexible set of primitives covering most tasks performed by human software engineers and analysts.',
          'and flexible enough to perform any task with tools in different forms (e.g., Python function, REST API, etc.) while being reliable and easy to maintain (Wang et al., 2024a)'))
E('des_docker', 'rationale_stated', 'Authors state that arbitrary Docker image support lets agents run on different operating systems and software environments.', 'p', 'L194 (Sec.2.2)',
  notes=Q('p', 'OpenHands allows agents to run on arbitrary operating systems with different software environments by supporting runtime based on arbitrary docker images.'))
E('des_skills', 'rationale_stated', 'Authors state why the AgentSkills library exists and the inclusion criteria for adding a skill.', 'p', 'L196-L198 (Sec.2.3)',
  notes=Q('p', 'creating, maintaining, and distributing a wide array of tools can be a daunting engineering challenge, especially when we want to make these tools available to different agent implementations',
          'The ease of defining a Python function as a tool lowers the barrier for community members to contribute new tools to the library.',
          'We only add a new skill when: (1) it is not readily achievable for LLM to write code directly (e.g., edit code and replace certain lines), and/or (2) it involves calling an external model'))
E('des_deleg', 'rationale_stated', 'Authors give the example that a generalist agent with limited browsing support delegates web tasks to a specialized browsing agent.', 'p', 'L201 (Sec.2.4)',
  notes=Q('p', 'the generalist CodeActAgent, with limited support for web-browsing, can use AgentDelegateAction to delegate web browsing tasks to the specialized BrowsingAgent to perform more complex browsing activity'))
E('des_micro', 'rationale_stated', 'Authors state that micro agents are meant to lower the barrier to agent development.', 'p', 'L253 (Sec.3)',
  notes=Q('p', 'It is designed to lower the barrier to agent development, where community members can share specialized prompts that work well for their particular use cases.'))
E('des_itest', 'rationale_stated', 'Authors state why integration tests with mocked LLM calls were built (cost, slowness, non-determinism).', 'p', 'L911 (App.E)',
  notes=Q('p', 'running them for every code changes can be prohibitively slow and expensive',
          'Addressing the challenge of non-determinism in large language models (LLMs) and the associated high costs, the framework intercepts all LLM calls and supplies predefined responses based on exact prompt matches.'))
E('des_evalprot', 'rationale_stated', 'Authors state the comparison protocol (open-source reproducible baselines without benchmark-specific manual prompt engineering) and that SWE-bench Lite is the default subset for cost saving.', 'p', 'L257 (Sec.4), L464 (Sec.4.2)',
  notes=Q('p', 'we compare OpenHands to open-source reproducible baselines that do not perform manual prompt engineering specifically based on the benchmark content',
          'We default to use this subset for testing for cost-saving consideration.'))
E('des_eth', 'rationale_stated', 'Authors state how they expect OpenHands to help mitigate agent risks: systematic evaluation, human-agent interaction with oversight, and access to agents for safety research.', 'p', 'L896-L899 (App.B)',
  notes=Q('p', 'Enabling systematic evaluation of these agents, which can identify and address risks before they are widely deployed.',
          'Facilitating human-agent interaction rather than allowing agents to operate autonomously without oversight.'))
E('des_bench', 'rationale_stated', 'Authors give reasons for three benchmark-specific adaptations: removing BioCoder context prompts, using Logic-LM logical forms for ProofWriter, and a concise-answer instruction for WebArena.', 'p', 'L556 (Sec.4.2), L773 (Sec.4.4), L1332 (App.K)',
  notes=Q('p', 'in this study, we have removed them to demonstrate the capability of OpenHands to perform context retrieval',
          'To minimize the impact of potential errors in semantic parsing, we use the logical forms provided by Logic-LM.',
          'we add the following instruction to let the agent reply with only a concise answer string when messaging the user to prevent the agent from failing the test due to extra text'))
E('des_multiact', 'rationale_stated', 'Authors state that the browsing agent may predict several actions per turn to save turns on routine same-page workflows.', 'p', 'L1284 (App.K)',
  notes=Q('p', 'This could save turns for common workflows that consist of a sequence of actions on the same page without any observation change'))

# ---------------------------------------------------------------- prior work (as characterized by the project)
E('prior_frameworks', 'external_fact', 'Authors characterize existing open agent frameworks as generally including interfaces, environments and interaction mechanisms.', 'p', 'L11 (Sec.1)',
  notes=Q('p', 'These agent frameworks generally include: 1) interfaces through which agents interact with the world (such as JSON-based function calls or code execution), 2) environments in which agents operate, and 3) interaction mechanisms for human-agent or agent-agent communication.'))
E('prior_exec', 'external_fact', 'Authors characterize the code-execution support of AutoGen and CrewAI in their related work.', 'p', 'L902 (App.C)',
  notes=Q('p', 'AutoGen Wu et al. (2023) advances beyond basic frameworks by implementing Python and bash execution capabilities, though with stateless command execution, while frameworks like CrewAI offer sandboxed but limited code interpreter features.'))
E('prior_swe', 'external_fact', 'Authors characterize AutoCodeRover and SWE-Agent as addressing GitHub issue fixing.', 'p', 'L907 (App.C)',
  notes=Q('p', 'AutoCodeRover Zhang et al. (2024b) addresses GitHub issues via code search and abstract syntax tree manipulation.',
          'SWE-Agent Yang et al. (2024) integrates LLMs for automated Github issue fixing, streamlining software engineering.'))
E('prior_table1', 'external_fact', 'Table 1 lists 12 frameworks with a Domain column: nine General, AutoCodeRover and SWE-Agent as SWE, OpenHands as General; the feature marks in the other columns were lost in extraction.', 'p', 'L209-L250 (Tab.1)',
  value={'general_domain_frameworks_excluding_openhands': 9, 'swe_domain_frameworks': 2},
  notes='Feature columns (GUI, tool library, sandbox, browser, multi-agent, human-AI, AgentHub, evaluation framework, agent QC) have no recoverable cell values; see missing_evidence M001. Footnote: "* No native support. Third-party commercial options are available."')
E('prior_swe_agent_aci', 'external_fact', 'Authors cite SWE-Agent as highlighting the importance of a carefully crafted agent-computer interface.', 'p', 'L196 (Sec.2.3)',
  notes=Q('p', 'SWE-Agent (Yang et al., 2024) highlights the importance of a carefully crafted Agent-Computer Interface (ACI, i.e., specialized tools for particular tasks) in successfully solving complex tasks.'))

# ---------------------------------------------------------------- method / platform design
E('m_state', 'method_detail', 'The state holds the event stream (chronological past actions and observations, including user interactions) plus auxiliary information such as accumulated LLM cost and delegation metadata.', 'p', 'L130 (Sec.2.1)',
  notes=Q('p', 'A key component of this state is the event stream, which is a chronological collection of past actions and observations, including the agent’s own actions and user interactions (e.g., instructions, feedback).'))
E('m_abstraction', 'method_detail', 'An agent is a function from event history to an action; the runtime maps an action to an observation; a new agent implements a step function over the state.', 'p', 'L46-L50 (Fig.2), L181 (Sec.2.1)',
  notes=Q('p', 'Agent: Event History -> Action', 'Runtime to execute all actions into observations',
          'The core of the agent abstraction lies in the step function, which takes the current state as input and generates an appropriate action based on the agent’s logic.'))
E('m_actions', 'method_detail', 'Three core action types: IPythonRunCellAction, CmdRunAction, and BrowserInteractiveAction (browsing DSL from BrowserGym).', 'p', 'L131 (Sec.2.1)',
  notes=Q('p', 'Actions IPythonRunCellAction and CmdRunAction enable the agent to execute arbitrary Python code and bash commands inside the sandbox environment',
          'BrowserInteractiveAction enables interaction with a web browser with a domain-specific language for browsing introduced by BrowserGym (Drouin et al., 2024).'))
E('m_runtime', 'method_detail', 'Each task session runs in an isolated Docker container reached through a REST API server; a configurable workspace directory is mounted.', 'p', 'L185 (Sec.2.2)',
  notes=Q('p', 'For each task session, OpenHands spins up a securely isolated docker container sandbox, where all the actions from the event stream are executed.',
          'A configurable workspace directory containing files the user wants the agent to work on is mounted into that secure sandbox for OpenHands agents to access.'))
E('m_api', 'method_detail', 'The in-sandbox API server maintains a bash shell, a Jupyter IPython server and a Playwright-based Chromium browser; browser observations include HTML, DOM, accessibility tree, screenshot and open tabs.', 'p', 'L186-L193 (Sec.2.2)',
  notes=Q('p', '(1) A bash shell that connects with the operating system environment (specified by the docker image) for command execution.',
          '(2) A Jupyter IPython server to handle interactive python (IPython) code execution requests and return the execution results back to the event stream.',
          'including HTML, DOM, accessibility tree (Mozilla), screenshot, opened tabs, etc.'))
E('m_image', 'method_detail', 'Runtime images are built from a user-provided base image with the runtime client installed; images carry a hash-based tag (MD5 of the build folder) and a generic tag; identical hash tags mean identical source code and Dockerfile.', 'p', 'L918-L972 (App.F)',
  notes=Q('p', 'This tag is based on the MD5 hash of the Docker build folder, which includes the source code (of runtime client and related dependencies) and Dockerfile',
          'Identical hash tags guarantee that the images were built with exactly the same source code and Dockerfile'))
E('m_skills', 'method_detail', 'AgentSkills is a Python package whose functions are automatically imported into the IPython environment; it includes file-editing utilities adapted from SWE-Agent and Aider, scrolling, and parsers for images, PDFs and other formats (supported list as of OpenHands v0.6 in App.I).', 'p', 'L197-L199 (Sec.2.3), L1050-L1114 (App.I)',
  notes=Q('p', 'AgentSkills is designed as a Python package consisting of different utility functions (i.e., tools) that are automatically imported into the Jupyter IPython environment',
          'AgentSkills library includes file editing utilities adapted from SWEAgent (Yang et al., 2024) and Aider (Gauthier) like edit_file'))
E('m_deleg', 'method_detail', 'A special action type, AgentDelegateAction, lets an agent hand a subtask to another agent.', 'p', 'L201 (Sec.2.4)',
  notes=Q('p', 'we use a special action type AgentDelegateAction, which enables an agent to delegate a specific subtask to another agent.'))
E('m_hub', 'method_detail', 'AgentHub holds over 10 agents: CodeActAgent (default generalist, CodeAct framework), Browsing Agent (zero-shot prompting), GPTSwarm agent (optimizable graphs) and micro agents.', 'p', 'L20 (Sec.1), L204-L253 (Sec.3)',
  notes=Q('p', 'OpenHands includes an agent hub with over 10 implemented agents (§3)',
          'CodeActActAgent is the default generalist agent based on the CodeAct framework (Wang et al., 2024a).'.replace('CodeActActAgent', 'CodeActAgent'),
          'with only zero-shot prompting'))
E('m_ui', 'method_detail', 'Chat-based graphical interface visualizes agent actions and lets the user interrupt the agent to give feedback at any moment; it connects to the event stream.', 'p', 'L20, L909 (App.D)',
  notes=Q('p', 'The user may interrupt the agent at any moment to provide additional feedback, comments, or instruction while the agent is working.'))
E('m_itest', 'method_detail', 'Integration-test framework: developers define a task and an expected gold file; LLM calls are intercepted and answered from stored prompt-response pairs; tests run on every pull request across platforms and sandboxes.', 'p', 'L911 (App.E)',
  notes=Q('p', 'Upon task execution through OpenHands, outputs are compared against a predefined "gold file" to ensure accuracy.',
          'Tests are automatically scheduled for every pull request and commit on the main branch'))
E('m_bench15', 'method_detail', 'Table 2 lists 15 benchmarks: seven software engineering, two web, six miscellaneous assistance.', 'p', 'L259-L271 (Tab.2)',
  value={'software': 7, 'web': 2, 'misc_assistance': 6, 'total': 15},
  notes=Q('p', 'we integrate 15 established benchmarks into OpenHands') + '. Software: SWE-Bench, HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA. Web: WebArena, MiniWoB++. Misc: GAIA, GPQA, AgentBench, MINT, Entity Deduction Arena, ProofWriter.')
E('m_community', 'observation', 'Authors report 32K GitHub stars, more than 2.1K contributions from over 188 contributors, and an MIT license, as of writing.', 'p', 'L7 (Abstract), L124 (Sec.1)',
  value={'github_stars': '32K', 'contributions': 'more than 2.1K', 'contributors': 'over 188'},
  notes=Q('p', 'OpenHands has gained significant traction, with 32K GitHub stars and more than 2.1K contributions from over 188 contributors.'))
E('m_protocol', 'method_detail', 'Evaluation protocol facts: results are reported without SWE-bench hint text; SWE-bench Lite (300 instances) is the default subset; MiniWoB++ is reported on the full 125-environment set with only full-set baselines.', 'p', 'L464 (Sec.4.2), L622 (Sec.4.3), Tab.4',
  notes=Q('p', 'The agent-modified code repository is tested against a test suite incorporating new tests added from human developers’ fixes for the same issue.',
          'Throughout this paper, we report all results without using hint text.',
          'Still, we report the performance on the full set and only include baselines that are evaluated on the full set.'))
E('m_swe_cost', 'observation', 'Authors estimate the complete SWE-Bench set (2294 instances) at $6.9k using a conservative $3 per instance, and a SWE-Bench Lite run with gpt-4o at around 600 USD.', 'p', 'L467 (fn.2), L912 (fn.4)', value={'full_set_instances': 2294, 'full_set_cost_usd': '6.9k', 'per_instance_usd_estimate': 3, 'lite_gpt4o_cost_usd': 'around 600'},
  notes=Q('p', 'Running the complete set of 2294 instances costs $6.9k, using a conservative estimate of $3 per instance.', 'Running a SWE-Bench Lite Jimenez et al. (2024) evaluation with gpt-4o costs around 600 USD.'))
E('m_benchsetup', 'method_detail', 'Benchmark set-ups: HumanEvalFix Python split (164 instances, pass@k, multi-turn self-debug with test feedback, 0-shot); ML-Bench quarter subset (68 instances); Gorilla APIBench (1775 instances, correct API domain); ToolQA easy subset (800 instances); BioCoder 157 Python functions with context prompts removed; BIRD 300 dev samples with execution accuracy and multi-turn SQL correction.', 'p', 'L466, L550-L556, L617 (Sec.4.2), Tab.4',
  notes=Q('p', 'We focus on the Python subset of the benchmark and allow models to solve the bugs by self-debug over multiple turns, incorporating feedback from test execution.',
          'we perform agent evaluation on the quarter subset of ML-Bench',
          'We adopt the easy subset for evaluation.',
          'We select 300 samples from the dev set to integrate into OpenHands and evaluate on execution accuracy.'))
E('m_websetup', 'method_detail', 'Web benchmark set-ups: WebArena has 812 human-curated tasks across shopping, forums, developer platforms and content management; MiniWoB++ has 125 synthetic minimalist environments with built-in rewards, some needing vision.', 'p', 'L621-L622 (Sec.4.3)',
  notes=Q('p', 'WebArena comprises 812 human-curated task instructions across various domains, including shopping, forums, developer platforms, and content management systems.',
          'The tasks are synthetically initialized on 125 different minimalist web interfaces.'))
E('m_miscsetup', 'method_detail', 'Miscellaneous benchmark set-ups: GAIA (466 tasks, Level-1 validation subset of 53 used), GPQA diamond (198), AgentBench OS subset (144), MINT math (225) and code (136) with up to five iterations and two chances to propose solutions, ProofWriter hardest 5-hop subset (600), Entity Deduction Arena two datasets of 100 instances each averaged.', 'p', 'L626-L627, L771-L774 (Sec.4.4), Tab.6',
  notes=Q('p', 'GAIA consists of 466 curated tasks across three levels.',
          'We follow the original paper and allow the agent to interact with up to five iterations with two chances to propose solutions.',
          'each comprising 100 instances, and report the average success rate over these two datasets'))
E('m_tab3note', 'method_detail', 'Table 3 footnote: the asterisked number is reported from CodeActAgent v1.5; dashes mark cells with no reported result.', 'p', 'L382 (Tab.3)',
  notes=Q('p', '* Numbers are reported from CodeActAgent v1.5.'))

# ---------------------------------------------------------------- results: software
E('r_swe_oh', 'result', 'SWE-Bench Lite (300 instances, no hint text), OpenHands CodeActAgent v1.8 resolve rates by model: claude-3-5-sonnet@20240620 26.0, gpt-4o-2024-05-13 22.0; average cost per instance 1.10 and 1.72 USD.', 'p', 'L472-L546 (Tab.4), L286-L376 (Tab.3)', strength='hard',
  value={'claude-3-5-sonnet@20240620': 26.0, 'gpt-4o-2024-05-13': 22.0, 'avg_cost_usd': {'claude-3-5-sonnet@20240620': 1.10, 'gpt-4o-2024-05-13': 1.72}, 'unit': 'percent of instances resolved'},
  cond='SWE-Bench Lite, 300 instances, without hint, OH CodeActAgent v1.8', notes='Tab.4 and Tab.3 agree on 22.0 and 26.0.' + TAB_NOTE)
E('r_swe_mini', 'result', 'SWE-Bench Lite, OpenHands CodeActAgent v1.8 with gpt-4o-mini-2024-07-18: 7.0 in Table 4 (average cost 0.01 USD).', 'p', 'L472-L546 (Tab.4)', strength='hard',
  value={'value': 7.0, 'metric': 'swebench_lite_resolve_rate_pct'}, cond='SWE-Bench Lite, 300 instances, without hint, OH CodeActAgent v1.8, gpt-4o-mini-2024-07-18',
  quantity='swebench_lite_oh_v18_gpt4omini_resolve_rate', status='conflicting', conflicts_with=['E_SWE_MINI_TAB3'],
  notes='Table 4 value; Table 3 lists 6.3 for the same agent and model (see conflicting item).' + TAB_NOTE)
E('r_swe_mini_t3', 'result', 'SWE-Bench Lite, OpenHands CodeActAgent v1.8 with gpt-4o-mini-2024-07-18: 6.3 in Table 3.', 'p', 'L364-L366 (Tab.3)', strength='hard',
  value={'value': 6.3, 'metric': 'swebench_lite_resolve_rate_pct'}, cond='SWE-Bench Lite, OH CodeActAgent v1.8, gpt-4o-mini-2024-07-18',
  quantity='swebench_lite_oh_v18_gpt4omini_resolve_rate', status='conflicting', conflicts_with=['E_SWE_MINI'],
  notes='Table 3 is captioned "Selected evaluation results" and refers to Tab. 4 for full results.' + TAB_NOTE)
E('r_swe_ref', 'result', 'SWE-Bench Lite reference systems: SWE-Agent gpt-4-1106-preview 18.0 (avg cost 1.67 USD); AutoCodeRover gpt-4-0125-preview 19.0; Aider gpt-4o & claude-3-opus 26.3; Table 3 also lists Moatless Tools claude-3.5-sonnet 26.7 and Agentless gpt-4o 27.3.', 'p', 'L286-L316 (Tab.3), L472-L546 (Tab.4)', strength='hard',
  value={'SWE-Agent gpt-4-1106-preview': 18.0, 'AutoCodeRover gpt-4-0125-preview': 19.0, 'Aider gpt-4o & claude-3-opus': 26.3, 'Moatless Tools claude-3.5-sonnet (Tab.3 only)': 26.7, 'Agentless gpt-4o (Tab.3 only)': 27.3},
  cond='SWE-Bench Lite, 300 instances, without hint', notes='Reference numbers as reported in the project paper; not re-run by the authors as far as the text states.' + TAB_NOTE)
E('r_swe_text', 'observation', 'Authors describe 26% for CodeActAgent v1.8 with claude-3.5-sonnet as a competitive resolve rate compared to other open-source SWE specialists.', 'p', 'L464 (Sec.4.2)',
  notes=Q('p', 'our most recent version of CodeActAgent v1.8, using claude-3.5-sonnet, achieves a competitive resolve rate of 26% compared to other open-source SWE specialists.'))
E('r_hef', 'result', 'HumanEvalFix (Python, 164 instances), OpenHands CodeActAgent v1.5 0-shot: gpt-4o-2024-05-13 79.3 (avg cost 0.14 USD); gpt-3.5-turbo-16k-0613 20.1 (0.11 USD).', 'p', 'L472-L546 (Tab.4), L466', strength='hard',
  value={'gpt-4o-2024-05-13': 79.3, 'gpt-3.5-turbo-16k-0613': 20.1, 'unit': 'percent of bugs fixed (pass@k setup of Muennighoff et al.)'},
  cond='HumanEvalFix Python split, 164 instances, 0-shot, multi-turn self-debug', notes=Q('p', 'OpenHands CodeActAgent successfully fixes 79.3% of bugs in the Python split.') + TAB_NOTE)
E('r_hef_ref', 'result', 'HumanEvalFix reference results: BLOOMZ-176B 16.6, OctoCoder-15B 30.4, DeepSeekCoder-33B-Instruct 47.5, StarCoder2-15B 48.6, SWE-agent 1-shot gpt-4-turbo 87.7.', 'p', 'L472-L546 (Tab.4), L466', strength='hard',
  value={'BLOOMZ-176B': 16.6, 'OctoCoder-15B': 30.4, 'DeepSeekCoder-33B-Instruct': 47.5, 'StarCoder2-15B': 48.6, 'SWE-agent 1-shot gpt-4-turbo': 87.7},
  cond='HumanEvalFix Python split, 164 instances', notes=Q('p', 'This is significantly better than all non-agentic approaches, almost doubling the performance of StarCoder2-15B') + ' (the word "significantly" is the authors\' and no test is reported).' + TAB_NOTE)
E('r_sw_other', 'result', 'Other software benchmarks, OpenHands CodeActAgent v1.5 with gpt-4o-2024-05-13: BIRD (300 instances, +BM25) 47.3; ML-Bench (68 instances) 76.5; BioCoder Python (157) 27.5; Gorilla APIBench (1775) 36.4; ToolQA easy (800) 47.2.', 'p', 'L472-L546 (Tab.4)', strength='soft',
  value={'BIRD': 47.3, 'ML-Bench': 76.5, 'BioCoder (Python)': 27.5, 'Gorilla APIBench': 36.4, 'ToolQA': 47.2},
  cond='CodeActAgent v1.5, gpt-4o-2024-05-13, 0-shot, benchmark-specific subsets', notes='Row-to-value alignment inferred from row order and counts because the table layout is damaged; treat as soft.')
E('r_sw_other_ref', 'result', 'Reference rows for those benchmarks in Table 4 (inferred alignment): BIRD CodeLlama-7B-Instruct 18.3, CodeQwen-7B-Chat 31.3; ML-Bench SWE-Agent gpt-4-1106-preview 42.6, Aider gpt-4o 64.4; BioCoder gpt-3.5-turbo 11.0, gpt-4-1106-preview 12.7; Gorilla APIBench finetuned Gorilla llama-7b 75.0; ToolQA ReAct gpt-3.5-turbo 36.8, gpt-3 43.1.', 'p', 'L472-L546 (Tab.4)', strength='soft',
  value={'BIRD CodeLlama-7B-Instruct': 18.3, 'BIRD CodeQwen-7B-Chat': 31.3, 'ML-Bench SWE-Agent gpt-4-1106-preview': 42.6, 'ML-Bench Aider gpt-4o': 64.4, 'BioCoder gpt-3.5-turbo': 11.0, 'BioCoder gpt-4-1106-preview': 12.7, 'Gorilla finetuned llama-7b': 75.0, 'ToolQA ReAct gpt-3.5-turbo': 36.8, 'ToolQA ReAct gpt-3': 43.1},
  notes='Row-to-value alignment inferred from row order and counts; see missing_evidence M002.')
E('r_sw_weak', 'negative_result', 'OpenHands with weaker models scores low: SWE-Bench Lite gpt-4o-mini 7.0 (Tab.4; 6.3 in Tab.3); HumanEvalFix gpt-3.5-turbo-16k-0613 20.1; ML-Bench gpt-3.5-turbo-16k-0613 13.2; Gorilla APIBench gpt-3.5-turbo-0125 21.6; ToolQA gpt-3.5-turbo-0125 2.3.', 'p', 'L472-L546 (Tab.4)', strength='soft',
  value={'SWE-Bench Lite gpt-4o-mini (Tab.4)': 7.0, 'HumanEvalFix gpt-3.5-turbo-16k-0613': 20.1, 'ML-Bench gpt-3.5-turbo-16k-0613': 13.2, 'Gorilla APIBench gpt-3.5-turbo-0125': 21.6, 'ToolQA gpt-3.5-turbo-0125': 2.3},
  notes='Values other than SWE-Bench Lite and HumanEvalFix rest on inferred row alignment.')
E('r_hef_neg', 'negative_result', 'On HumanEvalFix, SWE-agent (1-shot, gpt-4-turbo) reaches 87.7 against OpenHands 0-shot 79.3.', 'p', 'L466 (Sec.4.2.1), Tab.4', strength='hard',
  value={'SWE-agent 1-shot gpt-4-turbo': 87.7, 'OpenHands v1.5 0-shot gpt-4o': 79.3},
  notes=Q('p', 'While SWE-Agent achieves 87.7%, Yang et al. (2024) provides the model a full demonstration of a successful sample trajectory fixing one of the bugs in the test dataset (“1-shot”), whereas our evaluation of OpenHands is 0-shot.'))
E('r_swe_neg', 'negative_result', 'On SWE-Bench Lite the OpenHands 26.0 (claude-3-5-sonnet) is below the listed Aider 26.3, Moatless Tools 26.7 and Agentless 27.3; OpenHands with gpt-4o is 22.0.', 'p', 'L286-L316 (Tab.3), Tab.4', strength='hard',
  value={'OpenHands claude-3-5-sonnet': 26.0, 'Aider': 26.3, 'Moatless Tools': 26.7, 'Agentless': 27.3, 'OpenHands gpt-4o': 22.0})
E('r_gor_neg', 'negative_result', 'On Gorilla APIBench the OpenHands gpt-4o result (36.4) is below the finetuned Gorilla row (75.0), under the inferred alignment.', 'p', 'L472-L546 (Tab.4)', strength='soft',
  value={'OpenHands v1.5 gpt-4o': 36.4, 'Gorilla finetuned llama-7b': 75.0}, notes='Alignment inferred.')

# ---------------------------------------------------------------- results: web
E('r_wa', 'result', 'WebArena (812 instances): OpenHands BrowsingAgent v1.0 gpt-4o-mini 8.5, gpt-4o 14.8, claude-3-5-sonnet 15.5 (avg cost 0.01, 0.15, 0.10 USD); CodeActAgent v1.8 via delegation to BrowsingAgent gpt-4o-mini 8.3, gpt-4o 14.5, claude-3-5-sonnet 15.3.', 'p', 'L562-L615 (Tab.5)', strength='hard',
  value={'BrowsingAgent v1.0': {'gpt-4o-mini-2024-07-18': 8.5, 'gpt-4o-2024-05-13': 14.8, 'claude-3-5-sonnet-20240620': 15.5},
         'CodeActAgent v1.8 via delegation': {'gpt-4o-mini-2024-07-18': 8.3, 'gpt-4o-2024-05-13': 14.5, 'claude-3-5-sonnet-20240620': 15.3},
         'avg_cost_usd_BrowsingAgent': [0.01, 0.15, 0.10], 'unit': 'success rate %'},
  cond='WebArena, 812 instances', notes=TAB_NOTE.strip())
E('r_wa_ref', 'result', 'WebArena reference results: Lemur-chat-70b 5.3; Patel et al. trained 72B 9.4; AutoWebGLM trained 7B 18.2; Auto Eval & Refine GPT-4 + Reflexion with GPT-4V reward model 20.2; WebArena Agent gpt-3.5-turbo 6.2 and gpt-4-turbo 14.4.', 'p', 'L562-L615 (Tab.5)', strength='hard',
  value={'Lemur-chat-70b': 5.3, 'Patel et al. trained 72B': 9.4, 'AutoWebGLM trained 7B': 18.2, 'Auto Eval & Refine': 20.2, 'WebArena Agent gpt-3.5-turbo': 6.2, 'WebArena Agent gpt-4-turbo': 14.4},
  cond='WebArena, 812 instances', notes=TAB_NOTE.strip())
E('r_mw', 'result', 'MiniWoB++ (125 environments): OpenHands BrowsingAgent v1.0 gpt-3.5-turbo-0125 27.2, gpt-4o 40.8 (avg cost 0.01, 0.05 USD); CodeActAgent v1.8 via delegation gpt-4o 39.8; references Workflow Guided Exploration 34.6 and CC-NET 91.1.', 'p', 'L562-L615 (Tab.5)', strength='hard',
  value={'BrowsingAgent v1.0 gpt-3.5-turbo-0125': 27.2, 'BrowsingAgent v1.0 gpt-4o': 40.8, 'CodeActAgent v1.8 via delegation gpt-4o': 39.8, 'Workflow Guided Exploration': 34.6, 'CC-NET': 91.1},
  cond='MiniWoB++, 125 environments, full set', notes='WGE and CC-NET are described in Tab.5 as trained specialist models.' + TAB_NOTE)
E('r_web_text', 'observation', 'Authors state that BrowsingAgent achieves competitive performance among agents that use LLMs with domain-general prompting techniques on WebArena.', 'p', 'L621 (Sec.4.3)',
  notes=Q('p', 'our BrowsingAgent achieves competitive performance among agents that use LLMs with domain-general prompting techniques.'))
E('r_web_neg', 'negative_result', 'On WebArena the best OpenHands number (15.5) is below AutoWebGLM (18.2) and Auto Eval & Refine (20.2); on MiniWoB++ the best OpenHands number (40.8) is below CC-NET (91.1) and above Workflow Guided Exploration (34.6).', 'p', 'L562-L615 (Tab.5)', strength='hard',
  value={'OpenHands WebArena best': 15.5, 'AutoWebGLM': 18.2, 'Auto Eval & Refine': 20.2, 'OpenHands MiniWoB++ best': 40.8, 'CC-NET': 91.1, 'Workflow Guided Exploration': 34.6})

# ---------------------------------------------------------------- results: misc
E('r_gaia', 'result', 'GAIA Level-1 validation (53 instances): OpenHands GPTSwarm v1.0 gpt-4-0125-preview 30.2 (avg cost 0.110 USD), gpt-4o-2024-05-13 32.1 (0.050 USD); AutoGPT gpt-4-turbo 13.2.', 'p', 'L633-L652 (Tab.6)', strength='hard',
  value={'OH GPTSwarm gpt-4-0125-preview': 30.2, 'OH GPTSwarm gpt-4o-2024-05-13': 32.1, 'AutoGPT gpt-4-turbo': 13.2}, cond='GAIA L1 validation set, 53 instances', notes=TAB_NOTE.strip())
E('r_gpqa', 'result', 'GPQA diamond (198 instances): OpenHands CodeActAgent v1.8 claude-3-5-sonnet-20240620 52.0 (avg cost 0.065 USD); few-shot chain-of-thought gpt-3.5-turbo-16k 29.6, gpt-4 38.8; non-expert human 21.9.', 'p', 'L633-L670 (Tab.6)', strength='hard',
  value={'OH CodeActAgent v1.8 claude-3-5-sonnet-20240620': 52.0, 'Few-shot CoT gpt-3.5-turbo-16k': 29.6, 'Few-shot CoT gpt-4': 38.8, 'Non-expert human': 21.9}, cond='GPQA diamond set, 198 instances', notes=TAB_NOTE.strip())
E('r_gpqa_expert6', 'result', 'GPQA diamond expert human accuracy in Table 6: 81.3.', 'p', 'L654-L658 (Tab.6)', strength='hard',
  value={'value': 81.3, 'metric': 'gpqa_diamond_accuracy_pct'}, cond='GPQA diamond expert human validators', quantity='gpqa_diamond_expert_human_accuracy',
  status='conflicting', conflicts_with=['E_GPQA_EXPERT7'],
  resolution={'chosen': 'E_GPQA_EXPERT6', 'reason': 'Table 6 is the table the results section discusses; both tables are in the same paper and no primary log exists. The 0.1 difference is disclosed in the draft.', 'by': 'agent'})
E('r_gpqa_expert7', 'result', 'GPQA diamond expert human accuracy in Table 7: 81.2.', 'p', 'L979-L1030 (Tab.7)', strength='hard',
  value={'value': 81.2, 'metric': 'gpqa_diamond_accuracy_pct'}, cond='GPQA diamond expert human validators', quantity='gpqa_diamond_expert_human_accuracy',
  status='conflicting', conflicts_with=['E_GPQA_EXPERT6'])
E('r_gpqa7', 'result', 'GPQA full results (diamond / main / extended, percent): OpenHands CodeActAgent v1.5 gpt-3.5-turbo 27.9 / 23.4 / 26.1 (avg cost 0.012 USD); gpt-4-turbo 51.8 / 47.4 / 42.4 (0.501 USD); gpt-4o 53.1 / 49.3 / 52.8 (0.054 USD); GPT-4 with search 38.8 / 41.0 / 39.4; expert human 72.5 (main), 65.4 (extended).', 'p', 'L979-L1045 (Tab.7)', strength='hard',
  value={'OH v1.5 gpt-3.5-turbo': [27.9, 23.4, 26.1], 'OH v1.5 gpt-4-turbo': [51.8, 47.4, 42.4], 'OH v1.5 gpt-4o': [53.1, 49.3, 52.8], 'GPT-4 with search': [38.8, 41.0, 39.4], 'expert main/extended': [72.5, 65.4],
         'avg_cost_usd_OH': [0.012, 0.501, 0.054]}, cond='GPQA diamond / main / extended sets', notes='Table 3 marks 53.1 with an asterisk as reported from CodeActAgent v1.5.' + TAB_NOTE)
E('r_ab', 'result', 'AgentBench OS subset (144 instances): OpenHands CodeActAgent v1.5 gpt-4o-2024-05-13 57.6 (avg cost 0.085 USD), gpt-3.5-turbo-0125 11.8 (0.006 USD); AgentBench baseline agent gpt-4 42.4, gpt-3.5-turbo 32.6.', 'p', 'L672-L688 (Tab.6)', strength='hard',
  value={'OH gpt-4o-2024-05-13': 57.6, 'OH gpt-3.5-turbo-0125': 11.8, 'baseline gpt-4': 42.4, 'baseline gpt-3.5-turbo': 32.6}, cond='AgentBench OS (bash) subset, 144 instances', notes=TAB_NOTE.strip())
E('r_mint', 'result', 'MINT (math subset 225 instances): OpenHands CodeActAgent v1.5 gpt-4o-2024-05-13 77.3 (0.070 USD), gpt-3.5-turbo-16k-0613 33.8 (0.048 USD); MINT baseline gpt-4-0613 65.8. MINT code subset (136 instances): OpenHands gpt-4o 50.0 (0.087 USD), gpt-3.5-turbo-16k-0613 5.2 (0.030 USD); baseline gpt-4-0613 59.6.', 'p', 'L690-L724 (Tab.6)', strength='hard',
  value={'math': {'OH gpt-4o': 77.3, 'OH gpt-3.5-turbo-16k-0613': 33.8, 'baseline gpt-4-0613': 65.8}, 'code': {'OH gpt-4o': 50.0, 'OH gpt-3.5-turbo-16k-0613': 5.2, 'baseline gpt-4-0613': 59.6}},
  cond='MINT math 225 instances, code 136 instances', notes=TAB_NOTE.strip())
E('r_pw', 'result', 'ProofWriter (600 instances, 5-hop): OpenHands CodeActAgent v1.5 gpt-4o 78.8; few-shot chain-of-thought gpt4 68.1; Logic-LM (gpt4 + symbolic solver) 79.6.', 'p', 'L726-L742 (Tab.6)', strength='hard',
  value={'OH gpt-4o-2024-05-13': 78.8, 'CoT gpt4': 68.1, 'Logic-LM gpt4 + symbolic solver': 79.6}, cond='ProofWriter, 600 instances requiring 5-hop reasoning', notes=TAB_NOTE.strip())
E('r_eda', 'result', 'Entity Deduction Arena (200 instances): OpenHands CodeActAgent v1.5 gpt-4o 38.0, gpt-3.5-turbo-16k-0613 24.0; zero-shot prompting gpt-4-0314 40.0, gpt-3.5-turbo-0613 27.0.', 'p', 'L744-L760 (Tab.6)', strength='hard',
  value={'OH gpt-4o-2024-05-13': 38.0, 'OH gpt-3.5-turbo-16k-0613': 24.0, 'zero-shot gpt-4-0314': 40.0, 'zero-shot gpt-3.5-turbo-0613': 27.0}, cond='Entity Deduction Arena, Things and Celebrities, 100 instances each, averaged', notes=TAB_NOTE.strip())
E('r_misc_neg', 'negative_result', 'On miscellaneous benchmarks OpenHands is below the listed reference in five rows: MINT code gpt-4o 50.0 vs baseline gpt-4-0613 59.6; Entity Deduction Arena gpt-4o 38.0 vs gpt-4-0314 40.0; ProofWriter gpt-4o 78.8 vs Logic-LM 79.6; AgentBench gpt-3.5-turbo-0125 11.8 vs baseline gpt-3.5-turbo 32.6; MINT code gpt-3.5-turbo-16k-0613 5.2 vs 59.6 for gpt-4-0613.', 'p', 'L633-L760 (Tab.6)', strength='hard',
  value={'MINT code OH gpt-4o': 50.0, 'MINT code baseline gpt-4-0613': 59.6, 'EDA OH gpt-4o': 38.0, 'EDA gpt-4-0314': 40.0, 'ProofWriter OH gpt-4o': 78.8, 'Logic-LM': 79.6, 'AgentBench OH gpt-3.5-turbo-0125': 11.8, 'AgentBench baseline gpt-3.5-turbo': 32.6, 'MINT code OH gpt-3.5-turbo-16k-0613': 5.2})
E('r_general', 'observation', 'Authors state the same CodeAct agent without prompt modifications is competitive in three task categories, and that agents that are optimized for a category are the typical baselines.', 'p', 'L461 (Sec.4.1)',
  notes=Q('p', 'Notably, the same CodeAct agent, without any modifications to its system prompt, demonstrates competitive performance across three major task categories: software development, web interaction, and miscellaneous tasks.',
          'This is particularly significant when compared to the baseline agents, which are typically designed and optimized for specific task categories.'))
E('r_gaia_text', 'observation', 'Authors state that OpenHands runtime and tools simplify GAIA integration significantly (qualitative statement; no measurement).', 'p', 'L626 (Sec.4.4)',
  notes=Q('p', 'Setting up GAIA is traditionally challenging due to the complexity of integrating various tools with the agent'))

# ---------------------------------------------------------------- author-stated limitations (verbatim)
E('lim_complex', 'limitation_noted', 'Authors state that current agents still struggle with complex tasks.', 'p', 'L887 (App.A)',
  notes=Q('p', 'Current agents still struggle with complex tasks, and we are interested in building better agents through both training and inference time techniques.'))
E('lim_edit', 'limitation_noted', 'Authors state that the current agent suffers a lot when editing long files.', 'p', 'L892 (App.A)',
  notes=Q('p', 'Current agent suffers a lot when editing long files, and we are interested in exploring different approaches to improve the file editing performance of agents.'))
E('lim_workflow', 'limitation_noted', 'Authors state that OpenHands workflows still need a substantial handcrafted workload.', 'p', 'L894 (App.A)',
  notes=Q('p', 'Currently, OpenHands’s workflow still requires a substantial handcrafted workload.'))
E('lim_multimodal', 'limitation_noted', 'Authors state their multi-modality support goes through predefined agent skills and they want it to be principled via standard IPython and browser integration.', 'p', 'L886 (App.A)',
  notes=Q('p', 'While our current implementation already supports a wide range of file formats through predefined agent skills, we are interested in enabling multi-modality in a principled way through standard IPython and browser integration'))
E('lim_research', 'limitation_noted', 'Authors state that most AI agents today are research artifacts that cannot reliably perform complex long-horizon real-world tasks, and that safe and reliable agents remain challenging.', 'p', 'L896 (App.B), L777 (Sec.5)',
  notes=Q('p', 'Most AI agents today are still research artifacts and lack the ability to perform complex, long-horizon tasks in the real world reliably.', 'Despite challenges in developing safe and reliable agents (§A)'))
E('lim_top', 'limitation_noted', 'Authors state that OpenHands agents may not achieve top performance in every category.', 'p', 'L461 (Sec.4.1)',
  notes=Q('p', 'While OpenHands agents may not achieve top performance in every category, they are designed with generality in mind.'))
E('lim_hef', 'limitation_noted', 'Authors note the HumanEvalFix comparison with SWE-Agent is not like for like: SWE-Agent used a 1-shot demonstration, OpenHands 0-shot.', 'p', 'L466 (Sec.4.2.1)',
  notes=Q('p', 'whereas our evaluation of OpenHands is 0-shot'))
E('lim_repo_compat', 'limitation_noted', 'Benchmarks README states that not every benchmarks version is compatible with every Agent SDK version, and that a migration from OpenHands V0 to the SDK is in progress.', 'r1', 'L5, L197',
  notes=Q('r1', 'not every version of the benchmarks is compatible with every version of the SDK', 'Migration in Progress'))
E('lim_repo_nosandbox', 'limitation_noted', 'Agent Canvas README warns that running without a sandbox gives the agent full access to the machine\'s filesystem, and labels the project status beta.', 'r2', 'L14, L65-L66',
  notes=Q('r2', "This runs the agent-server directly on the machine you're installing on — the agent will have full access to your filesystem!", 'status-beta'))

# ---------------------------------------------------------------- future directions
E('fut_dirs', 'hypothesis_stated', 'Authors list future directions: principled multi-modality, stronger agents via training and inference-time techniques, better long-file editing, Auto Eval & Refine as an optional browsing component, and graph-based automatic workflow generation.', 'p', 'L885-L894 (App.A)',
  notes=Q('p', 'Auto Eval & Refine Pan et al. (2024), an agent retry-on-error strategy with Reflexion Shinn et al. (2024) prompts and task completion reward models, will be integrated as an optional component attached to our browsing agent.',
          'We believe that graph-based frameworks such as GPTSwarm Zhuge et al. (2024) and LangGraph Chase (2022) could serve as alternative solutions for building agents.'))
E('fut_hef', 'hypothesis_stated', 'Authors state that 100% on HumanEvalFix is entirely feasible because the bugs were human-created and carefully validated, and that they seek it in future iterations.', 'p', 'L466, L548 (Sec.4.2.1)',
  notes=Q('p', 'achieving 100% on this benchmark is entirely feasible, which we seek to do in future iterations of OpenHands.'))

# ---------------------------------------------------------------- READMEs (repository state, soft)
E('rd1_list', 'method_detail', 'Benchmarks README lists six benchmarks marked active: SWE-Bench, SWE-Bench Pro, GAIA, Commit0, OpenAgentSafety, ProgramBench.', 'r1', 'L9-L16',
  notes='Table rows "Status: Active" for the six benchmarks; the README describes evaluation infrastructure for OpenHands agents.')
E('rd1_remote', 'method_detail', 'Benchmarks README describes two workspace types: local Docker containers (default) and a remote runtime API that provisions one isolated container per evaluation instance, "e.g., 32+ concurrent workers".', 'r1', 'L142-L170',
  notes=Q('r1', 'Each evaluation instance runs in its own isolated container, allowing for massive parallelization (e.g., 32+ concurrent workers)'))
E('rd2_desc', 'method_detail', 'Agent Canvas README: a self-hosted control center that runs OpenHands, Claude Code, Codex, Gemini or any Agent-Client-Protocol-compatible agent across local, remote and cloud backends, with automations that run on a schedule or on webhook events.', 'r2', 'L8-L10, L33-L46',
  notes=Q('r2', 'The self-hosted developer control center for coding agents and automations.', 'Run OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent across local, remote, and cloud backends.'))
E('rd2_arch', 'method_detail', 'Agent Canvas is powered by the OpenHands Agent Server, a REST API for running multiple agents on one machine; the frontend can connect to several Agent Servers; responsibilities are split across four repositories.', 'r2', 'L126-L150',
  notes=Q('r2', 'a REST API for running multiple agents on a single machine'))

E('prior_roles', 'external_fact', 'Authors describe roles of several prior frameworks: MetaGPT (standardized operating procedures), AutoGen (conversation framework), AutoAgents and AGENTS (customizable agent architecture), Auto-GPT (decomposing user goals), LangChain and LangGraph (building blocks with basic runtime support), CrewAI (orchestrating multi-agent communication).', 'p', 'L901-L902 (App.C)',
  notes=Q('p', 'MetaGPT Hong et al. (2023) emphasizing standardized operating procedures',
          'AutoGen Wu et al. (2023) providing a conversation framework for interactive systems',
          'AutoAgents Chen et al. (2024) offer new paradigms for customizable agent architecture',
          'Notable works such as Auto-GPT Gravitas (2023) harness LLMs for task completion by decomposing user goals into executable steps.',
          'LangChain and LangGraph Chase (2022) provide foundational building blocks with basic runtime support',
          'CrewAI CrewAI (2024) focuses on orchestrating multi-agent communications'))

# ---------------------------------------------------------------- fix cross-references for conflict pairs
alias = {'E_SWE_MINI': ids['r_swe_mini'], 'E_SWE_MINI_TAB3': ids['r_swe_mini_t3'],
         'E_GPQA_EXPERT6': ids['r_gpqa_expert6'], 'E_GPQA_EXPERT7': ids['r_gpqa_expert7']}
for it in items:
    if 'conflicts_with' in it:
        it['conflicts_with'] = [alias.get(x, x) for x in it['conflicts_with']]
    if 'resolution' in it:
        it['resolution']['chosen'] = alias.get(it['resolution']['chosen'], it['resolution']['chosen'])
# resolution for the SWE-Bench Lite gpt-4o-mini pair
for it in items:
    if it['id'] == ids['r_swe_mini']:
        it['resolution'] = {'chosen': ids['r_swe_mini'], 'reason': 'Table 3 is captioned as a selection and defers to Table 4 for full results, so the full table is preferred; the paper text will disclose the 6.3 in Table 3.', 'by': 'agent'}
# source hashes
for it in items:
    p = it['locator']['path']
    it['source_hash'] = 'sha256:' + hashlib.sha256(open(p, 'rb').read()).hexdigest()

json.dump({'project_root': '.', 'generated_at': '2026-09-29', 'generated_by': 'CORPUS_AGENT role performed by AUTHOR', 'items': items},
          open('.rcs/evidence/research_evidence.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(ids, open('.rcs/_ids.json', 'w'), indent=1)
print(len(items), 'items')
