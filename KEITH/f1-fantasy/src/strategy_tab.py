"""F1 Strategy Tab — tire degradation, pit windows, compound recommendations."""
import streamlit as st
from typing import Dict, List, Tuple, Optional

# 2026 Pirelli compounds
COMPOUNDS_2026 = {
    'C1': {'color': '#FFFFFF', 'name': 'Hard', 'durability': 5},
    'C2': {'color': '#FFFFFF', 'name': 'Medium', 'durability': 4},
    'C3': {'color': '#FFCC00', 'name': 'Medium-Soft', 'durability': 3},
    'C4': {'color': '#FF3333', 'name': 'Soft', 'durability': 2},
    'C5': {'color': '#FF3333', 'name': 'Ultra Soft', 'durability': 1},
}


class SuzukaStrategy:
    """Suzuka-specific strategy constants."""

    def __init__(self):
        self.circuit = "Suzuka International Racing Course"
        self.total_laps = 53
        self.degradation_level = "high"  # 130R high-speed corner + heavy braking
        self.typical_stops = 2  # historically
        self.expected_compounds = ['C1', 'C2', 'C3', 'C4']  # 2026 selection
        self.overtaking_zones = [1, 2]  # Turn 1 (250R hairpin), main straight DRS
        self.pit_loss_seconds = 25
        self.safety_car_probability = 0.30  # 30% historical SC chance


class StrategyModel:
    """
    Model for F1 race strategy decisions.
    Analyzes: 1-stop vs 2-stop, pit windows, compound recommendations.
    """

    def __init__(self):
        self.suzuka = SuzukaStrategy()
        self.sc_deployment_laps = [15, 30, 45]  # approximate SC deployment windows

    def prefer_two_stop(self, stint_length: int) -> bool:
        """At Suzuka, stint > 25 laps suggests 2-stop due to degradation."""
        return stint_length > 25

    def calculate_pit_window(self, total_laps: int, stops: int, stint: int) -> int:
        """
        Calculate optimal pit lap for a given stint.
        Example: 53 lap race, 2 stops, stint 1 → pit around lap 17-22.
        """
        if stops == 0:
            return total_laps
        stint_length = total_laps / (stops + 1)
        pit_lap = int(stint_length * stint)
        return max(1, pit_lap)

    def recommend_compound(self, stint: int, tire_age: int, track_temp: float = 30) -> str:
        """
        Recommend tire compound based on stint and conditions.
        Suzuka: medium/hard for first stint (durability), soft for late race.
        """
        if stint == 1:
            if track_temp > 40:
                return 'C1'  # Hard for hot tracks
            return 'C2'  # Medium for normal
        elif stint == 2:
            return 'C3'  # Medium-soft
        else:
            return 'C4'  # Soft for final stint / undercut

    def strategy_score(self, strategy: Dict) -> float:
        """
        Score a race strategy from 0-100.
        Factors: number of stops (fewer=better), compound hardness (medium=better than soft)
        """
        stop_score = max(0, 20 - strategy['stops'] * 8)  # 0 stops = 20, 2 stops = 4
        compound = strategy.get('avg_compound', 'medium')
        compound_map = {'hard': 30, 'C1': 30, 'C2': 35, 'medium': 40, 'C3': 40, 'C4': 50, 'soft': 50, 'C5': 55}
        compound_score = compound_map.get(compound, 35)
        tire_life_score = min(30, strategy.get('tire_life', 25) * 0.6)
        return round(stop_score + compound_score + tire_life_score, 1)

    def compare_strategies(self, strategies: List[Dict]) -> List[Dict]:
        """Sort strategies by score descending."""
        for s in strategies:
            s['score'] = self.strategy_score(s)
        return sorted(strategies, key=lambda x: x['score'], reverse=True)

    def monte_carlo_outcome(self, base_strategy: Dict,
                           sc_risk: float = 0.30) -> Dict:
        """
        Estimate outcome distribution given SC probability.
        Returns: {pct_good, pct_neutral, pct_bad}
        """
        # Simplified: if SC hits during pit window, strategy disrupted
        pit_window = base_strategy.get('pit_window', 20)
        if sc_risk > 0.25:
            return {'outcome': 'DISRUPTED', 'delta': -15, 'probability': sc_risk}
        return {'outcome': 'NORMAL', 'delta': 0, 'probability': 1 - sc_risk}


def render_strategy_tab():
    """Render the Streamlit strategy tab."""
    st.markdown("### 🛞 Race Strategy")

    model = StrategyModel()
    suzuka = model.suzuka

    # Strategy parameters
    col1, col2 = st.columns(2)
    with col1:
        race_laps = st.slider("Race Length (laps)", 50, 60, 53)
    with col2:
        num_stops = st.radio("Strategy", ["1-Stop", "2-Stop", "Compare Both"])

    # Pit window calculator
    st.markdown("#### 🎯 Optimal Pit Windows")
    stops = 1 if num_stops == "1-Stop" else 2
    for stint_n in range(1, stops + 2):
        pit_lap = model.calculate_pit_window(race_laps, stops, stint_n)
        st.markdown(f"**Stint {stint_n}:** Pit at lap `{pit_lap}` (±2)")

    # Compound recommendation
    st.markdown("#### 🏭 Compound Recommendations")
    compounds = st.columns(3)
    for i, stint_n in enumerate([1, 2, 3][:stops + 1]):
        with compounds[i]:
            compound = model.recommend_compound(stint_n, tire_age=0)
            color = COMPOUNDS_2026.get(compound, {}).get('color', '#888')
            st.markdown(f"**Stint {stint_n}:** :{color[{0:6} if color=='#FFFFFF' else 0:6]}**[{compound}]**")

    # Strategy comparison
    st.markdown("#### ⚖️ Strategy Comparison")
    s1 = {'stops': stops, 'avg_compound': 'hard' if stops == 1 else 'medium', 'tire_life': race_laps}
    s2 = {'stops': 2, 'avg_compound': 'medium', 'tire_life': race_laps // 2}

    strategies = model.compare_strategies([s1, s2])
    for strat in strategies:
        st.markdown(f"- **{num_stops}** ({stops} stops, {s1['avg_compound']}): Score `{strat['score']}`")

    # SC risk
    st.markdown(f"#### ⚠️ Safety Car Risk: `{suzuka.safety_car_probability * 100:.0f}%`")
    st.markdown(f"SC deployment historically likely at laps {model.sc_deployment_laps}. "
                f"If SC overlaps with pit window, 2-stop gains track position.")


def render_mock_strategy():
    """Render mock strategy when no live data available."""
    st.markdown("### 🛞 Race Strategy")
    st.info("Strategy recommendations update as race data arrives.")

    st.markdown("#### 🎯 Optimal Pit Windows")
    st.markdown("- **Stint 1:** Pit at lap `18` (±2)")
    st.markdown("- **Stint 2:** Pit at lap `35` (±2)")

    st.markdown("#### 🏭 Compound Recommendations")
    st.markdown("- **Stint 1:** Hard (C1) — best for Suzuka degradation")
    st.markdown("- **Stint 2:** Medium (C2) — balanced")
    st.markdown("- **Stint 3:** Soft (C4) — for final overtake")

    st.markdown("#### ⚖️ Strategy Comparison")
    st.markdown("- **1-Stop:** Hard/Hard: Score `67.2`")
    st.markdown("- **2-Stop:** Hard/Medium/Soft: Score `71.5` ← preferred")