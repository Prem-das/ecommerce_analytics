# E-commerce Analytics Project

An end-to-end e-commerce data analytics project built using the Olist Brazilian e-commerce dataset.

This README documents the project **up to the completion of the Python analysis stage**.

---

# Project Workflow Completed So Far

```text
RAW DATA
   ↓
01_data_profiling.py
   ↓
02_data_cleaning.py
   ↓
03_data_quality_investigation.py
   ↓
04_analytical_dataset.py
   ↓
05_business_analysis.py
   ↓
06_advanced_business_analysis.py
```

The purpose of this stage is to move from raw operational data to validated, business-ready analytical findings.

---

# 1. Project Directory Structure

```text
ecommerce_analytics/
│
├── README.md
│
├── data/
│   │
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── geolocation.csv
│   │   ├── order_items.csv
│   │   ├── payments.csv
│   │   ├── reviews.csv
│   │   ├── orders.csv
│   │   ├── products.csv
│   │   ├── sellers.csv
│   │   └── product_category_name_translation.csv
│   │
│   ├── processed/
│   │   ├── customers_clean.csv
│   │   ├── geolocation_clean.csv
│   │   ├── order_items_clean.csv
│   │   ├── payments_clean.csv
│   │   ├── reviews_clean.csv
│   │   ├── orders_clean.csv
│   │   ├── products_clean.csv
│   │   ├── sellers_clean.csv
│   │   ├── category_translation_clean.csv
│   │   └── products_enriched.csv
│   │
│   └── analysis/
│       ├── monthly_revenue.csv
│       ├── revenue_by_customer_state.csv
│       ├── category_analysis.csv
│       ├── product_analysis.csv
│       ├── seller_analysis.csv
│       ├── delivery_by_state.csv
│       ├── late_delivery_vs_reviews.csv
│       ├── review_by_category.csv
│       │
│       └── advanced/
│           └── [advanced analysis outputs]
│
├── python/
│   ├── 01_data_profiling.py
│   ├── 02_data_cleaning.py
│   ├── 03_data_quality_investigation.py
│   ├── 04_analytical_dataset.py
│   ├── 05_business_analysis.py
│   └── 06_advanced_business_analysis.py
│
├── sql/
├── excel/
├── powerbi/
└── reports/
```

The folders after `python/` are part of the broader project structure but are **not documented as completed stages in this README**.

---

# 2. Raw Dataset

The project starts with the raw Olist e-commerce dataset.

The raw data contains the following major tables:

```text
customers
geolocation
order_items
payments
reviews
orders
products
sellers
product_category_name_translation
```

These files are stored in:

```text
data/raw/
```

The raw files are treated as the original source data.

**Raw data should not be modified.**

---

# 3. 01_data_profiling.py

## Purpose

The first Python script is used to understand the raw dataset before making changes.

It establishes:

- Number of rows
- Number of columns
- Column names
- Data types
- Missing values
- Duplicate records
- Unique values
- Numeric distributions
- Categorical distributions
- Order-status distributions
- Initial data-quality issues

The goal is to answer:

> **What do we have in the dataset, and what problems exist?**

This prevents cleaning or analysis decisions from being made blindly.

### Input

```text
data/raw/
```

### Output

Profiling information used to guide the cleaning stage.

---

# 4. 02_data_cleaning.py

## Purpose

This stage converts the raw data into cleaner, more consistent datasets.

The raw data remains untouched.

The cleaned datasets are written to:

```text
data/processed/
```

## Main cleaning operations

### Text standardization

Appropriate text fields are standardized by handling issues such as unnecessary whitespace and inconsistent formatting.

However, legitimate differences are not blindly destroyed.

For example:

```text
sao paulo
são paulo
```

are not automatically treated as the same value simply because they look similar.

Any mapping of legitimate values should have an analytical reason behind it.

### Date conversion

Order-related timestamp columns are converted to appropriate datetime values.

### Numeric standardization

Numeric fields are converted and validated.

### Duplicate handling

Exact duplicate records are investigated and removed where appropriate.

For example, duplicate geolocation records were identified during the cleaning process.

### Financial checks

The pipeline checks:

