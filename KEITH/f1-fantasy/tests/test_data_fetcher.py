import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_fetcher import OpenF1Client, F1FantasyScorer

class TestOpenF1Client:
    """Tests for OpenF1 API client"""

    def test_fetch_sessions_returns_list(self):
        """OpenF1 returns a list of session dicts"""
        with patch('data_fetcher.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {"session_key": "9222", "session_name": "Qualifying", "country_code": "JP", "year": 2026}
            ]
            client = OpenF1Client()
            result = client.fetch_sessions(country_code="JP", year=2026)
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["country_code"] == "JP"

    def test_fetch_drivers_returns_driver_data(self):
        """Driver fetch returns name, team, number"""
        with patch('data_fetcher.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {"driver_number": 44, "full_name": "Lewis Hamilton", "team_name": "Mercedes", "session_key": "9222"}
            ]
            client = OpenF1Client()
            result = client.fetch_drivers(session_key="9222")
            assert result[0]["full_name"] == "Lewis Hamilton"
            assert result[0]["team_name"] == "Mercedes"

    def test_fetch_laps_returns_lap_times(self):
        with patch('data_fetcher.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {"driver_number": 44, "lap_number": 1, "lap_time": 90000, "position": 1}
            ]
            client = OpenF1Client()
            result = client.fetch_laps(session_key="9222")
            assert result[0]["lap_number"] == 1

    def test_api_unavailable_returns_empty(self):
        """When API fails, client returns empty list gracefully"""
        with patch('data_fetcher.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            client = OpenF1Client()
            result = client.fetch_sessions(country_code="JP", year=2026)
            assert result == []

class TestF1FantasyScorer:
    """Tests for F1 Fantasy scoring calculator"""

    def test_calculate_ppm(self):
        """Points per million = fantasy_points / price"""
        scorer = F1FantasyScorer()
        result = scorer.calculate_ppm(points=25, price=20000000)
        assert result == 1.25  # 25/20M = 1.25 PPM

    def test_calculate_total_cost_valid(self):
        """Total of 5 drivers + 2 constructors within $100M"""
        picks = {
            'drivers': [
                {'name': 'Russell', 'price': 18400000},
                {'name': 'Antonelli', 'price': 16200000},
            ],
            'constructors': [
                {'name': 'Mercedes', 'price': 31000000},
            ]
        }
        scorer = F1FantasyScorer()
        total = scorer.calculate_total_cost(picks)
        assert total == 65600000