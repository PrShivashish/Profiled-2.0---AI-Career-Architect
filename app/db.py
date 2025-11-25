import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- CHANGE 1: Get DATABASE_URL from environment (Render sets this automatically) ---
# OLD: load_dotenv() + DB_URL = os.getenv("DB_URL")
# NEW: Direct environment read with fallback for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",  # Render will set this
    "postgresql://user:password@localhost:5432/hr_reco"  # Local fallback
)

# --- CHANGE 2: Fix Render's postgres:// to postgresql:// (SQLAlchemy requirement) ---
# Render PostgreSQL gives "postgres://" but SQLAlchemy needs "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- UNCHANGED: Create engine ---
engine = create_engine(DATABASE_URL)

# --- CHANGE 3: Add SessionLocal for better connection management ---
SessionLocal = sessionmaker(bind=engine)

# --- UNCHANGED: Load jobs function ---
def load_jobs_df():
    return pd.read_sql("SELECT * FROM linkedin_jobs", engine)

# --- CHANGE 4: Add session management function (best practice for production) ---
def get_db():
    """
    Database session generator for FastAPI dependency injection.
    Ensures connections are properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
