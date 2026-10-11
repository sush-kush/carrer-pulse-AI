"""CareerPulse AI — Data Quality Page"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.data_loader import get_quality_report, REQUIRED_COLS
from modules.ui_components import page_header, kpi_card, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Data Quality", "Transparency into dataset coverage, missing values, and data integrity", badge="🗄️"),
                unsafe_allow_html=True)

    report = get_quality_report(df)

    # ── Coverage KPIs ──────────────────────────────────────────────────────
    st.markdown("### 📊 Coverage Summary")
    cols = st.columns(4)
    cards = [
        (f"{report['total_records']:,}", "Total Records", "#4f8ef7"),
        (f"{report['salary_coverage_pct']}%", "Salary Disclosed", "#10b981"),
        (f"{report['skill_coverage_pct']}%", "Skill Coverage", "#8b5cf6"),
        (f"{report['experience_coverage_pct']}%", "Experience Coverage", "#14b8a6"),
    ]
    for col, (v, l, c) in zip(cols, cards):
        with col:
            st.markdown(kpi_card(v, l, color=c), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols2 = st.columns(4)
    cards2 = [
        (f"{report['location_coverage_pct']}%", "Location Coverage", "#f59e0b"),
        (f"{report['rating_coverage_pct']}%", "Rating Coverage", "#ef4444"),
        (f"{report['unique_titles']:,}", "Unique Job Titles", "#4f8ef7"),
        (f"{report['unique_companies']:,}", "Unique Companies", "#8b5cf6"),
    ]
    for col, (v, l, c) in zip(cols2, cards2):
        with col:
            st.markdown(kpi_card(v, l, color=c), unsafe_allow_html=True)

    st.markdown("---")

    # ── Missing values chart ───────────────────────────────────────────────
    st.markdown("### ❌ Missing Values by Column")
    missing_data = []
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        if n_missing > 0:
            missing_data.append({
                "column": col,
                "missing": n_missing,
                "pct": round(n_missing / len(df) * 100, 2),
            })
    missing_df = pd.DataFrame(missing_data).sort_values("missing", ascending=False)

    if missing_df.empty:
        st.success("No missing values detected in the dataset!")
    else:
        fig = go.Figure(go.Bar(
            x=missing_df["pct"], y=missing_df["column"], orientation="h",
            marker=dict(
                color=missing_df["pct"],
                colorscale=[[0,"#10b981"],[0.3,"#f59e0b"],[1,"#ef4444"]],
                cmin=0, cmax=100, showscale=True,
                colorbar=dict(title="Missing %"),
            ),
            text=missing_df["pct"].apply(lambda x: f"{x}%"),
            textposition="outside",
        ))
        fig.update_layout(**CHART_LAYOUT, height=max(300, len(missing_df) * 30),
                          title="Missing Values (% of total records)",
                          yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                          xaxis=dict(showgrid=True, gridcolor="#2d3148",
                                     title="Missing %", range=[0, 105]))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Coverage bars ──────────────────────────────────────────────────────
    st.markdown("### ✅ Field Coverage")
    coverage_fields = {
        "Salary Disclosed":     report["salary_coverage_pct"],
        "Skills Present":       report["skill_coverage_pct"],
        "Experience Present":   report["experience_coverage_pct"],
        "Location Present":     report["location_coverage_pct"],
        "Rating Present":       report["rating_coverage_pct"],
    }

    cov_df = pd.DataFrame(
        list(coverage_fields.items()), columns=["field", "pct"]
    ).sort_values("pct", ascending=False)

    fig2 = go.Figure(go.Bar(
        x=cov_df["pct"], y=cov_df["field"], orientation="h",
        marker=dict(
            color=cov_df["pct"],
            colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
            cmin=0, cmax=100, showscale=False,
        ),
        text=cov_df["pct"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    fig2.update_layout(**CHART_LAYOUT, height=280,
                       yaxis=dict(autorange="reversed"),
                       xaxis=dict(showgrid=True, gridcolor="#2d3148",
                                  title="Coverage %", range=[0, 110]))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Column-by-column detail ────────────────────────────────────────────
    st.markdown("### 🔍 Column Detail")
    col_data = []
    for col in df.columns:
        n_null = int(df[col].isna().sum())
        n_unique = int(df[col].nunique())
        dtype = str(df[col].dtype)
        col_data.append({
            "Column": col,
            "Type": dtype,
            "Non-Null": len(df) - n_null,
            "Null": n_null,
            "Null %": f"{n_null/len(df)*100:.1f}%",
            "Unique Values": n_unique,
        })
    col_df = pd.DataFrame(col_data)
    st.dataframe(col_df, use_container_width=True, hide_index=True)

    # ── Currency breakdown ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💱 Currency Distribution")
    curr = report["currencies"]
    curr_df = pd.DataFrame(list(curr.items()), columns=["Currency", "Postings"])
    st.dataframe(curr_df, use_container_width=True, hide_index=True)
    st.markdown("*Note: USD postings represent a small fraction. All salary analysis is in INR.*")

    st.markdown("---")
    st.markdown("""
    <div class="cp-card">
      <strong>Data Cleaning Summary</strong>
      <ul style="color:#9ca3c0; font-size:13px; margin-top:8px;">
        <li>Duplicate job IDs removed before analysis</li>
        <li>Salary = 0 treated as undisclosed (not included in salary stats)</li>
        <li>Skills parsed from comma-separated strings and title-cased</li>
        <li>Location primary city extracted from multi-city strings</li>
        <li>Experience parsed to numeric min/max fields</li>
        <li>Outlier salaries (&gt;300 LPA) excluded from ML model training</li>
        <li>Role categories assigned via keyword matching</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)
