"""Model registry: the single place that knows which models exist.

No Streamlit here. The sidebar, the parameter panel and the info panel are all
generated from ModelDefinition objects, so adding a model never touches the UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .catalog import CATALOG


@dataclass(frozen=True)
class Parameter:
    key: str          # name used in code, e.g. "p1"
    symbol: str       # LaTeX, e.g. "p_1"
    label: str        # Danish description
    default: float
    min: float
    max: float
    step: float
    group: str = "Parametre"
    tooltip: str = ""

    def __post_init__(self) -> None:
        if not (self.min <= self.default <= self.max) or self.step <= 0:
            raise ValueError(f"Ugyldig parameterdefinition: {self.key}")


@dataclass(frozen=True)
class DisplayOption:
    key: str
    label: str
    default: bool = True


@dataclass(frozen=True)
class Derived:
    label: str
    value: float
    baseline: float | None = None
    decimals: int = 2


@dataclass(frozen=True)
class Analysis:
    derived: tuple[Derived, ...]
    steps: tuple[str, ...]            # LaTeX lines showing the calculation
    change_note: str | None = None    # comparison with baseline, if any


@dataclass(frozen=True)
class ModelDefinition:
    id: str
    name: str
    category: str
    chapter: str
    description: str
    parameters: tuple[Parameter, ...]
    options: tuple[DisplayOption, ...]
    equations: tuple[str, ...]                       # LaTeX
    extra_variables: tuple[tuple[str, str], ...]     # (LaTeX symbol, description)
    assumptions: tuple[str, ...]
    interpretation: tuple[str, ...]
    analyse: Callable[[dict, dict | None], Analysis]
    build_figure: Callable[[dict, dict | None, dict], Any]
    keywords: tuple[str, ...] = ()
    also_in: tuple[tuple[str, str], ...] = ()        # extra (category, chapter) spots


class Registry:
    def __init__(self) -> None:
        self._models: dict[str, ModelDefinition] = {}

    def register(self, model: ModelDefinition) -> ModelDefinition:
        if model.id in self._models:
            raise ValueError(f"Model-id er allerede registreret: {model.id}")
        self._models[model.id] = model
        return model

    def get(self, model_id: str) -> ModelDefinition:
        return self._models[model_id]

    def all(self) -> list[ModelDefinition]:
        return list(self._models.values())

    def default_model_id(self) -> str:
        return next(iter(self._models))

    def tree(self) -> dict[str, dict[str, list[ModelDefinition]]]:
        """category -> chapter -> models. Catalog order first, then extras."""
        tree: dict[str, dict[str, list[ModelDefinition]]] = {
            cat: {ch: [] for ch in chapters} for cat, chapters in CATALOG.items()
        }
        for m in self._models.values():
            for cat, ch in ((m.category, m.chapter), *m.also_in):
                tree.setdefault(cat, {}).setdefault(ch, []).append(m)
        return tree

    def search(self, query: str) -> list[ModelDefinition]:
        terms = query.lower().split()
        hits = []
        for m in self._models.values():
            hay = " ".join([m.name, m.description, m.category, m.chapter, *m.keywords]).lower()
            if all(t in hay for t in terms):
                hits.append(m)
        return hits


REGISTRY = Registry()
