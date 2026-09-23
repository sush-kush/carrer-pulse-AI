"""CareerPulse AI — Career Path Explorer"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from collections import Counter

from modules.feature_engineering import get_skills_by_role, get_related_roles
from modules.data_loader import COL_TITLE
from modules.ui_components import page_header, disclaimer_box, skill_pills, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Career Path Explorer", "Explore possible role transitions based on skill overlap in the dataset", badge="🛤️"),
                unsafe_allow_html=True)

    st.markdown("""
    <div class="cp-card">
      <strong>How Career Paths are Derived</strong><br>
      <span style="color:#9ca3c0;font-size:13px;">
        This tool identifies roles with overlapping skill requirements in the dataset.
        A higher overlap score means more shared skill requirements between two roles.
        <br><br>
        <em>This reflects skill-pattern similarity in the dataset — not a prescribed career path.
        Actual career transitions depend on many factors beyond skills.</em>
      </span>
    </div>
    """, unsafe_allow_html=True)

    top_roles = df[COL_TITLE].value_counts().head(80).index.tolist()

    col1, col2 = st.columns(2)
    with col1:
        current_role = st.selectbox("🔵 Your Current Role (or closest match)", top_roles, key="cp_current")
    with col2:
        top_n = st.slider("Number of transition paths", 5, 15, 8, key="cp_topn")

    explore = st.button("🔍 Explore Career Paths", type="primary")

    if not explore:
        st.markdown("""
        <div style="text-align:center; padding:40px; color:#6b7280;">
          <div style="font-size:40px;">🛤️</div>
          <div style="font-size:15px; margin-top:8px;">
            Select your current role and click <strong>Explore</strong>.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    with st.spinner("Analyzing skill overlaps…"):
        related = get_related_roles(df, current_role, top_n=top_n)
        current_skills_df = get_skills_by_role(df, current_role, top_n=15)

    if related.empty:
        st.info("No related roles found for this selection.")
        return

    # ── Current role skills ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### 🔵 Current Role: **{current_role}**")
    if not current_skills_df.empty:
        st.markdown("**Key skills observed in this role:**")
        st.markdown(skill_pills(current_skills_df["skill"].tolist()[:15]), unsafe_allow_html=True)

    n_postings = len(df[df[COL_TITLE].str.lower().str.contains(current_role.lower(), na=False)])
    st.markdown(f"<div style='font-size:13px;color:#9ca3c0;margin-bottom:16px;'>{n_postings:,} postings in dataset</div>",
                unsafe_allow_html=True)

    # ── Transition chart ───────────────────────────────────────────────────
    st.markdown("### 🔀 Possible Role Transitions (by skill overlap)")

    colors = ["#10b981" if s >= 40 else "#f59e0b" if s >= 20 else "#ef4444"
              for s in related["overlap_score"]]

    fig = go.Figure(go.Bar(
        x=related["overlap_score"],
        y=related["role"],
        orientation="h",
        marker_color=colors,
        text=related["overlap_score"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3c0", family="Inter"),
        margin=dict(l=10, r=60, t=30, b=10),
        height=max(300, top_n * 42),
        title=f"Skill Overlap: {current_role} → Other Roles",
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Skill Overlap Score (%)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Path detail cards ──────────────────────────────────────────────────
    st.markdown("### 🗺️ Path Detail Cards")
    st.markdown("*Click any role below to see the additional skills commonly observed in those postings.*")

    for _, row in related.iterrows():
        overlap = row["overlap_score"]
        badge_color = "#10b981" if overlap >= 40 else "#f59e0b" if overlap >= 20 else "#ef4444"
        difficulty = "Low Transition" if overlap >= 40 else "Medium Transition" if overlap >= 20 else "High Transition"

        target_skills_df = get_skills_by_role(df, row["role"], top_n=10)
        curr_skill_set = set(current_skills_df["skill"].tolist() if not current_skills_df.empty else [])
        target_skill_set = set(target_skills_df["skill"].tolist() if not target_skills_df.empty else [])
        additional_skills = list(target_skill_set - curr_skill_set)[:8]

        with st.expander(f"→ {row['role']}  ({overlap:.1f}% overlap · {difficulty})", expanded=False):
            e1, e2 = st.columns(2)
            with e1:
                st.markdown(f"**Postings in dataset:** {row['postings']:,}")
                st.markdown(f"**Skill overlap score:** {overlap:.1f}%")
                st.markdown(f"""<span class="badge badge-{'green' if overlap>=40 else 'orange' if overlap>=20 else 'red'}">{difficulty}</span>""",
                            unsafe_allow_html=True)
            with e2:
                if additional_skills:
                    st.markdown("**Additional skills commonly observed:**")
                    st.markdown(skill_pills(additional_skills), unsafe_allow_html=True)
                else:
                    st.markdown("*Highly similar skill requirements.*")

    st.markdown(disclaimer_box(
        "Career paths shown are based on skill pattern overlap in the dataset. "
        "They represent dataset observations — not guaranteed career trajectories."
    ), unsafe_allow_html=True)
