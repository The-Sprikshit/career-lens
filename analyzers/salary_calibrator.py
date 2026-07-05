"""
Salary Calibrator
=================
Fixes the over-prediction problem by:
1. Adjusting predictions by country (India is ~30% of USA)
2. Capping predictions to realistic role+experience salary bands
3. Returning a RANGE (low/mid/high) instead of a point estimate

Be honest: regression models trained on noisy data will over-predict.
The calibration layer corrects for this using industry-known salary bands.
"""

from data.role_profiles import (
    ROLE_PROFILES,
    COUNTRY_ADJUSTMENTS,
    estimate_experience_level,
)


# USD → INR conversion (2025)
USD_TO_INR = 83.0


def calibrate_salary(
    raw_prediction_usd: float,
    role: str,
    country: str,
    experience_years: float,
    skills: list = None,
) -> dict:
    """
    Take the model's raw prediction and return a calibrated, honest range.

    Returns:
    {
        "salary_low_usd":  120000,
        "salary_mid_usd":  145000,
        "salary_high_usd": 170000,
        "salary_low_lpa":   "99.6 LPA",        # only for India
        "salary_high_lpa":  "141.1 LPA",        # only for India
        "confidence":       "medium",
        "notes":            "Capped by role band for India Senior SE",
    }
    """
    role_key = role.lower().strip()
    profile = ROLE_PROFILES.get(role_key)

    # Fallback: use software engineer band
    if not profile:
        profile = ROLE_PROFILES["software engineer"]

    # Get the role's salary band for this experience level
    level = estimate_experience_level(experience_years)
    band_usd = profile["salary_bands_usd"][level]
    band_low, band_high = band_usd

    # Apply country adjustment
    country_adj = COUNTRY_ADJUSTMENTS.get(country, 0.7)
    band_low_adj = band_low * country_adj
    band_high_adj = band_high * country_adj

    # Now use the model's prediction to position WITHIN the band
    # If model predicts way above band → cap to band high
    # If model predicts way below band → floor to band low
    # If in range → use as a position indicator
    raw_adj = raw_prediction_usd * country_adj

    # Calibrated point = weighted blend of model and band midpoint
    band_mid = (band_low_adj + band_high_adj) / 2
    calibrated_mid = 0.4 * raw_adj + 0.6 * band_mid
    # Cap to band
    calibrated_mid = max(band_low_adj, min(band_high_adj, calibrated_mid))

    # Compute range around the calibrated mid (±15%)
    salary_low = calibrated_mid * 0.85
    salary_high = calibrated_mid * 1.15

    # Floor / cap to band
    salary_low = max(band_low_adj, salary_low)
    salary_high = min(band_high_adj, salary_high)

    # Confidence: how close model was to band before capping
    if band_low_adj <= raw_adj <= band_high_adj:
        confidence = "high"
    elif abs(raw_adj - band_mid) / band_mid < 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    notes = []
    if raw_adj > band_high_adj * 1.2:
        notes.append(
            f"Model over-predicted (${raw_adj:,.0f}); capped to band max ${band_high_adj:,.0f}"
        )
    elif raw_adj < band_low_adj * 0.5:
        notes.append(
            f"Model under-predicted (${raw_adj:,.0f}); floored to band min ${band_low_adj:,.0f}"
        )
    if country == "India":
        notes.append(f"India adjustment applied ({country_adj}x USA baseline)")

    result = {
        "salary_low_usd":  round(salary_low, 0),
        "salary_mid_usd":  round(calibrated_mid, 0),
        "salary_high_usd": round(salary_high, 0),
        "raw_prediction_usd": round(raw_prediction_usd, 0),
        "band_low_usd":  round(band_low_adj, 0),
        "band_high_usd": round(band_high_adj, 0),
        "confidence": confidence,
        "level": level,
        "country_adj": country_adj,
        "notes": notes,
    }

    if country == "India":
        result["salary_low_lpa"]  = f"₹{salary_low * USD_TO_INR / 100_000:.1f} LPA"
        result["salary_high_lpa"] = f"₹{salary_high * USD_TO_INR / 100_000:.1f} LPA"
        result["salary_mid_lpa"]  = f"₹{calibrated_mid * USD_TO_INR / 100_000:.1f} LPA"

    return result


if __name__ == "__main__":
    # Test calibration
    print("=" * 70)
    print("SALARY CALIBRATION TEST")
    print("=" * 70)

    test_cases = [
        ("software engineer", 5, "USA",   200000),
        ("software engineer", 5, "India", 200000),
        ("data scientist",    3, "USA",   200000),
        ("data scientist",    3, "India", 200000),
        ("ml engineer",       4, "USA",   200000),
        ("ml engineer",       4, "India", 200000),
        ("data analyst",      2, "USA",   200000),
        ("product manager",   6, "USA",   200000),
        ("product manager",   6, "India", 200000),
        ("engineering manager", 8, "USA", 200000),
    ]
    print(f"\n{'Role':<22} {'Yrs':>3} {'Country':<8} {'Raw':>10} → Calibrated Range")
    print("-" * 70)
    for role, yrs, country, raw in test_cases:
        cal = calibrate_salary(raw, role, country, yrs)
        if country == "India":
            print(f"{role:<22} {yrs:>3} {country:<8} ${raw/1000:>5.0f}k → "
                  f"₹{cal['salary_low_usd']*USD_TO_INR/100000:.0f}-{cal['salary_high_usd']*USD_TO_INR/100000:.0f} LPA"
                  f" (${cal['salary_low_usd']/1000:.0f}k-${cal['salary_high_usd']/1000:.0f}k) "
                  f"[{cal['confidence']}]")
        else:
            print(f"{role:<22} {yrs:>3} {country:<8} ${raw/1000:>5.0f}k → "
                  f"${cal['salary_low_usd']/1000:.0f}k-${cal['salary_high_usd']/1000:.0f}k "
                  f"[{cal['confidence']}]")
        if cal["notes"]:
            for n in cal["notes"]:
                print(f"  ⚠️  {n}")