```text
Negative prices
Zero prices
Negative freight
Zero freight
```

### Payment checks

The pipeline checks:

```text
Zero payments
Invalid installments
```

### Product checks

The pipeline checks:

```text
Missing categories
Missing weights
Invalid weights
Missing dimensions
Invalid dimensions
```

### Review checks

Review scores are validated.

### Order checks

Order statuses and order timestamps are validated.

### Delivery checks

The pipeline investigates:

```text
Delivery before purchase
Estimated delivery before purchase
Approval before purchase
Carrier delivery before purchase
Customer delivery before carrier
```

### Referential integrity

Relationships between the major tables are checked:

```text
order_items → orders
order_items → products
order_items → sellers
orders → customers
payments → orders
reviews → orders
products → categories
```

## Main processed outputs

```text
customers_clean.csv
geolocation_clean.csv
order_items_clean.csv
payments_clean.csv
reviews_clean.csv
orders_clean.csv
products_clean.csv
sellers_clean.csv
category_translation_clean.csv
products_enriched.csv
```

---

# 5. 03_data_quality_investigation.py

## Purpose

Not every suspicious record should be deleted.

This stage investigates anomalies discovered during the cleaning and validation process.

The script produces investigation results without modifying the underlying data.

## Issues investigated

### Unmatched product categories

The investigation identified unmatched category values including:

```text
NaN
portateis_cozinha_e_preparadores_de_alimentos
pc_gamer
```

### Carrier delivery before purchase

Records where the carrier delivery timestamp appears before the purchase timestamp are investigated.

### Customer delivery before carrier

Records where the customer delivery timestamp appears before the carrier delivery timestamp are investigated.

### Invalid or missing product weights

Missing and zero-value weights are investigated.

### Zero-value payments

Zero-payment records are identified for investigation.

### Invalid payment installments

Invalid installment values are identified.

### Extreme delivery durations

Very long delivery periods are identified for further investigation.

## Important principle

This script is an investigation layer.

It does not silently delete suspicious records.

```text
No data was modified.
No records were deleted.
Results are for investigation only.
```

---

# 6. 04_analytical_dataset.py

## Purpose

After cleaning and quality investigation, the next stage creates the analytical layer used for business analysis.

This stage prepares the data so that business questions can be answered consistently.

The analytical layer contains or derives metrics such as:

- Revenue
- Freight
- Total order value
- Delivery duration
- Delivery delay
- Customer type
- Product information
- Category information
- Customer state
- Review information

## Revenue reconciliation

A key validation was performed:

```text
Revenue from order items : R$ 13,591,643.70
Revenue from orders      : R$ 13,591,643.70
Difference               : R$ 0.00
```

This confirms that the revenue calculations reconcile.

The analytical dataset therefore provides the foundation for the business analysis stage.

---

# 7. 05_business_analysis.py

## Purpose

This is the main business analysis stage.

It converts the analytical data into business KPIs and analysis tables.

---

## Executive KPIs

The analysis produced:

```text
Total revenue              : R$ 13,591,643.70
Total freight              : R$ 2,251,909.54
Total order value          : R$ 15,843,553.24
Total orders               : 99,441
Total items                : 112,650
Unique customers           : 96,096
Revenue AOV                : R$ 136.68
AOV including freight      : R$ 159.33
Freight / revenue          : 16.57%
Repeat customer rate       : 3.12%
Average delivery time      : 12.56 days
Median delivery time       : 10.22 days
Late delivery rate         : 8.11%
Extreme delivery rate      : 0.08%
Average review score       : 4.09
```

---

## Revenue Analysis

Monthly revenue analysis includes:

- Revenue
- Freight
- Orders
- AOV
- Revenue growth

Output:

```text
data/analysis/monthly_revenue.csv
```

---

## Customer Analysis

Customer analysis includes:

- One-time customers
- Repeat customers
- Customer share
- Revenue by customer state
- Orders by state
- State-level AOV

Output:

```text
data/analysis/revenue_by_customer_state.csv
```

The observed repeat customer rate was:

```text
3.12%
```

---

## Product Analysis

Category-level analysis includes:

- Revenue
- Freight
- Orders
- Items
- Average price
- Freight percentage
- Revenue share

