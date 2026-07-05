"""
SQL Database Layer — stores every resume analysis for tracking.
User can re-upload their resume over time and see improvement.
Uses SQLite (zero-config) but works with any SQL DB via SQLAlchemy.
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List


DB_PATH = os.environ.get("RESUME_DB_PATH", "resume_analyses.db")


def init_db() -> None:
    """Create the analyses table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            email TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            overall_quality_score INTEGER,
            authenticity_score INTEGER,
            predicted_salary_usd REAL,
            years_experience REAL,
            skills_count INTEGER,
            missing_skills TEXT,
            top_skill_uplift TEXT,
            red_flags TEXT,
            suggestions TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS skill_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            skill TEXT,
            category TEXT,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(user_name: str, email: str, result: Dict) -> int:
    """Save a full analysis. Returns the analysis ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO analyses (
            user_name, email, overall_quality_score, authenticity_score,
            predicted_salary_usd, years_experience, skills_count,
            missing_skills, top_skill_uplift, red_flags, suggestions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_name or "Anonymous",
        email or "",
        result.get("quality", {}).get("overall_score", 0),
        result.get("authenticity", {}).get("authenticity_score", 0),
        result.get("salary_prediction", {}).get("salary_mid_usd", 0),
        result.get("parsed", {}).get("years_experience", 0),
        len(result.get("skills", {}).get("skills", [])),
        ",".join(result.get("skills", {}).get("missing_critical", [])[:5]),
        result.get("skill_roi", [{}])[0].get("skill", "") if result.get("skill_roi") else "",
        "\n".join(result.get("authenticity", {}).get("red_flags", [])),
        "\n".join(result.get("quality", {}).get("suggestions", [])),
    ))
    analysis_id = c.lastrowid

    # Save individual skills
    for s in result.get("skills", {}).get("skills", []):
        from data.skills_db import SKILLS_DB
        c.execute("""
            INSERT INTO skill_progress (analysis_id, skill, category)
            VALUES (?, ?, ?)
        """, (analysis_id, s, SKILLS_DB.get(s, {}).get("category", "unknown")))

    conn.commit()
    conn.close()
    return analysis_id


def get_user_history(email: str) -> List[Dict]:
    """Get all past analyses for a user (by email)."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM analyses WHERE email = ? ORDER BY analyzed_at DESC",
        (email,)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_progress_summary(email: str) -> Optional[Dict]:
    """Compare latest vs earliest analysis to show improvement."""
    history = get_user_history(email)
    if len(history) < 2:
        return None
    latest = history[0]
    earliest = history[-1]
    return {
        "analyses_count": len(history),
        "quality_delta": latest["overall_quality_score"] - earliest["overall_quality_score"],
        "authenticity_delta": latest["authenticity_score"] - earliest["authenticity_score"],
        "salary_delta_usd": latest["predicted_salary_usd"] - earliest["predicted_salary_usd"],
        "latest": latest,
        "earliest": earliest,
    }


if __name__ == "__main__":
    init_db()
    print(f"✅ DB initialized at {DB_PATH}")
    # Demo: save a fake analysis
    demo = {
        "quality": {"overall_score": 78, "suggestions": ["Add metrics", "Use stronger verbs"]},
        "authenticity": {"authenticity_score": 85, "red_flags": []},
        "salary_prediction": {"salary_mid_usd": 95000},
        "parsed": {"years_experience": 3},
        "skills": {"skills": ["python", "aws"], "missing_critical": ["kubernetes"]},
        "skill_roi": [{"skill": "kubernetes", "salary_uplift_usd": 12000}],
    }
    aid = save_analysis("Demo User", "demo@example.com", demo)
    print(f"✅ Demo analysis saved with ID {aid}")
