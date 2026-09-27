# CORPUS_AGENT Run Summary

## Task
Extract structured evidence from SWE-bench paper (ICLR 2024) and README to support research communication.

## Mode
`evidence` mode on `./project/` with outputs to `./out/`

## Files Processed
- `paper.txt` (2,645 lines) - Published ICLR 2024 conference version of "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (arXiv:2310.06770v3)
- `README_1.md` (218 lines) - GitHub repository README with setup, usage, and citation information

## Evidence Extraction Results

### Evidence Items Extracted: 68 items (E001-E068)

#### By Kind (count):
- **result** (22): Model performance measurements on SWE-bench and variants
- **metric** (28): Dataset characteristics and model capabilities  
- **observation** (8): Patterns observed in model behavior and retrieval performance
- **limitation_noted** (2): Known limitations acknowledged by authors
- **dataset** (2): SWE-bench composition and structure
- **external_fact** (0)
- **experiment** (0)
- **baseline** (0)
- **negative_result** (0)
- **assumption** (0)
- **hypothesis_stated** (0)
- **method_detail** (0)
- **implementation_detail** (0)

#### By Strength:
- **hard** (66 items, 97%): Measurements from Tables, stated statistics, concrete numbers
- **soft** (2 items, 3%): Qualitative observations and noted limitations

#### By Status:
- **ok** (66 items, 97%)
- **conflicting** (2 items, 3%): Claude 2 resolution rate discrepancy (1.96% vs 1.97%)
- **incomplete** (0)
- **unverifiable** (0)
- **superseded** (0)

### Conflicts Detected: 1 major conflict

**Claude 2 Performance Discrepancy:**
- Abstract and Section 5 text state: **1.96%** resolution rate
- Table 5 (main results): **1.97%** resolution rate
- Evidence items: E015 (1.96%) and E016 (1.97%)
- Impact: Negligible (0.01% difference) but indicates potential measurement or rounding inconsistency
- Status: Marked as conflicting on both items; recommend using 1.96% as primary value (appears twice in text vs once in table)

## Claim Candidates: 20 proposed claims (C001-C020)

### Distribution by Claim Type:
- **measured** (4): Direct measurements from results tables
- **observed** (10): Patterns and relationships observed in data
- **derived** (3): Computed from multiple evidence items
- **interpretation** (2): Explanatory claims requiring mechanistic reasoning
- **hypothesis** (1): Untested speculation about image-containing instances

### Confidence Distribution:
- **high** (12 claims, 60%): Strong evidence base, multiple sources, consistent patterns
- **moderate** (7 claims, 35%): Mix of hard and soft evidence, or single measurement
- **low** (1 claim, 5%): Hypothesis about multimodal content (E060)

### Author Confirmation Status:
- **pending** (20/20): All claims generated as candidates pending author review
- **origin**: 13 author_stated, 7 inferred

## Limitations Documented: 5 limitations (L001-L005)

1. **L001** - Claude 2 performance discrepancy (1.96% vs 1.97%)
   - Severity: negligible practical impact but precision issue
   - Affects: C002

2. **L002** - Context overload mechanism is inferred, not directly measured
   - Severity: interpretation requires external citation
   - Affects: C017

3. **L003** - GPT-4 evaluated on 25% subset due to budget constraints
   - Severity: asymmetric comparison with other models
   - Affects: C015

4. **L004** - SWE-bench limited to Python programming language
   - Severity: limits generalization of findings
   - Affects: C001

5. **L005** - Execution-based testing doesn't guarantee code quality
   - Severity: resolution rate ≠ solution quality
   - Affects: C002, C006, C008

## Missing Evidence: 22 gaps identified

### High Priority Missing Evidence:
1. **Detailed error categorization** - Only 11 qualitative examples; no systematic failure type breakdown
2. **Training data contamination verification** - Assumes disjoint repos prevent leakage; not empirically verified
3. **Statistical significance testing** - No confidence intervals or hypothesis tests on performance differences

### Medium Priority Missing Evidence:
- Per-instance difficulty metrics and attribute correlations
- Model performance stability/variance across multiple runs
- Ablation studies on retrieval methods beyond BM25
- Cross-model overlap analysis beyond Claude 2 vs SWE-Llama 13b
- Patch application failure categorization
- Prompt engineering sensitivity quantification

### Low Priority Missing Evidence:
- SWE-Llama performance on training repositories
- Hyperparameter ablations for fine-tuning
- Comprehensive cross-model instance overlap
- Temporal trend analysis across more time ranges
- Language generalization feasibility analysis

## Key Findings

