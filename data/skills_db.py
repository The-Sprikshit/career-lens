"""
Skills Database
Curated list of technical + soft skills with categories.
Used for skill extraction and ROI calculation.
"""

SKILLS_DB = {
    # ── Programming Languages ──
    "python": {"category": "language", "salary_weight": 1.25, "demand": 0.95},
    "java": {"category": "language", "salary_weight": 1.20, "demand": 0.92},
    "javascript": {"category": "language", "salary_weight": 1.18, "demand": 0.94},
    "typescript": {"category": "language", "salary_weight": 1.22, "demand": 0.90},
    "c++": {"category": "language", "salary_weight": 1.18, "demand": 0.85},
    "c#": {"category": "language", "salary_weight": 1.15, "demand": 0.82},
    "go": {"category": "language", "salary_weight": 1.28, "demand": 0.80},
    "rust": {"category": "language", "salary_weight": 1.30, "demand": 0.70},
    "kotlin": {"category": "language", "salary_weight": 1.22, "demand": 0.78},
    "swift": {"category": "language", "salary_weight": 1.20, "demand": 0.75},
    "r": {"category": "language", "salary_weight": 1.15, "demand": 0.72},
    "scala": {"category": "language", "salary_weight": 1.20, "demand": 0.65},
    "ruby": {"category": "language", "salary_weight": 1.15, "demand": 0.70},
    "php": {"category": "language", "salary_weight": 1.10, "demand": 0.68},
    "sql": {"category": "language", "salary_weight": 1.18, "demand": 0.95},

    # ── Web Frameworks ──
    "react": {"category": "web_framework", "salary_weight": 1.22, "demand": 0.93},
    "angular": {"category": "web_framework", "salary_weight": 1.18, "demand": 0.82},
    "vue": {"category": "web_framework", "salary_weight": 1.18, "demand": 0.78},
    "next.js": {"category": "web_framework", "salary_weight": 1.24, "demand": 0.85},
    "node.js": {"category": "web_framework", "salary_weight": 1.20, "demand": 0.90},
    "express": {"category": "web_framework", "salary_weight": 1.15, "demand": 0.80},
    "django": {"category": "web_framework", "salary_weight": 1.20, "demand": 0.82},
    "flask": {"category": "web_framework", "salary_weight": 1.15, "demand": 0.75},
    "fastapi": {"category": "web_framework", "salary_weight": 1.22, "demand": 0.78},
    "spring": {"category": "web_framework", "salary_weight": 1.18, "demand": 0.80},
    "spring boot": {"category": "web_framework", "salary_weight": 1.22, "demand": 0.85},

    # ── Cloud / DevOps ──
    "aws": {"category": "cloud", "salary_weight": 1.30, "demand": 0.96},
    "azure": {"category": "cloud", "salary_weight": 1.25, "demand": 0.85},
    "gcp": {"category": "cloud", "salary_weight": 1.25, "demand": 0.82},
    "docker": {"category": "cloud", "salary_weight": 1.20, "demand": 0.92},
    "kubernetes": {"category": "cloud", "salary_weight": 1.32, "demand": 0.88},
    "terraform": {"category": "cloud", "salary_weight": 1.25, "demand": 0.78},
    "jenkins": {"category": "cloud", "salary_weight": 1.15, "demand": 0.75},
    "ci/cd": {"category": "cloud", "salary_weight": 1.20, "demand": 0.85},
    "ansible": {"category": "cloud", "salary_weight": 1.18, "demand": 0.70},
    "helm": {"category": "cloud", "salary_weight": 1.15, "demand": 0.65},

    # ── Databases ──
    "postgresql": {"category": "database", "salary_weight": 1.18, "demand": 0.85},
    "mysql": {"category": "database", "salary_weight": 1.12, "demand": 0.82},
    "mongodb": {"category": "database", "salary_weight": 1.15, "demand": 0.78},
    "redis": {"category": "database", "salary_weight": 1.18, "demand": 0.75},
    "elasticsearch": {"category": "database", "salary_weight": 1.20, "demand": 0.72},
    "dynamodb": {"category": "database", "salary_weight": 1.20, "demand": 0.72},
    "snowflake": {"category": "database", "salary_weight": 1.28, "demand": 0.80},
    "bigquery": {"category": "database", "salary_weight": 1.22, "demand": 0.75},

    # ── ML / AI ──
    "tensorflow": {"category": "ml_ai", "salary_weight": 1.28, "demand": 0.85},
    "pytorch": {"category": "ml_ai", "salary_weight": 1.30, "demand": 0.88},
    "scikit-learn": {"category": "ml_ai", "salary_weight": 1.20, "demand": 0.85},
    "machine learning": {"category": "ml_ai", "salary_weight": 1.30, "demand": 0.95},
    "deep learning": {"category": "ml_ai", "salary_weight": 1.32, "demand": 0.90},
    "nlp": {"category": "ml_ai", "salary_weight": 1.28, "demand": 0.85},
    "computer vision": {"category": "ml_ai", "salary_weight": 1.28, "demand": 0.80},
    "llm": {"category": "ml_ai", "salary_weight": 1.35, "demand": 0.92},
    "transformers": {"category": "ml_ai", "salary_weight": 1.30, "demand": 0.85},
    "langchain": {"category": "ml_ai", "salary_weight": 1.28, "demand": 0.75},
    "rag": {"category": "ml_ai", "salary_weight": 1.28, "demand": 0.72},
    "prompt engineering": {"category": "ml_ai", "salary_weight": 1.20, "demand": 0.70},
    "mlops": {"category": "ml_ai", "salary_weight": 1.30, "demand": 0.78},

    # ── Data Engineering ──
    "spark": {"category": "data_eng", "salary_weight": 1.25, "demand": 0.82},
    "kafka": {"category": "data_eng", "salary_weight": 1.28, "demand": 0.80},
    "airflow": {"category": "data_eng", "salary_weight": 1.25, "demand": 0.78},
    "hadoop": {"category": "data_eng", "salary_weight": 1.15, "demand": 0.65},
    "dbt": {"category": "data_eng", "salary_weight": 1.20, "demand": 0.70},
    "etl": {"category": "data_eng", "salary_weight": 1.15, "demand": 0.75},

    # ── Tools / Other ──
    "git": {"category": "tools", "salary_weight": 1.08, "demand": 0.95},
    "linux": {"category": "tools", "salary_weight": 1.12, "demand": 0.85},
    "rest api": {"category": "tools", "salary_weight": 1.15, "demand": 0.85},
    "graphql": {"category": "tools", "salary_weight": 1.18, "demand": 0.72},
    "microservices": {"category": "tools", "salary_weight": 1.20, "demand": 0.82},
    "agile": {"category": "tools", "salary_weight": 1.05, "demand": 0.80},
    "scrum": {"category": "tools", "salary_weight": 1.05, "demand": 0.72},
}

# Skill categories for the radar chart
SKILL_CATEGORIES = list(set(s["category"] for s in SKILLS_DB.values()))

# Strong action verbs (for resume quality scoring)
STRONG_VERBS = [
    "achieved", "architected", "built", "created", "delivered", "designed",
    "developed", "engineered", "established", "executed", "implemented",
    "improved", "increased", "launched", "led", "managed", "mentored",
    "migrated", "optimized", "orchestrated", "pioneered", "reduced",
    "refactored", "researched", "resolved", "scaled", "shipped", "spearheaded",
    "streamlined", "transformed",
]

# Weak / fluff phrases (for authenticity scoring)
WEAK_PHRASES = [
    "passionate about", "hardworking", "team player", "go-getter",
    "self-starter", "detail-oriented", "synergy", "rockstar", "ninja",
    "guru", "wizard", "thought leader", "disruptor", "innovative thinker",
    "results-driven", "dynamic professional", "best-in-class",
]
