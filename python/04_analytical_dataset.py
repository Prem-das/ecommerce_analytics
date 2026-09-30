import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================



PROCESSED_DIR = Path(__file__).resolve().parent / "data" / "processed"

ANALYTICAL_DIR = PROCESSED_DIR / "analytical"

ANALYTICAL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_csv(filename):
    """Load a processed CSV file."""
    return pd.read_csv(PROCESSED_DIR / filename)


def save_csv(df, filename):
    """Save an analytical dataset."""
    path = ANALYTICAL_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved: {path}")


def check_unique(df, column, table_name):
    """Check whether a column is unique."""
    duplicates = df[column].duplicated().sum()

    print(
        f"{table_name:<25} "
        f"rows={len(df):>8,} | "
        f"duplicate {column}={duplicates:,}"
    )


# ============================================================
# LOAD PROCESSED DATA
# ============================================================

print("=" * 70)
print("LOADING PROCESSED DATA")
print("=" * 70)

customers = load_csv("customers_clean.csv")
orders = load_csv("orders_clean.csv")
order_items = load_csv("order_items_clean.csv")
payments = load_csv("payments_clean.csv")
reviews = load_csv("reviews_clean.csv")
products = load_csv("products_enriched.csv")
sellers = load_csv("sellers_clean.csv")

print("Processed data loaded successfully.")


# ============================================================
# CONVERT DATE COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("CONVERTING DATE COLUMNS")
print("=" * 70)

order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in order_date_columns:
    if column in orders.columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

print("Order dates converted.")


# ============================================================
# FACT ORDERS
# GRAIN: 1 ROW = 1 ORDER
# ============================================================

print("\n" + "=" * 70)
print("BUILDING FACT ORDERS")
print("=" * 70)

fact_orders = orders.copy()


# ------------------------------------------------------------
# Order-level revenue
# ------------------------------------------------------------

order_value = (
    order_items
    .groupby("order_id", as_index=False)
    .agg(
        order_revenue=("price", "sum"),
        order_freight=("freight_value", "sum"),
        item_count=("order_item_id", "count")
    )
)

fact_orders = fact_orders.merge(
    order_value,
    on="order_id",
    how="left",
    validate="one_to_one"
)


# ------------------------------------------------------------
# Total order value
# ------------------------------------------------------------

fact_orders["order_total_value"] = (
    fact_orders["order_revenue"].fillna(0)
    + fact_orders["order_freight"].fillna(0)
)


# ------------------------------------------------------------
# Delivery metrics
# ------------------------------------------------------------

