"""CareerPulse AI — Data Explorer"""

import streamlit as st
import pandas as pd

from modules.data_loader import COL_TITLE, COL_COMPANY, COL_LOCATION
from modules.ui_components import page_header, CHART_LAYOUT, section_label, back_button

DISPLAY_COLS = [
    "title", "companyName", "location_primary", "experience",
    "min_salary_lpa", "max_salary_lpa", "salary", "exp_bucket",
    "skills_count", "AggregateRating",
]


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Data Explorer", "Search, filter, sort, and inspect the underlying dataset", badge="📊"),
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cp-card">
      <strong>Dataset:</strong> indian-job-market-dataset-2025.xlsx &nbsp;·&nbsp;
      <strong>Records:</strong> {len(df):,} &nbsp;·&nbsp;
      <strong>Columns:</strong> {len(df.columns)} &nbsp;·&nbsp;
      <span style="color:#10b981;">All data is from the uploaded file.</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────
    st.markdown("### 🔧 Filters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_title = st.text_input("Search Job Title", placeholder="e.g. Data Analyst",
                                      key="de_title")
    with col2:
        search_company = st.text_input("Search Company", placeholder="e.g. Accenture",
                                        key="de_company")
    with col3:
        top_locs = ["All"] + df["location_primary"].value_counts().head(40).index.tolist()
        sel_loc = st.selectbox("Location", top_locs, key="de_loc")
    with col4:
        exp_opts = ["All"] + ["Fresher (0 yrs)", "0–2 Years", "2–5 Years",
                               "5–8 Years", "8–12 Years", "12+ Years"]
        sel_exp = st.selectbox("Experience", exp_opts, key="de_exp")

    col5, col6, col7 = st.columns(3)
    with col5:
        salary_only = st.checkbox("Only postings with disclosed salary", key="de_sal")
    with col6:
        rated_only = st.checkbox("Only postings with company rating", key="de_rated")
    with col7:
        recent_only = st.checkbox("Recent postings only (≤5 days)", key="de_recent")

    # ── Apply filters ──────────────────────────────────────────────────────
    fdf = df.copy()

    if search_title:
        fdf = fdf[fdf[COL_TITLE].str.lower().str.contains(search_title.lower(), na=False)]
    if search_company:
        fdf = fdf[fdf[COL_COMPANY].str.lower().str.contains(search_company.lower(), na=False)]
    if sel_loc != "All":
        fdf = fdf[fdf["location_primary"] == sel_loc]
    if sel_exp != "All":
        fdf = fdf[fdf["exp_bucket"] == sel_exp]
    if salary_only:
        fdf = fdf[fdf["salary_disclosed"]]
    if rated_only:
        fdf = fdf[fdf["AggregateRating"].notna()]
    if recent_only:
        recent_labels = {"Just Now", "Few Hours Ago", "Today", "1 Day Ago",
                         "2 Days Ago", "3 Days Ago", "4 Days Ago", "5 Days Ago"}
        fdf = fdf[fdf["jobUploaded"].isin(recent_labels)]

    st.markdown(f"**{len(fdf):,} records match your filters.**")

    if fdf.empty:
        st.warning("No records match the current filters.")
        return

    # ── Column selection ───────────────────────────────────────────────────
    available_cols = [c for c in DISPLAY_COLS if c in fdf.columns]
    selected_cols = st.multiselect(
        "Columns to display",
        available_cols,
        default=available_cols[:8],
        key="de_cols",
    )

    if not selected_cols:
        st.info("Select at least one column.")
        return

    # ── Sort ───────────────────────────────────────────────────────────────
    sort_col = st.selectbox("Sort by", ["—"] + selected_cols, key="de_sort")
    sort_dir = st.radio("Sort direction", ["Descending", "Ascending"],
                         horizontal=True, key="de_sortdir")

    display = fdf[selected_cols].copy()

    if sort_col != "—" and sort_col in display.columns:
        display = display.sort_values(sort_col, ascending=(sort_dir == "Ascending"))

    # Rename for display
    rename_map = {
        "title": "Job Title", "companyName": "Company",
        "location_primary": "Location", "experience": "Experience",
        "min_salary_lpa": "Min Salary (LPA)", "max_salary_lpa": "Max Salary (LPA)",
        "salary": "Salary (raw)", "exp_bucket": "Exp Level",
        "skills_count": "# Skills", "AggregateRating": "Rating",
    }
    display = display.rename(columns={k: v for k, v in rename_map.items() if k in display.columns})

    # Pagination
    page_size = st.slider("Rows per page", 10, 200, 50, step=10, key="de_pagesize")
    total_pages = max(1, (len(display) - 1) // page_size + 1)
    page_num = st.number_input(f"Page (1–{total_pages})", min_value=1,
                                max_value=total_pages, value=1, key="de_page")
    start = (page_num - 1) * page_size
    end   = start + page_size

    st.dataframe(
        display.iloc[start:end].reset_index(drop=True),
        use_container_width=True,
        height=600,
    )

    st.markdown(f"*Showing rows {start+1}–{min(end, len(display))} of {len(display):,}.*")

    # ── Row inspector ──────────────────────────────────────────────────────
    with st.expander("🔎 Inspect a Record", expanded=False):
        idx = st.number_input("Row index (0-based from full filtered set)",
                               min_value=0, max_value=len(fdf)-1, value=0, key="de_inspect")
        record = fdf.iloc[int(idx)]
        cols_to_show = [
            "title", "companyName", "location_primary", "experience",
            "salary", "min_salary_lpa", "max_salary_lpa",
            "skills_list", "AggregateRating", "ReviewsCount",
            "jobUploaded", "role_category",
        ]
        for col in cols_to_show:
            if col in record.index:
                val = record[col]
                if col == "skills_list" and isinstance(val, list):
                    val = ", ".join(val)
                st.markdown(f"**{col}:** {val}")
