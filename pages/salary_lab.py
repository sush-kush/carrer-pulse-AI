"""CareerPulse AI — Salary Lab + Salary Predictor"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from modules.feature_engineering import (
    get_salary_distribution, get_salary_by_exp, get_location_salary_stats,
    get_skills_by_role,
)
from modules.ml_engine import SalaryPredictor
from modules.data_loader import COL_TITLE
from modules.ui_components import page_header, disclaimer_box, kpi_card, CHART_LAYOUT, section_label, back_button


@st.cache_resource
def _get_predictor(df):
    p = SalaryPredictor()
    return p.train(df)


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Salary Lab", "Explore observed salary data and ML-based salary prediction", badge="💰"),
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Salary Overview", "📍 By Location", "📅 By Experience", "🤖 Salary Predictor"
    ])

    # ── Tab 1: Overview ───────────────────────────────────────────────────
    with tab1:
        sal_df = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()]
        st.markdown(f"""
        <div class="cp-card" style="margin-bottom:16px;">
          <strong>Salary Data Coverage</strong><br>
          <span style="color:#9ca3c0; font-size:13px;">
          {len(sal_df):,} of {len(df):,} postings ({len(sal_df)/len(df)*100:.1f}%) have disclosed salary data.
          The remaining {len(df)-len(sal_df):,} postings show "Not Disclosed" and are excluded from all salary analytics.
          </span>
        </div>
        """, unsafe_allow_html=True)

        if sal_df.empty:
            st.warning("No salary data available.")
            return

        # Summary KPIs
        mid = sal_df["mid_salary_lpa"]
        cols = st.columns(4)
        for col, (v, l, c) in zip(cols, [
            (f"₹{mid.min():.1f}", "Min (LPA)", "#14b8a6"),
            (f"₹{mid.mean():.1f}", "Mean (LPA)", "#4f8ef7"),
            (f"₹{mid.median():.1f}", "Median (LPA)", "#8b5cf6"),
            (f"₹{mid.max():.1f}", "Max (LPA)", "#f59e0b"),
        ]):
            with col:
                st.markdown(kpi_card(v, l, color=c), unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### Salary Distribution (Disclosed)")
            dist = get_salary_distribution(df)
            fig = go.Figure(go.Bar(
                x=dist["range"], y=dist["count"], marker_color="#4f8ef7",
                text=dist["count"].apply(lambda x: f"{x:,}"), textposition="outside",
            ))
            fig.update_layout(**CHART_LAYOUT, height=380,
                              xaxis=dict(title="Salary Range (LPA)"),
                              yaxis=dict(showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown("#### Salary Box Plot by Role Category")
            roles_sal = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()]
            fig2 = go.Figure()
            cats = roles_sal["role_category"].value_counts().head(10).index.tolist()
            colors = px.colors.qualitative.Set3
            for i, cat in enumerate(cats):
                sub = roles_sal[roles_sal["role_category"] == cat]["mid_salary_lpa"]
                fig2.add_trace(go.Box(
                    y=sub, name=cat, marker_color=colors[i % len(colors)],
                    boxpoints=False, whiskerwidth=0.5,
                ))
            fig2.update_layout(**CHART_LAYOUT, height=380,
                               yaxis=dict(title="Salary (LPA)", showgrid=True, gridcolor="#2d3148"),
                               showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Salary by role (top 20)
        st.markdown("#### Top Roles by Median Salary")
        top_roles = df[df["salary_disclosed"] & df["mid_salary_lpa"].notna()].groupby(COL_TITLE).agg(
            median_lpa=("mid_salary_lpa", "median"),
            count=("jobId", "count"),
        ).query("count >= 10").nlargest(20, "median_lpa").reset_index()
        top_roles.columns = ["role", "median_lpa", "count"]

        fig3 = go.Figure(go.Bar(
            x=top_roles["median_lpa"], y=top_roles["role"], orientation="h",
            marker_color="#10b981",
            text=top_roles["median_lpa"].apply(lambda x: f"₹{x:.1f}L"),
            textposition="outside",
        ))
        fig3.update_layout(**CHART_LAYOUT, height=500,
                           yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                           xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Median Salary (LPA)"))
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown(disclaimer_box(
            "Observed salary values only. Postings with undisclosed salaries are excluded."
        ), unsafe_allow_html=True)

    # ── Tab 2: By Location ────────────────────────────────────────────────
    with tab2:
        loc_sal = get_location_salary_stats(df)
        if loc_sal.empty:
            st.info("Insufficient location salary data.")
        else:
            st.markdown("#### Salary Statistics by Location (≥10 disclosed postings)")
            col_a, col_b = st.columns(2)
            with col_a:
                fig4 = go.Figure(go.Bar(
                    x=loc_sal["mean_lpa"].head(20), y=loc_sal["location"].head(20),
                    orientation="h", marker_color="#4f8ef7",
                    text=loc_sal["mean_lpa"].head(20).apply(lambda x: f"₹{x:.1f}L"),
                    textposition="outside",
                ))
                fig4.update_layout(**CHART_LAYOUT, height=480,
                                   title="Mean Salary by Location",
                                   yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                                   xaxis=dict(showgrid=True, gridcolor="#2d3148"))
                st.plotly_chart(fig4, use_container_width=True)
            with col_b:
                fig5 = go.Figure(go.Bar(
                    x=loc_sal["median_lpa"].head(20), y=loc_sal["location"].head(20),
                    orientation="h", marker_color="#8b5cf6",
                    text=loc_sal["median_lpa"].head(20).apply(lambda x: f"₹{x:.1f}L"),
                    textposition="outside",
                ))
                fig5.update_layout(**CHART_LAYOUT, height=480,
                                   title="Median Salary by Location",
                                   yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                                   xaxis=dict(showgrid=True, gridcolor="#2d3148"))
                st.plotly_chart(fig5, use_container_width=True)

            st.dataframe(
                loc_sal.rename(columns={
                    "location": "Location", "salary_count": "Postings with Salary",
                    "mean_lpa": "Mean (LPA)", "median_lpa": "Median (LPA)",
                    "min_lpa": "Min (LPA)", "max_lpa": "Max (LPA)",
                }),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 3: By Experience ──────────────────────────────────────────────
    with tab3:
        exp_sal = get_salary_by_exp(df)
        if exp_sal.empty:
            st.info("Insufficient experience-salary data.")
        else:
            st.markdown("#### Salary Progression by Experience Level")
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(x=exp_sal["exp_bucket"], y=exp_sal["mean_lpa"],
                                   name="Mean LPA", marker_color="#4f8ef7"))
            fig6.add_trace(go.Bar(x=exp_sal["exp_bucket"], y=exp_sal["median_lpa"],
                                   name="Median LPA", marker_color="#8b5cf6"))
            fig6.update_layout(**CHART_LAYOUT, height=380, barmode="group",
                               xaxis=dict(title="Experience Level"),
                               yaxis=dict(title="Salary (LPA)", showgrid=True, gridcolor="#2d3148"),
                               legend=dict(orientation="h", y=1.02))
            st.plotly_chart(fig6, use_container_width=True)

            st.dataframe(
                exp_sal.rename(columns={
                    "exp_bucket": "Experience", "mean_lpa": "Mean (LPA)",
                    "median_lpa": "Median (LPA)", "count": "Postings"
                }),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 4: Salary Predictor ───────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div class="cp-card">
          <strong>🤖 ML-Powered Salary Predictor</strong><br>
          <span style="color:#9ca3c0; font-size:13px;">
          This model is trained on disclosed salary observations from the uploaded dataset using
          Gradient Boosting regression. Features: job role, location, experience, and skills count.
          </span>
        </div>
        """, unsafe_allow_html=True)

        predictor = _get_predictor(df)

        if not predictor.trained:
            st.warning("Insufficient salary data to train the predictor.")
            return

        # Model metrics
        with st.expander("📈 Model Performance Metrics", expanded=False):
            mc1, mc2, mc3, mc4 = st.columns(4)
            m = predictor.metrics
            mc1.metric("MAE", f"₹{m['MAE']:.2f} LPA")
            mc2.metric("RMSE", f"₹{m['RMSE']:.2f} LPA")
            mc3.metric("R² Score", str(m['R2']))
            mc4.metric("Test Records", f"{m['n_test']:,}")
            st.markdown(f"*Trained on {predictor.n_train:,} salary observations from the dataset.*")

            # Feature importance
            st.markdown("**Feature Importance**")
            fi = predictor.feature_importances
            fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance %"])
            fig_fi = go.Figure(go.Bar(
                x=fi_df["Importance %"], y=fi_df["Feature"], orientation="h",
                marker_color="#4f8ef7", text=fi_df["Importance %"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            ))
            fig_fi.update_layout(**CHART_LAYOUT, height=200,
                                  yaxis=dict(autorange="reversed"),
                                  xaxis=dict(showgrid=True, gridcolor="#2d3148"))
            st.plotly_chart(fig_fi, use_container_width=True)

        st.markdown("### 🎯 Predict Salary")
        top_roles = df[COL_TITLE].value_counts().head(100).index.tolist()
        top_locs  = df["location_primary"].value_counts().head(50).index.tolist()

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            pred_role = st.selectbox("Job Role", top_roles, key="pred_role")
        with p2:
            pred_loc = st.selectbox("Location", top_locs, key="pred_loc")
        with p3:
            pred_exp = st.slider("Experience (years)", 0, 25, 3, key="pred_exp")
        with p4:
            pred_skills = st.slider("Number of Skills", 1, 20, 6, key="pred_skills")

        if st.button("🔮 Predict Salary", key="do_predict"):
            result = predictor.predict(pred_role, pred_loc, float(pred_exp), pred_skills)
            if "error" in result:
                st.error(result["error"])
            else:
                st.markdown("---")
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown(f"""
                    <div class="cp-kpi">
                      <div class="cp-kpi-val" style="color:#10b981;">
                        ₹{result['range_low_lpa']:.1f} – ₹{result['range_high_lpa']:.1f} LPA
                      </div>
                      <div class="cp-kpi-label">Estimated Salary Range</div>
                    </div>
                    """, unsafe_allow_html=True)
                with r2:
                    st.markdown(f"""
                    <div class="cp-kpi">
                      <div class="cp-kpi-val" style="color:#4f8ef7;">₹{result['predicted_lpa']:.1f} LPA</div>
                      <div class="cp-kpi-label">Point Estimate</div>
                    </div>
                    """, unsafe_allow_html=True)
                with r3:
                    conf_color = {"Moderate–High": "#10b981", "Moderate": "#f59e0b", "Low": "#ef4444"}
                    c = conf_color.get(result["confidence"], "#9ca3c0")
                    st.markdown(f"""
                    <div class="cp-kpi">
                      <div class="cp-kpi-val" style="color:{c};">{result['confidence']}</div>
                      <div class="cp-kpi-label">Prediction Confidence</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"*Based on {result['n_train']:,} training observations from the dataset.*")
                st.markdown(disclaimer_box(
                    "This is a model-based estimate derived from the uploaded dataset. "
                    "It is not a guarantee of actual compensation. Actual salaries vary."
                ), unsafe_allow_html=True)
