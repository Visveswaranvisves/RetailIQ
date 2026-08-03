import sqlite3
import pandas as pd
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "..", "retailiq.db")
conn = sqlite3.connect(db_path)

print("=" * 60)
print("RECONCILIATION CHECK -- run these against Power BI visuals")
print("=" * 60)

# Total customers
total_customers = pd.read_sql("SELECT COUNT(*) AS n FROM customer_features", conn)
print(f"\nTotal customers (customer_features): {total_customers['n'][0]}")

# Total revenue
total_revenue = pd.read_sql(
    "SELECT ROUND(SUM(payment_value), 2) AS total FROM payments_clean", conn)
print(f"Total revenue (all payments): {total_revenue['total'][0]}")

# Overall churn rate
churn_rate = pd.read_sql("SELECT AVG(churned) AS rate FROM customer_features", conn)
print(f"Overall churn rate: {round(churn_rate['rate'][0]*100, 2)}%")

# Segment counts (should match Power BI CLV segment chart)
segment_counts = pd.read_sql(
    "SELECT segment, COUNT(*) AS n FROM rfm_segments GROUP BY segment ORDER BY n DESC", conn)
print("\nSegment counts:")
print(segment_counts)

# Cohort month 0 retention (should be 100% for every cohort in the heatmap)
cohort_check = pd.read_sql(
    "SELECT cohort_month, retention_pct FROM cohort_retention WHERE month_index = 0", conn)
print(f"\nCohort month_index=0 all at 100%: {(cohort_check['retention_pct'] == 100.0).all()}")

# Top 5 sellers by revenue (should match Power BI top-15 chart's top entries)
top_sellers = pd.read_sql("""
    SELECT s.seller_id, ROUND(SUM(oi.price), 2) AS total_sales
    FROM order_items_clean oi
    JOIN sellers_clean s ON oi.seller_id = s.seller_id
    GROUP BY s.seller_id
    ORDER BY total_sales DESC
    LIMIT 5
""", conn)
print("\nTop 5 sellers by revenue:")
print(top_sellers)

# Top 5 states by revenue (should match the geo map/bar chart)
top_states = pd.read_sql("""
    SELECT c.customer_state, ROUND(SUM(p.payment_value), 2) AS total_revenue
    FROM orders_clean o
    JOIN customers_clean c ON o.customer_id = c.customer_id
    JOIN payments_clean p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    ORDER BY total_revenue DESC
    LIMIT 5
""", conn)
print("\nTop 5 states by revenue:")
print(top_states)

conn.close()