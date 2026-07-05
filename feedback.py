"""
Feedback System + Custom Training Data
=======================================
Two ways to improve model accuracy with YOUR data:

1. FEEDBACK LOOP — When the predicted salary is wrong, user can submit
   the actual salary. This builds a labeled dataset over time.

2. CUSTOM TRAINING DATA — User uploads their own CSV with labeled
   salary data. We merge it with public datasets and retrain.

Both approaches are stored in SQLite and the model can be retrained
on demand using `python ml_models.py --with-feedback`.
"""

import os
import io
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = "resume_analyses.db"


def init_feedback_tables():
    """Create tables for feedback and custom training data."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS salary_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            role TEXT,
            country TEXT,
            experience_years REAL,
            skills_count INTEGER,
            predicted_salary_usd REAL,
            actual_salary_usd REAL,
            feedback_note TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS custom_training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            uploaded_by TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            row_count INTEGER
        )
    """)
    conn.commit()
    conn.close()


def submit_salary_feedback(email: str, role: str, country: str,
                           experience_years: float, skills_count: int,
                           predicted_salary_usd: float,
                           actual_salary_usd: float,
                           note: str = "") -> int:
    """Save user's actual salary as a labeled data point."""
    init_feedback_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO salary_feedback
        (email, role, country, experience_years, skills_count,
         predicted_salary_usd, actual_salary_usd, feedback_note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, role, country, experience_years, skills_count,
          predicted_salary_usd, actual_salary_usd, note))
    fid = c.lastrowid
    conn.commit()
    conn.close()
    return fid


def get_feedback_dataframe() -> pd.DataFrame:
    """Get all feedback as a DataFrame for training."""
    init_feedback_tables()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM salary_feedback", conn)
    conn.close()
    return df


def get_feedback_stats() -> Dict:
    """Summary stats on collected feedback."""
    df = get_feedback_dataframe()
    if df.empty:
        return {"count": 0}
    error = df["predicted_salary_usd"] - df["actual_salary_usd"]
    return {
        "count": len(df),
        "mean_error_usd": round(error.mean(), 0),
        "mean_abs_error_usd": round(error.abs().mean(), 0),
        "mape": round((error.abs() / df["actual_salary_usd"]).mean() * 100, 1),
        "countries": df["country"].nunique(),
        "roles": df["role"].nunique(),
        "earliest": df["submitted_at"].min(),
        "latest": df["submitted_at"].max(),
    }


# ─────────────────────────────────────────────────────────────────────
# CUSTOM TRAINING DATA — User uploads their own labeled CSV
# ─────────────────────────────────────────────────────────────────────
EXPECTED_COLUMNS = {
    "job_title": "string",
    "experience_years": "float",
    "country": "string",
    "company_size": "string",
    "skills_count": "int",
    "salary_usd": "float",
    # Optional:
    "experience_level": "string",
    "education_level": "string",
}


def validate_custom_data(df: pd.DataFrame) -> Dict:
    """
    Validate user-uploaded training data.
    Returns: {"valid": bool, "issues": [...], "row_count": int}
    """
    issues = []
    df.columns = [c.lower().strip() for c in df.columns]

    # Required columns
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        issues.append(f"Missing required columns: {missing}")

    # Validate values
    if "salary_usd" in df.columns:
        bad_salary = df[(df["salary_usd"] < 1000) | (df["salary_usd"] > 1_000_000)]
        if len(bad_salary) > 0:
            issues.append(
                f"{len(bad_salary)} rows have unrealistic salary "
                f"(<$1k or >$1M). Review these."
            )
        if df["salary_usd"].isna().sum() > 0:
            issues.append(
                f"{df['salary_usd'].isna().sum()} rows have missing salary."
            )

    if "experience_years" in df.columns:
        bad_exp = df[(df["experience_years"] < 0) | (df["experience_years"] > 50)]
        if len(bad_exp) > 0:
            issues.append(f"{len(bad_exp)} rows have invalid experience years.")

    if "country" in df.columns:
        # Standardize country names (some might be 'usa', 'US', 'United States')
        df["country"] = df["country"].str.strip().str.title()
        bad_countries = df[df["country"].str.len() < 2]
        if len(bad_countries) > 0:
            issues.append(f"{len(bad_countries)} rows have invalid country names.")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "row_count": len(df),
        "columns": list(df.columns),
    }


