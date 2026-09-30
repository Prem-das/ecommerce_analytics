# ================================================================
# 06_advanced_business_analysis.py
# ADVANCED BUSINESS ANALYSIS
# ================================================================

import pandas as pd
import numpy as np
from pathlib import Path


# ================================================================
# CONFIGURATION
# ================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis" / "advanced"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)



# ================================================================
# HELPER FUNCTIONS
# ================================================================

def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def load_csv(filename):
    path = PROCESSED_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"\nFile not found:\n{path}\n\n"
            f"Expected file: {filename}"
        )

    return pd.read_csv(path)


def save_csv(df, filename):
    path = ANALYSIS_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved: {path}")


def require_columns(df, columns, table_name):
    missing = [col for col in columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"\nMissing columns in {table_name}: {missing}\n"
            f"Available columns:\n{list(df.columns)}"
        )


# ================================================================
# 1. LOAD DATA
# ================================================================

print_header("LOADING PROCESSED DATA")

customers = load_csv("customers_clean.csv")
orders = load_csv("orders_clean.csv")
order_items = load_csv("order_items_clean.csv")
payments = load_csv("payments_clean.csv")
reviews = load_csv("reviews_clean.csv")
products = load_csv("products_enriched.csv")
sellers = load_csv("sellers_clean.csv")

print("All processed datasets loaded successfully.")


# ================================================================
# 2. VALIDATE REQUIRED COLUMNS
# ================================================================

print_header("VALIDATING DATA STRUCTURE")

require_columns(
    customers,
    [
        "customer_id",
        "customer_unique_id",
        "customer_state",
        "customer_city"
    ],
    "customers"
)

require_columns(
    orders,
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp"
    ],
    "orders"
)

require_columns(
    order_items,
    [
        "order_id",
        "product_id",
        "seller_id",
        "price",
        "freight_value"
    ],
    "order_items"
)

require_columns(
    payments,
    [
        "order_id",
        "payment_type",
        "payment_value"
    ],
    "payments"
)

require_columns(
    reviews,
    [
        "order_id",
        "review_score"
    ],
    "reviews"
)

require_columns(
    products,
    [
        "product_id"
    ],
    "products"
)

require_columns(
    sellers,
    [
        "seller_id"
    ],
    "sellers"
)

print("All required columns are present.")


# ================================================================
# 3. DATE STANDARDIZATION
# ================================================================

print_header("STANDARDIZING DATES")

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    if col in orders.columns:
        orders[col] = pd.to_datetime(
            orders[col],
            errors="coerce"
        )

print("Date columns standardized.")


# ================================================================
# 4. CREATE ORDER-LEVEL REVENUE TABLE
# ================================================================

print_header("CREATING ORDER-LEVEL REVENUE DATA")

order_revenue = (
    order_items
    .groupby("order_id", as_index=False)
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        items=("order_id", "size"),
        unique_products=("product_id", "nunique"),
        unique_sellers=("seller_id", "nunique")
    )
)

print(f"Order-level revenue records: {len(order_revenue):,}")


# ================================================================
# 5. CREATE CUSTOMER-ORDER ANALYTICAL TABLE
# ================================================================

print_header("CREATING CUSTOMER-ORDER ANALYTICAL TABLE")

customer_lookup = customers[
    [
        "customer_id",
        "customer_unique_id",
        "customer_state",
        "customer_city"
    ]
].drop_duplicates("customer_id")


orders_analysis = orders.merge(
    customer_lookup,
    on="customer_id",
    how="left",
    validate="many_to_one"
)

orders_analysis = orders_analysis.merge(
    order_revenue,
    on="order_id",
    how="left",
    validate="one_to_one"
)

orders_analysis["revenue"] = orders_analysis["revenue"].fillna(0)
orders_analysis["freight"] = orders_analysis["freight"].fillna(0)
orders_analysis["items"] = orders_analysis["items"].fillna(0)

orders_analysis["total_order_value"] = (
    orders_analysis["revenue"]
    + orders_analysis["freight"]
)

print(f"Analytical order rows: {len(orders_analysis):,}")


# ================================================================
# 6. DELIVERY METRICS
# ================================================================

print_header("CREATING DELIVERY METRICS")

