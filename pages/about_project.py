"""CareerPulse AI — About Project Page"""

import streamlit as st
from modules.ui_components import page_header, back_button, section_label, kpi_card, disclaimer_box


def render(df):
    back_button(fallback="home")

    st.markdown(page_header(
        "About CareerPulse AI",
        "AI-powered career intelligence built on real Indian job market data",
        badge="⭐",
    ), unsafe_allow_html=True)

    # ── What is CareerPulse AI ───────────────────────────────────────────────
    st.markdown(section_label("What is CareerPulse AI?"), unsafe_allow_html=True)
    st.markdown(
        '<div class="cp-card">'
        '<div style="font-size:16px;font-weight:700;color:#F1F2F8;margin-bottom:10px;">'
        'A Real-Data Career Intelligence Platform</div>'
        '<div style="font-size:14px;color:#A0A8C8;line-height:1.8;">'
        'CareerPulse AI is a complete, production-quality career intelligence platform '
        'that transforms <strong style="color:#C4B5FD;">real Indian job market data</strong> '
        'into actionable insights using data analytics, machine learning, and an AI-powered copilot.<br><br>'
        'It is designed to answer the questions that students, freshers, working professionals, '
        'career switchers, recruiters, and job seekers ask every day — but with <em>actual data</em>, '
        'not guesswork.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Live dataset numbers ─────────────────────────────────────────────────
    st.markdown(section_label("Dataset at a Glance"), unsafe_allow_html=True)
    from modules.feature_engineering import get_kpis
    kpis = get_kpis(df)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card(f"{kpis['total_postings']:,}", "Job Postings", "📋",
                             gradient="var(--grad-brand)"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(f"{kpis['unique_companies']:,}", "Companies", "🏢",
                             gradient="var(--grad-warm)"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card(f"{kpis['unique_skills']:,}", "Unique Skills", "🧠",
                             gradient="var(--grad-cool)"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card(f"{kpis['unique_locations']:,}", "Locations", "📍",
                             gradient="linear-gradient(135deg,#F59E0B,#FF6B8A)"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Project Purpose ──────────────────────────────────────────────────────
    st.markdown(section_label("Project Purpose"), unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            '<div class="cp-card" style="height:100%;">'
            '<div style="font-size:14px;font-weight:700;color:#C4B5FD;margin-bottom:10px;">The Problem</div>'
            '<div style="font-size:13px;color:#A0A8C8;line-height:1.8;">'
            'Job seekers and students lack clear, data-backed answers to critical questions:<br>'
            '&#8226; What skills are actually in demand?<br>'
            '&#8226; What salaries are being offered?<br>'
            '&#8226; Which roles match my profile?<br>'
            '&#8226; Where are most opportunities located?<br>'
            '&#8226; What should I learn next?'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_r:
        st.markdown(
            '<div class="cp-card" style="height:100%;">'
            '<div style="font-size:14px;font-weight:700;color:#20C997;margin-bottom:10px;">The Solution</div>'
            '<div style="font-size:13px;color:#A0A8C8;line-height:1.8;">'
            'CareerPulse AI ingests a real dataset of 97,000+ Indian job postings and:<br>'
            '&#8226; Runs analytics to surface market patterns<br>'
            '&#8226; Trains ML models for salary prediction<br>'
            '&#8226; Matches user skills to real job roles<br>'
            '&#8226; Simulates "What if I learn X?" scenarios<br>'
            '&#8226; Answers natural-language career questions'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Key Features ─────────────────────────────────────────────────────────
    st.markdown(section_label("Key Features"), unsafe_allow_html=True)

    features = [
        ("🌐", "Market Analytics",
         "Real-time KPI dashboard covering total postings, companies, roles, "
         "locations, salary coverage and experience distribution — all from the actual dataset."),
        ("🧠", "Skill Intelligence",
         "Deep analysis of skill demand — most required skills globally, by role, "
         "by location, by experience level, with co-occurrence network visualization."),
        ("💰", "Salary Lab",
         "Observed salary distributions, salary by role/location/experience, "
         "and an ML-powered salary predictor trained on 33,000+ disclosed salary records."),
        ("💼", "Role Explorer",
         "Select any job role and instantly see its skills, salary statistics, "
         "experience requirements, top hiring locations, and related roles."),
        ("🔮", "Career Simulator",
         "Run 'What if I add Power BI to my skills?' — compares your match score "
         "before and after, showing newly unlocked roles and improved opportunities."),
        ("🎯", "My Career",
         "Enter your skills, target role, and experience. Get a composite Market "
         "Alignment Score (Skill Match + Location Fit + Experience Fit) and a "
         "detailed skill gap analysis."),
        ("🔍", "Opportunity Explorer",
         "Search actual job postings from the dataset that match your profile — "
         "filtered by role, location, experience, and ranked by skill overlap."),
        ("🤖", "AI Career Copilot",
         "Ask natural-language questions about the job market. Every answer is "
         "derived from dataset analytics — no fabricated statistics, no external knowledge."),
        ("📍", "Location Intelligence",
         "City-by-city analysis of posting volumes, salary statistics, top skills, "
         "and multi-city comparison tables."),
        ("🏢", "Company Intelligence",
         "Company-level profiles including posting volume, roles hired, locations, "
         "ratings, and salary data from the dataset."),
    ]

    rows = [features[i:i+2] for i in range(0, len(features), 2)]
    for row in rows:
        cols = st.columns(2)
        for col, (icon, title, desc) in zip(cols, row):
            with col:
                st.markdown(
                    f'<div class="cp-card" style="margin-bottom:10px;">'
                    f'<div style="font-size:22px;margin-bottom:8px;">{icon}</div>'
                    f'<div style="font-size:14px;font-weight:700;color:#F1F2F8;margin-bottom:6px;">{title}</div>'
                    f'<div style="font-size:12px;color:#A0A8C8;line-height:1.7;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── Technology Stack ─────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(section_label("Technology Stack"), unsafe_allow_html=True)

    tech = [
        ("Python 3.10+", "Core language", "#6C5CE7"),
        ("Streamlit 1.63", "Web framework", "#FF6B8A"),
        ("Pandas 3 / NumPy 2", "Data processing", "#00B8D9"),
        ("Scikit-learn", "ML models (GradientBoosting)", "#20C997"),
        ("Plotly 7", "Interactive charts", "#F59E0B"),
        ("NetworkX 3", "Skill co-occurrence network", "#8B7FF0"),
        ("openpyxl", "Excel dataset reading", "#33C9E3"),
        ("Custom CSS", "Dark SaaS design system", "#FF8FA3"),
    ]

    tech_cols = st.columns(4)
    for i, (name, role, color) in enumerate(tech):
        with tech_cols[i % 4]:
            st.markdown(
                f'<div style="background:rgba(108,92,231,0.06);border:1px solid rgba(108,92,231,0.15);'
                f'border-radius:10px;padding:14px;margin-bottom:10px;text-align:center;">'
                f'<div style="font-size:13px;font-weight:700;color:{color};margin-bottom:4px;">{name}</div>'
                f'<div style="font-size:11px;color:#6B7280;">{role}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Dataset Information ───────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(section_label("Dataset Information"), unsafe_allow_html=True)

    st.markdown(
        '<div class="cp-card">'
        '<div style="font-size:14px;font-weight:700;color:#00B8D9;margin-bottom:12px;">'
        '&#128196; indian-job-market-dataset-2025.xlsx — Single Source of Truth</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px;color:#A0A8C8;">'
        '<div>&#8226; <strong style="color:#E2E8F0;">Source file:</strong> indian-job-market-dataset-2025.xlsx</div>'
        '<div>&#8226; <strong style="color:#E2E8F0;">Sheet:</strong> Sheet1</div>'
        f'<div>&#8226; <strong style="color:#E2E8F0;">Records:</strong> {len(df):,} job postings</div>'
        f'<div>&#8226; <strong style="color:#E2E8F0;">Original columns:</strong> 17</div>'
        f'<div>&#8226; <strong style="color:#E2E8F0;">Companies:</strong> {kpis["unique_companies"]:,}</div>'
        f'<div>&#8226; <strong style="color:#E2E8F0;">Unique roles:</strong> {kpis["unique_roles"]:,}</div>'
        f'<div>&#8226; <strong style="color:#E2E8F0;">Salary disclosed:</strong> {kpis["salary_coverage_pct"]}%</div>'
        f'<div>&#8226; <strong style="color:#E2E8F0;">Skill coverage:</strong> ~99%</div>'
        '</div>'
        '<div style="margin-top:12px;font-size:12px;color:#6B7280;line-height:1.7;">'
        'The platform derives 13 additional engineered features: location_primary, skills_list, '
        'skills_count, exp_bucket, exp_mid, salary_mid, min/max/mid salary in LPA, '
        'salary_disclosed, role_category, is_recent.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── How the dataset is used ───────────────────────────────────────────────
    st.markdown(section_label("How CareerPulse AI Uses the Dataset"), unsafe_allow_html=True)

    steps = [
        ("1", "Load & Validate", "The dataset is loaded once and cached. Columns are validated, duplicates removed, and 0-salary entries flagged as undisclosed.", "#6C5CE7"),
        ("2", "Clean & Derive", "Skills are parsed from comma-separated strings. Location is normalized to primary city. Experience and salary are parsed to numeric fields. Role categories are assigned via keyword matching.", "#00B8D9"),
        ("3", "Analyse", "All analytics (KPIs, role demand, skill frequency, salary stats, location stats) are computed dynamically using Pandas groupby and aggregation — never hard-coded.", "#20C997"),
        ("4", "Model", "A Gradient Boosting salary predictor is trained on ~33k disclosed salary records. Role matching uses vectorized Jaccard similarity. All models are evaluated on held-out test data.", "#FF6B8A"),
        ("5", "Respond", "The AI Copilot routes natural-language questions to analytics functions and returns data-backed answers. No LLM API is used — responses are strictly from dataset computations.", "#F59E0B"),
    ]

    for num, title, desc, color in steps:
        st.markdown(
            f'<div style="display:flex;gap:16px;align-items:flex-start;'
            f'padding:14px;margin-bottom:8px;background:rgba(108,92,231,0.04);'
            f'border:1px solid rgba(108,92,231,0.12);border-radius:12px;">'
            f'<div style="width:32px;height:32px;border-radius:50%;'
            f'background:{color};color:#fff;font-size:14px;font-weight:800;'
            f'display:flex;align-items:center;justify-content:center;flex-shrink:0;">{num}</div>'
            f'<div>'
            f'<div style="font-size:14px;font-weight:700;color:#F1F2F8;margin-bottom:4px;">{title}</div>'
            f'<div style="font-size:12px;color:#A0A8C8;line-height:1.7;">{desc}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Limitations ───────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(section_label("Limitations"), unsafe_allow_html=True)

    limitations = [
        ("Salary coverage", f"Only {kpis['salary_coverage_pct']}% of postings disclose salary. All salary analytics cover disclosed postings only."),
        ("Temporal data", "jobUploaded uses relative labels (~10-day window), not calendar dates. Long-term forecasting is not reliable."),
        ("ML accuracy", "Salary predictor R² ≈ 0.43 — directional estimates only. All predictions are labelled as estimates."),
        ("Skill normalization", "Skills are title-cased. Minor spelling variants may appear as separate skills."),
        ("Dataset snapshot", "Represents a point-in-time snapshot — not a continuously updating live job board."),
        ("Location parsing", "Multi-city postings are reduced to primary city; some nuance is lost."),
    ]

    lim_cols = st.columns(2)
    for i, (title, desc) in enumerate(limitations):
        with lim_cols[i % 2]:
            st.markdown(
                f'<div style="background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.18);'
                f'border-radius:10px;padding:12px 14px;margin-bottom:8px;">'
                f'<div style="font-size:12px;font-weight:700;color:#F59E0B;margin-bottom:4px;">{title}</div>'
                f'<div style="font-size:12px;color:#9CA3AF;line-height:1.6;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(disclaimer_box(
        "All insights, predictions, and recommendations in CareerPulse AI are derived "
        "from the uploaded dataset. They are statistical observations and should not be "
        "interpreted as guaranteed hiring outcomes, compensation promises, or professional career advice."
    ), unsafe_allow_html=True)
