import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

# --- Orders ---
orders = pd.read_sql("SELECT * FROM orders", conn)
date_cols = ["order_purchase_timestamp", "order_approved_at",
             "order_delivered_carrier_date", "order_delivered_customer_date",
             "order_estimated_delivery_date"]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

# Keep only delivered + canceled orders for analysis (drop unavailable/processing edge cases)
orders_clean = orders[orders["order_status"].isin(
    ["delivered", "canceled", "shipped", "invoiced"]
)].copy()

orders_clean.to_sql("orders_clean", conn, if_exists="replace", index=False)
print(f"orders_clean: {len(orders_clean)} rows (from {len(orders)} raw)")

# --- Payments ---
payments = pd.read_sql("SELECT * FROM payments", conn)
payments_clean = payments.dropna(subset=["payment_value"]).copy()
payments_clean = payments_clean[payments_clean["payment_value"] > 0]
payments_clean.to_sql("payments_clean", conn, if_exists="replace", index=False)
print(f"payments_clean: {len(payments_clean)} rows (from {len(payments)} raw)")

# --- Reviews ---
reviews = pd.read_sql("SELECT * FROM reviews", conn)
reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], errors="coerce")
reviews_clean = reviews.dropna(subset=["review_score"]).copy()
reviews_clean.to_sql("reviews_clean", conn, if_exists="replace", index=False)
print(f"reviews_clean: {len(reviews_clean)} rows (from {len(reviews)} raw)")

# --- Customers, Products, Sellers, Order Items: light pass ---
for table in ["customers", "order_items", "products", "sellers"]:
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    before = len(df)
    df = df.drop_duplicates()
    df.to_sql(f"{table}_clean", conn, if_exists="replace", index=False)
    print(f"{table}_clean: {len(df)} rows (from {before} raw, {before - len(df)} dupes dropped)")

conn.close()
print("\nCleaning complete. *_clean tables created alongside raw tables.")