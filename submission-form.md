# Vireo Audio — Task 1 V5 — Set C
## Submission Form

### 1. What did you build and what business outcome does it drive?

I built a reproducible Python-based refund analysis pipeline for Vireo Audio's support data.

The pipeline cleans and reconciles the ticket export, corrects legacy monetary units, removes migration duplicates, joins agent/order/product information, produces monthly refund reporting by reason code and resolving agent, and flags records requiring review.

The final canonical dataset contains **2,340 refund tickets** with total refunds of **₹67,09,932 (₹67.10 lakh)**.

The original raw export appeared to contain **₹23.01 crore** in refund value. The analysis identified two major data-quality issues behind the inflated figure:

- Legacy Freshdesk refund values were stored in native units and need to be divided by 100.
- 638 ticket IDs appeared twice because of migration/re-import across the helpdesk and legacy systems.

After correction and deduplication, the final refund total is **₹67.10 lakh**, and the monthly, reason-code, and agent-level totals reconcile exactly to this amount.

The analysis also identifies reason-code screening candidates and refund/replacement exceptions for operational review.

---

### 2. What does it cost to run?

The policy gives a blended support contact cost of **₹290 per ticket**.

At approximately **650 tickets per week**:

- Weekly tickets = 650
- Annual tickets = 650 × 52 = 33,800
- Monthly equivalent = 33,800 ÷ 12 = 2,816.67 tickets
- Monthly support contact cost = 2,816.67 × ₹290
- **Estimated monthly support contact cost = ₹8,16,833**
- **Estimated annual support contact cost = ₹98,02,000**

This is the estimated support-contact operating cost from the policy. It is separate from the refund amounts themselves.

Run cost for this analysis tool: **[FILL IN IF REQUIRED]**

---

### 3. How do you know it works?

The pipeline was tested against the full dataset.

- Source tickets: **12,238**
- Canonical unique tickets after migration deduplication: **11,600**
- Refund tickets: **2,340**
- Migration duplicate ticket IDs identified: **638**
- Refund + replacement exceptions: **166**
- GW-OTHER refunds above ₹500: **879 review candidates**
- Refunds missing a reason code: **0**
- Refunds greater than matched order value: **0**
- Unmatched agent roster records: **0**

Reconciliation checks:

- Monthly refund total = **₹67,09,932**
- Reason-code refund total = **₹67,09,932**
- Agent refund total = **₹67,09,932**
- Difference across all reconciliations = **₹0**

The reason-code classifier was deliberately treated as a screening tool rather than as ground truth. It produced:

- 2,340 refund tickets analysed
- 952 clear classifications
- 1,388 cases requiring review
- 446 potential reason-code mismatch candidates
- ₹12,77,100 associated with those potential mismatch candidates

These are **review candidates, not confirmed classification errors**.

A 120-case diagnostic evaluation sample was also generated for further validation. The sample contains potential mismatches, clear cases, and review cases. The evaluation should not be interpreted as a population-level error estimate without independent human validation.

---

### 4. Did you change, narrow, or push back on the client ask?

Yes.

The original request was to show "who is giving away money and for what."

I narrowed the interpretation to **refund activity associated with the resolving agent and reason code**, rather than treating the data as proof that an individual agent was personally responsible for inappropriate refunds.

This matters because:

- The policy says Returns Desk processes the majority of refunds by design.
- Agents can have multiple roster assignments over time.
- The recorded reason code can be incorrect or overly broad.
- Some refund records require contextual review.
- The data contains migration and monetary-unit issues.

I therefore report agent-level refund activity and review flags without treating high refund volume as evidence of wrongdoing.

---

### 5. What is wrong with what you are handing in?

The main limitation is that the ticket export does not contain a dedicated refund-event timestamp.

For monthly reporting, the current pipeline therefore assigns the refund to the month of the ticket's `created_at` timestamp.

This is a reporting approximation and should be replaced with the actual refund-event timestamp if Finance has access to it.

The reason-code classifier is also intentionally conservative. Ambiguous cases are sent to review rather than being automatically reclassified.

---

### 6. What did you deliberately leave out, and why?

I deliberately did not build a fully automated LLM-based reason-code replacement system.

The available evidence is not strong enough to safely overwrite the agent-selected reason code for every ticket. Instead, deterministic data cleaning and reconciliation are performed first, with rule-based screening used to identify records requiring review.

I also did not attempt to rank agents by "bad" or "good" refund behaviour because raw refund volume is affected by team role, workload, ticket mix, and the policy's operating model.

---

### 7. Did you build or find anything nobody asked for?

Yes.

The pipeline identifies additional operational review signals:

- Refund + replacement combinations, which the policy says should not normally occur for the same order.
- GW-OTHER refunds above the ₹500 goodwill-credit cap as review candidates.
- Potential reason-code mismatches based on ticket evidence.
- Migration duplicate records.
- Legacy monetary-unit inconsistencies.
- Exact reconciliation across monthly, reason-code, and agent reporting.

These checks help explain why the original Finance export was materially inflated.

---

### 8. AI assistance

AI assistance was used during development for:

- Structuring the analysis workflow.
- Writing and debugging Python code.
- Designing data-quality checks.
- Developing conservative reason-code screening rules.
- Reviewing intermediate outputs and identifying potential edge cases.
- Drafting the business memo and documentation.

AI was not treated as the source of truth for the financial totals. The final totals are generated programmatically from the supplied data and reconciliation checks.

Models/tools used:

- **ChatGPT / GPT-5.6**
- **Python**
- **pandas**
- **NumPy**
- **pypdf**
- **VS Code**

Where AI was less useful: automatic reason-code classification produced ambiguous cases and potential false positives, so the final pipeline deliberately keeps uncertain cases in review rather than automatically changing the recorded code.

Discarded/changed approach:

- An early broad regex classifier was narrowed to a conservative screening approach because broad keyword matches could produce false positives.
- Agent-level reporting was changed from raw volume comparisons to context-aware reporting because team roles differ.

---

### 9. Screen recording

Recording link:

**[PASTE PUBLIC SCREEN RECORDING LINK HERE]**

---

### 10. Public Google Drive link

**[PASTE PUBLIC GOOGLE DRIVE FOLDER/LINK HERE]**

---

### 11. Monday handover — three things

1. **Use the cleaned canonical refund dataset and reconciled ₹67.10 lakh total as the current reporting baseline.**

2. **Validate the review candidates**, especially refund + replacement cases and GW-OTHER / reason-code screening candidates, before taking corrective action.

3. **Obtain the actual refund-event timestamp** from the source system so monthly Finance reporting can be based on refund date rather than ticket creation date.

---

### 12. Honest hours spent

**[FILL IN ACTUAL HOURS]**

---

### 13. GitHub Repository

**[PASTE PUBLIC GITHUB REPOSITORY LINK HERE]**