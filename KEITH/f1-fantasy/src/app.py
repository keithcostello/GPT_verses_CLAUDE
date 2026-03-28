"""F1 Fantasy Suzuka Dashboard — Tabbed Streamlit app."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from data_fetcher import OpenF1Client, F1FantasyScorer
from prediction_model import PredictionModel
from optimizer import FantasyOptimizer
from telemetry_tab import render_telemetry_tab, render_mock_telemetry
from strategy_tab import render_strategy_tab, render_mock_strategy
from weather_tab import render_weather_tab, render_mock_weather
from monte_carlo_tab import render_monte_carlo_tab, render_mock_monte_carlo
import styles  # noqa: F401

# Page config
st.set_page_config(
    page_title="F1 Fantasy — Suzuka 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# F1 Team colors (hex) — same as before
TEAM_COLORS = {
    "Mercedes": "#A8A9AD", "Ferrari": "#DC0000", "McLaren": "#FF8700",
    "Red Bull": "#3671C6", "Haas": "#B6BABD", "Alpine": "#FF87BC",
    "Williams": "#64C4FF", "Aston Martin": "#358F75", "Racing Bulls": "#6692FF", "Kick Sauber": "#52E252",
}

def render_driver_card(driver: dict):
    """Render a single driver pick card."""
    team = driver.get('team', 'Unknown')
    color = TEAM_COLORS.get(team, "#888888")
    ppm = driver.get('projected_ppm', 0)
    points = driver.get('projected_points', 0)
    price_m = driver.get('price', 0) / 1_000_000
    html = f"""
    <div style="background:#161b22; border-left: 4px solid {color}; padding: 12px; margin: 4px 0; border-radius: 4px;">
        <div style="color:#f0f6fc; font-weight: 600; font-size: 15px;">{driver['name']}</div>
        <div style="color:#8b949e; font-size: 12px;">{team}</div>
        <div style="margin-top: 8px;">
            <span style="color:#58a6ff; font-family: 'JetBrains Mono', monospace; font-size: 14px;">${price_m:.1f}M</span>
            <span style="color:#8b949e; margin-left: 12px;">{points:.0f} pts</span>
            <span style="color:#3fb950; margin-left: 12px; font-weight: 600;">{ppm:.2f} PPM</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_constructor_card(constructor: dict):
    color = TEAM_COLORS.get(constructor['name'], "#888888")
    price_m = constructor.get('price', 0) / 1_000_000
    points = constructor.get('projected_points', 0)
    html = f"""
    <div style="background:#161b22; border-left: 4px solid {color}; padding: 12px; margin: 4px 0; border-radius: 4px;">
        <div style="color:#f0f6fc; font-weight: 600; font-size: 15px;">{constructor['name']}</div>
        <div style="margin-top: 8px;">
            <span style="color:#58a6ff; font-family: 'JetBrains Mono', monospace; font-size: 14px;">${price_m:.1f}M</span>
            <span style="color:#8b949e; margin-left: 12px;">{points:.0f} pts</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_fantasy_tab():
    """Render the Fantasy picks tab — current single-page content."""
    # Header
    st.markdown("""
    <div style="background:#0d1117; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
        <h1 style="color:#f0f6fc; margin:0; font-family:'Inter','DM Sans',sans-serif; font-weight:600;">F1 Fantasy — Suzuka 2026</h1>
        <p style="color:#8b949e; margin:4px 0 0 0;">GP Japan | March 28-29, 2026</p>
    </div>
    """, unsafe_allow_html=True)

    model = PredictionModel()
    predictions = model.predict_all_drivers()
    drivers = [{'name': p['name'], 'team': p.get('team', ''), 'price': p['price'], 'projected_points': p['projected_points']} for p in predictions]
    constructors = [
        {"name": "Mercedes", "price": 31000000, "projected_points": 40.0, "team": "Mercedes"},
        {"name": "Ferrari", "price": 28000000, "projected_points": 36.0, "team": "Ferrari"},
        {"name": "McLaren", "price": 26500000, "projected_points": 32.0, "team": "McLaren"},
        {"name": "Haas", "price": 17000000, "projected_points": 20.0, "team": "Haas"},
        {"name": "Alpine", "price": 15000000, "projected_points": 18.0, "team": "Alpine"},
        {"name": "Williams", "price": 13000000, "projected_points": 15.0, "team": "Williams"},
        {"name": "Aston Martin", "price": 14500000, "projected_points": 16.0, "team": "Aston Martin"},
        {"name": "Red Bull", "price": 24000000, "projected_points": 28.0, "team": "Red Bull"},
    ]

    col_budget, col_drivers, col_constructors = st.columns(3)
    with col_budget:
        st.metric("Budget", "$100M")
    with col_drivers:
        st.metric("Drivers", "5 / 5")
    with col_constructors:
        st.metric("Constructors", "2 / 2")

    st.divider()

    try:
        opt = FantasyOptimizer(drivers, constructors)
        result = opt.optimize()

        col_picks, col_projs = st.columns([1, 1])
        with col_picks:
            st.markdown("#### Your Picks")
            st.markdown("**Drivers**")
            for d in result['drivers']:
                render_driver_card(d)
            st.markdown("**Constructors**")
            for c in result['constructors']:
                render_constructor_card(c)
            st.markdown(f"""
            <div style="background:#1c2128; padding: 12px; border-radius: 6px; margin-top: 12px;">
                <div style="color:#8b949e; font-size: 12px;">TOTAL COST</div>
                <div style="color:#58a6ff; font-family: monospace; font-size: 20px; font-weight: bold;">${result['total_cost']/1e6:.1f}M</div>
                <div style="color:#8b949e; font-size: 12px; margin-top: 4px;">{result['budget_used_pct']}% of $100M budget used</div>
                <div style="color:#3fb950; font-size: 14px; margin-top: 4px;">Projected: {result['total_projected_points']:.0f} pts</div>
            </div>
            """, unsafe_allow_html=True)
        with col_projs:
            st.markdown("#### Projected Rankings")
            for i, driver in enumerate(predictions[:10]):
                color = TEAM_COLORS.get(driver.get('team', ''), "#888888")
                st.markdown(f"**{i+1}. {driver['name']}** ({driver.get('team', '')}) — ${driver['price']/1e6:.1f}M — **{driver['projected_ppm']:.2f} PPM**")
    except Exception as e:
        st.error(f"Optimization error: {e}")

    # Suzuka timing
    st.divider()
    st.markdown("""
| Session | Day | Time (JST) | Time (ET) |
|---------|-----|------------|-----------|
| FP1 | Fri Mar 27 | 10:30 | 21:30 Thu |
| FP2 | Fri Mar 27 | 14:00 | 01:00 Fri |
| FP3 | Sat Mar 28 | 11:30 | 22:30 Fri |
| **Qualifying** | **Sat Mar 28** | **15:00** | **02:00 Sat** |
| Race | Sun Mar 29 | 15:00 | 02:00 Sun |
""")

def main():
    # Tab layout
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Fantasy",
        "Telemetry",
        "Strategy",
        "Weather",
        "Monte Carlo"
    ])

    with tab1:
        render_fantasy_tab()
    with tab2:
        try:
            render_telemetry_tab()
        except Exception:
            render_mock_telemetry()
    with tab3:
        try:
            render_strategy_tab()
        except Exception:
            render_mock_strategy()
    with tab4:
        try:
            render_weather_tab()
        except Exception:
            render_mock_weather()
    with tab5:
        try:
            render_monte_carlo_tab()
        except Exception:
            render_mock_monte_carlo()

if __name__ == "__main__":
    main()