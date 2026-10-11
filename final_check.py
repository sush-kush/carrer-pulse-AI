import sys
sys.path.insert(0, '.')
import pandas as pd
from modules import data_loader as dl
from modules.ui_components import (
    GLOBAL_CSS, CHART_LAYOUT, CHART_COLORS,
    page_header, section_label, kpi_card, score_bar,
    disclaimer_box, skill_pills,
)

df_raw = pd.read_excel(dl.DEFAULT_PATH, sheet_name='Sheet1', engine='openpyxl')
df = dl._validate_columns(df_raw)
df = dl._clean(df)

# Test kpi_card new signature
h = kpi_card('97,679', 'Job Postings', 'icon')
assert 'cp-kpi' in h, "kpi_card new sig failed"

# Test backward compat
h2 = kpi_card('5,000', 'Companies', color='#4f8ef7')
assert 'cp-kpi' in h2, "kpi_card backward compat failed"

# Test section_label
sl = section_label('Overview')
assert 'cp-section-label' in sl, "section_label failed"

# Test page_header new signature
ph = page_header('Market Pulse', 'subtitle', badge='Analytics')
assert 'cp-page-header' in ph, "page_header failed"

# Test CHART_LAYOUT
assert 'paper_bgcolor' in CHART_LAYOUT, "CHART_LAYOUT missing"

# Test navigation
from app import NAV_GROUPS, ALL_PAGES
assert len(NAV_GROUPS) == 6
assert len(ALL_PAGES) == 16

# Test all pages import
pages = ['market_pulse','skill_intelligence','salary_lab','role_explorer',
         'my_career','career_simulator','career_path','opportunity_explorer',
         'location_intelligence','company_intelligence','forecast_lab',
         'ai_copilot_page','data_explorer','data_quality','about_dataset','home']
for p in pages:
    mod = __import__(f'pages.{p}', fromlist=['render'])
    assert hasattr(mod, 'render'), f"No render in {p}"

print("ALL TESTS PASSED")
print("Nav groups:", len(NAV_GROUPS))
print("Total pages:", len(ALL_PAGES))
print("Dataset rows:", len(df))
