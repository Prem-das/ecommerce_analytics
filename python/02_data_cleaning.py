
"""
Olist E-Commerce Analytics
02_data_cleaning.py

Purpose:
    Clean, standardize, validate, and enrich the raw Olist dataset.

Principles:
    1. Never modify raw data.
    2. Never delete suspicious records without evidence.
    3. Preserve original information where useful.
    4. Create quality flags for questionable records.
    5. Validate relationships before analytical joins.
"""

import pandas as pd
import numpy as np
import re
import unicodedata
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================



BASE_DIR = Path(__file__).resolve().parent  

# 2. Build the data paths relative to the BASE_DIR
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(value):
    """
    Standardize text for analytical purposes.

    Example:
        'São Paulo' -> 'sao paulo'
        ' SÃO  PAULO ' -> 'sao paulo'
    """

    if pd.isna(value):
        return value

    value = str(value)

    # Normalize unicode characters
    value = unicodedata.normalize("NFKD", value)

    # Remove accents
    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    # Lowercase
    value = value.lower()

    # Replace multiple whitespace characters
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_text_column(df, column):
    """Apply text normalization while preserving missing values."""

    if column in df.columns:
        df[column] = df[column].apply(normalize_text)

    return df


def convert_to_datetime(df, columns):
    """Convert columns to datetime safely."""

    for column in columns:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# 1. LOAD RAW DATA
# ============================================================

print("\n" + "=" * 70)
print("LOADING RAW DATA")
print("=" * 70)

customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
geolocation = pd.read_csv(RAW_DIR / "olist_geolocation_dataset.csv")
order_items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv")
orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
sellers = pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv")
category_translation = pd.read_csv(
    RAW_DIR / "product_category_name_translation.csv"
)

print("Raw data loaded successfully.")


# ============================================================
# 2. CREATE WORKING COPIES
# ============================================================

customers_clean = customers.copy()
geolocation_clean = geolocation.copy()
order_items_clean = order_items.copy()
payments_clean = payments.copy()
reviews_clean = reviews.copy()
orders_clean = orders.copy()
products_clean = products.copy()
sellers_clean = sellers.copy()
category_translation_clean = category_translation.copy()


# ============================================================
# 3. TEXT STANDARDIZATION
# ============================================================

print("\n" + "=" * 70)
print("STANDARDIZING TEXT FIELDS")
print("=" * 70)


# -------------------------
# Customers
# -------------------------

clean_text_column(
    customers_clean,
    "customer_city"
)

clean_text_column(
    customers_clean,
    "customer_state"
)


# -------------------------
# Sellers
# -------------------------

clean_text_column(
    sellers_clean,
    "seller_city"
)

clean_text_column(
    sellers_clean,
    "seller_state"
)


# -------------------------
# Geolocation
# -------------------------

clean_text_column(
    geolocation_clean,
    "geolocation_city"
)

clean_text_column(
    geolocation_clean,
    "geolocation_state"
)


# -------------------------
# Payments
# -------------------------

clean_text_column(
    payments_clean,
    "payment_type"
)


# -------------------------
# Product categories
# -------------------------

clean_text_column(
    products_clean,
    "product_category_name"
)

clean_text_column(
    category_translation_clean,
    "product_category_name"
)

clean_text_column(
    category_translation_clean,
    "product_category_name_english"
)


print("Text standardization complete.")


# ============================================================
# 4. DATE STANDARDIZATION
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


orders_clean = convert_to_datetime(
    orders_clean,
    order_date_columns
)


print("Order dates converted successfully.")


# ============================================================
# 5. NUMERIC STANDARDIZATION
# ============================================================

print("\n" + "=" * 70)
print("STANDARDIZING NUMERIC COLUMNS")
print("=" * 70)


numeric_columns = {

    "order_items": [
        "order_item_id",
        "price",
        "freight_value"
    ],

    "payments": [
        "payment_value",
        "payment_installments"
    ],

    "reviews": [
        "review_score"
    ],

    "products": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]
}


for column in numeric_columns["order_items"]:

    order_items_clean[column] = pd.to_numeric(
        order_items_clean[column],
        errors="coerce"
    )


for column in numeric_columns["payments"]:

    payments_clean[column] = pd.to_numeric(
        payments_clean[column],
        errors="coerce"
    )


for column in numeric_columns["reviews"]:

    reviews_clean[column] = pd.to_numeric(
        reviews_clean[column],
        errors="coerce"
    )


for column in numeric_columns["products"]:

    products_clean[column] = pd.to_numeric(
        products_clean[column],
        errors="coerce"
    )


print("Numeric standardization complete.")


# ============================================================
# 6. DUPLICATE HANDLING
# ============================================================

print("\n" + "=" * 70)
print("HANDLING DUPLICATES")
print("=" * 70)


