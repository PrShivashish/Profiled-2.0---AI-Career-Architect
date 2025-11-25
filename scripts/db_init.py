import psycopg2
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

SCHEMA_PATH = Path("sql/schema.sql")

def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"schema.sql not found at: {SCHEMA_PATH}")

    print(f"Reading schema from: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            print("🛠 Running schema.sql ...")
            cur.execute(schema_sql)
        print("Schema executed successfully.")
    finally:
        conn.close()
        print("Connection closed.")


if __name__ == "__main__":
    init_db()