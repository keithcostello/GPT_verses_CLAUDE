"""F1 Fantasy lineup optimizer using OR-tools Mixed Integer Programming."""
from typing import List, Dict
from ortools.linear_solver import pywraplp


class FantasyOptimizer:
    """
    Optimize F1 Fantasy lineup: 5 drivers + 2 constructors under $100M cap.
    Uses OR-tools mixed integer programming (MIP) to maximize projected points.
    """

    def __init__(self, drivers: List[Dict], constructors: List[Dict],
                 budget: int = 100_000_000):
        self.drivers = drivers
        self.constructors = constructors
        self.budget = budget
        self.num_drivers = len(drivers)
        self.num_constructors = len(constructors)

    def optimize(self) -> Dict:
        """
        Solve the lineup optimization problem.
        Returns: {drivers, constructors, total_cost, total_projected_points, budget_used_pct}
        """
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            raise ImportError("OR-tools not installed. Run: pip install ortools")

        # Decision variables
        # x[i] = 1 if driver i is selected
        x = [solver.IntVar(0, 1, f'driver_{i}') for i in range(self.num_drivers)]
        # y[j] = 1 if constructor j is selected
        y = [solver.IntVar(0, 1, f'constructor_{j}') for j in range(self.num_constructors)]

        # Constraints

        # Exactly 5 drivers
        solver.Add(sum(x) == 5)

        # Exactly 2 constructors
        solver.Add(sum(y) == 2)

        # Budget constraint
        cost_constraint = sum(
            self.drivers[i]['price'] * x[i] for i in range(self.num_drivers)
        ) + sum(
            self.constructors[j]['price'] * y[j] for j in range(self.num_constructors)
        ) <= self.budget
        solver.Add(cost_constraint)

        # Objective: maximize projected points
        solver.Maximize(sum(
            self.drivers[i]['projected_points'] * x[i] for i in range(self.num_drivers)
        ) + sum(
            self.constructors[j]['projected_points'] * y[j] for j in range(self.num_constructors)
        ))

        # Solve
        status = solver.Solve()

        if status != pywraplp.Solver.OPTIMAL:
            # Return best available if not optimal
            pass

        # Extract results
        selected_drivers = [
            self.drivers[i] for i in range(self.num_drivers) if x[i].solution_value() > 0.5
        ]
        selected_constructors = [
            self.constructors[j] for j in range(self.num_constructors) if y[j].solution_value() > 0.5
        ]

        total_cost = sum(d['price'] for d in selected_drivers) + sum(c['price'] for c in selected_constructors)
        total_points = sum(d['projected_points'] for d in selected_drivers) + sum(c['projected_points'] for c in selected_constructors)

        return {
            'drivers': selected_drivers,
            'constructors': selected_constructors,
            'total_cost': int(total_cost),
            'total_projected_points': round(total_points, 1),
            'budget_used_pct': round(total_cost / self.budget * 100, 1),
            'solver_status': str(status)
        }