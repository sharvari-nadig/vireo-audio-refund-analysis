# Vireo Audio — Refund Reporting Review

**To:** Arjun Mehta, Finance Controller

**Subject:** Monthly refund reporting — corrected totals, reason codes and agent view

**Period:** January 2025 – June 2026

## Executive summary

The original export shows **₹23.01 crore** of refunds. After correcting the legacy monetary-unit issue and removing duplicate migration representations, the canonical refund total is **₹67.10 lakh across 2,340 refund tickets**.

The difference is primarily caused by two data-quality issues:

1. **Legacy Freshdesk monetary values** are stored in native units rather than rupees and require division by 100.

2. **638 ticket IDs** appear twice, once as `helpdesk` and once as `legacy_fd`. The helpdesk representation was retained for these migration duplicates.

The final canonical dataset contains **11,600 unique tickets** and reconciles exactly across monthly, reason-code and agent-level refund reports.

## Refund position

| Measure | Value |
|---|---:|
| Raw exported refund value | ₹23.01 crore |
| After legacy amount normalization | ₹70.71 lakh |
| Duplicate migration adjustment | ₹3.61 lakh |
| Final canonical refund value | **₹67.10 lakh** |
| Refund tickets | **2,340** |
| Canonical tickets | **11,600** |

The final total reconciles exactly across all three reporting views: monthly, reason code and resolving agent.

Quarterly canonical refunds were approximately **₹6.10 lakh, ₹7.27 lakh, ₹12.07 lakh, ₹16.28 lakh, ₹12.58 lakh and ₹12.80 lakh** respectively from 2025 Q1 through 2026 Q2.

## Where the refunds are going

The largest recorded reason-code totals are:

| Reason code | Refund value |
|---|---:|
| GW-OTHER | ₹29.07 lakh |
| RETURN-QC-OK | ₹11.81 lakh |
| DUP-PAYMENT | ₹8.85 lakh |
| CANCEL | ₹6.13 lakh |
| DOA-REPL | ₹4.71 lakh |
| WTY-BUYBACK | ₹2.89 lakh |
| PRICE-ADJ | ₹2.07 lakh |
| LOST-TRANSIT | ₹1.57 lakh |

`GW-OTHER` represents about **43% of canonical refund value**, making reason-code quality an important control area.

The agent report should be interpreted in the context of team design. The policy states that the Returns Desk processes the large majority of refunds by design, so raw refund volume should **not** be treated as evidence of inappropriate agent behaviour.

## Control findings

There are **166 canonical tickets** containing both a refund and a replacement. The support policy states that a refund and replacement should not both be issued for the same order; errors are to be escalated to the Team Lead and Finance on the same day.

There are also **879 GW-OTHER refunds above ₹500**. These are review candidates against the ₹500 goodwill-credit cap, but they are **not automatically confirmed policy breaches**, because `GW-OTHER` is defined as "Goodwill/Other" and the data does not independently establish that every such refund was a goodwill credit.

A rule-based screening identified **446 potential reason-code mismatches**, representing **₹12.77 lakh**, or about **19% of canonical refund value**. These are screening candidates rather than confirmed errors.

## Validation

A 120-ticket stratified diagnostic sample was generated to test the reason-code screening workflow. It included potential mismatches, clear classifications and cases requiring review.

An AI-assisted evidence review of this sample classified:

- **55** as correct
- **43** as incorrect
- **22** as ambiguous / insufficient evidence

Of the 98 classifiable cases, 43 were labelled incorrect (**43.9%**).

This is a **diagnostic evaluation of the screening approach, not a population-level error estimate or independent human audit**. The main observed error type was a reason-code mismatch, particularly cases where the recorded `GW-OTHER` code appeared inconsistent with evidence in the customer message or agent notes.

The result supports using the classifier as a **review-screening tool rather than an automatic reason-code correction system**.

## Recommended next actions

1. **Use the canonicalized refund report** for the board pack rather than the raw export.

2. **Review the 166 refund-plus-replacement cases** with Finance and Team Leads.

3. **Review the GW-OTHER population**, especially cases above the goodwill threshold, and improve reason-code selection guidance.

4. **Add a controlled reconciliation step** to future refund reporting so legacy monetary units and migration duplicates cannot inflate totals.

**Important limitation:** the source data does not contain a dedicated refund-event timestamp. Refund month in this analysis is therefore assigned using the ticket's `created_at` timestamp.