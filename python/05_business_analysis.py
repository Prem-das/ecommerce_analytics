import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ANALYTICAL_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "analytical"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_csv(filename):
    """Load an analytical CSV."""
    return pd.read_csv(
        ANALYTICAL_DIR / filename
    )


def save_csv(df, filename):
    """Save an analysis result."""
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False)

    print(f"Saved: {path}")


# ============================================================
# LOAD ANALYTICAL DATA
# ============================================================

print("=" * 70)
print("LOADING ANALYTICAL DATA")
print("=" * 70)

fact_orders = load_csv(
    "fact_orders.csv"
)

fact_order_items = load_csv(
    "fact_order_items.csv"
)

dim_customers = load_csv(
    "dim_customers.csv"
)

dim_products = load_csv(
    "dim_products.csv"
)

dim_sellers = load_csv(
    "dim_sellers.csv"
)


print("Analytical data loaded successfully.")


# ============================================================
# DATE CONVERSION
# ============================================================

fact_orders["order_purchase_timestamp"] = pd.to_datetime(
    fact_orders["order_purchase_timestamp"],
    errors="coerce"
)


# ============================================================
# 1. EXECUTIVE KPIs
# ============================================================

print("\n" + "=" * 70)
print("1. EXECUTIVE KPIs")
print("=" * 70)


total_revenue = fact_orders[
    "order_revenue"
].sum()

total_freight = fact_orders[
    "order_freight"
].sum()

total_order_value = fact_orders[
    "order_total_value"
].sum()

total_orders = fact_orders[
    "order_id"
].nunique()

total_items = fact_order_items[
    ["order_id", "order_item_id"]
].drop_duplicates().shape[0]

unique_customers = dim_customers[
    "customer_unique_id"
].nunique()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

average_order_value_with_freight = (
    total_order_value / total_orders
    if total_orders > 0
    else 0
)

freight_percentage = (
    total_freight / total_revenue * 100
    if total_revenue > 0
    else 0
)


print(f"Total revenue              : R$ {total_revenue:,.2f}")
print(f"Total freight              : R$ {total_freight:,.2f}")
print(f"Total order value          : R$ {total_order_value:,.2f}")
print(f"Total orders               : {total_orders:,}")
print(f"Total items                : {total_items:,}")
print(f"Unique customers           : {unique_customers:,}")
print(f"Revenue AOV                : R$ {average_order_value:,.2f}")
print(
    f"AOV including freight     : "
    f"R$ {average_order_value_with_freight:,.2f}"
)
print(f"Freight / revenue         : {freight_percentage:.2f}%")


# ============================================================
# 2. REVENUE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("2. REVENUE ANALYSIS")
print("=" * 70)


monthly_revenue = (
    fact_orders
    .dropna(subset=["order_purchase_timestamp"])
    .assign(
        month=lambda df:
        df["order_purchase_timestamp"].dt.to_period("M")
    )
    .groupby("month")
    .agg(
        revenue=("order_revenue", "sum"),
        freight=("order_freight", "sum"),
        orders=("order_id", "nunique")
    )
    .reset_index()
)


monthly_revenue["month"] = (
    monthly_revenue["month"]
    .astype(str)
)

monthly_revenue["aov"] = (
    monthly_revenue["revenue"]
    / monthly_revenue["orders"]
)


monthly_revenue["revenue_growth_pct"] = (
    monthly_revenue["revenue"]
    .pct_change()
    * 100
)


print("\nMonthly revenue:")
print(
    monthly_revenue.to_string(
        index=False
    )
)


save_csv(
    monthly_revenue,
    "monthly_revenue.csv"
)


# ============================================================
# 3. CUSTOMER ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("3. CUSTOMER ANALYSIS")
print("=" * 70)


customer_type_summary = (
    dim_customers
    .groupby("customer_type")
    .agg(
        customers=(
            "customer_unique_id",
            "nunique"
        )
    )
    .reset_index()
)


customer_type_summary["customer_share_pct"] = (
    customer_type_summary["customers"]
    / customer_type_summary["customers"].sum()
    * 100
)


print(
    customer_type_summary.to_string(
        index=False
    )
)


repeat_customers = dim_customers[
    dim_customers["customer_type"] == "repeat"
][
    "customer_unique_id"
].nunique()


repeat_customer_rate = (
    repeat_customers
    / unique_customers
    * 100
)


print(
    f"\nRepeat customer rate: "
    f"{repeat_customer_rate:.2f}%"
)


# ------------------------------------------------------------
# Revenue by customer state
# ------------------------------------------------------------