orders_analysis["delivery_days"] = (
    orders_analysis["order_delivered_customer_date"]
    - orders_analysis["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders_analysis["estimated_days"] = (
    orders_analysis["order_estimated_delivery_date"]
    - orders_analysis["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders_analysis["delivery_delay_days"] = (
    orders_analysis["order_delivered_customer_date"]
    - orders_analysis["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

orders_analysis["is_late"] = (
    orders_analysis["delivery_delay_days"] > 0
)

orders_analysis["is_delivered"] = (
    orders_analysis["order_delivered_customer_date"].notna()
)

orders_analysis["is_extreme_delivery"] = (
    orders_analysis["delivery_days"] > 90
)

valid_delivery = orders_analysis[
    orders_analysis["is_delivered"]
    & orders_analysis["delivery_days"].notna()
    & (orders_analysis["delivery_days"] >= 0)
].copy()

print(
    f"Valid delivered orders: "
    f"{len(valid_delivery):,}"
)

print(
    f"Average delivery days: "
    f"{valid_delivery['delivery_days'].mean():.2f}"
)

print(
    f"Median delivery days: "
    f"{valid_delivery['delivery_days'].median():.2f}"
)


# ================================================================
# 7. CUSTOMER RFM ANALYSIS
# ================================================================

print_header("CUSTOMER RFM ANALYSIS")

customer_orders = orders_analysis[
    orders_analysis["customer_unique_id"].notna()
].copy()

reference_date = (
    customer_orders["order_purchase_timestamp"].max()
    + pd.Timedelta(days=1)
)

rfm = (
    customer_orders
    .groupby("customer_unique_id")
    .agg(
        last_purchase=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        total_freight=("freight", "sum")
    )
    .reset_index()
)

rfm["recency_days"] = (
    reference_date - rfm["last_purchase"]
).dt.days

rfm["monetary"] = rfm["monetary"].round(2)
rfm["total_freight"] = rfm["total_freight"].round(2)

# Quantile scoring
rfm["R_score"] = pd.qcut(
    rfm["recency_days"].rank(method="first"),
    5,
    labels=[5, 4, 3, 2, 1]
).astype(int)

rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["M_score"] = pd.qcut(
    rfm["monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["RFM_score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
    + rfm["M_score"].astype(str)
)

def classify_customer(row):

    if (
        row["R_score"] >= 4
        and row["F_score"] >= 4
        and row["M_score"] >= 4
    ):
        return "Champions"

    if (
        row["R_score"] >= 3
        and row["F_score"] >= 3
    ):
        return "Loyal Customers"

    if row["R_score"] >= 4:
        return "Recent Customers"

    if (
        row["R_score"] <= 2
        and row["F_score"] >= 3
    ):
        return "At Risk"

    if (
        row["R_score"] <= 2
        and row["F_score"] <= 2
    ):
        return "Lost Customers"

    return "Potential Customers"


rfm["customer_segment"] = rfm.apply(
    classify_customer,
    axis=1
)

save_csv(rfm, "customer_rfm_analysis.csv")

print(
    rfm["customer_segment"]
    .value_counts()
)


# ================================================================
# 8. CUSTOMER LIFETIME VALUE PROXY
# ================================================================

print_header("CUSTOMER VALUE ANALYSIS")

customer_value = (
    customer_orders
    .groupby("customer_unique_id")
    .agg(
        total_revenue=("revenue", "sum"),
        total_orders=("order_id", "nunique"),
        total_items=("items", "sum"),
        total_freight=("freight", "sum")
    )
    .reset_index()
)

customer_value["average_order_value"] = (
    customer_value["total_revenue"]
    / customer_value["total_orders"]
)

customer_value["revenue_per_item"] = (
    customer_value["total_revenue"]
    / customer_value["total_items"].replace(0, np.nan)
)

customer_value = customer_value.replace(
    [np.inf, -np.inf],
    np.nan
)

customer_value = customer_value.round(2)

save_csv(
    customer_value,
    "customer_value_analysis.csv"
)


# ================================================================
# 9. CUSTOMER COHORT ANALYSIS
# ================================================================

print_header("CUSTOMER COHORT ANALYSIS")

cohort_data = customer_orders[
    [
        "customer_unique_id",
        "order_purchase_timestamp",
        "order_id",
        "revenue"
    ]
].copy()

cohort_data["order_month"] = (
    cohort_data["order_purchase_timestamp"]
    .dt.to_period("M")
)

first_purchase = (
    cohort_data
    .groupby("customer_unique_id")["order_purchase_timestamp"]
    .min()
    .dt.to_period("M")
    .rename("cohort_month")
)

cohort_data = cohort_data.merge(
    first_purchase,
    on="customer_unique_id",
    how="left"
)

cohort_data["cohort_index"] = (
    (
        cohort_data["order_month"].dt.year
        - cohort_data["cohort_month"].dt.year
    ) * 12
    +
    (
        cohort_data["order_month"].dt.month
        - cohort_data["cohort_month"].dt.month
    )
    + 1
)

cohort_customers = (
    cohort_data
    .groupby(
        ["cohort_month", "cohort_index"]
    )["customer_unique_id"]
    .nunique()
    .reset_index()
)

cohort_table = cohort_customers.pivot(
    index="cohort_month",
    columns="cohort_index",
    values="customer_unique_id"
)

cohort_sizes = (
    cohort_table.iloc[:, 0]
)

cohort_retention = (
    cohort_table
    .divide(cohort_sizes, axis=0)
    * 100
)

cohort_retention = cohort_retention.round(2)

save_csv(
    cohort_retention.reset_index(),
    "customer_cohort_retention.csv"
)


# ================================================================
# 10. PRODUCT PERFORMANCE
# ================================================================

print_header("ADVANCED PRODUCT ANALYSIS")

product_items = order_items.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one"
)

product_analysis = (
    product_items
    .groupby("product_id", as_index=False)
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        items=("product_id", "size"),
        average_price=("price", "mean"),
        sellers=("seller_id", "nunique"),
        orders=("order_id", "nunique")
    )
)

if "product_category_name_english" in product_items.columns:

    category_lookup = (
        product_items[
            [
                "product_id",
                "product_category_name_english"
            ]
        ]
        .drop_duplicates("product_id")
    )

    product_analysis = product_analysis.merge(
        category_lookup,
        on="product_id",
        how="left"
    )

product_analysis["freight_pct"] = (
    product_analysis["freight"]
    / product_analysis["revenue"].replace(0, np.nan)
    * 100
)

product_analysis["revenue_per_order"] = (
    product_analysis["revenue"]
    / product_analysis["orders"].replace(0, np.nan)
)

product_analysis = product_analysis.replace(
    [np.inf, -np.inf],
    np.nan
)

product_analysis = product_analysis.sort_values(
    "revenue",
    ascending=False
)

save_csv(
    product_analysis,
    "advanced_product_analysis.csv"
)


# ================================================================
# 11. CATEGORY PERFORMANCE
# ================================================================

print_header("ADVANCED CATEGORY ANALYSIS")

if "product_category_name_english" in product_items.columns:

    category_analysis = (
        product_items
        .groupby(
            "product_category_name_english",
            dropna=False
        )
        .agg(
            revenue=("price", "sum"),
            freight=("freight_value", "sum"),
            items=("product_id", "size"),
            orders=("order_id", "nunique"),
            products=("product_id", "nunique"),
            sellers=("seller_id", "nunique"),
            average_price=("price", "mean")
        )
        .reset_index()
    )

    category_analysis[
        "freight_pct"
    ] = (
        category_analysis["freight"]
        / category_analysis["revenue"].replace(0, np.nan)
        * 100
    )

    total_category_revenue = (
        category_analysis["revenue"].sum()
    )

    category_analysis[
        "revenue_share_pct"
    ] = (
        category_analysis["revenue"]
        / total_category_revenue
        * 100
    )

    category_analysis[
        "revenue_per_order"
    ] = (
        category_analysis["revenue"]
        / category_analysis["orders"].replace(0, np.nan)
    )

    category_analysis = category_analysis.replace(
        [np.inf, -np.inf],
        np.nan
    )

    category_analysis = category_analysis.sort_values(
        "revenue",
        ascending=False
    )

    save_csv(
        category_analysis,
        "advanced_category_analysis.csv"
    )

else:
    print(
        "Category column not available. "
        "Skipping category analysis."
    )


# ================================================================
# 12. SELLER PERFORMANCE
# ================================================================

print_header("ADVANCED SELLER ANALYSIS")

seller_analysis = (
    order_items
    .groupby("seller_id", as_index=False)
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        orders=("order_id", "nunique"),
        items=("order_id", "size"),
        products=("product_id", "nunique"),
        average_item_price=("price", "mean")
    )
)

seller_analysis["freight_pct"] = (
    seller_analysis["freight"]
    / seller_analysis["revenue"].replace(0, np.nan)
    * 100
)

seller_analysis["revenue_per_order"] = (
    seller_analysis["revenue"]
    / seller_analysis["orders"].replace(0, np.nan)
)

seller_analysis["revenue_per_item"] = (
    seller_analysis["revenue"]
    / seller_analysis["items"].replace(0, np.nan)
)

seller_analysis = seller_analysis.replace(
    [np.inf, -np.inf],
    np.nan
)

seller_analysis = seller_analysis.sort_values(
    "revenue",
    ascending=False
)

save_csv(
    seller_analysis,
    "advanced_seller_analysis.csv"
)


# ================================================================
# 13. SELLER CONCENTRATION
# ================================================================

print_header("SELLER CONCENTRATION")

seller_sorted = seller_analysis.sort_values(
    "revenue",
    ascending=False
).copy()

total_revenue = seller_sorted["revenue"].sum()

seller_sorted["revenue_share_pct"] = (
    seller_sorted["revenue"]
    / total_revenue
    * 100
)

seller_sorted["cumulative_revenue_pct"] = (
    seller_sorted["revenue_share_pct"]
    .cumsum()
)

top_10_share = seller_sorted.head(10)[
    "revenue_share_pct"
].sum()

top_20_share = seller_sorted.head(20)[
    "revenue_share_pct"
].sum()

top_50_share = seller_sorted.head(50)[
    "revenue_share_pct"
].sum()

print(
    f"Top 10 sellers revenue share : "
    f"{top_10_share:.2f}%"
)

print(
    f"Top 20 sellers revenue share : "
    f"{top_20_share:.2f}%"
)

print(
    f"Top 50 sellers revenue share : "
    f"{top_50_share:.2f}%"
)

save_csv(
    seller_sorted,
    "seller_concentration.csv"
)


# ================================================================
# 14. STATE PERFORMANCE
# ================================================================

print_header("STATE PERFORMANCE ANALYSIS")

state_analysis = (
    orders_analysis
    .groupby("customer_state", dropna=False)
    .agg(
        revenue=("revenue", "sum"),
        freight=("freight", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_unique_id", "nunique"),
        items=("items", "sum")
    )
    .reset_index()
)

state_analysis["aov"] = (
    state_analysis["revenue"]
    / state_analysis["orders"].replace(0, np.nan)
)

state_analysis["freight_pct"] = (
    state_analysis["freight"]
    / state_analysis["revenue"].replace(0, np.nan)
    * 100
)

state_analysis["revenue_per_customer"] = (
    state_analysis["revenue"]
    / state_analysis["customers"].replace(0, np.nan)
)

state_analysis = state_analysis.replace(
    [np.inf, -np.inf],
    np.nan
)

state_analysis = state_analysis.sort_values(
    "revenue",
    ascending=False
)

save_csv(
    state_analysis,
    "advanced_state_analysis.csv"
)


# ================================================================
# 15. PAYMENT ANALYSIS
# ================================================================

print_header("PAYMENT ANALYSIS")

payment_analysis = (
    payments
    .groupby("payment_type", dropna=False)
    .agg(
        payment_value=("payment_value", "sum"),
        transactions=("payment_type", "size"),
        orders=("order_id", "nunique"),
        average_payment=("payment_value", "mean")
    )
    .reset_index()
)

payment_total = payment_analysis[
    "payment_value"
].sum()

payment_analysis["payment_share_pct"] = (
    payment_analysis["payment_value"]
    / payment_total
    * 100
)

payment_analysis = payment_analysis.sort_values(
    "payment_value",
    ascending=False
)

save_csv(
    payment_analysis,
    "payment_analysis.csv"
)


# ================================================================
# 16. MONTHLY BUSINESS PERFORMANCE
# ================================================================

print_header("MONTHLY BUSINESS PERFORMANCE")

monthly = orders_analysis.copy()

monthly["month"] = (
    monthly["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)

monthly_analysis = (
    monthly
    .groupby("month")
    .agg(
        revenue=("revenue", "sum"),
        freight=("freight", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_unique_id", "nunique"),
        items=("items", "sum")
    )
    .reset_index()
)

monthly_analysis["aov"] = (
    monthly_analysis["revenue"]
    / monthly_analysis["orders"].replace(0, np.nan)
)

monthly_analysis["revenue_growth_pct"] = (
    monthly_analysis["revenue"]
    .pct_change()
    * 100
)

monthly_analysis["order_growth_pct"] = (
    monthly_analysis["orders"]
    .pct_change()
    * 100
)

monthly_analysis = monthly_analysis.replace(
    [np.inf, -np.inf],
    np.nan
)

save_csv(
    monthly_analysis,
    "advanced_monthly_performance.csv"
)


# ================================================================
# 17. DELIVERY PERFORMANCE BY STATE
# ================================================================

print_header("DELIVERY PERFORMANCE BY STATE")

delivery_state = (
    valid_delivery
    .groupby("customer_state", dropna=False)
    .agg(
        orders=("order_id", "nunique"),
        average_delivery_days=("delivery_days", "mean"),
        median_delivery_days=("delivery_days", "median"),
        late_orders=("is_late", "sum"),
        extreme_orders=("is_extreme_delivery", "sum")
    )
    .reset_index()
)

delivery_state["late_delivery_rate_pct"] = (
    delivery_state["late_orders"]
    / delivery_state["orders"].replace(0, np.nan)
    * 100
)

delivery_state["extreme_delivery_rate_pct"] = (
    delivery_state["extreme_orders"]
    / delivery_state["orders"].replace(0, np.nan)
    * 100
)

delivery_state = delivery_state.sort_values(
    "late_delivery_rate_pct",
    ascending=False
)

save_csv(
    delivery_state,
    "advanced_delivery_by_state.csv"
)


# ================================================================
# 18. REVIEW ANALYSIS
# ================================================================

print_header("CUSTOMER EXPERIENCE ANALYSIS")

review_distribution = (
    reviews
    .groupby("review_score", dropna=False)
    .size()
    .reset_index(name="reviews")
)

total_reviews = review_distribution[
    "reviews"
].sum()

review_distribution["review_share_pct"] = (
    review_distribution["reviews"]
    / total_reviews
    * 100
)

save_csv(
    review_distribution,
    "review_distribution.csv"
)

print(
    f"Average review score: "
    f"{reviews['review_score'].mean():.2f}"
)


# ================================================================
# 19. DELIVERY VS REVIEW SCORE
# ================================================================

print_header("DELIVERY VS CUSTOMER SATISFACTION")

review_order = (
    reviews[
        [
            "order_id",
            "review_score"
        ]
    ]
    .groupby("order_id", as_index=False)
    .agg(
        review_score=("review_score", "mean")
    )
)

delivery_review = valid_delivery.merge(
    review_order,
    on="order_id",
    how="inner",
    validate="one_to_one"
)

delivery_review["delivery_group"] = np.where(
    delivery_review["is_late"],
    "Late",
    "On time"
)

delivery_review_analysis = (
    delivery_review
    .groupby("delivery_group")
    .agg(
        orders=("order_id", "nunique"),
        average_review_score=("review_score", "mean")
    )
    .reset_index()
)

delivery_review_analysis[
    "average_review_score"
] = delivery_review_analysis[
    "average_review_score"
].round(2)

save_csv(
    delivery_review_analysis,
    "delivery_vs_review_advanced.csv"
)

print(delivery_review_analysis)


# ================================================================
# 20. REVIEW BY CATEGORY
# ================================================================

print_header("REVIEW PERFORMANCE BY CATEGORY")

if "product_category_name_english" in product_items.columns:

    review_items = reviews[
        [
            "order_id",
            "review_score"
        ]
    ].merge(
        order_items[
            [
                "order_id",
                "product_id"
            ]
        ],
        on="order_id",
        how="inner"
    )

    review_items = review_items.merge(
        products[
            [
                "product_id",
                "product_category_name_english"
            ]
        ]
        if "product_category_name_english" in products.columns
        else products[["product_id"]],
        on="product_id",
        how="left"
    )

    if "product_category_name_english" in review_items.columns:

        category_reviews = (
            review_items
            .groupby(
                "product_category_name_english",
                dropna=False
            )
            .agg(
                reviews=("review_score", "size"),
                average_review_score=(
                    "review_score",
                    "mean"
                )
            )
            .reset_index()
        )

        category_reviews = category_reviews.sort_values(
            "average_review_score"
        )

        save_csv(
            category_reviews,
            "advanced_review_by_category.csv"
        )


# ================================================================
# 21. CUSTOMER RETENTION SUMMARY
# ================================================================

print_header("CUSTOMER RETENTION SUMMARY")

customer_frequency = (
    customer_orders
    .groupby("customer_unique_id")
    ["order_id"]
    .nunique()
)

one_time_customers = (
    customer_frequency == 1
).sum()

repeat_customers = (
    customer_frequency > 1
).sum()

total_customers = len(customer_frequency)

repeat_rate = (
    repeat_customers
    / total_customers
    * 100
)

retention_summary = pd.DataFrame({
    "metric": [
        "total_customers",
        "one_time_customers",
        "repeat_customers",
        "repeat_customer_rate_pct"
    ],
    "value": [
        total_customers,
        one_time_customers,
        repeat_customers,
        repeat_rate
    ]
})

save_csv(
    retention_summary,
    "customer_retention_summary.csv"
)

print(
    f"Total customers       : {total_customers:,}"
)

print(
    f"One-time customers    : {one_time_customers:,}"
)

print(
    f"Repeat customers      : {repeat_customers:,}"
)

print(
    f"Repeat customer rate  : {repeat_rate:.2f}%"
)


# ================================================================
# 22. EXECUTIVE ADVANCED SUMMARY
# ================================================================

print_header("ADVANCED BUSINESS ANALYSIS SUMMARY")

total_revenue = orders_analysis[
    "revenue"
].sum()

total_freight = orders_analysis[
    "freight"
].sum()

total_orders = orders_analysis[
    "order_id"
].nunique()

total_items = order_items.shape[0]

total_customers = orders_analysis[
    "customer_unique_id"
].nunique()

revenue_aov = (
    total_revenue
    / total_orders
)

total_order_value = (
    total_revenue
    + total_freight
)

aov_with_freight = (
    total_order_value
    / total_orders
)

freight_ratio = (
    total_freight
    / total_revenue
    * 100
)

average_delivery = (
    valid_delivery["delivery_days"].mean()
)

median_delivery = (
    valid_delivery["delivery_days"].median()
)

late_rate = (
    valid_delivery["is_late"].mean()
    * 100
)

extreme_rate = (
    valid_delivery["is_extreme_delivery"].mean()
    * 100
)

average_review = (
    reviews["review_score"].mean()
)

print(
    f"Total revenue              : "
    f"R$ {total_revenue:,.2f}"
)

print(
    f"Total freight              : "
    f"R$ {total_freight:,.2f}"
)

print(
    f"Total orders               : "
    f"{total_orders:,}"
)

print(
    f"Total items                : "
    f"{total_items:,}"
)

print(
    f"Unique customers           : "
    f"{total_customers:,}"
)

print(
    f"Revenue AOV                : "
    f"R$ {revenue_aov:,.2f}"
)

print(
    f"AOV including freight     : "
    f"R$ {aov_with_freight:,.2f}"
)

print(
    f"Freight / revenue         : "
    f"{freight_ratio:.2f}%"
)

print(
    f"Repeat customer rate      : "
    f"{repeat_rate:.2f}%"
)

print(
    f"Average delivery time     : "
    f"{average_delivery:.2f} days"
)

print(
    f"Median delivery time      : "
    f"{median_delivery:.2f} days"
)

print(
    f"Late delivery rate        : "
    f"{late_rate:.2f}%"
)

print(
    f"Extreme delivery rate     : "
    f"{extreme_rate:.2f}%"
)

print(
    f"Average review score      : "
    f"{average_review:.2f}"
)


# ================================================================
# 23. FINAL OUTPUT
# ================================================================

print_header("ADVANCED BUSINESS ANALYSIS COMPLETE")

print(
    f"""
Analysis results saved to:

    {ANALYSIS_DIR}

Generated outputs include:

    customer_rfm_analysis.csv
    customer_value_analysis.csv
    customer_cohort_retention.csv
    advanced_product_analysis.csv
    advanced_category_analysis.csv
    advanced_seller_analysis.csv
    seller_concentration.csv
    advanced_state_analysis.csv
    payment_analysis.csv
    advanced_monthly_performance.csv
    advanced_delivery_by_state.csv
    review_distribution.csv
    delivery_vs_review_advanced.csv
    advanced_review_by_category.csv
    customer_retention_summary.csv

No raw or processed data was modified.
"""
)