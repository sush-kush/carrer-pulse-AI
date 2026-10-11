"""
CareerPulse AI — Main Application Entry Point
Run: streamlit run app.py  (from the careerpulse/ directory)
"""

import os
import sys
from pathlib import Path

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="CareerPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from modules.ui_components import GLOBAL_CSS
from modules.data_loader import load_data

# ── Inject CSS design system ──────────────────────────────────────────────────
# Pure property-value CSS only — no @keyframes, no @import, no @media blocks.
# Safe for Streamlit 1.63 HTML sanitizer.
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Extra layout tweaks ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Sidebar ── */
section[data-testid="stSidebar"] { min-width:230px !important; max-width:230px !important; }
[data-testid="stSidebarNav"],
[data-testid="stSidebarNav"] + div { display:none !important; }

/* ── Remove ALL top blank space ── */
[data-testid="stHeader"]      { display:none !important; height:0 !important; min-height:0 !important; }
[data-testid="stToolbar"]     { display:none !important; height:0 !important; min-height:0 !important; }
[data-testid="stDecoration"]  { display:none !important; height:0 !important; min-height:0 !important; }
.stDeployButton               { display:none !important; height:0 !important; }
#MainMenu                     { display:none !important; visibility:hidden !important; }
footer                        { display:none !important; visibility:hidden !important; }
header                        { display:none !important; visibility:hidden !important; }

/* ── Main content area — zero top gap ── */
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="block-container"] {
  padding-top: 0.5rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  padding-bottom: 2rem !important;
  max-width: 1400px !important;
  margin-top: 0 !important;
}

/* ── Eliminate the app-view top margin ── */
[data-testid="stAppViewContainer"] > section:first-child { padding-top: 0 !important; }
[data-testid="stMain"] { padding-top: 0 !important; margin-top: 0 !important; }
.main { padding-top: 0 !important; }

