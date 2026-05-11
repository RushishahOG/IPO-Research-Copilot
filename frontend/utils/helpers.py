import streamlit as st
from datetime import datetime


def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return ts


def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def skeleton_loader(lines: int = 3):
    for _ in range(lines):
        st.markdown('<div class="skeleton-line"></div>', unsafe_allow_html=True)
