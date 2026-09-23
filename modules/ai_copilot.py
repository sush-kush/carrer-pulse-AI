"""
CareerPulse AI — AI Career Copilot
Rule-based NL query engine grounded strictly in the dataset.
No external APIs, no fabricated responses.
"""

import re
from collections import Counter

import pandas as pd

from modules.data_loader import COL_TITLE, COL_COMPANY, COL_LOCATION
from modules.feature_engineering import (
    get_skill_frequency,
    get_skills_by_role,
    get_role_salary_stats,
    get_location_demand,
    get_role_demand,
    match_roles_to_skills,
    compute_skill_gap,
    simulate_skill_addition,
)


# ── Intent patterns ───────────────────────────────────────────────────────────

_INTENTS = [
    ("skill_demand",       [r"most demand\w* skill", r"top skill", r"popular skill", r"common skill",
                             r"most demanded", r"in demand", r"^what skill", r"what are.{0,10}skill"]),
    ("location_demand",    [r"(best|top|most).{0,15}(city|cit|location|place).{0,20}(for|to find|job)",
                             r"which city", r"which cit", r"where.{0,20}(most|many|best).{0,20}job",
                             r"most job.{0,15}(in|at|city|location)",
                             r"job.{0,20}(in|at).{0,20}(bengaluru|mumbai|delhi|pune|hyderabad|chennai|noida|gurugram)"]),
    ("role_skills",        [r"skill.{0,20}(for|in|require).{0,30}role", r"what skill.{0,10}(do i|should).{0,20}(need|learn|know)", r"skills? for (.+)"]),
    ("salary_stats",       [r"salary.{0,20}(data analyst|engineer|developer|manager|analyst|architect|consultant)", r"how much.{0,20}earn", r"pay.{0,20}(for|in)", r"compensation"]),
    ("role_match",         [r"match.{0,20}skill", r"role.{0,20}(match|suit|fit)", r"which role.{0,20}(for me|suit)", r"jobs? for"]),
    ("skill_gap",          [r"skill gap", r"missing skill", r"what skill.{0,10}(lack|missing|need to learn)"]),
    ("compare_roles",      [r"compare.{0,30}(analyst|engineer|developer|manager)", r"vs\.{0,5}(analyst|engineer|developer|manager)", r"difference between"]),
    ("what_if_skill",      [r"what if.{0,20}(learn|add|know|acquire)", r"if i (learn|add|know)", r"after learning"]),
    ("company_info",       [r"(accenture|infosys|wipro|tcs|ibm|capgemini|cognizant).{0,20}(job|role|hiring|post)", r"top compan", r"best compan"]),
    ("exp_for_role",       [r"experience.{0,20}(for|required|needed).{0,20}(role|job|position)", r"how many year", r"fresher.{0,20}(eligible|apply)"]),
    ("general_market",     [r"job market", r"how many job", r"total post", r"overview", r"market stat"]),
]


def classify_intent(query: str) -> str:
    q = query.lower()
    for intent, patterns in _INTENTS:
        for p in patterns:
            if re.search(p, q):
                return intent
    return "general"


# ── Response generators ───────────────────────────────────────────────────────

def answer(df: pd.DataFrame, query: str) -> str:
    intent = classify_intent(query)
    q = query.lower()

    try:
        if intent == "skill_demand":
            return _answer_skill_demand(df, q)
        elif intent == "role_skills":
            return _answer_role_skills(df, q)
        elif intent == "salary_stats":
            return _answer_salary(df, q)
        elif intent == "role_match":
            return _answer_role_match(df, q)
        elif intent == "skill_gap":
            return _answer_skill_gap(df, q)
        elif intent == "location_demand":
            return _answer_location(df, q)
        elif intent == "compare_roles":
            return _answer_compare_roles(df, q)
        elif intent == "what_if_skill":
            return _answer_what_if(df, q)
        elif intent == "company_info":
            return _answer_company(df, q)
        elif intent == "exp_for_role":
            return _answer_experience(df, q)
        elif intent == "general_market":
            return _answer_market_overview(df)
        else:
            return _answer_general(df, q)
    except Exception as e:
        return (
            f"⚠️ I encountered an issue processing your query: `{e}`\n\n"
            "Please try rephrasing your question or use the specific analysis pages."
        )


# ── Individual answer functions ───────────────────────────────────────────────

