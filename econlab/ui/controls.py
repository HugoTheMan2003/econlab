"""Right sidebar: parameter sliders + number inputs (kept in sync), display
options, baseline buttons and derived values. Everything is generated from the
selected ModelDefinition."""
import streamlit as st


def _k(model, name: str, kind: str) -> str:
    return f"{model.id}:{name}:{kind}"


def _sync(src: str, dst: str) -> None:
    st.session_state[dst] = st.session_state[src]


def _set_params(model, values: dict) -> None:
    for p in model.parameters:
        for kind in ("slider", "num"):
            st.session_state[_k(model, p.key, kind)] = float(values[p.key])


def _reset(model) -> None:
    _set_params(model, {p.key: p.default for p in model.parameters})


def _save_baseline(model, values: dict) -> None:
    st.session_state[f"{model.id}:baseline"] = dict(values)


def _restore_baseline(model) -> None:
    _set_params(model, st.session_state[f"{model.id}:baseline"])


def _clear_baseline(model) -> None:
    st.session_state.pop(f"{model.id}:baseline", None)


def _parameter_row(model, p) -> None:
    sk, nk = _k(model, p.key, "slider"), _k(model, p.key, "num")
    help_text = f"{p.tooltip}\n\nGyldigt interval: {p.min:g} – {p.max:g}. Standard: {p.default:g}."
    st.markdown(f"${p.symbol}$ · {p.label}", help=help_text)
    c1, c2 = st.columns([3, 2])
    c1.slider(p.label, min_value=p.min, max_value=p.max, step=p.step, key=sk,
              on_change=_sync, args=(sk, nk), label_visibility="collapsed")
    c2.number_input(p.label, min_value=p.min, max_value=p.max, step=p.step, key=nk,
                    format="%.2f", on_change=_sync, args=(nk, sk), label_visibility="collapsed")


def render(model):
    ss = st.session_state
    for p in model.parameters:
        for kind in ("slider", "num"):
            ss.setdefault(_k(model, p.key, kind), float(p.default))
    for o in model.options:
        ss.setdefault(_k(model, o.key, "opt"), o.default)

    groups: dict[str, list] = {}
    for p in model.parameters:
        groups.setdefault(p.group, []).append(p)
    for group, params in groups.items():
        st.caption(group.upper())
        for p in params:
            _parameter_row(model, p)
    st.button("Nulstil parametre", on_click=_reset, args=(model,), width="stretch")
    values = {p.key: float(ss[_k(model, p.key, "slider")]) for p in model.parameters}

    st.caption("VISNING")
    options = {o.key: st.checkbox(o.label, key=_k(model, o.key, "opt")) for o in model.options}

    st.caption("SCENARIE")
    bkey = f"{model.id}:baseline"
    c1, c2 = st.columns(2)
    c1.button("Gem baseline", on_click=_save_baseline, args=(model, values), width="stretch")
    c2.button("Fjern", on_click=_clear_baseline, args=(model,), width="stretch",
              disabled=bkey not in ss)
    if bkey in ss:
        st.button("Gendan baseline", on_click=_restore_baseline, args=(model,), width="stretch")
    return values, options, ss.get(bkey)


def render_results(analysis) -> None:
    st.divider()
    st.caption("BEREGNEDE VÆRDIER")
    for d in analysis.derived:
        delta = None
        if d.baseline is not None and abs(d.value - d.baseline) > 1e-12:
            delta = f"{d.value - d.baseline:+.{d.decimals}f} ift. baseline"
        st.metric(d.label, f"{d.value:.{d.decimals}f}", delta=delta, delta_color="off")
    if analysis.change_note:
        st.info(analysis.change_note)
