"""EconLab entry point. Run with:  streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="EconLab", page_icon="∑", layout="wide",
                   initial_sidebar_state="expanded")

from econlab.engine import ParameterError  # noqa: E402
from econlab.models import load_models  # noqa: E402
from econlab.registry import REGISTRY  # noqa: E402
from econlab.ui import controls, info_panel, sidebar, workspace  # noqa: E402

CSS = """
<style>
.block-container {padding-top: 1.5rem; max-width: 100%;}
section[data-testid="stSidebar"] button {justify-content: flex-start; text-align: left;}
.el-logo {font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: .5rem;}
.el-mark {color: #2563eb;}
</style>
"""

load_models()                         # 1. models register themselves
model = sidebar.render(REGISTRY)      # 2. sidebar is built from the registry
st.markdown(CSS, unsafe_allow_html=True)

graph_col, param_col = st.columns([3.6, 1.4], gap="large")
with param_col:                       # 3. controls are built from model.parameters
    values, options, baseline = controls.render(model)

analysis = fig = error = None
try:                                  # 4. engine calculates, figure is built
    analysis = model.analyse(values, baseline)
    fig = model.build_figure(values, baseline, options)
except ParameterError as exc:
    error = str(exc)

with param_col:
    if analysis:
        controls.render_results(analysis)
with graph_col:
    workspace.render_header(model)
    workspace.render_graph(fig, error)
if analysis:
    info_panel.render(model, analysis)
