import pandas as pd
from pathlib import Path
import re


# ============================================================
# PATHS
# ============================================================

INPUT = Path("out/clean_tickets.csv")
OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

refunds = df[
    df["has_refund"] == True
].copy()

refunds["evidence_text"] = (
    refunds["customer_message"].fillna("")
    + " "
    + refunds["agent_notes"].fillna("")
).str.lower()


# ============================================================
# RULES
# ============================================================

rules = {
    "CANCEL": [
        r"cancelled before dispatch",
        r"canceled before dispatch",
        r"cancellation request",
        r"cancel order",
        r"order cancellation",
        r"cancelled.*before.*dispatch",
        r"canceled.*before.*dispatch",
    ],

    "DUP-PAYMENT": [
        r"duplicate payment",
        r"charged twice",
        r"payment debited.*no order",
        r"debited.*without.*order",
        r"failed order after payment",
        r"failed order.*payment",
        r"no order.*payment",
    ],

    "DOA-REPL": [
        r"dead on arrival",
        r"\bdoa\b",
        r"not working on arrival",
        r"arrived.*not working",
    ],

    "LOST-TRANSIT": [
        r"lost in transit",
        r"lost.*shipment",
        r"shipment.*lost",
        r"undelivered",
        r"not delivered",
        r"damaged in transit",
        r"transit damage",
    ],

    "PRICE-ADJ": [
        r"price adjustment",
        r"price difference",
        r"coupon",
        r"promo code",
        r"promotional price",
        r"wrong price",
    ],

    "RETURN-QC-OK": [
        r"reverse pickup qc",
        r"pickup.*qc",
        r"qc.*pickup",
        r"return.*qc",
        r"qc.*return",
        r"return received.*qc",
        r"passed qc",
    ],

    "WTY-BUYBACK": [
        r"warranty buyback",
        r"buyback",
    ],
}


# ============================================================
# CLASSIFICATION FUNCTION
# ============================================================

def classify_reason(text):

    matches = []

    for reason, patterns in rules.items():

        for pattern in patterns:

            if re.search(pattern, text):

                matches.append(reason)
                break

    # No clear evidence
    if len(matches) == 0:
        return "REVIEW", 0

    # One clear reason
    if len(matches) == 1:
        return matches[0], 1

    # Multiple competing signals
    return "REVIEW", len(matches)


# ============================================================
# APPLY CLASSIFIER
# ============================================================

results = refunds["evidence_text"].apply(
    classify_reason
)

refunds["predicted_reason"] = results.apply(
    lambda x: x[0]
)

refunds["evidence_match_count"] = results.apply(
    lambda x: x[1]
)


# ============================================================
# COMPARE WITH RECORDED CODE
# ============================================================

refunds["reason_mismatch"] = (
    (refunds["predicted_reason"] != "REVIEW")
    &
    (
        refunds["predicted_reason"]
        != refunds["refund_reason_code"]
    )
)


# ============================================================
# POTENTIAL MISMATCHES
# ============================================================

mismatches = refunds[
    refunds["reason_mismatch"]
].copy()


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("REASON CLASSIFICATION")
print("=" * 70)

print(f"\nRefund tickets analysed: {len(refunds):,}")

print(
    "\nClear classifications:",
    int(
        (
            refunds["predicted_reason"] != "REVIEW"
        ).sum()
    )
)

print(
    "Sent to REVIEW:",
    int(
        (
            refunds["predicted_reason"] == "REVIEW"
        ).sum()
    )
)

print(
    "\nPotential reason-code mismatches:",
    len(mismatches)
)

print(
    "Potential mismatch amount:",
    f"₹{mismatches['refund_amount_clean_inr'].sum():,.2f}"
)


# ============================================================
# PREDICTED REASON DISTRIBUTION
# ============================================================

print("\nPREDICTED REASONS")

print(
    refunds["predicted_reason"]
    .value_counts()
    .to_string()
)


# ============================================================
# MISMATCH BY RECORDED CODE
# ============================================================

print("\nMISMATCHES BY RECORDED CODE")

print(
    mismatches[
        "refund_reason_code"
    ].value_counts()
    .to_string()
)


# ============================================================
# MISMATCHES BY PREDICTED CODE
# ============================================================

print("\nMISMATCHES BY PREDICTED CODE")

print(
    mismatches[
        "predicted_reason"
    ].value_counts()
    .to_string()
)


# ============================================================
# TOP MISMATCH EXAMPLES
# ============================================================

print("\nTOP POTENTIAL MISMATCHES")

columns = [
    "ticket_id",
    "refund_amount_clean_inr",
    "refund_reason_code",
    "predicted_reason",
    "agent_id",
    "agent_name",
    "agent_team",
    "agent_notes",
]

print(
    mismatches[
        columns
    ]
    .sort_values(
        "refund_amount_clean_inr",
        ascending=False
    )
    .head(30)
    .to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

refunds.to_csv(
    OUT_DIR / "classified_refunds.csv",
    index=False
)

mismatches.to_csv(
    OUT_DIR / "potential_reason_mismatches.csv",
    index=False
)

print("\nSaved:")
print("out/classified_refunds.csv")
print("out/potential_reason_mismatches.csv")