import pandas as pd
from pathlib import Path
# Use backslash or put r before writing the directory
DATA_DIR = DATA_DIR = Path("C:/Users/premk/OneDrive/Documents/ecommerce_analytics/data/raw")
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
    "category_translation": category_translation
}

for name, df in datasets.items():
    print(f"{name}: {df.shape}")

# This being just the more comprehensive way to know what is inside of every csv file
for name, df in datasets.items():
    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)
    print(df.columns.tolist())


# inspecting the missing values 

for name, df in datasets.items():
    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)
    missing = df.isnull().sum()
    print(missing[missing > 0])
#inspecting for duplicate values 

for name, df in datasets.items():
    print( f"{name} : {df.duplicated().sum()} dupicate rows")


# # checking if the order ids are unique expected value is 99441
print("Orders:", orders["order_id"].nunique())
print("Order rows:", len(orders))


print("Order items:", len(order_items))
print(
    "Unique orders in order_items:",
    order_items["order_id"].nunique()
)


# inspecting data types 

for name, df in datasets.items():
    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)
    print(df.dtypes)

# converting dates

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col])

print(orders[date_columns].dtypes)


# calculating delivery time 

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.days

print(orders["delivery_days"].describe())


# calculating late deliveries 

orders["is_late"] = (
    orders["order_delivered_customer_date"]
    > orders["order_estimated_delivery_date"]
)

print(orders["is_late"].value_counts())


# # calculating Late delivery rate:

late_delivery_rate = orders["is_late"].mean()

print(
    f"Late delivery rate: {late_delivery_rate:.2%}"
)



# order status

print(orders["order_status"].value_counts())

# for each order status how many missing delivery date we have 
print(
    pd.crosstab(
        orders["order_status"],
        orders["order_delivered_customer_date"].isna()
    )
)

print(
    orders.nlargest(
        10,
        "delivery_days"
    )[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "delivery_days"
        ]
    ].to_string()
)


delivered_orders = orders[
    orders["order_delivered_customer_date"].notna()
]

late_delivery_rate = delivered_orders["is_late"].mean()

print(
    f"Late delivery rate: {late_delivery_rate:.2%}"
)


print(order_items.head().to_string())
print(order_items.describe().to_string())


print(order_items["price"].describe())
print(order_items["freight_value"].describe())


print(order_items["order_id"].nunique())
print(order_items["product_id"].nunique())
print(order_items["seller_id"].nunique())


# checking for average items per order
items_per_order = (
    len(order_items)
    / order_items["order_id"].nunique()
)
print(f"Average items per order: {items_per_order:.2f}")




print("=="*50)
#how many orders contains more than one orders 

items_per_order2 = (
    order_items
    .groupby("order_id")
    .size()
)

print(items_per_order2.describe())

print(
    (items_per_order2 > 1).sum()
)



# Total Product Revenue 

total_revenue = order_items["price"].sum()
print(f"Total product revenue: R$ {total_revenue:,.2f}")

# Shipping Revenue 

total_freight = order_items["freight_value"].sum()
print(f"Total freight value: R$ {total_freight:,.2f}")

total_value = (
    total_revenue + total_freight
)

print(f"Product + freight value: R$ {total_value:,.2f}")


# Calculate AOV more importantly Average product revenue per order and Average freight value per order  

unique_orders = order_items["order_id"].nunique()

aov_product = total_revenue / unique_orders

aov_with_freight = total_value / unique_orders

print(f"Product AOV: R$ {aov_product:,.2f}")
print(f"Product + freight AOV: R$ {aov_with_freight:,.2f}")


#examine expansive products

print(
    order_items.nlargest(10, "price")[
        [
            "order_id",
            "product_id",
            "seller_id",
            "price",
            "freight_value"
        ]
    ]
)


# freight burden

order_items["freight_pct"] = (
    order_items["freight_value"]
    / order_items["price"]
) * 100


print(order_items["freight_pct"].describe())



print("--"*50)


# product categoryies that generate the most revenue

product_sales = order_items.merge(
    products[
        [
            "product_id",
            "product_category_name"
        ]
    ],
    on = "product_id",
    how="left"
)

print(product_sales.head())