def _answer_skill_demand(df, q) -> str:
    skills_df = get_skill_frequency(df, top_n=15)
    lines = ["**📊 Most Demanded Skills in the Dataset**\n"]
    lines.append("| # | Skill | Postings | Coverage |")
    lines.append("|---|-------|----------|---------|")
    for i, row in skills_df.iterrows():
        lines.append(f"| {i+1} | {row['skill']} | {row['count']:,} | {row['pct']}% |")
    lines.append(f"\n*Based on {len(df):,} job postings in the uploaded dataset.*")
    return "\n".join(lines)


def _answer_role_skills(df, q) -> str:
    # Extract role from query
    role = _extract_role_from_query(df, q)
    if not role:
        return (
            "I couldn't identify a specific role in your question. "
            "Try: *'What skills are required for Data Analyst?'*"
        )
    skills_df = get_skills_by_role(df, role, top_n=12)
    if skills_df.empty:
        return f"No postings found for role matching **{role}** in the dataset."

    lines = [f"**🧠 Skills Commonly Observed for '{role}' Roles**\n"]
    lines.append("| Skill | Postings | Frequency |")
    lines.append("|-------|----------|-----------|")
    for _, row in skills_df.iterrows():
        lines.append(f"| {row['skill']} | {row['count']:,} | {row['pct']}% |")
    n = int(skills_df['count'].sum() / max(len(skills_df), 1))
    lines.append(f"\n*Dataset observation — not a hiring guarantee.*")
    return "\n".join(lines)


def _answer_salary(df, q) -> str:
    role = _extract_role_from_query(df, q)
    if not role:
        # General salary stats
        sal = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()]["mid_salary_lpa"]
        if sal.empty:
            return "The dataset does not contain sufficient disclosed salary data."
        return (
            f"**💰 Overall Salary Statistics (Disclosed Postings Only)**\n\n"
            f"- **Postings with salary data:** {len(sal):,} of {len(df):,} total\n"
            f"- **Mean:** ₹{sal.mean():.2f} LPA\n"
            f"- **Median:** ₹{sal.median():.2f} LPA\n"
            f"- **Range:** ₹{sal.min():.2f} – ₹{sal.max():.2f} LPA\n"
            f"- **25th–75th pct:** ₹{sal.quantile(0.25):.2f} – ₹{sal.quantile(0.75):.2f} LPA\n\n"
            f"*Salary is undisclosed in {len(df) - len(sal):,} postings and excluded from these statistics.*"
        )

    stats = get_role_salary_stats(df, role)
    if not stats:
        return (
            f"No postings with disclosed salary found for **{role}** in the dataset. "
            "Try the Salary Lab for broader analysis."
        )
    return (
        f"**💰 Salary Statistics for '{role}'** (Disclosed Postings Only)\n\n"
        f"- **Total postings:** {stats['count']:,}\n"
        f"- **With salary data:** {stats['salary_count']:,}\n"
        f"- **Mean:** ₹{stats['mean_lpa']} LPA\n"
        f"- **Median:** ₹{stats['median_lpa']} LPA\n"
        f"- **Range:** ₹{stats['min_lpa']} – ₹{stats['max_lpa']} LPA\n"
        f"- **25th–75th pct:** ₹{stats['p25_lpa']} – ₹{stats['p75_lpa']} LPA\n\n"
        f"*These are observed salary values from the dataset. Actual compensation varies.*"
    )


def _answer_role_match(df, q) -> str:
    # Extract skills from query
    skills = _extract_skills_from_query(df, q)
    if not skills:
        return (
            "Please mention your skills in the query. "
            "Example: *'Which roles match Python, SQL, and Excel?'*"
        )
    matches = match_roles_to_skills(df, skills, top_n=8)
    if matches.empty:
        return "No matching roles found for the specified skills in the dataset."

    lines = [f"**🎯 Roles Matching Skills: {', '.join(skills[:5])}**\n"]
    lines.append("| Role | Match Score | Postings |")
    lines.append("|------|------------|---------|")
    for _, row in matches.iterrows():
        lines.append(f"| {row['role']} | {row['match_score']}% | {row['postings']:,} |")
    lines.append("\n*Match score = skill overlap ratio across relevant postings.*")
    lines.append("*This reflects skill pattern similarity, not hiring probability.*")
    return "\n".join(lines)


