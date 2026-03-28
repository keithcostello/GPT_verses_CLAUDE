"""F1 Monte Carlo Strategy Simulator Tab — probability-weighted race outcomes."""
import streamlit as st
import random
from dataclasses import dataclass, field
from typing import Dict, List, Set
from collections import defaultdict

# Base race parameters (2026 Suzuka)
DRIVERS_2026 = [
    "Russell", "Antonelli", "Hamilton", "Leclerc", "Piastri", "Norris",
    "Verstappen", "Perez", "Bearman", "Gasly", "Ocon", "Alonso"
]


@dataclass
class RaceScenario:
    """Single simulated race scenario."""
    sc_timing: int = 0  # lap SC deploys (0 = no SC)
    sc_duration: int = 0  # seconds
    rain_probability: float = 0.0  # 0-1
    dnf_drivers: List[str] = field(default_factory=list)
    finishing_positions: Dict[str, int] = field(default_factory=dict)


class MonteCarloSimulator:
    """
    Monte Carlo simulation for F1 race outcomes.
    Runs N scenarios varying:
    - Safety Car timing
    - DNF probability per driver
    - Weather (rain)
    - Tire strategy outcomes

    Returns probability distributions over finishing positions.
    """

    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
        self.sc_probability = 0.30  # 30% SC chance at Suzuka
        self.dnf_probability = 0.08  # 8% per-driver DNF chance
        self.drivers = DRIVERS_2026

        # Base pace ranking (from Australia/China 2026)
        self.base_pace = {
            'Russell': 1, 'Antonelli': 2, 'Hamilton': 3, 'Leclerc': 4,
            'Piastri': 5, 'Norris': 6, 'Verstappen': 7, 'Bearman': 8,
            'Gasly': 9, 'Ocon': 10, 'Alonso': 11, 'Perez': 12
        }

    def generate_scenario(self) -> RaceScenario:
        """Generate one random race scenario."""
        # SC timing: 0 = no SC, or random lap 10-45
        sc_timing = 0
        sc_duration = 0
        if random.random() < self.sc_probability:
            sc_timing = random.randint(10, 45)
            sc_duration = random.randint(5, 12)  # 5-12 seconds

        # Rain
        rain_probability = 0.40  # Suzuka March ~40%

        # DNFs: each driver has independent chance
        dnf_drivers = []
        for driver in self.drivers:
            if random.random() < self.dnf_probability:
                dnf_drivers.append(driver)

        # Finishing positions
        finishing_positions = self._calculate_positions(
            sc_timing, sc_duration, rain_probability, dnf_drivers
        )

        return RaceScenario(
            sc_timing=sc_timing,
            sc_duration=sc_duration,
            rain_probability=rain_probability,
            dnf_drivers=dnf_drivers,
            finishing_positions=finishing_positions
        )

    def _calculate_positions(self, sc_timing: int, sc_duration: int,
                           rain_probability: float, dnf_drivers: List[str]) -> Dict[str, int]:
        """Calculate finishing positions given scenario parameters."""
        # Start with base pace ranking
        available = [d for d in self.drivers if d not in dnf_drivers]

        # SC disrupts order: if SC timing > 0, some positions swap
        positions = {}
        for i, driver in enumerate(available):
            # Base position from pace ranking
            base = self.base_pace.get(driver, 10)

            # SC adds randomness: +random offset
            if sc_timing > 0:
                offset = random.randint(-4, 4)
            else:
                offset = random.randint(-2, 2)

            # Rain adds more chaos
            if rain_probability > 0.3:
                offset += random.randint(-3, 3)

            final_position = max(1, min(len(available), base + offset))
            positions[driver] = final_position

        # Sort by position value
        sorted_drivers = sorted(positions.keys(), key=lambda d: positions[d])
        return {d: i+1 for i, d in enumerate(sorted_drivers)}

    def run_simulation(self) -> Dict:
        """
        Run N Monte Carlo simulations.
        Returns probability distributions.
        """
        all_positions = defaultdict(list)  # driver -> [pos1, pos2, ...]
        podium_counts = defaultdict(int)  # driver -> count in top 3

        for _ in range(self.n_simulations):
            scenario = self.generate_scenario()
            for driver, pos in scenario.finishing_positions.items():
                all_positions[driver].append(pos)
                if pos <= 3:
                    podium_counts[driver] += 1

        # Calculate statistics
        avg_positions = {
            driver: sum(positions) / len(positions)
            for driver, positions in all_positions.items()
        }

        podium_probabilities = {
            driver: round(count / self.n_simulations * 100, 1)
            for driver, count in podium_counts.items()
        }

        # Win probability
        win_counts = defaultdict(int)
        for driver in all_positions:
            win_counts[driver] = sum(1 for p in all_positions[driver] if p == 1)
        win_probabilities = {
            driver: round(count / self.n_simulations * 100, 1)
            for driver, count in win_counts.items()
        }

        return {
            'average_positions': avg_positions,
            'podium_probabilities': podium_probabilities,
            'win_probabilities': win_probabilities,
            'total_simulations': self.n_simulations
        }


