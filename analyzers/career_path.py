"""
Career Path Simulator — based on user's current profile, suggest 3
realistic paths with salary projections. Novel feature.
"""

from typing import Dict, List
from data.skills_db import SKILLS_DB


# Career trajectory templates — common paths in tech
CAREER_PATHS = {
    "data scientist": {
        "next_roles": [
            {"role": "Senior Data Scientist", "years": 2, "salary_mult": 1.30},
            {"role": "ML Engineer", "years": 3, "salary_mult": 1.35},
            {"role": "Data Science Manager", "years": 5, "salary_mult": 1.55},
            {"role": "Principal Data Scientist", "years": 7, "salary_mult": 1.80},
            {"role": "Director of Data Science", "years": 10, "salary_mult": 2.20},
        ],
        "skills_to_add": ["mlops", "kubernetes", "spark", "langchain"],
    },
    "software engineer": {
        "next_roles": [
            {"role": "Senior Software Engineer", "years": 2, "salary_mult": 1.30},
            {"role": "Tech Lead", "years": 4, "salary_mult": 1.45},
            {"role": "Engineering Manager", "years": 6, "salary_mult": 1.65},
            {"role": "Principal Engineer", "years": 8, "salary_mult": 1.90},
            {"role": "CTO", "years": 12, "salary_mult": 2.50},
        ],
        "skills_to_add": ["kubernetes", "microservices", "aws", "terraform"],
    },
    "ml engineer": {
        "next_roles": [
            {"role": "Senior ML Engineer", "years": 2, "salary_mult": 1.30},
            {"role": "ML Architect", "years": 4, "salary_mult": 1.55},
            {"role": "AI Engineering Manager", "years": 6, "salary_mult": 1.75},
            {"role": "Head of AI", "years": 10, "salary_mult": 2.30},
        ],
        "skills_to_add": ["kubernetes", "mlops", "transformers", "rag"],
    },
    "data analyst": {
        "next_roles": [
            {"role": "Senior Data Analyst", "years": 2, "salary_mult": 1.25},
            {"role": "Data Scientist", "years": 3, "salary_mult": 1.40},
            {"role": "Analytics Manager", "years": 5, "salary_mult": 1.55},
        ],
        "skills_to_add": ["python", "machine learning", "sql", "spark"],
    },
    "backend developer": {
        "next_roles": [
            {"role": "Senior Backend Engineer", "years": 2, "salary_mult": 1.30},
            {"role": "Tech Lead", "years": 4, "salary_mult": 1.50},
            {"role": "Engineering Manager", "years": 6, "salary_mult": 1.70},
        ],
        "skills_to_add": ["kubernetes", "aws", "microservices", "graphql"],
    },
    "frontend developer": {
        "next_roles": [
            {"role": "Senior Frontend Engineer", "years": 2, "salary_mult": 1.30},
            {"role": "Full Stack Engineer", "years": 3, "salary_mult": 1.40},
            {"role": "Engineering Manager", "years": 6, "salary_mult": 1.65},
        ],
        "skills_to_add": ["typescript", "next.js", "react", "graphql"],
    },
    "devops engineer": {
        "next_roles": [
            {"role": "Senior DevOps Engineer", "years": 2, "salary_mult": 1.30},
            {"role": "SRE Lead", "years": 4, "salary_mult": 1.50},
            {"role": "Platform Engineering Manager", "years": 6, "salary_mult": 1.75},
        ],
        "skills_to_add": ["kubernetes", "terraform", "ansible", "helm"],
    },
}


def suggest_paths(current_role: str, current_skills: List[str],
                  current_salary_usd: float) -> List[Dict]:
    """
    Given a user's current role, return 3 plausible career paths.
    Each path shows 2-3 progression steps with salary projections.
    """
    role_key = (current_role or "").lower().strip()
    path = CAREER_PATHS.get(role_key, CAREER_PATHS["software engineer"])

    # Pick 3 progression scenarios
    next_roles = path["next_roles"]

    paths = []
    # Path 1: Individual contributor (deep specialization)
    if len(next_roles) >= 1:
        ic_target = next_roles[0]
        paths.append({
            "type": "Individual Contributor",
            "title": f"Become a {ic_target['role']}",
            "timeline_years": ic_target["years"],
            "salary_now": current_salary_usd,
            "salary_then": round(current_salary_usd * ic_target["salary_mult"], 0),
            "skills_needed": [s for s in path["skills_to_add"][:2]
                              if s not in current_skills],
        })

    # Path 2: T-shaped expert (technical + breadth)
    if len(next_roles) >= 2:
        expert_target = next_roles[min(2, len(next_roles)-1)]
        paths.append({
            "type": "Technical Expert",
            "title": f"Grow into {expert_target['role']}",
            "timeline_years": expert_target["years"],
            "salary_now": current_salary_usd,
            "salary_then": round(current_salary_usd * expert_target["salary_mult"], 0),
            "skills_needed": [s for s in path["skills_to_add"]
                              if s not in current_skills][:3],
        })

    # Path 3: Management
    mgmt_idx = next((i for i, r in enumerate(next_roles)
                     if "manager" in r["role"].lower() or "lead" in r["role"].lower()
                     or "head" in r["role"].lower() or "director" in r["role"].lower()
                     or "cto" in r["role"].lower()), len(next_roles) - 1)
    mgmt_target = next_roles[mgmt_idx]
    paths.append({
        "type": "Management Track",
        "title": f"Move into {mgmt_target['role']}",
        "timeline_years": mgmt_target["years"],
        "salary_now": current_salary_usd,
        "salary_then": round(current_salary_usd * mgmt_target["salary_mult"], 0),
        "skills_needed": ["leadership", "mentoring", "scrum"],  # soft skills
    })

    return paths


if __name__ == "__main__":
    paths = suggest_paths("data scientist", ["python", "sql"], 100_000)
    for p in paths:
        print(f"\n{p['type']}: {p['title']}")
        print(f"  Timeline: {p['timeline_years']} years")
        print(f"  Salary: ${p['salary_now']:,.0f} → ${p['salary_then']:,.0f}")
        print(f"  Skills needed: {p['skills_needed']}")
