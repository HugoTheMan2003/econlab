"""Collapsible panel below the graph: equations, variables, calculation, assumptions."""
import streamlit as st


def render(model, analysis) -> None:
    with st.expander("Matematik og økonomisk fortolkning", expanded=True):
        tabs = st.tabs(["Ligninger", "Variable", "Udregning", "Antagelser", "Fortolkning"])
        with tabs[0]:
            for eq in model.equations:
                st.latex(eq)
        with tabs[1]:
            for p in model.parameters:
                st.markdown(f"- ${p.symbol}$ — {p.label}. {p.tooltip}")
            for symbol, desc in model.extra_variables:
                st.markdown(f"- ${symbol}$ — {desc}")
        with tabs[2]:
            for step in analysis.steps:
                st.latex(step)
        with tabs[3]:
            for a in model.assumptions:
                st.markdown(f"- {a}")
        with tabs[4]:
            for i in model.interpretation:
                st.markdown(f"- {i}")
