import streamlit as st
import pandas as pd
from frontend.services.api_client import get_documents, delete_document, reingest_document, APIClientError
from frontend.utils.helpers import format_timestamp


def render_document_table():
    with st.spinner("Loading documents..."):
        try:
            docs = get_documents()
        except APIClientError as e:
            st.error(str(e))
            return

    if not docs:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;">
                <div style="font-size:3rem;margin-bottom:16px;opacity:0.5;">📂</div>
                <div style="font-size:1.15rem;color:var(--text-secondary);">No documents ingested yet</div>
                <div style="font-size:0.88rem;color:var(--text-tertiary);margin-top:8px;">Upload a DRHP PDF to get started</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(docs)
    if not df.empty and "uploaded_at" in df.columns:
        df["uploaded_at"] = df["uploaded_at"].apply(format_timestamp)

    display_cols = ["doc_name", "status", "section_count", "uploaded_at"]
    display_cols = [c for c in display_cols if c in df.columns]

    search = st.text_input("🔍 Search documents", placeholder="Filter by document name...")
    if search:
        mask = df["doc_name"].str.contains(search, case=False, na=False)
        df = df[mask]

    for _, row in df.iterrows():
        doc_name = row["doc_name"]

        with st.container():
            cols = st.columns([3, 1, 1, 1, 1])

            with cols[0]:
                st.markdown(f'<div class="doc-name">{doc_name}</div>', unsafe_allow_html=True)
                if "uploaded_at" in row:
                    st.markdown(f'<div class="doc-meta">Uploaded: {row["uploaded_at"]}</div>', unsafe_allow_html=True)

            with cols[1]:
                status = row.get("status", "unknown")
                is_ready = status == "ready"
                c = "var(--accent)" if is_ready else "var(--warning)"
                bg = "var(--accent-dim)" if is_ready else "var(--warning-dim, rgba(255,214,0,0.1))"
                bd = "rgba(0,230,118,0.2)" if is_ready else "rgba(255,214,0,0.2)"
                st.markdown(
                    f"""<span class="doc-status" style="background:{bg};color:{c};border:1px solid {bd};">
                        ● {status}</span>""",
                    unsafe_allow_html=True,
                )

            with cols[2]:
                sc = row.get("section_count")
                if sc is not None:
                    st.markdown(f'<span style="font-size:0.88rem;font-weight:500;">{sc}</span> <span style="font-size:0.75rem;color:var(--text-tertiary);">sections</span>', unsafe_allow_html=True)

            with cols[3]:
                if st.button("🔄 Reingest", key=f"reing_{doc_name}", use_container_width=True):
                    with st.spinner(f"Re-ingesting {doc_name}..."):
                        try:
                            result = reingest_document(doc_name)
                            st.success(result.get("message", f"{doc_name} re-ingested"))
                            st.rerun()
                        except APIClientError as e:
                            st.error(str(e))

            with cols[4]:
                if st.button("🗑️ Delete", key=f"del_{doc_name}", use_container_width=True):
                    try:
                        result = delete_document(doc_name)
                        st.success(f"Deleted {result['doc_name']}")
                        st.rerun()
                    except APIClientError as e:
                        st.error(str(e))

        st.markdown('<hr class="doc-divider">', unsafe_allow_html=True)
