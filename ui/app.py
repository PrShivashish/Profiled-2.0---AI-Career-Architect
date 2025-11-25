from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from io import BytesIO
import requests

app = Flask(__name__)

API_URL = "http://localhost:8000/match"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    """Extract text from uploaded PDF"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        pdf_bytes = BytesIO(file.read())
        reader = PdfReader(pdf_bytes)
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n".join(pages)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """Forward analysis request to backend API"""
    try:
        data = request.json
        cv_text = data.get('cv_text', '')
        top_k = data.get('top_k', 5)
        
        if not cv_text.strip():
            return jsonify({'error': 'CV text is empty'}), 400
        
        # Call your existing backend API
        response = requests.post(API_URL, json={
            'cv_text': cv_text,
            'top_k': top_k
        })
        
        result = response.json()
        
        # Build strengths and weaknesses (ENGLISH TRANSLATION)
        strengths, weaknesses = build_strengths_weaknesses(result)
        result['strengths'] = strengths
        result['weaknesses'] = weaknesses
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def build_strengths_weaknesses(data):
    """Build strengths and weaknesses analysis"""
    skills = data.get("candidate_skills", [])
    ats = data.get("ats_score", 0)
    
    strengths = []
    weaknesses = []
    
    # ATS-based analysis (ENGLISH)
    if ats > 0.75:
        strengths.append("CV is very ATS-friendly (good structure & keywords).")
    elif ats > 0.50:
        strengths.append("CV is moderately ATS-friendly.")
    else:
        weaknesses.append("Low ATS score — missing important sections/keywords.")
    
    # Skill-based analysis (ENGLISH)
    if len(skills) >= 10:
        strengths.append("Has many technical skills.")
    elif len(skills) >= 5:
        strengths.append("Has an adequate amount of skills.")
    else:
        weaknesses.append("Very few skills detected — add more to the SKILLS section.")
    
    # Job match analysis (ENGLISH)
    top_jobs = data.get("top_jobs", [])
    if top_jobs:
        top_job = top_jobs[0]
        overlap = top_job.get("overlap_skills", [])
        gap = top_job.get("gap_skills", [])
        
        if len(overlap) >= 4:
            strengths.append(f"Great match for **{top_job['title']}** (high skill overlap).")
        elif len(overlap) >= 2:
            strengths.append("Has relevant skills for the recommended role.")
        else:
            weaknesses.append("Skill match for this role is still low.")
        
        if len(gap) >= 4:
            weaknesses.append("Large skill gap for the main target job.")
        elif len(gap) > 0:
            weaknesses.append("Specific skills are missing.")
    
    return strengths, weaknesses

if __name__ == '__main__':
    app.run(debug=True, port=5000)