customer_revenue = (
    fact_orders[
        [
            "order_id",
            "customer_id",
            "order_revenue"
        ]
    ]
    .merge(
        dim_customers[
            [
                "customer_id",
                "customer_state"
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one"
    )
    .groupby("customer_state")
    .agg(
        revenue=("order_revenue", "sum"),
        orders=("order_id", "nunique")
    )
    .reset_index()
)


customer_revenue["aov"] = (
    customer_revenue["revenue"]
    / customer_revenue["orders"]
)


customer_revenue = (
    customer_revenue
    .sort_values(
        "revenue",
        ascending=False
    )
)


print("\nRevenue by state:")
print(
    customer_revenue.head(15).to_string(
        index=False
    )
)


save_csv(
    customer_revenue,
    "revenue_by_customer_state.csv"
)


# ============================================================
# 4. PRODUCT ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. PRODUCT ANALYSIS")
print("=" * 70)


category_analysis = (
    fact_order_items
    .groupby(
        "product_category_name_english",
        dropna=False
    )
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        orders=("order_id", "nunique"),
        items=("order_item_id", "count")
    )
    .reset_index()
)


category_analysis["average_price"] = (
    category_analysis["revenue"]
    / category_analysis["items"]
)


category_analysis["freight_pct"] = (
    category_analysis["freight"]
    / category_analysis["revenue"]
    * 100
)


category_analysis["revenue_share_pct"] = (
    category_analysis["revenue"]
    / category_analysis["revenue"].sum()
    * 100
)


category_analysis = (
    category_analysis
    .sort_values(
        "revenue",
        ascending=False
    )
)


print("\nTop categories by revenue:")

print(
    category_analysis
    .head(15)
    .to_string(index=False)
)


save_csv(
    category_analysis,
    "category_analysis.csv"
)


# ------------------------------------------------------------
# Top products
# ------------------------------------------------------------

product_analysis = (
    fact_order_items
    .groupby("product_id")
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        orders=("order_id", "nunique"),
        items=("order_item_id", "count")
    )
    .reset_index()
)


product_analysis["average_price"] = (
    product_analysis["revenue"]
    / product_analysis["items"]
)


product_analysis = (
    product_analysis
    .sort_values(
        "revenue",
        ascending=False
    )
)


print("\nTop products by revenue:")

print(
    product_analysis.head(20).to_string(
        index=False
    )
)


save_csv(
    product_analysis,
    "product_analysis.csv"
)


# ============================================================
# 5. SELLER ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("5. SELLER ANALYSIS")
print("=" * 70)


seller_analysis = (
    fact_order_items
    .groupby("seller_id")
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        orders=("order_id", "nunique"),
        items=("order_item_id", "count")
    )
    .reset_index()
)


seller_analysis["average_item_price"] = (
    seller_analysis["revenue"]
    / seller_analysis["items"]
)


seller_analysis = (
    seller_analysis
    .sort_values(
        "revenue",
        ascending=False
    )
)


print("\nTop sellers by revenue:")

print(
    seller_analysis.head(20).to_string(
        index=False
    )
)


save_csv(
    seller_analysis,
    "seller_analysis.csv"
)


# ============================================================
# 6. OPERATIONS ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("6. OPERATIONS ANALYSIS")
print("=" * 70)


delivered_orders = fact_orders[
    fact_orders["delivery_days"].notna()
].copy()


average_delivery_days = (
    delivered_orders["delivery_days"]
    .mean()
)


median_delivery_days = (
    delivered_orders["delivery_days"]
    .median()
)


late_orders = delivered_orders[
    delivered_orders["is_late"] == True
]


late_delivery_rate = (
    len(late_orders)
    / len(delivered_orders)
    * 100
)


extreme_orders = delivered_orders[
    delivered_orders["is_extreme_delivery"] == True
]


extreme_delivery_rate = (
    len(extreme_orders)
    / len(delivered_orders)
    * 100
)


print(
    f"Delivered orders          : "
    f"{len(delivered_orders):,}"
)

print(
    f"Average delivery days     : "
    f"{average_delivery_days:.2f}"
)

print(
    f"Median delivery days      : "
    f"{median_delivery_days:.2f}"
)

print(
    f"Late delivery rate        : "
    f"{late_delivery_rate:.2f}%"
)

print(
    f"Extreme delivery rate     : "
    f"{extreme_delivery_rate:.2f}%"
)


# ------------------------------------------------------------
# Delivery performance by state
# ------------------------------------------------------------

