import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'KEITH', 'f1-fantasy', 'src'))

from strategy_tab import StrategyModel, SuzukaStrategy

class TestSuzukaStrategy:
    """Tests for Suzuka-specific strategy factors."""

    def test_degradation_factor_high(self):
        """Suzuka has high degradation due to 130R and heavy braking."""
        s = SuzukaStrategy()
        assert s.degradation_level == "high"
        assert s.typical_stops in [1, 2]

    def test_compound_range(self):
        """2026 Suzuka: C1-C4 likely (C5 softest, C1 hardest)."""
        s = SuzukaStrategy()
        assert 'C1' in s.expected_compounds
        assert 'C2' in s.expected_compounds

    def test_overtaking_zones(self):
        """Suzuka: Turn 1 (heavy braking, good for overtake) + main straight DRS."""
        s = SuzukaStrategy()
        assert 1 in s.overtaking_zones
        assert len(s.overtaking_zones) >= 1


class TestStrategyModel:
    """Tests for strategy prediction model."""

    def test_one_stop_vs_two_stop_threshold(self):
        """Stint length > 25 laps → 2-stop preferred at Suzuka."""
        model = StrategyModel()
        assert model.prefer_two_stop(stint_length=30) == True
        assert model.prefer_two_stop(stint_length=15) == False

    def test_pit_window_calculation(self):
        """Optimal pit window: (total_laps / stops) * stint_number."""
        model = StrategyModel()
        # 53 lap race, 2 stops: first pit at laps 17-22
        window = model.calculate_pit_window(total_laps=53, stops=2, stint=1)
        assert 15 <= window <= 25

    def test_compound_recommendation(self):
        """First stint at Suzuka: medium or hard preferred."""
        model = StrategyModel()
        compound = model.recommend_compound(stint=1, tire_age=0, track_temp=30)
        assert compound in ['medium', 'hard', 'C2', 'C3']

    def test_strategy_score(self):
        """Compare two strategy options."""
        model = StrategyModel()
        s1 = {'stops': 1, 'avg_compound': 'hard', 'tire_life': 53}
        s2 = {'stops': 2, 'avg_compound': 'medium', 'tire_life': 25}
        score1 = model.strategy_score(s1)
        score2 = model.strategy_score(s2)
        assert isinstance(score1, (int, float))
        assert isinstance(score2, (int, float))