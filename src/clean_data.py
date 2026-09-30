import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data")
OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading data...")

tickets = pd.read_csv(DATA_DIR / "tickets.csv")
agents = pd.read_csv(DATA_DIR / "agents.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")

print(f"Tickets loaded:   {len(tickets):,}")
print(f"Agents loaded:    {len(agents):,}")
print(f"Orders loaded:    {len(orders):,}")
print(f"Customers loaded: {len(customers):,}")
print(f"Products loaded:  {len(products):,}")


# ============================================================
# 1. IDENTIFY MIGRATION DUPLICATES
# ============================================================

print("\nChecking migration duplicates...")

duplicate_ids = (
    tickets.groupby("ticket_id")["source_system"]
    .nunique()
)

migration_duplicate_ids = duplicate_ids[
    duplicate_ids > 1
].index

migration_duplicate_rows = tickets[
    tickets["ticket_id"].isin(migration_duplicate_ids)
].copy()

print(
    f"Migration-duplicated ticket IDs: "
    f"{len(migration_duplicate_ids):,}"
)

print(
    f"Rows belonging to migration duplicates: "
    f"{len(migration_duplicate_rows):,}"
)


# ============================================================
# 2. CREATE CANONICAL TICKET DATASET
# ============================================================

# The dataset contains one helpdesk row and one legacy_fd row
# for each migrated duplicate ticket.
#
# We keep the helpdesk representation where available.
# Legacy-only tickets remain and are normalized below.

tickets["source_priority"] = tickets["source_system"].map(
    {
        "helpdesk": 1,
        "legacy_fd": 2,
    }
)

tickets = tickets.sort_values(
    ["ticket_id", "source_priority"]
)

canonical = tickets.drop_duplicates(
    subset="ticket_id",
    keep="first"
).copy()

print(
    f"Canonical tickets after deduplication: "
    f"{len(canonical):,}"
)


# ============================================================
# 3. NORMALIZE REFUND AMOUNTS
# ============================================================

print("\nNormalizing refund amounts...")

canonical["refund_amount_raw"] = canonical[
    "refund_amount_inr"
]

canonical["refund_amount_clean_inr"] = canonical[
    "refund_amount_inr"
]

legacy_mask = canonical["source_system"] == "legacy_fd"

canonical.loc[
    legacy_mask,
    "refund_amount_clean_inr"
] = (
    canonical.loc[
        legacy_mask,
        "refund_amount_clean_inr"
    ] / 100
)

print(
    "Legacy refund amounts converted using "
    "Freshdesk native-unit / 100 rule."
)


# ============================================================
# 4. PARSE DATES
# ============================================================

date_columns = [
    "created_at",
    "first_response_at",
    "resolved_at",
]

for column in date_columns:
    canonical[column] = pd.to_datetime(
        canonical[column],
        errors="coerce"
    )

agents["from_date"] = pd.to_datetime(
    agents["from_date"],
    errors="coerce"
)

agents["to_date"] = pd.to_datetime(
    agents["to_date"],
    errors="coerce"
)


# ============================================================
# 5. DATE-AWARE AGENT MATCHING
# ============================================================

print("\nMatching agents to roster assignments...")

agent_lookup = agents[
    [
        "agent_id",
        "name",
        "site",
        "team",
        "shift",
        "tier",
        "from_date",
        "to_date",
    ]
].copy()

canonical["agent_roster_matches"] = 0

canonical["agent_name"] = pd.NA
canonical["agent_site"] = pd.NA
canonical["agent_team"] = pd.NA
canonical["agent_shift"] = pd.NA
canonical["agent_tier"] = pd.NA

for idx, row in canonical.iterrows():

    agent_rows = agent_lookup[
        agent_lookup["agent_id"] == row["agent_id"]
    ]

    valid_rows = agent_rows[
        (agent_rows["from_date"] <= row["created_at"])
        &
        (
            agent_rows["to_date"].isna()
            |
            (agent_rows["to_date"] >= row["created_at"])
        )
    ]

    canonical.at[
        idx,
        "agent_roster_matches"
    ] = len(valid_rows)

    if len(valid_rows) == 1:

        agent = valid_rows.iloc[0]

        canonical.at[
            idx,
            "agent_name"
        ] = agent["name"]

        canonical.at[
            idx,
            "agent_site"
        ] = agent["site"]

        canonical.at[
            idx,
            "agent_team"
        ] = agent["team"]

        canonical.at[
            idx,
            "agent_shift"
        ] = agent["shift"]

        canonical.at[
            idx,
            "agent_tier"
        ] = agent["tier"]


