"""CareerPulse AI — Career Simulator Page"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.feature_engineering import simulate_skill_addition, get_skill_frequency
from modules.ui_components import page_header, disclaimer_box, skill_pills, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Career Simulator", "Simulate 'What if I learn X?' — dataset-based scenario analysis", badge="🔮"),
                unsafe_allow_html=True)

    st.markdown("""
    <div class="cp-card">
      <strong>How it works</strong><br>
      <span style="color:#9ca3c0;font-size:13px;">
        Enter your current skills, then add new skills you are considering learning.
        The simulator compares your profile <em>before</em> and <em>after</em> against
        actual job postings in the dataset — showing you how your match scores and
        relevant opportunities change.<br><br>
        ⚠️ This is a <strong>dataset-based scenario analysis</strong>, not a job guarantee.
      </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        current_raw = st.text_area(
            "📌 Your Current Skills (one per line or comma-separated)",
            placeholder="Python\nSQL\nExcel\nPandas",
            height=130, key="sim_current",
        )
    with col2:
        new_raw = st.text_area(
            "➕ Skills You Want to Add (one per line or comma-separated)",
            placeholder="Power BI\nTableau\nMachine Learning",
            height=130, key="sim_new",
        )

    simulate = st.button("🔮 Run Simulation", type="primary", use_container_width=False)

    if not simulate:
        # Show popular skill suggestions
        top_skills = get_skill_frequency(df, top_n=30)["skill"].tolist()
        st.markdown("**💡 Popular skills to consider adding:**")
        st.markdown(skill_pills(top_skills[:20]), unsafe_allow_html=True)
        return

    # Parse
    current_skills = [s.strip().title() for s in current_raw.replace(",", "\n").split("\n") if s.strip()]
    new_skills     = [s.strip().title() for s in new_raw.replace(",", "\n").split("\n") if s.strip()]

    if not new_skills:
        st.warning("Please enter at least one skill to add.")
        return

    with st.spinner("Running simulation…"):
        result = simulate_skill_addition(df, current_skills, new_skills)

    before = result["before"]
    after  = result["after"]

    st.markdown("---")
    st.markdown("### 📊 Simulation Results")

    # ── Score delta cards ──────────────────────────────────────────────────
    d1, d2, d3, d4 = st.columns(4)
    delta_score = result["score_delta"]
    delta_posts = result["postings_delta"]
    delta_roles = len(result["new_roles"])

    score_color = "#10b981" if delta_score > 0 else "#ef4444" if delta_score < 0 else "#9ca3c0"
    posts_color = "#10b981" if delta_posts > 0 else "#9ca3c0"

    with d1:
        st.markdown(f"""
        <div class="cp-kpi">
          <div class="cp-kpi-val" style="color:#4f8ef7;">{result['before_avg_score']:.1f}%</div>
          <div class="cp-kpi-label">Match Score Before</div>
        </div>""", unsafe_allow_html=True)
    with d2:
        st.markdown(f"""
        <div class="cp-kpi">
          <div class="cp-kpi-val" style="color:#10b981;">{result['after_avg_score']:.1f}%</div>
          <div class="cp-kpi-label">Match Score After</div>
        </div>""", unsafe_allow_html=True)
    with d3:
        sign = "+" if delta_score >= 0 else ""
        st.markdown(f"""
        <div class="cp-kpi">
          <div class="cp-kpi-val" style="color:{score_color};">{sign}{delta_score:.1f}%</div>
          <div class="cp-kpi-label">Score Change</div>
        </div>""", unsafe_allow_html=True)
    with d4:
        st.markdown(f"""
        <div class="cp-kpi">
          <div class="cp-kpi-val" style="color:{posts_color};">+{delta_roles}</div>
          <div class="cp-kpi-label">New Role Matches</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Before / After side by side ────────────────────────────────────────
    col_b, col_a = st.columns(2)

    with col_b:
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2);
                    border-radius:12px; padding:16px; margin-bottom:12px;">
          <div style="font-size:14px; font-weight:700; color:#ef4444; margin-bottom:8px;">
            BEFORE — Without New Skills
          </div>
          <div style="font-size:12px; color:#9ca3c0;">Skills: {", ".join(current_skills) if current_skills else "None"}</div>
        </div>
        """, unsafe_allow_html=True)

        if before.empty:
            st.info("No role matches before adding skills.")
        else:
            for _, row in before.head(8).iterrows():
                ms = row["match_score"]
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:8px 0; border-bottom:1px solid #2d3148;">
                  <div style="font-size:13px;color:#e8eaf0;">{row['role']}</div>
                  <div style="font-size:13px;font-weight:700;color:#9ca3c0;">{ms:.1f}%</div>
                </div>""", unsafe_allow_html=True)

    with col_a:
        all_skills = current_skills + new_skills
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2);
                    border-radius:12px; padding:16px; margin-bottom:12px;">
          <div style="font-size:14px; font-weight:700; color:#10b981; margin-bottom:8px;">
            AFTER — With New Skills Added
          </div>
          <div style="font-size:12px; color:#9ca3c0;">
            Skills: {", ".join(all_skills[:8])}{"..." if len(all_skills) > 8 else ""}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if after.empty:
            st.info("No role matches after adding skills.")
        else:
            for _, row in after.head(8).iterrows():
                ms = row["match_score"]
                is_new = row["role"] in result["new_roles"]
                color = "#10b981" if is_new else "#e8eaf0"
                badge = ' <span style="background:rgba(16,185,129,0.15);color:#10b981;font-size:10px;padding:2px 6px;border-radius:4px;">NEW</span>' if is_new else ""
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:8px 0; border-bottom:1px solid #2d3148;">
                  <div style="font-size:13px;color:{color};">{row['role']}{badge}</div>
                  <div style="font-size:13px;font-weight:700;color:#10b981;">{ms:.1f}%</div>
                </div>""", unsafe_allow_html=True)

    # ── Bar chart comparison ───────────────────────────────────────────────
    if not before.empty and not after.empty:
        st.markdown("---")
        st.markdown("#### 📊 Match Score Comparison")

        all_roles = list(set(before["role"].tolist() + after["role"].tolist()))[:12]
        before_scores = {r: float(before.loc[before["role"] == r, "match_score"].values[0])
                         if r in before["role"].values else 0 for r in all_roles}
        after_scores  = {r: float(after.loc[after["role"] == r, "match_score"].values[0])
                         if r in after["role"].values else 0 for r in all_roles}

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Before", x=all_roles,
                              y=[before_scores[r] for r in all_roles],
                              marker_color="#ef4444", opacity=0.8))
        fig.add_trace(go.Bar(name="After", x=all_roles,
                              y=[after_scores[r] for r in all_roles],
                              marker_color="#10b981", opacity=0.9))
        fig.update_layout(
            **CHART_LAYOUT, height=360, barmode="group",
            xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
            yaxis=dict(title="Match Score %", showgrid=True, gridcolor="#2d3148"),
            legend=dict(orientation="h", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── New roles ──────────────────────────────────────────────────────────
    if result["new_roles"]:
        st.markdown("---")
        st.markdown("#### 🆕 Newly Unlocked Roles")
        st.markdown(skill_pills(result["new_roles"], style="present"), unsafe_allow_html=True)
        st.markdown(f"*Adding {', '.join(new_skills)} opened {len(result['new_roles'])} new role matches.*")

    st.markdown(disclaimer_box(
        "This simulation reflects dataset-based skill pattern analysis. "
        "It is not a guarantee of employment or hiring outcomes."
    ), unsafe_allow_html=True)