# Exact duplicate records

geolocation_before = len(geolocation_clean)

geolocation_clean = (
    geolocation_clean
    .drop_duplicates()
    .reset_index(drop=True)
)

geolocation_removed = (
    geolocation_before
    - len(geolocation_clean)
)


print(
    f"Geolocation exact duplicates removed: "
    f"{geolocation_removed:,}"
)


# Other tables contain legitimate repeated business records,
# so we do NOT blindly drop duplicates.


# ============================================================
# 7. CUSTOMER QUALITY FLAGS
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER QUALITY CHECKS")
print("=" * 70)


customers_clean["customer_city_missing"] = (
    customers_clean["customer_city"].isna()
)


customers_clean["customer_state_missing"] = (
    customers_clean["customer_state"].isna()
)


customers_clean["customer_zip_missing"] = (
    customers_clean["customer_zip_code_prefix"].isna()
)


print(
    "Missing customer cities:",
    customers_clean["customer_city_missing"].sum()
)

print(
    "Missing customer states:",
    customers_clean["customer_state_missing"].sum()
)

print(
    "Missing customer ZIP codes:",
    customers_clean["customer_zip_missing"].sum()
)


# ============================================================
# 8. PRODUCT QUALITY FLAGS
# ============================================================

print("\n" + "=" * 70)
print("PRODUCT QUALITY CHECKS")
print("=" * 70)


products_clean["category_missing"] = (
    products_clean["product_category_name"].isna()
)


products_clean["weight_missing"] = (
    products_clean["product_weight_g"].isna()
)


products_clean["dimensions_missing"] = (
    products_clean[
        [
            "product_length_cm",
            "product_height_cm",
            "product_width_cm"
        ]
    ]
    .isna()
    .any(axis=1)
)


products_clean["invalid_weight"] = (
    products_clean["product_weight_g"] <= 0
)


products_clean["invalid_dimensions"] = (
    (
        products_clean[
            [
                "product_length_cm",
                "product_height_cm",
                "product_width_cm"
            ]
        ] <= 0
    )
    .any(axis=1)
)


print(
    "Missing categories:",
    products_clean["category_missing"].sum()
)

print(
    "Missing weights:",
    products_clean["weight_missing"].sum()
)

print(
    "Missing dimensions:",
    products_clean["dimensions_missing"].sum()
)

print(
    "Invalid weights:",
    products_clean["invalid_weight"].sum()
)

print(
    "Invalid dimensions:",
    products_clean["invalid_dimensions"].sum()
)


# ============================================================
# 9. ORDER ITEM QUALITY FLAGS
# ============================================================

print("\n" + "=" * 70)
print("ORDER ITEM QUALITY CHECKS")
print("=" * 70)


order_items_clean["negative_price"] = (
    order_items_clean["price"] < 0
)


order_items_clean["zero_price"] = (
    order_items_clean["price"] == 0
)


order_items_clean["negative_freight"] = (
    order_items_clean["freight_value"] < 0
)


order_items_clean["zero_freight"] = (
    order_items_clean["freight_value"] == 0
)


# Derived value
order_items_clean["total_item_value"] = (
    order_items_clean["price"]
    + order_items_clean["freight_value"]
)


# Freight percentage
order_items_clean["freight_pct"] = np.where(
    order_items_clean["price"] > 0,
    (
        order_items_clean["freight_value"]
        / order_items_clean["price"]
    ) * 100,
    np.nan
)


print(
    "Negative prices:",
    order_items_clean["negative_price"].sum()
)

print(
    "Zero prices:",
    order_items_clean["zero_price"].sum()
)

print(
    "Negative freight:",
    order_items_clean["negative_freight"].sum()
)

print(
    "Zero freight:",
    order_items_clean["zero_freight"].sum()
)


# ============================================================
# 10. PAYMENT QUALITY CHECKS
# ============================================================

print("\n" + "=" * 70)
print("PAYMENT QUALITY CHECKS")
print("=" * 70)


payments_clean["negative_payment"] = (
    payments_clean["payment_value"] < 0
)


payments_clean["zero_payment"] = (
    payments_clean["payment_value"] == 0
)


payments_clean["invalid_installments"] = (
    payments_clean["payment_installments"] <= 0
)


print(
    "Negative payments:",
    payments_clean["negative_payment"].sum()
)

print(
    "Zero payments:",
    payments_clean["zero_payment"].sum()
)

print(
    "Invalid installments:",
    payments_clean["invalid_installments"].sum()
)


# ============================================================
# 11. REVIEW QUALITY CHECKS
# ============================================================

print("\n" + "=" * 70)
print("REVIEW QUALITY CHECKS")
print("=" * 70)


reviews_clean["invalid_review_score"] = ~(
    reviews_clean["review_score"].between(1, 5)
)


