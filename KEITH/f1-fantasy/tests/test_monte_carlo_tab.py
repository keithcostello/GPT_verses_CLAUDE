import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'KEITH', 'f1-fantasy', 'src'))

import random
random.seed(42)  # reproducibility

from monte_carlo_tab import MonteCarloSimulator, RaceScenario

class TestMonteCarloSimulator:
    """Tests for Monte Carlo strategy simulator."""

    def test_simulator_initialization(self):
        """Simulator initialized with drivers and race parameters."""
        sim = MonteCarloSimulator(n_simulations=100)
        assert sim.n_simulations == 100
        assert sim.sc_probability == 0.30  # 30% SC chance
        assert sim.dnf_probability == 0.08  # 8% DNF chance

    def test_single_scenario_generation(self):
        """Generates a valid RaceScenario."""
        sim = MonteCarloSimulator(n_simulations=10)
        scenario = sim.generate_scenario()
        assert isinstance(scenario, RaceScenario)
        assert 0 <= scenario.sc_timing <= 53  # within race laps
        assert scenario.finishing_positions is not None

    def test_scenario_variation(self):
        """Two scenarios should differ (SC timing, weather, etc.)."""
        sim = MonteCarloSimulator(n_simulations=50)
        s1 = sim.generate_scenario()
        s2 = sim.generate_scenario()
        # At least SC timing or finishing positions should differ
        assert s1.sc_timing != s2.sc_timing or s1.finishing_positions != s2.finishing_positions

    def test_podium_probabilities(self):
        """After 100 simulations, drivers should have probability 0-100%."""
        sim = MonteCarloSimulator(n_simulations=100)
        results = sim.run_simulation()
        podiums = results['podium_probabilities']
        assert isinstance(podiums, dict)
        for driver, prob in podiums.items():
            assert 0 <= prob <= 100


class TestRaceScenario:
    """Tests for individual race scenario."""

    def test_scenario_fields(self):
        """Scenario has all required fields."""
        s = RaceScenario(
            sc_timing=20,
            sc_duration=8,
            rain_probability=0.3,
            dnf_drivers=['Verstappen'],
            finishing_positions={'Hamilton': 1, 'Russell': 2, 'Leclerc': 3}
        )
        assert s.sc_timing == 20
        assert 'Hamilton' in s.finishing_positions