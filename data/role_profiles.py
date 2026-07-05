"""
Role Profiles Database
=======================
Comprehensive profiles for technical AND non-technical roles.
Each profile defines:
- Required skills (must-have to be competitive)
- Preferred skills (nice-to-have, boost chances)
- Soft skills (especially important for mgmt/non-tech roles)
- Salary bands by experience level (USD, then converted)
- Category (technical / non_technical / management)

Salary ranges are based on 2024-2025 market data (levels.fyi,
Glassdoor, LinkedIn, AmbitionBox for India).
"""

# ─────────────────────────────────────────────────────────────────────
# COUNTRY ADJUSTMENTS
# ─────────────────────────────────────────────────────────────────────
# Tech salaries vary dramatically by country. USA is the baseline.
# India is dramatically lower because the "USD" salary in datasets
# is often an INR amount mistakenly labeled as USD.
COUNTRY_ADJUSTMENTS = {
    "USA": 1.00,
    "UK": 0.80,
    "Germany": 0.80,
    "Canada": 0.80,
    "Australia": 0.80,
    "Singapore": 0.90,
    "UAE": 0.80,
    "Remote": 0.95,
    "India": 0.30,   # ← KEY: Indian tech salaries are ~30% of USA equivalent
    "Other": 0.70,
}


