"""CareerPulse AI — My Career (Personalized Profile + Skill Gap)"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.feature_engineering import (
    match_roles_to_skills, compute_skill_gap, get_role_salary_stats,
    get_skill_frequency,
)
from modules.ml_engine import compute_market_alignment
from modules.data_loader import COL_TITLE
from modules.ui_components import page_header, score_bar, disclaimer_box, skill_pills, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("My Career", "Personalized career profile and market alignment", badge="🎯"),
                unsafe_allow_html=True)

    # ── Profile Input ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="cp-card">
      <strong>👤 Enter Your Career Profile</strong><br>
      <span style="color:#9ca3c0; font-size:13px;">
        All analysis is computed against actual job postings in the dataset.
      </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        skills_input = st.text_area(
            "Your Current Skills (one per line or comma-separated)",
            placeholder="Python\nSQL\nExcel\nTableau\nPandas",
            height=120, key="mc_skills",
        )
        target_role = st.text_input(
            "Target Role (leave blank for general analysis)",
            placeholder="Data Analyst", key="mc_role",
        )

    with col2:
        exp_years = st.slider("Your Experience (years)", 0, 25, 2, key="mc_exp")
        top_locs = df["location_primary"].value_counts().head(40).index.tolist()
        pref_location = st.selectbox("Preferred Location", ["Any"] + top_locs, key="mc_loc")

    analyze = st.button("🔍 Analyze My Career Profile", type="primary", use_container_width=False)

    if not analyze:
        st.markdown("""
        <div style="text-align:center; padding:40px; color:#6b7280;">
          <div style="font-size:40px;">🎯</div>
          <div style="font-size:16px; margin-top:8px;">
            Enter your profile and click <strong>Analyze</strong> to see your market alignment.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Parse skills
    raw_skills = skills_input.replace(",", "\n")
    user_skills = [s.strip().title() for s in raw_skills.split("\n") if s.strip()]

    if not user_skills:
        st.warning("Please enter at least one skill.")
        return

    loc_param = pref_location if pref_location != "Any" else None

    # ── Market Alignment Score ─────────────────────────────────────────────
    alignment = compute_market_alignment(
        df, user_skills, target_role, float(exp_years), pref_location
    )

    st.markdown("---")
    st.markdown("### 📊 Market Alignment Analysis")

    score = alignment["score"]
    score_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
    score_label = "Strong" if score >= 70 else "Moderate" if score >= 40 else "Limited"

    sa, sb, sc = st.columns([1, 2, 1])
    with sb:
        st.markdown(f"""
        <div class="cp-kpi" style="text-align:center; padding:32px;">
          <div style="font-size:13px; font-weight:700; letter-spacing:0.1em; color:#9ca3c0;
                      text-transform:uppercase; margin-bottom:12px;">Market Alignment</div>
          <div style="font-size:64px; font-weight:900; color:{score_color};
                      letter-spacing:-0.04em;">{score:.0f}%</div>
          <div style="font-size:15px; color:{score_color}; font-weight:600;
                      margin-top:4px;">{score_label} Match</div>
          <div style="font-size:12px; color:#6b7280; margin-top:8px;">
            Based on {alignment['relevant_postings']:,} relevant postings
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Breakdown
    bd_cols = st.columns(3)
    bd_data = [
        ("Skill Match", alignment["skill_score"], "#4f8ef7"),
        ("Location Fit", alignment["location_score"], "#8b5cf6"),
        ("Experience Fit", alignment["experience_score"], "#14b8a6"),
    ]
    for col, (label, val, color) in zip(bd_cols, bd_data):
        with col:
            st.markdown(f"""
            <div class="cp-kpi">
              <div class="cp-kpi-val" style="color:{color};">{val:.0f}%</div>
              <div class="cp-kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(disclaimer_box(
        "Market alignment is a dataset-derived metric, not a hiring probability."
    ), unsafe_allow_html=True)

    # ── Role Matches ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💼 Roles That Match Your Skills")
    matches = match_roles_to_skills(df, user_skills, top_n=15)

    if matches.empty:
        st.info("No role matches found. Try adding more skills.")
    else:
        for _, row in matches.head(8).iterrows():
            ms = row["match_score"]
            bar_color = "#10b981" if ms >= 60 else "#f59e0b" if ms >= 30 else "#ef4444"
            matched_str = ", ".join(row["matched_skills"][:6]) if row["matched_skills"] else "—"
            missing_str = ", ".join(row["top_missing_skills"][:4]) if row["top_missing_skills"] else "—"
            avg_lpa = f"₹{row['avg_lpa']:.1f}" if pd.notna(row.get('avg_lpa')) else "N/A"
            st.markdown(f"""
            <div class="cp-card">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <div style="font-size:16px; font-weight:700; color:#e8eaf0;">{row['role']}</div>
                  <div style="font-size:12px; color:#9ca3c0; margin-top:4px;">
                    {row['postings']:,} postings · Avg salary {avg_lpa} LPA
                  </div>
                </div>
                <div style="font-size:22px; font-weight:800; color:{bar_color};">{ms:.0f}%</div>
              </div>
              <div style="margin-top:10px;">
                <div class="cp-bar-outer">
                  <div class="cp-bar-inner" style="width:{ms}%; background:{bar_color};"></div>
                </div>
              </div>
              <div style="margin-top:8px; font-size:12px; color:#9ca3c0;">
                ✅ Matched: {matched_str}<br>
                ❌ Frequently observed missing: {missing_str}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Skill Gap Analysis ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 Skill Gap Analysis")

    analysis_role = target_role if target_role else (matches.iloc[0]["role"] if not matches.empty else "")
    if not analysis_role:
        st.info("Enter a target role to see skill gap analysis.")
        return

    gap = compute_skill_gap(df, user_skills, analysis_role)
    if "error" in gap:
        st.info(gap["error"])
        return

    st.markdown(f"""
    <div class="cp-card">
      <div style="font-size:15px; font-weight:700; color:#e8eaf0;">
        Skill Gap: <span style="color:#4f8ef7;">{analysis_role}</span>
      </div>
      <div style="font-size:13px; color:#9ca3c0; margin-top:4px;">
        {gap['total_postings']:,} postings analyzed · {gap['total_role_skills']} unique skills observed
        · Dataset skill match: <span style="color:#10b981; font-weight:700;">{gap['match_pct']}%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**✅ Skills You Have (observed in role)**")
        present_skills = list(gap["present_skills"].keys())
        if present_skills:
            st.markdown(skill_pills(present_skills, style="present"), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#9ca3c0;font-size:13px;'>None of your skills matched.</span>",
                        unsafe_allow_html=True)

    with g2:
        st.markdown("**❌ Frequently Observed Skills You Don't Have**")
        missing_skills = list(gap["missing_skills"].keys())
        if missing_skills:
            st.markdown(skill_pills(missing_skills, style="missing"), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#10b981;font-size:13px;'>Great! No major gaps detected.</span>",
                        unsafe_allow_html=True)

    # Missing skill frequency chart
    if gap["missing_skills"]:
        miss_df = pd.DataFrame(
            list(gap["missing_skills"].items()), columns=["skill", "count"]
        ).head(15)
        pcts = [round(c / gap["total_postings"] * 100, 1) for c in miss_df["count"]]
        miss_df["pct"] = pcts

        fig = go.Figure(go.Bar(
            x=miss_df["pct"], y=miss_df["skill"], orientation="h",
            marker_color="#ef4444",
            text=miss_df["pct"].apply(lambda x: f"{x}%"),
            textposition="outside",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3c0", family="Inter"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=380, title="Missing Skills Ranked by Observed Frequency",
            yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
            xaxis=dict(showgrid=True, gridcolor="#2d3148", title="% of Role Postings"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("*Skills ranked by frequency in actual postings for the target role.*")
