import re
import pandas as pd
from typing import List, Dict
from .db import load_jobs_df
from .ats import ats_score

SKILL_PATH = "data/skills_dict.txt"

class JobRecommender:
    def __init__(self):
        print("Loading skills dictionary...")
        self.skills_vocab = self._load_skills()

        print("Loading jobs from PostgreSQL...")
        self.jobs = load_jobs_df()
        # Normalize columns
        self.jobs.columns = [c.lower() for c in self.jobs.columns]
        print(f"Loaded {len(self.jobs)} jobs.")

    def _load_skills(self):
        try:
            with open(SKILL_PATH, "r", encoding="utf-8") as f:
                return [s.strip().lower() for s in f if s.strip()]
        except Exception as e:
            print(f"Error loading skills: {e}")
            return []

    def extract_skills(self, text: str) -> List[str]:
        text_low = text.lower()
        skills_found = []
        for skill in sorted(self.skills_vocab, key=len, reverse=True):
            if re.search(r"\b" + re.escape(skill) + r"\b", text_low):
                skills_found.append(skill)
        return sorted(list(set(skills_found)))

    def compute_match_score(self, cv_text, candidate_skills, job_row, user_domain=None):
        # 1. SKILL SCORE
        skills_str = str(job_row.get("skills_required", ""))
        job_skills = [s.strip().lower() for s in skills_str.split(";") if s.strip()]
        
        set_c = set(candidate_skills)
        set_j = set(job_skills)
        overlap = set_c & set_j
        gap = set_j - set_c
        
        skill_score = len(overlap) / len(set_j) if len(set_j) > 0 else 0.0

        # 2. TITLE MATCH
        title = str(job_row.get("title", "")).lower()
        
        # 3. DOMAIN ENFORCEMENT (THE FIX)
        domain_score = 0.0
        
        if user_domain:
            user_domain = user_domain.lower()
            
            # A. HARD REJECT LOGIC (Anti-False Positive)
            # If user wants Food/Bio, reject tech keywords immediately
            if "food" in user_domain or "bio" in user_domain:
                tech_keywords = ["data scientist", "software", "full stack", "react", "python", "java developer", "ai engineer"]
                if any(k in title for k in tech_keywords):
                    return -1.0, [], [] # Kill this match immediately
            
            # If user wants Core Engineering, reject IT keywords
            if "civil" in user_domain or "mechanical" in user_domain or "electrical" in user_domain:
                it_keywords = ["software", "web", "frontend", "backend", "data", "cloud"]
                if any(k in title for k in it_keywords):
                    return -1.0, [], [] # Kill match

            # B. POSITIVE BOOSTING
            # Check if any word from the selected domain matches the job title
            # e.g. User: "Food Technologist", Job: "Food Safety Officer" -> Match on "Food"
            domain_keywords = user_domain.split()
            matches = sum(1 for k in domain_keywords if k in title)
            
            if matches > 0:
                domain_score = 1.0 # High boost for relevant title matches
            elif "technologist" in title and "food" in user_domain: # Specific override
                domain_score = 1.0

        else:
            # No domain selected? Fall back to basic title matching
            generic_words = ["senior", "junior", "lead", "manager", "associate", "intern"]
            title_keywords = [w for w in re.split(r'\W+', title) if w and w not in generic_words and len(w) > 2]
            
            matches = sum(1 for w in title_keywords if w in cv_text.lower())
            domain_score = matches / len(title_keywords) if len(title_keywords) > 0 else 0.0

        # 4. FINAL WEIGHTED SCORE
        # Domain matching is king (70%), Skills are secondary (30%)
        final_score = (domain_score * 0.7) + (skill_score * 0.3)

        return final_score, sorted(list(overlap)), sorted(list(gap))

    def compute(self, cv_text: str, top_k: int = 5, domain: str = None) -> Dict:
        ats = ats_score(cv_text)
        candidate_skills = self.extract_skills(cv_text)

        results = []
        for _, row in self.jobs.iterrows():
            score, overlap, gap = self.compute_match_score(cv_text, candidate_skills, row, domain)
            
            # Filter out garbage/rejected matches
            if score > 0.01: 
                results.append({
                    "job_id": int(row.get("id", 0)),
                    "title": row.get("title", "Unknown Role"),
                    "company": row.get("company", "Unknown Company"),
                    "location": row.get("location", "India"),
                    "url": row.get("url", "#"),
                    "fit_score": score,
                    "overlap_skills": overlap,
                    "gap_skills": gap
                })

        top_jobs = sorted(results, key=lambda x: x["fit_score"], reverse=True)[:top_k]

        return {
            "ats_score": ats,
            "candidate_skills": candidate_skills,
            "top_jobs": top_jobs,
        }