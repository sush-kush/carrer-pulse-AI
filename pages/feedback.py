"""CareerPulse AI — Feedback Page"""

import streamlit as st
from modules.ui_components import page_header, back_button, section_label, disclaimer_box


def render(df):
    back_button(fallback="home")

    st.markdown(page_header(
        "Feedback",
        "Help us improve CareerPulse AI — share your thoughts and suggestions",
        badge="💬",
    ), unsafe_allow_html=True)

    # ── Intro card ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="cp-card">'
        '<div style="font-size:14px;font-weight:700;color:#F1F2F8;margin-bottom:6px;">'
        'We value your feedback</div>'
        '<div style="font-size:13px;color:#A0A8C8;line-height:1.7;">'
        'CareerPulse AI is built to help users understand the Indian job market. '
        'Your feedback helps us improve the analytics, UI, and AI features. '
        'All fields are optional.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(section_label("Share Your Feedback"), unsafe_allow_html=True)

    # ── Form ─────────────────────────────────────────────────────────────────
    with st.form(key="feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Your Name (optional)",
                placeholder="e.g. Priya Sharma",
                key="fb_name",
            )
        with col2:
            email = st.text_input(
                "Email Address (optional)",
                placeholder="e.g. priya@example.com",
                key="fb_email",
            )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        rating = st.select_slider(
            "Overall Rating",
            options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
            value="⭐⭐⭐⭐ Very Good",
            key="fb_rating",
        )

        feature = st.selectbox(
            "Feature you're giving feedback about",
            options=[
                "General / Overall",
                "Home Dashboard",
                "Market Pulse",
                "Skill Intelligence",
                "Salary Lab + Predictor",
                "Role Explorer",
                "My Career",
                "Career Simulator",
                "Career Path Explorer",
                "Opportunity Explorer",
                "Location Intelligence",
                "Company Intelligence",
                "Forecast Lab",
                "AI Career Copilot",
                "Data Explorer",
                "UI / Design",
                "Other",
            ],
            key="fb_feature",
        )

        feedback_text = st.text_area(
            "Your Feedback / Suggestions",
            placeholder="Tell us what you liked, what could be improved, or any ideas you have...",
            height=160,
            key="fb_text",
        )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        would_recommend = st.radio(
            "Would you recommend CareerPulse AI to others?",
            options=["Yes, definitely", "Maybe", "Not sure yet"],
            horizontal=True,
            key="fb_recommend",
        )

        submitted = st.form_submit_button(
            "📩  Submit Feedback",
            use_container_width=False,
        )

    # ── Post-submission ───────────────────────────────────────────────────────
    if submitted:
        # Validate: at least feedback text
        if not feedback_text.strip():
            st.warning("Please enter your feedback or suggestions before submitting.")
        else:
            _show_success(name, rating, feature, feedback_text, would_recommend)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(disclaimer_box(
        "Feedback is collected for product improvement purposes only. "
        "This form does not currently persist submissions to a database — "
        "your feedback is processed in the current session. "
        "No personal data is stored beyond the session."
    ), unsafe_allow_html=True)

    # ── What we're working on ─────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(section_label("What We're Working On"), unsafe_allow_html=True)

    roadmap = [
        ("Resume Parser", "Auto-extract skills from uploaded resume PDF", "🔜", "#6C5CE7"),
        ("Live Job Data", "Integration with live job APIs for real-time dataset updates", "🔜", "#00B8D9"),
        ("Skill Trends", "Multi-month historical skill demand tracking", "🔜", "#20C997"),
        ("Career Timeline", "Visual career progression paths based on dataset patterns", "🔜", "#F59E0B"),
    ]

    rm_cols = st.columns(4)
    for col, (title, desc, badge, color) in zip(rm_cols, roadmap):
        with col:
            st.markdown(
                f'<div style="background:rgba(108,92,231,0.06);border:1px solid rgba(108,92,231,0.15);'
                f'border-radius:12px;padding:14px;text-align:center;">'
                f'<div style="font-size:11px;font-weight:700;color:{color};'
                f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">{badge}</div>'
                f'<div style="font-size:13px;font-weight:700;color:#E2E8F0;margin-bottom:6px;">{title}</div>'
                f'<div style="font-size:11px;color:#6B7280;line-height:1.5;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _show_success(name: str, rating: str, feature: str, text: str, recommend: str):
    """Display a professional success card after form submission."""
    display_name = name.strip() if name.strip() else "there"
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(32,201,151,0.1),rgba(0,184,217,0.06));'
        f'border:1px solid rgba(32,201,151,0.3);border-radius:16px;padding:28px 32px;margin-top:8px;">'
        f'<div style="font-size:28px;margin-bottom:12px;">&#10003;</div>'
        f'<div style="font-size:18px;font-weight:800;color:#20C997;margin-bottom:8px;">'
        f'Thank you, {display_name}!</div>'
        f'<div style="font-size:14px;color:#A0A8C8;line-height:1.7;margin-bottom:16px;">'
        f'Your feedback has been received for this session. '
        f'We appreciate you taking the time to help improve CareerPulse AI.'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">'
        f'<div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 12px;">'
        f'<div style="font-size:10px;color:#6B7280;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:4px;">Rating</div>'
        f'<div style="font-size:13px;font-weight:600;color:#F1F2F8;">{rating}</div>'
        f'</div>'
        f'<div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 12px;">'
        f'<div style="font-size:10px;color:#6B7280;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:4px;">Feature</div>'
        f'<div style="font-size:13px;font-weight:600;color:#F1F2F8;">{feature}</div>'
        f'</div>'
        f'<div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 12px;">'
        f'<div style="font-size:10px;color:#6B7280;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:4px;">Recommend</div>'
        f'<div style="font-size:13px;font-weight:600;color:#F1F2F8;">{recommend}</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
