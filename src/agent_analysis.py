from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "out"

CLEAN_FILE = OUT_DIR / "clean_tickets.csv"
MISMATCH_FILE = OUT_DIR / "potential_reason_mismatches.csv"

AGENT_OUTPUT = OUT_DIR / "agent_risk_analysis.csv"
TEAM_OUTPUT = OUT_DIR / "team_refund_analysis.csv"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

df = pd.read_csv(CLEAN_FILE)
mismatches = pd.read_csv(MISMATCH_FILE)


# ---------------------------------------------------------
# REFUND TICKETS
# ---------------------------------------------------------

refunds = df[
    df["refund_amount_clean_inr"].fillna(0) > 0
].copy()

refunds["refund_amount_clean_inr"] = pd.to_numeric(
    refunds["refund_amount_clean_inr"],
    errors="coerce"
).fillna(0)


# ---------------------------------------------------------
# MISMATCH INFORMATION
# ---------------------------------------------------------

mismatch_counts = (
    mismatches.groupby("agent_id")
    .agg(
        potential_mismatch_tickets=("ticket_id", "count"),
        potential_mismatch_amount=(
            "refund_amount_clean_inr",
            "sum"
        )
    )
    .reset_index()
)


# ---------------------------------------------------------
# POLICY FLAG COLUMNS
# ---------------------------------------------------------

# GW-OTHER refunds above ₹500 are flagged for review.
# This is a screening flag, not an automatic policy violation.

refunds["gw_other_over_500_flag"] = (
    (refunds["refund_reason_code"] == "GW-OTHER")
    & (refunds["refund_amount_clean_inr"] > 500)
)

refunds["gw_other_over_500_amount_calc"] = (
    refunds["refund_amount_clean_inr"]
    .where(refunds["gw_other_over_500_flag"], 0)
)

# Policy exception: refund + replacement on the same ticket.
refunds["refund_replacement_exception_flag"] = (
    refunds["refund_and_replacement"]
    .fillna(False)
)


# ---------------------------------------------------------
# AGENT-LEVEL ANALYSIS
# ---------------------------------------------------------

agent_summary = (
    refunds.groupby(
        [
            "agent_id",
            "agent_name",
            "agent_team",
            "agent_tier"
        ],
        dropna=False
    )
    .agg(
        refund_tickets=("ticket_id", "count"),

        total_refund_inr=(
            "refund_amount_clean_inr",
            "sum"
        ),

        average_refund_inr=(
            "refund_amount_clean_inr",
            "mean"
        ),

        gw_other_over_500_tickets=(
            "gw_other_over_500_flag",
            "sum"
        ),

        gw_other_over_500_amount=(
            "gw_other_over_500_amount_calc",
            "sum"
        ),

        refund_replacement_exceptions=(
            "refund_replacement_exception_flag",
            "sum"
        )
    )
    .reset_index()
)


# ---------------------------------------------------------
# MERGE MISMATCH INFORMATION
# ---------------------------------------------------------

agent_summary = agent_summary.merge(
    mismatch_counts,
    on="agent_id",
    how="left"
)

agent_summary["potential_mismatch_tickets"] = (
    agent_summary["potential_mismatch_tickets"]
    .fillna(0)
    .astype(int)
)

agent_summary["potential_mismatch_amount"] = (
    agent_summary["potential_mismatch_amount"]
    .fillna(0)
)


# ---------------------------------------------------------
# MISMATCH VALUE %
# ---------------------------------------------------------

agent_summary["mismatch_value_pct"] = (
    agent_summary["potential_mismatch_amount"]
    / agent_summary["total_refund_inr"]
    * 100
)

agent_summary["mismatch_value_pct"] = (
    agent_summary["mismatch_value_pct"]
    .fillna(0)
)


# ---------------------------------------------------------
# SORT
# ---------------------------------------------------------

agent_summary = agent_summary.sort_values(
    "total_refund_inr",
    ascending=False
)


# ---------------------------------------------------------
# SAVE AGENT REPORT
# ---------------------------------------------------------