# ─────────────────────────────────────────────────────────────────────
# ROLE PROFILES
# ─────────────────────────────────────────────────────────────────────
ROLE_PROFILES = {
    # ──────── TECHNICAL ROLES ────────
    "software engineer": {
        "category": "technical",
        "description": "Builds software systems and applications",
        "required_skills": ["git", "sql", "rest api", "linux"],
        "preferred_skills": ["python", "javascript", "docker", "aws",
                             "microservices", "typescript", "react"],
        "soft_skills": ["problem solving", "communication"],
        "salary_bands_usd": {
            "Junior":   (70000, 110000),
            "Mid-level":(110000, 165000),
            "Senior":   (165000, 240000),
            "Expert":   (240000, 380000),
        },
    },
    "backend developer": {
        "category": "technical",
        "description": "Builds server-side logic and APIs",
        "required_skills": ["python", "sql", "rest api", "git", "linux"],
        "preferred_skills": ["docker", "kubernetes", "aws", "postgresql",
                             "redis", "microservices", "graphql"],
        "soft_skills": ["problem solving", "communication"],
        "salary_bands_usd": {
            "Junior":   (70000, 105000),
            "Mid-level":(105000, 160000),
            "Senior":   (160000, 230000),
            "Expert":   (230000, 350000),
        },
    },
    "frontend developer": {
        "category": "technical",
        "description": "Builds user interfaces",
        "required_skills": ["javascript", "react", "git", "rest api"],
        "preferred_skills": ["typescript", "next.js", "vue", "graphql",
                             "css", "webpack"],
        "soft_skills": ["creativity", "communication", "attention to detail"],
        "salary_bands_usd": {
            "Junior":   (65000, 100000),
            "Mid-level":(100000, 150000),
            "Senior":   (150000, 215000),
            "Expert":   (215000, 320000),
        },
    },
    "full stack developer": {
        "category": "technical",
        "description": "Works on both frontend and backend",
        "required_skills": ["javascript", "react", "node.js", "sql", "git"],
        "preferred_skills": ["typescript", "next.js", "postgresql", "docker",
                             "aws", "mongodb"],
        "soft_skills": ["problem solving", "communication"],
        "salary_bands_usd": {
            "Junior":   (70000, 110000),
            "Mid-level":(110000, 165000),
            "Senior":   (165000, 235000),
            "Expert":   (235000, 340000),
        },
    },
    "data scientist": {
        "category": "technical",
        "description": "Builds predictive models and analyzes data",
        "required_skills": ["python", "sql", "machine learning", "statistics"],
        "preferred_skills": ["tensorflow", "pytorch", "scikit-learn",
                             "deep learning", "nlp", "spark", "tableau"],
        "soft_skills": ["analytical thinking", "communication", "business acumen"],
        "salary_bands_usd": {
            "Junior":   (80000, 115000),
            "Mid-level":(115000, 165000),
            "Senior":   (165000, 230000),
            "Expert":   (230000, 360000),
        },
    },
    "ml engineer": {
        "category": "technical",
        "description": "Deploys and maintains ML models in production",
        "required_skills": ["python", "machine learning", "docker", "aws"],
        "preferred_skills": ["kubernetes", "tensorflow", "pytorch", "mlops",
                             "ci/cd", "fastapi", "spark"],
        "soft_skills": ["problem solving", "communication"],
        "salary_bands_usd": {
            "Junior":   (85000, 125000),
            "Mid-level":(125000, 180000),
            "Senior":   (180000, 260000),
            "Expert":   (260000, 400000),
        },
    },
    "data engineer": {
        "category": "technical",
        "description": "Builds data pipelines and infrastructure",
        "required_skills": ["python", "sql", "spark", "aws"],
        "preferred_skills": ["kafka", "airflow", "snowflake", "dbt",
                             "kubernetes", "bigquery", "postgresql"],
        "soft_skills": ["problem solving", "analytical thinking"],
        "salary_bands_usd": {
            "Junior":   (75000, 110000),
            "Mid-level":(110000, 160000),
            "Senior":   (160000, 225000),
            "Expert":   (225000, 340000),
        },
    },
    "data analyst": {
        "category": "technical",
        "description": "Analyzes data to support business decisions",
        "required_skills": ["sql", "python", "excel"],
        "preferred_skills": ["tableau", "power bi", "r", "statistics",
                             "machine learning", "looker"],
        "soft_skills": ["analytical thinking", "communication", "business acumen"],
        "salary_bands_usd": {
            "Junior":   (55000, 85000),
            "Mid-level":(85000, 120000),
            "Senior":   (120000, 170000),
            "Expert":   (170000, 230000),
        },
    },
    "devops engineer": {
        "category": "technical",
        "description": "Manages infrastructure, CI/CD, deployment",
        "required_skills": ["linux", "docker", "aws", "ci/cd", "git"],
        "preferred_skills": ["kubernetes", "terraform", "ansible", "jenkins",
                             "helm", "prometheus", "grafana"],
        "soft_skills": ["problem solving", "communication"],
        "salary_bands_usd": {
            "Junior":   (75000, 115000),
            "Mid-level":(115000, 170000),
            "Senior":   (170000, 240000),
            "Expert":   (240000, 360000),
        },
    },
    "cloud engineer": {
        "category": "technical",
        "description": "Designs and manages cloud infrastructure",
        "required_skills": ["aws", "linux", "docker", "terraform"],
        "preferred_skills": ["kubernetes", "ansible", "ci/cd", "jenkins"],
        "soft_skills": ["problem solving", "communication"],
        "salary_bands_usd": {
            "Junior":   (75000, 115000),
            "Mid-level":(115000, 170000),
            "Senior":   (170000, 240000),
            "Expert":   (240000, 350000),
        },
    },
    "cybersecurity analyst": {
        "category": "technical",
        "description": "Monitors and protects systems from threats",
        "required_skills": ["linux", "networking", "python"],
        "preferred_skills": ["siem", "penetration testing", "firewall",
                             "incident response", "compliance"],
        "soft_skills": ["attention to detail", "analytical thinking"],
        "salary_bands_usd": {
            "Junior":   (65000, 100000),
            "Mid-level":(100000, 145000),
            "Senior":   (145000, 200000),
            "Expert":   (200000, 290000),
        },
    },
    "ai engineer": {
        "category": "technical",
        "description": "Builds AI/LLM-powered applications",
        "required_skills": ["python", "machine learning", "rest api"],
        "preferred_skills": ["llm", "langchain", "rag", "transformers",
                             "openai", "vector databases", "prompt engineering"],
        "soft_skills": ["problem solving", "communication", "creativity"],
        "salary_bands_usd": {
            "Junior":   (90000, 130000),
            "Mid-level":(130000, 185000),
            "Senior":   (185000, 270000),
            "Expert":   (270000, 420000),
        },
    },

    # ──────── NON-TECHNICAL ROLES ────────
    "product manager": {
        "category": "non_technical",
        "description": "Owns product strategy and roadmap",
        "required_skills": ["communication", "analytical thinking", "agile"],
        "preferred_skills": ["sql", "data analysis", "user research",
                             "scrum", "roadmap", "jira", "figma"],
        "soft_skills": ["leadership", "communication", "strategic thinking",
                        "stakeholder management", "empathy"],
        "salary_bands_usd": {
            "Junior":   (80000, 120000),
            "Mid-level":(120000, 170000),
            "Senior":   (170000, 240000),
            "Expert":   (240000, 400000),
        },
    },
    "engineering manager": {
        "category": "management",
        "description": "Leads an engineering team",
        "required_skills": ["leadership", "communication", "agile"],
        "preferred_skills": ["scrum", "mentoring", "performance management",
                             "hiring", "architecture", "ci/cd"],
        "soft_skills": ["leadership", "communication", "mentoring",
                        "conflict resolution", "strategic thinking"],
        "salary_bands_usd": {
            "Junior":   (130000, 180000),
            "Mid-level":(180000, 240000),
            "Senior":   (240000, 330000),
            "Expert":   (330000, 500000),
        },
    },
    "project manager": {
        "category": "non_technical",
        "description": "Plans and executes projects",
        "required_skills": ["agile", "scrum", "communication", "jira"],
        "preferred_skills": ["pmp", "budgeting", "risk management",
                             "stakeholder management"],
        "soft_skills": ["organization", "communication", "leadership"],
        "salary_bands_usd": {
            "Junior":   (65000, 95000),
            "Mid-level":(95000, 130000),
            "Senior":   (130000, 180000),
            "Expert":   (180000, 250000),
        },
    },
    "business analyst": {
        "category": "non_technical",
        "description": "Bridges business needs and technical solutions",
        "required_skills": ["sql", "excel", "communication"],
        "preferred_skills": ["tableau", "power bi", "data analysis",
                             "requirements gathering", "process modeling"],
        "soft_skills": ["analytical thinking", "communication",
                        "business acumen"],
        "salary_bands_usd": {
            "Junior":   (55000, 80000),
            "Mid-level":(80000, 115000),
            "Senior":   (115000, 155000),
            "Expert":   (155000, 210000),
        },
    },
    "marketing manager": {
        "category": "non_technical",
        "description": "Leads marketing strategy and campaigns",
        "required_skills": ["communication", "analytical thinking", "seo"],
        "preferred_skills": ["google analytics", "content marketing",
                             "social media", "ppc", "hubspot", "email marketing"],
        "soft_skills": ["creativity", "communication", "strategic thinking"],
        "salary_bands_usd": {
            "Junior":   (55000, 85000),
            "Mid-level":(85000, 120000),
            "Senior":   (120000, 175000),
            "Expert":   (175000, 260000),
        },
    },
    "sales manager": {
        "category": "non_technical",
        "description": "Leads sales team and strategy",
        "required_skills": ["communication", "negotiation", "crm"],
        "preferred_skills": ["salesforce", "hubspot", "pipeline management",
                             "forecasting", "lead generation"],
        "soft_skills": ["leadership", "communication", "persuasion"],
        "salary_bands_usd": {
            "Junior":   (60000, 95000),
            "Mid-level":(95000, 140000),
            "Senior":   (140000, 200000),
            "Expert":   (200000, 320000),
        },
    },
    "hr manager": {
        "category": "non_technical",
        "description": "Manages people operations and talent",
        "required_skills": ["communication", "empathy"],
        "preferred_skills": ["recruiting", "performance management",
                             "compensation", "employee relations",
                             "hris", "workday"],
        "soft_skills": ["empathy", "communication", "discretion"],
        "salary_bands_usd": {
            "Junior":   (55000, 80000),
            "Mid-level":(80000, 115000),
            "Senior":   (115000, 160000),
            "Expert":   (160000, 230000),
        },
    },
    "ux designer": {
        "category": "non_technical",
        "description": "Designs user experiences for digital products",
        "required_skills": ["figma", "user research"],
        "preferred_skills": ["prototyping", "wireframing", "html", "css",
                             "design systems", "accessibility"],
        "soft_skills": ["creativity", "empathy", "communication"],
        "salary_bands_usd": {
            "Junior":   (65000, 95000),
            "Mid-level":(95000, 135000),
            "Senior":   (135000, 190000),
            "Expert":   (190000, 280000),
        },
    },
    "technical writer": {
        "category": "non_technical",
        "description": "Creates technical documentation",
        "required_skills": ["writing", "communication"],
        "preferred_skills": ["markdown", "git", "api documentation",
                             "content strategy", "confluence"],
        "soft_skills": ["writing", "attention to detail", "empathy"],
        "salary_bands_usd": {
            "Junior":   (55000, 80000),
            "Mid-level":(80000, 110000),
            "Senior":   (110000, 150000),
            "Expert":   (150000, 200000),
        },
    },
}


