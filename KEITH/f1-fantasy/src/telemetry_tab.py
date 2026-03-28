"""F1 Live Telemetry Tab — sector times, position gaps, lap charts."""
import streamlit as st
import requests
from typing import Dict, List, Optional

BASE_URL = "https://api.openf1.org/v1"

class SuzukaTelemetry:
    """Suzuka circuit telemetry utilities."""

    def __init__(self):
        self.circuit_name = "Suzuka International Racing Course"
        self.circuit_country = "Japan"
        self.sector_boundaries = {
            'sector_1': 'Turn 1-7 (Toyota S-Figure, DunlopCurve)',
            'sector_2': 'Turn 8-12 (250R, Hairpin, Spoon Curve)',
            'sector_3': 'Turn 13-16 (130R, final chicane)'
        }

    def fetch_suzuka_session(self, year=2026) -> Optional[Dict]:
        """Get the Suzuka session key for a given year."""
        try:
            resp = requests.get(f"{BASE_URL}/sessions", params={
                'year': year,
                'country_code': 'JP',
                'session_name': 'Race'
            }, timeout=10)
            data = resp.json()
            if data:
                return data[0]
        except Exception:
            pass
        return None

    def fetch_lap_times(self, session_key: str) -> List[Dict]:
        """Fetch all lap times for a session."""
        try:
            resp = requests.get(f"{BASE_URL}/laps", params={
                'session_key': session_key
            }, timeout=15)
            return resp.json()
        except Exception:
            return []

    def fetch_positions(self, session_key: str) -> List[Dict]:
        """Fetch position data for all drivers."""
        try:
            resp = requests.get(f"{BASE_URL}/position", params={
                'session_key': session_key
            }, timeout=15)
            return resp.json()
        except Exception:
            return []

    def fetch_intervals(self, session_key: str) -> List[Dict]:
        """Fetch gap/interval data to leader."""
        try:
            resp = requests.get(f"{BASE_URL}/intervals", params={
                'session_key': session_key
            }, timeout=15)
            return resp.json()
        except Exception:
            return []

    def fetch_stints(self, session_key: str) -> List[Dict]:
        """Fetch stint/pit stop data."""
        try:
            resp = requests.get(f"{BASE_URL}/stints", params={
                'session_key': session_key
            }, timeout=15)
            return resp.json()
        except Exception:
            return []

    def get_driver_sector_times(self, driver_number: int) -> Dict:
        """
        Get sector times for a driver.
        Note: OpenF1 does not provide sector-level timing;
        this returns structural sector boundaries for Suzuka.
        """
        return {
            'sector_1': 'Turn 1-7 (Toyota S-Figure, DunlopCurve)',
            'sector_2': 'Turn 8-12 (250R, Hairpin, Spoon Curve)',
            'sector_3': 'Turn 13-16 (130R, final chicane)',
            'driver_number': driver_number
        }


class TelemetryAnalyzer:
    """Analyze telemetry data for strategy insights."""

    def identify_position_gains(self, positions_by_driver: Dict[str, List[int]]) -> List[str]:
        """
        Given {driver: [start_pos, mid_pos, end_pos]},
        return drivers who gained net positions.
        Did not lose = maintained or improved position.
        """
        gainers = []
        for driver, positions in positions_by_driver.items():
            if len(positions) >= 2 and positions[-1] <= positions[0]:
                gainers.append(driver)
        return gainers

    def fastest_lap_detection(self, laps: List[Dict]) -> Dict:
        """Return driver + time of fastest lap."""
        if not laps:
            return {'driver': None, 'time': None}
        valid = [l for l in laps if l.get('time') and l['time'] > 0]
        if not valid:
            return {'driver': None, 'time': None}
        fastest = min(valid, key=lambda x: x['time'])
        return {'driver': fastest.get('driver', 'Unknown'), 'time': fastest['time']}

    def pit_stop_count_from_stints(self, driver: str, stints: List[Dict]) -> int:
        """2 stints = 1 pit stop, 3 stints = 2 pit stops."""
        driver_stints = [s for s in stints if s.get('driver') == driver]
        return max(0, len(driver_stints) - 1)

    def stint_analysis(self, stints: List[Dict]) -> Dict:
        """
        Return per-driver stint analysis:
        {driver: [(compound, lap_start, lap_end), ...]}
        """
        result = {}
        for stint in stints:
            driver = stint.get('driver', 'Unknown')
            if driver not in result:
                result[driver] = []
            result[driver].append((
                stint.get('compound', 'Unknown'),
                stint.get('lap_start', 0),
                stint.get('lap_end', 0)
            ))
        return result


