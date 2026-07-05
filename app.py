"""
Resume AI v4 — FastAPI-powered salary engine + full upgraded UI.
"""
import os, sys, re, json, datetime, threading, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe
import plotly.graph_objects as go
import plotly.express as px
import httpx

st.set_page_config(page_title="Resume AI", page_icon="✦",
                   layout="wide", initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════════════════
# PALETTE — electric indigo × neon cyan × deep space
# ═══════════════════════════════════════════════════════════════════════
C = dict(
    bg     = "#07080F",
    card   = "#0D1120",
    card2  = "#111827",
    bdr    = "#1C2333",
    bdr2   = "#253048",
    cyan   = "#00F5D4",
    indigo = "#6366F1",
    violet = "#A855F7",
    rose   = "#F43F5E",
    amber  = "#FBBF24",
    lime   = "#84CC16",
    sky    = "#38BDF8",
    t1     = "#EEF2FF",
    t2     = "#8B9BC8",
    t3     = "#3D4F72",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global ── */
.stApp{{background:{C['bg']}!important;font-family:'Inter',sans-serif;color:{C['t1']};}}
* {{box-sizing:border-box;}}

/* ── Sidebar ── */
[data-testid="stSidebar"]{{
  background:linear-gradient(180deg,#0B0F1E 0%,#0D1225 100%)!important;
  border-right:1px solid {C['bdr']}!important;
  min-width:270px!important;max-width:270px!important;
}}
[data-testid="stSidebar"] .stMarkdown h2{{
  font-family:'Space Grotesk',sans-serif!important;
  background:linear-gradient(90deg,{C['cyan']},{C['indigo']});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  font-size:1.3rem!important;letter-spacing:-.01em;margin:0!important;
}}
[data-testid="stSidebar"] *{{color:{C['t2']}!important;}}
[data-testid="stSidebar"] strong{{color:{C['t1']}!important;}}

/* sidebar section cards */
.sb-card{{
  background:{C['card']}; border:1px solid {C['bdr']};
  border-radius:10px; padding:.75rem .9rem; margin:.4rem 0;
}}
.sb-lbl{{
  color:{C['t3']}!important; font-size:.65rem!important;
  font-weight:700!important; letter-spacing:.12em!important;
  text-transform:uppercase!important; margin-bottom:.35rem; display:block;
}}
.sb-stat{{display:flex;justify-content:space-between;align-items:center;margin:.2rem 0;}}
.sb-stat-k{{color:{C['t2']}; font-size:.78rem;}}
.sb-stat-v{{color:{C['t1']}; font-size:.78rem; font-weight:600;
  font-family:'JetBrains Mono',monospace;}}
.sb-badge{{
  display:inline-block;border-radius:5px;padding:2px 7px;
  font-size:.68rem;font-weight:700;letter-spacing:.04em;
}}
.badge-ok  {{background:{C['cyan']}22;border:1px solid {C['cyan']}55;color:{C['cyan']};}}
.badge-warn{{background:{C['amber']}22;border:1px solid {C['amber']}55;color:{C['amber']};}}
.badge-bad {{background:{C['rose']}22;border:1px solid {C['rose']}55;color:{C['rose']};}}

/* link cards */
.link-card{{
  background:{C['card2']};border:1px solid {C['bdr']};border-radius:8px;
  padding:.5rem .8rem;margin:.25rem 0;display:flex;align-items:center;gap:.6rem;
}}
.link-icon{{font-size:1rem;flex-shrink:0;}}
.link-url{{color:{C['cyan']};font-size:.76rem;font-family:'JetBrains Mono',monospace;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px;}}

/* ── Metrics ── */
[data-testid="stMetric"]{{
  background:{C['card']};border:1px solid {C['bdr']};border-radius:12px;
  padding:.85rem 1rem!important;transition:border-color .2s,transform .15s;
}}
[data-testid="stMetric"]:hover{{border-color:{C['cyan']}60;transform:translateY(-1px);}}
[data-testid="stMetricLabel"]{{
  color:{C['t3']}!important;font-size:.65rem!important;font-weight:700!important;
  letter-spacing:.09em!important;text-transform:uppercase!important;
}}
[data-testid="stMetricValue"]{{
  color:{C['t1']}!important;font-family:'Space Grotesk',sans-serif!important;
  font-size:1.4rem!important;font-weight:700!important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"]{{
  background:{C['card']};border-radius:12px;padding:3px;
  border:1px solid {C['bdr']};gap:1px;
}}
[data-testid="stTabs"] [role="tab"]{{
  border-radius:9px!important;color:{C['t2']}!important;
  font-weight:500!important;font-size:.8rem!important;padding:.4rem .8rem!important;
  transition:color .15s!important;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{{
  background:linear-gradient(135deg,{C['cyan']},{C['indigo']})!important;
  color:#fff!important;font-weight:700!important;
}}

/* ── Buttons ── */
.stButton>button{{
  background:linear-gradient(135deg,{C['indigo']},{C['violet']})!important;
  color:#fff!important;border:none!important;border-radius:8px!important;
  font-weight:600!important;font-size:.84rem!important;
  padding:.45rem 1.3rem!important;letter-spacing:.02em;transition:opacity .2s!important;
}}
.stButton>button:hover{{opacity:.85!important;}}
.stDownloadButton>button{{
  background:transparent!important;color:{C['cyan']}!important;
  border:1.5px solid {C['cyan']}!important;border-radius:8px!important;
  font-weight:600!important;font-size:.83rem!important;padding:.42rem 1rem!important;
  width:100%!important;transition:background .2s!important;
}}
.stDownloadButton>button:hover{{background:{C['cyan']}14!important;}}

/* ── Progress ── */
.stProgress>div>div>div{{
  background:linear-gradient(90deg,{C['cyan']},{C['indigo']})!important;border-radius:3px;
}}
.stProgress>div>div{{background:{C['bdr']}!important;border-radius:3px;}}

/* ── Inputs ── */
.stTextInput>div>div>input,.stNumberInput>div>div>input,
.stTextArea textarea{{
  background:{C['card2']}!important;border:1px solid {C['bdr']}!important;
  border-radius:7px!important;color:{C['t1']}!important;font-size:.85rem!important;
}}
.stTextInput>div>div>input:focus{{border-color:{C['cyan']}!important;}}
.stSelectbox>div>div{{
  background:{C['card2']}!important;border:1px solid {C['bdr']}!important;border-radius:7px!important;
}}
[data-testid="stFileUploader"]{{
  background:{C['cyan']}05;border:2px dashed {C['cyan']}40!important;border-radius:12px!important;
}}

/* ── Alerts ── */
div[data-testid="stAlert"]{{border-radius:9px!important;}}

/* ── Scrollbar ── */
hr{{border:none!important;border-top:1px solid {C['bdr']}!important;margin:1rem 0!important;}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:{C['bg']};}}
::-webkit-scrollbar-thumb{{background:{C['bdr2']};border-radius:2px;}}
::-webkit-scrollbar-thumb:hover{{background:{C['cyan']};}}

/* ── Hero ── */
.hero{{
  background:linear-gradient(135deg,{C['cyan']}0E,{C['indigo']}0E);
  border:1px solid {C['indigo']}35;border-radius:16px;
  padding:1.3rem 1.7rem;margin-bottom:.9rem;position:relative;overflow:hidden;
}}
.hero::before{{
  content:'';position:absolute;top:-40px;right:-40px;
  width:180px;height:180px;border-radius:50%;
  background:radial-gradient({C['cyan']}15,transparent 70%);
}}
.hero h1{{
  font-family:'Space Grotesk',sans-serif;font-size:1.75rem;font-weight:800;
  background:linear-gradient(90deg,{C['cyan']},{C['indigo']},{C['violet']});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;
}}

/* ── Section heading ── */
.sh{{
  font-family:'Space Grotesk',sans-serif;font-size:.92rem;font-weight:700;
  color:{C['t1']};margin:.85rem 0 .5rem;display:flex;align-items:center;gap:.4rem;
}}

/* ── Gate banners ── */
.gate{{border-radius:13px;padding:1.2rem 1.4rem;margin-bottom:.85rem;}}
.gate-weak{{background:{C['rose']}08;border:1px solid {C['rose']}35;}}
.gate-warn{{background:{C['amber']}08;border:1px solid {C['amber']}35;}}
.gate-title{{font-family:'Space Grotesk',sans-serif;font-size:.95rem;
  font-weight:700;color:{C['t1']};margin-bottom:.25rem;}}

/* ── Salary band display ── */
.sal-band{{
  display:flex;align-items:center;justify-content:center;
  gap:1.5rem;padding:1.2rem;background:{C['card2']};
  border:1px solid {C['bdr']};border-radius:12px;margin:.5rem 0;
  flex-wrap:wrap;
}}
.sal-num{{font-family:'Space Grotesk',sans-serif;font-weight:700;
  font-size:1.55rem;color:{C['t1']};line-height:1;}}
.sal-label{{font-size:.66rem;color:{C['t3']};font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;margin-top:.15rem;}}
.sal-mid .sal-num{{
  font-size:2rem;
  background:linear-gradient(90deg,{C['cyan']},{C['indigo']});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}}
.sal-sep{{color:{C['bdr2']};font-size:1.2rem;}}

/* ── Check items ── */
.ci{{
  background:{C['card2']};border:1px solid {C['bdr']};border-radius:8px;
  padding:.48rem .9rem;margin:.22rem 0;color:#C8D4F0;font-size:.83rem;
  border-left:3px solid {C['bdr2']};
}}
.ci-c{{border-left-color:{C['cyan']};}}
.ci-r{{border-left-color:{C['rose']};}}
.ci-g{{border-left-color:{C['lime']};}}
.ci-a{{border-left-color:{C['amber']};}}
.ci-v{{border-left-color:{C['violet']};}}

/* ── Pills ── */
.pill{{display:inline-block;border-radius:20px;padding:3px 10px;
  font-size:.74rem;font-weight:500;margin:2px;}}
.p-g{{background:{C['lime']}18;border:1px solid {C['lime']}45;color:{C['lime']};}}
.p-r{{background:{C['rose']}15;border:1px solid {C['rose']}45;color:#FCA5A5;}}
.p-a{{background:{C['amber']}15;border:1px solid {C['amber']}45;color:{C['amber']};}}
.p-c{{background:{C['cyan']}14;border:1px solid {C['cyan']}45;color:{C['cyan']};}}
.p-v{{background:{C['violet']}18;border:1px solid {C['violet']}50;color:#C4B5FD;}}

/* ── Roadmap ── */
.rm-step{{
  display:flex;gap:.85rem;align-items:flex-start;
  background:{C['card2']};border:1px solid {C['bdr']};border-radius:10px;
  padding:.8rem 1rem;margin:.32rem 0;
}}
.rm-num{{
  background:linear-gradient(135deg,{C['cyan']},{C['indigo']});color:{C['bg']};
  border-radius:50%;width:26px;height:26px;display:flex;align-items:center;
  justify-content:center;font-weight:800;font-size:.78rem;flex-shrink:0;
}}
.rm-title{{color:{C['t1']};font-weight:600;font-size:.86rem;margin-bottom:.2rem;}}
.rm-desc{{color:{C['t2']};font-size:.78rem;line-height:1.55;}}
.rm-link{{color:{C['cyan']};}}

/* ── Match badge ── */
.mbadge{{
  display:inline-flex;align-items:center;justify-content:center;
  width:70px;height:70px;border-radius:50%;
  font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:800;
}}
.mb-hi{{background:{C['lime']}18;border:2.5px solid {C['lime']};color:{C['lime']};}}
.mb-md{{background:{C['amber']}18;border:2.5px solid {C['amber']};color:{C['amber']};}}
.mb-lo{{background:{C['rose']}18;border:2.5px solid {C['rose']};color:{C['rose']};}}

/* ── API status ── */
.api-status{{
  display:flex;align-items:center;gap:.4rem;
  font-size:.7rem;font-weight:600;margin:.2rem 0;
}}
.api-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0;}}
.api-on{{background:{C['lime']};box-shadow:0 0 6px {C['lime']};}}
.api-off{{background:{C['rose']};}}
</style>
""", unsafe_allow_html=True)

# ── IMPORTS ──────────────────────────────────────────────────────────
from parser import parse_resume
from analyzers.skill_extractor import extract_skills, calculate_skill_roi
from analyzers.resume_quality import analyze_quality
from analyzers.authenticity import analyze_authenticity
from analyzers.career_path import suggest_paths
from analyzers.salary_calibrator import calibrate_salary
from analyzers.role_gap import analyze_role_gap
from data.role_profiles import ROLE_CATEGORIES, estimate_experience_level
from data.skills_db import SKILLS_DB
from db import save_analysis
from portfolio_store import save_submission, validate_url, init_db
from report_gen import generate_report

init_db()

# ── FastAPI salary client ─────────────────────────────────────────────
API_URL = "http://localhost:8000"

def _start_api_server():
    """Launch salary_api.py in background if not already running."""
    try:
        httpx.get(f"{API_URL}/health", timeout=1.5)
        return True
    except Exception:
        pass
    try:
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "salary_api:app",
             "--host", "0.0.0.0", "--port", "8000", "--log-level", "error"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(12):
            time.sleep(0.5)
            try:
                httpx.get(f"{API_URL}/health", timeout=1)
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False

@st.cache_resource(show_spinner=False)
def ensure_api():
    return _start_api_server()

def api_salary(role, experience_years, country, skills=None):
    """Call FastAPI salary engine. Returns dict or None on failure."""
    try:
        r = httpx.post(f"{API_URL}/predict", json={
            "role": role, "experience_years": float(experience_years),
            "country": country, "skills": skills or [],
        }, timeout=4.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

# ── GATE ─────────────────────────────────────────────────────────────
THRESHOLD = 42
WARNING   = 65

def profile_strength(parsed, skills_result, quality_result):
    q  = quality_result["overall_score"]
    sk = min(100, len(skills_result["skills"]) * 8)
    ex = min(20, (parsed.get("years_experience") or 0) * 4)
    lk = 10 if parsed.get("links") else 0
    em = 5  if parsed.get("email") else 0
    return round(min(100, q*0.5 + sk*0.3 + ex + lk + em))

def essentials_check(parsed, skills_result):
    text  = parsed.get("raw_text","").lower()
    links = " ".join(parsed.get("links",[])).lower()
    secs  = parsed.get("sections", {})
    return [
        ("📧 Email address",        bool(parsed.get("email"))),
        ("📞 Phone number",         bool(parsed.get("phone"))),
        ("🔗 LinkedIn profile",     "linkedin" in text or "linkedin" in links),
        ("💻 GitHub profile",       "github"   in text or "github"   in links),
        ("🌐 Portfolio / website",  any(x in text for x in ["portfolio","behance","website"])),
        ("📝 Professional summary", any(k in secs for k in ["summary","objective","profile"])),
        ("🎓 Education section",    "education" in secs),
        ("💼 Experience / Projects",any(k in secs for k in ["experience","work experience","projects"])),
        ("🛠 Skills section",       "skills" in secs or bool(skills_result["skills"])),
        ("📊 Quantified impact",    bool(re.search(r'\d+%|\d+ (users|clients|projects|teams)', text))),
    ]

# ══════════════════════════════════════════════════════════════════════
# CHARTS  — new palette, glow effects, gradient bars
# ══════════════════════════════════════════════════════════════════════

BG    = C['bg'];    CARD  = C['card'];   BDR = C['bdr']
CYN   = C['cyan'];  IND   = C['indigo']; VIO = C['violet']
ROSE  = C['rose'];  AMB   = C['amber'];  LIM = C['lime']
T1    = C['t1'];    T2    = C['t2'];     T3  = C['t3']

def dfig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w,h), facecolor=BG)
    ax.set_facecolor(CARD)
    for sp in ax.spines.values(): sp.set_edgecolor(BDR)
    ax.tick_params(colors=T2, labelsize=8.5)
    ax.xaxis.label.set_color(T2); ax.yaxis.label.set_color(T2)
    ax.title.set_color(T1)
    ax.grid(color=BDR, alpha=0.5, linestyle="--", linewidth=0.4)
    return fig, ax

def _glow_bar(ax, y, w, left, height, color, zorder=3, alpha=0.85):
    ax.barh(y, w, left=left, height=height,
            color=color, alpha=alpha, edgecolor="none", zorder=zorder)
    ax.barh(y, w*0.05, left=left+w*0.95, height=height,
            color="white", alpha=0.12, edgecolor="none", zorder=zorder+1)

def viz_quality_radar(subscores):
    cats = list(subscores.keys()); vals = list(subscores.values())
    cats2 = cats+[cats[0]]; vals2 = vals+[vals[0]]
    angles = np.linspace(0,2*np.pi,len(cats2)).tolist()
    fig = plt.figure(figsize=(5.2,5.2), facecolor=BG)
    ax  = fig.add_subplot(111, polar=True, facecolor=CARD)
    # outer glow
    ax.fill(angles,[100]*len(angles), color=IND, alpha=0.04)
    ax.fill(angles, vals2, color=CYN, alpha=0.18)
    ax.fill(angles, vals2, color=IND, alpha=0.06)
    ax.plot(angles, vals2, color=CYN, linewidth=2.5,
            path_effects=[pe.withStroke(linewidth=5,foreground=CYN+"44")])
    ax.scatter(angles, vals2, color=CYN, s=55, zorder=5,
               edgecolors=BG, linewidth=1.5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([c.replace("_"," ").title() for c in cats], color=T2, fontsize=7.5)
    ax.set_ylim(0,100); ax.set_yticks([20,40,60,80,100])
    ax.set_yticklabels([""]*5); ax.tick_params(colors=BDR)
    ax.spines["polar"].set_color(BDR)
    for gl in ax.yaxis.get_gridlines(): gl.set_color(BDR); gl.set_linewidth(0.4)
    ax.set_title("Quality Radar", color=T1, fontsize=11, fontweight="700", pad=14)
    return fig

def viz_skills_demand(role_gap):
    req_miss  = role_gap.get("required_missing", [])
    pref_miss = role_gap.get("preferred_missing", [])
    req_have  = role_gap.get("required_have", [])
    target    = role_gap.get("role","Role")

    def demand(s): return SKILLS_DB.get(s,{}).get("demand",0.5)
    items = (
        [(s, ROSE, "🔴 Critical—Missing")  for s in sorted(req_miss,  key=demand, reverse=True)[:8]] +
        [(s, AMB,  "🟡 Preferred—Missing") for s in sorted(pref_miss, key=demand, reverse=True)[:5]] +
        [(s, LIM,  "✅ Required—You Have") for s in sorted(req_have,  key=demand, reverse=True)[:4]]
    )
    if not items:
        fig,ax = dfig(8,3)
        ax.text(.5,.5,"No skill data",ha="center",color=T2,transform=ax.transAxes)
        return fig

    labels  = [x[0].title() for x in items]
    demands = [demand(x[0])*100 for x in items]
    colors  = [x[1] for x in items]
    cats_txt= [SKILLS_DB.get(x[0],{}).get("category","").replace("_"," ").title() for x in items]

    fig, ax = dfig(11, max(5, len(items)*.5))
    ax.grid(axis="y",alpha=0)
    ax.grid(axis="x",color=BDR,alpha=0.3,linestyle="--",linewidth=0.4)

    for i,(lbl,dem,col,cat) in enumerate(zip(labels[::-1],demands[::-1],colors[::-1],cats_txt[::-1])):
        _glow_bar(ax, i, dem, 0, 0.62, col)
        ax.text(dem+1, i, f"{dem:.0f}%  ·  {cat}", va="center",
                fontsize=8, color=T1, fontweight="500")

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels[::-1], color=T2, fontsize=8.5)
    ax.set_xlabel("Market Demand %", color=T2, fontsize=9)
    ax.set_title(f"Skills Required for {target.title()}  —  by Demand",
                 color=T1, fontsize=12, fontweight="700", pad=12)
    ax.set_xlim(0,118)
    legend = [mpatches.Patch(color=ROSE,label="Critical — Missing"),
              mpatches.Patch(color=AMB, label="Preferred — Missing"),
              mpatches.Patch(color=LIM, label="Required — You Have")]
    ax.legend(handles=legend, facecolor=CARD, edgecolor=BDR,
              labelcolor=T2, fontsize=8, loc="lower right")
    plt.tight_layout()
    return fig

def viz_skill_roi(roi_list, country="India"):
    top = roi_list[:10]
    skills  = [r["skill"].title() for r in top][::-1]
    uplifts = [r["salary_uplift_usd"] for r in top][::-1]
    n = len(skills)
    if n == 0: return dfig(8,3)[0]
    cmap = plt.cm.cool
    bar_colors = [cmap(i/max(n-1,1)) for i in range(n)]

    fig, ax = dfig(10, max(4.5, n*.52))
    ax.grid(axis="y",alpha=0)
    ax.grid(axis="x",color=BDR,alpha=0.3,linestyle="--",linewidth=0.4)
    for i,(sk,val,col) in enumerate(zip(skills,uplifts,bar_colors)):
        _glow_bar(ax, i, val, 0, 0.62, col)
    ax.set_yticks(range(n))
    ax.set_yticklabels(skills, color=T2, fontsize=8.5)
    for i,(val,col) in enumerate(zip(uplifts,bar_colors)):
        label = (f"+₹{val*83/100000:.0f}L/yr" if country=="India"
                 else f"+${val:,.0f}/yr")
        ax.text(val+200,i,label,va="center",fontsize=8.5,color=T1,fontweight="600")
    ax.set_xlabel("Expected Salary Uplift (USD/year)", color=T2)
    ax.set_title("💡 Skill → Salary Impact  (Cool = lower, Purple = highest)",
                 color=T1, fontsize=11, fontweight="700", pad=12)
    ax.set_xlim(0, max(uplifts)*1.26)
    plt.tight_layout()
    return fig

def viz_salary_gauge(low, mid, high, unit, level):
    """Horizontal salary gauge — neon glow style."""
    fig, ax = plt.subplots(figsize=(10,2.8), facecolor=BG)
    ax.set_facecolor(BG); ax.axis("off")

    # track
    track_y, track_h = 0.38, 0.16
    ax.barh(track_y, high-low, left=low, height=track_h,
            color=C['card2'], zorder=1, edgecolor=BDR, linewidth=0.8)

    # gradient fill — low to high
    n_segs = 40
    for i in range(n_segs):
        frac = i/n_segs
        c = plt.cm.cool(frac*0.75+0.1)
        x0 = low + (mid-low)*frac if frac < 0.5 else mid + (high-mid)*(frac-0.5)*2
        seg_w = (high-low)/n_segs
        ax.barh(track_y, seg_w, left=low+(high-low)*i/n_segs, height=track_h,
                color=c, alpha=0.85, zorder=2, edgecolor="none")

    # mid marker glow
    ax.plot([mid,mid],[track_y-track_h*.9,track_y+track_h*1.9],
            color=CYN, linewidth=4, zorder=5,
            path_effects=[pe.withStroke(linewidth=10,foreground=CYN+"44")])
    ax.scatter([mid],[track_y+track_h*.5], color=CYN, s=130, zorder=6,
               edgecolors=BG, linewidth=2)

    def fmt(v, unit):
        if unit=="LPA": return f"₹{v:.1f}L"
        return f"${v/1000:.0f}k"

    for xv,yv,lbl,col,fs,fw in [
        (low,  track_y+track_h*2.4, fmt(low,unit),  T3,  9, "400"),
        (low,  track_y-track_h*1.8, "Lower",         T3,  7, "400"),
        (mid,  track_y+track_h*2.4, fmt(mid,unit),  CYN, 12,"700"),
        (mid,  track_y-track_h*1.8, "Median",         T2,  7, "600"),
        (high, track_y+track_h*2.4, fmt(high,unit),  T3,  9, "400"),
        (high, track_y-track_h*1.8, "Upper",         T3,  7, "400"),
    ]:
        ax.text(xv, yv, lbl, ha="center", color=col, fontsize=fs, fontweight=fw)

    ax.text((low+high)/2, track_y+track_h*4.3,
            f"Salary Range  ·  {level}  ·  India 2025",
            ha="center", color=T1, fontsize=11, fontweight="600")
    ax.set_xlim(low*.82, high*1.12); ax.set_ylim(0,1)
    plt.tight_layout(pad=0)
    return fig

def viz_salary_compare(current, predicted, top_uplift, country):
    def fmt(v):
        return f"₹{v:.0f}L" if country=="India" else f"${v:,.0f}"
    if country=="India":
        vals   = [current, predicted, predicted+top_uplift]
        ylabel = "Salary (LPA)"
    else:
        vals   = [current, predicted, predicted+top_uplift]
        ylabel = "Salary (USD/yr)"
    labels = ["Your\nCurrent","Market Rate\n(Your Profile)","With Top\nSkill"]
    colors = [T3, CYN, LIM]
    fig, ax = dfig(8,4.5)
    ax.grid(axis="x",alpha=0)
    ax.grid(axis="y",color=BDR,alpha=0.35,linestyle="--",linewidth=0.4)
    for i,(lbl,val,col) in enumerate(zip(labels,vals,colors)):
        ax.bar(i, val, color=col, width=0.48, edgecolor="none", alpha=0.9, zorder=3)
        ax.bar(i, val*0.06, bottom=val*0.94, color="white",
               width=0.48, alpha=0.14, edgecolor="none", zorder=4)
        ax.text(i, val+max(vals)*.015, fmt(val),
                ha="center", color=T1, fontsize=10, fontweight="700")
    ax.set_xticks(range(3)); ax.set_xticklabels(labels, color=T2)
    ax.set_ylabel(ylabel, color=T2); ax.set_ylim(0, max(vals)*1.2)
    ax.set_title("Salary Reality Check", color=T1, fontsize=12, fontweight="700", pad=12)
    plt.tight_layout()
    return fig

def viz_career_paths(paths, country):
    colors = [CYN, IND, LIM]
    fig = go.Figure()
    for i,p in enumerate(paths):
        yrs  = list(range(p["timeline_years"]+1))
        sals = [p["salary_now"]+(p["salary_then"]-p["salary_now"])*(y/p["timeline_years"])
                for y in yrs]
        fig.add_trace(go.Scatter(
            x=yrs, y=sals, mode="lines+markers", name=p["type"],
            line=dict(color=colors[i%3], width=3.5),
            marker=dict(size=8, color=colors[i%3], line=dict(color=BG,width=2)),
            hovertemplate=f"<b>{p['type']}</b><br>Year %{{x}}: "
                          f"{'₹' if country=='India' else '$'}%{{y:,.0f}}"
                          f"{'L' if country=='India' else ''}<extra></extra>",
        ))
        fig.add_annotation(x=p["timeline_years"], y=p["salary_then"],
            text=f"<b>{'₹' if country=='India' else '$'}{p['salary_then']:,.0f}"
                 f"{'L' if country=='India' else ''}</b>",
            showarrow=False, xshift=10,
            font=dict(color=colors[i%3], size=11))
    fig.update_layout(
        title=dict(text="Career Path Salary Projections",
                   font=dict(color=T1,size=13,family="Space Grotesk")),
        paper_bgcolor=BG, plot_bgcolor=C['card2'],
        font=dict(family="Inter",color=T2),
        xaxis=dict(title="Years from now",gridcolor=BDR,color=T2,
                   showline=True,linecolor=BDR,dtick=1),
        yaxis=dict(title=f"Salary ({'LPA' if country=='India' else 'USD'})",
                   gridcolor=BDR,color=T2),
        legend=dict(bgcolor=CARD,bordercolor=BDR,borderwidth=1,font=dict(color=T2)),
        hovermode="x unified",height=390,
        margin=dict(l=10,r=20,t=45,b=10),
    )
    return fig

def viz_authenticity(red_flags, signals):
    items = [("✗  "+f,ROSE) for f in red_flags]+[("✓  "+s,LIM) for s in signals]
    if not items:
        fig,ax = dfig(8,2); ax.text(.5,.5,"All clean!",ha="center",color=LIM,
                                    transform=ax.transAxes,fontsize=12); return fig
    fig,ax = dfig(10, max(3, len(items)*.44))
    ax.grid(axis="y",alpha=0)
    for i,(lbl,col) in enumerate(items):
        _glow_bar(ax, i, 1, 0, 0.6, col, alpha=0.55)
        ax.text(.025, i, lbl, va="center", fontsize=9, color=T1)
    ax.set_yticks([]); ax.set_xticks([])
    ax.set_title("Authenticity Analysis", color=T1, fontsize=11, fontweight="700", pad=12)
    plt.tight_layout()
    return fig

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ✦ Resume AI")
    st.markdown(f"<span style='color:{T3};font-size:.7rem;font-family:\"JetBrains Mono\",monospace'>"
                f"Career Intelligence Platform v4</span>", unsafe_allow_html=True)

    # API status
    api_ok = ensure_api()
    dot_cls = "api-on" if api_ok else "api-off"
    status_txt = "Salary Engine Online" if api_ok else "Salary Engine Offline (fallback)"
    st.markdown(f'<div class="api-status"><div class="api-dot {dot_cls}"></div>'
                f'<span style="color:{"#84CC16" if api_ok else "#F43F5E"}">{status_txt}</span></div>',
                unsafe_allow_html=True)
    st.divider()

    # ── Upload ────────────────────────────────────────────────────
    st.markdown(f'<span class="sb-lbl">📄 Resume Upload</span>', unsafe_allow_html=True)
    uploaded = st.file_uploader("resume", type=["pdf","docx","txt"],
                                label_visibility="collapsed",
                                help="PDF, DOCX, or TXT. Stays local — never uploaded to servers.")
    st.divider()

    # ── Country + Role ────────────────────────────────────────────
    st.markdown(f'<span class="sb-lbl">🌍 Country & Target Role</span>', unsafe_allow_html=True)
    country = st.selectbox("Country",
        ["India","USA","UK","Germany","Canada","Australia","Singapore","UAE","Remote","Other"],
        label_visibility="collapsed")
    sel_cat = st.selectbox("Category", list(ROLE_CATEGORIES.keys()),
                           label_visibility="collapsed")
    target_role = st.selectbox("Role", ROLE_CATEGORIES[sel_cat],
                               label_visibility="collapsed")
    st.divider()

    # ── User info ─────────────────────────────────────────────────
    st.markdown(f'<span class="sb-lbl">👤 Your Profile</span>', unsafe_allow_html=True)
    user_name      = st.text_input("Full name",   placeholder="e.g. Priya Sharma",
                                   label_visibility="collapsed")
    current_role   = st.text_input("Current job title", placeholder="e.g. Data Analyst",
                                   label_visibility="collapsed")
    current_salary_inp = st.text_input(
        "Current salary", placeholder="e.g. 8 LPA  or  $85,000",
        label_visibility="collapsed",
        help="Enter as '8 LPA' for India or '$85000' for USD")
    user_email     = st.text_input("Email (for history)", placeholder="you@email.com",
                                   label_visibility="collapsed")
    st.divider()

    # ── Profile links + save ──────────────────────────────────────
    st.markdown(f'<span class="sb-lbl">🔗 Profile Links</span>', unsafe_allow_html=True)
    github_url    = st.text_input("GitHub",    placeholder="https://github.com/you",
                                  label_visibility="collapsed")
    portfolio_url = st.text_input("Portfolio", placeholder="https://yoursite.com",
                                  label_visibility="collapsed")
    linkedin_url  = st.text_input("LinkedIn",  placeholder="https://linkedin.com/in/you",
                                  label_visibility="collapsed")

    if st.button("💾  Save Links to Database", use_container_width=True):
        errs = []
        for url, kind in [(github_url,"github"),(linkedin_url,"linkedin"),
                          (portfolio_url,"portfolio")]:
            ok, msg = validate_url(url, kind)
            if not ok: errs.append(msg)
        if errs:
            for e in errs: st.error(e, icon="⚠️")
        elif not any([github_url, portfolio_url, linkedin_url]):
            st.info("Enter at least one link.")
        else:
            try:
                sid = save_submission(
                    name=user_name or "—", email=user_email or "—",
                    github_url=github_url, portfolio_url=portfolio_url,
                    linkedin_url=linkedin_url, target_role=target_role,
                    strength_score=st.session_state.get("strength",0),
                    quality_score=st.session_state.get("quality_score",0),
                    skills_detected=st.session_state.get("detected_skills",[]),
                )
                st.success(f"✅ Saved! Submission #{sid}")
            except Exception as ex:
                st.error(f"Save failed: {ex}")

    # Show saved links
    saved_links = [(ico,url) for ico,url in [("🐙",github_url),("🌐",portfolio_url),("💼",linkedin_url)] if url]
    if saved_links:
        for ico, url in saved_links:
            short = url.replace("https://","").replace("http://","")[:30]
            st.markdown(f'<div class="link-card"><span class="link-icon">{ico}</span>'
                        f'<span class="link-url">{short}</span></div>', unsafe_allow_html=True)
    st.divider()

    # ── Analysis snapshot (shown after upload) ────────────────────
    if st.session_state.get("snap"):
        snap = st.session_state["snap"]
        st.markdown(f'<span class="sb-lbl">📊 Analysis Snapshot</span>',unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sb-card">
          <div class="sb-stat">
            <span class="sb-stat-k">Quality</span>
            <span class="sb-stat-v">{snap['quality']}/100</span>
          </div>
          <div class="sb-stat">
            <span class="sb-stat-k">Strength</span>
            <span class="sb-stat-v">{snap['strength']}/100</span>
          </div>
          <div class="sb-stat">
            <span class="sb-stat-k">Skills</span>
            <span class="sb-stat-v">{snap['skills']}</span>
          </div>
          <div class="sb-stat">
            <span class="sb-stat-k">Experience</span>
            <span class="sb-stat-v">{snap['exp']}y</span>
          </div>
          <div class="sb-stat">
            <span class="sb-stat-k">Salary Est.</span>
            <span class="sb-stat-v">{snap['salary']}</span>
          </div>
          <div style="margin-top:.4rem">
            <span class="sb-badge {"badge-ok" if snap["strength"]>=65
                                    else "badge-warn" if snap["strength"]>=42
                                    else "badge-bad"}">
              {"Full Analysis" if snap["strength"]>=65
               else "Developing" if snap["strength"]>=42
               else "Build-Up Mode"}
            </span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.divider()

    # ── PDF Download ──────────────────────────────────────────────
    if st.session_state.get("report_bytes"):
        st.markdown(f'<span class="sb-lbl">📥 Download Report</span>',unsafe_allow_html=True)
        st.download_button(
            label="📄  Download Full PDF Report",
            data=st.session_state["report_bytes"],
            file_name=f"resumeai_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption("Includes salary estimate, skill gaps, action plan & career paths.")
    st.divider()
    st.caption(f"Salary data · Glassdoor · AmbitionBox · levels.fyi · 2025")

# ══════════════════════════════════════════════════════════════════════
# LANDING
# ══════════════════════════════════════════════════════════════════════
if uploaded is None:
    st.markdown(f"""
    <div class="hero">
      <h1>✦ Resume AI</h1>
      <p style="color:{T2};margin:.35rem 0 0;font-size:.9rem">
        Genuine salary estimates · skill gap analysis · career path projections
      </p>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col,icon,title,desc,col_a in zip(
        [c1,c2,c3,c4],
        ["🎯","💰","📊","📈"],
        ["Accurate Salary","Skill Gap","Quality Score","Career Paths"],
        ["Real 2025 data, not synthetic. Fresher ₹4–8 LPA, Senior ₹30–55 LPA.",
         "Exactly which skills you need. Ranked by demand %.",
         "6-dimension scoring. Radar chart + subscores.",
         "3 projection scenarios with salary milestones."],
        [CYN,IND,VIO,LIM],
    ):
        with col:
            st.markdown(f"""
            <div style="background:{C['card']};border:1px solid {C['bdr']};
                        border-top:2px solid {col_a};border-radius:12px;
                        padding:1rem 1.1rem;margin-bottom:.5rem">
              <div style="font-size:1.4rem;margin-bottom:.3rem">{icon}</div>
              <div style="color:{T1};font-weight:600;font-size:.88rem;
                          font-family:'Space Grotesk',sans-serif">{title}</div>
              <div style="color:{T3};font-size:.74rem;margin-top:.22rem;
                          line-height:1.5">{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.info("👈 Upload your resume in the sidebar. "
            "You can save GitHub/portfolio links anytime — even without uploading.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# PARSE & ANALYSE
# ══════════════════════════════════════════════════════════════════════
with st.spinner("📄 Reading resume..."):
    try:
        uploaded.seek(0)
        parsed = parse_resume(uploaded, filename_hint=uploaded.name)
    except Exception as e:
        st.error(f"❌ Parse failed: {e}"); st.stop()
    for w in parsed.get("parse_warnings",[]): st.warning(f"⚠️ {w}")

with st.spinner("🔬 Running analysis..."):
    skills_result  = extract_skills(parsed["raw_text"])
    quality_result = analyze_quality(parsed)
    auth_result    = analyze_authenticity(parsed)
    role_gap       = analyze_role_gap(target_role, skills_result["skills"])
    role_gap["role"] = target_role

    role_for_sal = current_role or (parsed["job_titles"][0]
                                    if parsed["job_titles"] else "software engineer")
    exp_years = parsed["years_experience"] or 0

    # ── FastAPI salary (accurate) ─────────────────────────────────
    sal_api = api_salary(role_for_sal, exp_years, country, skills_result["skills"])

    if sal_api:
        unit = sal_api["unit"]    # "LPA" or "USD/yr"
        sal_low  = sal_api["low"]
        sal_mid  = sal_api["mid"]
        sal_high = sal_api["high"]
        sal_level= sal_api["level"]
        sal_notes= sal_api["notes"]
        sal_sources=sal_api["sources"]
        sal_bonus_pct = sal_api["skill_bonus_pct"]
        using_api = True
    else:
        # Fallback to calibrator
        from ml_models import load_real_datasets, train_salary_model, predict_salary
        @st.cache_resource(show_spinner=False)
        def get_model():
            return train_salary_model(load_real_datasets())
        pipe = get_model()
        raw_pred   = predict_salary(pipe, role_for_sal, exp_years,
                                    len(skills_result["skills"]) or 5, "Medium",
                                    country, estimate_experience_level(exp_years))
        cal = calibrate_salary(raw_pred, role_for_sal, country, exp_years)
        if country == "India":
            unit     = "LPA"
            sal_low  = round(cal["salary_low_usd"]*83/100000, 1)
            sal_mid  = round(cal["salary_mid_usd"]*83/100000, 1)
            sal_high = round(cal["salary_high_usd"]*83/100000, 1)
        else:
            unit     = "USD/yr"
            sal_low  = cal["salary_low_usd"]
            sal_mid  = cal["salary_mid_usd"]
            sal_high = cal["salary_high_usd"]
        sal_level  = estimate_experience_level(exp_years)
        sal_notes  = cal.get("notes", [])
        sal_sources= ["Glassdoor 2025","AmbitionBox","levels.fyi"]
        sal_bonus_pct = 0
        using_api  = False

    skill_roi    = calculate_skill_roi(skills_result["skills"], None,
                                       sal_mid if unit!="LPA" else sal_mid/83*100000)
    career_paths = suggest_paths(role_for_sal, skills_result["skills"],
                                 sal_mid if unit!="LPA" else sal_mid/83*100000)

strength = profile_strength(parsed, skills_result, quality_result)
is_weak  = strength < THRESHOLD
is_warn  = THRESHOLD <= strength < WARNING

# Parse current salary input
def parse_current_salary(txt, country):
    if not txt: return 0
    txt = txt.upper().replace(",","").replace(" ","")
    if "LPA" in txt:
        try: return float(txt.replace("LPA","").replace("₹",""))
        except: return 0
    nums = re.findall(r"[\d.]+", txt)
    if nums:
        v = float(nums[0])
        return v if v < 200 else v/83/100000 if country=="India" else v
    return 0

current_sal_val = parse_current_salary(current_salary_inp, country)

# ── Stash for sidebar ─────────────────────────────────────────────
sal_display = (f"₹{sal_mid} LPA" if unit=="LPA" else f"${sal_mid:,.0f}")
st.session_state["snap"] = dict(
    quality=quality_result["overall_score"], strength=strength,
    skills=len(skills_result["skills"]), exp=exp_years, salary=sal_display,
)
st.session_state["quality_score"]   = quality_result["overall_score"]
st.session_state["strength"]        = strength
st.session_state["detected_skills"] = skills_result["skills"]

# ── Generate PDF ──────────────────────────────────────────────────
try:
    # Convert to USD for report
    if unit == "LPA":
        cal_for_report = dict(
            salary_low_usd=sal_low/83*100000,
            salary_mid_usd=sal_mid/83*100000,
            salary_high_usd=sal_high/83*100000,
            confidence="high" if using_api else "medium",
        )
    else:
        cal_for_report = dict(
            salary_low_usd=sal_low, salary_mid_usd=sal_mid,
            salary_high_usd=sal_high, confidence="high" if using_api else "medium"
        )
    st.session_state["report_bytes"] = generate_report(
        name=parsed.get("name") or user_name or parsed.get("email","Candidate"),
        role=role_for_sal, country=country, parsed=parsed,
        quality_result=quality_result, auth_result=auth_result,
        calibrated=cal_for_report, skill_roi=skill_roi,
        role_gap=role_gap, career_paths=career_paths,
        skills_result=skills_result, strength=strength,
        target_role=target_role, is_weak=is_weak,
    )
except Exception: st.session_state["report_bytes"] = None

def fmt_sal(v):
    if unit == "LPA": return f"₹{v:.1f} LPA"
    return f"${v:,.0f}"

# ══════════════════════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════════════════════
detected_title = (parsed["job_titles"][0].title()
                  if parsed["job_titles"] else role_for_sal.title())
display_name = parsed.get("name") or user_name or None
st.markdown(f"""
<div class="hero" style="padding:.95rem 1.5rem">
  <span style="color:{T3};font-size:.65rem;font-weight:700;
               letter-spacing:.12em;text-transform:uppercase">Analysis Complete</span>
  <h1 style="font-size:1.25rem;margin-top:.15rem">{detected_title}</h1>
  {f'<div style="color:{T3};font-size:.85rem;margin-top:.1rem">{display_name}</div>' if display_name else ''}
</div>""", unsafe_allow_html=True)

m0,m1,m2,m3,m4,m5,m6 = st.columns(7)
with m0: st.metric("👤 Name",    parsed.get("name") or "Not found")
with m1: st.metric("📧 Email",   parsed["email"] or "—")
with m2: st.metric("📞 Phone",   "✓" if parsed["phone"] else "Missing")
with m3: st.metric("💼 Exp",     f"{exp_years}y")
with m4: st.metric("🛠 Skills",  len(skills_result["skills"]))
with m5: st.metric("📊 Quality", f"{quality_result['overall_score']}/100")
with m6: st.metric("💪 Strength",f"{strength}/100")

if parsed.get("github") or parsed.get("linkedin"):
    link_html = []
    if parsed.get("github"):
        gh_url = parsed["github"] if parsed["github"].startswith("http") else f"https://{parsed['github']}"
        link_html.append(f'<a href="{gh_url}" target="_blank" style="margin-right:1.2rem">💻 GitHub ↗</a>')
    if parsed.get("linkedin"):
        li_url = parsed["linkedin"] if parsed["linkedin"].startswith("http") else f"https://{parsed['linkedin']}"
        link_html.append(f'<a href="{li_url}" target="_blank">🔗 LinkedIn ↗</a>')
    st.markdown(f'<div style="font-size:.85rem;margin:.3rem 0 .6rem">{"".join(link_html)}</div>',
                unsafe_allow_html=True)

st.divider()

# Gate banners
if is_weak:
    st.markdown(f"""
    <div class="gate gate-weak">
      <div class="gate-title">🚧  Profile Strength {strength}/100 — Needs Content</div>
      <div style="color:{T2};font-size:.83rem;line-height:1.6">
        Resume doesn't have enough content for a reliable salary estimate.
        <strong style="color:{AMB}">Follow the build-up plan below</strong> then re-upload.
      </div>
    </div>""", unsafe_allow_html=True)
elif is_warn:
    st.markdown(f"""
    <div class="gate gate-warn">
      <div class="gate-title">⚠️  Profile Strength {strength}/100 — Developing</div>
      <div style="color:{T2};font-size:.83rem;line-height:1.6">
        Salary shown is <strong style="color:{AMB}">approximate</strong> — 
        add more skills & experience detail for higher accuracy.
      </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# WEAK PROFILE — BUILD-UP MODE
# ══════════════════════════════════════════════════════════════════════
if is_weak:
    tab1,tab2,tab3 = st.tabs(["📋 Build Your Profile","🎯 Skills Roadmap","📊 Quality"])

    with tab1:
        checks  = essentials_check(parsed, skills_result)
        missing = [l for l,ok in checks if not ok]
        st.markdown(f'<div class="sh">✅ Profile Essentials Checklist</div>',unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        for i,(lbl,ok) in enumerate(checks):
            (c1 if i%2==0 else c2).markdown(
                f'<div class="ci {"ci-g" if ok else "ci-r"}">'
                f'{"✅" if ok else "❌"}  {lbl}</div>', unsafe_allow_html=True)

        if skills_result["skills"]:
            st.divider()
            st.markdown(f'<div class="sh">🛠 Skills Detected</div>',unsafe_allow_html=True)
            st.markdown(" ".join(f'<span class="pill p-c">{s.title()}</span>'
                                 for s in skills_result["skills"]),unsafe_allow_html=True)
        else:
            st.divider()
            st.warning("No recognised skills found. Add a **Skills** section "
                       "(Python, SQL, Excel, Figma, etc.).")

        if missing:
            st.divider()
            st.markdown(f'<div class="sh">🔧 Step-by-Step Fix Plan</div>',unsafe_allow_html=True)
            fixes = {
                "📧 Email address":       ("Add at the very top of resume.","yourname@gmail.com"),
                "📞 Phone number":        ("Add next to email.","+91-XXXXX-XXXXX"),
                "🔗 LinkedIn profile":    ("Create LinkedIn, paste URL in header.","linkedin.com → Sign up → copy URL"),
                "💻 GitHub profile":      ("Create GitHub, upload ≥1 project.","github.com → New repository → upload code"),
                "🌐 Portfolio / website": ("Free portfolio via GitHub Pages.","Search 'GitHub Pages tutorial' — 30 min"),
                "📝 Professional summary":("3-line summary at top.",
                                          "'X-year [role] skilled in [top 3]. Built [achievement]. Seeking [target].'"),
                "🎓 Education section":   ("Degree, institution, year.","Add expected year if still studying."),
                "💼 Experience / Projects":("Internships, freelance, or projects.","No job? Use 'Project Experience'."),
                "🛠 Skills section":      ("List every tool you know.","Languages, frameworks, databases, tools."),
                "📊 Quantified impact":   ("Add numbers to your bullet points.","E.g. 'Reduced load time by 40%' or 'Built for 500 users'"),
            }
            for i,label in enumerate(missing, 1):
                detail, tip = fixes.get(label, ("Add this to your resume.",""))
                st.markdown(f"""<div class="rm-step">
                  <div class="rm-num">{i}</div>
                  <div><div class="rm-title">{label}</div>
                  <div class="rm-desc">{detail}<br>
                  <span class="rm-link">{tip}</span></div></div></div>""",unsafe_allow_html=True)

    with tab2:
        st.markdown(f'<div class="sh">🎯 Skills Roadmap for {target_role.title()}</div>',unsafe_allow_html=True)
        st.pyplot(viz_skills_demand(role_gap))
        if role_gap.get("required_missing"):
            st.divider()
            st.markdown(f'<div class="sh">🔴 Critical Skills — Learn First</div>',unsafe_allow_html=True)
            for i,sk in enumerate(role_gap["required_missing"][:8],1):
                d = SKILLS_DB.get(sk,{}).get("demand",0.7)*100
                cat = SKILLS_DB.get(sk,{}).get("category","").replace("_"," ").title()
                st.markdown(f"""<div class="rm-step">
                  <div class="rm-num">{i}</div>
                  <div><div class="rm-title">{sk.title()}
                    <span style="color:{T3};font-weight:400;font-size:.72rem"> — {cat} · {d:.0f}% demand</span>
                  </div>
                  <div class="rm-desc">Learn free:
                    <a class="rm-link" href="https://youtube.com/results?search_query={sk.replace(' ','+')}+tutorial" target="_blank">YouTube</a> ·
                    <a class="rm-link" href="https://coursera.org/search?query={sk.replace(' ','+')}" target="_blank">Coursera</a> ·
                    <a class="rm-link" href="https://freecodecamp.org/news/search/?query={sk.replace(' ','+')}" target="_blank">freeCodeCamp</a>
                  </div></div></div>""", unsafe_allow_html=True)
        if role_gap.get("preferred_missing"):
            st.divider()
            st.markdown(f'<div class="sh">🟡 Then Add These</div>',unsafe_allow_html=True)
            st.markdown(" ".join(f'<span class="pill p-a">{s.title()}</span>'
                                 for s in role_gap["preferred_missing"][:10]),unsafe_allow_html=True)

    with tab3:
        sc = quality_result["overall_score"]
        col_s = LIM if sc>=75 else AMB if sc>=55 else ROSE
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1.1rem;margin-bottom:1rem">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:3rem;
                      font-weight:800;color:{col_s};line-height:1">{sc}</div>
          <div>
            <div style="color:{T1};font-weight:600;font-size:1rem">/ 100 Quality Score</div>
            <div style="color:{T3};font-size:.79rem">Add more content to unlock full analysis</div>
          </div>
        </div>""", unsafe_allow_html=True)
        q1,q2 = st.columns([1,1])
        with q1: st.pyplot(viz_quality_radar(quality_result["subscores"]))
        with q2:
            for k,v in quality_result["subscores"].items():
                bc = LIM if v>=75 else AMB if v>=50 else ROSE
                st.markdown(f"""<div style="margin-bottom:.5rem">
                  <div style="display:flex;justify-content:space-between;margin-bottom:.18rem">
                    <span style="color:{T2};font-size:.82rem">{k.replace('_',' ').title()}</span>
                    <span style="color:{bc};font-weight:600;font-size:.82rem">{v}/100</span>
                  </div></div>""", unsafe_allow_html=True)
                st.progress(v/100)

# ══════════════════════════════════════════════════════════════════════
# STRONG / WARN — FULL ANALYSIS
# ══════════════════════════════════════════════════════════════════════
else:
    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "💰 Salary","🎯 Role Gap","📊 Quality",
        "📈 Career Path","🔍 Authenticity","📋 Action Plan",
    ])

    # ── SALARY ─────────────────────────────────────────────────────
    with tab1:
        if is_warn:
            st.info("⚠️ Estimate is approximate — more skills & experience needed for precision.")
        if not using_api:
            st.warning("Salary engine offline — using fallback calibration (less accurate).")

        # BIG salary display
        st.markdown(f"""
        <div class="sal-band">
          <div style="text-align:center">
            <div class="sal-num">{fmt_sal(sal_low)}</div>
            <div class="sal-label">Lower Band</div>
          </div>
          <div class="sal-sep">—</div>
          <div class="sal-mid" style="text-align:center">
            <div class="sal-num">{fmt_sal(sal_mid)}</div>
            <div class="sal-label" style="color:{CYN}">Median · {sal_level[:12]}</div>
          </div>
          <div class="sal-sep">—</div>
          <div style="text-align:center">
            <div class="sal-num">{fmt_sal(sal_high)}</div>
            <div class="sal-label">Upper Band</div>
          </div>
        </div>""", unsafe_allow_html=True)

        s1,s2,s3 = st.columns(3)
        with s1: st.metric("📍 Level", sal_level[:20])
        with s2: st.metric("🌍 Country", country)
        with s3:
            top_roi = skill_roi[0]["salary_uplift_usd"] if skill_roi else 0
            boost = (f"+₹{top_roi*83/100000:.0f} LPA" if unit=="LPA"
                     else f"+${top_roi:,.0f}/yr")
            st.metric("🚀 Top Skill Boost", boost,
                      help=skill_roi[0]["skill"].title() if skill_roi else "")

        st.divider()
        st.markdown(f'<div class="sh">📊 Salary Gauge</div>',unsafe_allow_html=True)
        st.pyplot(viz_salary_gauge(sal_low, sal_mid, sal_high, unit, sal_level))

        # Skill bonus callout
        if sal_bonus_pct > 0:
            st.success(f"🚀 Your skills add **{sal_bonus_pct:.0f}% above base** salary for this role.")

        # Current salary comparison
        if current_sal_val > 0:
            st.divider()
            cur_display = (f"₹{current_sal_val} LPA" if unit=="LPA"
                           else f"${current_sal_val:,.0f}")
            delta = sal_mid - current_sal_val
            delta_pct = (delta/current_sal_val)*100 if current_sal_val else 0
            if delta > current_sal_val*.15:
                st.warning(f"⚠️ You're earning **{fmt_sal(abs(delta))} below market**. "
                           f"That's {delta_pct:.0f}% gap. Time to negotiate or switch.")
            elif delta < -current_sal_val*.15:
                st.success(f"✅ You're earning **above market rate** by {abs(delta_pct):.0f}%. Well done!")
            else:
                st.info(f"✅ Your salary ({cur_display}) aligns with market expectations.")
            st.pyplot(viz_salary_compare(current_sal_val, sal_mid,
                      (top_roi*83/100000 if unit=="LPA" else top_roi), country))

        with st.expander("ℹ️  Salary calculation details"):
            st.markdown(f"""
            | Detail | Value |
            |--------|-------|
            | Engine | {"FastAPI Rule-Based Engine v2" if using_api else "ML Fallback"} |
            | Experience tier | {sal_level} |
            | Skill bonus | {sal_bonus_pct:.0f}% |
            | Country | {country} |
            | Confidence | {"HIGH" if using_api else "MEDIUM"} |
            """)
            for n in sal_notes: st.caption(f"• {n}")
            st.caption("Sources: " + " · ".join(sal_sources))

        if skill_roi:
            st.divider()
            st.markdown(f'<div class="sh">💡 Skill → Salary Impact</div>',unsafe_allow_html=True)
            st.pyplot(viz_skill_roi(skill_roi, country))

    # ── ROLE GAP ───────────────────────────────────────────────────
    with tab2:
        score = role_gap.get("match_score", 0)
        bc    = "mb-hi" if score>=75 else "mb-md" if score>=50 else "mb-lo"

        r1,r2,r3 = st.columns([1,2,2])
        with r1:
            st.markdown(f"""<div style="text-align:center;padding:.6rem 0">
              <div class="mbadge {bc}">{int(score)}</div>
              <div style="color:{T2};font-size:.7rem;margin-top:.35rem">Match Score</div>
            </div>""", unsafe_allow_html=True)
        with r2:
            st.metric("Required Skills",
                      f"{len(role_gap.get('required_have',[]))}/{role_gap.get('total_required',0)}")
            st.metric("Preferred Skills", len(role_gap.get("preferred_have",[])))
        with r3:
            st.metric("Salary if You Land This Role",
                      f"{fmt_sal(sal_low)} – {fmt_sal(sal_high)}")

        st.markdown(f"*{role_gap.get('description','')}*")
        st.divider()
        st.markdown(f'<div class="sh">📊 Skills Demand Chart</div>',unsafe_allow_html=True)
        st.pyplot(viz_skills_demand(role_gap))

        st.divider()
        cl,cr = st.columns(2)
        with cl:
            if role_gap.get("required_missing"):
                st.markdown("**🔴 Critical Missing**")
                st.markdown(" ".join(f'<span class="pill p-r">{s.title()}</span>'
                                     for s in role_gap["required_missing"]),unsafe_allow_html=True)
        with cr:
            if role_gap.get("required_have"):
                st.markdown("**✅ Required — You Have**")
                st.markdown(" ".join(f'<span class="pill p-g">{s.title()}</span>'
                                     for s in role_gap["required_have"]),unsafe_allow_html=True)

        if role_gap.get("recommendations"):
            st.divider()
            st.markdown(f'<div class="sh">📋 Prioritised Recommendations</div>',unsafe_allow_html=True)
            for i,rec in enumerate(role_gap["recommendations"][:8],1):
                d   = SKILLS_DB.get(rec["skill"],{}).get("demand",0)*100
                cls = "ci-r" if rec["priority"]=="critical" else "ci-a"
                badge = "🔴" if rec["priority"]=="critical" else "🟡"
                st.markdown(
                    f'<div class="ci {cls}">{badge} <strong>{i}. {rec["skill"].title()}</strong>'
                    f' <span style="color:{T3};font-size:.73rem">[{d:.0f}% demand]</span>'
                    f' — {rec["reason"]}</div>', unsafe_allow_html=True)

    # ── QUALITY ────────────────────────────────────────────────────
    with tab3:
        sc = quality_result["overall_score"]
        col_s = LIM if sc>=75 else AMB if sc>=55 else ROSE
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1rem">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:3.2rem;
                      font-weight:800;color:{col_s};line-height:1">{sc}</div>
          <div>
            <div style="color:{T1};font-weight:600;font-size:1.1rem">/ 100 Quality Score</div>
            <div style="color:{T3};font-size:.79rem">
              {'Excellent — your resume stands out' if sc>=80
               else 'Good — a few improvements needed' if sc>=65
               else 'Needs work — follow action plan'}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        q1,q2 = st.columns([1,1])
        with q1: st.pyplot(viz_quality_radar(quality_result["subscores"]))
        with q2:
            for k,v in quality_result["subscores"].items():
                bc = LIM if v>=75 else AMB if v>=50 else ROSE
                st.markdown(f"""<div style="margin-bottom:.55rem">
                  <div style="display:flex;justify-content:space-between;margin-bottom:.18rem">
                    <span style="color:{T2};font-size:.83rem">{k.replace('_',' ').title()}</span>
                    <span style="color:{bc};font-weight:600;font-size:.83rem">{v}/100</span>
                  </div></div>""", unsafe_allow_html=True)
                st.progress(v/100)
            st.divider()
            stats = quality_result.get("stats",{})
            for lbl,val in [("Bullet points",stats.get("bullet_count","—")),
                            ("Strong verbs",stats.get("strong_verbs","—")),
                            ("Quantified",f"{stats.get('quantified_pct',0)}%"),
                            ("Fluff phrases",stats.get("fluff_count","—"))]:
                st.markdown(f"""<div style="display:flex;justify-content:space-between;
                                padding:.26rem 0;border-bottom:1px solid {BDR}">
                  <span style="color:{T2};font-size:.8rem">{lbl}</span>
                  <span style="color:{T1};font-weight:600;font-size:.8rem;
                    font-family:'JetBrains Mono',monospace">{val}</span>
                </div>""", unsafe_allow_html=True)

    # ── CAREER PATH ────────────────────────────────────────────────
    with tab4:
        st.plotly_chart(viz_career_paths(career_paths, country), use_container_width=True)
        st.divider()
        for i,p in enumerate(career_paths):
            clrs = [CYN,IND,LIM]
            now_s  = (f"₹{p['salary_now']*83/100000:.0f} LPA" if unit=="LPA"
                      else f"${p['salary_now']:,.0f}")
            then_s = (f"₹{p['salary_then']*83/100000:.0f} LPA" if unit=="LPA"
                      else f"${p['salary_then']:,.0f}")
            with st.expander(f"**{p['type']}** — {p.get('title','')}"):
                pc1,pc2,pc3 = st.columns(3)
                with pc1: st.metric("Now", now_s)
                with pc2: st.metric(f"In {p['timeline_years']}y", then_s,
                                    delta=f"{((p['salary_then']/max(p['salary_now'],1))-1)*100:+.0f}%")
                with pc3:
                    sk = ", ".join(p.get("skills_needed",[])[:3]) or "Deepen current"
                    st.markdown(f"**Skills to add:**<br>{sk}", unsafe_allow_html=True)

    # ── AUTHENTICITY ───────────────────────────────────────────────
    with tab5:
        auth_score = auth_result["authenticity_score"]
        ac = LIM if auth_score>=80 else AMB if auth_score>=60 else ROSE
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1rem">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:3.2rem;
                      font-weight:800;color:{ac};line-height:1">{auth_score}</div>
          <div>
            <div style="color:{T1};font-weight:600;font-size:1.1rem">/ 100 Authenticity</div>
            <div style="color:{T3};font-size:.79rem">
              {'Genuine and credible' if auth_score>=80
               else 'Some concerns — check red flags' if auth_score>=60
               else 'Multiple red flags — recruiters may question this'}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.pyplot(viz_authenticity(auth_result["red_flags"],auth_result["credibility_signals"]))
        a1,a2 = st.columns(2)
        with a1:
            st.markdown("**🚩 Red Flags**")
            for f in auth_result["red_flags"]:
                st.markdown(f'<div class="ci ci-r">❌  {f}</div>',unsafe_allow_html=True)
            if not auth_result["red_flags"]: st.success("None found — great!")
        with a2:
            st.markdown("**✅ Credibility Signals**")
            for s in auth_result["credibility_signals"]:
                st.markdown(f'<div class="ci ci-g">✓  {s}</div>',unsafe_allow_html=True)

    # ── ACTION PLAN ────────────────────────────────────────────────
    with tab6:
        st.markdown(f'<div class="sh">📋 Personalised Action Plan</div>',unsafe_allow_html=True)

        checks = essentials_check(parsed, skills_result)
        missing_ess = [l for l,ok in checks if not ok]
        if missing_ess:
            st.markdown("**🔗 Missing Profile Essentials — Fix First**")
            for lbl in missing_ess:
                st.markdown(f'<div class="ci ci-r">□  {lbl}</div>',unsafe_allow_html=True)
            st.divider()

        ap1,ap2 = st.columns(2)
        with ap1:
            issues = quality_result.get("issues",[]) + auth_result.get("red_flags",[])
            st.markdown("**🚨 Resume Issues**")
            for issue in (issues[:6] or ["No critical issues found ✅"]):
                st.markdown(f'<div class="ci ci-r">□  {issue}</div>',unsafe_allow_html=True)
            st.markdown("<br>**💡 Resume Improvements**",unsafe_allow_html=True)
            for sug in quality_result.get("suggestions",[])[:5]:
                st.markdown(f'<div class="ci ci-g">□  {sug}</div>',unsafe_allow_html=True)

        with ap2:
            st.markdown("**💰 Skills for Salary Growth**")
            for r in skill_roi[:5]:
                up = (f"+₹{r['salary_uplift_usd']*83/100000:.0f} LPA"
                      if unit=="LPA" else f"+${r['salary_uplift_usd']:,.0f}")
                st.markdown(f'<div class="ci ci-c">□  Learn <strong>'
                            f'{r["skill"].title()}</strong> — {up}</div>',unsafe_allow_html=True)
            st.markdown(f"<br>**🎯 Skills for {target_role.title()}**",unsafe_allow_html=True)
            for rec in role_gap.get("recommendations",[])[:5]:
                badge = "🔴" if rec["priority"]=="critical" else "🟡"
                cls   = "ci-r" if rec["priority"]=="critical" else "ci-a"
                st.markdown(f'<div class="ci {cls}">□  {badge} {rec["skill"].title()}'
                            f' — {rec["reason"]}</div>',unsafe_allow_html=True)

        # Save to DB
        if user_email:
            st.divider()
            try:
                aid = save_analysis(current_role or "User", user_email, {
                    "quality":quality_result,"authenticity":auth_result,
                    "salary": {"low":sal_low,"mid":sal_mid,"high":sal_high,"unit":unit},
                    "parsed":parsed,"skills":skills_result,"skill_roi":skill_roi,
                })
                st.success(f"✅ Analysis #{aid} saved to your history.")
            except Exception as e:
                st.caption(f"Could not save: {e}")

# ── FOOTER ────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="text-align:center;padding:.45rem 0">
  <span style="color:{T3};font-size:.72rem;font-family:'JetBrains Mono',monospace">
    ✦ Resume AI v4  ·  FastAPI Salary Engine  ·  Glassdoor · AmbitionBox · levels.fyi 2025
    ·  Estimates only — actual pay varies by company & negotiation
  </span>
</div>""", unsafe_allow_html=True)
