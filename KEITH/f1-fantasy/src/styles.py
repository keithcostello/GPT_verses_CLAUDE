"""F1 Fantasy professional dark theme styles for Streamlit."""
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
    """Apply professional dark theme to the F1 Fantasy dashboard."""
    st.markdown("""
    <style>
    /* Page background */
    .stApp {
        background-color: #0f1419;
        color: #e6edf3;
    }

    /* Headers — clean sans-serif, no decoration */
    h1, h2, h3 {
        font-family: 'Inter', 'DM Sans', sans-serif;
        color: #e6edf3;
        font-weight: 600;
    }

    /* Metric values — monospace for numbers */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'Consolas', monospace;
        font-size: 1.4rem;
        color: #58a6ff;
    }

    /* Metric labels */
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Driver cards — professional dark card style */
    .driver-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 3px solid [TEAM_COLOR];
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 4px;
    }
    .driver-name {
        font-size: 14px;
        font-weight: 600;
        color: #e6edf3;
    }
    .driver-team {
        font-size: 12px;
        color: #8b949e;
    }
    .driver-stat {
        font-family: monospace;
        font-size: 13px;
        color: #58a6ff;
    }
    .driver-ppm {
        font-family: monospace;
        font-size: 13px;
        color: #3fb950;
    }

    /* Section headers — no emoji, text only */
    .section-header {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8b949e;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }

    /* Tables */
    .dataframe {
        background: #161b22;
        border: 1px solid #30363d;
    }

    /* Dividers */
    hr {
        border-color: #21262d;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0f1419;
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Load Inter and JetBrains Mono fonts
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)