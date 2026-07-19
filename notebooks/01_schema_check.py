import sqlite3
conn = sqlite3.connect("retailiq.db")
cur = conn.cursor()
for table in ["orders","order_items","customers","payments","reviews","products","sellers","geolocation"]:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    print(f"\n{table}:")
    print(f"  {cols}")
conn.close()