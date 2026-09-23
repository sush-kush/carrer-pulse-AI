"""
CareerPulse AI — Data Loader & Cleaner
Loads, validates, and cleans the Indian Job Market Dataset 2025.
Single source of truth: the uploaded .xlsx file.
"""

import os
import re
import warnings
import numpy as np
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")

# ── Path resolution ──────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
DEFAULT_PATH = os.path.join(_ROOT, "..", "indian-job-market-dataset-2025.xlsx")


# ── Column constants ─────────────────────────────────────────────────────────
COL_TITLE       = "title"
COL_JOB_ID      = "jobId"
COL_CURRENCY    = "currency"
COL_UPLOADED    = "jobUploaded"
COL_COMPANY     = "companyName"
COL_SKILLS      = "tagsAndSkills"
COL_EXPERIENCE  = "experience"
COL_SALARY      = "salary"
COL_LOCATION    = "location"
COL_COMPANY_ID  = "companyId"
COL_REVIEWS     = "ReviewsCount"
COL_RATING      = "AggregateRating"
COL_DESC        = "jobDescription"
COL_MIN_SAL     = "minimumSalary"
COL_MAX_SAL     = "maximumSalary"
COL_MIN_EXP     = "minimumExperience"
COL_MAX_EXP     = "maximumExperience"

REQUIRED_COLS = [
    COL_TITLE, COL_JOB_ID, COL_CURRENCY, COL_UPLOADED,
    COL_COMPANY, COL_SKILLS, COL_EXPERIENCE, COL_SALARY,
    COL_LOCATION, COL_MIN_SAL, COL_MAX_SAL,
    COL_MIN_EXP, COL_MAX_EXP,
]

# Relative-time labels from jobUploaded that imply "recent" (within ~10 days)
_RECENT_LABELS = {
    "just now", "few hours ago", "today", "1 day ago",
    "2 days ago", "3 days ago", "4 days ago", "5 days ago",
    "6 days ago", "7 days ago", "8 days ago", "9 days ago", "10 days ago",
}


