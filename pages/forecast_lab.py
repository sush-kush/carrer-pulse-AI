"""CareerPulse AI — Forecast Lab"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from modules.ui_components import page_header, disclaimer_box, CHART_LAYOUT, section_label, back_button


_RECENCY_ORDER = [
    "Just Now", "Few Hours Ago", "Today", "1 Day Ago", "2 Days Ago",
    "3 Days Ago", "4 Days Ago", "5 Days Ago", "6 Days Ago",
    "7 Days Ago", "8 Days Ago", "9 Days Ago", "10 Days Ago",
]


def _get_relative_day(label: str) -> int | None:
    label = str(label).strip()
    mapping = {
        "Just Now": 0, "Few Hours Ago": 0, "Today": 0, "1 Day Ago": 1,
        "2 Days Ago": 2, "3 Days Ago": 3, "4 Days Ago": 4, "5 Days Ago": 5,
        "6 Days Ago": 6, "7 Days Ago": 7, "8 Days Ago": 8, "9 Days Ago": 9, "10 Days Ago": 10,
    }
    return mapping.get(label, None)


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Forecast Lab", "Model-based trends and forecasting from historical data", badge="📈"),
                unsafe_allow_html=True)

    # ── Dataset date check ─────────────────────────────────────────────────
    df2 = df.copy()
    df2["day_offset"] = df2["jobUploaded"].apply(_get_relative_day)
    time_df = df2.dropna(subset=["day_offset"])

    st.markdown(f"""
    <div class="cp-card">
      <strong>📅 Dataset Temporal Coverage</strong><br>
      <span style="color:#9ca3c0;font-size:13px;">
        The dataset uses relative time labels (e.g., "2 Days Ago", "7 Days Ago") rather than
        absolute calendar dates. This provides a <strong>~10-day rolling window</strong> of
        posting activity — sufficient for recency analysis but <strong>insufficient for
        long-term trend forecasting</strong>.<br><br>
        The Forecast Lab shows posting volume trends within this window and applies a
        simple linear projection. Projections are illustrative only.
      </span>
    </div>
    """, unsafe_allow_html=True)

    if time_df.empty:
        st.warning("No temporal data found in the dataset for trend analysis.")
        return

    tab1, tab2, tab3 = st.tabs([
        "📊 Posting Activity Trend", "🧠 Skill Demand Trend", "💼 Role Demand Trend"
    ])

    # ── Tab 1: Overall posting volume ─────────────────────────────────────
    with tab1:
        daily = time_df.groupby("day_offset").size().reset_index(name="postings")
        daily = daily.sort_values("day_offset", ascending=False)  # oldest first
        daily["day_label"] = daily["day_offset"].apply(
            lambda x: f"{int(x)} Days Ago" if x > 0 else "Today/Recent"
        )

        # Simple linear extrapolation
        x = daily["day_offset"].values
        y = daily["postings"].values
        if len(x) >= 3:
            coeffs = np.polyfit(x, y, 1)
            future_days = np.array([-1, -2, -3])  # "tomorrow", "day after", etc.
            future_pred = np.polyval(coeffs, future_days).clip(0)
            future_labels = ["1 Day Ahead", "2 Days Ahead", "3 Days Ahead"]
        else:
            future_pred, future_labels = [], []

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["day_label"][::-1].tolist(),
            y=daily["postings"][::-1].tolist(),
            mode="lines+markers",
            name="Observed Postings",
            line=dict(color="#4f8ef7", width=2),
            marker=dict(size=7),
        ))
        if len(future_labels) > 0:
            fig.add_trace(go.Scatter(
                x=future_labels,
                y=future_pred.tolist(),
                mode="lines+markers",
                name="Linear Projection (Illustrative)",
                line=dict(color="#f59e0b", width=2, dash="dash"),
                marker=dict(size=7, symbol="x"),
            ))
        fig.update_layout(**CHART_LAYOUT, height=380,
                          title="Job Posting Activity (Recent Window)",
                          xaxis=dict(title="Day", showgrid=True, gridcolor="#2d3148"),
                          yaxis=dict(title="Postings", showgrid=True, gridcolor="#2d3148"),
                          legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(disclaimer_box(
            "This dataset uses relative time labels (~10-day window). "
            "Linear projection is illustrative only — insufficient data for reliable forecasting. "
            "The dataset does not contain long-term historical records."
        ), unsafe_allow_html=True)

    # ── Tab 2: Skill demand trend ─────────────────────────────────────────
    with tab2:
        st.markdown("#### Skill Posting Volume over the ~10-Day Window")

        from modules.feature_engineering import get_skill_frequency
        top_skills = get_skill_frequency(df, top_n=20)["skill"].tolist()
        sel_skills = st.multiselect(
            "Select skills to compare", top_skills,
            default=top_skills[:5], key="fl_skills",
        )

        if not sel_skills:
            st.info("Select at least one skill.")
        else:
            # Explode skills with day_offset
            exploded = time_df.copy()
            exploded = exploded.explode("skills_list")
            exploded = exploded[exploded["skills_list"].isin(sel_skills)]
            skill_trend = exploded.groupby(["day_offset", "skills_list"]).size().reset_index(name="count")

            fig2 = go.Figure()
            colors = ["#4f8ef7", "#8b5cf6", "#14b8a6", "#f59e0b", "#10b981",
                      "#ef4444", "#f97316", "#ec4899", "#06b6d4", "#84cc16"]
            for i, skill in enumerate(sel_skills):
                sub = skill_trend[skill_trend["skills_list"] == skill].sort_values("day_offset", ascending=False)
                if sub.empty:
                    continue
                labels = sub["day_offset"].apply(
                    lambda x: f"{int(x)}d ago" if x > 0 else "Today"
                ).tolist()
                fig2.add_trace(go.Scatter(
                    x=labels, y=sub["count"].tolist(),
                    mode="lines+markers", name=skill,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6),
                ))
            fig2.update_layout(**CHART_LAYOUT, height=380,
                               title="Skill Posting Frequency over Time Window",
                               xaxis=dict(showgrid=True, gridcolor="#2d3148"),
                               yaxis=dict(showgrid=True, gridcolor="#2d3148",
                                          title="Postings with Skill"),
                               legend=dict(orientation="h", y=1.05))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("*Trend based on ~10-day posting window. Not sufficient for long-term demand forecasting.*")

    # ── Tab 3: Role demand trend ──────────────────────────────────────────
    with tab3:
        from modules.data_loader import COL_TITLE
        top_roles = df[COL_TITLE].value_counts().head(30).index.tolist()
        sel_roles = st.multiselect(
            "Select roles to compare", top_roles,
            default=top_roles[:4], key="fl_roles",
        )

        if not sel_roles:
            st.info("Select at least one role.")
        else:
            role_trend = time_df[time_df[COL_TITLE].isin(sel_roles)].groupby(
                ["day_offset", COL_TITLE]
            ).size().reset_index(name="count")

            fig3 = go.Figure()
            colors = ["#4f8ef7", "#8b5cf6", "#14b8a6", "#f59e0b", "#10b981",
                      "#ef4444", "#f97316", "#ec4899"]
            for i, role in enumerate(sel_roles):
                sub = role_trend[role_trend[COL_TITLE] == role].sort_values("day_offset", ascending=False)
                if sub.empty:
                    continue
                labels = sub["day_offset"].apply(
                    lambda x: f"{int(x)}d ago" if x > 0 else "Today"
                ).tolist()
                fig3.add_trace(go.Scatter(
                    x=labels, y=sub["count"].tolist(),
                    mode="lines+markers", name=role,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6),
                ))
            fig3.update_layout(**CHART_LAYOUT, height=380,
                               title="Role Posting Frequency over Time Window",
                               xaxis=dict(showgrid=True, gridcolor="#2d3148"),
                               yaxis=dict(showgrid=True, gridcolor="#2d3148",
                                          title="Postings"),
                               legend=dict(orientation="h", y=1.05))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("*Based on ~10-day window. Not a long-term forecast.*")

    st.markdown("""
    <div class="cp-disclaimer" style="margin-top:16px;">
      <strong>Forecast Limitation:</strong>
      The uploaded dataset does not contain long-term historical date records.
      The "jobUploaded" field uses relative labels spanning approximately 10 days.
      This is insufficient for reliable long-term trend forecasting.
      All visualizations here reflect <strong>short-window observations</strong>, not multi-month or multi-year forecasts.
    </div>
    """, unsafe_allow_html=True)