def _answer_skill_gap(df, q) -> str:
    role = _extract_role_from_query(df, q)
    skills = _extract_skills_from_query(df, q)
    if not role:
        return "Please specify a target role. Example: *'What skills am I missing for Data Analyst?'*"
    if not skills:
        return "Please also mention your current skills. Example: *'I know Python and SQL. What am I missing for Data Analyst?'*"

    gap = compute_skill_gap(df, skills, role)
    if "error" in gap:
        return f"⚠️ {gap['error']}"

    lines = [f"**🔍 Skill Gap Analysis for '{role}'**\n"]
    lines.append(f"- Your skills: {', '.join(skills)}")
    lines.append(f"- Role postings analyzed: {gap['total_postings']:,}")
    lines.append(f"- Dataset skill match: **{gap['match_pct']}%**\n")
    if gap["missing_skills"]:
        lines.append("**Frequently Observed Skills You Haven't Listed:**")
        for skill, cnt in list(gap["missing_skills"].items())[:8]:
            pct = round(cnt / gap["total_postings"] * 100, 1)
            lines.append(f"  - {skill} ({pct}% of postings)")
    lines.append("\n*Based on skill frequency in the uploaded dataset.*")
    return "\n".join(lines)


def _answer_location(df, q) -> str:
    loc_df = get_location_demand(df, top_n=10)
    lines = ["**📍 Locations with Most Job Postings (Dataset Observation)**\n"]
    lines.append("| # | Location | Postings | Share |")
    lines.append("|---|----------|----------|-------|")
    for i, row in loc_df.iterrows():
        lines.append(f"| {i+1} | {row['location']} | {row['count']:,} | {row['pct']}% |")
    lines.append("\n*Observation from the uploaded dataset only.*")
    return "\n".join(lines)


def _answer_compare_roles(df, q) -> str:
    roles = _extract_multiple_roles(df, q)
    if len(roles) < 2:
        return "Please mention two roles to compare. Example: *'Compare Data Analyst vs Business Analyst'*"

    lines = [f"**⚖️ Role Comparison: {' vs '.join(roles)}**\n"]
    for role in roles:
        stats = get_role_salary_stats(df, role)
        skills_df = get_skills_by_role(df, role, top_n=5)
        top_skills = ", ".join(skills_df["skill"].tolist()[:5]) if not skills_df.empty else "N/A"
        lines.append(f"### {role}")
        lines.append(f"- **Postings:** {stats.get('count', 0):,}")
        if stats:
            lines.append(f"- **Median Salary:** ₹{stats.get('median_lpa', 'N/A')} LPA")
        lines.append(f"- **Top Skills:** {top_skills}\n")
    lines.append("*Based on observed patterns in the uploaded dataset.*")
    return "\n".join(lines)


def _answer_what_if(df, q) -> str:
    new_skills = _extract_skills_from_query(df, q)
    if not new_skills:
        return (
            "Please specify skills to add. "
            "Example: *'What if I learn Power BI and Tableau?'*\n\n"
            "For a full simulation, use the **Career Simulator** page."
        )

    result = simulate_skill_addition(df, [], new_skills)
    after = result["after"]
    if after.empty:
        return f"No role matches found for: {', '.join(new_skills)}."

    lines = [f"**🔮 What If You Add: {', '.join(new_skills)}?**\n"]
    lines.append(f"Adding these skills would match skill patterns in these roles:\n")
    lines.append("| Role | Match Score | Postings |")
    lines.append("|------|------------|---------|")
    for _, row in after.head(6).iterrows():
        lines.append(f"| {row['role']} | {row['match_score']}% | {row['postings']:,} |")
    lines.append("\n*Dataset-based scenario — not a hiring guarantee. Use the Career Simulator for a full analysis.*")
    return "\n".join(lines)


def _answer_company(df, q) -> str:
    top_companies = df[COL_COMPANY].value_counts().head(10)
    lines = ["**🏢 Companies with Most Job Postings (from Dataset)**\n"]
    lines.append("| # | Company | Postings |")
    lines.append("|---|---------|---------|")
    for i, (company, count) in enumerate(top_companies.items()):
        lines.append(f"| {i+1} | {company} | {count:,} |")
    lines.append("\n*Only companies present in the uploaded dataset are shown.*")
    return "\n".join(lines)


def _answer_experience(df, q) -> str:
    role = _extract_role_from_query(df, q)
    sub = df.copy()
    role_label = "all roles"
    if role:
        sub = df[df[COL_TITLE].str.lower().str.contains(role.lower(), na=False)]
        role_label = role
    if sub.empty:
        return f"No postings found for **{role}** in the dataset."

    min_exp = sub["minimumExperience"].dropna()
    max_exp = sub["maximumExperience"].dropna()
    if min_exp.empty:
        return "No experience data available for this query."

    return (
        f"**📅 Experience Required for '{role_label}'**\n\n"
        f"- **Postings analyzed:** {len(sub):,}\n"
        f"- **Mean minimum experience:** {min_exp.mean():.1f} years\n"
        f"- **Mean maximum experience:** {max_exp.mean():.1f} years\n"
        f"- **Fresher-friendly (0 yrs min):** {(min_exp == 0).sum():,} postings\n"
        f"- **Most common range:** {sub['experience'].value_counts().index[0] if sub['experience'].notna().any() else 'N/A'}\n\n"
        f"*Observation from the uploaded dataset.*"
    )


