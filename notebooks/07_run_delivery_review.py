import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

with open("sql/04_delivery_vs_review.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, conn)
print("On-time vs Late delivery — review score comparison:")
print(df)

# Extra: correlation between raw delivery days and review score, order-level
detail_query = """
SELECT
    JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS delivery_days,
    r.review_score
FROM orders_clean o
JOIN reviews_clean r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
"""
detail_df = pd.read_sql(detail_query, conn)
correlation = detail_df["delivery_days"].corr(detail_df["review_score"])
print(f"\nCorrelation (delivery_days vs review_score): {round(correlation, 3)}")

df.to_sql("delivery_vs_review", conn, if_exists="replace", index=False)
conn.close()
print("\nSaved as table 'delivery_vs_review' in retailiq.db")