"""CareerPulse AI — About Dataset Page"""

import streamlit as st
import pandas as pd

from modules.ui_components import page_header, CHART_LAYOUT, section_label, back_button
from modules.data_loader import REQUIRED_COLS


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("About Dataset", "Full transparency about the data powering CareerPulse AI", badge="ℹ️"),
                unsafe_allow_html=True)

    st.markdown("""
    <div class="cp-card" style="border-color: #4f8ef7;">
      <div style="font-size:16px; font-weight:700; color:#4f8ef7; margin-bottom:8px;">
        📢 Single Source of Truth
      </div>
      <div style="color:#9ca3c0; font-size:14px; line-height:1.7;">
        <strong style="color:#e8eaf0;">CareerPulse AI uses the uploaded dataset as its sole
        job-market data source.</strong><br>
        No external APIs, no synthetic records, no fabricated statistics.
        Every insight, chart, and prediction is derived exclusively from
        <strong style="color:#e8eaf0;">indian-job-market-dataset-2025.xlsx</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Dataset Identity")
        st.markdown(f"""
        <div class="cp-card">
          <table style="width:100%; font-size:13px; color:#9ca3c0; border-collapse:collapse;">
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">File</td>
                <td>indian-job-market-dataset-2025.xlsx</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Sheet</td>
                <td>Sheet1</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Total Records</td>
                <td>{len(df):,}</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Columns</td>
                <td>{len(df.columns)}</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Domain</td>
                <td>Indian Job Market 2025</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Currency</td>
                <td>Primarily INR (129 USD postings)</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Unique Companies</td>
                <td>{df['companyName'].nunique():,}</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Unique Job Titles</td>
                <td>{df['title'].nunique():,}</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Unique Locations</td>
                <td>{df['location_primary'].nunique():,}</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 Coverage Stats")
        sal_disclosed = int(df["salary_disclosed"].sum())
        st.markdown(f"""
        <div class="cp-card">
          <table style="width:100%; font-size:13px; color:#9ca3c0; border-collapse:collapse;">
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Salary Disclosed</td>
                <td>{sal_disclosed:,} ({sal_disclosed/len(df)*100:.1f}%)</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Skill Coverage</td>
                <td>{(df['skills_count']>0).sum():,} ({(df['skills_count']>0).mean()*100:.1f}%)</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Experience Coverage</td>
                <td>{df['minimumExperience'].notna().sum():,} ({df['minimumExperience'].notna().mean()*100:.1f}%)</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Rating Coverage</td>
                <td>{df['AggregateRating'].notna().sum():,} ({df['AggregateRating'].notna().mean()*100:.1f}%)</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Salary Range (disclosed)</td>
                <td>₹{df['min_salary_lpa'].min():.1f}L – ₹{df['max_salary_lpa'].max():.0f}L</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Avg Rating</td>
                <td>{df['AggregateRating'].mean():.2f} / 5.0</td></tr>
            <tr><td style="padding:6px 0; color:#e8eaf0; font-weight:600;">Temporal Window</td>
                <td>~10-day relative labels</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Column reference ───────────────────────────────────────────────────
    st.markdown("### 🗂️ Column Reference")
    col_descriptions = {
        "title":              "Job title / role name",
        "jobId":              "Unique job posting identifier",
        "currency":           "Salary currency (INR / USD)",
        "jobUploaded":        "Relative upload time (e.g. '3 Days Ago')",
        "companyName":        "Hiring company name",
        "tagsAndSkills":      "Comma-separated skill tags",
        "experience":         "Experience range string (e.g. '2-5 Yrs')",
        "salary":             "Human-readable salary string",
        "location":           "Job location (may include multiple cities)",
        "companyId":          "Internal company identifier",
        "ReviewsCount":       "Number of company reviews",
        "AggregateRating":    "Company aggregate rating (1–5)",
        "jobDescription":     "Full job description text",
        "minimumSalary":      "Parsed minimum salary (INR)",
        "maximumSalary":      "Parsed maximum salary (INR)",
        "minimumExperience":  "Parsed minimum experience (years)",
        "maximumExperience":  "Parsed maximum experience (years)",
    }
    col_df = pd.DataFrame([
        {"Column": k, "Description": v, "Type": str(df[k].dtype) if k in df.columns else "derived"}
        for k, v in col_descriptions.items()
    ])
    st.dataframe(col_df, use_container_width=True, hide_index=True)

    # ── Derived features ───────────────────────────────────────────────────
    st.markdown("### ⚙️ Derived Features (Added by CareerPulse AI)")
    derived = [
        ("location_primary",  "First city extracted from location field"),
        ("skills_list",       "Parsed list of individual skills"),
        ("skills_count",      "Number of skills per posting"),
        ("exp_bucket",        "Bucketed experience level (e.g. '2–5 Years')"),
        ("exp_mid",           "Midpoint of experience range"),
        ("salary_mid",        "Midpoint of salary range (INR)"),
        ("min_salary_lpa",    "Minimum salary in Lakhs per Annum"),
        ("max_salary_lpa",    "Maximum salary in Lakhs per Annum"),
        ("mid_salary_lpa",    "Mid-point salary in LPA"),
        ("salary_disclosed",  "Boolean: True if salary is disclosed"),
        ("role_category",     "Broad role category (e.g. 'Data & Analytics')"),
        ("is_recent",         "True if posting is within 5 days"),
    ]
    der_df = pd.DataFrame(derived, columns=["Feature", "Description"])
    st.dataframe(der_df, use_container_width=True, hide_index=True)

    # ── Cleaning steps ─────────────────────────────────────────────────────
    st.markdown("### 🧹 Data Cleaning Performed")
    st.markdown("""
    <div class="cp-card">
      <ol style="color:#9ca3c0; font-size:13px; line-height:2; margin:0; padding-left:20px;">
        <li>Removed duplicate job IDs (keeping first occurrence)</li>
        <li>Stripped whitespace from all string columns</li>
        <li>Replaced "nan" / "None" strings with proper NaN</li>
        <li>Salary = 0 treated as undisclosed (set to NaN)</li>
        <li>Skills parsed from comma-separated strings and title-cased</li>
        <li>Primary location extracted from multi-city strings (first token before comma)</li>
        <li>Hybrid/Remote prefixes stripped from location before extraction</li>
        <li>Experience parsed to float min/max fields</li>
        <li>Role categories assigned via keyword matching on job title</li>
        <li>Outlier salaries (&gt;300 LPA) excluded from ML salary predictor training only</li>
      </ol>
    </div>
    """, unsafe_allow_html=True)

    # ── Limitations ────────────────────────────────────────────────────────
    st.markdown("### ⚠️ Known Limitations")
    st.markdown("""
    <div class="cp-card" style="border-color:#f59e0b;">
      <ul style="color:#9ca3c0; font-size:13px; line-height:2; margin:0; padding-left:20px;">
        <li><strong style="color:#f59e0b;">Salary coverage:</strong>
            Only ~34% of postings disclose salary. Salary analytics exclude undisclosed postings.</li>
        <li><strong style="color:#f59e0b;">Temporal data:</strong>
            "jobUploaded" uses relative labels (~10-day window), not calendar dates.
            Long-term trend forecasting is not reliable with this data.</li>
        <li><strong style="color:#f59e0b;">Location parsing:</strong>
            Multi-city postings are reduced to primary city; some nuance is lost.</li>
        <li><strong style="color:#f59e0b;">Skill normalization:</strong>
            Skills are title-cased; minor variant spelling may appear as separate skills.</li>
        <li><strong style="color:#f59e0b;">Predictions:</strong>
            All ML predictions are estimates from dataset patterns — not hiring guarantees.</li>
        <li><strong style="color:#f59e0b;">Dataset snapshot:</strong>
            This dataset represents a point-in-time snapshot, not the full live job market.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)
