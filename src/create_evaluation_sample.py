import pandas as pd
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

INPUT = Path("out/classified_refunds.csv")
OUTPUT = Path("eval/manual_review_sample.csv")

SAMPLE_SIZE = 120


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT)

df = df[df["has_refund"] == True].copy()


# ============================================================
# CREATE STRATA
# ============================================================

# We want the sample to contain:
# 1. Potential mismatches
# 2. Clear classifications
# 3. REVIEW cases
# 4. Different refund reason codes


df["review_group"] = "Other"

df.loc[
    df["reason_mismatch"] == True,
    "review_group"
] = "Potential mismatch"

df.loc[
    (df["reason_mismatch"] == False)
    & (df["predicted_reason"] != "REVIEW"),
    "review_group"
] = "Clear classification"

df.loc[
    df["predicted_reason"] == "REVIEW",
    "review_group"
] = "REVIEW"


# ============================================================
# STRATIFIED SAMPLING
# ============================================================

samples = []

groups = [
    ("Potential mismatch", 50),
    ("Clear classification", 40),
    ("REVIEW", 30),
]


for group_name, n in groups:

    subset = df[
        df["review_group"] == group_name
    ]

    n = min(n, len(subset))

    if n > 0:
        samples.append(
            subset.sample(
                n=n,
                random_state=42
            )
        )


sample = pd.concat(
    samples,
    ignore_index=True
)


# ============================================================
# ADD MANUAL REVIEW COLUMNS
# ============================================================

sample["manual_correct_reason"] = ""

sample["manual_decision"] = ""

sample["error_type"] = ""

sample["review_notes"] = ""


# ============================================================
# SELECT USEFUL COLUMNS
# ============================================================

columns = [
    "ticket_id",
    "created_at",
    "agent_id",
    "agent_name",
    "agent_team",
    "refund_amount_clean_inr",
    "refund_reason_code",
    "predicted_reason",
    "evidence_match_count",
    "reason_mismatch",
    "review_group",
    "customer_message",
    "agent_notes",
    "manual_correct_reason",
    "manual_decision",
    "error_type",
    "review_notes",
]


sample = sample[columns]


# ============================================================
# SORT FOR EASY REVIEW
# ============================================================

sample = sample.sort_values(
    [
        "review_group",
        "refund_reason_code"
    ]
)


# ============================================================
# SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

sample.to_csv(
    OUTPUT,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MANUAL EVALUATION SAMPLE")
print("=" * 70)

print(
    f"Total refund tickets available: {len(df)}"
)

print(
    f"Evaluation sample created: {len(sample)}"
)

print("\nSample by review group:")

print(
    sample["review_group"]
    .value_counts()
    .to_string()
)

print("\nSample by recorded reason:")

print(
    sample["refund_reason_code"]
    .value_counts()
    .to_string()
)

print("\nSaved:")
print("eval/manual_review_sample.csv")