def _answer_market_overview(df) -> str:
    sal = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()]["mid_salary_lpa"]
    top_role = df[COL_TITLE].value_counts().index[0]
    top_loc  = df["location_primary"].value_counts().index[0]
    top_co   = df[COL_COMPANY].value_counts().index[0]
    return (
        f"**🌐 Indian Job Market — Dataset Overview**\n\n"
        f"- **Total Job Postings:** {len(df):,}\n"
        f"- **Unique Companies:** {df[COL_COMPANY].nunique():,}\n"
        f"- **Unique Job Titles:** {df[COL_TITLE].nunique():,}\n"
        f"- **Unique Locations:** {df['location_primary'].nunique():,}\n"
        f"- **Salary Disclosed:** {df['salary_disclosed'].sum():,} ({df['salary_disclosed'].mean()*100:.1f}%)\n"
        f"- **Avg Salary (disclosed):** ₹{sal.mean():.2f} LPA\n"
        f"- **Most Posted Role:** {top_role}\n"
        f"- **Most Active City:** {top_loc}\n"
        f"- **Most Active Company:** {top_co}\n\n"
        f"*All figures derived from the uploaded dataset.*"
    )


def _answer_general(df, q) -> str:
    # Try to answer based on extracted entities
    role = _extract_role_from_query(df, q)
    skills = _extract_skills_from_query(df, q)

    if role:
        return _answer_salary(df, q) if "salary" in q or "pay" in q or "earn" in q else _answer_role_skills(df, q)
    if skills:
        return _answer_role_match(df, q)

    return (
        "I can help you with questions like:\n\n"
        "- *What skills are most demanded?*\n"
        "- *Which roles match Python and SQL?*\n"
        "- *What salary is observed for Data Analyst?*\n"
        "- *What skills are required for a Software Engineer?*\n"
        "- *Compare Data Analyst vs Business Analyst*\n"
        "- *What if I learn Power BI?*\n"
        "- *Which cities have the most job postings?*\n\n"
        "Or use the navigation to explore specific modules."
    )


# ── Entity extraction helpers ─────────────────────────────────────────────────

def _extract_role_from_query(df: pd.DataFrame, query: str) -> str:
    """Try to find a known role mentioned in the query."""
    q = query.lower()
    # Check against top roles
    top_roles = df[COL_TITLE].value_counts().head(200).index.tolist()
    for role in top_roles:
        if role.lower() in q:
            return role
    # Broad keyword matches
    role_keywords = {
        "data analyst": "Data Analyst",
        "data scientist": "Data Scientist",
        "software engineer": "Software Engineer",
        "software developer": "Software Developer",
        "data engineer": "Data Engineer",
        "product manager": "Product Manager",
        "business analyst": "Business Analyst",
        "machine learning engineer": "Machine Learning Engineer",
        "devops engineer": "Devops Engineer",
        "full stack developer": "Full Stack Developer",
        "java developer": "Java Developer",
        "python developer": "Python Developer",
        "frontend developer": "Frontend Developer",
        "backend developer": "Backend Developer",
        "sales executive": "Sales Executive",
    }
    for kw, role in role_keywords.items():
        if kw in q:
            return role
    return ""


def _extract_skills_from_query(df: pd.DataFrame, query: str) -> list:
    """Extract skill names mentioned in query."""
    from modules.feature_engineering import get_skill_frequency
    top_skills = get_skill_frequency(df, top_n=100)["skill"].str.lower().tolist()
    q_lower = query.lower()
    found = []
    for skill in top_skills:
        if skill.lower() in q_lower:
            found.append(skill.title())
    return found


def _extract_multiple_roles(df: pd.DataFrame, query: str) -> list:
    """Extract two or more roles for comparison."""
    roles = []
    top_roles = df[COL_TITLE].value_counts().head(100).index.tolist()
    q = query.lower()
    for role in top_roles:
        if role.lower() in q:
            roles.append(role)
        if len(roles) >= 2:
            break
    if len(roles) < 2:
        # Keyword fallback
        keywords = ["data analyst", "business analyst", "software engineer",
                    "data scientist", "product manager", "data engineer"]
        for kw in keywords:
            if kw in q and kw.title() not in [r.lower() for r in roles]:
                roles.append(kw.title())
            if len(roles) >= 2:
                break
    return roles
