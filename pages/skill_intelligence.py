"""CareerPulse AI — Skill Intelligence Page"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import networkx as nx

from modules.feature_engineering import (
    get_skill_frequency, get_skills_by_role,
    get_skills_by_location, get_skill_cooccurrence,
    get_skill_by_exp_bucket,
)
from modules.data_loader import COL_TITLE
from modules.ui_components import page_header, disclaimer_box, skill_pills, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Skill Intelligence", "Analyze skill demand, frequency, co-occurrence and networks", badge="🧠"),
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Skill Demand", "💼 Skills by Role", "📍 Skills by Location",
        "🔗 Skill Network", "📅 Skills by Experience"
    ])

    # ── Tab 1: Global skill demand ────────────────────────────────────────
    with tab1:
        col_ctrl, _ = st.columns([1, 2])
        with col_ctrl:
            top_n = st.slider("Top N skills to display", 10, 80, 30, key="skill_topn")

        skills_df = get_skill_frequency(df, top_n=top_n)

        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("#### Most Demanded Skills")
            fig = go.Figure(go.Bar(
                x=skills_df["count"], y=skills_df["skill"], orientation="h",
                marker=dict(
                    color=skills_df["count"],
                    colorscale=[
                        [0, "#1e2130"], [0.3, "#4f3a8b"], [0.7, "#6b4ef5"], [1, "#8b5cf6"]
                    ],
                    showscale=False,
                ),
                text=skills_df["pct"].apply(lambda x: f"{x}%"),
                textposition="outside",
            ))
            fig.update_layout(
                **CHART_LAYOUT, height=max(400, top_n * 18),
                yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Postings"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown("#### Skill Coverage %")
            fig2 = go.Figure(go.Bar(
                x=skills_df["pct"], y=skills_df["skill"], orientation="h",
                marker_color="#14b8a6",
                text=skills_df["pct"].apply(lambda x: f"{x}%"),
                textposition="outside",
            ))
            fig2.update_layout(
                **CHART_LAYOUT, height=max(400, top_n * 18),
                yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                xaxis=dict(showgrid=True, gridcolor="#2d3148", title="% of Postings"),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"*Showing top {top_n} skills across {len(df):,} job postings.*")

    # ── Tab 2: Skills by Role ─────────────────────────────────────────────
    with tab2:
        top_roles = df[COL_TITLE].value_counts().head(60).index.tolist()
        selected_role = st.selectbox("Select Job Role", top_roles, key="skill_role")
        role_skills = get_skills_by_role(df, selected_role, top_n=25)

        if role_skills.empty:
            st.info(f"No skill data found for '{selected_role}'.")
        else:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                fig3 = go.Figure(go.Bar(
                    x=role_skills["pct"], y=role_skills["skill"], orientation="h",
                    marker=dict(
                        color=role_skills["pct"],
                        colorscale=[[0, "#1e2130"], [1, "#4f8ef7"]],
                        showscale=False,
                    ),
                    text=role_skills["pct"].apply(lambda x: f"{x}%"),
                    textposition="outside",
                ))
                fig3.update_layout(
                    **CHART_LAYOUT, height=500,
                    title=f"Skills for: {selected_role}",
                    yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                    xaxis=dict(showgrid=True, gridcolor="#2d3148", title="% of Postings"),
                )
                st.plotly_chart(fig3, use_container_width=True)

            with col_b:
                st.markdown("**Skill Pills**")
                st.markdown(skill_pills(role_skills["skill"].tolist()), unsafe_allow_html=True)
                n_postings = len(df[df[COL_TITLE].str.lower().str.contains(selected_role.lower(), na=False)])
                st.markdown(f"<div style='font-size:12px;color:#9ca3c0;margin-top:8px;'>Based on {n_postings:,} postings</div>",
                            unsafe_allow_html=True)

    # ── Tab 3: Skills by Location ─────────────────────────────────────────
    with tab3:
        top_locs = df["location_primary"].value_counts().head(30).index.tolist()
        sel_loc = st.selectbox("Select Location", top_locs, key="skill_loc")
        loc_skills = get_skills_by_location(df, sel_loc, top_n=20)

        if loc_skills.empty:
            st.info(f"No skill data found for '{sel_loc}'.")
        else:
            fig4 = go.Figure(go.Bar(
                x=loc_skills["pct"], y=loc_skills["skill"], orientation="h",
                marker_color="#f59e0b",
                text=loc_skills["pct"].apply(lambda x: f"{x}%"),
                textposition="outside",
            ))
            fig4.update_layout(
                **CHART_LAYOUT, height=480,
                title=f"Top Skills in {sel_loc}",
                yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                xaxis=dict(showgrid=True, gridcolor="#2d3148", title="% of Postings"),
            )
            st.plotly_chart(fig4, use_container_width=True)

    # ── Tab 4: Skill Network ──────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div class="cp-card">
          <strong>Skill Co-occurrence Network</strong> — edges connect skills that frequently
          appear together in the same job posting. Derived from actual dataset co-occurrence.
        </div>
        """, unsafe_allow_html=True)

        min_w = st.slider("Minimum co-occurrence count", 20, 200, 50, key="cooc_min")
        max_skills = st.slider("Max skills in network", 15, 40, 25, key="cooc_max")

        cooc = get_skill_cooccurrence(df, min_count=min_w, max_skills=max_skills)
        if cooc.empty:
            st.info("Not enough co-occurrences found with current settings. Try lowering the minimum count.")
        else:
            _render_network(cooc)

    # ── Tab 5: Skills by Experience ────────────────────────────────────────
    with tab5:
        exp_skill_df = get_skill_by_exp_bucket(df, top_n=10)
        if exp_skill_df.empty:
            st.info("No data available.")
        else:
            buckets = exp_skill_df["exp_bucket"].unique().tolist()
            sel_bucket = st.selectbox("Experience Level", buckets, key="skill_exp_bucket")
            sub = exp_skill_df[exp_skill_df["exp_bucket"] == sel_bucket]
            fig5 = go.Figure(go.Bar(
                x=sub["count"], y=sub["skill"], orientation="h",
                marker_color="#10b981",
                text=sub["count"].apply(lambda x: f"{x:,}"),
                textposition="outside",
            ))
            fig5.update_layout(
                **CHART_LAYOUT, height=380,
                title=f"Top Skills for {sel_bucket}",
                yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Postings"),
            )
            st.plotly_chart(fig5, use_container_width=True)