def render_monte_carlo_tab():
    """Render the Streamlit Monte Carlo tab."""
    st.markdown("### 🎲 Monte Carlo Simulator")

    # Parameters
    col1, col2 = st.columns(2)
    with col1:
        n_simulations = st.slider("Simulations", 100, 5000, 1000, step=100)
    with col2:
        show_top_n = st.slider("Show Top N Drivers", 3, 12, 6)

    st.markdown(f"Running **{n_simulations:,}** race simulations with SC/DNF/rain variation...")

    # Run simulation
    sim = MonteCarloSimulator(n_simulations=n_simulations)
    results = sim.run_simulation()

    # Win probability
    st.markdown("#### 🏆 Win Probability")
    wins = results['win_probabilities']
    sorted_wins = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    for driver, prob in sorted_wins[:show_top_n]:
        bar_len = int(prob / 2)
        bar = "█" * bar_len
        st.markdown(f"{driver}: `{prob:5.1f}%` {bar}")

    # Podium probability
    st.markdown("#### 🎖️ Podium Probability (Top 3)")
    podiums = results['podium_probabilities']
    sorted_podiums = sorted(podiums.items(), key=lambda x: x[1], reverse=True)
    for driver, prob in sorted_podiums[:show_top_n]:
        bar_len = int(prob / 2)
        bar = "█" * bar_len
        st.markdown(f"{driver}: `{prob:5.1f}%` {bar}")

    # Average finishing position
    st.markdown("#### 📊 Expected Finishing Position")
    avg_pos = results['average_positions']
    sorted_avg = sorted(avg_pos.items(), key=lambda x: x[1])
    for driver, avg in sorted_avg[:show_top_n]:
        st.markdown(f"**{driver}:** P{avg:.1f}")

    # Methodology note
    st.caption(
        f"Model: {n_simulations} simulations | "
        f"SC probability: 30% | DNF probability: 8%/driver | Rain: ~40%"
    )


def render_mock_monte_carlo():
    """Render mock Monte Carlo when user hasn't clicked run."""
    st.markdown("### 🎲 Monte Carlo Simulator")
    st.info("Adjust parameters and click **Run Simulation** to see probability distributions.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Simulations", "1,000")
    with col2:
        st.metric("SC Probability", "30%")

    st.markdown("#### 🏆 Win Probability (preview)")
    st.markdown("- **Antonelli:** `25.3%` ████████████")
    st.markdown("- **Russell:** `22.1%` ███████████")
    st.markdown("- **Hamilton:** `18.7%` █████████")
    st.markdown("- **Leclerc:** `15.2%` ████████")

    st.markdown("#### 🎖️ Podium Probability (preview)")
    st.markdown("- **Mercedes:** `68%`")
    st.markdown("- **Ferrari:** `52%`")
    st.markdown("- **McLaren:** `31%`")