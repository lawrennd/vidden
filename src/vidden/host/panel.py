"""Panel host for latent explorers.

``latent_explorer(model, view)`` returns a layout. It does not call
``servable()``. Example scripts under ``examples/`` are the serve entries.

Pointer events come from Bokeh ``tap`` / ``mousemove`` on ``plot.state``,
not HoloViews ``PointerXY``. Click toggles tracking (MATLAB
``lvmClassVisualise``). ``Tap`` is left-click; right-click on the ARD
histogram is ``Plot.context_menu`` / ``MenuItemClick``. Double-click
sets the green (x) axis.

The reconstruction pane is a view with ``.fig`` and ``modify(y)``. Init
once, then only write data sources.
"""

from __future__ import annotations

import numpy as np

from vidden.demos import load_face_model, load_oil_model, load_stick_model, optimize_stick_model
from vidden.host.events import (
    bar_index_from_event_x,
    disable_bokeh_context_menu,
    event_has_shift,
    install_bar_x_menu,
    menu_item_dimension,
)
from vidden.models import (
    assemble_latent,
    input_sensitivity_values,
    latent_array,
    latent_axis_limits,
    latent_posterior_density_grid,
    most_significant_dims,
    reconstruct_mean,
    sensitivity_bar_ylim,
)
from vidden.views.stick import StickView, largest_training_pose

_DEFAULT_HEADING = (
    "Starts from PCA. Optimize trains the model. The latent position "
    "starts at 0 (MATLAB ``latentPos``). A click only writes the two "
    "visible axes; the rest stay where you left them. Switch the bar "
    "axes to set the other coordinates. Left-click a bar for red (y). "
    "Right-click the histogram and choose a dimension for green (x); "
    "double-click a bar also sets green."
)


def latent_training_points(xy, labels=None):
    """Latent scatter Points. Colour by ``labels`` when length matches."""
    import holoviews as hv

    xy = np.asarray(xy, dtype=float)
    if xy.ndim != 2 or xy.shape[1] < 2:
        xy = np.atleast_2d(xy)
    xy = xy[:, :2]
    if labels is not None:
        lab = np.asarray(labels).reshape(-1)
        if lab.shape[0] == xy.shape[0]:
            return hv.Points(
                {"x": xy[:, 0], "y": xy[:, 1], "label": lab},
                ["x", "y"],
                "label",
            )
    return hv.Points(xy, ["x", "y"])


