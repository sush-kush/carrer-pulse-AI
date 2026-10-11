
 """CareerPulse AI — Role Explorer Page"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from modules.feature_engineering import (
    get_skills_by_role, get_role_salary_stats,
    get_location_demand, get_related_roles,
)
from modules.data_loader import COL_TITLE, COL_COMPANY
from modules.ui_components import page_header, disclaimer_box, skill_pills, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Role Explorer", "Deep-dive into any job role from the dataset", badge="💼"),
                unsafe_allow_html=True)

    top_roles = df[COL_TITLE].value_counts().head(100).index.tolist()
    selected = st.selectbox("🔍 Select a Job Role to Explore", top_roles)

    sub = df[df[COL_TITLE].str.lower().str.contains(selected.lower(), na=False)]
    if sub.empty:
        st.warning(f"No postings found for '{selected}'.")
        return

    st.markdown("---")

    # ── Summary KPIs ──────────────────────────────────────────────────────
    sal_sub = sub[sub["salary_disclosed"] & sub["mid_salary_lpa"].notna()]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Postings", f"{len(sub):,}")
    c2.metric("Companies", f"{sub[COL_COMPANY].nunique():,}")
    c3.metric("Locations", f"{sub['location_primary'].nunique():,}")
    c4.metric("With Salary", f"{len(sal_sub):,}")
    c5.metric("Avg Rating", f"{sub['AggregateRating'].mean():.2f}" if sub["AggregateRating"].notna().any() else "N/A")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 Skills", "💰 Salary", "📅 Experience", "📍 Locations & Companies", "🔗 Related Roles"
    ])

    with tab1:
        skills_df = get_skills_by_role(df, selected, top_n=25)
        if skills_df.empty:
            st.info("No skill data for this role.")
        else:
            col_l, col_r = st.columns([2, 1])
            with col_l:
                fig = go.Figure(go.Bar(
                    x=skills_df["pct"], y=skills_df["skill"], orientation="h",
                    marker=dict(color=skills_df["pct"],
                                colorscale=[[0, "#1e2130"], [1, "#4f8ef7"]], showscale=False),
                    text=skills_df["pct"].apply(lambda x: f"{x:.1f}%"),
                    textposition="outside",
                ))
                fig.update_layout(**CHART_LAYOUT, height=520,
                                  title=f"Skill Frequency in '{selected}' Postings",
                                  yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                                  xaxis=dict(showgrid=True, gridcolor="#2d3148",
                                             title="% of Postings"))
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                st.markdown("**Skills observed in this role:**")
                st.markdown(skill_pills(skills_df["skill"].tolist()), unsafe_allow_html=True)

    with tab2:
        stats = get_role_salary_stats(df, selected)
        if not stats or stats.get("salary_count", 0) == 0:
            st.info("No disclosed salary data for this role.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Mean (LPA)", f"₹{stats['mean_lpa']}")
            m2.metric("Median (LPA)", f"₹{stats['median_lpa']}")
            m3.metric("Min (LPA)", f"₹{stats['min_lpa']}")
            m4.metric("Max (LPA)", f"₹{stats['max_lpa']}")

            sal_vals = sal_sub["mid_salary_lpa"]
            fig2 = go.Figure()
            fig2.add_trace(go.Histogram(x=sal_vals, nbinsx=25, marker_color="#4f8ef7",
                                         opacity=0.8, name="Salary Distribution"))
            fig2.add_vline(x=stats["median_lpa"], line_dash="dash", line_color="#f59e0b",
                           annotation_text=f"Median ₹{stats['median_lpa']}L")
            fig2.add_vline(x=stats["mean_lpa"], line_dash="dot", line_color="#10b981",
                           annotation_text=f"Mean ₹{stats['mean_lpa']}L")
            fig2.update_layout(**CHART_LAYOUT, height=360,
                               xaxis=dict(title="Salary (LPA)", showgrid=True, gridcolor="#2d3148"),
                               yaxis=dict(title="Postings", showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown(f"*Based on {stats['salary_count']:,} postings with disclosed salary.*")
            st.markdown(disclaimer_box("Observed salary data only. Undisclosed salaries excluded."),
                        unsafe_allow_html=True)

    with tab3:
        min_exp = sub["minimumExperience"].dropna()
        max_exp = sub["maximumExperience"].dropna()
        if min_exp.empty:
            st.info("No experience data for this role.")
        else:
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Avg Min Exp", f"{min_exp.mean():.1f} yrs")
            e2.metric("Avg Max Exp", f"{max_exp.mean():.1f} yrs")
            e3.metric("Fresher Roles", f"{(min_exp == 0).sum():,}")
            e4.metric("Senior (10+ yrs)", f"{(min_exp >= 10).sum():,}")

            exp_fig = go.Figure(go.Histogram(x=min_exp, nbinsx=20, marker_color="#8b5cf6",
                                              opacity=0.8))
            exp_fig.update_layout(**CHART_LAYOUT, height=320,
                                   xaxis=dict(title="Minimum Experience Required (yrs)",
                                              showgrid=True, gridcolor="#2d3148"),
                                   yaxis=dict(title="Postings", showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(exp_fig, use_container_width=True)

            vc = sub["exp_bucket"].value_counts().reset_index()
            vc.columns = ["Bucket", "Count"]
            st.dataframe(vc, use_container_width=True, hide_index=True)

    with tab4:
        col_loc, col_co = st.columns(2)
        with col_loc:
            st.markdown("**Top Locations**")
            loc_vc = sub["location_primary"].value_counts().head(15).reset_index()
            loc_vc.columns = ["location", "count"]
            fig3 = go.Figure(go.Bar(
                x=loc_vc["count"], y=loc_vc["location"], orientation="h",
                marker_color="#14b8a6",
                text=loc_vc["count"].apply(lambda x: f"{x:,}"), textposition="outside",
            ))
            fig3.update_layout(**CHART_LAYOUT, height=400,
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig3, use_container_width=True)

        with col_co:
            st.markdown("**Top Companies Hiring**")
            co_vc = sub[COL_COMPANY].value_counts().head(15).reset_index()
            co_vc.columns = ["company", "count"]
            fig4 = go.Figure(go.Bar(
                x=co_vc["count"], y=co_vc["company"], orientation="h",
                marker_color="#f59e0b",
                text=co_vc["count"].apply(lambda x: f"{x:,}"), textposition="outside",
            ))
            fig4.update_layout(**CHART_LAYOUT, height=400,
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig4, use_container_width=True)

    with tab5:
        related = get_related_roles(df, selected, top_n=10)
        if related.empty:
            st.info("No related roles found.")
        else:
            st.markdown("""
            <div class="cp-card">
              Related roles are identified based on skill requirement overlap in the dataset.
              Higher overlap score = more similar skill requirements.
            </div>
            """, unsafe_allow_html=True)
            fig5 = go.Figure(go.Bar(
                x=related["overlap_score"], y=related["role"], orientation="h",
                marker_color="#8b5cf6",
                text=related["overlap_score"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            ))
            fig5.update_layout(**CHART_LAYOUT, height=360,
                               title="Skill Overlap Score with Related Roles",
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148",
                                          title="Skill Overlap %"))
            st.plotly_chart(fig5, use_container_width=True)
            st.markdown(disclaimer_box(
                "Related roles are based on skill co-occurrence in the dataset — not career advice."
            ), unsafe_allow_html=True)
