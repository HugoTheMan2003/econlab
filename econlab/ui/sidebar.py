"""Left sidebar: logo, search and a nested category > chapter > model tree.

Streamlit forbids nested expanders, so open/closed state is kept in
st.session_state["nav_open"] and toggled with buttons.
"""
import streamlit as st

LOGO = '<div class="el-logo"><span class="el-mark">∑</span> EconLab</div>'


def _toggle(path: str) -> None:
    st.session_state["nav_open"].symmetric_difference_update({path})


def _select(model_id: str) -> None:
    st.session_state["selected_model"] = model_id


def _indent(level: int):
    return st.container() if level == 0 else st.columns([level, 10])[1]


def _model_button(model, path: str, level: int) -> None:
    selected = st.session_state["selected_model"] == model.id
    with _indent(level):
        st.button(model.name, key=f"nav:model:{path}:{model.id}", on_click=_select,
                  args=(model.id,), type="primary" if selected else "secondary", width="stretch")


def _init_state(registry) -> None:
    ss = st.session_state
    ss.setdefault("selected_model", registry.default_model_id())
    if "nav_open" not in ss:
        m = registry.get(ss["selected_model"])
        ss["nav_open"] = {m.category, f"{m.category}/{m.chapter}"}


def render(registry):
    _init_state(registry)
    with st.sidebar:
        st.markdown(LOGO, unsafe_allow_html=True)
        query = st.text_input("Søg", placeholder="Søg efter model …",
                              label_visibility="collapsed", key="nav_query")
        if query.strip():
            hits = registry.search(query)
            if not hits:
                st.caption("Ingen modeller fundet.")
            for m in hits:
                _model_button(m, f"search/{m.chapter}", 0)
        else:
            open_ = st.session_state["nav_open"]
            for cat, chapters in registry.tree().items():
                cat_open = cat in open_
                st.button(f"{'▾' if cat_open else '▸'} {cat}", key=f"nav:cat:{cat}",
                          on_click=_toggle, args=(cat,), type="tertiary", width="stretch")
                if not cat_open:
                    continue
                for ch, models in chapters.items():
                    path = f"{cat}/{ch}"
                    ch_open = path in open_
                    with _indent(1):
                        st.button(f"{'▾' if ch_open else '▸'} {ch}", key=f"nav:ch:{path}",
                                  on_click=_toggle, args=(path,), type="tertiary", width="stretch")
                    if not ch_open:
                        continue
                    if not models:
                        with _indent(2):
                            st.caption("Kommer snart")
                    for m in models:
                        _model_button(m, path, 2)
    return registry.get(st.session_state["selected_model"])
