import dataclasses

import pytest

from econlab.engine import BudgetLine, ParameterError, classify_change

DEFAULT = BudgetLine(m=100, p1=10, p2=5)


def test_default_intercepts_and_slope():
    assert DEFAULT.x1_max == 10
    assert DEFAULT.x2_max == 20
    assert DEFAULT.slope == -2


def test_line_points_satisfy_budget_equation():
    xs, ys = DEFAULT.line_points(11)
    for x1, x2 in zip(xs, ys):
        assert DEFAULT.expenditure(x1, x2) == pytest.approx(100)
    assert ys[0] == pytest.approx(20)
    assert ys[-1] == pytest.approx(0)


def test_rearranged_equation():
    assert DEFAULT.x2_on_line(4) == pytest.approx(100 / 5 - 2 * 4)


def test_income_increase_is_parallel_outward():
    new = BudgetLine(150, 10, 5)
    assert (new.x1_max, new.x2_max, new.slope) == (15, 30, DEFAULT.slope)
    assert classify_change(DEFAULT, new).kind == "parallel_out"


def test_income_decrease_is_parallel_inward():
    new = BudgetLine(50, 10, 5)
    assert new.slope == DEFAULT.slope
    assert classify_change(DEFAULT, new).kind == "parallel_in"


def test_price1_increase_pivots_inward_around_x2_intercept():
    new = BudgetLine(100, 20, 5)
    assert new.x2_max == DEFAULT.x2_max and new.x1_max == 5
    assert classify_change(DEFAULT, new).kind == "pivot_x2_in"


def test_price1_decrease_pivots_outward():
    assert classify_change(DEFAULT, BudgetLine(100, 5, 5)).kind == "pivot_x2_out"


def test_price2_increase_pivots_inward_around_x1_intercept():
    new = BudgetLine(100, 10, 10)
    assert new.x1_max == DEFAULT.x1_max and new.x2_max == 10
    assert classify_change(DEFAULT, new).kind == "pivot_x1_in"


def test_combined_change():
    assert classify_change(DEFAULT, BudgetLine(120, 20, 5)).kind == "combined"


def test_proportional_scaling_leaves_set_unchanged():
    assert classify_change(DEFAULT, BudgetLine(200, 20, 10)).kind == "unchanged"


def test_affordability():
    assert DEFAULT.is_affordable(5, 10)       # exactly on the line
    assert DEFAULT.is_affordable(0, 0)
    assert not DEFAULT.is_affordable(6, 10)   # costs 110
    assert not DEFAULT.is_affordable(-1, 0)


@pytest.mark.parametrize("m,p1,p2,fragment", [
    (-1, 10, 5, "m"),
    (100, 0, 5, "p₁"),
    (100, 10, 0, "p₂"),
    (100, -3, 5, "p₁"),
    (float("nan"), 10, 5, "m"),
    (100, float("inf"), 5, "p1"),
    ("100", 10, 5, "m"),
    (True, 10, 5, "m"),
])
def test_invalid_parameters_raise(m, p1, p2, fragment):
    with pytest.raises(ParameterError, match=fragment):
        BudgetLine(m, p1, p2)


def test_zero_income_is_a_single_point():
    b = BudgetLine(0, 10, 5)
    assert (b.x1_max, b.x2_max) == (0, 0)
    assert b.is_affordable(0, 0) and not b.is_affordable(1, 0)


def test_tiny_price_gives_large_finite_intercept():
    assert BudgetLine(100, 1e-9, 5).x1_max == pytest.approx(1e11)


def test_model_is_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT.m = 5