# Categorical groupings for UI
ROLE_CATEGORIES = {
    "🔧 Technical / Engineering": [
        "software engineer", "backend developer", "frontend developer",
        "full stack developer", "devops engineer", "cloud engineer",
        "cybersecurity analyst", "ai engineer",
    ],
    "📊 Data / ML": [
        "data scientist", "data analyst", "ml engineer", "data engineer",
    ],
    "👔 Management / Leadership": [
        "engineering manager", "product manager", "project manager",
    ],
    "💼 Business / Non-Technical": [
        "business analyst", "marketing manager", "sales manager",
        "hr manager", "ux designer", "technical writer",
    ],
}


def get_role_list_flat():
    """Flat list of all role names (for matching against parsed job titles)."""
    return list(ROLE_PROFILES.keys())


def get_profile(role_name: str) -> dict | None:
    """Get profile for a role, case-insensitive matching."""
    role_name = role_name.lower().strip()
    if role_name in ROLE_PROFILES:
        return ROLE_PROFILES[role_name]
    # Try fuzzy match (e.g., "data science" → "data scientist")
    for key in ROLE_PROFILES:
        if key in role_name or role_name in key:
            return ROLE_PROFILES[key]
    return None


def estimate_experience_level(years: float) -> str:
    """Map years of experience to a level."""
    if years < 2:
        return "Junior"
    elif years < 5:
        return "Mid-level"
    elif years < 10:
        return "Senior"
    else:
        return "Expert"


if __name__ == "__main__":
    print(f"Loaded {len(ROLE_PROFILES)} role profiles")
    print(f"Categories: {list(ROLE_CATEGORIES.keys())}")
    print(f"\nIndia software engineer salary band (Senior):")
    band = ROLE_PROFILES["software engineer"]["salary_bands_usd"]["Senior"]
    india_band = (band[0] * COUNTRY_ADJUSTMENTS["India"],
                  band[1] * COUNTRY_ADJUSTMENTS["India"])
    print(f"  USA: ${band[0]:,} - ${band[1]:,}")
    print(f"  India: ${india_band[0]:,.0f} - ${india_band[1]:,.0f}")
    print(f"        ₹{india_band[0]*83/100000:.1f} - ₹{india_band[1]*83/100000:.1f} LPA")
