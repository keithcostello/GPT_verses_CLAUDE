import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'KEITH', 'f1-fantasy', 'src'))

from weather_tab import WeatherAnalyzer, RainPredictor

class TestWeatherAnalyzer:
    """Tests for weather impact analysis."""

    def test_wet_race_threshold(self):
        """Rainfall > 0.5mm = wet race conditions."""
        a = WeatherAnalyzer()
        assert a.is_wet_race(rainfall=0.3) == False
        assert a.is_wet_race(rainfall=0.8) == True

    def test_grip_level_dry(self):
        """Dry track = 100% grip."""
        a = WeatherAnalyzer()
        grip = a.track_grip_level(rainfall=0, track_temp=35)
        assert grip == 1.0

    def test_grip_level_wet(self):
        """Heavy rain = 60% grip."""
        a = WeatherAnalyzer()
        grip = a.track_grip_level(rainfall=2.5, track_temp=20)
        assert grip < 1.0

    def test_rain_probability_output(self):
        """Returns 0-100 probability."""
        rp = RainPredictor()
        # March Suzuka: moderate rain chance (30-40%)
        prob = rp.suzuka_rain_probability(month=3)
        assert 0 <= prob <= 100
        assert isinstance(prob, float)

class TestRainPredictor:
    """Tests for rain prediction at Suzuka."""

    def test_suzuka_march_rainy(self):
        """March is wet season in Japan."""
        rp = RainPredictor()
        prob = rp.suzuka_rain_probability(month=3)
        assert prob > 20  # wet season

    def test_wind_impact(self):
        """High wind (>30 kph) affects aero balance at Suzuka."""
        rp = RainPredictor()
        impact = rp.wind_impact(wind_speed=35)
        assert impact < 0  # wind reduces grip, negative impact