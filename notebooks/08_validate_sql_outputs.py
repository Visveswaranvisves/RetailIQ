import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

print("=" * 60)
print("VALIDATION 1: RFM totals should match total delivered orders")
print("=" * 60)
rfm = pd.read_sql("SELECT * FROM rfm_segments", conn)
raw_delivered = pd.read_sql(
    "SELECT COUNT(DISTINCT c.customer_unique_id) AS n FROM orders_clean o "
    "JOIN customers_clean c ON o.customer_id = c.customer_id "
    "WHERE o.order_status = 'delivered'", conn)
print(f"Unique customers in rfm_segments: {len(rfm)}")
print(f"Unique customers with delivered orders (raw check): {raw_delivered['n'][0]}")
print("MATCH" if len(rfm) == raw_delivered['n'][0] else "MISMATCH -- investigate")

print("\n" + "=" * 60)
print("VALIDATION 2: Cohort month_index=0 should always be 100% retention")
print("=" * 60)
cohort = pd.read_sql("SELECT * FROM cohort_retention", conn)
month0 = cohort[cohort["month_index"] == 0]
bad_rows = month0[month0["retention_pct"] != 100.0]
print(f"Rows where month_index=0 but retention != 100%: {len(bad_rows)}")
print("PASS" if len(bad_rows) == 0 else "FAIL -- check join logic")

print("\n" + "=" * 60)
print("VALIDATION 3: Repeat purchase count should be less than total customers")
print("=" * 60)
repeat = pd.read_sql("SELECT * FROM repeat_purchase_intervals", conn)
total_customers = pd.read_sql("SELECT COUNT(DISTINCT customer_unique_id) AS n FROM customers_clean", conn)
print(f"Repeat purchasers: {len(repeat)}")
print(f"Total unique customers: {total_customers['n'][0]}")
print(f"Repeat purchase rate: {round(100*len(repeat)/total_customers['n'][0], 2)}%")
print("PASS (sensible range)" if len(repeat) < total_customers['n'][0] else "FAIL")

print("\n" + "=" * 60)
print("VALIDATION 4: Late deliveries should have lower avg review score")
print("=" * 60)
delivery = pd.read_sql("SELECT * FROM delivery_vs_review", conn)
print(delivery)
late_score = delivery[delivery["delivery_status"] == "Late"]["avg_review_score"].values
ontime_score = delivery[delivery["delivery_status"] == "On Time / Early"]["avg_review_score"].values
if len(late_score) and len(ontime_score):
    print("PASS -- late < on-time" if late_score[0] < ontime_score[0] else "FAIL -- unexpected direction")

conn.close()
print("\nAll validations complete.")