import streamlit as st
from frontend.components.upload_zone import render_upload_zone
from frontend.services.api_client import get_documents, APIClientError


def render_upload():
    render_upload_zone()

    st.markdown("<hr style='border-color:var(--border);margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="margin-bottom:12px;">
            <span style="font-size:0.88rem;font-weight:600;color:var(--text-secondary);">Recently Ingested Documents</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        docs = get_documents()
        if docs:
            for doc in docs[-5:]:
                st.markdown(
                    f"""
                    <div class="doc-row">
                        <span style="font-size:1.1rem;">📄</span>
                        <div style="flex:1;">
                            <div class="doc-name">{doc['doc_name']}</div>
                            <div class="doc-meta">{doc.get('section_count', '?')} sections  ·  {doc.get('status', 'unknown')}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No documents uploaded yet.")
    except APIClientError:
        st.caption("Could not load document list.")
