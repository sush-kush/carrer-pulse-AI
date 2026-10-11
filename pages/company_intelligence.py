"""CareerPulse AI — Company Intelligence"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.feature_engineering import get_company_stats
from modules.data_loader import COL_TITLE, COL_COMPANY, COL_RATING, COL_REVIEWS
from modules.ui_components import page_header, kpi_card, disclaimer_box, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Company Intelligence", "Explore companies by hiring volume, ratings, salaries and roles", badge="🏢"),
                unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────
    cols = st.columns(4)
    with cols[0]: st.markdown(kpi_card(f"{df[COL_COMPANY].nunique():,}", "Unique Companies", color="#4f8ef7"), unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_card(df[COL_COMPANY].value_counts().index[0], "Most Active Company", color="#8b5cf6"), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_card(f"{df[COL_RATING].notna().sum():,}", "With Rating Data", color="#14b8a6"), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_card(f"{df[COL_RATING].mean():.2f} / 5.0" if df[COL_RATING].notna().any() else "N/A", "Avg Rating", color="#f59e0b"), unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Company Deep-Dive", "⭐ Ratings"])

    # ── Tab 1: Overview ───────────────────────────────────────────────────
    with tab1:
        top_n = st.slider("Top N companies", 10, 50, 20, key="co_topn")
        comp_df = get_company_stats(df, top_n=top_n)

        st.markdown("#### Companies by Posting Volume")
        fig = go.Figure(go.Bar(
            x=comp_df["postings"], y=comp_df["company"], orientation="h",
            marker=dict(color=comp_df["postings"],
                        colorscale=[[0,"#1e2130"],[1,"#4f8ef7"]], showscale=False),
            text=comp_df["postings"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig.update_layout(**CHART_LAYOUT, height=max(400, top_n * 22),
                          yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                          xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Job Postings"))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Avg Salary by Company (Top 20, ≥10 postings with salary)")
        sal_comp = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()].groupby(COL_COMPANY).agg(
            avg_lpa=("mid_salary_lpa", "mean"),
            n=("jobId", "count"),
        ).query("n >= 10").nlargest(20, "avg_lpa").reset_index()
        sal_comp.columns = ["company", "avg_lpa", "n"]
        sal_comp["avg_lpa"] = sal_comp["avg_lpa"].round(2)

        fig2 = go.Figure(go.Bar(
            x=sal_comp["avg_lpa"], y=sal_comp["company"], orientation="h",
            marker_color="#10b981",
            text=sal_comp["avg_lpa"].apply(lambda x: f"₹{x:.1f}L"),
            textposition="outside",
        ))
        fig2.update_layout(**CHART_LAYOUT, height=480,
                           yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                           xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Avg Mid Salary (LPA)"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2: Company Deep-Dive ──────────────────────────────────────────
    with tab2:
        companies = df[COL_COMPANY].value_counts().head(100).index.tolist()
        sel_co = st.selectbox("Select Company", companies, key="co_select")

        sub = df[df[COL_COMPANY] == sel_co]
        sal_sub = sub[sub["salary_disclosed"] & sub["mid_salary_lpa"].notna()]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Job Postings", f"{len(sub):,}")
        m2.metric("Unique Roles", f"{sub[COL_TITLE].nunique():,}")
        m3.metric("Locations", f"{sub['location_primary'].nunique():,}")
        rating_val = sub[COL_RATING].mean()
        m4.metric("Avg Rating", f"{rating_val:.2f}/5.0" if pd.notna(rating_val) else "N/A")

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"**Top Roles at {sel_co}**")
            role_vc = sub[COL_TITLE].value_counts().head(12).reset_index()
            role_vc.columns = ["role", "count"]
            fig3 = go.Figure(go.Bar(
                x=role_vc["count"], y=role_vc["role"], orientation="h",
                marker_color="#4f8ef7",
                text=role_vc["count"].apply(lambda x: f"{x:,}"),
                textposition="outside",
            ))
            fig3.update_layout(**CHART_LAYOUT, height=380,
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig3, use_container_width=True)

        with col_r:
            st.markdown(f"**Locations Hiring**")
            loc_vc = sub["location_primary"].value_counts().head(12).reset_index()
            loc_vc.columns = ["location", "count"]
            fig4 = go.Figure(go.Bar(
                x=loc_vc["count"], y=loc_vc["location"], orientation="h",
                marker_color="#8b5cf6",
                text=loc_vc["count"].apply(lambda x: f"{x:,}"),
                textposition="outside",
            ))
            fig4.update_layout(**CHART_LAYOUT, height=380,
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig4, use_container_width=True)

        if not sal_sub.empty:
            st.markdown(f"**Salary Distribution at {sel_co}**")
            fig5 = go.Figure(go.Histogram(x=sal_sub["mid_salary_lpa"], nbinsx=20,
                                           marker_color="#14b8a6", opacity=0.85))
            fig5.update_layout(**CHART_LAYOUT, height=300,
                               xaxis=dict(title="Salary (LPA)", showgrid=True, gridcolor="#2d3148"),
                               yaxis=dict(title="Postings", showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig5, use_container_width=True)

    # ── Tab 3: Ratings ────────────────────────────────────────────────────
    with tab3:
        rated = df[df[COL_RATING].notna()].copy()
        if rated.empty:
            st.info("No rating data available.")
        else:
            st.markdown(f"**Rating data available for {df[COL_COMPANY].nunique()} companies**")

            top_rated = rated.groupby(COL_COMPANY).agg(
                avg_rating=(COL_RATING, "mean"),
                review_count=(COL_REVIEWS, "mean"),
                postings=("jobId", "count"),
            ).query("postings >= 5").nlargest(20, "avg_rating").reset_index()
            top_rated.columns = ["company", "avg_rating", "avg_reviews", "postings"]
            top_rated["avg_rating"] = top_rated["avg_rating"].round(2)

            fig6 = go.Figure(go.Bar(
                x=top_rated["avg_rating"], y=top_rated["company"], orientation="h",
                marker=dict(color=top_rated["avg_rating"],
                            colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                            cmin=1, cmax=5, showscale=True),
                text=top_rated["avg_rating"].apply(lambda x: f"⭐{x}"),
                textposition="outside",
            ))
            fig6.update_layout(**CHART_LAYOUT, height=520,
                               title="Top Rated Companies (≥5 postings, by avg rating)",
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148",
                                          title="Average Rating", range=[0, 5.5]))
            st.plotly_chart(fig6, use_container_width=True)

    st.markdown(disclaimer_box(
        "All company data is sourced exclusively from the uploaded dataset."
    ), unsafe_allow_html=True)
