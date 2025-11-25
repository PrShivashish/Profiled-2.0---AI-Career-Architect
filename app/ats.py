import os

def load_skills_vocab():
    """Load the universal skills list to use for scoring."""
    # Assuming the file is at project_root/data/skills_dict.txt
    # and this file is at project_root/app/ats.py
    path = os.path.join(os.path.dirname(__file__), "..", "data", "skills_dict.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(s.strip().lower() for s in f if s.strip())
    except Exception:
        return set()

# Load once at module level
SKILLS_DB = load_skills_vocab()

def ats_score(text: str) -> float:
    t = text.lower()
    score = 0.0

    # 1. Length Check (Ideal: 1000–3000 chars)
    length = len(t)
    if length > 2800: score += 0.20
    elif length > 1800: score += 0.20
    elif length > 900: score += 0.15
    elif length > 500: score += 0.10
    else: score += 0.05

    # 2. Essential Sections
    sections = ["experience", "education", "skills", "projects", "certifications", "summary", "objective"]
    hits = sum(1 for s in sections if s in t)
    score += min(0.20, hits * 0.05)

    # 3. Action Verbs (Leadership & Initiative)
    action_verbs = [
        "led", "managed", "developed", "designed", "implemented", "created",
        "analyzed", "optimized", "achieved", "improved", "collaborated",
        "coordinated", "established", "negotiated", "supervised", "trained"
    ]
    verb_hits = sum(1 for v in action_verbs if v in t)
    if verb_hits > 10: score += 0.15
    elif verb_hits > 5: score += 0.10
    elif verb_hits > 2: score += 0.05

    # 4. Universal Skill Density (The Fix)
    # Instead of hardcoded tech words, we check against the full skills database
    skill_hits = 0
    for skill in SKILLS_DB:
        # Word boundary check is expensive, simple substring check is faster for scoring
        if skill in t:
            skill_hits += 1
            
    # Adjust thresholds based on finding ANY relevant skills
    if skill_hits > 15: score += 0.25
    elif skill_hits > 10: score += 0.20
    elif skill_hits > 5: score += 0.15
    elif skill_hits > 2: score += 0.05

    # 5. Formatting (Bullet Points)
    bullets = t.count("•") + t.count("- ") + t.count("* ") + t.count("➢")
    if bullets > 15: score += 0.10
    elif bullets > 5: score += 0.05

    # 6. Contact Info Check (Bonus)
    if "@" in t and any(x in t for x in [".com", ".in", ".org"]):
        score += 0.05
    if any(c.isdigit() for c in t): # Crude phone check
        score += 0.05

    # 7. Penalties (Formatting Noise)
    noise = t.count("====") + t.count("****") + t.count("____")
    if noise > 5: score -= 0.10

    return max(0.0, min(1.0, score))