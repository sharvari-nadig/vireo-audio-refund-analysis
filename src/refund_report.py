import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

INPUT = Path("out/clean_tickets.csv")
OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD CLEAN DATA
# ============================================================

df = pd.read_csv(INPUT)

df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce"
)

refunds = df[
    df["has_refund"] == True
].copy()


# ============================================================
# MONTH
# ============================================================

refunds["month"] = refunds[
    "created_at"
].dt.to_period("M").astype(str)


# ============================================================
# TOTAL REFUND
# ============================================================

total_refund = refunds[
    "refund_amount_clean_inr"
].sum()

refund_count = len(refunds)


# ============================================================
# MONTHLY TOTAL
# ============================================================

monthly_total = (
    refunds
    .groupby("month")
    .agg(
        refund_tickets=("ticket_id", "nunique"),
        refund_amount_inr=(
            "refund_amount_clean_inr",
            "sum"
        )
    )
    .reset_index()
)


# ============================================================
# MONTH × REASON
# ============================================================

monthly_reason = (
    refunds
    .groupby(
        ["month", "refund_reason_code"],
        dropna=False
    )
    .agg(
        refund_tickets=("ticket_id", "nunique"),
        refund_amount_inr=(
            "refund_amount_clean_inr",
            "sum"
        )
    )
    .reset_index()
)


# ============================================================
# MONTH × AGENT
# ============================================================

monthly_agent = (
    refunds
    .groupby(
        ["month", "agent_id", "agent_name", "agent_team", "agent_tier"],
        dropna=False
    )
    .agg(
        refund_tickets=("ticket_id", "nunique"),
        refund_amount_inr=(
            "refund_amount_clean_inr",
            "sum"
        )
    )
    .reset_index()
)


# ============================================================
# REASON TOTAL
# ============================================================

reason_total = (
    refunds
    .groupby("refund_reason_code")
    .agg(
        refund_tickets=("ticket_id", "nunique"),
        refund_amount_inr=(
            "refund_amount_clean_inr",
            "sum"
        )
    )
    .reset_index()
    .sort_values(
        "refund_amount_inr",
        ascending=False
    )
)


# ============================================================
# AGENT TOTAL
# ============================================================

agent_total = (
    refunds
    .groupby(
        ["agent_id", "agent_name", "agent_team", "agent_tier"],
        dropna=False
    )
    .agg(
        refund_tickets=("ticket_id", "nunique"),
        refund_amount_inr=(
            "refund_amount_clean_inr",
            "sum"
        )
    )
    .reset_index()
    .sort_values(
        "refund_amount_inr",
        ascending=False
    )
)


# ============================================================
# RECONCILIATION
# ============================================================

monthly_sum = monthly_total[
    "refund_amount_inr"
].sum()

reason_sum = reason_total[
    "refund_amount_inr"
].sum()

agent_sum = agent_total[
    "refund_amount_inr"
].sum()


reconciliation = pd.DataFrame(
    {
        "measure": [
            "Clean refund ticket count",
            "Clean refund amount",
            "Monthly report total",
            "Reason report total",
            "Agent report total",
            "Monthly difference",
            "Reason difference",
            "Agent difference",
        ],
        "value": [
            refund_count,
            total_refund,
            monthly_sum,
            reason_sum,
            agent_sum,
            total_refund - monthly_sum,
            total_refund - reason_sum,
            total_refund - agent_sum,
        ],
    }
)


# ============================================================
# SAVE REPORTS
# ============================================================

monthly_total.to_csv(
    OUT_DIR / "monthly_refunds.csv",
    index=False
)

monthly_reason.to_csv(
    OUT_DIR / "monthly_refunds_by_reason.csv",
    index=False
)

monthly_agent.to_csv(
    OUT_DIR / "monthly_refunds_by_agent.csv",
    index=False
)

reason_total.to_csv(
    OUT_DIR / "refunds_by_reason_total.csv",
    index=False
)

agent_total.to_csv(
    OUT_DIR / "refunds_by_agent_total.csv",
    index=False
)

reconciliation.to_csv(
    OUT_DIR / "reconciliation.csv",
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("REFUND REPORT")
print("=" * 70)

print(f"\nRefund tickets: {refund_count:,}")
print(f"Total refunds: ₹{total_refund:,.2f}")

print("\nMONTHLY REFUNDS")
print(monthly_total.to_string(index=False))

print("\nREFUNDS BY REASON")
print(reason_total.to_string(index=False))

print("\nTOP 20 AGENTS BY REFUND VALUE")
print(
    agent_total
    .head(20)
    .to_string(index=False)
)

print("\nRECONCILIATION")
print(reconciliation.to_string(index=False))

print("\nReports saved in:")
print(OUT_DIR)