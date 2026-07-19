import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

tables = ["orders", "order_items", "customers", "payments", "reviews", "products", "sellers"]

for table in tables:
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    print(f"\n=== {table} ({len(df)} rows) ===")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if len(nulls) > 0:
        print("Nulls found:\n", nulls)
    else:
        print("No nulls.")
    dupes = df.duplicated().sum()
    print(f"Duplicate rows: {dupes}")

conn.close()
