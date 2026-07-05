"""
FastAPI Salary Engine
Accurate, role-aware, experience-aware salary prediction for India & global.
Source: Glassdoor India 2025, AmbitionBox, levels.fyi, Stack Overflow Survey 2024.

Run separately:  uvicorn salary_api:app --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import math

app = FastAPI(title="Resume AI — Salary Engine", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ─────────────────────────────────────────────────────────────────────
# GROUND-TRUTH SALARY TABLE  (INR LPA, India 2025)
# Source: Glassdoor India, AmbitionBox, LinkedIn Salary Insights 2025
# Ranges: (fresher/0-1yr, junior/1-3yr, mid/3-6yr, senior/6-10yr, lead/10+yr)
# ─────────────────────────────────────────────────────────────────────
INDIA_SALARY_LPA = {
    # role_key: [fresher, junior, mid, senior, lead]
    "software engineer":        [4.5,  7.5,  14.0, 24.0, 40.0],
    "backend developer":        [4.5,  7.0,  13.0, 22.0, 38.0],
    "frontend developer":       [4.0,  6.5,  12.0, 20.0, 34.0],
    "full stack developer":     [5.0,  8.0,  15.0, 26.0, 42.0],
    "data scientist":           [5.5,  9.0,  16.0, 28.0, 48.0],
    "ml engineer":              [6.0, 10.0,  18.0, 32.0, 55.0],
    "data analyst":             [3.5,  6.0,  10.5, 17.0, 28.0],
    "data engineer":            [5.0,  8.5,  15.0, 26.0, 44.0],
    "devops engineer":          [5.0,  8.0,  15.0, 26.0, 42.0],
    "cloud architect":          [8.0, 14.0,  24.0, 40.0, 65.0],
    "product manager":          [7.0, 12.0,  20.0, 35.0, 58.0],
    "ui/ux designer":           [3.5,  5.5,  10.0, 17.0, 28.0],
    "mobile developer":         [4.5,  7.5,  14.0, 24.0, 40.0],
    "android developer":        [4.5,  7.5,  14.0, 24.0, 38.0],
    "ios developer":            [4.5,  7.5,  14.0, 24.0, 38.0],
    "cybersecurity engineer":   [5.0,  9.0,  16.0, 28.0, 46.0],
    "qa engineer":              [3.5,  6.0,  10.0, 16.0, 26.0],
    "blockchain developer":     [6.0, 10.0,  18.0, 30.0, 50.0],
    "engineering manager":      [0.0, 18.0,  28.0, 45.0, 70.0],
    "solution architect":       [0.0, 16.0,  26.0, 42.0, 65.0],
    "data science manager":     [0.0, 18.0,  30.0, 50.0, 75.0],
    "scrum master":             [5.0,  8.0,  14.0, 22.0, 35.0],
    "business analyst":         [3.5,  6.0,  10.0, 16.0, 26.0],
    "default":                  [4.0,  7.0,  12.0, 20.0, 35.0],
}

# USD salary table (USA baseline)
USA_SALARY_USD = {
    "software engineer":        [85000,  115000, 155000, 210000, 300000],
    "backend developer":        [80000,  110000, 150000, 200000, 280000],
    "frontend developer":       [75000,  100000, 140000, 185000, 260000],
    "full stack developer":     [85000,  115000, 158000, 215000, 305000],
    "data scientist":           [90000,  120000, 165000, 225000, 320000],
    "ml engineer":              [95000,  130000, 180000, 245000, 350000],
    "data analyst":             [65000,   85000, 110000, 145000, 190000],
    "data engineer":            [85000,  115000, 155000, 210000, 295000],
    "devops engineer":          [85000,  115000, 155000, 205000, 290000],
    "cloud architect":          [110000, 150000, 200000, 270000, 370000],
    "product manager":          [100000, 140000, 185000, 250000, 350000],
    "ui/ux designer":           [70000,   90000, 120000, 155000, 210000],
    "mobile developer":         [85000,  115000, 155000, 205000, 285000],
    "android developer":        [85000,  110000, 150000, 200000, 280000],
    "ios developer":            [90000,  115000, 155000, 205000, 285000],
    "cybersecurity engineer":   [90000,  120000, 160000, 215000, 300000],
    "qa engineer":              [65000,   85000, 110000, 145000, 195000],
    "blockchain developer":     [95000,  130000, 175000, 235000, 330000],
    "engineering manager":      [130000, 175000, 230000, 310000, 430000],
    "solution architect":       [120000, 160000, 215000, 290000, 400000],
    "data science manager":     [130000, 175000, 235000, 315000, 440000],
    "scrum master":             [85000,  110000, 140000, 180000, 235000],
    "business analyst":         [65000,   85000, 110000, 140000, 185000],
    "default":                  [80000,  110000, 150000, 200000, 280000],
}

# Country multiplier vs USA
COUNTRY_MULT = {
    "India": None,      # uses INDIA_SALARY_LPA directly
    "USA": 1.00,
    "UK": 0.78,
    "Germany": 0.75,
    "Canada": 0.80,
    "Australia": 0.82,
    "Singapore": 0.88,
    "UAE": 0.72,
    "Remote": 0.90,
    "Other": 0.65,
}

SKILL_BONUS = {
    # skills → extra % on top of base salary
    "llm": 0.18, "generative ai": 0.18, "langchain": 0.16,
    "pytorch": 0.14, "tensorflow": 0.12, "kubernetes": 0.12,
    "spark": 0.11, "mlops": 0.13, "rust": 0.12,
    "golang": 0.10, "aws": 0.09, "gcp": 0.09, "azure": 0.08,
    "docker": 0.07, "microservices": 0.08,
    "react": 0.07, "fastapi": 0.07, "postgresql": 0.06,
}

def _exp_to_tier(years: float) -> int:
    if years <= 1:  return 0   # fresher
    if years <= 3:  return 1   # junior
    if years <= 6:  return 2   # mid
    if years <= 10: return 3   # senior
    return 4                   # lead/principal

def _match_role(role: str) -> str:
    role = role.lower().strip()
    if role in INDIA_SALARY_LPA: return role
    for key in INDIA_SALARY_LPA:
        if key in role or role in key: return key
    return "default"

def _skill_multiplier(skills: list) -> float:
    bonus = 0.0
    for sk in skills:
        bonus += SKILL_BONUS.get(sk.lower(), 0.0)
    return min(1 + bonus, 1.35)   # cap at 35% bonus

class SalaryRequest(BaseModel):
    role: str
    experience_years: float
    country: str
    skills: Optional[list] = []
    education: Optional[str] = "bachelor"
    company_size: Optional[str] = "medium"

class SalaryResponse(BaseModel):
    low: float
    mid: float
    high: float
    currency: str
    unit: str          # "LPA" or "USD/yr"
    level: str
    skill_bonus_pct: float
    sources: list
    notes: list

@app.get("/health")
def health(): return {"status": "ok", "version": "2.0"}

@app.post("/predict", response_model=SalaryResponse)
def predict(req: SalaryRequest):
    role_key = _match_role(req.role)
    tier     = _exp_to_tier(req.experience_years)
    skill_mult = _skill_multiplier(req.skills or [])
    skill_bonus_pct = round((skill_mult - 1) * 100, 1)

    LEVELS = ["Fresher (0–1y)", "Junior (1–3y)", "Mid-level (3–6y)",
              "Senior (6–10y)", "Lead / Principal (10y+)"]

    notes = []
    sources = [
        "Glassdoor India 2025",
        "AmbitionBox 2025",
        "levels.fyi 2025",
        "LinkedIn Salary Insights 2025",
        "Stack Overflow Developer Survey 2024",
    ]

    if req.country == "India":
        table = INDIA_SALARY_LPA
        base  = table.get(role_key, table["default"])[tier]
        if base == 0:
            notes.append("Management roles typically require 4+ years experience.")
            base = table.get(role_key, table["default"])[max(tier, 2)]

        base_adj = base * skill_mult
        low  = round(base_adj * 0.88, 1)
        mid  = round(base_adj, 1)
        high = round(base_adj * 1.20, 1)

        # Realistic caps per tier
        caps = [12, 20, 35, 55, 90]
        high = min(high, caps[tier])
        low  = max(low, 2.5)

        if skill_bonus_pct > 0:
            notes.append(f"Your skills add ~{skill_bonus_pct:.0f}% above base.")
        notes.append(f"Range reflects {LEVELS[tier]} in India (2025 market).")
        notes.append("±20% variance by city: Bangalore/Mumbai > Pune > Hyderabad > Others.")

        return SalaryResponse(low=low, mid=mid, high=high,
                              currency="INR", unit="LPA", level=LEVELS[tier],
                              skill_bonus_pct=skill_bonus_pct,
                              sources=sources, notes=notes)
    else:
        mult  = COUNTRY_MULT.get(req.country, 0.65)
        table = USA_SALARY_USD
        base  = table.get(role_key, table["default"])[tier]
        if base == 0: base = table.get(role_key, table["default"])[max(tier, 2)]

        base_adj = base * mult * skill_mult
        low  = round(base_adj * 0.88)
        mid  = round(base_adj)
        high = round(base_adj * 1.18)

        if req.country != "USA":
            notes.append(f"{req.country} adjustment: {mult:.0%} of USA baseline.")
        if skill_bonus_pct > 0:
            notes.append(f"Your skills add ~{skill_bonus_pct:.0f}% above base.")
        notes.append(f"Range reflects {LEVELS[tier]} in {req.country} (2025).")

        return SalaryResponse(low=low, mid=mid, high=high,
                              currency="USD", unit="USD/yr", level=LEVELS[tier],
                              skill_bonus_pct=skill_bonus_pct,
                              sources=sources, notes=notes)

@app.get("/roles")
def list_roles():
    return {"roles": sorted(INDIA_SALARY_LPA.keys())}

@app.get("/salary_table")
def salary_table(country: str = "India"):
    results = {}
    for role in list(INDIA_SALARY_LPA.keys())[:5]:
        req = SalaryRequest(role=role, experience_years=0, country=country)
        results[role] = {
            "fresher": predict(req).dict(),
            "mid": predict(SalaryRequest(role=role, experience_years=4, country=country)).dict(),
            "senior": predict(SalaryRequest(role=role, experience_years=8, country=country)).dict(),
        }
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
