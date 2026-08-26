import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

policies = pd.read_csv("data/policies/store_policies.csv")

for _, row in policies.iterrows():
    cursor.execute("""
        INSERT INTO policies
        (policy_type, description, conditions, timeframe)
        VALUES (%s, %s, %s, %s)
    """, (
        row["policy_type"],
        row["description"],
        row["conditions"],
        row["timeframe"]
    ))

conn.commit()

print(f"Loaded {len(policies)} policies into PostgreSQL.")

cursor.close()
conn.close()