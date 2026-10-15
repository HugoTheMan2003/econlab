"""Budgetlinje: Mikroøkonomi -> Forbrugerteori."""
from __future__ import annotations

import plotly.graph_objects as go

from ..engine import BudgetLine, classify_change
from ..registry import (REGISTRY, Analysis, Derived, DisplayOption,
                        ModelDefinition, Parameter)

BLUE, GREY = "#2563eb", "#6b7280"
HOVER = "x₁ = %{x:.2f}<br>x₂ = %{y:.2f}<extra>%{fullData.name}</extra>"

PARAMETERS = (
    Parameter("m", "m", "Indkomst", 100.0, 0.0, 1000.0, 1.0, group="Indkomst",
              tooltip="Forbrugerens samlede indkomst. Må ikke være negativ."),
    Parameter("p1", "p_1", "Pris på gode 1", 10.0, 0.1, 100.0, 0.1, group="Priser",
              tooltip="Pris pr. enhed af gode 1. Skal være strengt positiv."),
    Parameter("p2", "p_2", "Pris på gode 2", 5.0, 0.1, 100.0, 0.1, group="Priser",
              tooltip="Pris pr. enhed af gode 2. Skal være strengt positiv."),
)
OPTIONS = (
    DisplayOption("show_feasible", "Vis budgetmængde (mulige forbrug)"),
    DisplayOption("show_intercepts", "Vis skæringspunkter"),
    DisplayOption("show_baseline", "Vis oprindelig budgetlinje (baseline)"),
)


def build_figure(values: dict, baseline: dict | None, options: dict) -> go.Figure:
    bl = BudgetLine(**values)
    base = BudgetLine(**baseline) if baseline and options.get("show_baseline", True) else None
    fig = go.Figure()

    if options.get("show_feasible", True) and bl.m > 0:
        fig.add_trace(go.Scatter(
            x=[0, bl.x1_max, 0, 0], y=[0, 0, bl.x2_max, 0], mode="none", fill="toself",
            fillcolor="rgba(37,99,235,0.10)", name="Budgetmængde", hoverinfo="skip"))
    if base is not None:
        xs, ys = base.line_points()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Oprindelig budgetlinje",
                                 line=dict(color=GREY, width=2, dash="dash"), hovertemplate=HOVER))
    xs, ys = bl.line_points()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Budgetlinje",
                             line=dict(color=BLUE, width=3), hovertemplate=HOVER))
    if options.get("show_intercepts", True) and bl.m > 0:
        fig.add_trace(go.Scatter(
            x=[bl.x1_max, 0], y=[0, bl.x2_max], mode="markers+text", name="Skæringspunkter",
            text=[f"x₁ = {bl.x1_max:.2f}", f"x₂ = {bl.x2_max:.2f}"],
            textposition=["top center", "middle right"],
            marker=dict(size=9, color=BLUE, line=dict(width=2, color="white")),
            hovertemplate=HOVER))
    if bl.m > 0:
        fig.add_annotation(x=bl.x1_max / 2, y=bl.x2_max / 2, showarrow=False, xshift=40, yshift=22,
                           text=f"hældning = −p₁/p₂ = {bl.slope:.2f}", font=dict(color=BLUE, size=13))
    else:
        fig.add_annotation(x=0, y=0, showarrow=True, ax=90, ay=-50,
                           text="m = 0: budgetmængden er kun punktet (0, 0)")

    xmax = max([bl.x1_max] + ([base.x1_max] if base else []))
    ymax = max([bl.x2_max] + ([base.x2_max] if base else []))
    xlim = xmax * 1.2 if xmax > 0 else 1.0
    ylim = ymax * 1.2 if ymax > 0 else 1.0
    axis = dict(gridcolor="#eef0f3", zeroline=True, zerolinecolor="#9ca3af")
    fig.update_layout(
        template="plotly_white", height=560, dragmode="pan", hovermode="closest",
        margin=dict(l=60, r=20, t=30, b=50),
        xaxis=dict(title="Mængde af gode 1 (x₁)", range=[-0.04 * xlim, xlim], **axis),
        yaxis=dict(title="Mængde af gode 2 (x₂)", range=[-0.04 * ylim, ylim], **axis),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0))
    return fig


def analyse(values: dict, baseline: dict | None) -> Analysis:
    bl = BudgetLine(**values)
    base = BudgetLine(**baseline) if baseline else None
    derived = (
        Derived("Maks. gode 1 (m/p₁)", bl.x1_max, base.x1_max if base else None),
        Derived("Maks. gode 2 (m/p₂)", bl.x2_max, base.x2_max if base else None),
        Derived("Hældning (−p₁/p₂)", bl.slope, base.slope if base else None),
    )
    steps = (
        rf"x_1^{{\max}} = \dfrac{{m}}{{p_1}} = \dfrac{{{bl.m:g}}}{{{bl.p1:g}}} = {bl.x1_max:.2f}",
        rf"x_2^{{\max}} = \dfrac{{m}}{{p_2}} = \dfrac{{{bl.m:g}}}{{{bl.p2:g}}} = {bl.x2_max:.2f}",
        rf"\text{{hældning}} = -\dfrac{{p_1}}{{p_2}} = -\dfrac{{{bl.p1:g}}}{{{bl.p2:g}}} = {bl.slope:.2f}",
        rf"x_2 = {bl.x2_max:.2f} - {abs(bl.slope):.2f}\,x_1",
    )
    note = classify_change(base, bl).description if base else None
    return Analysis(derived, steps, note)


MODEL = REGISTRY.register(ModelDefinition(
    id="budget_line",
    name="Budgetlinje",
    category="MIKROØKONOMI",
    chapter="Forbrugerteori",
    description="Forbrugerens budgetbegrænsning p₁x₁ + p₂x₂ = m og den tilhørende budgetmængde.",
    parameters=PARAMETERS,
    options=OPTIONS,
    equations=(
        r"p_1 x_1 + p_2 x_2 = m",
        r"x_2 = \dfrac{m}{p_2} - \dfrac{p_1}{p_2}\,x_1",
        r"B = \{(x_1, x_2) \in \mathbb{R}_+^2 : p_1 x_1 + p_2 x_2 \le m\}",
    ),
    extra_variables=(("x_1", "Mængde af gode 1"), ("x_2", "Mængde af gode 2")),
    assumptions=(
        "Priserne er strengt positive (p₁ > 0, p₂ > 0) og indkomsten er ikke-negativ (m ≥ 0).",
        "Priserne er lineære: ingen mængderabatter.",
        "Goderne er perfekt delelige, og x₁, x₂ ≥ 0.",
        "Hele indkomsten kan bruges i én periode; ingen opsparing eller lån.",
    ),
    interpretation=(
        "Højere indkomst m forskyder budgetlinjen parallelt udad; lavere indkomst forskyder den indad.",
        "Stiger p₁, drejer linjen indad om skæringspunktet på x₂-aksen (m/p₂ er uændret).",
        "Stiger p₂, drejer linjen indad om skæringspunktet på x₁-aksen (m/p₁ er uændret).",
        "Hældningen −p₁/p₂ er alternativomkostningen: hvor mange enheder gode 2 der opgives pr. enhed gode 1.",
        "Ganges m, p₁ og p₂ med samme positive tal, er budgetmængden uændret.",
    ),
    analyse=analyse,
    build_figure=build_figure,
    keywords=("budgetbegrænsning", "budget constraint", "forbruger", "priser", "indkomst"),
))
