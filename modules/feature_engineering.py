"""
CareerPulse AI — Feature Engineering
Derives analytical features from cleaned dataset for analytics and ML.
"""

import re
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import pandas as pd
import streamlit as st

from modules.data_loader import (
    COL_TITLE, COL_COMPANY, COL_SKILLS, COL_LOCATION,
    COL_MIN_SAL, COL_MAX_SAL, COL_MIN_EXP, COL_MAX_EXP,
    COL_RATING, COL_REVIEWS, COL_UPLOADED,
)


# ── Skill analytics ──────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_skill_frequency(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """Global skill frequency across all postings."""
    counter: Counter = Counter()
    for skills in df["skills_list"]:
        counter.update(skills)
    rows = [{"skill": s, "count": c, "pct": round(c / len(df) * 100, 2)}
            for s, c in counter.most_common(top_n)]
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_skills_by_role(df: pd.DataFrame, role: str, top_n: int = 20) -> pd.DataFrame:
    """Top skills for a specific job title."""
    sub = df[df[COL_TITLE].str.lower() == role.lower()]
    if sub.empty:
        # fuzzy: contains
        sub = df[df[COL_TITLE].str.lower().str.contains(role.lower(), na=False)]
    counter: Counter = Counter()
    for skills in sub["skills_list"]:
        counter.update(skills)
    total = len(sub)
    rows = [{"skill": s, "count": c, "pct": round(c / total * 100, 2) if total else 0}
            for s, c in counter.most_common(top_n)]
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_skills_by_location(df: pd.DataFrame, location: str, top_n: int = 20) -> pd.DataFrame:
    sub = df[df["location_primary"].str.lower() == location.lower()]
    counter: Counter = Counter()
    for skills in sub["skills_list"]:
        counter.update(skills)
    total = len(sub)
    rows = [{"skill": s, "count": c, "pct": round(c / total * 100, 2) if total else 0}
            for s, c in counter.most_common(top_n)]
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_skill_cooccurrence(df: pd.DataFrame, min_count: int = 10, max_skills: int = 30) -> pd.DataFrame:
    """Pairwise skill co-occurrence matrix (top skills only)."""
    # limit to top skills for performance
    top_skills = set(get_skill_frequency(df, top_n=max_skills)["skill"].tolist())
    pair_counter: Counter = Counter()
    for skills in df["skills_list"]:
        filtered = [s for s in skills if s in top_skills]
        for a, b in combinations(sorted(filtered), 2):
            pair_counter[(a, b)] += 1
    rows = [{"source": a, "target": b, "weight": w}
            for (a, b), w in pair_counter.items() if w >= min_count]
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_skill_by_exp_bucket(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Skill frequency broken down by experience bucket."""
    records = []
    for bucket in df["exp_bucket"].unique():
        sub = df[df["exp_bucket"] == bucket]
        counter: Counter = Counter()
        for skills in sub["skills_list"]:
            counter.update(skills)
        for skill, cnt in counter.most_common(top_n):
            records.append({"exp_bucket": bucket, "skill": skill, "count": cnt})
    return pd.DataFrame(records)


# ── Role analytics ────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_role_demand(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    vc = df[COL_TITLE].value_counts().head(top_n).reset_index()
    vc.columns = ["role", "count"]
    vc["pct"] = (vc["count"] / len(df) * 100).round(2)
    return vc


@st.cache_data(show_spinner=False)
def get_role_category_demand(df: pd.DataFrame) -> pd.DataFrame:
    vc = df["role_category"].value_counts().reset_index()
    vc.columns = ["category", "count"]
    vc["pct"] = (vc["count"] / len(df) * 100).round(2)
    return vc


@st.cache_data(show_spinner=False)
def get_role_salary_stats(df: pd.DataFrame, role: str) -> dict:
    sub = df[df[COL_TITLE].str.lower() == role.lower()]
    if sub.empty:
        sub = df[df[COL_TITLE].str.lower().str.contains(role.lower(), na=False)]
    sal = sub["mid_salary_lpa"].dropna()
    if sal.empty:
        return {}
    return {
        "count": len(sub),
        "salary_count": len(sal),
        "mean_lpa": round(sal.mean(), 2),
        "median_lpa": round(sal.median(), 2),
        "min_lpa": round(sal.min(), 2),
        "max_lpa": round(sal.max(), 2),
        "p25_lpa": round(sal.quantile(0.25), 2),
        "p75_lpa": round(sal.quantile(0.75), 2),
    }


# ── Location analytics ────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_location_demand(df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    vc = df["location_primary"].value_counts().head(top_n).reset_index()
    vc.columns = ["location", "count"]
    vc["pct"] = (vc["count"] / len(df) * 100).round(2)
    return vc


@st.cache_data(show_spinner=False)
def get_location_salary_stats(df: pd.DataFrame) -> pd.DataFrame:
    grp = df[df["salary_disclosed"]].groupby("location_primary")["mid_salary_lpa"]
    stats = grp.agg(["count", "mean", "median", "min", "max"]).reset_index()
    stats.columns = ["location", "salary_count", "mean_lpa", "median_lpa", "min_lpa", "max_lpa"]
    stats = stats[stats["salary_count"] >= 10].sort_values("mean_lpa", ascending=False)
    return stats.round(2)


# ── Company analytics ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_company_stats(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    grp = df.groupby(COL_COMPANY).agg(
        postings=("jobId", "count"),
        avg_rating=(COL_RATING, "mean"),
        review_count=(COL_REVIEWS, "mean"),
        avg_min_sal=(COL_MIN_SAL, "mean"),
        avg_max_sal=(COL_MAX_SAL, "mean"),
        locations=("location_primary", lambda x: x.nunique()),
        unique_roles=(COL_TITLE, "nunique"),
    ).reset_index()
    grp = grp.rename(columns={COL_COMPANY: "company"})
    grp["avg_rating"] = grp["avg_rating"].round(2)
    grp["avg_min_lpa"] = (grp["avg_min_sal"] / 100_000).round(2)
    grp["avg_max_lpa"] = (grp["avg_max_sal"] / 100_000).round(2)
    return grp.sort_values("postings", ascending=False).head(top_n)


# ── Salary analytics ──────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_salary_distribution(df: pd.DataFrame) -> pd.DataFrame:
    sal = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()]["mid_salary_lpa"]
    # Create histogram buckets
    bins = [0, 2, 4, 6, 8, 10, 15, 20, 30, 50, 100, 500]
    labels = ["<2L", "2–4L", "4–6L", "6–8L", "8–10L", "10–15L",
              "15–20L", "20–30L", "30–50L", "50–100L", ">100L"]
    bucketed = pd.cut(sal, bins=bins, labels=labels, right=True)
    vc = bucketed.value_counts().sort_index().reset_index()
    vc.columns = ["range", "count"]
    return vc


@st.cache_data(show_spinner=False)
def get_salary_by_exp(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna() & df["exp_mid"].notna()]
    grp = sub.groupby("exp_bucket")["mid_salary_lpa"].agg(["mean", "median", "count"]).reset_index()
    grp.columns = ["exp_bucket", "mean_lpa", "median_lpa", "count"]
    # Preserve meaningful order
    order = ["Fresher (0 yrs)", "0–2 Years", "2–5 Years", "5–8 Years", "8–12 Years", "12+ Years", "Not Specified"]
    grp["_order"] = grp["exp_bucket"].map({b: i for i, b in enumerate(order)})
    grp = grp.sort_values("_order").drop(columns=["_order"])
    return grp.round(2)


# ── Experience analytics ──────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_exp_distribution(df: pd.DataFrame) -> pd.DataFrame:
    vc = df["exp_bucket"].value_counts().reset_index()
    vc.columns = ["exp_bucket", "count"]
    order = ["Fresher (0 yrs)", "0–2 Years", "2–5 Years", "5–8 Years", "8–12 Years", "12+ Years", "Not Specified"]
    vc["_order"] = vc["exp_bucket"].map({b: i for i, b in enumerate(order)})
    return vc.sort_values("_order").drop(columns=["_order"])


# ── Career matching helpers ───────────────────────────────────────────────────

def match_roles_to_skills(df: pd.DataFrame, user_skills: list, top_n: int = 15) -> pd.DataFrame:
    """
    Match user skill list against job postings and return top roles.
    Score = Jaccard-like overlap: |user ∩ job_skills| / |user ∪ job_skills|
    Vectorized: explodes skills once, groups by role for performance.
    """
    if not user_skills:
        return pd.DataFrame()

    user_set = set(s.strip().title() for s in user_skills)
    n_user = len(user_set)

    # Compute per-posting intersection size using exploded skills
    # Build a boolean mask: True when the skill is in user_set
    exploded = df[[COL_TITLE, "skills_list", "skills_count"]].copy()
    exploded = exploded[exploded["skills_count"] > 0]

    # Compute matched count per row via list comprehension (fast, no iterrows)
    exploded = exploded.copy()
    exploded["matched_count"] = [
        len(user_set.intersection(sk)) for sk in exploded["skills_list"]
    ]
    exploded = exploded[exploded["matched_count"] > 0]

    if exploded.empty:
        return pd.DataFrame()

    # Union size = n_user + skills_count - matched_count
    exploded["union_count"] = n_user + exploded["skills_count"] - exploded["matched_count"]
    exploded["jaccard"] = exploded["matched_count"] / exploded["union_count"].clip(lower=1)

    # Group by role
    grp = exploded.groupby(COL_TITLE).agg(
        total_score=("jaccard", "sum"),
        count=("jaccard", "count"),
    ).reset_index()
    grp["match_score"] = (grp["total_score"] / grp["count"] * 100).round(1)
    grp = grp.rename(columns={COL_TITLE: "role"}).drop(columns=["total_score"])
    grp = grp.sort_values("match_score", ascending=False).head(top_n * 3)

    # Build matched/missing per top role
    results = []
    for _, row in grp.head(top_n).iterrows():
        role = row["role"]
        role_sub = exploded[exploded[COL_TITLE] == role]
        all_job_skills: Counter = Counter()
        matched_skills: set = set()
        for sk_list in df[df[COL_TITLE] == role]["skills_list"]:
            all_job_skills.update(sk_list)
            matched_skills |= user_set.intersection(sk_list)
        missing_counter = Counter({s: c for s, c in all_job_skills.items() if s not in user_set})
        results.append({
            "role": role,
            "match_score": row["match_score"],
            "postings": int(row["count"]),
            "matched_skills": sorted(matched_skills),
            "top_missing_skills": [s for s, _ in missing_counter.most_common(5)],
        })

    results_df = pd.DataFrame(results).sort_values("match_score", ascending=False).reset_index(drop=True)

    # Merge salary stats
    sal_stats = df[df["salary_disclosed"]].groupby(COL_TITLE)["mid_salary_lpa"].agg(
        ["mean", "median"]).rename(columns={"mean": "avg_lpa", "median": "med_lpa"}).round(2)
    results_df = results_df.merge(sal_stats, left_on="role", right_index=True, how="left")
    return results_df.reset_index(drop=True)


def compute_skill_gap(df: pd.DataFrame, user_skills: list, target_role: str, top_n: int = 15) -> dict:
    """Compute skill gap between user skills and target role requirements."""
    sub = df[df[COL_TITLE].str.lower() == target_role.lower()]
    if sub.empty:
        sub = df[df[COL_TITLE].str.lower().str.contains(target_role.lower(), na=False)]
    if sub.empty:
        return {"error": f"No postings found for role: {target_role}"}

    user_set = set(s.strip().title() for s in user_skills)

    counter: Counter = Counter()
    for skills in sub["skills_list"]:
        counter.update(skills)

    total = len(sub)
    all_role_skills = {s: c for s, c in counter.most_common()}

    present   = {s: c for s, c in all_role_skills.items() if s in user_set}
    missing_  = {s: c for s, c in all_role_skills.items() if s not in user_set}

    # Rank missing by frequency
    missing_ranked = sorted(missing_.items(), key=lambda x: x[1], reverse=True)[:top_n]

    match_pct = round(len(present) / max(len(all_role_skills), 1) * 100, 1)

    return {
        "role": target_role,
        "total_postings": total,
        "total_role_skills": len(all_role_skills),
        "user_skills_count": len(user_set),
        "present_skills": present,
        "missing_skills": dict(missing_ranked),
        "match_pct": match_pct,
        "top_n_skills": [(s, c, round(c/total*100, 1)) for s, c in counter.most_common(top_n)],
    }


def simulate_skill_addition(df: pd.DataFrame, user_skills: list, new_skills: list) -> dict:
    """Compare match before/after adding new skills."""
    before = match_roles_to_skills(df, user_skills, top_n=10)
    after  = match_roles_to_skills(df, user_skills + new_skills, top_n=10)

    before_roles = set(before["role"].tolist()) if not before.empty else set()
    after_roles  = set(after["role"].tolist())  if not after.empty  else set()
    new_roles    = after_roles - before_roles

    before_postings = before["postings"].sum() if not before.empty else 0
    after_postings  = after["postings"].sum()  if not after.empty  else 0

    before_score = before["match_score"].mean() if not before.empty else 0
    after_score  = after["match_score"].mean()  if not after.empty  else 0

    return {
        "before": before,
        "after": after,
        "new_roles": sorted(new_roles),
        "before_postings": int(before_postings),
        "after_postings": int(after_postings),
        "before_avg_score": round(float(before_score), 1),
        "after_avg_score": round(float(after_score), 1),
        "score_delta": round(float(after_score - before_score), 1),
        "postings_delta": int(after_postings - before_postings),
    }


# ── KPI summary ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_kpis(df: pd.DataFrame) -> dict:
    sal_df = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()]
    return {
        "total_postings": len(df),
        "unique_companies": df[COL_COMPANY].nunique(),
        "unique_roles": df[COL_TITLE].nunique(),
        "unique_locations": df["location_primary"].nunique(),
        "unique_skills": _count_unique_skills_fe(df),
        "salary_coverage_pct": round(df["salary_disclosed"].mean() * 100, 1),
        "avg_salary_lpa": round(sal_df["mid_salary_lpa"].mean(), 2) if not sal_df.empty else None,
        "median_salary_lpa": round(sal_df["mid_salary_lpa"].median(), 2) if not sal_df.empty else None,
        "exp_coverage_pct": round(df[COL_MIN_EXP].notna().mean() * 100, 1),
        "top_location": df["location_primary"].value_counts().index[0] if len(df) else "N/A",
        "top_company": df[COL_COMPANY].value_counts().index[0] if len(df) else "N/A",
        "top_role": df[COL_TITLE].value_counts().index[0] if len(df) else "N/A",
    }


def _count_unique_skills_fe(df: pd.DataFrame) -> int:
    s = set()
    for skills in df["skills_list"]:
        s.update(skills)
    return len(s)


# ── Related roles via skill overlap ──────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_related_roles(df: pd.DataFrame, role: str, top_n: int = 8) -> pd.DataFrame:
    """Find roles with overlapping skill requirements. Vectorized for performance."""
    sub = df[df[COL_TITLE].str.lower().str.contains(role.lower(), na=False)]
    if sub.empty:
        return pd.DataFrame()

    role_skills: Counter = Counter()
    for s in sub["skills_list"]:
        role_skills.update(s)
    role_set = set(dict(role_skills.most_common(15)).keys())
    n_role = len(role_set)
    if n_role == 0:
        return pd.DataFrame()

    # Score other roles using vectorized list comprehension
    other = df[~df[COL_TITLE].str.lower().str.contains(role.lower(), na=False)].copy()
    other = other[other["skills_count"] > 0]

    # Intersection and union sizes via list comprehension (no iterrows)
    inter = [len(role_set.intersection(sk)) for sk in other["skills_list"]]
    other = other.copy()
    other["inter"] = inter
    other = other[other["inter"] > 0]
    if other.empty:
        return pd.DataFrame()

    other["union_n"] = n_role + other["skills_count"] - other["inter"]
    other["jaccard"] = other["inter"] / other["union_n"].clip(lower=1)

    grp = other.groupby(COL_TITLE).agg(
        overlap=("jaccard", "sum"),
        count=("jaccard", "count"),
    ).reset_index()
    grp["overlap_score"] = (grp["overlap"] / grp["count"] * 100).round(1)
    grp = grp.rename(columns={COL_TITLE: "role", "count": "postings"})
    return grp.sort_values("overlap_score", ascending=False).head(top_n)[
        ["role", "overlap_score", "postings"]
    ].reset_index(drop=True)
