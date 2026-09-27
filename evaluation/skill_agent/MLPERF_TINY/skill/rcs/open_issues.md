# Open Issues — MLPerf Tiny Manuscript
## Run: v001 | Updated: step 21 post-edit

These items remain genuinely unresolved. Each must be addressed by the human authors before submission.

---

### 1. [MISSING] Archival URL / DOI for MLPerf Tiny v0.5 public results
**Location:** §6.1 and Table 2 note  
**Impact:** High — benchmark-track reviewers expect a stable pointer to verify the headline claims.  
**Action needed:** Add the permanent mlcommons.org results-round URL or a Zenodo/Figshare DOI to both marked locations.

---

### 2. [MISSING] Order-of-magnitude figure for wireless comms vs. local inference energy
**Location:** §1, first paragraph — "far exceeds the energy cost of running inference locally (Bouguera et al., 2018)"  
**Impact:** Medium — the motivating asymmetry is stated but not quantified; one number would make the case decisive.  
**Action needed:** Verify and quote the ratio from Bouguera et al. (2018), then add it inline (e.g., "by two to three orders of magnitude").

---

### 3. [UNRESOLVED] Statistical reliability of reference-model accuracy on small evaluation subsets
**Location:** §4.4 (200-image CIFAR-10 subset), §4.5 (248-sample anomaly detection subset), §4.2 (1,000-utterance KWS subset)  
**Impact:** Medium — reviewer concern about tight quality-target margins on small sets.  
**Action needed:** Either (a) provide full-set accuracy numbers alongside subset numbers, or (b) add confidence intervals, or (c) justify the subset sizes explicitly in the text (e.g., MCU time-cost rationale). The L002 limitation (single-run, no variance) compounds this.

---

### 4. [UNRESOLVED] Per-submission quantitative latency and energy figures absent from paper
**Location:** Table 2  
**Impact:** High — the abstract promises joint accuracy/latency/energy measurement; the results section delivers qualitative descriptions only.  
**Action needed:** Add a table column with representative IPS and µJ/inference figures for at least the reference ARM MCU submission and one accelerator submission. These numbers exist in the public results round and are not reproduced here due to evidence constraints on this draft. The Table 2 note directs readers to the public results, but the self-contained case requires embedding the headline numbers.

---

### 5. [UNRESOLVED] Host-power contamination magnitude not quantified
**Location:** §5.2 — isolation proxy description  
**Impact:** Low-medium — systems-ML reader may want to know how large the contamination effect is.  
**Action needed:** If a measurement of the host-contributed current through the serial link is available, add it. This would strengthen the case for the proxy's necessity.

---

### 6. [UNRESOLVED] PTQ variation within closed division not quantified
**Location:** §5.1 — PTQ residual variable note (added in this revision)  
**Impact:** Low — acknowledged as a limitation; future work.  
**Action needed:** If any data on PTQ-strategy variation exists (e.g., two calibration strategies on the same hardware), cite it to ground the residual-variable claim. If not, the current hedged prose is appropriate.

---

### 7. [UNRESOLVED] Figure 5 — Reference hardware latency/energy values unavailable
**Location:** Evidence item ME001 (missing evidence)  
**Impact:** Low — §6 does not include Figure 5 content; the paper already directs readers to public results for measured numbers.  
**Action needed:** Authors should verify whether a figure or table with reference-platform IPS/µJ values should be added, as this would address issue #4 above.

---

### 8. [ASSUMPTION RECORDED] Venue: NeurIPS Datasets and Benchmarks track
**Location:** plan/venue_profile.yaml  
**Impact:** Low — all venue formatting decisions are flagged `assumed: true`.  
**Action needed:** Confirm the target venue and re-check formatting against the actual submission guidelines. No claim content is venue-dependent.

---

### 9. [ASSUMPTION RECORDED] No user available during run; all STOP/ASK states resolved autonomously
**Location:** state.json, accepted_risks  
**Action needed:** Authors should review the following decisions made without human confirmation:
- Research question phrasing (§1 new paragraph)
- Challenge-solution crosswalk in §2
- Softening of "demonstrates" for the FPGA/open-division claim (§6.2)
- PTQ residual variable sentence (§5.1)
