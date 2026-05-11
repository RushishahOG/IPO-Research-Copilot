import streamlit as st
from frontend.services.api_client import chat_with_document, get_documents, APIClientError
from frontend.components.source_panel import render_source_panel
from frontend.utils.constants import SUGGESTED_PROMPTS, QUERY_TYPE_LABELS


def process_prompt(query: str):
    if not query or not st.session_state.selected_doc:
        return
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.spinner("🤖 Analyzing document..."):
        try:
            result = chat_with_document(query, st.session_state.selected_doc)
            answer = result.get("answer", "No answer generated.")
            sources = result.get("sources", [])
            agents = result.get("agents_used", [])
            qtype = result.get("query_type", "general")
            exec_time = result.get("execution_time_ms", 0)
            agent_labels = [QUERY_TYPE_LABELS.get(a, a) for a in agents]
            meta = f"⏱ {exec_time:.0f}ms  ·  🎯 {QUERY_TYPE_LABELS.get(qtype, qtype)}"
            if agent_labels:
                meta += f"  ·  🤖 {', '.join(agent_labels)}"
            full_response = f"{answer}\n\n---\n*{meta}*"
            st.session_state.chat_history.append({
                "role": "assistant", "content": full_response, "sources": sources,
            })
            st.session_state.query_analytics.append({
                "query": query, "doc_name": st.session_state.selected_doc,
                "query_type": qtype, "execution_time_ms": exec_time,
                "sources_count": len(sources),
            })
        except APIClientError as e:
            st.session_state.chat_history.append({
                "role": "assistant", "content": f"❌ **Error:** {e}", "sources": [],
            })
    st.rerun()


def render_chat():
    st.markdown(
        """
        <div class="page-header" style="text-align:center;">
            <div class="page-header-label">AI Assistant</div>
            <div class="page-header-title">Chat with DRHP Documents</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pending = st.session_state.pop("_pending_prompt", None)
    if pending and st.session_state.selected_doc:
        process_prompt(pending)
        return

    col_chat, col_sidebar = st.columns([3, 1])

    with col_chat:

        def render_messages():
            for msg in st.session_state.chat_history:
                role = msg["role"]
                is_user = role == "user"
                css = "user" if is_user else "assistant"
                avatar = "👤" if is_user else "🤖"

                st.markdown(
                    f"""
                    <div class="chat-message {css}">
                        <div class="chat-avatar {css}">{avatar}</div>
                        <div class="chat-content">{msg["content"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if not is_user and msg.get("sources"):
                    render_source_panel(msg["sources"])

        render_messages()

        if not st.session_state.chat_history:
            st.markdown(
                """
                <div class="chat-empty">
                    <div class="chat-empty-icon">💬</div>
                    <div class="chat-empty-title">Ask a question about the DRHP document</div>
                    <div class="chat-empty-desc">Select a document from the sidebar and type your query below</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        query = st.chat_input("Ask a question about the DRHP...", key="chat_query")
        if query and st.session_state.selected_doc:
            process_prompt(query)

    with col_sidebar:
        st.markdown(
            "<div style='font-size:0.72rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;font-weight:600;'>Document</div>",
            unsafe_allow_html=True,
        )

        try:
            docs = get_documents()
            doc_names = [d["doc_name"] for d in docs] if docs else []
            if doc_names:
                idx = 0
                if st.session_state.selected_doc in doc_names:
                    idx = doc_names.index(st.session_state.selected_doc)
                selected = st.selectbox(
                    "Document",
                    doc_names,
                    index=idx,
                    label_visibility="collapsed",
                )
                st.session_state.selected_doc = selected
            else:
                st.warning("No documents available. Upload a PDF first.")
                st.session_state.selected_doc = None
        except APIClientError:
            st.error("Backend unavailable")
            st.session_state.selected_doc = None

        if st.session_state.selected_doc:
            st.markdown(
                f"""
                <div style="margin-top:8px;padding:10px 14px;background:var(--accent-dim);border:1px solid rgba(0,230,118,0.12);border-radius:var(--radius-md);">
                    <div style="font-size:0.65rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.04em;">ACTIVE DOCUMENT</div>
                    <div style="font-size:0.9rem;font-weight:600;color:var(--accent);margin-top:2px;">📄 {st.session_state.selected_doc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='font-size:0.72rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.06em;margin-top:20px;margin-bottom:8px;font-weight:600;'>Suggested Prompts</div>",
            unsafe_allow_html=True,
        )
        for prompt in SUGGESTED_PROMPTS:
            key = f"sp_{hash(prompt)}"
            if st.button(prompt, key=key, use_container_width=True):
                st.session_state._pending_prompt = prompt
                st.rerun()
