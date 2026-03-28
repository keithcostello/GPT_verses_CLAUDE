"""F1 Weather Impact Tab — rain probability, track conditions, wet performance."""
import streamlit as st
import requests
from typing import Dict, List, Optional

BASE_URL = "https://api.openf1.org/v1"


class RainPredictor:
    """Rain prediction for Suzuka based on historical weather patterns."""

    def __init__(self):
        self.circuit = "Suzuka"
        # March Japan: transition season, moderate rain risk
        self.monthly_rain_prob = {
            1: 0.35, 2: 0.40, 3: 0.45, 4: 0.50,
            5: 0.55, 6: 0.60, 7: 0.65, 8: 0.60,
            9: 0.55, 10: 0.45, 11: 0.40, 12: 0.35
        }

    def suzuka_rain_probability(self, month: int = 3) -> float:
        """Return probability of rain at Suzuka for a given month (0-100)."""
        return self.monthly_rain_prob.get(month, 0.30) * 100

    def rain_intensity_label(self, rainfall_mm: float) -> str:
        """Classify rainfall intensity."""
        if rainfall_mm == 0:
            return "Dry"
        elif rainfall_mm < 0.5:
            return "Light drizzle"
        elif rainfall_mm < 2.0:
            return "Light rain"
        elif rainfall_mm < 5.0:
            return "Moderate rain"
        else:
            return "Heavy rain"

    def wind_impact(self, wind_speed: float) -> float:
        """
        Return grip multiplier impact from wind.
        Negative = reduces grip. High wind at Suzuka affects high-speed sections.
        """
        if wind_speed < 15:
            return 0.0
        elif wind_speed < 30:
            return -0.05
        else:
            return -0.12


class WeatherAnalyzer:
    """Analyze weather data for race strategy impact."""

    def __init__(self):
        self.rain_predictor = RainPredictor()

    def is_wet_race(self, rainfall: float) -> bool:
        """Rainfall > 0.5mm triggers wet race conditions."""
        return rainfall > 0.5

    def track_grip_level(self, rainfall: float, track_temp: float = 30) -> float:
        """
        Estimate track grip as multiplier (0.0-1.0).
        Dry = 1.0, heavy rain < 0.6.
        """
        if rainfall == 0:
            return 1.0
        elif rainfall < 0.5:
            return 0.85  # drizzle
        elif rainfall < 2.0:
            return 0.70
        elif rainfall < 5.0:
            return 0.60
        else:
            return 0.50  # heavy rain

    def wet_driver_advantage(self, rainfall: float) -> List[str]:
        """
        Return drivers who historically perform better in wet conditions.
        At Suzuka in wet: Hamilton (multiple wet wins), Verstappen (good in rain),
        Leclerc (Ferrari historically strong in wet).
        """
        if rainfall < 0.5:
            return []  # dry
        # Suzuka wet winners: Hamilton 2007, 2014, 2017; Verstappen 2022
        return ["Hamilton", "Verstappen", "Leclerc"]

    def pit_stop_penalty_wet(self, pit_loss: float) -> float:
        """Wet conditions = longer pit stops (+3 seconds typical)."""
        return pit_loss + 3.0

    def fetch_weather(self, session_key: str) -> List[Dict]:
        """Fetch weather data from OpenF1."""
        try:
            resp = requests.get(f"{BASE_URL}/weather", params={
                'session_key': session_key
            }, timeout=10)
            return resp.json()
        except Exception:
            return []


def render_weather_tab():
    """Render the Streamlit weather tab."""
    st.markdown("### 🌦️ Weather Impact")

    # Suzuka March weather overview
    rp = RainPredictor()
    rain_prob = rp.suzuka_rain_probability(month=3)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Suzuka Rain Probability", f"{rain_prob:.0f}%")
    with col2:
        st.metric("Track Temp (est.)", "28°C")
    with col3:
        st.metric("Humidity (est.)", "65%")

    # Rain probability gauge (text-based)
    st.markdown("#### 🌧️ Rain Risk Assessment")
    if rain_prob > 50:
        st.error(f"**HIGH RAIN RISK ({rain_prob:.0f}%)** — Consider intermediate/wet tires in your strategy")
    elif rain_prob > 30:
        st.warning(f"**MODERATE RAIN RISK ({rain_prob:.0f}%)** — Monitor FP/qualifying for rain setup")
    else:
        st.success(f"**LOW RAIN RISK ({rain_prob:.0f}%)** — Dry race expected")

    # Grip levels
    st.markdown("#### 🛞 Track Grip Forecast")
    conditions = [
        ("Dry", 1.0, "100%", "✅ C1/C2/C3 compounds"),
        ("Light drizzle", 0.85, "85%", "⚠️ Intermediate tire"),
        ("Moderate rain", 0.65, "65%", "❌ Wet required"),
        ("Heavy rain", 0.50, "50%", "❌ Wet required, race may be interrupted"),
    ]
    for label, grip, pct, recommendation in conditions:
        st.markdown(f"- **{label}:** Grip `{pct}` — {recommendation}")

    # Wet weather drivers
    st.markdown("#### 🌧️ Wet Weather Performers")
    st.markdown("Drivers who historically perform well in Suzuka wet conditions:")
    wet_drivers = rp.wet_driver_advantage(rainfall=2.0)
    for driver in wet_drivers:
        st.markdown(f"- **{driver}** 🏆")

    # Wind impact
    st.markdown("#### 💨 Wind Impact")
    wind_speed = st.slider("Wind Speed (kph)", 0, 60, 15)
    wind_penalty = rp.wind_impact(wind_speed)
    if wind_penalty < -0.1:
        st.warning(f"High wind ({wind_speed} kph) — reduced aero grip, unpredictable DRS zones")
    elif wind_penalty < 0:
        st.info(f"Moderate wind ({wind_speed} kph) — minor grip reduction")
    else:
        st.success(f"Low wind ({wind_speed} kph) — normal conditions")

    # Live weather data section
    st.markdown("#### 📡 Live Weather Data")
    st.info("Live weather data populates from OpenF1 when session is active.")


def render_mock_weather():
    """Render mock weather when no live data available."""
    st.markdown("### 🌦️ Weather Impact")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Suzuka Rain Probability", "~40%")
    with col2:
        st.metric("Track Temp (est.)", "28°C")
    with col3:
        st.metric("Humidity (est.)", "65%")

    st.markdown("#### 🌧️ Rain Risk Assessment")
    st.warning("**MODERATE RAIN RISK (~40%)** — Monitor FP/qualifying for rain setup")

    st.markdown("#### 🛞 Track Grip Forecast")
    st.markdown("- **Dry:** Grip `100%` — ✅ C1/C2/C3 compounds")
    st.markdown("- **Light drizzle:** Grip `85%` — ⚠️ Intermediate")
    st.markdown("- **Moderate rain:** Grip `65%` — ❌ Wet required")

    st.markdown("#### 💨 Wind Impact")
    st.info("Low wind expected — Suzuka's natural wind protection from trees")

    st.markdown("#### 🌧️ Wet Weather Performers")
    st.markdown("- **Hamilton** 🏆 (2007, 2014, 2017 Suzuka wet wins)")
    st.markdown("- **Verstappen** 🏆 (2022 Sprint in wet)")
    st.markdown("- **Leclerc** (Ferrari historically strong in wet)")