import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from frontend.utils.constants import PAGE_CONFIG
from frontend.utils.session import init_session_state
from frontend.utils.theme import T
from frontend.components.sidebar import render_sidebar
from frontend.components.health_badge import render_health_badge
from frontend.views.dashboard import render_dashboard
from frontend.views.upload import render_upload
from frontend.views.chat import render_chat
from frontend.views.analytics import render_analytics
from frontend.services.api_client import get_documents, APIClientError

st.set_page_config(**PAGE_CONFIG)
init_session_state()

css_path = Path(__file__).parent / "styles" / "main.css"
with open(css_path, "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_sidebar()

page = st.session_state.get("page", "home")


def render_home():
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-title">DRHP Analyst AI</div>
            <div class="hero-subtitle">
                Multi-Agent RAG System for Draft Red Herring Prospectus Analysis.
                AI-powered document intelligence for institutional-grade IPO research.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_health_badge()

    try:
        docs = get_documents()
        total_docs = len(docs)
        total_sections = sum(d.get("section_count", 0) for d in docs if d.get("section_count"))
    except APIClientError:
        total_docs = 0
        total_sections = 0

    metrics = [
        (str(total_docs), "Documents"),
        (str(total_sections), "Total Sections"),
        ("8", "AI Agents"),
        ("< 3s", "Avg. Response"),
    ]
    cols = st.columns(4)
    for col, (value, label) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Multi-Agent Architecture</div>
                <div class="feature-desc">8 specialist AI agents analyze risk, financials, legal, regulatory, IPO details, and more in parallel.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Section-Aware Retrieval</div>
                <div class="feature-desc">Intelligent RAG pipeline with section-level filtering and noise reduction for precise answers.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Evidence-Based Answers</div>
                <div class="feature-desc">Every response includes page-level source citations with snippet evidence for verification.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">Hallucination Prevention</div>
                <div class="feature-desc">Strict grounding rules enforce evidence-only answers with source validation.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Real-Time Processing</div>
                <div class="feature-desc">Instant ingestion pipeline with PDF splitting, vector embedding, and knowledge storage.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Investment Scoring</div>
                <div class="feature-desc">Automated red flag detection and investment scoring across risk, financial, and governance dimensions.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c2:
        if st.button("📂 View Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "dashboard"
            st.rerun()
    with c3:
        if st.button("📤 Upload Document", use_container_width=True, type="secondary"):
            st.session_state.page = "upload"
            st.rerun()

    st.markdown(
        """
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;max-width:900px;margin:32px auto 0;">
            <div class="glass-card quick-start-card">
                <h4 style="color:var(--accent);margin-bottom:10px;">⚡ Quick Start</h4>
                <ol style="color:var(--text-secondary);font-size:0.88rem;line-height:2.1;padding-left:20px;">
                    <li>Upload a DRHP PDF document</li>
                    <li>Wait for ingestion to complete</li>
                    <li>Navigate to Chat to ask questions</li>
                    <li>Get AI-powered, evidence-backed answers</li>
                </ol>
            </div>
            <div class="glass-card">
                <h4 style="color:var(--blue);margin-bottom:10px;">🔧 Tech Stack</h4>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">
                    <span class="tech-stack-badge">FastAPI</span>
                    <span class="tech-stack-badge">LangGraph</span>
                    <span class="tech-stack-badge">Pinecone</span>
                    <span class="tech-stack-badge">Gemini</span>
                    <span class="tech-stack-badge">Groq</span>
                    <span class="tech-stack-badge">Streamlit</span>
                    <span class="tech-stack-badge">Sentence Transformers</span>
                    <span class="tech-stack-badge">PyMuPDF</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="footer">DRHP Analyst AI v1.0  ·  Built with LangGraph, Pinecone & FastAPI  ·  © 2026</div>',
        unsafe_allow_html=True,
    )


if page == "home":
    render_home()
elif page == "dashboard":
    render_dashboard()
elif page == "upload":
    render_upload()
elif page == "chat":
    render_chat()
elif page == "analytics":
    render_analytics()
else:
    render_home()
