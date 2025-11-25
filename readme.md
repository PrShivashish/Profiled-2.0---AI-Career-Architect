# 🔍 HR Job Matching & Skill Gap Analysis
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)

End-to-End AI Engineering Project using Python, PostgreSQL, FastAPI, Streamlit, and LinkedIn Scraping

This project builds an end-to-end system for:
- Extracting job openings from LinkedIn (manual scraping)
- Cleaning and saving job data to PostgreSQL
- Extracting skills from CVs (PDF)
- Analyzing candidate fit-scores for jobs
- Identifying skill gaps
- Displaying results in a Streamlit-based interactive dashboard
- Simple ATS Score Calculation

---

## 📁 Project Structure
```
HR/
│
├─ app/ # Backend (FastAPI)
│ ├─ api.py
│ ├─ main.py
│ ├─ ats.py
│ ├─ db.py
│
├─ scripts/ # LinkedIn scraper
│ ├─ linkedin_scraper.py
│ ├─ db_init.py
│ ├─ ingest_data.py
│ ├─ test_connection.py
│
├─ data/ # Local dataset
│ ├─ skills_dict.txt
│ ├─ linkedin_jobs_indonesia.csv # <- scraping results
│
├─ sql/
│ ├─ schema.sql # Table creation
│
├─ ui/
│ ├─ static/ # html files
│ ├─ dashboard.py # Streamlit UI
│ ├─ app.py # Flask UI
│
├─ docker-compose.yaml
└─ requirements.txt
```

---

## 🚀 Features

### 📌 1. LinkedIn Job Scraper (Indonesia)
- Scraping title, company, location, URL.
- Scraping job description (LinkedIn HTML).
- Automatically extract required skills from the description.
- Save output to `data/linkedin_jobs_indonesia.csv`.

### 📌 2. PostgreSQL Job Database
- The `linkedin_jobs` table is created via `schema.sql`.
- Saves all scraping results for use in the recommender.

### 📌 3. FastAPI Recommender
- Extract skills from PDF CVs using a dictionary.
- Calculation:
- ATS Score
- Skill Overlap
- Skill Gap
- Fit Score (weighted similarity)
- Returns top-N job recommendations complete with URLs.

### 📌 4. Streamlit Dashboard
- Upload CV (PDF)
- View:
- ATS Score
- Detected Skills
- Job Recommendations
- Skill-Gap List
- Direct link to the original job opening

---

## ⚙️ Installation

### 1. Clone repository
```bash
git clone https://github.com/yourusername/hr-job-matching.git
HR CD
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate # Mac/Linux
.venv\Scripts\activate # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🗄️ PostgreSQL Setup

Use Configuration:
```bash
user: (user)
password: (password)
database: hr_reco
host: localhost
port: 5432
```

### 1. Create a database
```bash
CREATE hr_reco DATABASE;
```

### 2. Run the schema (create a table)
```bash
python scripts/db_init.py
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
This script will execute schema.sql and create a table:
```bash
public.linkedin_jobs
```

## 🔎 Scraping & Data Preparation

### 1. Run the LinkedIn Scraper
```bash
python scripts/linkedin_scraper.py
```

The scraping results will be saved to:
```bash
data/linkedin_jobs_indonesia.csv
```

### 2. Ingest CSV to PostgreSQL
```bash
python scripts/ingest_data.py
```

## 🚀 Execute Backend (FastAPI)

Start API server:

```bash
uvicorn app.api:app --reload --port 8000
```

**POST /match**
input:

```bash
{ 
"cv_text": ".....", 
"top_k": 5
}
```

Output:

```bash
{ 
"ats_score": 0.82, 
"candidate_skills": [...], 
"top_jobs": [ 
{ 
"job_id": 1, 
"title": "Machine Learning Engineer", 
"company": "Gojek", 
"location": "Jakarta", 
"fit_score": 0.64, 
"overlap_skills": [...], 
"gap_skills": [...], 
"url": "https://linkedin.com/jobs/view/..." 
}
]
}
```

## 🖥️ Running the UI (Streamlit / Flask)
```bash
streamlit run ui/dashboard.py # Streamlit
python ui/app.py # Flask
```

The dashboard can:
- Upload a PDF CV
- Display an ATS Score
- Display automatic skills
- Display job recommendations
- Display skill gaps
- Display job links

## 🧠 Fit Score Formula
```bash
fit_score = 0.6 * overlap_ratio + 0.4 * jaccard_similarity
```

Explanation:
- overlap_ratio = number of matching skills / total required skills
- jaccard similarity = intersection / union
- Generates a ranking of the most relevant jobs

## 📖 ATS Score Calculation

ATS Score based on:
- CV length
- CV structure (education, experience, skills, projects)
- Noise-free format
- Readability

Scale:
```bash
0.0 → 1.0
```

## 📊 End-to-End Workflow Diagram

```
[1] LinkedIn Scraper 
↓
[2] Save CSV to data/ 
↓
[3] Ingest CSV → PostgreSQL 
↓
[4] FastAPI loads job table 
↓
[5] User upload CV (PDF) → UI 
↓
[6] FastAPI → ATS Score + Skill Extract + Matching 
↓
[7] Streamlit displays ranked job recommendations
```

## 💡 Future Enhancements
- Matching based embeddings (SBERT/BGE/MiniLM)
- Job summarization (LLM)
- Multi-platform scraper (Glints, JobStreet, Kalibrr)
- Docker deployment (API + UI + DB)
- CI/CD Github Actions
- Automatic taxonomy extraction skill

## 🏆 Tech Stack
- **Languages**: Python
- **Backend**: FastAPI
- **Frontend**: Streamlit / Flask
- **Database**: PostgreSQL
- **Scraping**: BeautifulSoup4
- **PDF Parser**: PyPDF
- **Deployment (optional)**: Docker
