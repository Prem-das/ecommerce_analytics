
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = Path("C:/Users/premk/OneDrive/Documents/ecommerce_analytics/data/raw")


# ============================================================
# LOAD DATA
# ============================================================
customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
geolocation = pd.read_csv(DATA_DIR / "olist_geolocation_dataset.csv")
order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
sellers = pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv")
category_translation = pd.read_csv(
    DATA_DIR / "product_category_name_translation.csv"
)

datasets = {
    "customers": customers,
    "geolocation": geolocation,
    "order_items": order_items,
    "payments": payments,
    "reviews": reviews,
    "orders": orders,
    "products": products,
    "sellers": sellers,
    "category_translation": category_translation,
}


# ============================================================
# 1. BASIC DATASET INFORMATION
# ============================================================

print("\n" + "=" * 60)
print("DATASET SHAPES")
print("=" * 60)

for name, df in datasets.items():
    print(f"{name:25} {df.shape}")


# ============================================================
# 2. COLUMN INFORMATION
# ============================================================

print("\n" + "=" * 60)
print("COLUMN INFORMATION")
print("=" * 60)

for name, df in datasets.items():
    print(f"\n--- {name.upper()} ---")

    print("Columns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)


# ============================================================
# 3. MISSING VALUES
# ============================================================

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

for name, df in datasets.items():

    missing = df.isna().sum()
    missing = missing[missing > 0]

    print(f"\n--- {name.upper()} ---")

    if missing.empty:
        print("No missing values")
    else:
        print(missing)


# ============================================================
# 4. DUPLICATE ROWS
# ============================================================

print("\n" + "=" * 60)
print("DUPLICATE ROWS")
print("=" * 60)

for name, df in datasets.items():

    duplicate_count = df.duplicated().sum()

    print(
        f"{name:25} {duplicate_count:,} duplicate rows"
    )


# ============================================================
# 5. UNIQUE ID CHECKS
# ============================================================

print("\n" + "=" * 60)
print("UNIQUE ID CHECKS")
print("=" * 60)

print("\nCUSTOMERS")

print(
    "Rows:",
    len(customers)
)

print(
    "Unique customer_id:",
    customers["customer_id"].nunique()
)

print(
    "Duplicate customer_id:",
    customers["customer_id"].duplicated().sum()
)

print(
    "Unique customer_unique_id:",
    customers["customer_unique_id"].nunique()
)

print(
    "Duplicate customer_unique_id:",
    customers["customer_unique_id"].duplicated().sum()
)


# ============================================================
# 6. ORDER STATUS DISTRIBUTION
# ============================================================

print("\n" + "=" * 60)
print("ORDER STATUS DISTRIBUTION")
print("=" * 60)

print(
    orders["order_status"].value_counts()
)


# ============================================================
# 7. DATE CONVERSION
# ============================================================

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:

    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )


print("\n" + "=" * 60)
print("DATE DATA TYPES")
print("=" * 60)

print(
    orders[date_columns].dtypes
)


# ============================================================
# 8. DELIVERY TIME ANALYSIS
# ============================================================

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)


print("\n" + "=" * 60)
print("DELIVERY TIME STATISTICS")
print("=" * 60)

print(
    orders["delivery_days"].describe()
)


print("\nDeliveries > 30 days:")
print(
    (orders["delivery_days"] > 30).sum()
)

print("\nDeliveries > 60 days:")
print(
    (orders["delivery_days"] > 60).sum()
)

print("\nDeliveries > 90 days:")
print(
    (orders["delivery_days"] > 90).sum()
)


# ============================================================
# 9. DELIVERY DATE VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("DELIVERY DATE VALIDATION")
print("=" * 60)

delivery_before_purchase = (
    orders["order_delivered_customer_date"]
    < orders["order_purchase_timestamp"]
).sum()

estimated_before_purchase = (
    orders["order_estimated_delivery_date"]
    < orders["order_purchase_timestamp"]
).sum()


print(
    "Delivery before purchase:",
    delivery_before_purchase
)

print(
    "Estimated delivery before purchase:",
    estimated_before_purchase
)


# ============================================================
# 10. ORDER DELIVERY DATE COMPLETENESS
# ============================================================

print("\n" + "=" * 60)
print("DELIVERY DATE COMPLETENESS BY STATUS")
print("=" * 60)

delivery_status_check = pd.crosstab(
    orders["order_status"],
    orders["order_delivered_customer_date"].isna()
)

print(
    delivery_status_check
)


# ============================================================
# 11. ORDER ITEMS: PRICE AND FREIGHT
# ============================================================

print("\n" + "=" * 60)
print("ORDER ITEMS: PRICE & FREIGHT")
print("=" * 60)

print("\nPrice statistics:")
print(
    order_items["price"].describe()
)

print("\nFreight statistics:")
print(
    order_items["freight_value"].describe()
)

print(
    "\nNegative prices:",
    (order_items["price"] < 0).sum()
)

print(
    "Negative freight:",
    (order_items["freight_value"] < 0).sum()
)

print(
    "Zero prices:",
    (order_items["price"] == 0).sum()
)

print(
    "Zero freight:",
    (order_items["freight_value"] == 0).sum()
)


# ============================================================
# 12. REVENUE ANALYSIS
# ============================================================

total_revenue = order_items["price"].sum()
total_freight = order_items["freight_value"].sum()
total_value = total_revenue + total_freight

order_count = order_items["order_id"].nunique()

product_aov = total_revenue / order_count
total_aov = total_value / order_count


print("\n" + "=" * 60)
print("REVENUE ANALYSIS")
print("=" * 60)

