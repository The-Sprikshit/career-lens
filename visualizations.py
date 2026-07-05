"""
Visualizations — matplotlib + plotly charts for Streamlit.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List


# ── Matplotlib style ────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")


def plot_quality_radar(subscores: Dict[str, float]) -> plt.Figure:
    """Radar chart of resume quality subscores."""
    categories = list(subscores.keys())
    values = list(subscores.values())
    categories.append(categories[0])
    values.append(values[0])

    angles = np.linspace(0, 2 * np.pi, len(categories)).tolist()

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color="#4F8BF9", alpha=0.25)
    ax.plot(angles, values, color="#4F8BF9", linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([c.replace("_", " ").title() for c in categories[:-1]])
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_title("Resume Quality Profile", size=14, pad=20)
    return fig


def plot_skill_roi(roi_list: List[Dict], top_n: int = 10) -> plt.Figure:
    """Horizontal bar chart of skill salary uplifts."""
    if not roi_list:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return fig

    top = roi_list[:top_n]
    skills = [r["skill"] for r in top][::-1]
    uplifts = [r["salary_uplift_usd"] for r in top][::-1]
    colors = ["#2ecc71" if u > 15000 else "#f39c12" if u > 8000 else "#3498db"
              for u in uplifts]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(skills, uplifts, color=colors)
    ax.set_xlabel("Expected Salary Uplift (USD)", fontsize=11)
    ax.set_title(f"Top {top_n} Skills to Add for Salary Growth",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    for bar, val in zip(bars, uplifts):
        ax.text(val + 200, bar.get_y() + bar.get_height()/2,
                f"+${val:,.0f}", va="center", fontsize=9)
    plt.tight_layout()
    return fig


def plot_skills_by_category(by_category: Dict[str, List[str]],
                            missing_critical: List[str]) -> plt.Figure:
    """Bar chart of skill counts per category + missing critical."""
    from data.skills_db import SKILLS_DB
    cats = list(by_category.keys())
    have = [len(by_category[c]) for c in cats]
    missing = [len([m for m in missing_critical
                    if SKILLS_DB.get(m, {}).get("category") == c])
               for c in cats]

    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(cats))
    width = 0.35
    ax.bar(x - width/2, have, width, label="You have", color="#2ecc71")
    ax.bar(x + width/2, missing, width, label="Critical missing", color="#e74c3c")
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", " ").title() for c in cats],
                       rotation=30, ha="right")
    ax.set_ylabel("Skill count")
    ax.set_title("Skills Coverage by Category", fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig


def plot_career_paths(paths: List[Dict]) -> go.Figure:
    """Plotly line chart of career path salary progressions."""
    fig = go.Figure()
    colors = ["#3498db", "#e74c3c", "#2ecc71"]
    for i, path in enumerate(paths):
        years = [0, path["timeline_years"]]
        salaries = [path["salary_now"], path["salary_then"]]
        fig.add_trace(go.Scatter(
            x=years, y=salaries,
            mode="lines+markers+text",
            name=path["type"],
            line=dict(color=colors[i % 3], width=3),
            marker=dict(size=12),
            text=[f"${s:,.0f}" for s in salaries],
            textposition="top center",
        ))
    fig.update_layout(
        title="3 Career Path Projections",
        xaxis_title="Years from now",
        yaxis_title="Salary (USD)",
        height=450,
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def plot_salary_comparison(current_salary: float,
                           predicted: float,
                           top_skills_uplift: float) -> plt.Figure:
    """Compare current vs predicted vs predicted+best-skill."""
    labels = ["Current", "Predicted (you)", "Predicted + top skill"]
    values = [current_salary, predicted, predicted + top_skills_uplift]
    colors = ["#95a5a6", "#3498db", "#2ecc71"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("Salary (USD)")
    ax.set_title("Salary Reality Check", fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 2000,
                f"${val:,.0f}", ha="center", fontweight="bold")
    plt.tight_layout()
    return fig


def plot_authenticity_breakdown(red_flags: List[str],
                                signals: List[str]) -> plt.Figure:
    """Visual breakdown of authenticity analysis."""
    fig, ax = plt.subplots(figsize=(10, 4))
    items = red_flags + ["✓ " + s for s in signals]
    colors = ["#e74c3c"] * len(red_flags) + ["#2ecc71"] * len(signals)
    y_pos = np.arange(len(items))
    ax.barh(y_pos, [1] * len(items), color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xticks([])
    ax.set_xlim(0, 1.2)
    ax.set_title("Authenticity Signals", fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    plt.tight_layout()
    return fig


def plot_role_gap(gap_result: Dict, country: str = "USA") -> plt.Figure:
    """
    NEW CHART: Visualize skill gap for a target role.

    Shows each skill with color-coded priority:
    - Green: required skill you HAVE
    - Red: required skill you DON'T have (critical)
    - Yellow: preferred skill you DON'T have
    - Light green: preferred skill you HAVE
    """
    if "error" in gap_result:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, gap_result["error"], ha="center", va="center", wrap=True)
        return fig

    target = gap_result["target_role"].title()
    skills = []
    statuses = []
    priorities = []

    # Required have (green)
    for s in gap_result["required_have"]:
        skills.append(s)
        statuses.append("HAVE")
        priorities.append(0)

    # Required missing (red - critical)
    for s in gap_result["required_missing"]:
        skills.append(s)
        statuses.append("MISSING (CRITICAL)")
        priorities.append(1)

    # Preferred have (light green)
    for s in gap_result["preferred_have"]:
        skills.append(s)
        statuses.append("HAVE")
        priorities.append(2)

    # Preferred missing (yellow)
    for s in gap_result["preferred_missing"]:
        skills.append(s)
        statuses.append("MISSING")
        priorities.append(3)

    if not skills:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return fig

    # Sort: missing first (red on top), then by priority
    order = sorted(range(len(skills)), key=lambda i: (priorities[i], skills[i]))
    skills = [skills[i] for i in order]
    statuses = [statuses[i] for i in order]

    color_map = {
        "HAVE": "#2ecc71",
        "MISSING (CRITICAL)": "#e74c3c",
        "MISSING": "#f39c12",
    }
    colors = [color_map[s] for s in statuses]

    fig, ax = plt.subplots(figsize=(11, max(4, len(skills) * 0.35)))
    y_pos = np.arange(len(skills))
    bars = ax.barh(y_pos, [1] * len(skills), color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{s}  [{status}]" for s, status in zip(skills, statuses)],
                       fontsize=10)
    ax.set_xticks([])
    ax.set_xlim(0, 1.05)
    ax.set_title(
        f"Skill Gap for '{target}' (Match: {gap_result['match_score']}/100)",
        fontsize=13, fontweight="bold", pad=15
    )

    # Legend
    legend_patches = [
        mpatches.Patch(color="#e74c3c", label="Missing REQUIRED"),
        mpatches.Patch(color="#f39c12", label="Missing PREFERRED"),
        mpatches.Patch(color="#2ecc71", label="You HAVE this skill"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    plt.tight_layout()
    return fig


def plot_role_salary_band(role: str, country: str,
                          years: float, calibrated: Dict) -> plt.Figure:
    """
    Visualize the calibrated salary band for a role.
    Shows: raw model prediction, country-adjusted band, calibrated range.
    """
    fig, ax = plt.subplots(figsize=(9, 5))

    band_low = calibrated["band_low_usd"]
    band_high = calibrated["band_high_usd"]
    cal_low = calibrated["salary_low_usd"]
    cal_high = calibrated["salary_high_usd"]
    cal_mid = calibrated["salary_mid_usd"]
    raw = calibrated["raw_prediction_usd"]

    # Band background
    ax.barh(["Salary Band"], [band_high - band_low], left=[band_low],
            color="#ecf0f1", edgecolor="#bdc3c7", height=0.6,
            label=f"Industry band (${band_low/1000:.0f}k-${band_high/1000:.0f}k)")

    # Calibrated range
    ax.barh(["Your Range"], [cal_high - cal_low], left=[cal_low],
            color="#3498db", edgecolor="#2c3e50", height=0.6,
            label=f"Your calibrated range (${cal_low/1000:.0f}k-${cal_high/1000:.0f}k)")

    # Mid-point marker
    ax.scatter([cal_mid], ["Your Range"], color="#2c3e50", s=200, zorder=5,
               marker="D", label=f"Mid point: ${cal_mid/1000:.0f}k")

    # Raw prediction (where the model said before calibration)
    ax.axvline(raw, color="#e74c3c", linestyle="--", linewidth=2,
               label=f"Raw model: ${raw/1000:.0f}k (over-predicted, capped)")

    if country == "India":
        ax.set_xlabel(f"Salary (USD) — equivalent to ₹{cal_low*83/100000:.0f}-₹{cal_high*83/100000:.0f} LPA")
    else:
        ax.set_xlabel("Salary (USD)")

    ax.set_title(f"Salary Band for {role.title()} ({country})",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    return fig