def latent_explorer(model, view, *, heading=None, optimize=False):
    """Panel layout: latent scatter + reconstruction view + axis selectors.

    ``view`` must provide ``.fig`` and ``modify(y)``. Loads from whatever
    initialisation the caller used. Use the Optimize button for training.
    MATLAB ``lvmClassVisualise`` only updates after a click. Hovering onto
    empty latent space of an untrained GP is prior mean zero.
    """
    import holoviews as hv
    import panel as pn
    from holoviews import streams

    pn.extension()
    hv.extension("bokeh")

    if optimize:
        optimize_stick_model(model)

    X = latent_array(model)
    Q = X.shape[1]
    current = np.zeros((1, Q))
    start_x, start_y = most_significant_dims(model)
    dims = list(range(Q))
    dim_x = pn.widgets.Select(label="x axis (green)", options=dims, value=start_x)
    dim_y = pn.widgets.Select(label="y axis (red)", options=dims, value=start_y)
    train_btn = pn.widgets.Button(label="Optimize Bayesian GPLVM", color="primary")
    max_iters = pn.widgets.IntInput(label="max iters", value=5000, start=1, end=20000, width=120)
    status = pn.pane.Markdown(
        "PCA initialisation. Click Optimize to train. Then click the grey plot "
        "to track; left-click a bar for red (y); right-click and pick a "
        "dimension for green (x)."
    )
    tracking = {"on": False}

    latent_pipe = streams.Pipe(data=np.column_stack((X[:, start_x], X[:, start_y])))
    bar_pipe = streams.Pipe(data=0)
    cursor_pipe = streams.Pipe(data=np.array([[0.0, 0.0]]))
    bar_tick = {"n": 0}
    view_pane = pn.pane.Bokeh(view.fig)

    def _send_cursor():
        i, j = int(dim_x.value), int(dim_y.value)
        cursor_pipe.send(np.array([[float(current[0, i]), float(current[0, j])]]))

    def _modify_view(x, y, announce=False):
        if x is None or y is None:
            return
        z = assemble_latent(current, x, y, dim_x.value, dim_y.value)
        current[:] = z
        view.modify(reconstruct_mean(model, z))
        _send_cursor()
        if announce:
            prefix = "tracking" if tracking["on"] else "frozen"
            held = ", ".join(f"{k}={current[0, k]:.2f}" for k in range(Q))
            status.object = f"{prefix}: [{held}]"

    def _set_dim(widget, idx):
        idx = int(idx)
        if widget.value != idx:
            widget.value = idx

    def _refresh_views():
        X[:, :] = latent_array(model)
        current[:, :] = 0.0
        sx, sy = most_significant_dims(model)
        if dim_x.value != sx:
            dim_x.value = sx
        if dim_y.value != sy:
            dim_y.value = sy
        i, j = int(dim_x.value), int(dim_y.value)
        latent_pipe.send(np.column_stack((X[:, i], X[:, j])))
        _send_bars()
        _send_cursor()

    def _send_bars():
        bar_tick["n"] += 1
        bar_pipe.send(bar_tick["n"])

    def _on_dims(*_events):
        i, j = int(dim_x.value), int(dim_y.value)
        latent_pipe.send(np.column_stack((X[:, i], X[:, j])))
        _send_bars()
        _send_cursor()
        if tracking["on"]:
            _modify_view(float(current[0, i]), float(current[0, j]), announce=True)

    def _optimize(_event=None):
        train_btn.loading = True
        train_btn.disabled = True
        tracking["on"] = False
        status.object = f"Optimizing ({int(max_iters.value)} iters)…"

        def _run():
            try:
                optimize_stick_model(model, max_iters=int(max_iters.value))
                _refresh_views()
                ll = float(np.asarray(model.log_likelihood()).reshape(-1)[0])
                status.object = (
                    f"Optimization done (log lik {ll:.1f}). Latent position "
                    "is back at 0. Click to set the two visible axes; switch "
                    "bars to leave those values and set the others."
                )
            except Exception as exc:
                status.object = f"Optimization failed: {exc}"
            finally:
                train_btn.loading = False
                train_btn.disabled = False

        doc = getattr(pn.state, "curdoc", None)
        if doc is not None:
            doc.add_next_tick_callback(_run)
        else:
            _run()

    def _attach_once(fig, key):
        flag = f"_vidden_{key}"
        if getattr(fig, flag, False):
            return False
        setattr(fig, flag, True)
        return True

    def _disable_pan(fig):
        toolbar = getattr(fig, "toolbar", None)
        if toolbar is not None:
            toolbar.active_drag = None
            toolbar.active_scroll = None

    def _apply_bar_x(x, widget):
        idx = bar_index_from_event_x(x, Q)
        if idx is None:
            return
        _set_dim(widget, idx)
        which = "green (x)" if widget is dim_x else "red (y)"
        status.object = f"{which} axis → {idx}"

    def _latent_hook(plot, element):
        fig = plot.state
        _disable_pan(fig)
        disable_bokeh_context_menu(fig)
        if not _attach_once(fig, "latent_events"):
            return

        def on_tap(event):
            tracking["on"] = not tracking["on"]
            if tracking["on"]:
                _modify_view(event.x, event.y, announce=True)
            else:
                status.object = "Tracking off. Click the scatter to track again."

        def on_move(event):
            if tracking["on"]:
                _modify_view(event.x, event.y)

        fig.on_event("tap", on_tap)
        fig.on_event("mousemove", on_move)

    def _bar_hook(plot, element):
        fig = plot.state
        _disable_pan(fig)
        if not _attach_once(fig, "bar_events"):
            return
        install_bar_x_menu(fig, Q, lambda item: _apply_bar_x(menu_item_dimension(item, Q), dim_x))

        def on_tap(event):
            if event_has_shift(event):
                _apply_bar_x(event.x, dim_x)
            else:
                _apply_bar_x(event.x, dim_y)

        def on_doubletap(event):
            _apply_bar_x(event.x, dim_x)

        fig.on_event("tap", on_tap)
        fig.on_event("doubletap", on_doubletap)

    plot_tools = ["tap", "reset", "save"]

    def _sensitivity_bars(data=None):
        sens = input_sensitivity_values(model)
        i, j = int(dim_x.value), int(dim_y.value)
        color = [("#2ca02c" if k == i else "#d62728" if k == j else "#4c78a8") for k in range(Q)]
        ylim = sensitivity_bar_ylim(sens)
        return hv.Bars(
            {"dimension": list(range(Q)), "sensitivity": list(sens), "c": color},
            ["dimension"],
            ["sensitivity", "c"],
        ).opts(
            color="c",
            cmap="Category10",
            width=420,
            height=160,
            xlabel="latent dimension",
            ylabel="input sensitivity",
            ylim=ylim,
            xlim=(-0.5, Q - 0.5),
            framewise=True,
            shared_axes=False,
            show_legend=False,
            default_tools=plot_tools,
            tools=plot_tools,
            active_tools=["tap"],
            hooks=[_bar_hook],
        )

    def _latent_view(data):
        data = np.asarray(data)
        xlim, ylim = latent_axis_limits(data)
        i, j = int(dim_x.value), int(dim_y.value)
        x1, x2, density = latent_posterior_density_grid(
            model, i, j, xlim, ylim, default_vals=current[0]
        )
        img = hv.Image((x1, x2, density), ["x", "y"], "density").opts(
            cmap="gray",
            colorbar=False,
            xlim=xlim,
            ylim=ylim,
            framewise=False,
            default_tools=plot_tools,
            tools=plot_tools,
        )
        point_opts = dict(
            size=7,
            xlim=xlim,
            ylim=ylim,
            framewise=False,
            default_tools=plot_tools,
            tools=plot_tools,
        )
        pts = latent_training_points(data, getattr(model, "data_labels", None))
        if "label" in pts.vdims:
            pts = pts.opts(color="label", cmap="Category10", show_legend=False, **point_opts)
        else:
            pts = pts.opts(color="#4c78a8", **point_opts)
        return (img * pts).opts(
            width=420,
            height=420,
            xlim=xlim,
            ylim=ylim,
            xlabel=f"latent {i}",
            ylabel=f"latent {j}",
            framewise=False,
            default_tools=plot_tools,
            tools=plot_tools,
            active_tools=["tap"],
            toolbar=None,
        )

    def _cross(data):
        xy = np.asarray(data, dtype=float).reshape(1, 2)
        return hv.Points(xy, ["x", "y"]).opts(
            marker="x",
            color="red",
            size=18,
            line_width=3,
            default_tools=plot_tools,
            tools=plot_tools,
            show_legend=False,
            framewise=False,
        )

    latent_dmap = hv.DynamicMap(_latent_view, streams=[latent_pipe])
    cursor_dmap = hv.DynamicMap(_cross, streams=[cursor_pipe])
    scatter = (latent_dmap * cursor_dmap).opts(
        default_tools=plot_tools,
        tools=plot_tools,
        active_tools=["tap"],
        toolbar=None,
        show_legend=False,
        hooks=[_latent_hook],
    )
    bars_dmap = hv.DynamicMap(_sensitivity_bars, streams=[bar_pipe])
    dim_x.param.watch(_on_dims, "value")
    dim_y.param.watch(_on_dims, "value")
    train_btn.on_click(_optimize)

    if heading is None:
        heading = "### Latent explorer\n" + _DEFAULT_HEADING

    return pn.Column(
        pn.pane.Markdown(heading),
        pn.Row(dim_x, dim_y, train_btn, max_iters),
        pn.Row(pn.Column(scatter, bars_dmap), view_pane),
        status,
    )


