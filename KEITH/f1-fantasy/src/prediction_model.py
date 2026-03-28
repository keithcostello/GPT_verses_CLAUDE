"""F1 Fantasy prediction model — weighted composite scoring."""
from typing import List, Dict, Tuple

# 2026 race results (fantasy points per position)
RACE_POINTS = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

# 2026 driver prices (from F1 Fantasy / Amy's research)
DRIVER_PRICES = {
    "Russell": 18400000,
    "Antonelli": 16200000,
    "Piastri": 14100000,
    "Norris": 15800000,
    "Leclerc": 15500000,
    "Hamilton": 15000000,
    "Verstappen": 17300000,
    "Perez": 12000000,
    "Bearman": 8500000,
    "Gasly": 9200000,
    "Ocon": 9000000,
    "Norris": 15800000,
    "Alonso": 10000000,
    "Hulkenberg": 9500000,
    "Stroll": 9000000,
}

CONSTRUCTOR_PRICES = {
    "Mercedes": 31000000,
    "Ferrari": 28000000,
    "McLaren": 26500000,
    "Red Bull": 24000000,
    "Haas": 17000000,
    "Alpine": 15000000,
    "Williams": 13000000,
    "Aston Martin": 14500000,
}

# 2026 Australia GP results
AUSTRALIA_RESULTS = {
    "Russell": 1, "Antonelli": 2, "Piastri": 3, "Norris": 4, "Leclerc": 5, "Hamilton": 6,
    "Verstappen": 7, "Perez": 8, "Bearman": 9, "Gasly": 10, "Ocon": 11, "Alonso": 12
}

# 2026 China GP results
CHINA_RESULTS = {
    "Antonelli": 1, "Russell": 2, "Hamilton": 3, "Leclerc": 4, "Bearman": 5, "Gasly": 6,
    "Piastri": 7, "Norris": 8, "Verstappen": 9, "Perez": 10, "Ocon": 11, "Alonso": 12
}


def fantasy_points(position: int) -> int:
    """Convert finishing position to F1 Fantasy points."""
    return RACE_POINTS.get(position, 0)


class SuzukaCircuit:
    """Suzuka-specific factors — regulation-resistant constants."""

    def __init__(self):
        self.name = "Suzuka International Racing Course"
        self.pit_loss_seconds = 25  # ~370m at pit speed limit
        self.overtaking_zones = [1, 2]  # T1 (130R) and main straight DRS
        # Historical Suzuka performance factors (pre-2026 reg change)
        self.historical_suzuka = {
            "Hamilton": 0.95,  # Multiple wins
            "Russell": 0.88,
            "Verstappen": 0.92,
            "Leclerc": 0.85,
            "Norris": 0.82,
            "Piastri": 0.80,
            "Antonelli": 0.78,  # Rookies historically struggle at Suzuka
            "Bearman": 0.60,  # F1 rookie, hasn't raced Suzuka
            "Gasly": 0.85,  # Won 2023 AlphaTauri Suzuka
            "Ocon": 0.78,
            "Perez": 0.75,  # Struggles at high-speed corners
        }

    def get_suzuka_factor(self, driver: str) -> float:
        """Return 0.0-1.0 Suzuka historical factor for driver."""
        return self.historical_suzuka.get(driver, 0.70)


class PredictionModel:
    """
    Weighted composite prediction model.
    50% Australia + 30% China + 20% Suzuka factor.
    """

    def __init__(self):
        self.suzuka = SuzukaCircuit()
        self.driver_prices = DRIVER_PRICES
        self.constructor_prices = CONSTRUCTOR_PRICES

    def weighted_score(self, australia_pts: int, china_pts: int, suzuka_factor: float) -> float:
        """Composite score: 50% Australia + 30% China + 20% Suzuka-adjusted."""
        suzuka_score = 100 * suzuka_factor  # Normalize to ~100 scale
        return 0.50 * australia_pts + 0.30 * china_pts + 0.20 * suzuka_score

    def project_points(self, driver_name: str, australia_position: int, china_position: int,
                       suzuka_factor: float, price: float) -> Dict:
        """Project fantasy points and PPM for a single driver."""
        aus_pts = fantasy_points(australia_position)
        chn_pts = fantasy_points(china_position)
        composite = self.weighted_score(aus_pts, chn_pts, suzuka_factor)
        ppm = round(composite / (price / 1_000_000), 2)
        return {
            'name': driver_name,
            'australia_pts': aus_pts,
            'china_pts': chn_pts,
            'projected_ppm': ppm,
            'projected_points': round(composite, 1),
            'price': price,
            'suzuka_factor': suzuka_factor
        }

    def predict_all_drivers(self) -> List[Dict]:
        """Rank all drivers by projected PPM."""
        results = []
        australia = AUSTRALIA_RESULTS
        china = CHINA_RESULTS

        for driver, aus_pos in australia.items():
            if driver not in self.driver_prices:
                continue
            chn_pos = china.get(driver, 12)
            price = self.driver_prices[driver]
            suzuka_f = self.suzuka.get_suzuka_factor(driver)

            proj = self.project_points(driver, aus_pos, chn_pos, suzuka_f, price)
            results.append(proj)

        # Sort by projected PPM descending
        results.sort(key=lambda x: x['projected_ppm'], reverse=True)
        return results