"""CareerPulse AI — Market Pulse Page"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from modules.data_loader import COL_TITLE, COL_COMPANY, COL_LOCATION, COL_MIN_EXP
from modules.feature_engineering import (
    get_kpis, get_role_demand, get_location_demand,
    get_company_stats, get_exp_distribution,
    get_salary_distribution, get_role_category_demand,
)
from modules.ui_components import page_header, kpi_card, disclaimer_box, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Market Pulse", "Real-time job market intelligence dashboard", badge="🌐"),
                unsafe_allow_html=True)

    # ── Global Filters ────────────────────────────────────────────────────
    with st.expander("🔧 Global Filters", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            all_locs = ["All"] + sorted(df["location_primary"].value_counts().head(40).index.tolist())
            sel_loc = st.selectbox("Location", all_locs, key="mp_loc")
        with fc2:
            all_cats = ["All"] + sorted(df["role_category"].unique().tolist())
            sel_cat = st.selectbox("Role Category", all_cats, key="mp_cat")
        with fc3:
            exp_opts = ["All"] + ["Fresher (0 yrs)", "0–2 Years", "2–5 Years",
                                   "5–8 Years", "8–12 Years", "12+ Years"]
            sel_exp = st.selectbox("Experience", exp_opts, key="mp_exp")

    fdf = df.copy()
    if sel_loc != "All":
        fdf = fdf[fdf["location_primary"] == sel_loc]
    if sel_cat != "All":
        fdf = fdf[fdf["role_category"] == sel_cat]
    if sel_exp != "All":
        fdf = fdf[fdf["exp_bucket"] == sel_exp]

    if fdf.empty:
        st.warning("No records match the selected filters.")
        return

    # ── KPIs ──────────────────────────────────────────────────────────────
    kpis = get_kpis(fdf)
    cols = st.columns(4)
    kpi_data = [
        (f"{kpis['total_postings']:,}", "Job Postings", "#4f8ef7"),
        (f"{kpis['unique_companies']:,}", "Companies", "#8b5cf6"),
        (f"{kpis['unique_roles']:,}", "Unique Roles", "#14b8a6"),
        (f"{kpis['unique_locations']:,}", "Locations", "#f59e0b"),
    ]
    for col, (v, l, c) in zip(cols, kpi_data):
        with col:
            st.markdown(kpi_card(v, l, color=c), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols2 = st.columns(4)
    kpi_data2 = [
        (f"{kpis['unique_skills']:,}", "Unique Skills", "#10b981"),
        (f"{kpis['salary_coverage_pct']}%", "Salary Coverage", "#ef4444"),
        (f"₹{kpis['avg_salary_lpa']} LPA" if kpis['avg_salary_lpa'] else "N/A", "Avg Salary", "#f59e0b"),
        (f"₹{kpis['median_salary_lpa']} LPA" if kpis['median_salary_lpa'] else "N/A", "Median Salary", "#4f8ef7"),
    ]
    for col, (v, l, c) in zip(cols2, kpi_data2):
        with col:
            st.markdown(kpi_card(v, l, color=c), unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 1: Roles + Locations ──────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 🏆 Most Demanded Roles (Top 20)")
        roles = get_role_demand(fdf, top_n=20)
        fig = go.Figure(go.Bar(
            x=roles["count"], y=roles["role"], orientation="h",
            marker_color="#4f8ef7", text=roles["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig.update_layout(**CHART_LAYOUT, height=500,
                          yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                          xaxis=dict(showgrid=True, gridcolor="#2d3148"))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("#### 📍 Top Locations")
        locs = get_location_demand(fdf, top_n=20)
        fig2 = go.Figure(go.Bar(
            x=locs["count"], y=locs["location"], orientation="h",
            marker_color="#8b5cf6", text=locs["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig2.update_layout(**CHART_LAYOUT, height=500,
                           yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                           xaxis=dict(showgrid=True, gridcolor="#2d3148"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Role categories + Salary distribution ──────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🗂️ Postings by Role Category")
        cat_df = get_role_category_demand(fdf)
        fig3 = px.pie(cat_df, values="count", names="category",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig3.update_layout(**CHART_LAYOUT, height=360, showlegend=True,
                           legend=dict(font=dict(size=11)))
        fig3.update_traces(textposition="inside", textinfo="percent+label",
                           hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown("#### 💰 Salary Distribution (Disclosed Postings)")
        sal_df = get_salary_distribution(fdf)
        fig4 = go.Figure(go.Bar(
            x=sal_df["range"], y=sal_df["count"],
            marker_color="#14b8a6",
            text=sal_df["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig4.update_layout(**CHART_LAYOUT, height=360,
                           xaxis=dict(title="Salary Range (LPA)"),
                           yaxis=dict(showgrid=True, gridcolor="#2d3148"))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Experience distribution + Top companies ────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### 📅 Experience Distribution")
        exp_df = get_exp_distribution(fdf)
        fig5 = go.Figure(go.Bar(
            x=exp_df["exp_bucket"], y=exp_df["count"],
            marker_color="#f59e0b",
            text=exp_df["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig5.update_layout(**CHART_LAYOUT, height=340,
                           xaxis=dict(tickangle=-20),
                           yaxis=dict(showgrid=True, gridcolor="#2d3148"))
        st.plotly_chart(fig5, use_container_width=True)

    with col_d:
        st.markdown("#### 🏢 Top 10 Companies by Postings")
        comp = get_company_stats(fdf, top_n=10)
        fig6 = go.Figure(go.Bar(
            x=comp["postings"], y=comp["company"], orientation="h",
            marker_color="#ef4444",
            text=comp["postings"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig6.update_layout(**CHART_LAYOUT, height=340,
                           yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                           xaxis=dict(showgrid=True, gridcolor="#2d3148"))
        st.plotly_chart(fig6, use_container_width=True)

    # ── Posting recency ───────────────────────────────────────────────────
    st.markdown("#### ⏱️ Posting Recency")
    recency = fdf["jobUploaded"].value_counts().head(15).reset_index()
    recency.columns = ["when", "count"]
    fig7 = go.Figure(go.Bar(
        x=recency["when"], y=recency["count"], marker_color="#4f8ef7",
        text=recency["count"].apply(lambda x: f"{x:,}"), textposition="outside",
    ))
    fig7.update_layout(**CHART_LAYOUT, height=300,
                       xaxis=dict(tickangle=-30),
                       yaxis=dict(showgrid=True, gridcolor="#2d3148"))
    st.plotly_chart(fig7, use_container_width=True)

    st.markdown(disclaimer_box(
        "All metrics are computed from the uploaded dataset. "
        "Figures reflect postings in the dataset, not the entire job market."
    ), unsafe_allow_html=True)
