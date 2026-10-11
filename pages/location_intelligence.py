"""CareerPulse AI — Location Intelligence"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from modules.feature_engineering import (
    get_location_demand, get_location_salary_stats,
    get_skills_by_location, get_company_stats,
)
from modules.data_loader import COL_TITLE, COL_COMPANY
from modules.ui_components import page_header, kpi_card, disclaimer_box, CHART_LAYOUT, section_label, back_button


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("Location Intelligence", "Analyze job market patterns across Indian cities", badge="📍"),
                unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────
    loc_demand = get_location_demand(df, top_n=5)
    top_loc = loc_demand.iloc[0]["location"] if not loc_demand.empty else "N/A"
    top_loc_count = int(loc_demand.iloc[0]["count"]) if not loc_demand.empty else 0

    cols = st.columns(4)
    with cols[0]: st.markdown(kpi_card(f"{df['location_primary'].nunique():,}", "Unique Locations", color="#4f8ef7"), unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_card(top_loc, "Most Active City", color="#8b5cf6"), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_card(f"{top_loc_count:,}", f"Postings in {top_loc}", color="#14b8a6"), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_card(f"{df[df['location_primary']=='Remote'].shape[0]:,}", "Remote Postings", color="#f59e0b"), unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Posting Volume", "💰 Salary by City", "🧠 Skills by City", "🔄 City Comparison"
    ])

    # ── Tab 1: Volume ─────────────────────────────────────────────────────
    with tab1:
        top_n = st.slider("Top N cities", 10, 40, 20, key="loc_topn")
        loc_df = get_location_demand(df, top_n=top_n)

        fig = go.Figure(go.Bar(
            x=loc_df["count"], y=loc_df["location"], orientation="h",
            marker=dict(color=loc_df["count"], colorscale=[[0,"#1e2130"],[1,"#4f8ef7"]], showscale=False),
            text=loc_df["count"].apply(lambda x: f"{x:,}"), textposition="outside",
        ))
        fig.update_layout(**CHART_LAYOUT, height=max(400, top_n * 22),
                          title=f"Job Postings by City (Top {top_n})",
                          yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                          xaxis=dict(showgrid=True, gridcolor="#2d3148", title="Postings"))
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart
        fig2 = px.pie(loc_df.head(10), values="count", names="location",
                      color_discrete_sequence=px.colors.qualitative.Set3,
                      title="Share of Postings (Top 10 Cities)")
        fig2.update_layout(**CHART_LAYOUT, height=360)
        fig2.update_traces(textposition="inside", textinfo="percent+label", hole=0.35)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"*{top_loc} has the highest number of postings in the filtered dataset.*")

    # ── Tab 2: Salary by city ─────────────────────────────────────────────
    with tab2:
        loc_sal = get_location_salary_stats(df)
        if loc_sal.empty:
            st.info("Insufficient salary data for location analysis.")
        else:
            st.markdown("#### Mean & Median Salary by Location (≥10 disclosed postings)")
            col_l, col_r = st.columns(2)
            with col_l:
                fig3 = go.Figure(go.Bar(
                    x=loc_sal["mean_lpa"].head(20), y=loc_sal["location"].head(20),
                    orientation="h", marker_color="#4f8ef7",
                    text=loc_sal["mean_lpa"].head(20).apply(lambda x: f"₹{x:.1f}L"),
                    textposition="outside",
                ))
                fig3.update_layout(**CHART_LAYOUT, height=480, title="Mean Salary (LPA)",
                                   yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                                   xaxis=dict(showgrid=True, gridcolor="#2d3148"))
                st.plotly_chart(fig3, use_container_width=True)
            with col_r:
                fig4 = go.Figure(go.Bar(
                    x=loc_sal["median_lpa"].head(20), y=loc_sal["location"].head(20),
                    orientation="h", marker_color="#8b5cf6",
                    text=loc_sal["median_lpa"].head(20).apply(lambda x: f"₹{x:.1f}L"),
                    textposition="outside",
                ))
                fig4.update_layout(**CHART_LAYOUT, height=480, title="Median Salary (LPA)",
                                   yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                                   xaxis=dict(showgrid=True, gridcolor="#2d3148"))
                st.plotly_chart(fig4, use_container_width=True)

            st.dataframe(
                loc_sal.rename(columns={"location": "City", "salary_count": "Postings w/ Salary",
                                         "mean_lpa": "Mean LPA", "median_lpa": "Median LPA",
                                         "min_lpa": "Min LPA", "max_lpa": "Max LPA"}),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 3: Skills by city ──────────────────────────────────────────────
    with tab3:
        top_locs_list = df["location_primary"].value_counts().head(30).index.tolist()
        sel_loc = st.selectbox("Select City", top_locs_list, key="loc_skills_city")
        loc_skills = get_skills_by_location(df, sel_loc, top_n=20)
        if loc_skills.empty:
            st.info(f"No skill data for {sel_loc}.")
        else:
            fig5 = go.Figure(go.Bar(
                x=loc_skills["pct"], y=loc_skills["skill"], orientation="h",
                marker_color="#14b8a6",
                text=loc_skills["pct"].apply(lambda x: f"{x}%"),
                textposition="outside",
            ))
            fig5.update_layout(**CHART_LAYOUT, height=480, title=f"Top Skills in {sel_loc}",
                               yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                               xaxis=dict(showgrid=True, gridcolor="#2d3148", title="% of Postings"))
            st.plotly_chart(fig5, use_container_width=True)

    # ── Tab 4: City comparison ─────────────────────────────────────────────
    with tab4:
        top_locs_list2 = df["location_primary"].value_counts().head(30).index.tolist()
        selected_cities = st.multiselect(
            "Select cities to compare (2–6)",
            top_locs_list2,
            default=top_locs_list2[:4],
            key="loc_compare",
        )

        if len(selected_cities) < 2:
            st.info("Select at least 2 cities to compare.")
        else:
            compare_data = []
            for city in selected_cities:
                sub = df[df["location_primary"] == city]
                sal = sub[sub["salary_disclosed"] & sub["mid_salary_lpa"].notna()]["mid_salary_lpa"]
                compare_data.append({
                    "City": city,
                    "Postings": len(sub),
                    "Companies": sub[COL_COMPANY].nunique(),
                    "Unique Roles": sub[COL_TITLE].nunique(),
                    "Avg Salary LPA": round(sal.mean(), 2) if not sal.empty else None,
                    "Median Salary LPA": round(sal.median(), 2) if not sal.empty else None,
                    "Fresher Postings": int((sub["minimumExperience"] == 0).sum()),
                })
            cmp_df = pd.DataFrame(compare_data)
            st.dataframe(cmp_df, use_container_width=True, hide_index=True)

            fig6 = go.Figure()
            fig6.add_trace(go.Bar(name="Postings", x=cmp_df["City"], y=cmp_df["Postings"],
                                   marker_color="#4f8ef7"))
            fig6.add_trace(go.Bar(name="Companies", x=cmp_df["City"], y=cmp_df["Companies"],
                                   marker_color="#8b5cf6"))
            fig6.add_trace(go.Bar(name="Unique Roles", x=cmp_df["City"], y=cmp_df["Unique Roles"],
                                   marker_color="#14b8a6"))
            fig6.update_layout(**CHART_LAYOUT, height=360, barmode="group",
                               xaxis=dict(title="City"),
                               yaxis=dict(showgrid=True, gridcolor="#2d3148"),
                               legend=dict(orientation="h", y=1.02))
            st.plotly_chart(fig6, use_container_width=True)

    st.markdown(disclaimer_box(
        "All location data is from the uploaded dataset. "
        "Claims are framed as dataset observations, not absolute market facts."
    ), unsafe_allow_html=True)
