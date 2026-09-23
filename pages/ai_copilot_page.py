"""CareerPulse AI — AI Career Copilot Page"""

import streamlit as st

from modules.ai_copilot import answer
from modules.ui_components import page_header, disclaimer_box, CHART_LAYOUT, section_label, back_button

_SUGGESTIONS = [
    "What skills are most demanded?",
    "Which roles match Python and SQL?",
    "What salary is observed for Data Analyst?",
    "Compare Data Analyst vs Business Analyst",
    "What skills are required for a Software Engineer?",
    "Which cities have the most job postings?",
    "What if I learn Power BI and Tableau?",
    "What experience is needed for Data Scientist?",
    "What are the top companies hiring?",
    "Show me the job market overview",
]


def render(df):
    back_button(fallback="home")

    st.markdown(page_header("AI Career Copilot", "Ask natural-language questions — answered from the dataset", badge="🤖"),
                unsafe_allow_html=True)

    st.markdown("""
    <div class="cp-card">
      <strong>🔒 Strictly Grounded AI</strong><br>
      <span style="color:#9ca3c0;font-size:13px;">
        The AI Career Copilot answers only from the uploaded dataset.
        It does not invent statistics, salaries, companies, or trends.
        If the dataset cannot answer a question reliably, it says so.
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Chat history ───────────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Suggestion chips ───────────────────────────────────────────────────
    st.markdown("**💡 Try asking:**")
    chip_cols = st.columns(5)
    for i, suggestion in enumerate(_SUGGESTIONS[:10]):
        with chip_cols[i % 5]:
            if st.button(f"{suggestion[:40]}…" if len(suggestion) > 40 else suggestion,
                          key=f"chip_{i}", use_container_width=True):
                _handle_query(df, suggestion)
                st.rerun()

    st.markdown("---")

    # ── Input ──────────────────────────────────────────────────────────────
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            "Ask a career question",
            placeholder="e.g. What skills are most demanded for Data Engineer?",
            label_visibility="collapsed", key="copilot_input",
        )
    with col_btn:
        send = st.button("Ask →", type="primary", use_container_width=True)

    if send and user_query.strip():
        _handle_query(df, user_query.strip())
        st.rerun()

    # ── Chat display ───────────────────────────────────────────────────────
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding:48px; color:#6b7280;">
          <div style="font-size:40px;">🤖</div>
          <div style="font-size:16px; margin-top:8px;">
            Ask anything about the job market dataset above.
          </div>
          <div style="font-size:13px; margin-top:6px; color:#4b5563;">
            Tip: Try the suggestion chips for quick analysis.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Display conversation (newest first)
    for item in reversed(st.session_state.chat_history):
        # User bubble
        st.markdown(f"""
        <div class="cp-chat-user">
          <span style="font-size:11px;font-weight:700;color:#4f8ef7;
                       letter-spacing:0.06em;text-transform:uppercase;display:block;
                       margin-bottom:4px;">YOU</span>
          {item['query']}
        </div>
        """, unsafe_allow_html=True)

        # AI bubble
        st.markdown(f"""
        <div class="cp-chat-ai">
          <div class="cp-chat-ai-badge">⚡ CareerPulse AI · Dataset-Grounded</div>
          {item['response']}
        </div>
        """, unsafe_allow_html=True)

    # Clear history button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown(disclaimer_box(
        "All responses are derived from the uploaded dataset only. "
        "The AI does not use external knowledge, invent statistics, or guarantee outcomes."
    ), unsafe_allow_html=True)


def _handle_query(df, query: str):
    with st.spinner("Analyzing dataset…"):
        response = answer(df, query)
    st.session_state.chat_history.append({
        "query": query,
        "response": response,
    })
