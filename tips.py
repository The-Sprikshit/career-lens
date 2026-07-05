"""
Career Tips Engine
==================
Rule-based tip generator that responds to common career questions.
No LLM API needed — uses a curated tips database + intent matching.

Supports intents like:
- "what skills should I learn?"
- "how do I negotiate salary?"
- "should I switch jobs?"
- "what certification helps?"
- "how to get promoted?"
- generic questions

Each tip is personalized based on:
- User's current role
- Experience level
- Country
- Their analysis results (skill gaps, salary gap, etc.)
"""

import re
from typing import Dict, List, Optional
from data.role_profiles import ROLE_PROFILES, estimate_experience_level


# ─────────────────────────────────────────────────────────────────────
# INTENT PATTERNS (regex → intent name)
# ─────────────────────────────────────────────────────────────────────
INTENT_PATTERNS = {
    "learn_skill": [
        r"what (skill|to learn|should i learn)",
        r"which skill",
        r"how to (improve|add).*skill",
        r"new skill",
        r"next skill",
    ],
    "negotiate_salary": [
        r"negotiat",
        r"salary (raise|hike|increase|bump)",
        r"how (to|do i).*earn more",
        r"paid more",
        r"underpaid",
    ],
    "switch_job": [
        r"switch (job|company|role)",
        r"new job",
        r"job (hop|hopping)",
        r"change job",
        r"leave (my )?job",
        r"跳槽",  # Chinese for "job hop"
    ],
    "switch_career": [
        r"switch (career|field)",
        r"career change",
        r"different field",
        r"non.?technical",
        r"become (a|an) (manager|pm|product)",
    ],
    "certification": [
        r"certif",
        r"aws cert",
        r"azure cert",
        r"google cert",
        r"which cert",
    ],
    "promotion": [
        r"promot",
        r"get (a )?raise",
        r"advance",
        r"senior (role|position)",
        r"next level",
    ],
    "interview": [
        r"interview",
        r"prepare for",
        r"how to (ace|crack|pass)",
    ],
    "remote_work": [
        r"remote",
        r"work from home",
        r"wfh",
    ],
    "india_specific": [
        r"india",
        r"lpa",
        r"indian (market|companies|salary)",
    ],
    "thanks": [
        r"thank", r"thanks", r"thx",
    ],
    "help": [
        r"^help$", r"what can you", r"how do you work",
        r"^\\?$",
    ],
}


def detect_intent(question: str) -> str:
    """Match a question to an intent."""
    q = question.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, q):
                return intent
    return "general"


