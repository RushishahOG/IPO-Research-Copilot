import streamlit as st

PAGES_ORDERED = [
    ("home", "🏠", "Home"),
    ("dashboard", "📂", "Dashboard"),
    ("upload", "📤", "Upload"),
    ("chat", "💬", "Chat"),
    ("analytics", "📈", "Analytics"),
]


def render_nav_item(page_key: str, icon: str, label: str, is_active: bool):
    active_class = "active" if is_active else ""
    st.markdown(
        f"""
        <div class="nav-item {active_class}" onclick="document.querySelector('[data-nav=\"{page_key}\"]').click()">
            <span class="nav-icon">{icon}</span>
            <span class="nav-label">{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    clicked = st.button(
        label,
        key=f"nav_{page_key}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    )
    if clicked:
        st.session_state.page = page_key
        st.rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">📊</div>
                <div class="sidebar-title">DRHP Analyst AI</div>
                <div class="sidebar-subtitle">Multi-Agent RAG System</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current = st.session_state.get("page", "home")

        for page_key, icon, label in PAGES_ORDERED:
            is_active = current == page_key
            render_nav_item(page_key, icon, label, is_active)

        st.markdown(
            """
            <div class="sidebar-footer">
                DRHP Analyst AI v1.0<br>
                Built with LangGraph + Pinecone
            </div>
            """,
            unsafe_allow_html=True,
        )
