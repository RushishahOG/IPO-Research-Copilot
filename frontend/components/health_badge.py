import streamlit as st
from frontend.services.api_client import health_check, APIClientError


def render_health_badge():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        status = "loading"
        label = "Checking..."
        try:
            result = health_check()
            if result.get("status") == "healthy":
                status = "healthy"
                label = "System Healthy"
            else:
                status = "unhealthy"
                label = "System Degraded"
        except APIClientError:
            status = "unhealthy"
            label = "Backend Offline"

        st.markdown(
            f"""
            <div class="status-badge {status}" style="display:inline-flex; margin: 0 auto 8px;">
                <span class="status-dot {status}"></span>
                {label}
            </div>
            """,
            unsafe_allow_html=True,
        )
