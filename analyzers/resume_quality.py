"""
Resume Quality Analyzer — checks sections, action verbs, quantification,
length, fluff phrases. Returns a 0-100 quality score with sub-scores.
"""

import re
from typing import Dict
from data.skills_db import STRONG_VERBS, WEAK_PHRASES


def analyze_quality(parsed_resume: Dict) -> Dict:
    """
    Analyze resume quality across 6 dimensions.
    Returns: {
        "overall_score": 78,
        "subscores": {
            "sections": 90, "action_verbs": 60, "quantification": 40,
            "length": 80, "fluff": 100, "consistency": 85,
        },
        "issues": [...],          # specific problems
        "suggestions": [...]      # actionable improvements
    }
    """
    text = parsed_resume["raw_text"]
    text_lower = text.lower()
    sections = parsed_resume["sections"]
    subs = {}
    issues = []
    suggestions = []

    # ── 1. SECTIONS ──────────────────────────────────────────────────
    required = ["skills", "experience", "education"]
    nice_to_have = ["projects", "summary", "certifications", "achievements"]
    has_required = sum(1 for r in required if r in sections)
    has_nice     = sum(1 for n in nice_to_have if n in sections)
    sections_score = (has_required / len(required)) * 80 + (has_nice / len(nice_to_have)) * 20
    subs["sections"] = round(sections_score, 0)

    for r in required:
        if r not in sections:
            issues.append(f"Missing required section: '{r}'")
            suggestions.append(f"Add a '{r.title()}' section — recruiters expect it.")

    # ── 2. ACTION VERBS ──────────────────────────────────────────────
    word_count = parsed_resume["word_count"]
    bullet_lines = [l for l in text.split("\n") if l.strip().startswith(("•", "-", "*", "·"))]
    bullets_text = " ".join(bullet_lines).lower()
    verb_hits = sum(1 for v in STRONG_VERBS if v in bullets_text)
    # Score: >=5 strong verbs = full marks
    verbs_score = min(100, (verb_hits / 5) * 100) if bullet_lines else 50
    subs["action_verbs"] = round(verbs_score, 0)
    if verb_hits < 3:
        issues.append(f"Only {verb_hits} strong action verbs found in bullets")
        suggestions.append(f"Use stronger verbs: 'built', 'led', 'optimized', 'scaled' instead of 'worked on', 'helped with'.")

    # ── 3. QUANTIFICATION ────────────────────────────────────────────
    # % of bullets that contain a number (%, $, X years, etc.)
    quantified = 0
    for b in bullet_lines:
        if re.search(r"\b\d+(?:[,.]\d+)*(?:\s*%|\s*k|\s*m|\s*x|\s+users?|\s+customers?|\s+requests?|\s*ms|\s*x|\s*\+)?\b", b, re.IGNORECASE):
            quantified += 1
        elif re.search(r"\$\d", b):  # dollar amounts
            quantified += 1
    quant_pct = (quantified / len(bullet_lines) * 100) if bullet_lines else 0
    subs["quantification"] = round(min(100, quant_pct * 1.5), 0)  # 67%+ = full marks
    if quant_pct < 40:
        issues.append(f"Only {quant_pct:.0f}% of your bullets have numbers (top resumes: 60%+)")
        suggestions.append("Add metrics: 'reduced load time by 40%', 'served 10k+ users', '$2M cost savings'.")

    # ── 4. LENGTH ────────────────────────────────────────────────────
    if word_count < 200:
        length_score = 30
        issues.append(f"Resume is too short ({word_count} words)")
        suggestions.append("Aim for 400-800 words. You're underselling yourself.")
    elif word_count > 1200:
        length_score = 50
        issues.append(f"Resume is too long ({word_count} words)")
        suggestions.append("Trim to 400-800 words. Recruiters skim in 6-10 seconds.")
    elif 400 <= word_count <= 800:
        length_score = 100
    else:
        length_score = 80
    subs["length"] = length_score

    # ── 5. FLUFF DETECTION ──────────────────────────────────────────
    fluff_hits = [p for p in WEAK_PHRASES if p in text_lower]
    fluff_score = max(0, 100 - len(fluff_hits) * 15)
    subs["fluff"] = round(fluff_score, 0)
    if fluff_hits:
        issues.append(f"Fluff phrases detected: {', '.join(fluff_hits[:3])}")
        suggestions.append("Remove filler like 'passionate about', 'team player'. Show, don't tell.")

    # ── 6. CONSISTENCY ───────────────────────────────────────────────
    consistency_score = 100
    consistency_issues = []
    # Check for contradictions between skill count and listed skills
    skills_section = sections.get("skills", "") + sections.get("technical skills", "")
    skill_words = [w for w in re.split(r"[,\n;|]", skills_section) if w.strip()]
    n_skills = len(skill_words)
    if n_skills > 0 and n_skills < 3:
        consistency_score -= 20
        consistency_issues.append(f"Skills section lists only {n_skills} skills")
    # Check for very long employment gaps (rough)
    if parsed_resume["years_experience"] > 0 and word_count > 0:
        words_per_year = word_count / max(1, parsed_resume["years_experience"])
        if words_per_year < 30 and parsed_resume["years_experience"] > 5:
            consistency_score -= 10
            consistency_issues.append("Resume seems sparse for claimed experience level")

    subs["consistency"] = round(consistency_score, 0)
    issues.extend(consistency_issues)

    # ── OVERALL ──────────────────────────────────────────────────────
    overall = round(sum(subs.values()) / len(subs), 0)

    return {
        "overall_score": overall,
        "subscores": subs,
        "issues": issues,
        "suggestions": suggestions,
        "stats": {
            "word_count": word_count,
            "bullet_count": len(bullet_lines),
            "strong_verbs": verb_hits,
            "quantified_pct": round(quant_pct, 1),
            "fluff_count": len(fluff_hits),
            "skills_count": n_skills,
        },
    }


if __name__ == "__main__":
    sample = """
    John Doe
    john@example.com | linkedin.com/in/johndoe

    SUMMARY
    Passionate about technology and a hardworking team player.

    EXPERIENCE
    Software Engineer, ABC Corp (2020 - 2023)
    • Worked on backend services
    • Helped with API development
    • Synergy across teams

    SKILLS
    Python, Django, React

    EDUCATION
    B.Tech, IIT Delhi (2016 - 2020)
    """
    parsed = {
        "raw_text": sample,
        "sections": {
            "summary": "Passionate about technology and a hardworking team player.",
            "experience": sample,
            "skills": "Python, Django, React",
            "education": "B.Tech, IIT Delhi",
        },
        "word_count": len(sample.split()),
        "years_experience": 3,
    }
    result = analyze_quality(parsed)
    print(f"Overall: {result['overall_score']}/100")
    print(f"Subscores: {result['subscores']}")
    print(f"Issues: {result['issues']}")
    print(f"Suggestions: {result['suggestions']}")
