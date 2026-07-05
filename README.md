# ✦ Resume AI — Career Intelligence Platform

An AI-powered resume analyzer that gives honest, calibrated feedback: a
quality score, realistic salary ranges, skill-gap analysis for your target
role, and a prioritised action plan.

## Setup (one time)
```bash
pip install -r requirements.txt
```

## Run (two terminals)

**Terminal 1 — Salary Engine (FastAPI)**
```bash
cd final_app
python salary_api.py
```
You'll see: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 — Main App (Streamlit)**
```bash
cd final_app
streamlit run app.py
```
Opens at: http://localhost:8501

> **Note:** The app auto-starts the salary engine in the background if it
> isn't already running. Running it manually in Terminal 1 first just gives
> a faster startup.

## Features
- 📊 **Quality Score** — 6-dimension resume analysis
- 💰 **Calibrated Salary** — Honest 2025 market data for India & global
- 🎯 **Role Gap Analysis** — Exact skills missing for your target role
- 📈 **Career Paths** — 3 projections with salary milestones
- 🛠 **Skill Inventory** — Coverage by category + ROI per skill
- 📋 **Action Plan** — Prioritised checklist
- 👤 **Contact Extraction** — Name, email, phone, GitHub & LinkedIn (shown as clickable links)

## Salary Accuracy (2025 India Market)
| Role | Fresher | Mid (4y) | Senior (8y) |
|------|---------|----------|-------------|
| Software Engineer | ₹4–5.8 LPA | ₹13.2–18 LPA | ₹22.4–30.6 LPA |
| Data Scientist | ₹5.2–7 LPA | ₹15–20.5 LPA | ₹26.2–35.8 LPA |
| ML Engineer | ₹5.6–7.7 LPA | ₹16.9–23 LPA | ₹30–41 LPA |
| DevOps Engineer | ₹4.7–6.4 LPA | ₹14.1–19.2 LPA | ₹24.5–33.4 LPA |
| Product Manager | ₹—* | ₹18.7–25.5 LPA | ₹32.8–44.8 LPA |

*PM roles need 3+ years experience

## Salary Data Sources
- Glassdoor India 2025
- AmbitionBox 2025
- levels.fyi 2025
- Stack Overflow Developer Survey 2024