def _render_network(cooc_df):
    """Build and render a Plotly skill co-occurrence network."""
    G = nx.Graph()
    for _, row in cooc_df.iterrows():
        G.add_edge(row["source"], row["target"], weight=row["weight"])

    # Layout
    pos = nx.spring_layout(G, seed=42, k=2.0 / max(np.sqrt(len(G.nodes())), 1))

    # Degree-based node sizing
    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=0.8, color="#3d4168"),
        hoverinfo="none",
    )

    node_x  = [pos[n][0] for n in G.nodes()]
    node_y  = [pos[n][1] for n in G.nodes()]
    node_sz = [10 + 30 * degrees[n] / max_deg for n in G.nodes()]
    node_text = list(G.nodes())

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_text, textposition="top center",
        textfont=dict(size=10, color="#e8eaf0"),
        hoverinfo="text",
        marker=dict(
            size=node_sz,
            color=node_sz,
            colorscale=[[0, "#4f8ef7"], [0.5, "#8b5cf6"], [1, "#14b8a6"]],
            showscale=False,
            line=dict(width=1, color="#2d3148"),
        ),
    )

    fig = go.Figure([edge_trace, node_trace])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3c0"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=550,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"*{len(G.nodes())} skills, {len(G.edges())} co-occurrence edges shown. "
                f"Derived from actual skill co-occurrence in the dataset.*")
