import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
import re
from pathlib import Path
import os

# --- SETUP PATHS ---
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SKILL_DICT_PATH = DATA_DIR / "skills_dict.txt"
OUTPUT_CSV = DATA_DIR / "linkedin_jobs_india.csv"

# --- CONFIGURATION: UNIVERSAL INDIA SEARCH ---
LOCATION = "India"
MAX_PAGES_PER_ROLE = 1 

# THE MEGA LIST (55+ Roles for Maximum Diversity)
JOB_ROLES = [
    # --- TECH & IT ---
    "Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Machine Learning Engineer",
    "Data Scientist", "Data Analyst", "UI UX Designer", "Product Manager", "DevOps Engineer",
    "Cloud Architect", "Cyber Security Analyst", "Mobile App Developer", "QA Engineer",
    
    # --- CORE ENGINEERING ---
    "Electrical Engineer", "Electronics Engineer", "Embedded Systems Engineer",
    "VLSI Engineer", "Mechanical Engineer", "Automobile Engineer", "Civil Engineer",
    "Structural Engineer", "Chemical Engineer", "Petroleum Engineer", "Biomedical Engineer",

    # --- BUSINESS & MANAGEMENT ---
    "Business Analyst", "Project Manager", "Human Resources Manager", "Talent Acquisition",
    "Marketing Manager", "Digital Marketing Specialist", "Sales Executive", 
    "Supply Chain Manager", "Operations Manager", "Strategy Consultant",

    # --- FINANCE & COMMERCE ---
    "Chartered Accountant", "Financial Analyst", "Investment Banker", "Tax Consultant",
    "Risk Analyst", "Accountant", "Auditor",

    # --- CREATIVE & MEDIA ---
    "Graphic Designer", "Content Writer", "Video Editor", "Journalist", 
    "Fashion Designer", "Interior Designer", "Architect", "Copywriter",

    # --- SCIENCE & HEALTHCARE ---
    "Pharmacist", "Biotechnologist", "Microbiologist", "Clinical Research Associate",
    "Food Technologist", "Environmental Scientist", "Lab Technician"
]

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

def load_skill_vocab():
    if not SKILL_DICT_PATH.exists():
        print(f"[WARN] skills_dict.txt not found at: {SKILL_DICT_PATH}")
        return []
    with SKILL_DICT_PATH.open("r", encoding="utf-8") as f:
        return [s.strip().lower() for s in f.readlines() if s.strip()]

skills_vocab = load_skill_vocab()
print(f"Loaded {len(skills_vocab)} skills from dictionary")

def extract_skills_from_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    text_low = text.lower()
    found = []
    for skill in skills_vocab:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_low):
            found.append(skill)
    return ";".join(sorted(set(found)))

def fetch_page(query: str, start: int) -> str | None:
    params = {"keywords": query, "location": LOCATION, "start": start}
    try:
        res = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"[ERROR] Fetching {query} (start={start}): {e}")
        return None

def parse_job_list(html: str):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("li")
    jobs = []
    for card in cards:
        try:
            title_tag = card.find("h3", {"class": "base-search-card__title"})
            company_tag = card.find("h4", {"class": "base-search-card__subtitle"})
            loc_tag = card.find("span", {"class": "job-search-card__location"})
            link_tag = card.find("a", {"class": "base-card__full-link"})
            
            if title_tag and link_tag:
                jobs.append({
                    "Title": title_tag.get_text(strip=True),
                    "Company": company_tag.get_text(strip=True) if company_tag else "Unknown",
                    "Location": loc_tag.get_text(strip=True) if loc_tag else "India",
                    "URL": link_tag["href"]
                })
        except:
            continue
    return jobs

def fetch_job_description(url: str) -> str:
    if not url: return ""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        desc_div = soup.find("div", class_="show-more-less-html__markup")
        if desc_div:
            return desc_div.get_text(separator=" ", strip=True)
    except:
        pass
    return ""

def scrape_universal_jobs():
    print(f"🚀 Starting Universal Scraper for {len(JOB_ROLES)} Roles...")
    
    # 1. LOAD EXISTING DATA (Smart Appending)
    existing_urls = set()
    all_rows = []
    
    if OUTPUT_CSV.exists():
        try:
            df_existing = pd.read_csv(OUTPUT_CSV)
            all_rows = df_existing.to_dict('records')
            existing_urls = set(df_existing["URL"].tolist())
            print(f"Loaded {len(all_rows)} existing jobs. Searching for fresh ones...")
        except Exception as e:
            print(f"Could not load existing CSV (starting fresh): {e}")
            all_rows = []

    # 2. SCRAPE NEW JOBS
    random.shuffle(JOB_ROLES) # Shuffle to vary requests and avoid pattern detection
    
    for i, role in enumerate(JOB_ROLES):
        print(f"[{i+1}/{len(JOB_ROLES)}] Searching: {role}")
        
        for page in range(MAX_PAGES_PER_ROLE):
            start = page * 25
            html = fetch_page(role, start)
            if not html: continue
            
            new_jobs = parse_job_list(html)
            unique_new_jobs = [j for j in new_jobs if j["URL"] not in existing_urls]
            
            print(f"   found {len(new_jobs)} listings -> {len(unique_new_jobs)} are new")
            
            for job in unique_new_jobs:
                desc = fetch_job_description(job['URL'])
                job['Description'] = desc
                job['skills_required'] = extract_skills_from_text(desc)
                
                all_rows.append(job)
                existing_urls.add(job['URL'])
                
                # Random sleep to mimic human behavior
                time.sleep(random.uniform(0.8, 1.8))
            
            time.sleep(1) # Pause between pages

    # 3. SAVE UPDATED DATABASE
    df_final = pd.DataFrame(all_rows)
    df_final.drop_duplicates(subset=["URL"], inplace=True)
    df_final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    
    print(f"\n✅ SUCCESS: Database updated. Total Jobs: {len(df_final)}")
    print(f"   Saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    scrape_universal_jobs()