agent_summary.to_csv(
    AGENT_OUTPUT,
    index=False
)


# ---------------------------------------------------------
# TEAM SUMMARY
# ---------------------------------------------------------

team_summary = (
    agent_summary.groupby(
        [
            "agent_team",
            "agent_tier"
        ],
        dropna=False
    )
    .agg(
        agents=("agent_id", "nunique"),

        refund_tickets=(
            "refund_tickets",
            "sum"
        ),

        total_refund_inr=(
            "total_refund_inr",
            "sum"
        ),

        mismatch_tickets=(
            "potential_mismatch_tickets",
            "sum"
        ),

        mismatch_amount=(
            "potential_mismatch_amount",
            "sum"
        ),

        refund_replacement_exceptions=(
            "refund_replacement_exceptions",
            "sum"
        )
    )
    .reset_index()
)

team_summary = team_summary.sort_values(
    "total_refund_inr",
    ascending=False
)


# ---------------------------------------------------------
# SAVE TEAM REPORT
# ---------------------------------------------------------

team_summary.to_csv(
    TEAM_OUTPUT,
    index=False
)


# ---------------------------------------------------------
# PRINT AGENT REPORT
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("AGENT REFUND ANALYSIS")
print("=" * 80)

display_agent = agent_summary.copy()

display_agent["total_refund_inr"] = (
    display_agent["total_refund_inr"]
    .map(lambda x: f"₹{x:,.0f}")
)

display_agent["average_refund_inr"] = (
    display_agent["average_refund_inr"]
    .map(lambda x: f"₹{x:,.0f}")
)

display_agent["gw_other_over_500_amount"] = (
    display_agent["gw_other_over_500_amount"]
    .map(lambda x: f"₹{x:,.0f}")
)

display_agent["potential_mismatch_amount"] = (
    display_agent["potential_mismatch_amount"]
    .map(lambda x: f"₹{x:,.0f}")
)

display_agent["mismatch_value_pct"] = (
    display_agent["mismatch_value_pct"]
    .map(lambda x: f"{x:.1f}%")
)

print("\nALL AGENTS BY REFUND VALUE")

print(
    display_agent.to_string(
        index=False
    )
)


# ---------------------------------------------------------
# PRINT TEAM SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("TEAM SUMMARY")
print("=" * 80)

# Create a compact, readable console table instead of
# relying on pandas' automatic column-width formatting.

team_display = team_summary.copy()

team_display["total_refund_inr"] = (
    team_display["total_refund_inr"]
    .map(lambda x: f"₹{x:,.0f}")
)

team_display["mismatch_amount"] = (
    team_display["mismatch_amount"]
    .map(lambda x: f"₹{x:,.0f}")
)

team_display = team_display.rename(
    columns={
        "agent_team": "Team",
        "agent_tier": "Tier",
        "agents": "Agents",
        "refund_tickets": "Refund Tickets",
        "total_refund_inr": "Total Refund",
        "mismatch_tickets": "Potential Mismatches",
        "mismatch_amount": "Mismatch Amount",
        "refund_replacement_exceptions": "Refund+Replacement"
    }
)

print(
    team_display[
        [
            "Team",
            "Tier",
            "Agents",
            "Refund Tickets",
            "Total Refund",
            "Potential Mismatches",
            "Mismatch Amount",
            "Refund+Replacement"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# RECONCILIATION
# ---------------------------------------------------------

clean_total = refunds["refund_amount_clean_inr"].sum()
agent_total = agent_summary["total_refund_inr"].sum()

difference = clean_total - agent_total


print("\n" + "=" * 80)
print("RECONCILIATION CHECK")
print("=" * 80)

print(f"Clean refund total:      ₹{clean_total:,.2f}")
print(f"Agent analysis total:    ₹{agent_total:,.2f}")
print(f"Difference:              ₹{difference:,.2f}")

if abs(difference) < 0.01:
    print("STATUS: PASS")
else:
    print("STATUS: FAIL")


# ---------------------------------------------------------
# FILES
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(AGENT_OUTPUT)
print(TEAM_OUTPUT)