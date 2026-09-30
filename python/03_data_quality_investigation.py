
"""
Olist E-Commerce Analytics
03_data_quality_investigation.py

Purpose:
    Investigate suspicious records identified during data cleaning.

IMPORTANT:
    This script DOES NOT modify or delete data.
    It only investigates questionable records.
"""

import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================


PROCESSED_DIR = Path(__file__).resolve().parent / "data" / "processed"

# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 70)
print("LOADING PROCESSED DATA")
print("=" * 70)

orders = pd.read_csv(
    PROCESSED_DIR / "orders_clean.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)

products = pd.read_csv(
    PROCESSED_DIR / "products_clean.csv"
)

payments = pd.read_csv(
    PROCESSED_DIR / "payments_clean.csv"
)

category_translation = pd.read_csv(
    PROCESSED_DIR / "category_translation_clean.csv"
)

print("Processed data loaded successfully.")


# ============================================================
# CREATE QUALITY FLAGS
# ============================================================

print("\n" + "=" * 70)
print("CREATING INVESTIGATION FLAGS")
print("=" * 70)


# Carrier delivered before purchase
orders["carrier_delivery_before_purchase"] = (
    orders["order_delivered_carrier_date"]
    < orders["order_purchase_timestamp"]
)


# Customer delivered before carrier
orders["customer_delivery_before_carrier"] = (
    orders["order_delivered_customer_date"]
    < orders["order_delivered_carrier_date"]
)


# ============================================================
# 1. UNMATCHED PRODUCT CATEGORIES
# ============================================================

print("\n" + "=" * 70)
print("1. UNMATCHED PRODUCT CATEGORIES")
print("=" * 70)


valid_categories = set(
    category_translation[
        "product_category_name"
    ].dropna()
)


unmatched_products = products[
    ~products["product_category_name"].isin(
        valid_categories
    )
].copy()


print(
    f"Products without category translation: "
    f"{len(unmatched_products):,}"
)


print("\nCategory values involved:")

print(
    unmatched_products[
        "product_category_name"
    ]
    .value_counts(dropna=False)
    .head(30)
)


print("\nSample unmatched products:")

print(
    unmatched_products[
        [
            "product_id",
            "product_category_name"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 2. CARRIER BEFORE PURCHASE
# ============================================================

print("\n" + "=" * 70)
print("2. CARRIER DELIVERY BEFORE PURCHASE")
print("=" * 70)


carrier_before_purchase = orders[
    orders["carrier_delivery_before_purchase"]
].copy()


print(
    f"Suspicious records: "
    f"{len(carrier_before_purchase):,}"
)


if not carrier_before_purchase.empty:

    carrier_before_purchase[
        "difference_hours"
    ] = (
        carrier_before_purchase[
            "order_delivered_carrier_date"
        ]
        -
        carrier_before_purchase[
            "order_purchase_timestamp"
        ]
    ).dt.total_seconds() / 3600


    print("\nSample records:")

    print(
        carrier_before_purchase[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "difference_hours"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


    print("\nTime difference statistics:")

    print(
        carrier_before_purchase[
            "difference_hours"
        ].describe()
    )


# ============================================================
# 3. CUSTOMER BEFORE CARRIER
# ============================================================

print("\n" + "=" * 70)
print("3. CUSTOMER DELIVERY BEFORE CARRIER")
print("=" * 70)


customer_before_carrier = orders[
    orders["customer_delivery_before_carrier"]
].copy()


print(
    f"Suspicious records: "
    f"{len(customer_before_carrier):,}"
)


if not customer_before_carrier.empty:

    customer_before_carrier[
        "difference_hours"
    ] = (
        customer_before_carrier[
            "order_delivered_customer_date"
        ]
        -
        customer_before_carrier[
            "order_delivered_carrier_date"
        ]
    ).dt.total_seconds() / 3600


    print("\nSample records:")

    print(
        customer_before_carrier[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "difference_hours"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


    print("\nTime difference statistics:")

    print(
        customer_before_carrier[
            "difference_hours"
        ].describe()
    )


# ============================================================
# 4. INVALID PRODUCT WEIGHTS
# ============================================================

print("\n" + "=" * 70)
print("4. INVALID PRODUCT WEIGHTS")
print("=" * 70)


# Recalculate instead of depending on a saved flag
invalid_weights = products[
    products["product_weight_g"].isna()
    |
    (products["product_weight_g"] <= 0)
].copy()


print(
    f"Invalid/missing weight records: "
    f"{len(invalid_weights):,}"
)


if not invalid_weights.empty:

    print(
        invalid_weights[
            [
                "product_id",
                "product_category_name",
                "product_weight_g"
            ]
        ]
        .to_string(index=False)
    )


# ============================================================
# 5. ZERO-VALUE PAYMENTS
# ============================================================

print("\n" + "=" * 70)
print("5. ZERO-VALUE PAYMENTS")
print("=" * 70)


zero_payments = payments[
    payments["payment_value"] == 0
].copy()


print(
    f"Zero-payment records: "
    f"{len(zero_payments):,}"
)


if not zero_payments.empty:

    print(
        zero_payments[
            [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value"
            ]
        ]
        .to_string(index=False)
    )


# ============================================================
# 6. INVALID PAYMENT INSTALLMENTS
# ============================================================

print("\n" + "=" * 70)
print("6. INVALID PAYMENT INSTALLMENTS")
print("=" * 70)


invalid_installments = payments[
    payments["payment_installments"] <= 0
].copy()


print(
    f"Invalid installment records: "
    f"{len(invalid_installments):,}"
)


if not invalid_installments.empty:

    print(
        invalid_installments[
            [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value"
            ]
        ]
        .to_string(index=False)
    )


# ============================================================
# 7. EXTREME DELIVERY DURATIONS
# ============================================================

print("\n" + "=" * 70)
print("7. EXTREME DELIVERY DURATIONS")
print("=" * 70)


# Calculate delivery days if not already present
if "delivery_days" not in orders.columns:

    orders["delivery_days"] = (
        orders["order_delivered_customer_date"]
        -
        orders["order_purchase_timestamp"]
    ).dt.total_seconds() / (60 * 60 * 24)


extreme_deliveries = orders[
    orders["delivery_days"] > 90
].copy()


print(
    f"Deliveries over 90 days: "
    f"{len(extreme_deliveries):,}"
)


if not extreme_deliveries.empty:

    print("\nExtreme delivery records:")

    columns_to_show = [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "delivery_days"
    ]

    if "delivery_delay_days" in orders.columns:
        columns_to_show.append(
            "delivery_delay_days"
        )

    print(
        extreme_deliveries[
            columns_to_show
        ]
        .sort_values(
            "delivery_days",
            ascending=False
        )
        .head(30)
        .to_string(index=False)
    )


# ============================================================
# 8. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATA QUALITY INVESTIGATION SUMMARY")
print("=" * 70)


print(
    f"""
Unmatched product categories:       {len(unmatched_products):,}
Carrier before purchase:            {len(carrier_before_purchase):,}
Customer before carrier:            {len(customer_before_carrier):,}
Invalid/missing weights:            {len(invalid_weights):,}
Zero-value payments:                {len(zero_payments):,}
Invalid installments:               {len(invalid_installments):,}
Deliveries > 90 days:               {len(extreme_deliveries):,}
"""
)


print("=" * 70)
print("INVESTIGATION COMPLETE")
print("=" * 70)

print("\nNo data was modified.")
print("No records were deleted.")
print("Results are for investigation only.")

