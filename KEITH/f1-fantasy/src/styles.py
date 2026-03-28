"""F1 Fantasy dark theme styles for Streamlit."""
import streamlit as st

TEAM_COLORS = {
    "Mercedes": "#A8A9AD",
    "Ferrari": "#DC0000",
    "McLaren": "#FF8700",
    "Red Bull": "#3671C6",
    "Haas": "#B6BABD",
    "Alpine": "#FF87BC",
    "Williams": "#64C4FF",
    "Aston Martin": "#358F75",
    "Racing Bulls": "#6692FF",
    "Kick Sauber": "#52E252",
}


def apply_f1_dark_theme():
    """Apply F1-native dark theme to the Streamlit app."""
    st.markdown("""
    <style>
    /* Page background */
    .stApp {
        background-color: #0d1117;
        color: #f0f6fc;
    }

    /* Headers */
    h1, h2, h3 {
        color: #f0f6fc !important;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Dividers */
    hr {
        border-color: #21262d !important;
    }

    /* Tables */
    .dataframe {
        background-color: #161b22 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0d1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 4px;
    }

    /* Driver cards are styled inline in app.py */
    </style>
    """, unsafe_allow_html=True)

    # Import JetBrains Mono from Google Fonts
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
    * {
        font-family: 'DM Sans', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)