# ── Main loader ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…", ttl=3600)
def load_data(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Load, validate, and clean the dataset. Returns a clean DataFrame."""
    if not os.path.exists(path):
        st.error(f"Dataset file not found at: {path}")
        st.stop()

    try:
        df = pd.read_excel(path, sheet_name="Sheet1", engine="openpyxl")
    except Exception as e:
        st.error(f"Failed to read Excel file: {e}")
        st.stop()

    df = _validate_columns(df)
    df = _clean(df)
    return df


def _validate_columns(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(f"Dataset is missing expected columns: {missing}")
        st.stop()
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # ── 1. Remove exact duplicates ────────────────────────────────────────
    df = df.drop_duplicates(subset=[COL_JOB_ID], keep="first").reset_index(drop=True)

    # ── 2. Strip whitespace from string columns ──────────────────────────
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})

    # ── 3. Normalize title & company ─────────────────────────────────────
    df[COL_TITLE]   = df[COL_TITLE].str.title().str.strip()
    df[COL_COMPANY] = df[COL_COMPANY].str.strip()

    # ── 4. Clean location — keep primary city ────────────────────────────
    df["location_raw"] = df[COL_LOCATION].copy()
    df["location_primary"] = df[COL_LOCATION].apply(_extract_primary_location)

    # ── 5. Parse salary ──────────────────────────────────────────────────
    # Replace 0 salaries (means not disclosed) with NaN
    df[COL_MIN_SAL] = df[COL_MIN_SAL].where(df[COL_MIN_SAL] > 0, np.nan)
    df[COL_MAX_SAL] = df[COL_MAX_SAL].where(df[COL_MAX_SAL] > 0, np.nan)
    df["salary_mid"] = ((df[COL_MIN_SAL] + df[COL_MAX_SAL]) / 2).where(
        df[COL_MIN_SAL].notna() & df[COL_MAX_SAL].notna()
    )
    df["salary_disclosed"] = df[COL_MIN_SAL].notna()
    # Convert to lakhs for display
    df["min_salary_lpa"] = (df[COL_MIN_SAL] / 100_000).round(2)
    df["max_salary_lpa"] = (df[COL_MAX_SAL] / 100_000).round(2)
    df["mid_salary_lpa"] = (df["salary_mid"] / 100_000).round(2)

    # ── 6. Parse experience ──────────────────────────────────────────────
    df[COL_MIN_EXP] = pd.to_numeric(df[COL_MIN_EXP], errors="coerce")
    df[COL_MAX_EXP] = pd.to_numeric(df[COL_MAX_EXP], errors="coerce")
    df["exp_mid"] = ((df[COL_MIN_EXP] + df[COL_MAX_EXP]) / 2).where(
        df[COL_MIN_EXP].notna() & df[COL_MAX_EXP].notna()
    )
    df["exp_bucket"] = df[COL_MIN_EXP].apply(_exp_bucket)

    # ── 7. Normalize skills ───────────────────────────────────────────────
    df["skills_list"] = df[COL_SKILLS].apply(_parse_skills)
    df["skills_count"] = df["skills_list"].apply(len)

    # ── 8. Recency flag from jobUploaded ─────────────────────────────────
    df["is_recent"] = df[COL_UPLOADED].str.lower().isin(_RECENT_LABELS)

    # ── 9. Normalize rating ───────────────────────────────────────────────
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")
    df[COL_REVIEWS] = pd.to_numeric(df[COL_REVIEWS], errors="coerce")

    # ── 10. Broad role category ───────────────────────────────────────────
    df["role_category"] = df[COL_TITLE].apply(_categorize_role)

    return df


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_primary_location(loc: str) -> str:
    """Return the first city in a possibly multi-city string."""
    if pd.isna(loc) or loc == "nan":
        return "Unknown"
    # Remove hybrid/remote prefixes
    loc = re.sub(r"(?i)^(hybrid\s*[-–]\s*|remote\s*[-–]\s*)", "", str(loc).strip())
    # Take first token before comma
    primary = re.split(r"[,/|]", loc)[0].strip()
    return primary if primary else "Unknown"


def _parse_skills(raw) -> list:
    """Parse comma-separated skills string into a normalized list."""
    if pd.isna(raw) or str(raw).lower() in ("nan", "none", ""):
        return []
    skills = [s.strip().title() for s in str(raw).split(",") if s.strip()]
    # Remove very short tokens (likely noise)
    skills = [s for s in skills if len(s) >= 2]
    return list(dict.fromkeys(skills))  # deduplicate preserving order


def _exp_bucket(min_exp) -> str:
    """Convert numeric minimum experience into a human bucket."""
    if pd.isna(min_exp):
        return "Not Specified"
    v = float(min_exp)
    if v == 0:
        return "Fresher (0 yrs)"
    elif v <= 2:
        return "0–2 Years"
    elif v <= 5:
        return "2–5 Years"
    elif v <= 8:
        return "5–8 Years"
    elif v <= 12:
        return "8–12 Years"
    else:
        return "12+ Years"


_ROLE_KEYWORDS = {
    "Data & Analytics":       ["data", "analyst", "analytics", "bi ", "business intelligence", "tableau", "power bi"],
    "Software Development":   ["developer", "engineer", "software", "backend", "frontend", "full stack", "fullstack"],
    "Sales & Business Dev":   ["sales", "business development", "bd ", "account executive", "relationship manager"],
    "HR & Recruitment":       ["hr ", "human resource", "recruiter", "talent", "staffing"],
    "Finance & Accounts":     ["finance", "accountant", "accounting", "tax", "audit", "cfo", "gst", "tds"],
    "Marketing":              ["marketing", "brand", "digital marketing", "seo", "content", "social media"],
    "Product Management":     ["product manager", "product lead", "product owner", "pm "],
    "DevOps & Cloud":         ["devops", "cloud", "aws", "azure", "gcp", "sre", "infrastructure"],
    "Machine Learning & AI":  ["machine learning", "ml ", "ai ", "deep learning", "nlp", "data science"],
    "Healthcare":             ["medical", "pharma", "health", "nurse", "doctor", "clinical", "hospital"],
    "Operations":             ["operations", "supply chain", "logistics", "procurement", "warehouse"],
    "Customer Support":       ["customer support", "customer service", "helpdesk", "support executive"],
    "Design":                 ["designer", "ui ", "ux ", "graphic", "creative"],
    "Consulting":             ["consultant", "consulting", "advisory"],
}


def _categorize_role(title: str) -> str:
    if pd.isna(title):
        return "Other"
    t = str(title).lower()
    for category, keywords in _ROLE_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return category
    return "Other"


# ── Quality metrics (computed once) ──────────────────────────────────────────

def get_quality_report(df: pd.DataFrame) -> dict:
    total = len(df)
    return {
        "total_records": total,
        "duplicate_removed": 0,  # already removed in clean step
        "missing_skills": int(df[COL_SKILLS].isna().sum()),
        "missing_company": int(df[COL_COMPANY].isna().sum()),
        "missing_experience": int(df[COL_MIN_EXP].isna().sum()),
        "salary_disclosed": int(df["salary_disclosed"].sum()),
        "salary_not_disclosed": int((~df["salary_disclosed"]).sum()),
        "salary_coverage_pct": round(df["salary_disclosed"].mean() * 100, 1),
        "skill_coverage_pct": round((df["skills_count"] > 0).mean() * 100, 1),
        "experience_coverage_pct": round(df[COL_MIN_EXP].notna().mean() * 100, 1),
        "location_coverage_pct": round((df["location_primary"] != "Unknown").mean() * 100, 1),
        "rating_coverage_pct": round(df[COL_RATING].notna().mean() * 100, 1),
        "unique_titles": int(df[COL_TITLE].nunique()),
        "unique_companies": int(df[COL_COMPANY].nunique()),
        "unique_locations": int(df["location_primary"].nunique()),
        "unique_skills": _count_unique_skills(df),
        "currencies": df[COL_CURRENCY].value_counts().to_dict(),
    }


def _count_unique_skills(df: pd.DataFrame) -> int:
    all_skills = set()
    for skills in df["skills_list"]:
        all_skills.update(skills)
    return len(all_skills)