def render_telemetry_tab():
    """Render the Streamlit telemetry tab."""
    st.markdown("### 📡 Live Telemetry")

    # Session selector
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Season", [2026, 2025], index=0)
    with col2:
        session_type = st.selectbox("Session", ["Race", "Qualifying", "Sprint", "FP1", "FP2", "FP3"])

    telemetry = SuzukaTelemetry()
    analyzer = TelemetryAnalyzer()

    # Fetch session data
    session = telemetry.fetch_suzuka_session(year)

    if not session:
        st.warning("Suzuka session data not yet available. Check back when FP1 starts.")
        st.info("OpenF1 data is embargoed until race weekend begins.")
        return

    session_key = session.get('session_key')
    st.success(f"Session: {session.get('session_name', 'Race')} — {session.get('meeting_name', 'Japanese GP')}")

    # Fetch all telemetry data
    laps = telemetry.fetch_lap_times(session_key)
    positions = telemetry.fetch_positions(session_key)
    intervals = telemetry.fetch_intervals(session_key)
    stints = telemetry.fetch_stints(session_key)

    # Stint/Tire analysis
    st.markdown("#### 🛞 Tire Strategy")
    if stints:
        stint_data = analyzer.stint_analysis(stints)
        for driver, compound_list in list(stint_data.items())[:5]:
            compounds = " → ".join([f"{c[0]}(L{c[1]}-{c[2]})" for c in compound_list])
            st.markdown(f"**{driver}:** {compounds}")
    else:
        st.info("Stint data available after race starts.")

    # Position changes
    st.markdown("#### 📈 Position Changes")
    if positions:
        st.markdown(f"Live position data: {len(positions)} records")
    else:
        st.info("Position tracking active during race sessions.")

    # Lap time table
    st.markdown("#### ⏱️ Lap Times")
    if laps:
        # Show top 20 laps sorted by time
        valid_laps = [l for l in laps if l.get('lap_time') and l['lap_time'] > 0]
        valid_laps.sort(key=lambda x: x['lap_time'])
        for lap in valid_laps[:10]:
            driver = lap.get('driver_number', '?')
            lt = lap.get('lap_time', 0)
            pos = lap.get('position', '?')
            st.markdown(f"**P{pos}** Driver {driver}: `{lt/1000:.3f}s`")
    else:
        st.info("Lap time data populates as sessions run.")

    # Fastest lap
    if laps:
        fl = analyzer.fastest_lap_detection(laps)
        if fl['driver']:
            st.markdown(f"**Fastest Lap:** {fl['driver']} — `{fl['time']/1000:.3f}s`")


# Mock data for dashboard preview (when API not available)
def render_mock_telemetry():
    """Render mock telemetry when no live data available."""
    st.markdown("### 📡 Live Telemetry")
    st.info("📡 Live data will appear here when Suzuka sessions begin.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Session", "FP1", label_visibility="collapsed")
    with col2:
        st.metric("Status", "Upcoming", label_visibility="collapsed")
    with col3:
        st.metric("Data Points", "0", label_visibility="collapsed")

    st.markdown("#### 🛞 Tire Strategy")
    st.markdown("Waiting for race data...")

    st.markdown("#### 📈 Position Changes")
    st.markdown("Waiting for race data...")

    st.markdown("#### ⏱️ Lap Times")
    st.markdown("Waiting for race data...")