# ─────────────────────────────────────────────────────────────────────
# TIPS DATABASE
# ─────────────────────────────────────────────────────────────────────
TIPS_DB = {
    "learn_skill": {
        "general": [
            "📚 Focus on **high-demand + high-salary-weight** skills first. "
            "Check your Skill ROI tab for the top recommendations.",
            "🎯 Don't learn skills in isolation — pair each new skill with a project "
            "you can show on your resume.",
            "⚡ Specialize in 1-2 categories deeply rather than 5 categories shallowly. "
            "Recruiters value depth.",
        ],
        "data scientist": [
            "📊 Master **SQL** first — every data role tests it. "
            "Then learn **statistics** deeply (hypothesis testing, A/B testing).",
            "🤖 Move from sklearn → **PyTorch/TensorFlow** if you want to do deep learning.",
            "📈 Learn **experiment design** and **causal inference** — what separates "
            "junior from senior data scientists.",
        ],
        "ml engineer": [
            "🏗️ Focus on **MLOps**: Docker, Kubernetes, CI/CD, model monitoring. "
            "These separate ML engineers from data scientists.",
            "⚙️ Learn **Kubernetes** — it shows up in 60%+ of ML engineer JDs.",
            "📦 Study **feature stores** (Feast, Tecton) and **model registries** (MLflow).",
        ],
        "software engineer": [
            "🌐 Learn **cloud** (AWS/Azure/GCP) — most JDs require it. "
            "Pick one and get certified.",
            "🐳 Master **Docker + Kubernetes** — they're industry standard now.",
            "🔧 Go deep on **system design** — required for senior+ roles.",
        ],
        "frontend developer": [
            "⚛️ **TypeScript** is no longer optional — it's the default.",
            "🎨 Learn **React Server Components** and **Next.js** — they're trending.",
            "♿ Study **accessibility (a11y)** — most teams need it but few engineers know it.",
        ],
    },
    "negotiate_salary": {
        "general": [
            "💰 **Never share your current salary first.** When asked, deflect: "
            "'I'd prefer to understand the full scope of the role first.'",
            "📊 Research market rates on **levels.fyi**, **Glassdoor**, "
            "**AmbitionBox** (for India). Anchor with the high end.",
            "🎯 Always counter-offer. Even if you accept, counter once. "
            "The first offer is rarely the best.",
            "⏰ The best time to negotiate is AFTER you receive the offer, "
            "BEFORE you sign. Not during the interview.",
        ],
        "india": [
            "🇮🇳 In India, **offer letters from product companies** (Google, Microsoft, "
            "Amazon) carry more weight than service companies. Use them as anchors.",
            "💼 Consider **ESOPs/RSUs** for senior roles — they can double your total comp.",
            "📜 Keep records of your achievements. Update your resume before each negotiation.",
        ],
    },
    "switch_job": {
        "general": [
            "⏭️ Job hopping every 1-2 years is now normal in tech, especially in "
            "the first 5 years. Don't feel guilty.",
            "📈 Each switch typically yields a **15-30% salary increase** — "
            "often more than internal raises.",
            "🎯 Look for companies that are **growing fast** — more responsibilities, "
            "better titles, faster comp growth.",
            "🛑 Red flag: if you're switching just for money without learning new skills, "
            "you'll plateau by your mid-30s.",
        ],
    },
    "switch_career": {
        "general": [
            "🔀 Tech → Product Manager is one of the most common switches. "
            "Start by **leading a small project** at your current company.",
            "📚 Engineer → Data Scientist: focus on **SQL + statistics + ML**. "
            "Build 2-3 portfolio projects.",
            "💼 Tech → Sales/BD: your technical background is an advantage. "
            "Consider **Sales Engineer** roles as a bridge.",
        ],
    },
    "certification": {
        "general": [
            "🏆 **AWS Solutions Architect** — most valued cloud cert. "
            "Validates real skills, not just trivia.",
            "☁️ **Kubernetes Administrator (CKA)** — high demand, good salary impact.",
            "🤖 **TensorFlow / PyTorch certifications** — useful for ML roles.",
            "⚠️ Avoid certs with low industry recognition. Check LinkedIn job posts "
            "in your target role to see what they actually require.",
        ],
        "data scientist": [
            "📊 **Google Data Analytics** — good for beginners, recognized but basic.",
            "🤖 **AWS Machine Learning Specialty** — strong for ML engineers.",
        ],
        "devops engineer": [
            "🐳 **Certified Kubernetes Administrator (CKA)** — gold standard.",
            "🏗️ **AWS Solutions Architect** or **Azure Architect** — depends on your stack.",
            "🔧 **Terraform Associate** — infrastructure-as-code certification.",
        ],
    },
    "promotion": {
        "general": [
            "📋 Document your wins **continuously** — don't wait for review season. "
            "Keep a 'brag doc'.",
            "🎯 Promotions are based on **scope**, not just performance. "
            "Volunteer for projects slightly above your level.",
            "🤝 Find a **sponsor** (not just a mentor). Sponsors advocate for you in rooms "
            "you're not in.",
            "⏱️ Typical promotion cycles: **2-3 years** at most companies. "
            "If you're not progressing, switch jobs.",
        ],
        "india": [
            "🇮🇳 In Indian IT services, jumping to a **product company** often gives "
            "the biggest title+comp jump.",
            "📈 Get your manager to **align on promotion criteria** at the start of "
            "the year. Don't be surprised at review time.",
        ],
    },
    "interview": {
        "general": [
            "💻 Practice **system design** for senior+ roles. "
            "Use 'System Design Interview' by Alex Xu.",
            "🧠 Practice **coding problems** on LeetCode — 150-200 medium/hard problems "
            "is a good target.",
            "📝 For non-technical roles: prepare **behavioral stories using STAR** "
            "(Situation, Task, Action, Result).",
            "🎤 Always **research the company deeply** — mission, recent news, "
            "tech stack, culture. Ask thoughtful questions.",
        ],
    },
    "remote_work": {
        "general": [
            "🌍 **Remote roles** in India often pay 2-3x local market. "
            "Look at international remote-first companies.",
            "💻 **Async communication** is the #1 skill for remote work. "
            "Write clear docs, record Looms.",
            "⏰ **Time zone overlap** matters. US companies hiring remote in India "
            "typically want 4-6 hours overlap with US timezones.",
        ],
    },
    "india_specific": {
        "general": [
            "🇮🇳 **Product companies** (Flipkart, Razorpay, Cred, Swiggy) pay 30-50% "
            "more than service companies (TCS, Infosys, Wipro) for the same role.",
            "📊 **Tier-1 college brand** (IIT/BITS/NIT) gives a 20-40% salary premium "
            "at the start. After 5+ years, skills matter more.",
            "🏙️ **Bangalore vs other cities**: salary is typically 30-50% higher in Bangalore.",
        ],
    },
    "thanks": [
        "😊 Glad I could help! Feel free to ask more questions.",
        "👍 You're welcome! Re-upload your resume anytime to track progress.",
    ],
}