print(
    f"Product revenue:        R${total_revenue:,.2f}"
)

print(
    f"Freight value:          R${total_freight:,.2f}"
)

print(
    f"Product + freight:      R${total_value:,.2f}"
)

print(
    f"Product AOV:            R${product_aov:,.2f}"
)

print(
    f"Product + freight AOV:  R${total_aov:,.2f}"
)


# ============================================================
# 13. FREIGHT AS % OF PRODUCT PRICE
# ============================================================

order_items["freight_pct"] = (
    order_items["freight_value"]
    / order_items["price"]
) * 100


print("\n" + "=" * 60)
print("FREIGHT % STATISTICS")
print("=" * 60)

print(
    order_items["freight_pct"].describe()
)


# ============================================================
# 14. CATEGORY TRANSLATION
# ============================================================

product_sales = (
    order_items
    .merge(
        products[
            [
                "product_id",
                "product_category_name"
            ]
        ],
        on="product_id",
        how="left"
    )
    .merge(
        category_translation,
        on="product_category_name",
        how="left"
    )
)


print("\n" + "=" * 60)
print("CATEGORY TRANSLATION")
print("=" * 60)

missing_category_items = (
    product_sales[
        product_sales["product_category_name_english"].isna()
    ]
)

print(
    "Missing category items:",
    len(missing_category_items)
)

print(
    "Missing category revenue:",
    f"R${missing_category_items['price'].sum():,.2f}"
)

print(
    "Missing category revenue %:",
    f"{missing_category_items['price'].sum() / total_revenue * 100:.2f}%"
)


# ============================================================
# 15. CATEGORY REVENUE
# ============================================================

category_revenue = (
    product_sales
    .groupby("product_category_name_english")
    .agg(
        revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        orders=("order_id", "nunique"),
        items=("order_item_id", "count"),
        average_price=("price", "mean")
    )
)

category_revenue["freight_pct"] = (
    category_revenue["freight"]
    / category_revenue["revenue"]
) * 100

category_revenue["revenue_share"] = (
    category_revenue["revenue"]
    / category_revenue["revenue"].sum()
) * 100


category_revenue = category_revenue.sort_values(
    "revenue",
    ascending=False
)


print("\n" + "=" * 60)
print("TOP 15 CATEGORIES BY REVENUE")
print("=" * 60)

print(
    category_revenue.head(15)
)


print("\n" + "=" * 60)
print("TOP 15 CATEGORIES BY FREIGHT %")
print("=" * 60)

print(
    category_revenue
    .sort_values("freight_pct", ascending=False)
    .head(15)
)


# ============================================================
# 16. REFERENTIAL INTEGRITY
# ============================================================

print("\n" + "=" * 60)
print("REFERENTIAL INTEGRITY")
print("=" * 60)

checks = {

    "Order items → Orders":
        (~order_items["order_id"]
         .isin(orders["order_id"])).sum(),

    "Order items → Products":
        (~order_items["product_id"]
         .isin(products["product_id"])).sum(),

    "Order items → Sellers":
        (~order_items["seller_id"]
         .isin(sellers["seller_id"])).sum(),

    "Orders → Customers":
        (~orders["customer_id"]
         .isin(customers["customer_id"])).sum(),

    "Payments → Orders":
        (~payments["order_id"]
         .isin(orders["order_id"])).sum(),

    "Reviews → Orders":
        (~reviews["order_id"]
         .isin(orders["order_id"])).sum(),
}


for relationship, missing_count in checks.items():

    print(
        f"{relationship:30} {missing_count}"
    )


# ============================================================
# 17. CUSTOMER DISTRIBUTION
# ============================================================

print("\n" + "=" * 60)
print("CUSTOMER DISTRIBUTION")
print("=" * 60)

print(
    customers["customer_state"]
    .value_counts()
    .head(15)
)

print(
    "\nUnique customer cities:",
    customers["customer_city"].nunique()
)


# ============================================================
# 18. CUSTOMER ORDER FREQUENCY
# ============================================================

customer_orders = (
    orders
    .merge(
        customers[
            [
                "customer_id",
                "customer_unique_id"
            ]
        ],
        on="customer_id",
        how="left"
    )
)


customer_frequency = (
    customer_orders
    .groupby("customer_unique_id")
    .size()
)


print("\n" + "=" * 60)
print("CUSTOMER ORDER FREQUENCY")
print("=" * 60)

print(
    customer_frequency.describe()
)

one_order_customers = (
    customer_frequency == 1
).sum()

repeat_customers = (
    customer_frequency > 1
).sum()


print(
    "One-order customers:",
    one_order_customers
)

print(
    "Repeat customers:",
    repeat_customers
)

print(
    "Repeat customer rate:",
    f"{repeat_customers / len(customer_frequency) * 100:.2f}%"
)


# ============================================================
# 19. FINAL PROFILING SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DATA PROFILING COMPLETE")
print("=" * 60)

print(
    f"""
Datasets analyzed:             {len(datasets)}
Total orders:                  {len(orders):,}
Total order items:             {len(order_items):,}
Total customers:               {len(customers):,}
Unique customers:              {customers['customer_unique_id'].nunique():,}
Product revenue:               R${total_revenue:,.2f}
Freight value:                 R${total_freight:,.2f}
Missing-category revenue:      R${missing_category_items['price'].sum():,.2f}
Missing-category revenue %:    {missing_category_items['price'].sum() / total_revenue * 100:.2f}%
Repeat customers:              {repeat_customers:,}
Repeat customer rate:          {repeat_customers / len(customer_frequency) * 100:.2f}%
"""
)
