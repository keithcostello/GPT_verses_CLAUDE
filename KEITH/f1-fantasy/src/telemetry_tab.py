"""F1 Live Telemetry Tab — sector times, position gaps, lap charts."""
import streamlit as st
import requests
from typing import Dict, List, Optional

BASE_URL = "https://api.openf1.org/v1"


class OpenF1Client:
    """OpenF1 API client for F1 telemetry data."""

    def fetch_all_sessions(self, year: int = None) -> List[Dict]:
        """Fetch all sessions, optionally filtered by year."""
        params = {'limit': 200}
        if year:
            params['year'] = year
        try:
            resp = requests.get(f"{BASE_URL}/sessions", params=params, timeout=15)
            data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def fetch_laps(self, session_key: str) -> List[Dict]:
        """Fetch all lap times for a session."""
        try:
            resp = requests.get(f"{BASE_URL}/laps", params={
                'session_key': session_key
            }, timeout=15)
            data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def fetch_positions(self, session_key: str) -> List[Dict]:
        """Fetch position data for all drivers."""
        try:
            resp = requests.get(f"{BASE_URL}/position", params={
                'session_key': session_key
            }, timeout=15)
            data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def fetch_intervals(self, session_key: str) -> List[Dict]:
        """Fetch gap/interval data to leader."""
        try:
            resp = requests.get(f"{BASE_URL}/intervals", params={
                'session_key': session_key
            }, timeout=15)
            data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def fetch_stints(self, session_key: str) -> List[Dict]:
        """Fetch stint/pit stop data."""
        try:
            resp = requests.get(f"{BASE_URL}/stints", params={
                'session_key': session_key
            }, timeout=15)
            data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []


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
        valid = [l for l in laps if l.get('lap_time') and l['lap_time'] > 0]
        if not valid:
            return {'driver': None, 'time': None}
        fastest = min(valid, key=lambda x: x['lap_time'])
        return {'driver': fastest.get('driver_number', 'Unknown'), 'time': fastest['lap_time']}

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
    """Render the Streamlit telemetry tab with session selector."""
    st.markdown("### 📡 Live Telemetry")

    client = OpenF1Client()
    analyzer = TelemetryAnalyzer()

    # Year selector
    year = st.selectbox("Season", [2026, 2025, 2024, 2023], index=0)

    # Fetch all sessions for the selected year
    sessions = client.fetch_all_sessions(year=year)

    if not sessions:
        st.warning("No sessions found for the selected season. OpenF1 may be unavailable.")
        return

    # Group sessions by meeting/country
    meetings = {}
    for s in sessions:
        key = s.get('meeting_name', 'Unknown')
        if key not in meetings:
            meetings[key] = s

    # Country selector
    meeting_names = sorted(meetings.keys())
    if not meeting_names:
        st.warning("No Grand Prix found for the selected season.")
        return

    selected_meeting = st.selectbox("Grand Prix", meeting_names)

    # Session type selector
    meeting_sessions = [s for s in sessions if s.get('meeting_name') == selected_meeting]
    session_types = list(set(s.get('session_name', '') for s in meeting_sessions))
    session_type = st.selectbox("Session", sorted(session_types))

    # Get session key for selected session
    selected_session = next(
        (s for s in meeting_sessions if s.get('session_name') == session_type),
        None
    )

    if not selected_session:
        st.warning("Select a session to view telemetry.")
        return

    session_key = selected_session.get('session_key')
    st.success(f"Session: {session_type} — {selected_meeting}")

    # Fetch all telemetry data
    laps = client.fetch_laps(session_key)
    positions = client.fetch_positions(session_key)
    intervals = client.fetch_intervals(session_key)
    stints = client.fetch_stints(session_key)

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
        # Show top 10 laps sorted by lap_time
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
    st.info("📡 Select a session above to view live telemetry data.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Session", "—", label_visibility="collapsed")
    with col2:
        st.metric("Status", "Awaiting Selection", label_visibility="collapsed")
    with col3:
        st.metric("Data Points", "0", label_visibility="collapsed")

    st.markdown("#### 🛞 Tire Strategy")
    st.markdown("Select a race session above to view tire strategy.")

    st.markdown("#### 📈 Position Changes")
    st.markdown("Select a race session above to view position changes.")

    st.markdown("#### ⏱️ Lap Times")
    st.markdown("Select a race session above to view lap times.")