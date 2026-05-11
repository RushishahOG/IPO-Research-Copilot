import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.services.api_client import get_documents, APIClientError


def _plotly_layout(height: int = 280) -> dict:
    return {
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font_color": "rgba(255,255,255,0.65)",
        "font_size": 11,
        "height": height,
        "margin": dict(l=0, r=0, t=4, b=0),
        "hovermode": "x unified",
        "xaxis": dict(showgrid=False),
        "yaxis": dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
    }


def render_analytics():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-label">System Analytics</div>
            <div class="page-header-title">Analytics Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        docs = get_documents()
    except APIClientError:
        docs = []

    total_docs = len(docs)
    total_sections = sum(d.get("section_count", 0) for d in docs if d.get("section_count"))
    ready_docs = sum(1 for d in docs if d.get("status") == "ready")
    avg_sections = round(total_sections / total_docs, 1) if total_docs else 0

    metrics = [
        ("Total Documents", str(total_docs)),
        ("Indexed Sections", str(total_sections)),
        ("Ready Documents", str(ready_docs)),
        ("Avg Sections/Doc", str(avg_sections)),
    ]

    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics):
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

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(
            '<h4 style="color:var(--text-tertiary);font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:16px;font-weight:600;">Documents Overview</h4>',
            unsafe_allow_html=True,
        )
        if docs:
            df = pd.DataFrame(docs)
            vc = df["status"].value_counts().reset_index()
            vc.columns = ["status", "count"]
            fig = px.bar(
                vc, x="status", y="count",
                color="status",
                color_discrete_map={"ready": "var(--accent)", "processing": "var(--warning)", "error": "var(--danger)"},
                text="count",
            )
            fig.update_layout(**_plotly_layout(280), showlegend=False)
            fig.update_traces(textposition="outside", textfont_color="rgba(255,255,255,0.6)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No documents to display.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(
            '<h4 style="color:var(--text-tertiary);font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:16px;font-weight:600;">Sections per Document</h4>',
            unsafe_allow_html=True,
        )
        if docs:
            df = pd.DataFrame(docs)
            df = df.dropna(subset=["section_count"])
            if not df.empty:
                sdf = df.sort_values("section_count", ascending=True)
                fig = px.bar(
                    sdf, x="section_count", y="doc_name", orientation="h",
                    color="section_count",
                    color_continuous_scale=["rgba(0,230,118,0.2)", "var(--accent)"],
                    text="section_count",
                )
                fig.update_layout(**_plotly_layout(280), showlegend=False, xaxis_title=None, yaxis_title=None)
                fig.update_traces(textposition="outside", textfont_color="rgba(255,255,255,0.6)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No section data available.")
        else:
            st.info("No documents to display.")
        st.markdown("</div>", unsafe_allow_html=True)

    qa = st.session_state.get("query_analytics", [])
    if qa:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(
            '<h4 style="color:var(--text-tertiary);font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:16px;font-weight:600;">Query Performance (Session)</h4>',
            unsafe_allow_html=True,
        )

        qdf = pd.DataFrame(qa)
        c1, c2 = st.columns(2)
        with c1:
            qtypes = qdf["query_type"].value_counts().reset_index()
            qtypes.columns = ["query_type", "count"]
            fig = px.pie(
                qtypes, values="count", names="query_type",
                color_discrete_sequence=["var(--accent)", "var(--blue)", "var(--purple)", "var(--warning)", "var(--danger)"],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="rgba(255,255,255,0.65)", height=280,
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(font=dict(color="rgba(255,255,255,0.65)", size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            if "execution_time_ms" in qdf.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(len(qdf))), y=qdf["execution_time_ms"],
                    mode="lines+markers",
                    line=dict(color="var(--accent)", width=2),
                    marker=dict(color="var(--accent)", size=6),
                    fill="tozeroy",
                    fillcolor="rgba(0,230,118,0.06)",
                ))
                fig.update_layout(**_plotly_layout(280), showlegend=False, xaxis_title="Query #", yaxis_title="Latency (ms)")
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
