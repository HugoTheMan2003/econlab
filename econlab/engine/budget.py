"""Pure maths for the consumer budget constraint  p1*x1 + p2*x2 = m.

No Streamlit, no Plotly. Every result here is an exact analytical formula.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .errors import ParameterError


def _check_number(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ParameterError(f"{name} skal være et tal (fik {value!r}).")
    if not math.isfinite(value):
        raise ParameterError(f"{name} skal være et endeligt tal.")


@dataclass(frozen=True)
class BudgetLine:
    m: float   # income
    p1: float  # price of good 1
    p2: float  # price of good 2

    def __post_init__(self) -> None:
        for name in ("m", "p1", "p2"):
            _check_number(name, getattr(self, name))
        if self.m < 0:
            raise ParameterError("Indkomsten m kan ikke være negativ.")
        if self.p1 <= 0:
            raise ParameterError("Prisen p₁ skal være strengt positiv.")
        if self.p2 <= 0:
            raise ParameterError("Prisen p₂ skal være strengt positiv.")

    # --- derived quantities -------------------------------------------------
    @property
    def x1_max(self) -> float:
        return self.m / self.p1

    @property
    def x2_max(self) -> float:
        return self.m / self.p2

    @property
    def slope(self) -> float:
        return -self.p1 / self.p2

    # --- functions ----------------------------------------------------------
    def x2_on_line(self, x1):
        """x2 = m/p2 - (p1/p2) x1 (works for floats and numpy arrays)."""
        return self.m / self.p2 - (self.p1 / self.p2) * x1

    def expenditure(self, x1: float, x2: float) -> float:
        return self.p1 * x1 + self.p2 * x2

    def is_affordable(self, x1: float, x2: float, tol: float = 1e-9) -> bool:
        return x1 >= 0 and x2 >= 0 and self.expenditure(x1, x2) <= self.m + tol

    def line_points(self, n: int = 101):
        xs = np.linspace(0.0, self.x1_max, n)
        return xs, self.x2_on_line(xs)


@dataclass(frozen=True)
class BudgetChange:
    kind: str
    description: str
    d_x1_max: float
    d_x2_max: float
    d_slope: float


def classify_change(old: BudgetLine, new: BudgetLine, rel_tol: float = 1e-9) -> BudgetChange:
    """Describe how the budget line moved from `old` to `new`."""
    def close(a: float, b: float) -> bool:
        return math.isclose(a, b, rel_tol=rel_tol, abs_tol=1e-12)

    same_x1 = close(old.x1_max, new.x1_max)
    same_x2 = close(old.x2_max, new.x2_max)
    same_slope = close(old.slope, new.slope)

    if same_x1 and same_x2:
        kind, text = "unchanged", "Budgetmængden er uændret."
    elif same_slope:
        out = new.x1_max > old.x1_max
        kind = "parallel_out" if out else "parallel_in"
        text = (f"Parallelforskydning {'udad' if out else 'indad'}: begge skæringspunkter "
                "ændres i samme forhold, og hældningen er uændret.")
    elif same_x2:
        out = new.x1_max > old.x1_max
        kind = "pivot_x2_out" if out else "pivot_x2_in"
        text = (f"Budgetlinjen drejer {'udad' if out else 'indad'} om skæringspunktet på "
                "x₂-aksen; skæringspunktet på x₁-aksen ændres.")
    elif same_x1:
        out = new.x2_max > old.x2_max
        kind = "pivot_x1_out" if out else "pivot_x1_in"
        text = (f"Budgetlinjen drejer {'udad' if out else 'indad'} om skæringspunktet på "
                "x₁-aksen; skæringspunktet på x₂-aksen ændres.")
    else:
        kind = "combined"
        text = "Både skæringspunkter og hældning ændres: linjen både forskydes og drejer."

    return BudgetChange(kind, text, new.x1_max - old.x1_max,
                        new.x2_max - old.x2_max, new.slope - old.slope)
