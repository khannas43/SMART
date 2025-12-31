import psycopg2
import pandas as pd

HOST_IP = "172.17.16.1"  # WORKING IP!

print(f"Connecting to {HOST_IP}:5432...")
conn = psycopg2.connect(
    host=HOST_IP, port=5432, dbname="smart",
    user="sameer", password="anjali143"
)

# Fix pandas warning: use SQLAlchemy or raw cursor
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM schemes")
count = cursor.fetchone()[0]
print(f"✅ {count} schemes loaded!")

df = pd.read_sql("SELECT * FROM schemes LIMIT 5", conn)
print("✅ Data preview:")
print(df.head())
conn.close()