def get_tip(question: str, user_context: Dict = None) -> Dict:
    """
    Generate a personalized tip response.

    Args:
        question: User's question
        user_context: {
            "role": "data scientist",
            "country": "India",
            "experience_years": 4,
            "level": "Mid-level",
            "skills": [...],
            "missing_skills": [...],
        }

    Returns:
        {
            "intent": "learn_skill",
            "response": "...",          # main tip
            "follow_ups": [...],        # suggested next questions
            "personalized": True/False,
        }
    """
    intent = detect_intent(question)
    ctx = user_context or {}

    role = (ctx.get("role") or "general").lower()
    country = ctx.get("country", "USA")
    level = ctx.get("level", "Mid-level")
    missing = ctx.get("missing_skills", [])

    # Pick tips: role-specific first, fall back to general
    tips_for_intent = TIPS_DB.get(intent, {})
    role_specific = tips_for_intent.get(role, [])
    general_tips = tips_for_intent.get("general", [])

    # Combine: 2 role-specific + 1-2 general
    main_tips = (role_specific + general_tips)[:3]

    # Personalize with user's missing skills
    personalized_note = ""
    if missing and intent == "learn_skill":
        top_3_missing = missing[:3]
        personalized_note = (
            f"\n\n🎯 **Based on your resume**, you're missing: "
            f"{', '.join(top_3_missing)}. Prioritize those first."
        )

    if intent == "negotiate_salary" and country == "India":
        personalized_note = (
            f"\n\n🇮🇳 For your level ({level}) in India, "
            f"negotiation leverage is highest with **product companies** and "
            f"**offers from MNCs**."
        )

    response = "\n".join([f"- {t}" for t in main_tips])
    if personalized_note:
        response += personalized_note

    if not main_tips:
        # Fallback for general intent
        response = (
            "🤔 I'm not sure I understand that yet. Try asking about:\n"
            "- What skills should I learn next?\n"
            "- How do I negotiate salary?\n"
            "- Should I switch jobs?\n"
            "- What certification helps?\n"
            "- How do I get promoted?\n"
        )

    # Follow-up suggestions
    follow_ups = {
        "learn_skill": [
            f"Show me skill gaps for {ctx.get('target_role', role)}",
            "What projects should I build?",
            "Which certification helps most?",
        ],
        "negotiate_salary": [
            "How do I research market rates?",
            "When is the best time to negotiate?",
            "Should I share my current salary?",
        ],
        "switch_job": [
            "When is the right time to switch?",
            "How much of a raise should I expect?",
            "Should I switch company or role first?",
        ],
        "certification": [
            "Is AWS cert worth it for me?",
            "How long does it take to prepare?",
            "Do certifications actually matter?",
        ],
        "promotion": [
            "How long does promotion typically take?",
            "Should I switch to get promoted faster?",
            "What signals do managers look for?",
        ],
        "interview": [
            "How should I prepare for system design?",
            "Tell me about behavioral questions",
            "What questions should I ask them?",
        ],
        "switch_career": [
            "What skills do I need for the new field?",
            "How do I break in without experience?",
            "Should I do a bootcamp?",
        ],
        "remote_work": [
            "How do I find remote roles?",
            "What's the pay difference?",
            "How to manage time zones?",
        ],
    }.get(intent, [
        "What skills should I learn?",
        "How do I negotiate salary?",
        "Should I switch jobs?",
    ])

    return {
        "intent": intent,
        "response": response,
        "follow_ups": follow_ups,
        "personalized": bool(personalized_note),
    }


def get_daily_tip(role: str = "software engineer",
                  experience_years: float = 3,
                  country: str = "USA") -> str:
    """Return a single motivational/career tip of the day."""
    import random
    all_tips = (
        TIPS_DB.get("learn_skill", {}).get("general", []) +
        TIPS_DB.get("negotiate_salary", {}).get("general", []) +
        TIPS_DB.get("promotion", {}).get("general", [])
    )
    return random.choice(all_tips) if all_tips else "Keep learning! 🚀"


# ── CLI test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_questions = [
        "What skills should I learn?",
        "How do I negotiate salary in India?",
        "Should I switch jobs?",
        "What certification helps?",
        "How do I get promoted?",
        "Should I switch to product management?",
        "How do I prepare for interviews?",
        "Tell me about remote work in India",
        "thanks",
        "asdfasdf",  # unknown
    ]

    context = {
        "role": "data scientist",
        "country": "India",
        "experience_years": 4,
        "level": "Mid-level",
        "missing_skills": ["kubernetes", "sql", "tableau"],
    }

    for q in test_questions:
        result = get_tip(q, context)
        print(f"\nQ: {q}")
        print(f"Intent: {result['intent']}")
        print(f"Response:\n{result['response']}")
        print(f"Suggested follow-ups: {result['follow_ups']}")
        print("-" * 70)
