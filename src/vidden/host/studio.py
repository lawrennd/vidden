"""Browser drawing studio for a doodle family.

Uses Bokeh ``FreehandDrawTool``. Correspondence and JSON I/O are imported
from ``vidden.doodle``; this host does not match strokes or parse files
itself beyond calling the store.
"""

from __future__ import annotations

import numpy as np

from vidden.doodle.geometry import DOODLE_LIMITS
from vidden.doodle.store import (
    family_dir,
    family_slug,
    load_doodle_dir,
    save_family,
)
from vidden.views.doodle import raw_polylines, stroke_figure


def _strokes_from_source(source):
    xs = list(source.data.get("xs", []))
    ys = list(source.data.get("ys", []))
    doodle = []
    for x, y in zip(xs, ys, strict=True):
        if len(x) < 2:
            continue
        doodle.append(np.column_stack((np.asarray(x, dtype=float), np.asarray(y, dtype=float))))
    return doodle


def _empty_draw_data():
    return {"xs": [], "ys": []}


def _ghost_data(doodle):
    if not doodle:
        return {"xs": [], "ys": []}
    xs, ys = raw_polylines(doodle)
    return {"xs": xs, "ys": ys}


def _draw_pad(limits, width=450, height=450):
    from bokeh.models import ColumnDataSource, FreehandDrawTool, Range1d
    from bokeh.plotting import figure

    xmin, xmax, ymin, ymax = (float(v) for v in limits)
    ghost = ColumnDataSource({"xs": [], "ys": []})
    draw = ColumnDataSource(_empty_draw_data())
    fig = figure(
        width=width,
        height=height,
        match_aspect=True,
        title="drag to draw",
        tools="",
        toolbar_location=None,
        x_range=Range1d(xmin, xmax, bounds="auto"),
        y_range=Range1d(ymin, ymax, bounds="auto"),
    )
    fig.multi_line("xs", "ys", source=ghost, line_color="#b8b8b8", line_width=2.2, line_alpha=0.55)
    renderer = fig.multi_line("xs", "ys", source=draw, line_color="#111111", line_width=2)
    tool = FreehandDrawTool(renderers=[renderer], num_objects=64)
    fig.add_tools(tool)
    fig.toolbar.active_drag = tool
    if hasattr(fig, "context_menu"):
        fig.context_menu = None
    return fig, draw, ghost


def doodle_studio(outdir="doodles", family="faces", limits=DOODLE_LIMITS):
    """User studio: draw, grey selected reference below, save and load JSON."""
    import panel as pn

    pn.extension()
    slug = family_slug(family)
    state = {"doodles": [], "selected": None, "family": slug, "status": "Draw a stroke, then Keep."}
    dest = family_dir(outdir, slug)
    json_path = dest / "doodles.json"
    if json_path.is_file():
        loaded, _pngs, slug = load_doodle_dir(outdir, family=slug)
        state["doodles"] = loaded
        state["family"] = slug
        if loaded:
            state["selected"] = len(loaded) - 1
            state["status"] = f"Loaded {len(loaded)} doodles from {slug}."

    fig, draw, ghost = _draw_pad(limits)
    preview_fig, preview_src = stroke_figure([], colors=["#b8b8b8"], limits=limits, title="selected (grey)", width=450, height=220)
    picker = pn.widgets.Select(name="Gallery", options=[], value=None)
    family_box = pn.widgets.TextInput(name="Family", value=state["family"])
    status = pn.pane.Markdown(state["status"])

    def _refresh_picker():
        n = len(state["doodles"])
        picker.options = [f"{i}" for i in range(n)]
        if state["selected"] is not None and n:
            picker.value = f"{state['selected']}"
        elif n:
            picker.value = f"{n - 1}"
        else:
            picker.value = None

    def _show_selected():
        idx = state["selected"]
        doodle = state["doodles"][idx] if idx is not None and 0 <= idx < len(state["doodles"]) else []
        ghost.data = _ghost_data(doodle)
        xs, ys = raw_polylines(doodle)
        preview_src.data = {"xs": xs, "ys": ys, "colors": ["#b8b8b8"] * len(xs)}

    def _keep(_event=None):
        doodle = _strokes_from_source(draw)
        if not doodle:
            status.object = "Nothing to keep."
            return
        state["doodles"].append(doodle)
        state["selected"] = len(state["doodles"]) - 1
        draw.data = _empty_draw_data()
        _refresh_picker()
        _show_selected()
        status.object = f"Kept doodle {state['selected']} ({len(doodle)} strokes)."

    def _undo(_event=None):
        xs = list(draw.data.get("xs", []))
        ys = list(draw.data.get("ys", []))
        if not xs:
            status.object = "No stroke to undo."
            return
        xs.pop()
        ys.pop()
        draw.data = {"xs": xs, "ys": ys}
        status.object = "Undid last stroke."

    def _clear(_event=None):
        draw.data = _empty_draw_data()
        status.object = "Cleared the pad. Grey reference stays."

    def _save(_event=None):
        state["family"] = family_slug(family_box.value)
        path = save_family(family_dir(outdir, state["family"]), state["doodles"], family=state["family"])
        status.object = f"Saved {len(state['doodles'])} doodles to {path}."

    def _load(_event=None):
        state["family"] = family_slug(family_box.value)
        try:
            loaded, _pngs, slug = load_doodle_dir(outdir, family=state["family"])
        except FileNotFoundError as err:
            status.object = str(err)
            return
        state["doodles"] = loaded
        state["family"] = slug
        family_box.value = slug
        state["selected"] = len(loaded) - 1 if loaded else None
        draw.data = _empty_draw_data()
        _refresh_picker()
        _show_selected()
        status.object = f"Loaded {len(loaded)} doodles from {slug}."

    def _on_pick(event):
        if event.new is None or event.new == "":
            return
        state["selected"] = int(event.new)
        _show_selected()

    picker.param.watch(_on_pick, "value")
    keep = pn.widgets.Button(name="Keep", button_type="primary")
    undo = pn.widgets.Button(name="Undo")
    clear = pn.widgets.Button(name="Clear")
    save = pn.widgets.Button(name="Save")
    load = pn.widgets.Button(name="Load")
    keep.on_click(_keep)
    undo.on_click(_undo)
    clear.on_click(_clear)
    save.on_click(_save)
    load.on_click(_load)
    _refresh_picker()
    _show_selected()

    intro = pn.pane.Markdown(
        "### Doodle studio\n"
        "Drag on the pad to draw a stroke. Keep stores it. Click the gallery "
        "to grey that doodle below (and as a faint ghost on the pad). Save writes "
        f"`{outdir}/<family>/doodles.json`."
    )
    buttons = pn.Row(keep, undo, clear, save, load)
    layout = pn.Column(
        intro,
        pn.Row(fig, pn.Column(family_box, picker, buttons, status)),
        preview_fig,
    )
    layout._vidden_draw = draw
    layout._vidden_keep = keep
    layout._vidden_save = save
    layout._vidden_load = load
    layout._vidden_state = state
    return layout
