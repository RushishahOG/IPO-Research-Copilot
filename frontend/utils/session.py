import streamlit as st


def init_session_state():
    defaults = {
        "page": "home",
        "documents": [],
        "selected_doc": None,
        "chat_history": [],
        "upload_status": None,
        "health_status": None,
        "query_analytics": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