def stick_explorer(model=None, connect=None, optimize=False):
    """Stick-man explorer: ``StickView`` on ``latent_explorer``."""
    if model is None:
        model = load_stick_model(optimize=optimize)
    if connect is None:
        connect = model.data["connect"]
    view = StickView(largest_training_pose(model.Y), connect)
    return latent_explorer(
        model,
        view,
        heading="### Stick man latent explorer\n" + _DEFAULT_HEADING,
    )


def oil_explorer(model=None, optimize=False):
    """Oil-flow explorer: ``VectorView`` on ``latent_explorer``.

    Default data is ``pods.datasets.oil()`` (12-D observations, three
    labels), a 7-D Bayesian GPLVM as in ``bgplvm_oil``.
    """
    from vidden.views.stick import largest_training_pose
    from vidden.views.vector import VectorView, vector_y_limits

    if model is None:
        model = load_oil_model(optimize=optimize)
    Y = np.asarray(model.Y, dtype=float)
    view = VectorView(largest_training_pose(Y), limits=vector_y_limits(Y))
    return latent_explorer(
        model,
        view,
        heading=(
            "### Oil-flow latent explorer\n"
            "12-D oil as a line of index against value. Seven latent "
            "axes; switch bars after Optimize. Labels colour the scatter "
            "when the model carries ``data_labels``.\n" + _DEFAULT_HEADING
        ),
    )


def doodle_explorer(model=None, strokes=None, limits=None, optimize=False):
    """Doodle explorer: ``DoodleView`` on ``latent_explorer``.

    Default data is generated cartoon faces with known smile and
    roundness, not a user-drawn family.
    """
    from vidden.doodle import DOODLE_LIMITS, FACE_STROKES
    from vidden.views.doodle import DoodleView

    if model is None:
        model = load_face_model(optimize=optimize)
    if strokes is None:
        strokes = getattr(model, "doodle_strokes", FACE_STROKES)
    if limits is None:
        limits = DOODLE_LIMITS
    view = DoodleView(largest_training_pose(model.Y), strokes, limits=limits)
    return latent_explorer(
        model,
        view,
        heading=(
            "### Latent doodle space\n"
            "Generated faces on a smile × roundness grid, as a 2-D "
            "Bayesian GPLVM (lengthscale 0.5, like the stick man). "
            "Optimize, then click the grey plot to synthesize. This is "
            "the paper's click-to-generate demo, not an interpolation "
            "grid.\n" + _DEFAULT_HEADING
        ),
    )
