"""CareerPulse AI — Home Page (SaaS Landing)"""

import streamlit as st
import plotly.graph_objects as go

from modules.feature_engineering import (
    get_kpis, get_role_demand, get_location_demand,
    get_skill_frequency, get_salary_distribution,
)
from modules.ui_components import kpi_card, section_label, CHART_LAYOUT, CHART_COLORS


def _go_to(page_key: str):
    st.session_state.page = page_key
    st.rerun()


def render(df):

    # ── HERO SECTION ──────────────────────────────────────────────────────────
    # NOTE: No filter:blur(), no position:absolute decorative divs —
    # Streamlit 1.63 strips those inline styles, causing raw HTML to show.
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#131625 0%,#1a1e35 100%);
          border:1px solid rgba(108,92,231,0.2);border-radius:20px;
          padding:60px 40px 52px;margin-bottom:36px;text-align:center;">

          <div style="display:inline-flex;align-items:center;gap:6px;
            background:rgba(108,92,231,0.12);border:1px solid rgba(108,92,231,0.25);
            border-radius:100px;padding:5px 16px;font-size:11px;font-weight:700;
            color:#8B7FF0;letter-spacing:0.1em;text-transform:uppercase;
            margin-bottom:22px;">
            &#9889; AI-Powered Career Intelligence
          </div>

          <div style="font-size:clamp(36px,5vw,58px);font-weight:900;
            letter-spacing:-0.04em;line-height:1.08;margin-bottom:16px;
            background:linear-gradient(135deg,#6C5CE7,#00B8D9,#FF6B8A);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">
            CareerPulse AI
          </div>

          <div style="font-size:clamp(15px,2vw,19px);color:#A0A8C8;font-weight:400;
            letter-spacing:-0.01em;margin-bottom:12px;">
            Understand the Market. Predict Possibilities. Plan Your Career.
          </div>

          <div style="font-size:14px;color:#6B7280;max-width:520px;
            margin:0 auto 0;line-height:1.7;">
            AI-powered career intelligence built from
            <span style="color:#A0A8C8;font-weight:600;">real Indian job market data</span>
            &#8212; 97,000+ postings, 44,000+ skills, 18,000+ companies.
          </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── CTA BUTTONS ────────────────────────────────────────────────────────────
    _, cta_c, _ = st.columns([1, 2, 1])
    with cta_c:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🌐  Explore Market", use_container_width=True, key="hero_market"):
                _go_to("market_pulse")
        with b2:
            if st.button("🧠  Analyze Skills", use_container_width=True, key="hero_skills"):
                _go_to("skill_intelligence")
        with b3:
            if st.button("🔍  Find Opportunities", use_container_width=True, key="hero_opps"):
                _go_to("opportunity_explorer")

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── KPI SNAPSHOT ───────────────────────────────────────────────────────────
    kpis = get_kpis(df)
    st.markdown(section_label("Live Market Snapshot"), unsafe_allow_html=True)

    kpi_defs = [
        (f"{kpis['total_postings']:,}",    "Job Postings",    "📋", "var(--grad-brand)"),
        (f"{kpis['unique_companies']:,}",   "Companies",       "🏢", "var(--grad-warm)"),
        (f"{kpis['unique_roles']:,}",       "Unique Roles",    "💼", "var(--grad-cool)"),
        (f"{kpis['unique_locations']:,}",   "Locations",       "📍",
         "linear-gradient(135deg,#F59E0B,#FF6B8A)"),
        (f"{kpis['unique_skills']:,}",      "Skills Tracked",  "🧠",
         "linear-gradient(135deg,#20C997,#00B8D9)"),
        (f"{kpis['salary_coverage_pct']}%", "Salary Records",  "💰", "var(--grad-purple)"),
        (f"Rs.{kpis['median_salary_lpa']} LPA" if kpis["median_salary_lpa"] else "N/A",
         "Median Salary", "📈", "var(--grad-pink)"),
        (f"{kpis['exp_coverage_pct']}%",    "Exp. Coverage",   "📅", "var(--grad-green)"),
    ]

    row1_cols = st.columns(4)
    row2_cols = st.columns(4)
    for i, (val, label, icon, grad) in enumerate(kpi_defs):
        target_cols = row1_cols if i < 4 else row2_cols
        with target_cols[i % 4]:
            st.markdown(kpi_card(val, label, icon, gradient=grad), unsafe_allow_html=True)

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── MARKET SNAPSHOT CHARTS ─────────────────────────────────────────────────
    st.markdown(section_label("Market Snapshot"), unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;color:#F1F2F8;margin-bottom:10px;'>"
            "Top 10 Demanded Roles</div>",
            unsafe_allow_html=True,
        )
        roles = get_role_demand(df, top_n=10)
        fig1 = go.Figure(go.Bar(
            x=roles["count"], y=roles["role"], orientation="h",
            marker=dict(
                color=roles["count"],
                colorscale=[[0, "#1E2240"], [0.4, "#5046C8"], [1, "#6C5CE7"]],
                showscale=False,
            ),
            text=roles["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(size=10, color="#6B7280"),
        ))
        fig1.update_layout(
            **CHART_LAYOUT, height=340, showlegend=False,
            yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="#6B7280"), showgrid=False),
            xaxis=dict(showgrid=True, gridcolor="rgba(108,92,231,0.08)"),
        )
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;color:#F1F2F8;margin-bottom:10px;'>"
            "Top 10 Locations</div>",
            unsafe_allow_html=True,
        )
        locs = get_location_demand(df, top_n=10)
        fig2 = go.Figure(go.Bar(
            x=locs["count"], y=locs["location"], orientation="h",
            marker=dict(
                color=locs["count"],
                colorscale=[[0, "#0D1B2A"], [0.4, "#005F80"], [1, "#00B8D9"]],
                showscale=False,
            ),
            text=locs["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(size=10, color="#6B7280"),
        ))
        fig2.update_layout(
            **CHART_LAYOUT, height=340, showlegend=False,
            yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="#6B7280"), showgrid=False),
            xaxis=dict(showgrid=True, gridcolor="rgba(0,184,217,0.08)"),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with col_c:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;color:#F1F2F8;margin-bottom:10px;'>"
            "Top 10 In-Demand Skills</div>",
            unsafe_allow_html=True,
        )
        skills = get_skill_frequency(df, top_n=10)
        fig3 = go.Figure(go.Bar(
            x=skills["count"], y=skills["skill"], orientation="h",
            marker=dict(
                color=skills["count"],
                colorscale=[[0, "#0D1B1A"], [0.4, "#0B5745"], [1, "#20C997"]],
                showscale=False,
            ),
            text=skills["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(size=10, color="#6B7280"),
        ))
        fig3.update_layout(
            **CHART_LAYOUT, height=340, showlegend=False,
            yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="#6B7280"), showgrid=False),
            xaxis=dict(showgrid=True, gridcolor="rgba(32,201,151,0.08)"),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    # Second row of charts
    col_d, col_e = st.columns([3, 2])

    with col_d:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;color:#F1F2F8;margin-bottom:10px;'>"
            "Salary Distribution (Disclosed Postings)</div>",
            unsafe_allow_html=True,
        )
        sal = get_salary_distribution(df)
        fig4 = go.Figure(go.Bar(
            x=sal["range"], y=sal["count"],
            marker=dict(
                color=sal["count"],
                colorscale=[[0, "#1E1430"], [0.4, "#5046C8"], [1, "#FF6B8A"]],
                showscale=False,
            ),
            text=sal["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(size=10, color="#6B7280"),
        ))
        fig4.update_layout(
            **CHART_LAYOUT, height=280, showlegend=False,
            xaxis=dict(title="Salary Range (LPA)", tickfont=dict(size=10), showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(108,92,231,0.08)"),
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    with col_e:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;color:#F1F2F8;margin-bottom:10px;'>"
            "Role Categories</div>",
            unsafe_allow_html=True,
        )
        cat_vc = df["role_category"].value_counts().head(8).reset_index()
        cat_vc.columns = ["category", "count"]
        fig5 = go.Figure(go.Pie(
            labels=cat_vc["category"],
            values=cat_vc["count"],
            hole=0.55,
            marker=dict(colors=CHART_COLORS, line=dict(color="#0D0F18", width=2)),
            textposition="none",
        ))
        fig5.update_layout(
            **CHART_LAYOUT, height=280, showlegend=True,
            legend=dict(font=dict(size=10, color="#6B7280"), x=1.0, y=0.5,
                        bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── FEATURE CARDS ──────────────────────────────────────────────────────────
    st.markdown(section_label("Platform Capabilities"), unsafe_allow_html=True)

    features = [
        ("🧠", "Skill Intelligence",
         "Discover the most demanded skills, co-occurrence networks, and gaps for any target role.",
         "#6C5CE7", "rgba(108,92,231,0.08)", "skill_intelligence"),
        ("💰", "Salary Lab + Predictor",
         "Explore observed salary distributions and get ML-based salary range estimates.",
         "#00B8D9", "rgba(0,184,217,0.08)", "salary_lab"),
        ("💼", "Role Explorer",
         "Deep-dive into any job role — skills, salary, experience, locations and related roles.",
         "#FF6B8A", "rgba(255,107,138,0.08)", "role_explorer"),
        ("🎯", "My Career",
         "Enter your profile and instantly see your dataset-based market alignment score.",
         "#20C997", "rgba(32,201,151,0.08)", "my_career"),
        ("🔮", "Career Simulator",
         "Simulate 'What if I learn Python or Power BI?' and see how new skills expand your matches.",
         "#F59E0B", "rgba(245,158,11,0.08)", "career_simulator"),
        ("🤖", "AI Career Copilot",
         "Ask natural-language questions answered strictly from the uploaded dataset.",
         "#8B7FF0", "rgba(108,92,231,0.08)", "ai_copilot"),
    ]

    row_a = st.columns(3)
    row_b = st.columns(3)
    for i, (icon, title, desc, color, bg, page_key) in enumerate(features):
        target = row_a if i < 3 else row_b
        with target[i % 3]:
            st.markdown(
                f'<div class="cp-feature-card" style="margin-bottom:16px;">'
                f'<div class="cp-feature-icon" style="background:{bg};color:{color};">{icon}</div>'
                f'<div class="cp-feature-title">{title}</div>'
                f'<div class="cp-feature-desc">{desc}</div>'
                f'<div class="cp-feature-cta">Explore &#8594;</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Open {title}", key=f"feat_{page_key}", use_container_width=True):
                _go_to(page_key)

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── AI COPILOT CTA ─────────────────────────────────────────────────────────
    chips_html = _example_chips()
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(108,92,231,0.12) 0%,rgba(0,184,217,0.08) 100%);'
        f'border:1px solid rgba(108,92,231,0.25);border-radius:20px;padding:40px 36px;">'
        f'<div style="display:inline-flex;align-items:center;gap:6px;'
        f'background:rgba(108,92,231,0.15);border:1px solid rgba(108,92,231,0.3);'
        f'border-radius:100px;padding:4px 14px;font-size:11px;font-weight:700;'
        f'color:#8B7FF0;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:14px;">'
        f'&#129302; AI Career Copilot</div>'
        f'<div style="font-size:26px;font-weight:800;color:#F1F2F8;'
        f'letter-spacing:-0.03em;margin-bottom:8px;">Ask CareerPulse AI</div>'
        f'<div style="font-size:14px;color:#A0A8C8;margin-bottom:20px;line-height:1.6;">'
        f'Explore the job market using natural language. '
        f'Every answer is grounded in the uploaded dataset &#8212; no fabricated data.</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;">{chips_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _, ai_btn_c, _ = st.columns([1, 1, 1])
    with ai_btn_c:
        if st.button("🤖  Open AI Career Copilot", use_container_width=True, key="hero_ai"):
            _go_to("ai_copilot")

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;margin-top:48px;padding-top:20px;'
        'border-top:1px solid rgba(108,92,231,0.1);">'
        '<div style="font-size:12px;color:#4B5563;line-height:1.8;">'
        'CareerPulse AI &nbsp;&middot;&nbsp;'
        'Data Source: indian-job-market-dataset-2025.xlsx &nbsp;&middot;&nbsp;'
        'All insights derived from real data &nbsp;&middot;&nbsp;'
        'No external job-market data used'
        '</div></div>',
        unsafe_allow_html=True,
    )


def _example_chips() -> str:
    examples = [
        "What skills are most demanded?",
        "Which roles match Python and SQL?",
        "Salary range for Data Analyst?",
        "Top locations for ML engineers?",
    ]
    return "".join(
        f'<span style="background:rgba(108,92,231,0.1);border:1px solid rgba(108,92,231,0.2);'
        f'border-radius:100px;padding:5px 14px;font-size:12px;font-weight:500;'
        f'color:#8B7FF0;display:inline-block;">{ex}</span>'
        for ex in examples
    )
