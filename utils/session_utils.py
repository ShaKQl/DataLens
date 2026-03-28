import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

_DEFAULTS = {
    "df": None,
    "uploaded_file_name": None,
    "current_page": "A",
    "reset_counter": 0,
    "theme": "dark",
    "transformation_log": [],
    "df_original": None,
}


def initialize_session_state() -> None:
    """Set default session state values if not already present."""
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_current_df():
    """Return the current DataFrame from session state, or None."""
    return st.session_state.get('df')


def set_df(df, store_original=False):
    """Set the current DataFrame in session state."""
    if store_original and st.session_state.get('df_original') is None:
        st.session_state['df_original'] = df.copy()
    st.session_state['df'] = df


def reset_session():
    """Clear the DataFrame and increment reset_counter."""
    st.session_state['df'] = None
    st.session_state['df_original'] = None
    st.session_state['uploaded_file_name'] = None
    st.session_state['transformation_log'] = []
    st.session_state['reset_counter'] = st.session_state.get('reset_counter', 0) + 1


def get_theme():
    """Get current theme (dark or light)."""
    return st.session_state.get('theme', 'dark')


def toggle_theme():
    """Toggle between dark and light theme."""
    current = st.session_state.get('theme', 'dark')
    st.session_state['theme'] = 'light' if current == 'dark' else 'dark'


def log_transformation(operation, params, affected_columns):
    """Log a transformation step."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "parameters": params,
        "affected_columns": affected_columns,
    }
    st.session_state['transformation_log'].append(log_entry)


def get_transformation_log():
    """Get the transformation log."""
    return st.session_state.get('transformation_log', [])


def undo_last_transformation():
    """Undo the last transformation."""
    log = get_transformation_log()
    if not log:
        return False
    st.session_state['transformation_log'] = log[:-1]
    original = st.session_state.get('df_original')
    if original is not None:
        st.session_state['df'] = original.copy()
        return True
    return False


def get_original_df():
    """Get the original DataFrame before any transformations."""
    return st.session_state.get('df_original')