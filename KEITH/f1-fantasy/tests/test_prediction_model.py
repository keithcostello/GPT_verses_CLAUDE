import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from prediction_model import PredictionModel, SuzukaCircuit

class TestPredictionModel:
    """Tests for F1 race prediction model."""

    def test_weighted_composite_score(self):
        """50% Australia + 30% China + 20% Suzuka factor."""
        model = PredictionModel()
        # Russell: P1 Australia (25pts), P2 China (18pts)
        australia_pts = 25
        china_pts = 18
        suzuka_factor = 0.9  # Russell strong at Suzuka historically

        score = model.weighted_score(australia_pts, china_pts, suzuka_factor)
        expected = 0.50 * 25 + 0.30 * 18 + 0.20 * (100 * 0.9)  # 12.5 + 5.4 + 18 = 35.9
        assert abs(score - expected) < 0.1

    def test_project_points_returns_dict_with_keys(self):
        """project_points returns a dict with name, price, ppm, and points."""
        model = PredictionModel()
        result = model.project_points(
            driver_name="Russell",
            australia_position=1,
            china_position=2,
            suzuka_factor=0.9,
            price=18400000
        )
        assert isinstance(result, dict)
        assert result['name'] == 'Russell'
        assert result['price'] == 18400000
        assert 'projected_ppm' in result
        assert 'projected_points' in result
        assert result['projected_ppm'] > 0

    def test_suzuka_factor_for_specific_drivers(self):
        """Drivers with good Suzuka history get higher suzuka factors."""
        model = SuzukaCircuit()
        # Hamilton has multiple Suzuka wins
        hamilton = model.get_suzuka_factor("Hamilton")
        # Bearman hasn't raced F1 at Suzuka
        bearman = model.get_suzuka_factor("Bearman")
        assert hamilton > bearman

    def test_model_returns_ranked_list(self):
        """predict returns list sorted by projected PPM descending."""
        model = PredictionModel()
        results = model.predict_all_drivers()
        assert isinstance(results, list)
        assert len(results) > 0
        # Check sorted by PPM descending
        ppm_values = [r['projected_ppm'] for r in results]
        assert ppm_values == sorted(ppm_values, reverse=True)
        # PPM ranking is valid regardless of which driver is top
        # PPM = projected_points / (price / 1M) — cheap drivers with points rank high
        assert results[0]['projected_ppm'] >= results[1]['projected_ppm']
        # All PPM values should be positive
        assert all(r['projected_ppm'] > 0 for r in results)

class TestSuzukaCircuit:
    """Tests for Suzuka circuit-specific adjustments."""

    def test_pit_loss_time(self):
        """Suzuka pit loss ~25 seconds."""
        circuit = SuzukaCircuit()
        assert 20 <= circuit.pit_loss_seconds <= 30

    def test_overtaking_zones(self):
        """Suzuka has overtaking at T1 and the main straight."""
        circuit = SuzukaCircuit()
        zones = circuit.overtaking_zones
        assert 1 in zones  # T1
        assert len(zones) >= 2