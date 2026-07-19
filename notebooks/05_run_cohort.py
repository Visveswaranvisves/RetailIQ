import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

with open("sql/02_cohort_retention.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, conn)
print(f"Cohort table shape: {df.shape}")
print(df.head(20))

# Quick pivot preview — this is the shape your Power BI heatmap will use
pivot = df.pivot(index="cohort_month", columns="month_index", values="retention_pct")
print("\nRetention % pivot (preview):")
print(pivot.iloc[:5, :6])

df.to_sql("cohort_retention", conn, if_exists="replace", index=False)
conn.close()
print("\nSaved as table 'cohort_retention' in retailiq.db")
