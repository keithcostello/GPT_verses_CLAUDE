import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from optimizer import FantasyOptimizer

# Test data - prices adjusted so minimum feasible cost <= $100M
# Minimum 5 drivers: Bearman(5M) + Piastri(10M) + Leclerc(11M) + Norris(12M) + Hamilton(12M) = 50M
# Minimum 2 constructors: Haas(14M) + McLaren(18M) = 32M -> Total minimum = 82M (fits in 100M)
SAMPLE_DRIVERS = [
    {"name": "Russell", "team": "Mercedes", "price": 16000000, "projected_points": 35.0},
    {"name": "Antonelli", "team": "Mercedes", "price": 14000000, "projected_points": 32.0},
    {"name": "Hamilton", "team": "Ferrari", "price": 12000000, "projected_points": 28.0},
    {"name": "Leclerc", "team": "Ferrari", "price": 11000000, "projected_points": 26.0},
    {"name": "Piastri", "team": "McLaren", "price": 10000000, "projected_points": 24.0},
    {"name": "Norris", "team": "McLaren", "price": 12000000, "projected_points": 22.0},
    {"name": "Verstappen", "team": "Red Bull", "price": 15000000, "projected_points": 30.0},
    {"name": "Bearman", "team": "Haas", "price": 5000000, "projected_points": 18.0},
]

SAMPLE_CONSTRUCTORS = [
    {"name": "Mercedes", "price": 31000000, "projected_points": 40.0},
    {"name": "Ferrari", "price": 28000000, "projected_points": 36.0},
    {"name": "McLaren", "price": 26500000, "projected_points": 32.0},
    {"name": "Haas", "price": 17000000, "projected_points": 20.0},
]


class TestFantasyOptimizer:
    """Tests for OR-tools budget optimizer."""

    def test_exactly_5_drivers_selected(self):
        """Optimizer must select exactly 5 drivers."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        assert len(result['drivers']) == 5

    def test_exactly_2_constructors_selected(self):
        """Optimizer must select exactly 2 constructors."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        assert len(result['constructors']) == 2

    def test_budget_constraint_respected(self):
        """Total cost must not exceed $100M."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        assert result['total_cost'] <= 100_000_000

    def test_no_duplicate_teams_in_constructors(self):
        """Can select same team constructor only once."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        constructor_teams = [c['name'] for c in result['constructors']]
        assert len(constructor_teams) == len(set(constructor_teams))  # all unique

    def test_result_contains_projections(self):
        """Result includes total projected points and PPM."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        assert 'total_projected_points' in result
        assert 'total_cost' in result
        assert 'budget_used_pct' in result
        assert result['total_projected_points'] > 0

    def test_no_driver_duplicates(self):
        """Cannot select same driver twice."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        driver_names = [d['name'] for d in result['drivers']]
        assert len(driver_names) == len(set(driver_names))

    def test_optimize_returns_dict(self):
        """optimize() returns a dict with required keys."""
        opt = FantasyOptimizer(SAMPLE_DRIVERS, SAMPLE_CONSTRUCTORS)
        result = opt.optimize()
        assert isinstance(result, dict)
        assert 'drivers' in result
        assert 'constructors' in result
        assert 'total_cost' in result
        assert 'total_projected_points' in result