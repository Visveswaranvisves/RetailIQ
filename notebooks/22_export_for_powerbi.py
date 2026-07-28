import sqlite3
import pandas as pd
from pathlib import Path

conn = sqlite3.connect("../retailiq.db")

export_dir = Path("../powerbi/data")
export_dir.mkdir(parents=True, exist_ok=True)

tables_to_export = {
    "customer_features": "customer_features.csv",
    "cohort_retention": "cohort_retention.csv",
    "rfm_segments": "rfm_segments.csv",
    "delivery_vs_review": "delivery_vs_review.csv",
}

# Also export a seller performance table (new, needed for the dashboard)
seller_query = """
SELECT
    s.seller_id,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS order_count,
    ROUND(SUM(oi.price), 2) AS total_sales,
    ROUND(AVG(oi.price), 2) AS avg_item_price,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM order_items_clean oi
JOIN sellers_clean s ON oi.seller_id = s.seller_id
JOIN reviews_clean r ON oi.order_id = r.order_id
GROUP BY s.seller_id, s.seller_state
"""
seller_perf = pd.read_sql(seller_query, conn)
seller_perf.to_csv(export_dir / "seller_performance.csv", index=False)
print(f"seller_performance: {seller_perf.shape}")

# Geographic sales summary (state-level, for the map visual)
geo_sales_query = """
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(p.payment_value), 2) AS total_revenue,
    ROUND(AVG(p.payment_value), 2) AS avg_order_value
FROM orders_clean o
JOIN customers_clean c ON o.customer_id = c.customer_id
JOIN payments_clean p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
"""
geo_sales = pd.read_sql(geo_sales_query, conn)
geo_sales.to_csv(export_dir / "geo_sales.csv", index=False)
print(f"geo_sales: {geo_sales.shape}")

for table, fname in tables_to_export.items():
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    df.to_csv(export_dir / fname, index=False)
    print(f"{table}: {df.shape}")

conn.close()
print("\nAll exports complete -- ready for Power BI import")