"""
CareerPulse AI — Design System
Static dark theme. No animations. Streamlit 1.63 compatible.
"""

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL_CSS — injected via st.markdown(unsafe_allow_html=True)
# No @keyframes, no @import, no @media animation blocks.
# Pure property-value CSS only — safe for Streamlit 1.63 sanitizer.
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
:root {
  --cp-purple: #6C5CE7;
  --cp-cyan:   #00B8D9;
  --cp-pink:   #FF6B8A;
  --cp-green:  #20C997;
  --cp-amber:  #F59E0B;
  --bg-base:    #0D0F18;
  --bg-surface: #131625;
  --bg-card:    #181C2E;
  --bg-card2:   #1E2240;
  --border:     rgba(108,92,231,0.18);
  --border-h:   rgba(108,92,231,0.45);
  --text-1: #F1F2F8;
  --text-2: #A0A8C8;
  --text-3: #6B7280;
  --grad-brand:  linear-gradient(135deg,#6C5CE7,#00B8D9);
  --grad-warm:   linear-gradient(135deg,#6C5CE7,#FF6B8A);
  --grad-cool:   linear-gradient(135deg,#00B8D9,#20C997);
  --grad-purple: linear-gradient(135deg,#6C5CE7,#8B7FF0);
  --grad-pink:   linear-gradient(135deg,#FF6B8A,#FF8FA3);
  --grad-green:  linear-gradient(135deg,#20C997,#34D9B3);
  --grad-card:   linear-gradient(145deg,rgba(108,92,231,0.08),rgba(0,184,217,0.04));
  --r-sm:  8px;
  --r-md:  14px;
  --r-lg:  20px;
  --r-full: 100px;
  --shadow-glow: 0 0 24px rgba(108,92,231,0.25);
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
  background-color: var(--bg-base) !important;
  color: var(--text-1) !important;
  font-family: system-ui, -apple-system, sans-serif !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton, #MainMenu, footer, header {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  min-height: 0 !important;
}

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

[data-testid="stAppViewContainer"] > section:first-child { padding-top: 0 !important; }
[data-testid="stMain"] { padding-top: 0 !important; margin-top: 0 !important; }
.main { padding-top: 0 !important; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#0D0F18,#131625) !important;
  border-right: 1px solid rgba(108,92,231,0.15) !important;
  min-width: 230px !important;
  max-width: 230px !important;
}
[data-testid="stSidebarNav"],
[data-testid="stSidebarNav"] + div { display: none !important; }

h1,h2,h3,h4,h5,h6 {
  color: var(--text-1) !important;
  letter-spacing: -0.02em !important;
}

.stButton > button {
  background: var(--grad-brand) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 10px 22px !important;
  box-shadow: 0 2px 12px rgba(108,92,231,0.3) !important;
}
.stButton > button:hover {
  box-shadow: 0 6px 24px rgba(108,92,231,0.45) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div,
.stNumberInput > div > div > input {
  background-color: var(--bg-card2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text-1) !important;
  font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--cp-purple) !important;
  box-shadow: 0 0 0 3px rgba(108,92,231,0.15) !important;
}

.stSelectbox label,.stMultiSelect label,.stTextInput label,
.stTextArea label,.stSlider label,.stNumberInput label,
.stRadio label,.stCheckbox label {
  color: var(--text-2) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

.stSlider > div > div > div > div { background: var(--grad-brand) !important; }

.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: var(--r-sm) !important;
  color: var(--text-2) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: var(--grad-brand) !important;
  color: #fff !important;
  box-shadow: 0 2px 10px rgba(108,92,231,0.35) !important;
}

[data-testid="metric-container"] {
  background: var(--grad-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  padding: 16px !important;
}
[data-testid="metric-container"] label {
  color: var(--text-2) !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--text-1) !important;
  font-size: 24px !important;
  font-weight: 800 !important;
}

.stDataFrame {
  border-radius: var(--r-md) !important;
  border: 1px solid var(--border) !important;
}

.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text-1) !important;
  font-weight: 600 !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; margin: 24px 0 !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #131625; }
::-webkit-scrollbar-thumb { background: rgba(108,92,231,0.4); border-radius: 3px; }

.cp-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 20px 22px;
  margin-bottom: 14px;
}
.cp-card:hover {
  border-color: var(--border-h);
  box-shadow: var(--shadow-glow);
}

.cp-kpi {
  background: var(--grad-card);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 18px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cp-kpi::before {
  content: '';
  position: absolute; top:0; left:0; right:0; height:2px;
  background: var(--grad-brand);
}
.cp-kpi-icon { font-size: 20px; margin-bottom: 6px; display: block; }
.cp-kpi-val {
  font-size: 24px; font-weight: 800;
  letter-spacing: -0.03em; line-height: 1;
}
.cp-kpi-label {
  font-size: 10px; font-weight: 700; color: var(--text-3);
  text-transform: uppercase; letter-spacing: 0.08em; margin-top: 5px;
}

.cp-feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 24px 20px;
}
.cp-feature-card:hover {
  border-color: var(--border-h);
  box-shadow: var(--shadow-glow);
}
.cp-feature-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; margin-bottom: 14px;
}
.cp-feature-title { font-size: 15px; font-weight: 700; color: var(--text-1); margin-bottom: 6px; }
.cp-feature-desc  { font-size: 12px; color: var(--text-2); line-height: 1.6; }
.cp-feature-cta   { margin-top: 14px; font-size: 11px; font-weight: 700; color: var(--cp-purple);
                    text-transform: uppercase; letter-spacing: 0.06em; }

.cp-page-header {
  padding: 24px 0 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
.cp-page-badge {
  display: inline-block;
  background: rgba(108,92,231,0.12);
  border: 1px solid rgba(108,92,231,0.25);
  border-radius: var(--r-full);
  padding: 3px 12px;
  font-size: 11px; font-weight: 700;
  color: var(--cp-purple);
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;
}
.cp-page-title {
  font-size: 28px; font-weight: 800;
  color: var(--text-1); letter-spacing: -0.03em;
}
.cp-page-sub { font-size: 14px; color: var(--text-2); margin-top: 5px; }

.cp-disclaimer {
  background: rgba(245,158,11,0.07);
  border: 1px solid rgba(245,158,11,0.2);
  border-radius: var(--r-sm);
  padding: 10px 14px;
  font-size: 12px; color: #F59E0B; line-height: 1.5;
}

.cp-pill {
  display: inline-block;
  padding: 3px 11px;
  border-radius: var(--r-full);
  font-size: 12px; font-weight: 500;
  margin: 3px;
}
.cp-pill-blue   { background:rgba(108,92,231,0.12); color:#8B7FF0; border:1px solid rgba(108,92,231,0.2); }
.cp-pill-green  { background:rgba(32,201,151,0.12);  color:#20C997; border:1px solid rgba(32,201,151,0.2); }
.cp-pill-red    { background:rgba(255,107,138,0.12); color:#FF6B8A; border:1px solid rgba(255,107,138,0.2); }
.cp-pill-cyan   { background:rgba(0,184,217,0.12);   color:#00B8D9; border:1px solid rgba(0,184,217,0.2); }
.cp-pill-amber  { background:rgba(245,158,11,0.12);  color:#F59E0B; border:1px solid rgba(245,158,11,0.2); }

.cp-bar-outer {
  background: rgba(255,255,255,0.06);
  border-radius: var(--r-full); height: 8px; overflow: hidden;
  border: 1px solid var(--border);
}
.cp-bar-inner {
  height: 100%; border-radius: var(--r-full);
  background: var(--grad-brand);
}

.cp-section-label {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 18px;
}
.cp-section-label-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg,rgba(108,92,231,0.2),transparent);
}
.cp-section-label-text {
  font-size: 11px; font-weight: 700;
  color: var(--text-3);
  text-transform: uppercase; letter-spacing: 0.12em;
  white-space: nowrap;
}

.cp-chat-user {
  background: rgba(108,92,231,0.1);
  border: 1px solid rgba(108,92,231,0.2);
  border-radius: 12px 12px 4px 12px;
  padding: 12px 16px; margin: 8px 0; margin-left: 12%;
  font-size: 14px; color: var(--text-1);
}
.cp-chat-ai {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px 12px 12px 4px;
  padding: 14px 18px; margin: 8px 0; margin-right: 8%;
  font-size: 14px; color: var(--text-1); line-height: 1.65;
}
.cp-chat-ai-badge {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 10px; font-weight: 700; color: var(--cp-purple);
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;
  background: rgba(108,92,231,0.1);
  padding: 2px 8px; border-radius: var(--r-full);
}

.cp-anim-up   { opacity: 1; }
.cp-anim-down { opacity: 1; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#A0A8C8", family="system-ui, sans-serif", size=12),
    margin=dict(l=12, r=12, t=36, b=12),
    hoverlabel=dict(
        bgcolor="#1E2240",
        bordercolor="#6C5CE7",
        font=dict(color="#F1F2F8", size=12),
    ),
)

CHART_COLORS = [
    "#6C5CE7", "#00B8D9", "#FF6B8A", "#20C997",
    "#F59E0B", "#8B7FF0", "#33C9E3", "#FF8FA3",
    "#34D9B3", "#FBB040",
]

# ─────────────────────────────────────────────────────────────────────────────
# PYTHON HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", badge: str = "", icon: str = "") -> str:
    """Render a page header. Returns HTML string for st.markdown(unsafe_allow_html=True)."""
    badge_html = (
        f'<div class="cp-page-badge">{badge}</div>' if badge else ""
    )
    sub_html = (
        f'<div class="cp-page-sub">{subtitle}</div>' if subtitle else ""
    )
    icon_html = f'{icon} ' if icon else ""
    return (
        f'<div class="cp-page-header">'
        f'{badge_html}'
        f'<div class="cp-page-title">{icon_html}{title}</div>'
        f'{sub_html}'
        f'</div>'
    )


def section_label(text: str) -> str:
    return (
        f'<div class="cp-section-label">'
        f'<span class="cp-section-label-text">{text}</span>'
        f'<span class="cp-section-label-line"></span>'
        f'</div>'
    )


def kpi_card(value, label: str, icon: str = "📊", sub: str = "",
             gradient: str = "var(--grad-brand)", color: str = "") -> str:
    if color and gradient == "var(--grad-brand)":
        _cmap = {
            "#4f8ef7": "var(--grad-brand)",
            "#8b5cf6": "var(--grad-warm)",
            "#14b8a6": "var(--grad-cool)",
            "#f59e0b": "linear-gradient(135deg,#F59E0B,#FF6B8A)",
            "#10b981": "linear-gradient(135deg,#20C997,#00B8D9)",
            "#ef4444": "linear-gradient(135deg,#FF6B8A,#EF4444)",
        }
        gradient = _cmap.get(color, gradient)
    sub_html = f'<div class="cp-kpi-sub" style="font-size:11px;color:#6B7280;margin-top:4px;">{sub}</div>' if sub else ""
    return (
        f'<div class="cp-kpi">'
        f'<span class="cp-kpi-icon">{icon}</span>'
        f'<div class="cp-kpi-val" style="background:{gradient};'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">{value}</div>'
        f'<div class="cp-kpi-label">{label}</div>'
        f'{sub_html}'
        f'</div>'
    )


def score_bar(score: float, label: str = "") -> str:
    color = "#20C997" if score >= 70 else "#F59E0B" if score >= 40 else "#FF6B8A"
    lbl = f'<div style="font-size:12px;color:#A0A8C8;margin-bottom:5px;">{label}</div>' if label else ""
    return (
        f'<div style="margin-bottom:12px;">'
        f'{lbl}'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<div class="cp-bar-outer" style="flex:1;">'
        f'<div class="cp-bar-inner" style="width:{score}%;background:{color};"></div>'
        f'</div>'
        f'<div style="font-size:13px;font-weight:700;color:{color};min-width:36px;">{score:.0f}%</div>'
        f'</div>'
        f'</div>'
    )


def disclaimer_box(text: str) -> str:
    return f'<div class="cp-disclaimer">&#9888; {text}</div>'


def skill_pills(skills: list, style: str = "") -> str:
    cls_map = {
        "present": "cp-pill-green", "missing": "cp-pill-red",
        "cyan":    "cp-pill-cyan",  "amber":   "cp-pill-amber",
        "":        "cp-pill-blue",
    }
    cls = cls_map.get(style, "cp-pill-blue")
    pills = "".join(f'<span class="cp-pill {cls}">{s}</span>' for s in skills)
    return f'<div style="margin:8px 0;line-height:2;">{pills}</div>'


def nav_group(label: str) -> str:
    return (
        f'<div style="padding:10px 12px 3px;font-size:10px;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.1em;color:#4B5563;">{label}</div>'
    )


def back_button(fallback: str = "home") -> None:
    """
    Render a styled Back button using Streamlit's native button.
    Navigates to st.session_state.prev_page if set, otherwise to fallback.
    Call this at the TOP of every inner page's render() function.
    """
    import streamlit as st
    prev = st.session_state.get("prev_page", fallback)
    col, _ = st.columns([1, 6])
    with col:
        if st.button("← Back", key=f"back_btn_{prev}", use_container_width=True):
            st.session_state.page = prev
            st.rerun()
    st.markdown(
        '<div style="height:4px;border-bottom:1px solid rgba(108,92,231,0.1);margin-bottom:18px;"></div>',
        unsafe_allow_html=True,
    )

