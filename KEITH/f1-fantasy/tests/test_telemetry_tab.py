import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telemetry_tab import OpenF1Client, TelemetryAnalyzer

class TestOpenF1Client:
    """Tests for OpenF1 API client."""

    def test_fetch_all_sessions_returns_list(self):
        """Returns a list of sessions (empty on error)."""
        client = OpenF1Client()
        result = client.fetch_all_sessions(year=2026)
        assert isinstance(result, list)

    def test_fetch_laps_returns_list(self):
        """Returns lap list for a session key."""
        client = OpenF1Client()
        result = client.fetch_laps(session_key="nonexistent")
        assert isinstance(result, list)

    def test_fetch_positions_returns_list(self):
        """Returns position list for a session key."""
        client = OpenF1Client()
        result = client.fetch_positions(session_key="nonexistent")
        assert isinstance(result, list)

class TestTelemetryAnalyzer:
    """Tests for telemetry analysis."""

    def test_identify_position_gains(self):
        """Returns drivers who gained positions during the race."""
        positions = {
            'Russell': [1, 1, 1],
            'Hamilton': [3, 2, 2],
            'Norris': [4, 5, 6],  # lost positions
        }
        a = TelemetryAnalyzer()
        gains = a.identify_position_gains(positions)
        assert 'Russell' in gains
        assert 'Hamilton' in gains
        assert 'Norris' not in gains

    def test_fastest_lap_detection(self):
        """Returns the fastest lap time and driver."""
        laps = [
            {'driver_number': 44, 'lap_time': 90000},
            {'driver_number': 63, 'lap_time': 89500},  # fastest
            {'driver_number': 16, 'lap_time': 91000},
        ]
        a = TelemetryAnalyzer()
        fastest = a.fastest_lap_detection(laps)
        assert fastest['driver'] == 63
        assert fastest['time'] == 89500

    def test_pit_stop_count_from_stints(self):
        """Returns number of pit stops per driver from stint data."""
        stints = [
            {'driver': 'Russell', 'stint': 1, 'lap_end': 25},
            {'driver': 'Russell', 'stint': 2, 'lap_end': 50},
        ]
        a = TelemetryAnalyzer()
        count = a.pit_stop_count_from_stints('Russell', stints)
        assert count == 1  # 2 stints = 1 pit stop