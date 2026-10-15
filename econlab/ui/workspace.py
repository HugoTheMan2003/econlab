"""Central workspace: model heading and the interactive Plotly graph."""
import streamlit as st

PLOT_CONFIG = {
    "displaylogo": False,
    "scrollZoom": True,  # mouse-wheel zoom; drag = pan
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "filename": "econlab", "scale": 2},
}


def render_header(model) -> None:
    st.caption(f"{model.category} › {model.chapter}")
    st.subheader(model.name)
    st.write(model.description)


def render_graph(fig, error: str | None) -> None:
    if error:
        st.error(error)
        return
    st.plotly_chart(fig, config=PLOT_CONFIG, width="stretch")
