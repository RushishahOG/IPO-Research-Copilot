import streamlit as st
from frontend.components.document_table import render_document_table


def render_dashboard():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-label">Document Management</div>
            <div class="page-header-title">Document Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    render_document_table()
