"""
ML Models — train salary prediction on REAL datasets only.
Avoids the data leakage bug. Uses proper regression metrics.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from data.skills_db import SKILLS_DB


MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)


# ── Currency conversion table (USD-equivalent) ─────────────────────
USD_RATES = {
    "USD": 1.0, "EUR": 1.08, "GBP": 1.27, "INR": 0.012, "CAD": 0.74,
    "AUD": 0.66, "SGD": 0.74, "JPY": 0.0067, "CHF": 1.14, "HKD": 0.128,
    "CNY": 0.138, "ILS": 0.27, "MXN": 0.058, "BRL": 0.20, "ZAR": 0.054,
    "PLN": 0.25, "SEK": 0.095, "NOK": 0.094, "DKK": 0.145, "NZD": 0.61,
}


def _to_usd(row):
    rate = USD_RATES.get(row.get("salary_currency", "USD"), 1.0)
    return float(row["salary"]) * rate


def _find_uploads_dir():
    """Auto-detect where the CSV datasets live.

    Tries multiple common locations so the same code works on
    Windows, Linux, and different project layouts.
    """
    import os
    candidates = [
        os.environ.get("RESUME_UPLOADS_DIR"),
        os.path.join(os.getcwd(), "uploads"),
        os.path.join(os.getcwd(), "..", "uploads"),
        os.path.join(os.getcwd(), "..", "..", "uploads"),
        "/home/user/uploads",
    ]

    expected = ["Data Science Salary 2021 to 2023.csv"]
    for path in candidates:
        if not path or not os.path.isdir(path):
            continue
        if any(os.path.isfile(os.path.join(path, f)) for f in expected):
            return path
    # Fallback: first existing directory
    for path in candidates:
        if path and os.path.isdir(path):
            return path
    return os.getcwd()


def load_real_datasets(uploads_dir: str = None) -> pd.DataFrame:
    """
    Load and merge the REAL datasets only — skips ds1_global synthetic data.
    Returns a unified dataframe with columns:
    job_title, experience_years, skills_count, company_size, country,
    salary_usd, education_level, experience_level, skills_list

    If uploads_dir is None, auto-detects the location.
    """
    if uploads_dir is None:
        uploads_dir = _find_uploads_dir()
        print(f"  Auto-detected uploads dir: {uploads_dir}")

    frames = []

    # 1) Data Science Salary 2021 to 2023 (global, ~3.7k rows)
    try:
        df = pd.read_csv(f"{uploads_dir}/Data Science Salary 2021 to 2023.csv")
        df["skills_count"] = 5
        df["skills_list"] = ""
        df["education_level"] = "Bachelor"
        df["experience_level"] = df["experience_level"].map({
            "EN": "Junior", "MI": "Mid-level", "SE": "Senior", "EX": "Expert",
        }).fillna("Mid-level")
        df["country"] = df["company_location"]
        df["salary_usd"] = df["salary_in_usd"]
        frames.append(df[["job_title", "experience_level", "company_size",
                          "country", "salary_usd", "skills_count",
                          "skills_list", "education_level"]])
    except Exception as e:
        print(f"  Skip DS2021-2023: {e}")

    # 2) data_science_salaries.csv (global, ~6.6k rows)
    try:
        df = pd.read_csv(f"{uploads_dir}/data_science_salaries.csv")
        df["skills_count"] = 5
        df["skills_list"] = ""
        df["education_level"] = "Bachelor"
        df["experience_level"] = df["experience_level"].map({
            "EN": "Junior", "MI": "Mid-level", "SE": "Senior", "EX": "Expert",
        }).fillna("Mid-level")
        df["country"] = df["employee_residence"]
        df["salary_usd"] = df["salary_in_usd"]
        frames.append(df[["job_title", "experience_level", "company_size",
                          "country", "salary_usd", "skills_count",
                          "skills_list", "education_level"]])
    except Exception as e:
        print(f"  Skip DS salaries: {e}")

    # 3) ai_jobs_market_2025_2026.csv (mostly US/UK, ~1.5k rows)
    try:
        df = pd.read_csv(f"{uploads_dir}/ai_jobs_market_2025_2026.csv")
        df["experience_level"] = df["experience_level"].map({
            "Entry-level": "Junior", "Fresher": "Junior",
            "Mid-level": "Mid-level", "Senior (6-9 yrs)": "Senior",
            "Senior": "Senior", "Expert (10+ yrs)": "Expert", "Director": "Expert",
        }).fillna("Mid-level")
        df["company_size"] = df["company_size"].map({
            "Startup (1-50)": "Small",
            "Small (51-200)": "Small",
            "Medium (201-1000)": "Medium",
            "Large (1001-5000)": "Large",
            "Enterprise (5000+)": "Large",
        }).fillna("Medium")
        df["country"] = df["country"]
        df["salary_usd"] = df["annual_salary_usd"]
        df["skills_list"] = df["required_skills"].fillna("")
        df["skills_count"] = df["skills_list"].str.split("|").apply(len)
        df["education_level"] = df["education_required"].map({
            "Bachelor's": "Bachelor", "Master's": "Master",
            "PhD": "PhD", "Associate": "Associate",
            "High School": "High School",
        }).fillna("Bachelor")
        frames.append(df[["job_title", "experience_level", "company_size",
                          "country", "salary_usd", "skills_count",
                          "skills_list", "education_level"]])
    except Exception as e:
        print(f"  Skip AI jobs: {e}")

    # 4) Salary_Dataset_with_Extra_Features.csv (Indian glassdoor, ~22k rows)
    try:
        df = pd.read_csv(f"{uploads_dir}/Salary_Dataset_with_Extra_Features.csv")
        df["job_title"] = df["Job Roles"].fillna(df["Job Title"])
        df["company_size"] = "Medium"  # not provided
        df["country"] = "India"
        df["experience_level"] = "Mid-level"
        df["skills_count"] = 5
        df["skills_list"] = ""
        # Salary is in INR — convert to USD
        df["salary_usd"] = df["Salary"] * 0.012  # INR -> USD
        df["education_level"] = "Bachelor"
        frames.append(df[["job_title", "experience_level", "company_size",
                          "country", "salary_usd", "skills_count",
                          "skills_list", "education_level"]])
    except Exception as e:
        print(f"  Skip Indian glassdoor: {e}")

    if not frames:
        raise RuntimeError("No real datasets could be loaded!")

    master = pd.concat(frames, ignore_index=True)
    print(f"\nMerged real datasets: {len(master):,} rows")
    print(f"  Sources: {len(frames)} files")
    print(f"  Countries: {master['country'].nunique()}")
    print(f"  Salary range: ${master['salary_usd'].min():,.0f} – ${master['salary_usd'].max():,.0f}")
    print(f"  Median salary: ${master['salary_usd'].median():,.0f}")
    return master


def add_synthetic_experience_years(df: pd.DataFrame) -> pd.DataFrame:
    """Map experience_level to approximate years."""
    mapping = {"Junior": 2, "Mid-level": 5, "Senior": 8, "Expert": 12}
    df["experience_years"] = df["experience_level"].map(mapping).fillna(5)
    return df


def train_salary_model(master: pd.DataFrame) -> Pipeline:
    """
    Train a regression pipeline for salary prediction.
    Returns a fitted Pipeline (preprocessor + model).
    """
    master = add_synthetic_experience_years(master.copy())

    # Filter realistic salaries
    master = master[
        (master["salary_usd"] >= 5000)
        & (master["salary_usd"] <= 500_000)
    ].copy()

    # Feature columns
    NUM = ["experience_years", "skills_count"]
    CAT = ["job_title", "country", "company_size", "experience_level"]

    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=10), CAT),
        ],
        remainder="drop",
    )

    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        random_state=42,
    )

    pipe = Pipeline([("pre", pre), ("m", model)])

    X = master[NUM + CAT]
    y = master["salary_usd"]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42,
    )

    print("\nTraining salary model on real data...")
    pipe.fit(X_tr, y_tr)
    p = pipe.predict(X_te)

    print(f"\n📊 HONEST metrics (held-out test set):")
    print(f"   MAE:   ${mean_absolute_error(y_te, p):,.0f}")
    print(f"   RMSE:  ${np.sqrt(mean_squared_error(y_te, p)):,.0f}")
    print(f"   R²:    {r2_score(y_te, p):.3f}")

    cv = KFold(n_splits=3, shuffle=True, random_state=42)
    cv_r2 = cross_val_score(pipe, X, y, cv=cv, scoring="r2", n_jobs=-1)
    print(f"   CV R²: {cv_r2.mean():.3f} ± {cv_r2.std():.3f}")

    # Save
    with open(os.path.join(MODELS_DIR, "salary_model.pkl"), "wb") as f:
        pickle.dump(pipe, f)
    print(f"\n✅ Model saved to {MODELS_DIR}/salary_model.pkl")
    return pipe


def predict_salary(pipe: Pipeline,
                   job_title: str, experience_years: float,
                   skills_count: int, company_size: str, country: str,
                   experience_level: str) -> float:
    """Predict salary in USD for a single user."""
    import pandas as pd
    row = pd.DataFrame([{
        "experience_years": float(experience_years),
        "skills_count":     int(skills_count),
        "job_title":        job_title or "software engineer",
        "country":          country or "USA",
        "company_size":     company_size or "Medium",
        "experience_level": experience_level or "Mid-level",
    }])
    return float(pipe.predict(row)[0])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-feedback", action="store_true",
                       help="Retrain using user feedback + custom data too")
    parser.add_argument("--uploads-dir", default=None,
                       help="Path to public dataset folder (auto-detects if not provided)")
    args = parser.parse_args()

    if args.with_feedback:
        from feedback import get_all_training_data
        master = get_all_training_data(uploads_dir=args.uploads_dir)
    else:
        master = load_real_datasets(uploads_dir=args.uploads_dir)
    pipe = train_salary_model(master)

    # Sample predictions
    print("\n" + "=" * 50)
    print("SAMPLE PREDICTIONS")
    print("=" * 50)
    for jt, yrs, lvl, country in [
        ("software engineer", 2, "Junior", "India"),
        ("data scientist",    5, "Mid-level", "India"),
        ("ml engineer",       7, "Senior", "India"),
        ("data scientist",    5, "Senior", "USA"),
        ("software engineer", 3, "Mid-level", "USA"),
    ]:
        sal = predict_salary(pipe, jt, yrs, 6, "Medium", country, lvl)
        if country == "India":
            print(f"  {jt:<22} {yrs}y {lvl:<10} → ${sal:,.0f} (~₹{sal*83/100000:.1f} LPA)")
        else:
            print(f"  {jt:<22} {yrs}y {lvl:<10} → ${sal:,.0f}")
