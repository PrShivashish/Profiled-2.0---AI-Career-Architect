from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from .main import JobRecommender

app = FastAPI(title="Profiled API")
reco = JobRecommender()

class MatchRequest(BaseModel):
    cv_text: str
    top_k: int = 5
    domain: Optional[str] = None  # New optional field to capture user domain choice

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/match")
def match(req: MatchRequest):
    # Pass the domain to the compute engine in main.py
    return reco.compute(req.cv_text, top_k=req.top_k, domain=req.domain)