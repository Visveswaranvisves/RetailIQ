import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

with open("sql/03_repeat_purchase_interval.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, conn)
print(f"Repeat purchasers: {df.shape[0]} customers")
print(df.head(10))
print("\nOverall avg days between orders:", round(df["avg_days_between_orders"].mean(), 1))
print("Distribution:\n", df["avg_days_between_orders"].describe())

df.to_sql("repeat_purchase_intervals", conn, if_exists="replace", index=False)
conn.close()
print("\nSaved as table 'repeat_purchase_intervals' in retailiq.db")