"""
PDF Report Generator
Generates a downloadable career analysis report.
Uses only built-in string ops — no heavy LaTeX deps.
"""
import io, datetime
from fpdf import FPDF


ACCENT  = (79, 139, 249)    # blue
DARK    = (13, 17, 23)
CARD    = (17, 24, 39)
GREEN   = (16, 185, 129)
RED     = (239, 68, 68)
ORANGE  = (245, 158, 11)
PURPLE  = (139, 92, 246)
WHITE   = (249, 250, 251)
GREY    = (107, 114, 128)
LGREY   = (55, 65, 81)


class ReportPDF(FPDF):
    def header(self):
        # Gradient-style top bar
        self.set_fill_color(*ACCENT)
        self.rect(0, 0, 210, 8, "F")
        self.set_fill_color(*PURPLE)
        self.rect(140, 0, 70, 8, "F")

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GREY)
        self.cell(0, 5,
                  f"Resume AI · Generated {datetime.datetime.now().strftime('%d %b %Y %H:%M')} · "
                  f"Salary data: Glassdoor, AmbitionBox, levels.fyi 2025",
                  align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_fill_color(*ACCENT)
        self.rect(10, self.get_y(), 4, 6, "F")
        self.set_x(16)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*WHITE)
        self.cell(0, 6, title, ln=True)
        self.ln(2)

    def kv_row(self, key, value, color=None):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.set_x(12)
        self.cell(55, 6, key)
        self.set_text_color(*(color or WHITE))
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 6, str(value), ln=True)

    def bullet(self, text, color=None):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*(color or (200, 210, 220)))
        self.set_x(14)
        self.cell(5, 5.5, chr(149))
        self.multi_cell(170, 5.5, text)

    def score_bar(self, label, score, max_score=100):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.set_x(12)
        self.cell(60, 5.5, label)
        # bar background
        bx = self.get_x(); by = self.get_y() + 1
        self.set_fill_color(*LGREY)
        self.rect(bx, by, 80, 3.5, "F")
        # bar fill
        fill_w = (score / max_score) * 80
        col = GREEN if score >= 75 else ORANGE if score >= 50 else RED
        self.set_fill_color(*col)
        self.rect(bx, by, fill_w, 3.5, "F")
        # score text
        self.set_x(bx + 82)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.cell(20, 5.5, f"{score}/100", ln=True)


