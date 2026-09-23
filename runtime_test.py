"""Quick runtime chart-build test — no Streamlit server needed."""
import sys; sys.path.insert(0, '.')
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import plotly.graph_objects as go

from modules import data_loader as dl
from modules.ui_components import CHART_LAYOUT, CHART_COLORS, kpi_card, page_header, section_label

# Load dataset
df = pd.read_excel(dl.DEFAULT_PATH, sheet_name='Sheet1', engine='openpyxl')
df = dl._validate_columns(df)
df = dl._clean(df)
print(f"Dataset loaded: {len(df):,} rows")

# ── Test CHART_LAYOUT produces no duplicate-key errors ────────────────────────
from modules.feature_engineering import get_role_demand, get_skill_frequency, get_salary_distribution

roles = get_role_demand(df, top_n=10)
fig = go.Figure(go.Bar(x=roles["count"], y=roles["role"], orientation="h"))
fig.update_layout(**CHART_LAYOUT, height=340, showlegend=False,
                  yaxis=dict(autorange="reversed"),
                  xaxis=dict(showgrid=True, gridcolor="rgba(108,92,231,0.06)"))
print("Bar chart with CHART_LAYOUT: OK")

skills = get_skill_frequency(df, top_n=10)
fig2 = go.Figure(go.Bar(x=skills["count"], y=skills["skill"], orientation="h"))
fig2.update_layout(**CHART_LAYOUT, height=340, showlegend=False,
                   yaxis=dict(autorange="reversed"),
                   xaxis=dict(showgrid=True))
print("Skill chart: OK")

sal = get_salary_distribution(df)
fig3 = go.Figure(go.Bar(x=sal["range"], y=sal["count"]))
fig3.update_layout(**CHART_LAYOUT, height=280, showlegend=False)
print("Salary chart: OK")

# ── Test kpi_card variants ──────────────────────────────────────────────────
h1 = kpi_card("97,679", "Job Postings", "📋", gradient="var(--grad-brand)")
h2 = kpi_card("5,000",  "Companies",    color="#4f8ef7")   # backward compat
h3 = kpi_card("34%",    "Salary Coverage")
assert all("cp-kpi" in h for h in [h1, h2, h3]), "kpi_card HTML broken"
print("kpi_card variants: OK")

# ── Test page_header new signature ─────────────────────────────────────────
ph = page_header("Market Pulse", "subtitle here", badge="Analytics")
assert "cp-page-header" in ph and "cp-page-badge" in ph
ph2 = page_header("Salary Lab", "subtitle", badge="💰 Salary")
print("page_header: OK")

# ── Test section_label ────────────────────────────────────────────────────
sl = section_label("Live Market Snapshot")
assert "cp-section-label" in sl
print("section_label: OK")

# ── Test navigation structure ─────────────────────────────────────────────
from app import NAV_GROUPS, ALL_PAGES
assert len(NAV_GROUPS) == 6
assert len(ALL_PAGES) == 16
groups = [g["label"] for g in NAV_GROUPS]
expected = ["Overview", "Career Intelligence", "Opportunities", "Analytics", "AI", "System"]
assert groups == expected, f"Groups mismatch: {groups}"
print(f"Navigation: OK — {groups}")

# ── Verify all 16 page keys exist ─────────────────────────────────────────
expected_pages = {
    "home","market_pulse","skill_intelligence","salary_lab","role_explorer",
    "location_intelligence","company_intelligence","my_career","career_simulator",
    "career_path","opportunity_explorer","forecast_lab","ai_copilot",
    "data_explorer","data_quality","about_dataset"
}
assert set(ALL_PAGES.keys()) == expected_pages, f"Missing pages: {expected_pages - set(ALL_PAGES.keys())}"
print("All 16 pages present: OK")

print("\n=== ALL RUNTIME TESTS PASSED ===")
