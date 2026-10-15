import pytest

from econlab.models import load_models
from econlab.registry import REGISTRY


def test_budget_line_sits_in_forbrugerteori():
    load_models()
    ids = [m.id for m in REGISTRY.tree()["MIKROØKONOMI"]["Forbrugerteori"]]
    assert "budget_line" in ids


def test_empty_chapters_still_listed():
    load_models()
    assert "IS-LM" in REGISTRY.tree()["MAKROØKONOMI"]


def test_duplicate_registration_rejected():
    load_models()
    with pytest.raises(ValueError):
        REGISTRY.register(REGISTRY.get("budget_line"))


def test_search():
    load_models()
    assert [m.id for m in REGISTRY.search("budget")] == ["budget_line"]
    assert REGISTRY.search("xyzzy") == []


def test_figure_and_analysis_build_for_defaults():
    load_models()
    m = REGISTRY.get("budget_line")
    values = {p.key: p.default for p in m.parameters}
    opts = {o.key: o.default for o in m.options}
    fig = m.build_figure(values, dict(values, m=150.0), opts)
    assert len(fig.data) >= 3
    assert m.analyse(values, None).derived[0].value == 10
