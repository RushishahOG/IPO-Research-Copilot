import streamlit as st


def render_source_panel(sources: list):
    if not sources:
        return

    st.markdown(
        '<div class="source-section-title">📎 Evidence Sources</div>',
        unsafe_allow_html=True,
    )

    for i, src in enumerate(sources):
        page = src.get("page", "N/A")
        section = src.get("section", "Unknown")
        snippet = src.get("snippet", "")

        with st.expander(f"Source {i+1} — {section}  ·  Page {page}"):
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.markdown(
                    f"""
                    <div class="source-card-page">
                        <div style="font-size:0.65rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.04em;">PAGE</div>
                        <div style="font-size:1.5rem;font-weight:700;color:var(--accent);line-height:1.2;">{page}</div>
                    </div>
                    <div class="source-card-section">
                        <div style="font-size:0.65rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.04em;">SECTION</div>
                        <div style="font-size:0.82rem;font-weight:600;color:var(--blue);margin-top:2px;">{section}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_b:
                st.markdown(
                    f"""
                    <div class="source-snippet-box">
                        <div style="font-size:0.65rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">SNIPPET</div>
                        <div style="color:var(--text-secondary);font-size:0.85rem;line-height:1.7;">{snippet}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
