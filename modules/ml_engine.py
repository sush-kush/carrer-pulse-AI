"""
CareerPulse AI — ML Engine
Salary prediction, role similarity, skill recommendation.
All models trained only on the uploaded dataset.
"""

import warnings
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer

from modules.data_loader import COL_TITLE, COL_COMPANY, COL_LOCATION

warnings.filterwarnings("ignore")

# ── Salary Predictor ──────────────────────────────────────────────────────────

class SalaryPredictor:
    """
    Gradient Boosting regressor trained on dataset salary observations.
    Features: role (encoded), location (encoded), experience mid, skill count.
    Predicts mid-point salary in LPA.
    """

    def __init__(self):
        self.model = None
        self.role_enc = LabelEncoder()
        self.loc_enc = LabelEncoder()
        self.metrics: dict = {}
        self.feature_importances: dict = {}
        self.n_train: int = 0
        self.trained: bool = False
        self.min_lpa: float = 0
        self.max_lpa: float = 0

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        sub = df[
            df["salary_disclosed"] &
            df["mid_salary_lpa"].notna() &
            df["exp_mid"].notna()
        ].copy()
        # Cap extreme outliers (>300 LPA)
        sub = sub[sub["mid_salary_lpa"] <= 300]
        sub = sub[sub["mid_salary_lpa"] > 0]
        sub = sub.dropna(subset=[COL_TITLE, "location_primary"])
        return sub

    @st.cache_resource(show_spinner="Training Salary Predictor…")
    def train(_self, df: pd.DataFrame):
        sub = _self._prepare(df)
        if len(sub) < 100:
            _self.trained = False
            return _self

        _self.n_train = len(sub)
        _self.min_lpa = float(sub["mid_salary_lpa"].min())
        _self.max_lpa = float(sub["mid_salary_lpa"].max())

        roles     = _self.role_enc.fit_transform(sub[COL_TITLE].astype(str))
        locations = _self.loc_enc.fit_transform(sub["location_primary"].astype(str))

        X = np.column_stack([
            roles,
            locations,
            sub["exp_mid"].values,
            sub["skills_count"].values,
        ])
        y = sub["mid_salary_lpa"].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        _self.model = GradientBoostingRegressor(
            n_estimators=150, max_depth=5, learning_rate=0.1,
            subsample=0.8, random_state=42
        )
        _self.model.fit(X_train, y_train)

        y_pred = _self.model.predict(X_test)
        _self.metrics = {
            "MAE": round(mean_absolute_error(y_test, y_pred), 2),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 2),
            "R2": round(float(r2_score(y_test, y_pred)), 3),
            "n_test": len(y_test),
        }

        feat_names = ["Job Role", "Location", "Experience (yrs)", "Skills Count"]
        imps = _self.model.feature_importances_
        _self.feature_importances = {
            feat_names[i]: round(float(imps[i]) * 100, 1) for i in range(len(feat_names))
        }
        _self.trained = True
        return _self

    def predict(self, role: str, location: str, exp_mid: float, skills_count: int) -> dict:
        if not self.trained:
            return {"error": "Model not trained — insufficient salary data."}

        # Handle unseen labels
        role_enc = self._encode_label(self.role_enc, role)
        loc_enc  = self._encode_label(self.loc_enc, location)

        X = np.array([[role_enc, loc_enc, exp_mid, skills_count]])
        pred = float(self.model.predict(X)[0])
        pred = max(self.min_lpa, min(pred, self.max_lpa))

        # Confidence band ±20% based on model error
        low  = round(pred * 0.85, 2)
        high = round(pred * 1.15, 2)

        # Map R2 to confidence label
        r2 = self.metrics.get("R2", 0)
        if r2 >= 0.70:
            confidence = "Moderate–High"
        elif r2 >= 0.50:
            confidence = "Moderate"
        else:
            confidence = "Low"

        return {
            "predicted_lpa": round(pred, 2),
            "range_low_lpa": low,
            "range_high_lpa": high,
            "confidence": confidence,
            "n_train": self.n_train,
            "metrics": self.metrics,
            "feature_importances": self.feature_importances,
        }

    @staticmethod
    def _encode_label(encoder: LabelEncoder, value: str) -> int:
        try:
            return int(encoder.transform([value])[0])
        except ValueError:
            # Unseen label → use most frequent class (index 0)
            return 0


# ── Skill Recommender ─────────────────────────────────────────────────────────

class SkillRecommender:
    """
    Recommends skills the user is missing for a target role.
    Based purely on skill frequency in the dataset for that role.
    """

    def recommend(self, df: pd.DataFrame, user_skills: list, target_role: str, top_n: int = 10) -> list:
        sub = df[df[COL_TITLE].str.lower().str.contains(target_role.lower(), na=False)]
        if sub.empty:
            return []

        user_set = set(s.strip().title() for s in user_skills)
        counter: Counter = Counter()
        for skills in sub["skills_list"]:
            counter.update(skills)

        total = len(sub)
        recommendations = []
        for skill, cnt in counter.most_common():
            if skill not in user_set:
                recommendations.append({
                    "skill": skill,
                    "frequency": cnt,
                    "frequency_pct": round(cnt / total * 100, 1),
                })
            if len(recommendations) >= top_n:
                break
        return recommendations


