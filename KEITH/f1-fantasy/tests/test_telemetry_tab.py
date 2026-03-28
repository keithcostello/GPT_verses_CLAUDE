import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telemetry_tab import SuzukaTelemetry, TelemetryAnalyzer

class TestSuzukaTelemetry:
    """Tests for Suzuka telemetry fetcher."""

    def test_suzuka_session_key_known(self):
        """Suzuka has a known circuit ID in OpenF1."""
        t = SuzukaTelemetry()
        assert t.circuit_name == "Suzuka International Racing Course"

    def test_sector_boundaries_defined(self):
        """Suzuka has 3 sectors matching F1 standard."""
        t = SuzukaTelemetry()
        assert len(t.sector_boundaries) == 3
        # Turn 1 (heavy braking), 130R (high speed), final sector (technical)

    def test_get_driver_sector_times(self):
        """Returns sector 1, 2, 3 times for a driver."""
        t = SuzukaTelemetry()
        times = t.get_driver_sector_times(driver_number=44)
        assert 'sector_1' in times or 'sector_2' in times or 'sector_3' in times

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
            {'driver': 'Russell', 'time': 90000},
            {'driver': 'Hamilton', 'time': 89500},  # fastest
            {'driver': 'Leclerc', 'time': 91000},
        ]
        a = TelemetryAnalyzer()
        fastest = a.fastest_lap_detection(laps)
        assert fastest['driver'] == 'Hamilton'
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