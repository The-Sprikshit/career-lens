"""
Resume Authenticity Analyzer — detects fluff, contradictions, and
inflated claims. Novel feature most resume tools skip.

Detects:
- Skill-inflation: claiming many senior skills but shallow experience
- Experience-title mismatch: "Senior" in title but only 1 yr exp
- Buzzword density: too many empty phrases
- Repeated phrases: filler content padding
- Vague quantification: numbers without context
"""

import re
from collections import Counter
from typing import Dict, List


def analyze_authenticity(parsed_resume: Dict) -> Dict:
    """
    Returns {
        "authenticity_score": 75,    # 0-100
        "red_flags": [...],
        "credibility_signals": [...],
    }
    """
    text = parsed_resume["raw_text"]
    text_lower = text.lower()
    years_exp = parsed_resume["years_experience"]
    red_flags = []
    credibility_signals = []

    score = 100  # start perfect, deduct

    # ── 1. Skill inflation ───────────────────────────────────────────
    # If resume claims many skills but experience is short, suspicious
    skills_section = parsed_resume["sections"].get("skills", "") + \
                     parsed_resume["sections"].get("technical skills", "")
    n_skills = len([s for s in re.split(r"[,\n;|]", skills_section) if s.strip()])
    if years_exp and years_exp < 3 and n_skills > 15:
        red_flags.append(
            f"Claims {n_skills} skills with only {years_exp} yrs experience "
            f"— looks inflated"
        )
        score -= 15
    elif n_skills >= 5 and n_skills <= 25:
        credibility_signals.append(f"Skill count ({n_skills}) is realistic for the experience")

    # ── 2. Title-vs-experience mismatch ─────────────────────────────
    senior_titles = ["senior", "lead", "principal", "staff", "head", "director", "vp", "chief"]
    junior_titles = ["intern", "junior", "trainee", "associate"]
    claimed_titles = parsed_resume["job_titles"]

    has_senior = any(any(t in title for t in senior_titles) for title in claimed_titles)
    has_junior = any(any(t in title for t in junior_titles) for title in claimed_titles)

    if has_senior and years_exp and years_exp < 3:
        red_flags.append(
            f"Claims senior title with only {years_exp} yrs experience"
        )
        score -= 20
    elif has_senior and years_exp and years_exp >= 5:
        credibility_signals.append("Senior title consistent with experience level")

    # ── 3. Buzzword density ─────────────────────────────────────────
    buzzwords = [
        "passionate", "hardworking", "guru", "ninja", "rockstar",
        "synergy", "disrupt", "thought leader", "best-in-class",
        "world-class", "10x engineer",
    ]
    buzz_count = sum(1 for b in buzzwords if b in text_lower)
    if buzz_count >= 3:
        red_flags.append(f"High buzzword density ({buzz_count} fluff terms)")
        score -= 10 * buzz_count
    elif buzz_count == 0:
        credibility_signals.append("No fluff buzzwords detected")

    # ── 4. Repeated phrases (padding) ───────────────────────────────
    words = re.findall(r"\b[a-z]{4,}\b", text_lower)
    counter = Counter(words)
    padding = [w for w, c in counter.most_common(15) if c > 5 and w not in _STOPWORDS]
    if padding:
        red_flags.append(
            f"Repeated filler words: {', '.join(padding[:5])} "
            f"— resume may be padded"
        )
        score -= 5

    # ── 5. Vague quantification ─────────────────────────────────────
    # e.g., "many", "several", "various" — vague instead of specific
    vague_words = ["many", "several", "various", "some", "a few", "lots of", "numerous"]
    vague_count = sum(1 for v in vague_words if v in text_lower)
    if vague_count >= 3:
        red_flags.append(
            f"Uses vague quantifiers {vague_count}x ('many', 'several', etc.) "
            f"— replace with specific numbers"
        )
        score -= 5

    # ── 6. Action verb consistency ──────────────────────────────────
    # Top resumes use varied verbs; padded ones repeat same verb
    bullet_lines = [l for l in text.split("\n")
                    if l.strip().startswith(("•", "-", "*", "·"))]
    if len(bullet_lines) >= 5:
        first_verbs = []
        for b in bullet_lines:
            # first word of each bullet
            words_b = re.findall(r"[a-zA-Z]+", b)
            if words_b:
                first_verbs.append(words_b[0].lower())
        verb_counts = Counter(first_verbs)
        most_common_verb_count = verb_counts.most_common(1)[0][1] if verb_counts else 0
        if most_common_verb_count > len(bullet_lines) * 0.4:
            red_flags.append(
                f"Bullets start with the same verb {most_common_verb_count}x "
                f"— vary your verbs"
            )
            score -= 10

    score = max(0, min(100, score))

    return {
        "authenticity_score": score,
        "red_flags": red_flags,
        "credibility_signals": credibility_signals,
    }


_STOPWORDS = set("""
the and for with from this that have been will more most into your
their them they are was were but not you all can had her his our out
about just like over such also what when which who how than then
very just also been being have has had do does did could would should
""".split())


if __name__ == "__main__":
    sample = {
        "raw_text": """
        John Doe
        Senior Principal Staff Engineer (2020 - 2023)
        Passionate hardworking ninja rockstar disruptor.
        Many various numerous skills: Python, Java, C++, Rust, Go,
        Scala, Haskell, Elixir, Ruby, PHP, Kotlin, Swift, TypeScript,
        JavaScript, R, MATLAB, Julia, Perl, Lua, Dart, C#, F#, Groovy,
        Bash, SQL, NoSQL, GraphQL, React, Angular, Vue, Svelte, Solid,
        many many many many many many many many many skills.
        """,
        "sections": {"skills": "Python Java C++ Rust Go Scala etc"},
        "years_experience": 1,
        "job_titles": ["Senior Principal Staff Engineer"],
    }
    result = analyze_authenticity(sample)
    print(f"Score: {result['authenticity_score']}/100")
    print(f"Red flags: {result['red_flags']}")
    print(f"Credibility: {result['credibility_signals']}")