def generate_report(
    name: str,
    role: str,
    country: str,
    parsed: dict,
    quality_result: dict,
    auth_result: dict,
    calibrated: dict,
    skill_roi: list,
    role_gap: dict,
    career_paths: list,
    skills_result: dict,
    strength: int,
    target_role: str,
    is_weak: bool,
) -> bytes:
    """Generate full PDF report and return as bytes."""
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    pdf.set_margins(10, 14, 10)

    # ── COVER ────────────────────────────────────────────────────
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 10, "✦ Resume AI", ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 6, "Career Analysis Report", ln=True, align="C")
    pdf.ln(3)

    # Info box
    pdf.set_fill_color(17, 24, 39)
    pdf.rect(10, pdf.get_y(), 190, 28, "F")
    pdf.set_y(pdf.get_y() + 4)
    info_items = [
        ("Name",    name or "—"),
        ("Role",    role.title()),
        ("Country", country),
        ("Target",  target_role.title()),
        ("Date",    datetime.datetime.now().strftime("%d %b %Y")),
        ("Strength",f"{strength}/100"),
    ]
    pdf.set_font("Helvetica", "", 9)
    for i, (k, v) in enumerate(info_items):
        col = i % 3
        row = i // 3
        x = 14 + col * 64
        y = pdf.get_y() + row * 7 - (7 if row > 0 else 0)
        pdf.set_xy(x, y if row == 0 else y + 4)
        pdf.set_text_color(*GREY)
        pdf.cell(22, 5, k + ":")
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(40, 5, v, ln=(col == 2))
        pdf.set_font("Helvetica", "", 9)
    pdf.ln(10)

    # ── PROFILE SUMMARY ──────────────────────────────────────────
    pdf.section_title("Profile Summary")
    pdf.kv_row("Quality Score",     f"{quality_result['overall_score']}/100")
    pdf.kv_row("Authenticity Score",f"{auth_result['authenticity_score']}/100")
    pdf.kv_row("Profile Strength",  f"{strength}/100")
    pdf.kv_row("Skills Detected",   len(skills_result["skills"]))
    pdf.kv_row("Experience",        f"{parsed.get('years_experience',0)} years")
    pdf.kv_row("Email",             parsed.get("email") or "—")
    pdf.ln(3)

    # ── SALARY (only for strong profiles) ────────────────────────
    if not is_weak:
        pdf.section_title("Salary Estimate")
        mid = calibrated.get("salary_mid_usd", 0)
        lo  = calibrated.get("salary_low_usd", 0)
        hi  = calibrated.get("salary_high_usd", 0)
        if country == "India":
            def lpa(v): return f"₹{v*83/100000:.1f} LPA"
            pdf.kv_row("Salary Range", f"{lpa(lo)} – {lpa(hi)}", GREEN)
            pdf.kv_row("Mid-Point",    lpa(mid), ACCENT)
        else:
            pdf.kv_row("Salary Range", f"${lo:,.0f} – ${hi:,.0f}", GREEN)
            pdf.kv_row("Mid-Point",    f"${mid:,.0f}", ACCENT)
        pdf.kv_row("Confidence", calibrated.get("confidence","medium").upper())
        pdf.ln(3)

        # Skill ROI
        if skill_roi:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*GREY)
            pdf.set_x(12)
            pdf.cell(0, 5, "Top skills to learn for salary growth:", ln=True)
            for r in skill_roi[:5]:
                up = (f"+₹{r['salary_uplift_usd']*83/100000:.0f} LPA"
                      if country=="India" else f"+${r['salary_uplift_usd']:,.0f}")
                pdf.bullet(f"{r['skill'].title()} — {up}", ACCENT)
        pdf.ln(3)

    # ── QUALITY SUBSCORES ─────────────────────────────────────────
    pdf.section_title("Resume Quality Breakdown")
    for k, v in quality_result.get("subscores", {}).items():
        pdf.score_bar(k.replace("_", " ").title(), int(v))
        pdf.ln(1)
    pdf.ln(3)

    # ── ROLE GAP ──────────────────────────────────────────────────
    pdf.section_title(f"Role Gap — {target_role.title()}")
    pdf.kv_row("Match Score", f"{int(role_gap.get('match_score', 0))}/100")
    req_have = role_gap.get("required_have", [])
    req_miss = role_gap.get("required_missing", [])
    if req_have:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*GREEN)
        pdf.set_x(12); pdf.cell(0, 5, "✓ Required skills you have:", ln=True)
        pdf.bullet(", ".join(s.title() for s in req_have), (150, 240, 200))
    if req_miss:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RED)
        pdf.set_x(12); pdf.cell(0, 5, "✗ Critical missing skills:", ln=True)
        pdf.bullet(", ".join(s.title() for s in req_miss), (255, 170, 170))
    pdf.ln(3)

    # Recommendations
    if role_gap.get("recommendations"):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*WHITE)
        pdf.set_x(12); pdf.cell(0, 5, "Prioritised recommendations:", ln=True)
        for i, rec in enumerate(role_gap["recommendations"][:8], 1):
            badge = "🔴" if rec["priority"]=="critical" else "🟡"
            pdf.bullet(f"{i}. {rec['skill'].title()} [{rec['priority'].upper()}] — {rec['reason']}")
    pdf.ln(3)

    # ── CAREER PATHS ──────────────────────────────────────────────
    if not is_weak and career_paths:
        pdf.section_title("Career Path Projections")
        for p in career_paths:
            now_s  = (f"₹{p['salary_now']*83/100000:.0f} LPA" if country=="India"
                      else f"${p['salary_now']:,.0f}")
            then_s = (f"₹{p['salary_then']*83/100000:.0f} LPA" if country=="India"
                      else f"${p['salary_then']:,.0f}")
            growth = ((p["salary_then"]/max(p["salary_now"],1))-1)*100
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*ACCENT)
            pdf.set_x(12)
            pdf.cell(0, 5, f"▸ {p['type']} — {p.get('title','')}", ln=True)
            pdf.kv_row("  Now → In " + str(p["timeline_years"]) + "y",
                       f"{now_s} → {then_s}  ({growth:+.0f}%)")
            if p.get("skills_needed"):
                pdf.bullet("Skills: " + ", ".join(p["skills_needed"][:4]))
            pdf.ln(2)

    # ── ACTION PLAN ───────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("Your Action Plan")

    issues = quality_result.get("issues", []) + auth_result.get("red_flags", [])
    if issues:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RED)
        pdf.set_x(12); pdf.cell(0, 5, "Issues to fix:", ln=True)
        for issue in issues[:8]:
            pdf.bullet("☐  " + issue, (255, 160, 160))
        pdf.ln(2)

    suggestions = quality_result.get("suggestions", [])
    if suggestions:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*GREEN)
        pdf.set_x(12); pdf.cell(0, 5, "Resume improvements:", ln=True)
        for s in suggestions[:6]:
            pdf.bullet("☐  " + s, (150, 240, 200))
        pdf.ln(2)

    if skill_roi:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*ACCENT)
        pdf.set_x(12); pdf.cell(0, 5, "Skills for salary growth:", ln=True)
        for r in skill_roi[:5]:
            up = (f"+₹{r['salary_uplift_usd']*83/100000:.0f} LPA"
                  if country=="India" else f"+${r['salary_uplift_usd']:,.0f}")
            pdf.bullet(f"☐  Learn {r['skill'].title()} — {up}", (150, 200, 255))
        pdf.ln(2)

    for rec in role_gap.get("recommendations", [])[:5]:
        badge = "🔴" if rec["priority"]=="critical" else "🟡"
        pdf.bullet(f"☐  {badge} {rec['skill'].title()} for {target_role.title()} role")

    # ── DETECTED SKILLS ────────────────────────────────────────────
    pdf.ln(4)
    pdf.section_title("Skills Detected in Your Resume")
    skills_txt = ", ".join(s.title() for s in skills_result.get("skills", []))
    if skills_txt:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*WHITE)
        pdf.set_x(12)
        pdf.multi_cell(186, 5.5, skills_txt)
    else:
        pdf.bullet("No recognised skills found. Add a Skills section.")

    missing_txt = ", ".join(s.title() for s in skills_result.get("missing_critical", []))
    if missing_txt:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RED)
        pdf.set_x(12); pdf.cell(0, 5, "High-demand skills you're missing:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*WHITE)
        pdf.set_x(12)
        pdf.multi_cell(186, 5.5, missing_txt)

    # ── AUTHENTICITY ──────────────────────────────────────────────
    pdf.ln(4)
    pdf.section_title("Authenticity Analysis")
    pdf.kv_row("Authenticity Score", f"{auth_result['authenticity_score']}/100")
    for flag in auth_result.get("red_flags", []):
        pdf.bullet("✗ " + flag, (255, 150, 150))
    for sig in auth_result.get("credibility_signals", []):
        pdf.bullet("✓ " + sig, (150, 240, 200))

    # output
    return bytes(pdf.output())