reviews_clean["has_review_title"] = (
    reviews_clean["review_comment_title"]
    .fillna("")
    .str.strip()
    .ne("")
)


reviews_clean["has_review_message"] = (
    reviews_clean["review_comment_message"]
    .fillna("")
    .str.strip()
    .ne("")
)


print(
    "Invalid review scores:",
    reviews_clean["invalid_review_score"].sum()
)


# ============================================================
# 12. ORDER DATE LOGIC
# ============================================================

print("\n" + "=" * 70)
print("ORDER DATE VALIDATION")
print("=" * 70)


orders_clean["delivery_before_purchase"] = (
    orders_clean["order_delivered_customer_date"]
    < orders_clean["order_purchase_timestamp"]
)


orders_clean["estimated_before_purchase"] = (
    orders_clean["order_estimated_delivery_date"]
    < orders_clean["order_purchase_timestamp"]
)


orders_clean["approval_before_purchase"] = (
    orders_clean["order_approved_at"]
    < orders_clean["order_purchase_timestamp"]
)


orders_clean["carrier_before_purchase"] = (
    orders_clean["order_delivered_carrier_date"]
    < orders_clean["order_purchase_timestamp"]
)


orders_clean["customer_delivery_before_carrier"] = (
    orders_clean["order_delivered_customer_date"]
    < orders_clean["order_delivered_carrier_date"]
)


print(
    "Delivery before purchase:",
    orders_clean["delivery_before_purchase"].sum()
)

print(
    "Estimated delivery before purchase:",
    orders_clean["estimated_before_purchase"].sum()
)

print(
    "Approval before purchase:",
    orders_clean["approval_before_purchase"].sum()
)

print(
    "Carrier delivery before purchase:",
    orders_clean["carrier_before_purchase"].sum()
)

print(
    "Customer delivery before carrier:",
    orders_clean["customer_delivery_before_carrier"].sum()
)


# ============================================================
# 13. DELIVERY METRICS
# ============================================================

print("\n" + "=" * 70)
print("CREATING DELIVERY METRICS")
print("=" * 70)


