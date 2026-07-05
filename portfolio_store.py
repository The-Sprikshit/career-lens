"""
Portfolio & GitHub Link Storage
Saves user-submitted links to SQLite for later examination.
"""
import sqlite3, datetime, os, re

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio_submissions.db")


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            email       TEXT,
            github_url  TEXT,
            portfolio_url TEXT,
            linkedin_url  TEXT,
            target_role   TEXT,
            strength_score INTEGER,
            quality_score  INTEGER,
            skills_detected TEXT,
            notes       TEXT,
            submitted_at TEXT
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS link_visits (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sub_id  INTEGER,
            link_type TEXT,
            visited_at TEXT
        )""")
        con.commit()


def save_submission(name, email, github_url, portfolio_url, linkedin_url,
                    target_role, strength_score, quality_score,
                    skills_detected, notes=""):
    init_db()
    with _conn() as con:
        cur = con.execute("""
        INSERT INTO submissions
          (name,email,github_url,portfolio_url,linkedin_url,
           target_role,strength_score,quality_score,skills_detected,notes,submitted_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (name, email, github_url, portfolio_url, linkedin_url,
              target_role, strength_score, quality_score,
              ",".join(skills_detected), notes,
              datetime.datetime.now().isoformat()))
        con.commit()
        return cur.lastrowid


def get_all_submissions():
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM submissions ORDER BY submitted_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def validate_url(url: str, kind: str) -> tuple[bool, str]:
    """Basic validation. Returns (ok, message)."""
    if not url:
        return True, ""  # empty is fine
    url = url.strip()
    if kind == "github":
        if re.match(r"https?://github\.com/[A-Za-z0-9_.-]+", url):
            return True, ""
        return False, "Should look like: https://github.com/yourusername"
    if kind == "linkedin":
        if re.match(r"https?://(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", url):
            return True, ""
        return False, "Should look like: https://linkedin.com/in/yourname"
    # portfolio — just check it has http
    if url.startswith("http"):
        return True, ""
    return False, "Include https:// at the start"