# ============================================================
# 6. JOIN ORDER DATA
# ============================================================

print("\nJoining order data...")

order_columns = [
    "order_id",
    "customer_id",
    "sku",
    "order_date",
    "qty",
    "order_value_inr",
    "lot_code",
]

orders_for_join = orders[order_columns].copy()

orders_for_join = orders_for_join.rename(
    columns={
        "sku": "order_sku",
        "customer_id": "order_customer_id",
        "order_value_inr": "order_value_joined_inr",
    }
)

canonical = canonical.merge(
    orders_for_join,
    on="order_id",
    how="left",
)


# ============================================================
# 7. FALLBACK ORDER MATCH
# ============================================================

# README says:
# If order_id is blank, use customer_id + product_sku.

missing_order_mask = canonical["order_id"].isna()

fallback_orders = orders[
    [
        "customer_id",
        "sku",
        "order_id",
        "order_date",
        "qty",
        "order_value_inr",
        "lot_code",
    ]
].rename(
    columns={
        "sku": "product_sku",
        "order_id": "fallback_order_id",
        "order_value_inr": "fallback_order_value_inr",
    }
)

fallback_orders = fallback_orders.drop_duplicates(
    subset=["customer_id", "product_sku"]
)

fallback_match = canonical.loc[
    missing_order_mask,
    [
        "customer_id",
        "product_sku",
    ]
].merge(
    fallback_orders,
    on=["customer_id", "product_sku"],
    how="left",
)

canonical.loc[
    missing_order_mask,
    "fallback_order_id"
] = fallback_match["fallback_order_id"].values

canonical.loc[
    missing_order_mask,
    "fallback_order_value_inr"
] = fallback_match[
    "fallback_order_value_inr"
].values


# ============================================================
# 8. JOIN PRODUCT DATA
# ============================================================

print("\nJoining product data...")

product_columns = [
    "sku",
    "product_name",
    "family",
    "unit_cost_inr",
    "retail_price_inr",
    "warranty_months",
]

products_for_join = products[
    product_columns
].rename(
    columns={
        "sku": "product_sku"
    }
)

canonical = canonical.merge(
    products_for_join,
    on="product_sku",
    how="left",
)


# ============================================================
# 9. QUALITY / POLICY FLAGS
# ============================================================

print("\nCreating policy and quality flags...")

canonical["has_refund"] = (
    canonical["refund_amount_clean_inr"].notna()
    &
    (canonical["refund_amount_clean_inr"] > 0)
)

canonical["refund_and_replacement"] = (
    canonical["has_refund"]
    &
    (canonical["replacement_issued"] == "Y")
)

canonical["goodwill_over_500"] = (
    (canonical["refund_reason_code"] == "GW-OTHER")
    &
    canonical["has_refund"]
    &
    (canonical["refund_amount_clean_inr"] > 500)
)

canonical["refund_missing_reason"] = (
    canonical["has_refund"]
    &
    canonical["refund_reason_code"].isna()
)

canonical["refund_exceeds_order_value"] = (
    canonical["has_refund"]
    &
    canonical["order_value_joined_inr"].notna()
    &
    (
        canonical["refund_amount_clean_inr"]
        > canonical["order_value_joined_inr"]
    )
)

canonical["agent_roster_unmatched"] = (
    canonical["agent_roster_matches"] != 1
)


# ============================================================
# 10. SAVE CLEAN DATA
# ============================================================

output_file = OUT_DIR / "clean_tickets.csv"

canonical.to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)

print(f"Canonical tickets: {len(canonical):,}")
print(f"Refund tickets: {(canonical['has_refund']).sum():,}")
print(
    "Refund + replacement:",
    int(canonical["refund_and_replacement"].sum())
)
print(
    "GW-OTHER > ₹500:",
    int(canonical["goodwill_over_500"].sum())
)
print(
    "Refund missing reason:",
    int(canonical["refund_missing_reason"].sum())
)
print(
    "Refund > order value:",
    int(canonical["refund_exceeds_order_value"].sum())
)
print(
    "Agent roster unmatched:",
    int(canonical["agent_roster_unmatched"].sum())
)

print(f"\nSaved to: {output_file}")