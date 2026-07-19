import pandas as pd
import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = "retailiq.db"

files = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
}

conn = sqlite3.connect(DB_PATH)
for table, fname in files.items():
    df = pd.read_csv(DATA_DIR / fname)
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"{table}: {len(df)} rows, {df.shape[1]} columns")
conn.close()
print("Done. Database saved as retailiq.db")