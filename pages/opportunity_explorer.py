"""CareerPulse AI — Opportunity Explorer"""

import streamlit as st
import pandas as pd

from modules.ml_engine import find_opportunities
from modules.data_loader import COL_TITLE, COL_COMPANY
from modules.ui_components import page_header, disclaimer_box, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Opportunity Explorer", "Find actual job postings from the dataset that match your profile", badge="🔍"),
                unsafe_allow_html=True)

    st.markdown("""
    <div class="cp-card">
      <strong>How it works</strong><br>
      <span style="color:#9ca3c0;font-size:13px;">
        Enter your profile and the system filters actual records from the uploaded dataset
        that match your skills, role preference, location, and experience.
        Only real postings from the dataset are shown — no synthetic records.
      </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        skills_raw = st.text_area(
            "Your Skills (one per line or comma-separated)",
            placeholder="Python\nSQL\nPandas\nTableau",
            height=120, key="opp_skills",
        )
        target_role = st.text_input("Target Role (optional, partial match OK)",
                                    placeholder="Data Analyst", key="opp_role")

    with col2:
        top_locs = df["location_primary"].value_counts().head(40).index.tolist()
        location = st.selectbox("Preferred Location", ["Any"] + top_locs, key="opp_loc")
        exp_min  = st.slider("Your Experience (years)", 0, 25, 1, key="opp_exp")
        top_n    = st.slider("Max results to show", 5, 50, 20, key="opp_topn")

    search = st.button("🔍 Find Opportunities", type="primary")

    if not search:
        st.markdown("""
        <div style="text-align:center; padding:40px; color:#6b7280;">
          <div style="font-size:40px;">🔍</div>
          <div style="font-size:15px; margin-top:8px;">
            Fill in your profile and click <strong>Find Opportunities</strong>.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    user_skills = [s.strip().title() for s in skills_raw.replace(",", "\n").split("\n") if s.strip()]

    with st.spinner("Searching dataset…"):
        results = find_opportunities(
            df, user_skills, target_role,
            location if location != "Any" else "",
            float(exp_min), top_n=top_n,
        )

    st.markdown("---")
    if results.empty:
        st.warning("No matching postings found. Try broadening your filters.")
        return

    st.markdown(f"### 🎯 {len(results)} Matching Postings Found")
    st.markdown(f"*Showing actual records from the uploaded dataset, ranked by skill match score.*")

    for i, row in results.iterrows():
        ms = row.get("match_score", 0) * 100
        bar_color = "#10b981" if ms >= 50 else "#f59e0b" if ms >= 20 else "#9ca3c0"

        sal_txt = ""
        if pd.notna(row.get("min_salary_lpa")) and row["min_salary_lpa"] > 0:
            sal_txt = f"₹{row['min_salary_lpa']:.1f} – ₹{row['max_salary_lpa']:.1f} LPA"
        else:
            sal_txt = "Salary not disclosed"

        exp_txt = row.get("experience", "N/A")
        loc_txt = row.get("location_primary", row.get("location", "N/A"))

        st.markdown(f"""
        <div class="cp-card" style="margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="flex:1;">
              <div style="font-size:15px; font-weight:700; color:#e8eaf0;">{row[COL_TITLE]}</div>
              <div style="font-size:13px; color:#9ca3c0; margin-top:3px;">
                🏢 {row[COL_COMPANY]} &nbsp;·&nbsp;
                📍 {loc_txt} &nbsp;·&nbsp;
                📅 {exp_txt} &nbsp;·&nbsp;
                💰 {sal_txt}
              </div>
            </div>
            <div style="font-size:20px; font-weight:800; color:{bar_color}; min-width:60px; text-align:right;">
              {ms:.0f}%
            </div>
          </div>
          <div style="margin-top:10px;">
            <div class="cp-bar-outer">
              <div class="cp-bar-inner" style="width:{ms}%; background:{bar_color};"></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Full table toggle
    with st.expander("📋 View as Table"):
        display_cols = [c for c in [COL_TITLE, COL_COMPANY, "location_primary",
                                     "experience", "salary", "match_score"] if c in results.columns]
        display_df = results[display_cols].copy()
        display_df.columns = [c.replace("_", " ").title() for c in display_df.columns]
        if "Match Score" in display_df.columns:
            display_df["Match Score"] = (display_df["Match Score"] * 100).round(1).astype(str) + "%"
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown(disclaimer_box(
        "Only actual records from the uploaded dataset are shown. "
        "Match score reflects skill overlap — not a hiring guarantee."
    ), unsafe_allow_html=True)
