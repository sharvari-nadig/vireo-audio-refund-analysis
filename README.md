# Vireo Audio — Refund Analysis Tool

## Overview

This project analyzes Vireo Audio support-ticket data to answer the Finance question:

> How much money is being refunded, for what reasons, and which agents are associated with those refunds?

The pipeline cleans the exported data, corrects identified data-quality issues, produces refund reports by month, reason and agent, and flags cases requiring further review.

## Business Result

The raw export contains **₹23,01,24,081 (₹23.01 crore)** in reported refund amounts.

After:

- Normalizing legacy Freshdesk monetary values using the documented `/100` rule
- Removing migration duplicate representations
- Retaining the current helpdesk record where both systems contain the same ticket

the canonical dataset contains:

- **11,600 canonical tickets**
- **2,340 refund tickets**
- **₹67,09,932 (₹67.10 lakh) total refunds**

The final amount reconciles exactly across monthly, reason-code and agent reports.

**Reconciliation difference: ₹0**

## Key Data Checks

| Check | Result |
|---|---:|
| Source tickets | 12,238 |
| Canonical tickets | 11,600 |
| Migration-duplicated ticket IDs | 638 |
| Refund tickets | 2,340 |
| Refund + replacement cases | 166 |
| GW-OTHER refunds > ₹500 | 879 |
| Missing refund reason | 0 |
| Refund > order value | 0 |
| Unmatched agent roster | 0 |

## Refunds by Reason

| Reason | Tickets | Amount |
|---|---:|---:|
| GW-OTHER | 991 | ₹29,07,036 |
| RETURN-QC-OK | 452 | ₹11,81,386 |
| DUP-PAYMENT | 321 | ₹8,84,586 |
| CANCEL | 222 | ₹6,12,950 |
| DOA-REPL | 147 | ₹4,71,190 |
| WTY-BUYBACK | 89 | ₹2,89,154 |
| PRICE-ADJ | 71 | ₹2,07,073 |
| LOST-TRANSIT | 47 | ₹1,56,557 |

## Reason-Code Screening

The classifier uses customer messages and agent notes to identify potential differences between the recorded reason and the available evidence.

Current screening:

- 2,340 refund tickets analysed
- 952 clear classifications
- 1,388 sent to REVIEW
- 446 potential reason-code mismatches
- ₹12,77,100 associated with potential mismatches

The 446 cases are **potential mismatches, not confirmed errors**. They require review before being treated as actual coding errors.

## Agent Analysis

The agent analysis reports:

- Refund ticket count
- Total refund value
- Average refund value
- GW-OTHER refunds above ₹500
- Refund + replacement exceptions
- Potential reason-code mismatches

Agent analysis also reconciles to the cleaned refund total:

```text
Clean refund total:      ₹6,709,932.00
Agent analysis total:    ₹6,709,932.00
Difference:              ₹0.00
STATUS: PASS