/* ── Back button — subtle secondary style ── */
.main .stButton > button[data-testid*="back_btn"],
.main .stButton button:has(div:contains("Back")) {
  background: rgba(108,92,231,0.1) !important;
  color: #A0A8C8 !important;
  border: 1px solid rgba(108,92,231,0.25) !important;
  box-shadow: none !important;
  font-size: 13px !important;
  padding: 6px 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Dataset path ─────────────────────────────────────────────────────────────
# app.py lives at the project root — dataset must be in the same directory.
# Using pathlib avoids any "../" issues on Streamlit Cloud.
DATASET_PATH = str(Path(__file__).resolve().parent / "indian-job-market-dataset-2025.xlsx")

# ── Load data (cached) ────────────────────────────────────────────────────────
df = load_data(DATASET_PATH)

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION DEFINITION — grouped for professional sidebar
# ─────────────────────────────────────────────────────────────────────────────
NAV_GROUPS = [
    {
        "label": "Overview",
        "items": [
            {"icon": "⚡", "label": "Home",        "key": "home"},
            {"icon": "🌐", "label": "Market Pulse", "key": "market_pulse"},
        ],
    },
    {
        "label": "Career Intelligence",
        "items": [
            {"icon": "🧠", "label": "Skill Intelligence", "key": "skill_intelligence"},
            {"icon": "💼", "label": "Role Explorer",       "key": "role_explorer"},
            {"icon": "🛤", "label": "Career Path",         "key": "career_path"},
            {"icon": "🔮", "label": "Career Simulator",    "key": "career_simulator"},
            {"icon": "🎯", "label": "My Career",           "key": "my_career"},
        ],
    },
    {
        "label": "Opportunities",
        "items": [
            {"icon": "🔍", "label": "Opportunity Explorer",  "key": "opportunity_explorer"},
            {"icon": "🏢", "label": "Company Intelligence",  "key": "company_intelligence"},
            {"icon": "📍", "label": "Location Intelligence", "key": "location_intelligence"},
        ],
    },
    {
        "label": "Analytics",
        "items": [
            {"icon": "💰", "label": "Salary Lab",    "key": "salary_lab"},
            {"icon": "📈", "label": "Forecast Lab",  "key": "forecast_lab"},
            {"icon": "📊", "label": "Data Explorer", "key": "data_explorer"},
        ],
    },
    {
        "label": "AI",
        "items": [
            {"icon": "🤖", "label": "AI Career Copilot", "key": "ai_copilot"},
        ],
    },
    {
        "label": "More",
        "items": [
            {"icon": "⭐", "label": "About Project",  "key": "about_project"},
            {"icon": "💬", "label": "Feedback",        "key": "feedback"},
            {"icon": "🗄", "label": "Data Quality",    "key": "data_quality"},
            {"icon": "ℹ", "label": "About Dataset",   "key": "about_dataset"},
        ],
    },
]

ALL_PAGES = {item["key"]: item["label"]
             for group in NAV_GROUPS for item in group["items"]}

# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "prev_page" not in st.session_state:
    st.session_state.prev_page = "home"

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — custom branded navigation
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown(
        """
        <div style="padding:18px 14px 14px;border-bottom:1px solid rgba(108,92,231,0.2);margin-bottom:8px;">
          <div style="display:flex;align-items:center;gap:9px;margin-bottom:4px;">
            <div style="width:28px;height:28px;border-radius:8px;
              background:linear-gradient(135deg,#6C5CE7,#00B8D9);
              display:flex;align-items:center;justify-content:center;
              font-size:14px;flex-shrink:0;">&#9889;</div>
            <div style="font-size:16px;font-weight:800;
              background:linear-gradient(135deg,#6C5CE7,#00B8D9);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              background-clip:text;letter-spacing:-0.02em;">CareerPulse AI</div>
          </div>
          <div style="font-size:10px;color:#6B7280;padding-left:37px;letter-spacing:0.05em;">
            Understand · Analyze · Predict
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Live data pill
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:6px;
          background:rgba(32,201,151,0.08);border:1px solid rgba(32,201,151,0.2);
          border-radius:20px;padding:5px 12px;margin:8px 10px 10px;font-size:11px;font-weight:600;">
          <div style="width:7px;height:7px;border-radius:50%;background:#20C997;"></div>
          <span style="color:#20C997;">LIVE DATA</span>
          <span style="color:#6B7280;margin-left:2px;">{len(df):,} postings</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation groups
    active = st.session_state.page
    for group in NAV_GROUPS:
        st.markdown(
            f'<div style="padding:10px 14px 3px;font-size:10px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.1em;color:#4B5563;">'
            f'{group["label"]}</div>',
            unsafe_allow_html=True,
        )
        for item in group["items"]:
            is_active = item["key"] == active
            if st.button(
                f"{item['icon']}  {item['label']}",
                key=f"nav_{item['key']}",
                use_container_width=True,
            ):
                # Track previous page so Back button can return here
                st.session_state.prev_page = st.session_state.page
                st.session_state.page = item["key"]
                st.rerun()

    # Footer
    st.markdown(
        """
        <div style="padding:12px 14px;margin-top:8px;
          border-top:1px solid rgba(108,92,231,0.1);font-size:10px;color:#4B5563;line-height:1.7;">
          Data: indian-job-market-dataset-2025.xlsx<br>
          No external job-market data used.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Sidebar button style ──────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  border-radius: 7px !important;
  color: #9CA3AF !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 7px 12px !important;
  text-align: left !important;
  justify-content: flex-start !important;
  width: 100% !important;
  transition: background 0.15s ease, color 0.15s ease !important;
  letter-spacing: 0 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(108,92,231,0.12) !important;
  color: #E2E8F0 !important;
  transform: none !important;
  filter: none !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:focus {
  outline: none !important;
  box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from pages.home import render; render(df)
elif page == "market_pulse":
    from pages.market_pulse import render; render(df)
elif page == "skill_intelligence":
    from pages.skill_intelligence import render; render(df)
elif page == "salary_lab":
    from pages.salary_lab import render; render(df)
elif page == "role_explorer":
    from pages.role_explorer import render; render(df)
elif page == "location_intelligence":
    from pages.location_intelligence import render; render(df)
elif page == "company_intelligence":
    from pages.company_intelligence import render; render(df)
elif page == "my_career":
    from pages.my_career import render; render(df)
elif page == "career_simulator":
    from pages.career_simulator import render; render(df)
elif page == "career_path":
    from pages.career_path import render; render(df)
elif page == "opportunity_explorer":
    from pages.opportunity_explorer import render; render(df)
elif page == "forecast_lab":
    from pages.forecast_lab import render; render(df)
elif page == "ai_copilot":
    from pages.ai_copilot_page import render; render(df)
elif page == "data_explorer":
    from pages.data_explorer import render; render(df)
elif page == "data_quality":
    from pages.data_quality import render; render(df)
elif page == "about_dataset":
    from pages.about_dataset import render; render(df)
elif page == "about_project":
    from pages.about_project import render; render(df)
elif page == "feedback":
    from pages.feedback import render; render(df)
else:
    from pages.home import render; render(df)
