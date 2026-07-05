"""
Role Gap Analyzer
=================
Given a target role and the user's current skills, identify:
- Required skills the user HAS (✓)
- Required skills the user is MISSING (✗)
- Preferred skills the user HAS (+)
- Preferred skills the user is MISSING (○)
- Overall match score

This is what the user asked for: "recommend skills needed on the
basis of job roles, in the same format as the graph is shown".
"""

from typing import Dict, List
from data.role_profiles import ROLE_PROFILES, get_profile
from data.skills_db import SKILLS_DB


def analyze_role_gap(
    target_role: str,
    user_skills: List[str],
) -> Dict:
    """
    Compare user's skills vs target role requirements.

    Returns:
    {
        "target_role": "data scientist",
        "match_score": 67,                 # 0-100, % of required skills present
        "required_have": [...],            # skills user has
        "required_missing": [...],         # CRITICAL missing
        "preferred_have": [...],
        "preferred_missing": [...],        # nice-to-have missing
        "soft_skill_gaps": [...],
        "recommendations": [               # ordered by priority
            {"skill": "pytorch", "priority": "critical",
             "category": "ml_ai", "reason": "Required for most data scientist roles"},
            ...
        ],
        "category": "technical",
        "description": "...",
    }
    """
    profile = get_profile(target_role)
    if not profile:
        return {
            "target_role": target_role,
            "error": f"Unknown role: '{target_role}'. Available: {list(ROLE_PROFILES.keys())}",
        }

    # Normalize user skills to lowercase for comparison
    user_skills_set = set(s.lower().strip() for s in user_skills)

    # Required
    req_have = [s for s in profile["required_skills"] if s in user_skills_set]
    req_missing = [s for s in profile["required_skills"] if s not in user_skills_set]

    # Preferred
    pref_have = [s for s in profile["preferred_skills"] if s in user_skills_set]
    pref_missing = [s for s in profile["preferred_skills"] if s not in user_skills_set]

    # Soft skills (no DB match — just informational)
    soft_gaps = [s for s in profile.get("soft_skills", []) if s not in user_skills_set]

    # Match score: required = 70%, preferred = 30%
    if profile["required_skills"]:
        req_pct = len(req_have) / len(profile["required_skills"])
    else:
        req_pct = 1.0
    if profile["preferred_skills"]:
        pref_pct = len(pref_have) / len(profile["preferred_skills"])
    else:
        pref_pct = 1.0
    match_score = round((req_pct * 0.7 + pref_pct * 0.3) * 100, 0)

    # Build prioritized recommendations
    recommendations = []
    for skill in req_missing:
        info = SKILLS_DB.get(skill, {})
        recommendations.append({
            "skill": skill,
            "priority": "critical",
            "category": info.get("category", "general"),
            "reason": f"Required for {target_role} — most job postings list this",
        })
    for skill in pref_missing:
        info = SKILLS_DB.get(skill, {})
        recommendations.append({
            "skill": skill,
            "priority": "preferred",
            "category": info.get("category", "general"),
            "reason": f"Preferred for {target_role} — strengthens your profile",
        })

    # Sort by priority then by salary_weight (descending) so the most
    # impactful skills appear first
    priority_order = {"critical": 0, "preferred": 1}
    recommendations.sort(key=lambda r: (
        priority_order[r["priority"]],
        -SKILLS_DB.get(r["skill"], {}).get("salary_weight", 1.0),
    ))

    return {
        "target_role": target_role,
        "category": profile["category"],
        "description": profile["description"],
        "match_score": match_score,
        "required_have": req_have,
        "required_missing": req_missing,
        "preferred_have": pref_have,
        "preferred_missing": pref_missing,
        "soft_skill_gaps": soft_gaps,
        "recommendations": recommendations,
        "total_required": len(profile["required_skills"]),
        "total_preferred": len(profile["preferred_skills"]),
    }


def get_all_roles() -> List[str]:
    """Return all available role names."""
    return list(ROLE_PROFILES.keys())


if __name__ == "__main__":
    # Test with Priya (ML Engineer) targeting "data scientist"
    user_skills = [
        "python", "pytorch", "tensorflow", "scikit-learn", "nlp",
        "deep learning", "kubernetes", "docker", "aws", "spark",
        "airflow", "postgresql", "redis", "fastapi", "git", "linux",
        "ci/cd", "mlops", "microservices", "rest api", "machine learning",
    ]
    print("TEST: Priya targeting 'data scientist' role")
    print("=" * 70)
    gap = analyze_role_gap("data scientist", user_skills)
    print(f"Match score: {gap['match_score']}/100")
    print(f"Required have ({len(gap['required_have'])}): {gap['required_have']}")
    print(f"Required MISSING ({len(gap['required_missing'])}): {gap['required_missing']}")
    print(f"Preferred have ({len(gap['preferred_have'])}): {gap['preferred_have']}")
    print(f"Preferred MISSING ({len(gap['preferred_missing'])}): {gap['preferred_missing'][:5]}")
    print(f"\nTop recommendations:")
    for r in gap["recommendations"][:5]:
        print(f"  [{r['priority'].upper():<9}] {r['skill']:<20} — {r['reason']}")