Output:

```text
data/analysis/category_analysis.csv
```

Product-level analysis includes:

- Revenue
- Freight
- Orders
- Items
- Average price

Output:

```text
data/analysis/product_analysis.csv
```

---

## Seller Analysis

Seller-level analysis includes:

- Revenue
- Freight
- Orders
- Items
- Average item price

Output:

```text
data/analysis/seller_analysis.csv
```

---

## Operations Analysis

Operations analysis includes:

- Delivered orders
- Average delivery time
- Median delivery time
- Late delivery rate
- Extreme delivery rate
- Delivery performance by state

Output:

```text
data/analysis/delivery_by_state.csv
```

---

## Customer Experience Analysis

Customer experience analysis includes:

- Review score distribution
- Average review score
- Late delivery vs review score
- Review performance by category

Outputs:

```text
data/analysis/late_delivery_vs_reviews.csv
data/analysis/review_by_category.csv
```

A key finding from this analysis was that late orders had a substantially lower average review score than on-time orders.

---

# 8. 06_advanced_business_analysis.py

## Purpose

The advanced analysis stage goes deeper than the standard business KPIs.

It is used to investigate deeper business patterns involving areas such as:

- Customer behavior
- Product performance
- Category performance
- Seller performance
- Delivery performance
- Business concentration
- Segmentation
- Relationships between business metrics

The outputs from this stage are stored separately in:

```text
data/analysis/advanced/
```

This keeps the core business analysis separate from the deeper analytical work.

---

# Python Pipeline Summary

| File | Purpose |
|---|---|
| `01_data_profiling.py` | Understand the raw dataset |
| `02_data_cleaning.py` | Clean and standardize the data |
| `03_data_quality_investigation.py` | Investigate suspicious records |
| `04_analytical_dataset.py` | Build the business-ready analytical layer |
| `05_business_analysis.py` | Produce core business analysis and KPIs |
| `06_advanced_business_analysis.py` | Perform deeper business analysis |

---

# Complete Python Data Flow

```text
data/raw/
    │
    ▼
01_data_profiling.py
    │
    ▼
02_data_cleaning.py
    │
    ▼
data/processed/
    │
    ▼
03_data_quality_investigation.py
    │
    ▼
04_analytical_dataset.py
    │
    ├───────────────┐
    ▼               ▼
05_business_      06_advanced_
analysis.py       business_analysis.py
    │               │
    ▼               ▼
data/analysis/    data/analysis/advanced/
```

---

# Running the Python Pipeline

Run the scripts in this order:

```bash
python python/01_data_profiling.py
python python/02_data_cleaning.py
python python/03_data_quality_investigation.py
python python/04_analytical_dataset.py
python python/05_business_analysis.py
python python/06_advanced_business_analysis.py
```

The scripts should be run sequentially because later stages depend on outputs created by earlier stages.

---

# Data Handling Principles

## 1. Raw data is preserved

The original files in:

```text
data/raw/
```

should remain unchanged.

## 2. Cleaning comes before analysis

The project separates:

```text
profiling
→ cleaning
→ investigation
→ analytical preparation
→ business analysis
```

## 3. Suspicious does not automatically mean incorrect

Anomalies are investigated before deciding whether they should be modified or excluded.

## 4. IDs are identifiers

Fields such as:

```text
order_id
customer_id
product_id
seller_id
```

are keys and should not be treated as ordinary numerical measures.

## 5. Do not over-clean legitimate values

Values should not be changed simply because they look inconsistent.

For example:

```text
sao paulo
são paulo
```

should only be mapped together when there is a justified analytical reason.

---

# Python Environment

Recommended Python version:

```text
Python 3.10+
```

Main package used:

```text
pandas
```

Install with:

```bash
pip install pandas
```

---

# Current Project Status

The Python analysis stage is complete through:

```text
01_data_profiling.py
02_data_cleaning.py
03_data_quality_investigation.py
04_analytical_dataset.py
05_business_analysis.py
06_advanced_business_analysis.py
```

At this point, the project has progressed from raw data to cleaned, validated, analytical, and business-level Python outputs.

The README intentionally stops here and does not document the later stages of the broader project.
