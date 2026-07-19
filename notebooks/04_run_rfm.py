import sqlite3
import pandas as pd

conn = sqlite3.connect("retailiq.db")

with open("sql/01_rfm_segmentation.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, conn)
print(f"RFM table shape: {df.shape}")
print(df.head(10))
print("\nSegment counts:\n", df["segment"].value_counts())

df.to_sql("rfm_segments", conn, if_exists="replace", index=False)
conn.close()
print("\nSaved as table 'rfm_segments' in retailiq.db")