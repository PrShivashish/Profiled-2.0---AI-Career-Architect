import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL)

def load_jobs_df():
    return pd.read_sql("SELECT * FROM linkedin_jobs", engine)