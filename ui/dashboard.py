import streamlit as st
import pandas as pd
import requests
from pypdf import PdfReader
from io import BytesIO
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Profiled - AI Career Architect",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (THEME: COSMIC INTELLIGENCE) ---
st.markdown("""
    <style>
        /* IMPORT FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
        
        /* GLOBAL STYLES */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #E0E7FF; /* Light Indigo Text */
        }
        
        /* MAIN BACKGROUND (Deep Indigo to Violet) */
        .stApp {
            background: linear-gradient(135deg, #0F0C29 0%, #302B63 50%, #24243E 100%);
            background-attachment: fixed;
        }

        /* HEADERS (Font: Outfit) */
        h1, h2, h3, h4, h5 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px;
            color: #FFFFFF !important;
        }
        
        /* SIDEBAR STYLING */
        section[data-testid="stSidebar"] {
            background-color: rgba(15, 12, 41, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* CARDS: STRUCTURED GLASSMORPHISM */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(139, 92, 246, 0.5); /* Violet glow */
        }

        /* BUTTONS: VIBRANT & CLEAN */
        .stButton > button {
            background: linear-gradient(90deg, #8B5CF6 0%, #D946EF 100%); /* Violet to Pink */
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            letter-spacing: 0.5px;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(217, 70, 239, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #7C3AED 0%, #C026D3 100%);
            box-shadow: 0 6px 20px rgba(217, 70, 239, 0.5);
            transform: scale(1.02);
        }

        /* PROGRESS BAR */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        }

        /* SKILL CHIPS */
        .skill-chip {
            display: inline-block;
            padding: 5px 12px;
            margin: 4px;
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 50px;
            color: #E0E7FF;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        /* FILE UPLOADER CLEANUP */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            border-radius: 12px;
            border: 1px dashed rgba(255, 255, 255, 0.2);
        }
        
        /* Footer Styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: rgba(15, 23, 42, 0.9);
            color: #94A3B8;
            text-align: center;
            padding: 10px;
            font-size: 0.85rem;
            z-index: 100;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .footer a {
            color: #60A5FA;
            text-decoration: none;
            font-weight: 600;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000/match"

# --- HELPER FUNCTIONS ---
def extract_pdf(file):
    reader = PdfReader(file)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

def build_strengths_weaknesses(data):
    skills = data["candidate_skills"]
    ats = data["ats_score"]
    strengths = []
    weaknesses = []

    # Logic (English)
    if ats > 0.75: strengths.append("Strong ATS optimization detected.")
    elif ats > 0.50: strengths.append("Moderate ATS compatibility.")
    else: weaknesses.append("Low ATS score - consider restructuring.")

    if len(skills) >= 10: strengths.append(f"Detected {len(skills)} technical skills.")
    elif len(skills) < 5: weaknesses.append("Skill section appears sparse.")

    top_job = data["top_jobs"][0] if data["top_jobs"] else None
    if top_job:
        if len(top_job["overlap_skills"]) >= 3: strengths.append("Strong alignment with top market roles.")
        if len(top_job["gap_skills"]) > 5: weaknesses.append("Significant skill gaps for target roles.")

    return strengths, weaknesses

# --- SIDEBAR CONFIGURATION (Structured & Clean) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10628/10628946.png", width=70)
    st.markdown("""
        <h2 style='text-align: left; margin-top: -10px; background: -webkit-linear-gradient(0deg, #c084fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            Profiled - AI Career Architect
        </h2>
        <p style='font-size: 0.8rem; color: #94A3B8; margin-top: -15px;'>AI Career Architect v2.0</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 1️⃣ Upload Resume")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    
    st.markdown("### 2️⃣ Select Your Field")
    # --- NEW DOMAIN DROPDOWN ---
    domain_options = [
        "General (Auto-Detect)",
        "Software & IT",
        "Data Science & AI",
        "Core Engineering (Electrical/Mech/Civil)",
        "Business & Management",
        "Finance & Commerce",
        "Creative & Design",
        "Science & Healthcare (Food/Bio)"
    ]
    selected_domain = st.selectbox("Target Industry", domain_options)
    
    st.markdown("### ⚙️ Preferences")
    top_k = st.slider("Number of Job Recommendations", 1, 10, 5)
    
    st.markdown("---")
    analyze_btn = st.button("🚀 Run Analysis")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Designed for India • Powered by GenAI")

# --- MAIN CONTENT AREA ---
if not uploaded:
    # Hero Section for Empty State (Clean & Centered)
    st.markdown("""
    <div style="text-align: center; padding: 80px 0;">
        <h1 style="font-size: 3.8rem; margin-bottom: 15px; background: linear-gradient(90deg, #c084fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Your Future, Engineered.
        </h1>
        <p style="font-size: 1.3rem; color: #CBD5E1; max-width: 700px; margin: 0 auto; line-height: 1.6;">
            Stop applying blindly. Select your field, upload your resume, and let our AI match you with 
            <b>350+ curated roles</b> across India's top industries.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards Grid
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 220px;">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">📊</div>
            <h3 style="color: #E0E7FF;">ATS Parsing</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">See what the bots see. Get a real-time parseability score.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 220px;">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">🧬</div>
            <h3 style="color: #E0E7FF;">Skill DNA</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">Extract and validate your hard skills against market demands.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 220px;">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">🎯</div>
            <h3 style="color: #E0E7FF;">Precision Match</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">Instant mapping to roles in Bangalore, Gurgaon, Mumbai, & more.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # --- ANALYSIS RESULT VIEW ---
    if analyze_btn:
        with st.spinner("⚡ AI is analyzing career vectors..."):
            try:
                cv_text = extract_pdf(BytesIO(uploaded.read()))
                
                # Map dropdown selection to backend keywords
                domain_map = {
                    "General (Auto-Detect)": None,
                    "Software & IT": "Software Web Developer",
                    "Data Science & AI": "Data Scientist Analyst AI",
                    "Core Engineering (Electrical/Mech/Civil)": "Engineer Electrical Mechanical Civil",
                    "Business & Management": "Manager Business Analyst HR",
                    "Finance & Commerce": "Finance Accountant",
                    "Creative & Design": "Designer Graphic UI",
                    "Science & Healthcare (Food/Bio)": "Food Technologist Bio Science"
                }
                
                res = requests.post(API_URL, json={
                    "cv_text": cv_text, 
                    "top_k": top_k,
                    "domain": domain_map.get(selected_domain)
                })
                
                if res.status_code != 200:
                    st.error("❌ Failed to connect to AI Brain. Ensure backend is running.")
                else:
                    data = res.json()
                    strengths, weaknesses = build_strengths_weaknesses(data)
                    
                    # HEADER
                    st.markdown("## 🚀 Analysis Report")
                    
                    # METRICS ROW
                    m1, m2, m3 = st.columns([1.2, 2, 1.2])
                    
                    with m1:
                        # ATS Gauge - Updated Colors (Vibrant)
                        ats_val = int(data['ats_score'] * 100)
                        bar_color = "#34d399" if ats_val > 70 else "#fbbf24" if ats_val > 50 else "#f472b6"
                        
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center; padding: 30px; height: 100%;">
                            <h4 style="margin-bottom: 15px; color: #CBD5E1;">ATS Score</h4>
                            <div style="
                                width: 130px; height: 130px; border-radius: 50%; 
                                background: conic-gradient({bar_color} {ats_val * 3.6}deg, rgba(255,255,255,0.1) 0deg);
                                margin: 0 auto; display: flex; align-items: center; justify-content: center;
                                box-shadow: 0 0 25px {bar_color}40;">
                                <div style="
                                    width: 105px; height: 105px; background: #18162C; 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF;">{ats_val}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with m2:
                        # Insights Card (Clean Lists)
                        st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
                        st.markdown("#### 💡 Career Insights")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"<span style='color: #34d399; font-weight: 600; font-size: 0.9rem;'>✅ STRENGTHS</span>", unsafe_allow_html=True)
                            if strengths:
                                for s in strengths: st.markdown(f"<div style='margin-bottom:6px; font-size:0.85rem; color: #E0E7FF;'>• {s}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='font-size:0.85rem; color: #94A3B8;'>No specific strengths detected.</div>", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"<span style='color: #f472b6; font-weight: 600; font-size: 0.9rem;'>⚠️ GROWTH AREAS</span>", unsafe_allow_html=True)
                            if weaknesses:
                                for w in weaknesses: st.markdown(f"<div style='margin-bottom:6px; font-size:0.85rem; color: #E0E7FF;'>• {w}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='font-size:0.85rem; color: #94A3B8;'>No major weaknesses detected.</div>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with m3:
                        # Key Stats Card
                        st.markdown(f"""
                        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <div style="text-align: center; margin-bottom: 15px;">
                                <div style="font-size: 2.8rem; font-weight: 800; color: #A78BFA;">{len(data['candidate_skills'])}</div>
                                <div style="color: #94A3B8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Skills Found</div>
                            </div>
                            <div style="width: 60%; height: 1px; background: rgba(255,255,255,0.1); margin: 10px 0;"></div>
                            <div style="text-align: center; margin-top: 10px;">
                                <div style="font-size: 2.8rem; font-weight: 800; color: #60A5FA;">{len(data['top_jobs'])}</div>
                                <div style="color: #94A3B8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Matches</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # VERIFIED SKILLS SECTION
                    st.markdown("#### 🧬 Verified Skills Profile")
                    skills_html = "".join([f'<span class="skill-chip">{s}</span>' for s in data["candidate_skills"]])
                    st.markdown(f'<div class="glass-card">{skills_html}</div>', unsafe_allow_html=True)

                    # JOB RECOMMENDATIONS SECTION
                    st.markdown(f"#### 🎯 Top Matches: {selected_domain}")
                    
                    if not data["top_jobs"]:
                        st.info("No matches found. Try updating the database or selecting a different domain.")
                    
                    for job in data["top_jobs"]:
                        score = int(job['fit_score'] * 100)
                        bar_color = "bg-green-500" if score > 70 else "bg-yellow-500"
                        
                        # Generate chips for overlap skills
                        overlap_html = "".join([f'<span style="color:#10B981; background:rgba(16, 185, 129, 0.1); padding:2px 8px; border-radius:12px; font-size:0.75rem; margin-right:4px;">{s}</span>' for s in job['overlap_skills'][:5]])
                        
                        # Generate chips for gap skills
                        gap_html = "".join([f'<span style="color:#EF4444; background:rgba(239, 68, 68, 0.1); padding:2px 8px; border-radius:12px; font-size:0.75rem; margin-right:4px;">{s}</span>' for s in job['gap_skills'][:5]])

                        with st.container():
                            st.markdown(f"""
                            <div class="glass-card">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div>
                                        <h3 style="margin: 0; color: #3B82F6;">{job['title']}</h3>
                                        <p style="margin: 4px 0; font-weight: 600; color: #E2E8F0;">{job['company']}</p>
                                        <p style="margin: 0; font-size: 0.9rem; color: #94A3B8;">📍 {job['location']}</p>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 1.5rem; font-weight: 800; color: #10B981;">{score}% Match</div>
                                        <a href="{job.get('url', '#')}" target="_blank" style="text-decoration: none; color: #3B82F6; font-size: 0.9rem;">Apply Now ↗</a>
                                    </div>
                                </div>
                                <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                    <div>
                                        <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;">✅ YOUR MATCHING SKILLS</p>
                                        <div>{overlap_html if overlap_html else '<span style="color:#64748B; font-size:0.8rem;">None detected</span>'}</div>
                                    </div>
                                    <div>
                                        <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;">⚠️ MISSING SKILLS</p>
                                        <div>{gap_html if gap_html else '<span style="color:#64748B; font-size:0.8rem;">None missing</span>'}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        Made with ❤️ by <a href="https://www.linkedin.com/in/shivashish-prusty/" target="_blank">Shivashish</a>
    </div>
""", unsafe_allow_html=True)