def save_custom_training_data(df: pd.DataFrame, source_name: str,
                              uploaded_by: str = "user") -> int:
    """
    Save user's custom training data.
    Returns the dataset ID.
    """
    init_feedback_tables()
    validation = validate_custom_data(df)
    if not validation["valid"]:
        raise ValueError(f"Validation failed: {validation['issues']}")

    # Save raw CSV
    os.makedirs("data/custom", exist_ok=True)
    file_path = f"data/custom/{source_name}.csv"
    df.to_csv(file_path, index=False)

    # Track in DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO custom_training_data (source, uploaded_by, row_count)
        VALUES (?, ?, ?)
    """, (source_name, uploaded_by, len(df)))
    did = c.lastrowid
    conn.commit()
    conn.close()
    return did


def load_custom_datasets() -> pd.DataFrame:
    """Load all custom training datasets as one DataFrame."""
    if not os.path.exists("data/custom"):
        return pd.DataFrame()
    frames = []
    for f in os.listdir("data/custom"):
        if f.endswith(".csv"):
            try:
                frames.append(pd.read_csv(f"data/custom/{f}"))
            except Exception as e:
                print(f"⚠️ Failed to load {f}: {e}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def get_all_training_data(uploads_dir: str = None) -> pd.DataFrame:
    """
    Merge REAL public datasets + user feedback + custom data.
    This is what improves model accuracy over time.
    """
    from ml_models import load_real_datasets
    public = load_real_datasets(uploads_dir=uploads_dir)

    # Add feedback as additional labeled data
    feedback = get_feedback_dataframe()
    if not feedback.empty:
        fb_rows = pd.DataFrame({
            "job_title":        feedback["role"],
            "experience_level": "Mid-level",
            "company_size":     "Medium",
            "country":          feedback["country"],
            "salary_usd":       feedback["actual_salary_usd"],
            "skills_count":     feedback["skills_count"],
            "skills_list":      "",
            "education_level":  "Bachelor",
        })
        public = pd.concat([public, fb_rows], ignore_index=True)
        print(f"  + Added {len(fb_rows)} feedback rows")

    # Add custom training data
    custom = load_custom_datasets()
    if not custom.empty:
        # Normalize columns
        if "experience_level" not in custom.columns:
            custom["experience_level"] = "Mid-level"
        if "skills_list" not in custom.columns:
            custom["skills_list"] = ""
        if "education_level" not in custom.columns:
            custom["education_level"] = "Bachelor"
        public = pd.concat([public, custom], ignore_index=True)
        print(f"  + Added {len(custom)} custom rows")

    return public


# ── CLI demo ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_feedback_tables()

    # Demo: submit some feedback
    fid = submit_salary_feedback(
        email="demo@example.com",
        role="data scientist",
        country="India",
        experience_years=4,
        skills_count=15,
        predicted_salary_usd=125000,
        actual_salary_usd=42000,
        note="Model way too high - calibrated range was right",
    )
    print(f"✅ Saved feedback #{fid}")

    stats = get_feedback_stats()
    print(f"\nFeedback stats: {stats}")

    # Demo: load a custom CSV
    sample_csv = """job_title,experience_years,country,company_size,skills_count,salary_usd
data scientist,3,India,Medium,8,1800000
data scientist,5,India,Large,12,3500000
software engineer,2,USA,Medium,6,95000
software engineer,4,USA,Large,10,140000
"""
    df = pd.read_csv(io.StringIO(sample_csv))
    validation = validate_custom_data(df)
    print(f"\nCustom data validation: {validation}")
    if validation["valid"]:
        did = save_custom_training_data(df, source_name="my_research",
                                        uploaded_by="demo")
        print(f"✅ Saved custom dataset #{did} with {validation['row_count']} rows")
        print("\nTo retrain with this data, run:")
        print("  python ml_models.py --with-feedback")