orders_clean["delivery_days"] = (
    orders_clean["order_delivered_customer_date"]
    - orders_clean["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)


orders_clean["estimated_delivery_days"] = (
    orders_clean["order_estimated_delivery_date"]
    - orders_clean["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)


orders_clean["delivery_delay_days"] = (
    orders_clean["order_delivered_customer_date"]
    - orders_clean["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 60 * 60)


# ============================================================
# 14. DELIVERY OUTLIER FLAGS
# ============================================================

orders_clean["delivery_over_30_days"] = (
    orders_clean["delivery_days"] > 30
)


orders_clean["delivery_over_60_days"] = (
    orders_clean["delivery_days"] > 60
)


orders_clean["delivery_over_90_days"] = (
    orders_clean["delivery_days"] > 90
)


orders_clean["delivery_negative"] = (
    orders_clean["delivery_days"] < 0
)


orders_clean["is_late"] = (
    orders_clean["delivery_delay_days"] > 0
)


print(
    "Deliveries > 30 days:",
    orders_clean["delivery_over_30_days"].sum()
)

print(
    "Deliveries > 60 days:",
    orders_clean["delivery_over_60_days"].sum()
)

print(
    "Deliveries > 90 days:",
    orders_clean["delivery_over_90_days"].sum()
)

print(
    "Negative delivery duration:",
    orders_clean["delivery_negative"].sum()
)


# ============================================================
# 15. ORDER DATE DIMENSIONS
# ============================================================

orders_clean["purchase_date"] = (
    orders_clean["order_purchase_timestamp"].dt.date
)


orders_clean["purchase_year"] = (
    orders_clean["order_purchase_timestamp"].dt.year
)


orders_clean["purchase_month"] = (
    orders_clean["order_purchase_timestamp"].dt.month
)


orders_clean["purchase_month_name"] = (
    orders_clean["order_purchase_timestamp"].dt.month_name()
)


orders_clean["purchase_year_month"] = (
    orders_clean["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)


orders_clean["purchase_day_of_week"] = (
    orders_clean["order_purchase_timestamp"]
    .dt.day_name()
)


# ============================================================
# 16. ORDER STATUS QUALITY
# ============================================================

print("\n" + "=" * 70)
print("ORDER STATUS VALIDATION")
print("=" * 70)


valid_statuses = {
    "delivered",
    "shipped",
    "canceled",
    "unavailable",
    "invoiced",
    "processing",
    "created",
    "approved"
}


orders_clean["invalid_order_status"] = ~(
    orders_clean["order_status"].isin(valid_statuses)
)


print(
    "Invalid order statuses:",
    orders_clean["invalid_order_status"].sum()
)


# ============================================================
# 17. REFERENTIAL INTEGRITY
# ============================================================

print("\n" + "=" * 70)
print("REFERENTIAL INTEGRITY")
print("=" * 70)


relationship_checks = {

    "Order items -> Orders":
        ~order_items_clean["order_id"]
        .isin(orders_clean["order_id"]),

    "Order items -> Products":
        ~order_items_clean["product_id"]
        .isin(products_clean["product_id"]),

    "Order items -> Sellers":
        ~order_items_clean["seller_id"]
        .isin(sellers_clean["seller_id"]),

    "Orders -> Customers":
        ~orders_clean["customer_id"]
        .isin(customers_clean["customer_id"]),

    "Payments -> Orders":
        ~payments_clean["order_id"]
        .isin(orders_clean["order_id"]),

    "Reviews -> Orders":
        ~reviews_clean["order_id"]
        .isin(orders_clean["order_id"]),

    "Products -> Categories":
        ~products_clean["product_category_name"]
        .isin(
            category_translation_clean[
                "product_category_name"
            ]
        )
}


for relationship, invalid_rows in relationship_checks.items():

    print(
        f"{relationship:30} "
        f"{invalid_rows.sum():,} unmatched"
    )


# ============================================================
# 18. PRODUCT CATEGORY ENRICHMENT
# ============================================================

print("\n" + "=" * 70)
print("CREATING PRODUCT CATEGORY ENRICHMENT")
print("=" * 70)


products_enriched = (
    products_clean
    .merge(
        category_translation_clean,
        on="product_category_name",
        how="left",
        validate="many_to_one"
    )
)


products_enriched["product_category_name_english"] = (
    products_enriched[
        "product_category_name_english"
    ]
    .fillna("unknown")
)


print(
    "Products enriched:",
    len(products_enriched)
)


# ============================================================
# 19. CUSTOMER ORDER FREQUENCY
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER ORDER FREQUENCY")
print("=" * 70)


customer_order_map = (
    orders_clean[
        [
            "order_id",
            "customer_id"
        ]
    ]
    .merge(
        customers_clean[
            [
                "customer_id",
                "customer_unique_id"
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one"
    )
)


customer_frequency = (
    customer_order_map
    .groupby("customer_unique_id")
    .size()
)


print(
    "Unique customers:",
    len(customer_frequency)
)


print(
    "One-order customers:",
    (customer_frequency == 1).sum()
)


print(
    "Repeat customers:",
    (customer_frequency > 1).sum()
)


# ============================================================
# 20. FINAL QUALITY SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL DATA QUALITY SUMMARY")
print("=" * 70)


print(
    f"""
Customers:
    Rows: {len(customers_clean):,}
    Duplicate customer_id:
        {customers_clean["customer_id"].duplicated().sum():,}

Orders:
    Rows: {len(orders_clean):,}
    Duplicate order_id:
        {orders_clean["order_id"].duplicated().sum():,}

Order items:
    Rows: {len(order_items_clean):,}
    Negative prices:
        {order_items_clean["negative_price"].sum():,}
    Negative freight:
        {order_items_clean["negative_freight"].sum():,}
    Zero freight:
        {order_items_clean["zero_freight"].sum():,}

Products:
    Rows: {len(products_clean):,}
    Missing categories:
        {products_clean["category_missing"].sum():,}

Orders:
    Delivery > 30 days:
        {orders_clean["delivery_over_30_days"].sum():,}
    Delivery > 60 days:
        {orders_clean["delivery_over_60_days"].sum():,}
    Delivery > 90 days:
        {orders_clean["delivery_over_90_days"].sum():,}

Geolocation:
    Exact duplicates removed:
        {geolocation_removed:,}
"""
)


# ============================================================
# 21. SAVE CLEANED DATA
# ============================================================

print("\n" + "=" * 70)
print("SAVING PROCESSED DATA")
print("=" * 70)


output_tables = {

    "customers_clean":
        customers_clean,

    "geolocation_clean":
        geolocation_clean,

    "order_items_clean":
        order_items_clean,

    "payments_clean":
        payments_clean,

    "reviews_clean":
        reviews_clean,

    "orders_clean":
        orders_clean,

    "products_clean":
        products_clean,

    "sellers_clean":
        sellers_clean,

    "category_translation_clean":
        category_translation_clean,

    "products_enriched":
        products_enriched
}


for name, dataframe in output_tables.items():

    output_path = (
        PROCESSED_DIR
        / f"{name}.csv"
    )

    dataframe.to_csv(
        output_path,
        index=False
    )

    print(
        f"Saved: {name}.csv"
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("DATA CLEANING PIPELINE COMPLETE")
print("=" * 70)

print(
    f"""
Processed files:
    {len(output_tables)}

Output directory:
    {PROCESSED_DIR}

Raw data was not modified.
Suspicious records were flagged rather than
silently deleted.
"""
)

