import streamlit as st
import tempfile
from pathlib import Path
from frontend.services.api_client import upload_document, APIClientError


def render_upload_zone():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-label">Upload Document</div>
            <div class="page-header-title">DRHP PDF Upload</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if uploaded_file.size > 100 * 1024 * 1024:
            st.error("File exceeds 100MB limit.")
            return

        with st.status(f"📄 Ingesting **{uploaded_file.name}**...", expanded=True) as status:
            st.write("⏳ Saving file...")
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name

                st.write("🔍 Processing document sections...")
                result = upload_document(tmp_path)

                Path(tmp_path).unlink(missing_ok=True)

                doc_name = result.get("doc_name", "unknown")
                section_count = result.get("section_count", 0)

                status.update(
                    label=f"✅ **{doc_name}** ingested successfully!",
                    state="complete",
                    expanded=False,
                )
                if section_count:
                    st.info(f"📄 {section_count} sections indexed")

                st.session_state.upload_status = "success"

            except APIClientError as e:
                st.error(str(e))
                st.session_state.upload_status = "error"
            except Exception as e:
                st.error(f"Upload failed: {e}")
                st.session_state.upload_status = "error"

    st.markdown(
        '<div style="text-align:center;margin-top:24px;"><span style="font-size:0.8rem;color:var(--text-muted);">Supported: <strong>PDF</strong>  ·  Max: <strong>100 MB</strong></span></div>',
        unsafe_allow_html=True,
    )