delivery_by_state = (
    fact_orders[
        fact_orders["delivery_days"].notna()
    ]
    .merge(
        dim_customers[
            [
                "customer_id",
                "customer_state"
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one"
    )
    .groupby("customer_state")
    .agg(
        orders=("order_id", "nunique"),
        average_delivery_days=(
            "delivery_days",
            "mean"
        ),
        late_orders=(
            "is_late",
            "sum"
        )
    )
    .reset_index()
)


delivery_by_state["late_delivery_rate_pct"] = (
    delivery_by_state["late_orders"]
    / delivery_by_state["orders"]
    * 100
)


delivery_by_state = (
    delivery_by_state
    .sort_values(
        "late_delivery_rate_pct",
        ascending=False
    )
)


print("\nDelivery performance by state:")

print(
    delivery_by_state.to_string(
        index=False
    )
)


save_csv(
    delivery_by_state,
    "delivery_by_state.csv"
)

PROCESSED_DIR = Path("C:/Users/premk/OneDrive/Documents/ecommerce_analytics/data/processed")
reviews = load_csv(
    PROCESSED_DIR / "reviews_clean.csv"
)


# ============================================================
# 7. CUSTOMER EXPERIENCE
# ============================================================

print("\n" + "=" * 70)
print("7. CUSTOMER EXPERIENCE")
print("=" * 70)


# ------------------------------------------------------------
# Review score distribution
# ------------------------------------------------------------

review_score_summary = (
    reviews
    .groupby("review_score")
    .agg(
        reviews=("review_id", "count")
    )
    .reset_index()
)


review_score_summary["review_share_pct"] = (
    review_score_summary["reviews"]
    / review_score_summary["reviews"].sum()
    * 100
)


print("\nReview score distribution:")

print(
    review_score_summary.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# Average review score
# ------------------------------------------------------------

average_review_score = (
    reviews["review_score"]
    .mean()
)


print(
    f"\nAverage review score: "
    f"{average_review_score:.2f}"
)


# ------------------------------------------------------------
# Late delivery vs review score
# ------------------------------------------------------------

order_review = (
    fact_orders[
        [
            "order_id",
            "is_late",
            "delivery_days"
        ]
    ]
    .merge(
        reviews[
            [
                "order_id",
                "review_score"
            ]
        ],
        on="order_id",
        how="inner"
    )
)


late_review_analysis = (
    order_review
    .groupby("is_late")
    .agg(
        orders=("order_id", "nunique"),
        average_review_score=(
            "review_score",
            "mean"
        )
    )
    .reset_index()
)


late_review_analysis["delivery_group"] = (
    late_review_analysis["is_late"]
    .map({
        False: "On time",
        True: "Late"
    })
)


print("\nLate delivery vs review score:")

print(
    late_review_analysis[
        [
            "delivery_group",
            "orders",
            "average_review_score"
        ]
    ].to_string(index=False)
)


save_csv(
    late_review_analysis,
    "late_delivery_vs_reviews.csv"
)


# ------------------------------------------------------------
# Review score by category
# ------------------------------------------------------------

review_category = (
    reviews[
        [
            "order_id",
            "review_score"
        ]
    ]
    .merge(
        fact_order_items[
            [
                "order_id",
                "product_category_name_english"
            ]
        ],
        on="order_id",
        how="inner"
    )
)


review_category = (
    review_category
    .groupby(
        "product_category_name_english",
        dropna=False
    )
    .agg(
        reviews=("review_score", "count"),
        average_review_score=(
            "review_score",
            "mean"
        )
    )
    .reset_index()
)


review_category = (
    review_category
    .sort_values(
        "average_review_score"
    )
)


print("\nCategories with lowest average review scores:")

print(
    review_category.head(15).to_string(
        index=False
    )
)


save_csv(
    review_category,
    "review_by_category.csv"
)


# ============================================================
# FINAL BUSINESS ANALYSIS SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS ANALYSIS SUMMARY")
print("=" * 70)

print(f"""
Revenue:
    R$ {total_revenue:,.2f}

Orders:
    {total_orders:,}

Items:
    {total_items:,}

Unique customers:
    {unique_customers:,}

Revenue AOV:
    R$ {average_order_value:,.2f}

AOV including freight:
    R$ {average_order_value_with_freight:,.2f}

Freight / revenue:
    {freight_percentage:.2f}%

Repeat customer rate:
    {repeat_customer_rate:.2f}%

Average delivery time:
    {average_delivery_days:.2f} days

Median delivery time:
    {median_delivery_days:.2f} days

Late delivery rate:
    {late_delivery_rate:.2f}%

Extreme delivery rate:
    {extreme_delivery_rate:.2f}%

Average review score:
    {average_review_score:.2f}
""")


print("=" * 70)
print("BUSINESS ANALYSIS COMPLETE")
print("=" * 70)

print(f"""
Analysis results saved to:

    {OUTPUT_DIR}
""")

 