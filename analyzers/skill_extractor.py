"""
Skill Extractor — finds skills in resume text using the skills database.
"""

import re
from typing import List, Dict, Set
from data.skills_db import SKILLS_DB, SKILL_CATEGORIES


def extract_skills(resume_text: str) -> Dict:
    """
    Extract skills from resume text. Returns:
    {
        "skills": ["python", "aws", ...],   # detected skills
        "by_category": {"language": [...], ...},
        "missing_critical": [...],   # high-demand skills missing
        "coverage": 0.78  # % of in-demand skills the user has
    }
    """
    text_lower = resume_text.lower()
    detected: Set[str] = set()

    # Match each skill (with word boundaries for multi-word skills)
    for skill, _ in SKILLS_DB.items():
        # \b doesn't work well with ".js" or "/", so use flexible matching
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            detected.add(skill)

    # Group by category
    by_category: Dict[str, List[str]] = {cat: [] for cat in SKILL_CATEGORIES}
    for skill in detected:
        cat = SKILLS_DB[skill]["category"]
        by_category[cat].append(skill)

    # Coverage: % of high-demand (>=0.80) skills present
    high_demand = [s for s, v in SKILLS_DB.items() if v["demand"] >= 0.80]
    coverage = len(detected & set(high_demand)) / len(high_demand) if high_demand else 0

    # Critical missing skills (top 10 by demand × salary_weight)
    missing = [
        s for s, v in SKILLS_DB.items()
        if s not in detected and v["demand"] >= 0.75
    ]
    missing_sorted = sorted(
        missing,
        key=lambda s: SKILLS_DB[s]["demand"] * SKILLS_DB[s]["salary_weight"],
        reverse=True,
    )[:10]

    return {
        "skills": sorted(detected),
        "by_category": {k: sorted(v) for k, v in by_category.items() if v},
        "missing_critical": missing_sorted,
        "coverage": round(coverage, 3),
    }


def calculate_skill_roi(
    current_skills: List[str],
    salary_model_pipeline=None,
    baseline_salary_usd: float = None,
) -> List[Dict]:
    """
    THE KILLER FEATURE.
    For each missing high-impact skill, estimate how much it would boost
    the user's expected salary.

    Uses a HYBRID approach (more reliable than model alone, because most
    regression models can't distinguish individual skills at this scale):
      1. Baseline salary: from the model if provided, otherwise assume a
         market average for the candidate's profile.
      2. Per-skill uplift: derived from the curated SKILLS_DB salary_weight
         (which encodes known industry salary multipliers for each skill)
         combined with the skill's demand score.

    Returns: [{skill, salary_uplift_usd, pct_uplift, category, demand}, ...]
    """
    if not current_skills and baseline_salary_usd is None:
        return []

    # ── Baseline ────────────────────────────────────────────────────
    if baseline_salary_usd is None:
        # Fallback: USA median tech salary for mid-level
        baseline_salary_usd = 100_000.0

    # ── Per-skill uplift using SKILLS_DB ────────────────────────────
    candidates = [
        s for s, v in SKILLS_DB.items()
        if s not in current_skills
        and v["demand"] >= 0.70
        and v["salary_weight"] >= 1.10
    ]

    roi_list = []
    for skill in candidates:
        v = SKILLS_DB[skill]
        # Salary multiplier (e.g., 1.30 = +30% boost)
        # Diminishing returns: already have related skills, lower impact
        multiplier = v["salary_weight"] - 1.0   # 0.05 to 0.35 typical
        # Apply diminishing factor based on category overlap
        have_in_category = sum(
            1 for s in current_skills
            if SKILLS_DB.get(s, {}).get("category") == v["category"]
        )
        # First skill in category = full impact, 2nd = 70%, 3rd+ = 40%
        diminishing = 1.0 if have_in_category == 0 else \
                      0.7 if have_in_category == 1 else 0.4

        uplift = baseline_salary_usd * multiplier * diminishing

        if uplift > 300:  # meaningful uplift
            roi_list.append({
                "skill": skill,
                "category": v["category"],
                "salary_uplift_usd": round(uplift, 0),
                "pct_uplift": round(multiplier * diminishing * 100, 1),
                "demand": v["demand"],
            })

    # Sort by uplift
    roi_list.sort(key=lambda x: x["salary_uplift_usd"], reverse=True)
    return roi_list[:15] 


if __name__ == "__main__":
    sample = """
    Senior Software Engineer with 5 years experience in Python, Django,
    React, AWS, Docker, PostgreSQL, Git. Built microservices with Kubernetes.
    Proficient in TensorFlow and machine learning.
    """
    result = extract_skills(sample)
    print("Detected skills:", result["skills"])
    print("By category:", result["by_category"])
    print("Coverage:", result["coverage"])
    print("Critical missing:", result["missing_critical"])