if "delivery_days" not in fact_orders.columns:

    fact_orders["delivery_days"] = (
        fact_orders["order_delivered_customer_date"]
        - fact_orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400


if "delivery_delay_days" not in fact_orders.columns:

    fact_orders["delivery_delay_days"] = (
        fact_orders["order_delivered_customer_date"]
        - fact_orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400


# ------------------------------------------------------------
# Late delivery flag
# ------------------------------------------------------------

fact_orders["is_late"] = (
    fact_orders["delivery_delay_days"] > 0
)


# ------------------------------------------------------------
# Extreme delivery flag
# ------------------------------------------------------------

fact_orders["is_extreme_delivery"] = (
    fact_orders["delivery_days"] > 90
)


# ------------------------------------------------------------
# Delivery status
# ------------------------------------------------------------

fact_orders["delivery_status"] = "not_delivered"

fact_orders.loc[
    fact_orders["order_delivered_customer_date"].notna(),
    "delivery_status"
] = "on_time"

fact_orders.loc[
    fact_orders["is_late"] == True,
    "delivery_status"
] = "late"

fact_orders.loc[
    fact_orders["is_extreme_delivery"] == True,
    "delivery_status"
] = "extreme_delay"


# ------------------------------------------------------------
# Validate grain
# ------------------------------------------------------------

check_unique(
    fact_orders,
    "order_id",
    "fact_orders"
)


# ============================================================
# FACT ORDER ITEMS
# GRAIN: 1 ROW = 1 ORDER ITEM
# ============================================================

print("\n" + "=" * 70)
print("BUILDING FACT ORDER ITEMS")
print("=" * 70)

fact_order_items = order_items.copy()


# ------------------------------------------------------------
# Add product information
# ------------------------------------------------------------

product_columns = [
    "product_id",
    "product_category_name",
    "product_category_name_english"
]

available_product_columns = [
    column
    for column in product_columns
    if column in products.columns
]

product_lookup = products[available_product_columns].drop_duplicates(
    subset=["product_id"]
)

fact_order_items = fact_order_items.merge(
    product_lookup,
    on="product_id",
    how="left",
    validate="many_to_one"
)


# ------------------------------------------------------------
# Add seller information
# ------------------------------------------------------------

seller_columns = [
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state"
]

available_seller_columns = [
    column
    for column in seller_columns
    if column in sellers.columns
]

seller_lookup = sellers[available_seller_columns].drop_duplicates(
    subset=["seller_id"]
)

fact_order_items = fact_order_items.merge(
    seller_lookup,
    on="seller_id",
    how="left",
    validate="many_to_one"
)


# ------------------------------------------------------------
# Item-level total
# ------------------------------------------------------------

fact_order_items["item_total_value"] = (
    fact_order_items["price"]
    + fact_order_items["freight_value"]
)


# ------------------------------------------------------------
# Freight percentage
# ------------------------------------------------------------

fact_order_items["freight_pct"] = 0.0

valid_price = fact_order_items["price"] > 0

fact_order_items.loc[valid_price, "freight_pct"] = (
    fact_order_items.loc[valid_price, "freight_value"]
    / fact_order_items.loc[valid_price, "price"]
    * 100
)


# ------------------------------------------------------------
# Validate grain
# ------------------------------------------------------------

print(
    f"Order-item rows: {len(fact_order_items):,}"
)

print(
    f"Unique order/item combinations: "
    f"{fact_order_items[['order_id', 'order_item_id']].drop_duplicates().shape[0]:,}"
)


# ============================================================
# DIM CUSTOMERS
# GRAIN: 1 ROW = 1 CUSTOMER
# ============================================================

print("\n" + "=" * 70)
print("BUILDING DIM CUSTOMERS")
print("=" * 70)

dim_customers = customers.copy()


# ------------------------------------------------------------
# Calculate customer order frequency
# ------------------------------------------------------------

customer_orders = (
    orders
    .merge(
        customers[
            ["customer_id", "customer_unique_id"]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one"
    )
    .groupby("customer_unique_id")
    .size()
    .reset_index(name="order_count")
)


# ------------------------------------------------------------
# Add frequency to customers
# ------------------------------------------------------------

dim_customers = dim_customers.merge(
    customer_orders,
    on="customer_unique_id",
    how="left",
    validate="many_to_one"
)


# ------------------------------------------------------------
# Customer type
# ------------------------------------------------------------

dim_customers["customer_type"] = "one_time"

dim_customers.loc[
    dim_customers["order_count"] > 1,
    "customer_type"
] = "repeat"


# ------------------------------------------------------------
# Validate customer grain
# ------------------------------------------------------------

check_unique(
    dim_customers,
    "customer_id",
    "dim_customers"
)


# ============================================================
# DIM PRODUCTS
# GRAIN: 1 ROW = 1 PRODUCT
# ============================================================

print("\n" + "=" * 70)
print("BUILDING DIM PRODUCTS")
print("=" * 70)

dim_products = products.copy()

check_unique(
    dim_products,
    "product_id",
    "dim_products"
)


# ============================================================
# DIM SELLERS
# GRAIN: 1 ROW = 1 SELLER
# ============================================================

print("\n" + "=" * 70)
print("BUILDING DIM SELLERS")
print("=" * 70)

dim_sellers = sellers.copy()

check_unique(
    dim_sellers,
    "seller_id",
    "dim_sellers"
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL ANALYTICAL DATASET VALIDATION")
print("=" * 70)


datasets = {
    "fact_orders": fact_orders,
    "fact_order_items": fact_order_items,
    "dim_customers": dim_customers,
    "dim_products": dim_products,
    "dim_sellers": dim_sellers
}


for name, df in datasets.items():

    print(
        f"{name:<25} "
        f"rows={len(df):>8,} | "
        f"columns={len(df.columns):>3}"
    )


# ------------------------------------------------------------
# Revenue reconciliation
# ------------------------------------------------------------

item_revenue = fact_order_items["price"].sum()

order_revenue = fact_orders["order_revenue"].sum()

print("\nRevenue reconciliation:")

print(
    f"Revenue from order items : "
    f"R$ {item_revenue:,.2f}"
)

print(
    f"Revenue from orders      : "
    f"R$ {order_revenue:,.2f}"
)

print(
    f"Difference               : "
    f"R$ {item_revenue - order_revenue:,.2f}"
)


# ------------------------------------------------------------
# Referential integrity
# ------------------------------------------------------------

print("\nReferential integrity:")

missing_orders = (
    ~fact_order_items["order_id"].isin(
        fact_orders["order_id"]
    )
).sum()

missing_products = (
    ~fact_order_items["product_id"].isin(
        dim_products["product_id"]
    )
).sum()

missing_sellers = (
    ~fact_order_items["seller_id"].isin(
        dim_sellers["seller_id"]
    )
).sum()

print(
    f"Order items → Orders   : {missing_orders:,}"
)

print(
    f"Order items → Products : {missing_products:,}"
)

print(
    f"Order items → Sellers  : {missing_sellers:,}"
)


# ============================================================
# SAVE ANALYTICAL DATASETS
# ============================================================

print("\n" + "=" * 70)
print("SAVING ANALYTICAL DATASETS")
print("=" * 70)

save_csv(
    fact_orders,
    "fact_orders.csv"
)

save_csv(
    fact_order_items,
    "fact_order_items.csv"
)

save_csv(
    dim_customers,
    "dim_customers.csv"
)

save_csv(
    dim_products,
    "dim_products.csv"
)

save_csv(
    dim_sellers,
    "dim_sellers.csv"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("ANALYTICAL DATASET CREATION COMPLETE")
print("=" * 70)

print(f"""
Analytical data location:
    {ANALYTICAL_DIR}

Datasets created:
    5

fact_orders
    1 row = 1 order

fact_order_items
    1 row = 1 order item

dim_customers
    1 row = 1 customer

dim_products
    1 row = 1 product

dim_sellers
    1 row = 1 seller
""")