### Dataset Characteristics
- **2,294 validated task instances** from 12 Python repositories
- **~90,000 PRs filtered** through 3-stage pipeline (97.5% removal rate)
- Issues average **195 words**, codebases average **3,010 files** and **438K lines**
- Gold patches edit **1.7 files**, **3.0 functions**, **32.8 lines** on average
- **51 median pass-to-pass tests** per instance ensure regression detection

### Model Performance (BM25 Retrieval)
- **Claude 2**: 1.96% resolution (best performer)
- **Claude 3 Opus**: 3.79% resolution (best absolute, published after paper)
- **SWE-Llama 7b/13b**: 0.70% resolution (context distribution sensitivity)
- **ChatGPT-3.5**: 0.17% resolution (context limited to 16k tokens)
- **GPT-4**: 1.31% resolution (25% subset, budget-limited)

### Critical Finding: Context Length Paradox
- Performance **drops with increased context** (Claude 2: 1.96% @ 13k → 1.22% @ 50k)
- BM25 recall improves with more context (29.58% @ 13k → 51.06% @ 50k)
- **Oracle-collapsed retrieval improves Claude 2** (5.93% vs 4.80% full oracle)
- **Inference**: Context overload is a fundamental bottleneck; more information actively harms performance

### Model Behavior Patterns
- Generated patches **2.5-3.8x shorter** than reference solutions (19.6 vs 74.5 lines)
- Models rarely edit **>1 file**, despite 1.7 files in gold patches
- Models **miss 42-50% of oracle files** even when available
- Model code tends to be **primitive Python**, not using existing utilities

### Training Contribution
- **SWE-Llama fine-tuned** on 10,000 instances from 37 disjoint repositories
- Training setup reproducible: LoRA rank 16, learning rate 6e-4, 4-8 A100s
- **SWE-Llama competitive with Claude 2** in oracle setting (3.97% vs 4.80%)
- **Sensitive to context distribution shifts**: BM25 (0.70%) vs oracle (3.97%)

## Data Quality Assessment

### Strength of Evidence
- **Quantitative metrics**: Nearly all primary results are hard evidence from execution logs
- **Reproducibility**: 3-stage pipeline is well-documented and appears reproducible
- **Scale**: 2,294 instances provide statistical power for model comparison
- **Validation**: Triple-checked through attribute filtering and execution-based testing

### Potential Issues
1. **Single run per instance** (Pass@1) - no variance estimates
2. **Budget constraints** on GPT-4 - only 25% of instances evaluated
3. **Qualitative analysis** limited to 11 examples - may not represent failure modes
4. **Assume-disjoint repositories** for training data - not verified
5. **Text-only evaluation** - multimodal instances (2-32% depending on repo) untested

## Coverage Analysis

### Well-Covered Areas
✓ Dataset construction and statistics  
✓ Model performance measurements  
✓ Retrieval effectiveness  
✓ Context window constraints  
✓ Gold patch characteristics  

### Poorly-Covered Areas
✗ Why models fail (error categorization)  
✗ Statistical significance of differences  
✗ Multimodal content handling  
✗ Generalization beyond Python  
✗ Code quality vs test passing  

## Recommendations for Authors

1. **Verify the 1.96% vs 1.97% discrepancy** in Claude 2 performance - clarify which is correct
2. **Provide confidence intervals** on all reported resolution rates
3. **Add error categorization** - classify failures systematically (syntax, logic, localization, etc.)
4. **Empirically verify** that training repositories are truly disjoint from eval set
5. **Evaluate SWE-Llama on training repositories** to characterize generalization gap
6. **Release detailed per-instance results** for community analysis

## Time and Effort

- **Evidence extraction**: Complete
- **Conflict detection**: 1 conflict identified
- **Claim generation**: 20 claims proposed
- **Limitation identification**: 5 limitations documented
- **Missing evidence survey**: 22 gaps cataloged

## Files Generated

1. **research_evidence.json** (68 items)
   - Extracted verbatim from paper
   - Marked with precise locators (path + anchor text)
   - Strength and status assigned per rubric

2. **claim_candidates.json** (20 claims + 5 limitations)
   - Hierarchical evidence links
   - Confidence reasoning provided
   - Limited to evidence strength

3. **missing_evidence.json** (22 gaps)
   - Prioritized by severity
   - Justified with impact explanation
   - Sorted by location in document

4. **RUN_SUMMARY.md** (this file)
   - Comprehensive audit trail
   - Key findings synthesis
   - Recommendations for future work

---

**CORPUS_AGENT Status**: Complete ✓
