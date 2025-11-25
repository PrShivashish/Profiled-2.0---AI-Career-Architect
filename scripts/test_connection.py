import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
print(f"DB_URL = {DB_URL}")

try:
    print("Connecting to PostgreSQL...")
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        print("Connected successfully!")

        # test simple query
        result = conn.execute(text("SELECT now();"))
        print("Server time:", result.fetchone()[0])

        # check tables exist
        tables = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        ).fetchall()
        print("Tables:", [t[0] for t in tables])

        # count rows
        try:
            jobs_count = conn.execute(text("SELECT COUNT(*) FROM jobs")).fetchone()[0]
            print(f"jobs table rows: {jobs_count}")
        except Exception:
            print("Table 'jobs' not found.")

except Exception as e:
    print("Connection failed!")
    print("Error:", e)