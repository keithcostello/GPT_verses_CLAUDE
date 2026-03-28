"""OpenF1 API client and F1 Fantasy data utilities."""
import requests
from typing import List, Dict, Any, Optional

BASE_URL = "https://api.openf1.org/v1"

class OpenF1Client:
    """Client for OpenF1 API. No auth required."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        try:
            resp = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    def fetch_sessions(self, country_code: str = None, year: int = None) -> List[Dict]:
        params = {}
        if country_code:
            params['country_code'] = country_code
        if year:
            params['year'] = year
        return self._get("sessions", params)

    def fetch_drivers(self, session_key: str) -> List[Dict]:
        return self._get("drivers", {"session_key": session_key})

    def fetch_laps(self, session_key: str, driver_number: int = None) -> List[Dict]:
        params = {"session_key": session_key}
        if driver_number:
            params['driver_number'] = driver_number
        return self._get("laps", params)

    def fetch_weather(self, session_key: str) -> List[Dict]:
        return self._get("weather", {"session_key": session_key})


class F1FantasyScorer:
    """Calculate F1 Fantasy scores and metrics."""

    def calculate_ppm(self, points: float, price: float) -> float:
        """Points per million — fantasy output relative to cost."""
        if price <= 0:
            return 0.0
        return round(points / (price / 1_000_000), 2)

    def calculate_total_cost(self, picks: Dict) -> int:
        """Sum of all driver + constructor prices in a lineup."""
        driver_total = sum(d.get('price', 0) for d in picks.get('drivers', []))
        constructor_total = sum(c.get('price', 0) for c in picks.get('constructors', []))
        return driver_total + constructor_total

    def score_lineup(self, picks: Dict) -> Dict:
        """Return full lineup scoring summary."""
        total_cost = self.calculate_total_cost(picks)
        driver_count = len(picks.get('drivers', []))
        constructor_count = len(picks.get('constructors', []))
        return {
            'total_cost': total_cost,
            'budget_used_pct': round(total_cost / 100_000_000 * 100, 1),
            'driver_count': driver_count,
            'constructor_count': constructor_count,
            'valid': driver_count == 5 and constructor_count == 2 and total_cost <= 100_000_000
        }