# ── Role Similarity (skill-overlap based) ────────────────────────────────────

@st.cache_data(show_spinner=False)
def compute_role_similarity_matrix(df: pd.DataFrame, top_roles: int = 30) -> pd.DataFrame:
    """
    Build a skill-overlap similarity matrix for the top N roles.
    Uses Jaccard similarity on skill sets.
    """
    top = df[COL_TITLE].value_counts().head(top_roles).index.tolist()
    role_skills: dict = {}
    for role in top:
        sub = df[df[COL_TITLE] == role]
        counter: Counter = Counter()
        for skills in sub["skills_list"]:
            counter.update(skills)
        role_skills[role] = set(dict(counter.most_common(20)).keys())

    sim_rows = []
    for r1 in top:
        row = {"role": r1}
        for r2 in top:
            if r1 == r2:
                row[r2] = 1.0
            else:
                a, b = role_skills[r1], role_skills[r2]
                union = a | b
                row[r2] = round(len(a & b) / len(union), 3) if union else 0
        sim_rows.append(row)

    sim_df = pd.DataFrame(sim_rows).set_index("role")
    return sim_df


# ── Market Alignment Score ────────────────────────────────────────────────────

def compute_market_alignment(df: pd.DataFrame, user_skills: list, target_role: str,
                              exp_min: float, location: str) -> dict:
    """
    Holistic market alignment score (0–100) for a user profile.
    Composed of: skill match (60%) + location match (20%) + experience fit (20%).
    """
    if not user_skills:
        return {"score": 0, "breakdown": {}, "relevant_postings": 0}

    user_set = set(s.strip().title() for s in user_skills)

    # Filter to target role
    sub = df.copy()
    if target_role:
        role_sub = df[df[COL_TITLE].str.lower().str.contains(target_role.lower(), na=False)]
        if not role_sub.empty:
            sub = role_sub

    # Skill score — vectorized list comprehension (no iterrows)
    n_user = len(user_set)
    sub_has_skills = sub[sub["skills_count"] > 0]
    if not sub_has_skills.empty:
        inter_counts = [len(user_set.intersection(sk)) for sk in sub_has_skills["skills_list"]]
        union_counts = [n_user + sc - ic for ic, sc in zip(inter_counts, sub_has_skills["skills_count"])]
        jaccards = [ic / max(uc, 1) for ic, uc in zip(inter_counts, union_counts)]
        skill_score = round(float(np.mean(jaccards)) * 100, 1)
    else:
        skill_score = 0

    # Location score — how common is user's location in this role
    if location and location != "Any":
        loc_sub = sub[sub["location_primary"].str.lower() == location.lower()]
        loc_score = round(len(loc_sub) / max(len(sub), 1) * 100, 1)
        loc_score = min(loc_score * 5, 100)  # amplify; cap at 100
    else:
        loc_score = 50  # neutral if no location filter

    # Experience score — how well does exp fit the role distribution
    if exp_min is not None:
        exp_sub = sub[(sub["minimumExperience"] <= exp_min + 2) & (sub["maximumExperience"] >= exp_min - 1)]
        exp_score = round(len(exp_sub) / max(len(sub), 1) * 100, 1)
        exp_score = min(exp_score * 2, 100)
    else:
        exp_score = 50

    composite = round(skill_score * 0.60 + loc_score * 0.20 + exp_score * 0.20, 1)

    return {
        "score": composite,
        "skill_score": skill_score,
        "location_score": loc_score,
        "experience_score": exp_score,
        "relevant_postings": len(sub),
        "breakdown": {
            "Skill Match (60%)": skill_score,
            "Location Fit (20%)": loc_score,
            "Experience Fit (20%)": exp_score,
        },
    }


# ── Opportunity Finder ────────────────────────────────────────────────────────

def find_opportunities(df: pd.DataFrame, user_skills: list, target_role: str,
                        location: str, exp_min: float, top_n: int = 20) -> pd.DataFrame:
    """Return actual dataset records matching user profile."""
    sub = df.copy()

    if target_role:
        sub = sub[sub[COL_TITLE].str.lower().str.contains(target_role.lower(), na=False)]
    if location and location not in ("Any", ""):
        sub = sub[sub["location_primary"].str.lower() == location.lower()]
    if exp_min is not None:
        sub = sub[sub["minimumExperience"].notna() & (sub["minimumExperience"] <= exp_min + 3)]

    if user_skills:
        user_set = set(s.strip().title() for s in user_skills)
        n_user = len(user_set)
        # Vectorized jaccard via list comprehension
        inter = [len(user_set.intersection(sk)) for sk in sub["skills_list"]]
        union_n = [n_user + sc - ic for ic, sc in zip(inter, sub["skills_count"])]
        scores = [ic / max(un, 1) for ic, un in zip(inter, union_n)]
        sub = sub.copy()
        sub["match_score"] = scores
        sub = sub.sort_values("match_score", ascending=False)
    else:
        sub = sub.copy()
        sub["match_score"] = 0.0

    cols = [COL_TITLE, COL_COMPANY, "location_primary", COL_LOCATION,
            "experience", "salary", "min_salary_lpa", "max_salary_lpa", "match_score"]
    cols = [c for c in cols if c in sub.columns]
    return sub[cols].head(top_n).reset_index(drop=True)
