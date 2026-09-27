# Paper Spine

**Problem:** Existing language model benchmarks have saturated and rely on self-contained, short-context coding tasks that do not reflect real-world software engineering complexity. {C001}

**Gap:** No benchmark evaluated whether LMs can perform authentic repository-scale software engineering: navigating large codebases, interpreting multi-faceted issues, and generating multi-file, multi-function patches. {C002}

**Question:** Can current language models resolve real-world GitHub issues by editing large Python codebases to pass pre-existing test suites? {C003}

**Approach:** SWE-bench collects 2,294 task instances from 12 popular Python repositories by linking merged pull requests (which contribute new tests) to the issues they resolve, then validates each instance via execution; models are evaluated with BM25 and oracle retrieval settings; SWE-Llama is fine-tuned on 19,000 additional instances. {C004}

**Key finding:** All state-of-the-art models struggle severely: the best BM25 result is Claude 3 Opus at 3.79%, and even with perfectly retrieved context (oracle-collapsed) Claude 3 Opus reaches only 9.39%; the primary bottleneck is context localization, not context recall. {C005}

**Meaning:** Real-world software engineering exposes fundamental limitations in LMs' ability to localize, understand, and correctly modify repository-scale code; the benchmark provides a sustainable, continuously updatable testbed for measuring progress toward practically autonomous LMs. {C006}

**Main limit:** Only Python repositories are included; baseline experiments use retrieval-only approaches rather than agent-based or tool-augmented systems; test-passing does not guarantee code quality. {C007}
