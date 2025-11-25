import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Database Configuration
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    print("❌ ERROR: DB_URL not found in .env file")
    exit()

# Setup Paths
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "linkedin_jobs_india.csv"

def ingest_data():
    print(f"📂 Looking for data at: {CSV_PATH}")

    if not CSV_PATH.exists():
        print(f"❌ ERROR: CSV file not found at {CSV_PATH}")
        print("   Please run 'python scripts/linkedin_scraper.py' first.")
        return

    try:
        # Read CSV
        print("📖 Reading CSV file...")
        jobs = pd.read_csv(CSV_PATH)
        print(f"✅ CSV Loaded Successfully. Rows: {len(jobs)}")
        
        if len(jobs) < 100:
            print("⚠️ WARNING: CSV has very few rows. Did the scraper finish?")

        # Connect to DB
        print("🔌 Connecting to Database...")
        engine = create_engine(DB_URL)
        
        # Test Connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful.")

        # Ingest Data
        print("🚀 Uploading data to 'linkedin_jobs' table...")
        # 'replace' drops the table if it exists and creates a new one
        jobs.to_sql("linkedin_jobs", engine, if_exists="replace", index=False)
        
        print("🎉 SUCCESS: Data ingestion complete.")
        print(f"   Total Jobs in DB: {len(jobs)}")

    except Exception as e:
        print(f"❌ CRITICAL ERROR during ingestion: {e}")

if __name__ == "__main__":
    ingest_data()