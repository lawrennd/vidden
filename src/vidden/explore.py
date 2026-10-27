"""Browser latent explorer for stick-man reconstructions.

Jupyter::

    from vidden.explore import stick_explorer
    stick_explorer()

Standalone (from the repository root)::

    panel serve examples/stick.py --show

Requires HoloViews, Panel, and Bokeh (``vidden[explore]``). GPy is only
needed to load the OSU stick demo (``vidden[gpy]``).
"""

from __future__ import annotations

import numpy as np


def _is_array_mean(value):
    """True when ``X.mean`` is data, not ``ndarray.mean`` / ``Param.mean``."""
    if value is None or callable(value):
        return False
    try:
        np.asarray(value)
    except (TypeError, ValueError):
        return False
    return True


def _latent_values(model):
    """Latent locations: posterior mean when present, ``X`` otherwise.

    Do not use ``hasattr(X, "mean")``: Param/ndarray ``mean`` is a method.
    """
    X = model.X
    mean = getattr(X, "mean", None)
    if _is_array_mean(mean):
        return mean
    return X


def latent_mean_row(model):
    """Writable ``(1, Q)`` row from a GPLVM or BayesianGPLVM."""
    vals = _latent_values(model)
    row = np.array(np.asarray(vals[:1, :]), dtype=float, copy=True)
    return np.atleast_2d(row.reshape(row.shape[0], -1)[:1])


def latent_array(model):
    """``(N, Q)`` latent locations for the scatter plot."""
    return np.array(np.asarray(_latent_values(model)), dtype=float, copy=True)


def reconstruct_mean(model, z):
    """Posterior mean only. Skip predictive variance (not drawn)."""
    z = np.atleast_2d(z)
    raw = getattr(model, "_raw_predict", None)
    if callable(raw):
        mu = raw(z, full_cov=False)[0]
        if getattr(model, "normalizer", None) is not None:
            mu = model.normalizer.inverse_mean(mu)
    else:
        mu = model.predict(z)[0]
    return np.asarray(mu, dtype=float)[0]


def assemble_latent(mean_row, x, y, dim_x, dim_y):
    """Write the two visible axes; leave every other coordinate as it was.

    MATLAB ``lvmVisualise`` starts ``latentPos`` at zeros and
    ``lvmClassVisualise('move')`` only updates ``dim1`` and ``dim2``.
    """
    z = np.array(np.asarray(mean_row), dtype=float, copy=True)
    z = np.atleast_2d(z.reshape(z.shape[0], -1)[:1])
    z[0, int(dim_x)] = float(x)
    z[0, int(dim_y)] = float(y)
    return z


def assemble_latent_nearest(X, x, y, dim_x, dim_y):
    """Unused coordinates from the nearest training embedding (not MATLAB)."""
    X = np.atleast_2d(np.asarray(X, dtype=float))
    dim_x = int(dim_x)
    dim_y = int(dim_y)
    d2 = (X[:, dim_x] - float(x)) ** 2 + (X[:, dim_y] - float(y)) ** 2
    z = np.array(X[int(np.argmin(d2))], dtype=float, copy=True)[None, :]
    z[0, dim_x] = float(x)
    z[0, dim_y] = float(y)
    return z


def y_to_xyz(y):
    """Reshape a stick-man vector into an ``(J, 3)`` point cloud."""
    vec = np.asarray(y, dtype=float).reshape(-1)
    if vec.size % 3 != 0:
        raise ValueError("stick-man vector length must be divisible by 3")
    return vec.reshape(3, vec.size // 3).T


def stick_polylines(xyz, connect):
    """NaN-separated bone polylines from a joint connectivity matrix."""
    xyz = np.asarray(xyz, dtype=float)
    connect = np.asarray(connect)
    i_idx, j_idx = np.nonzero(connect)
    xs, ys, zs = [], [], []
    for i, j in zip(i_idx, j_idx, strict=False):
        xs.extend((xyz[i, 0], xyz[j, 0], np.nan))
        ys.extend((xyz[i, 1], xyz[j, 1], np.nan))
        zs.extend((xyz[i, 2], xyz[j, 2], np.nan))
    return np.asarray(xs), np.asarray(ys), np.asarray(zs)


def matlab_view_project(xyz, azimuth=-37.5, elevation=30.0):
    """Orthographic screen coordinates for MATLAB's default ``view``.

    ``stickVisualise`` is ``plot3`` plus ``axis equal``. The figure is still a
    2-D canvas; ``stickModify`` only ``set``s X/Y/Z on the existing line
    handles. Bokeh does the same with a ColumnDataSource once the 3-D joints
    are projected with MATLAB's default camera (azimuth -37.5, elevation 30).
    """
    xyz = np.asarray(xyz, dtype=float)
    az = np.deg2rad(float(azimuth))
    el = np.deg2rad(float(elevation))
    x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    u = -np.sin(az) * x + np.cos(az) * y
    v = -np.cos(az) * np.sin(el) * x - np.sin(az) * np.sin(el) * y + np.cos(el) * z
    return u, v


def stick_bone_segments(u, v, connect):
    """Per-bone two-point polylines (MATLAB ``line`` handles after the joints)."""
    i_idx, j_idx = np.nonzero(np.asarray(connect))
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    us = [[float(u[i]), float(u[j])] for i, j in zip(i_idx, j_idx, strict=False)]
    vs = [[float(v[i]), float(v[j])] for i, j in zip(i_idx, j_idx, strict=False)]
    return us, vs


def projected_axis_limits(limits_3d, azimuth=-37.5, elevation=30.0):
    """Screen box of the Visualise cube (MATLAB ``axis equal``, then freeze)."""
    lim = np.asarray(limits_3d, dtype=float)
    corners = np.array([[x, y, z] for x in lim[0] for y in lim[1] for z in lim[2]])
    u, v = matlab_view_project(corners, azimuth, elevation)
    return (float(u.min()), float(u.max())), (float(v.min()), float(v.max()))


def cubic_axis_limits(xyz, pad=0.05):
    """Cubic equal-aspect box from the Visualise pose (MATLAB ``axis equal``).

    ``stickModify`` never changes the axes. GPy ``mocap_data_show.modify``
    deletes and redraws artists, which lets matplotlib autoscale.
    """
    xyz = np.asarray(xyz, dtype=float)
    lo = xyz.min(axis=0)
    hi = xyz.max(axis=0)
    centers = 0.5 * (lo + hi)
    half = 0.5 * float(np.max(hi - lo))
    if half <= 0.0:
        half = 1.0
    half *= 1.0 + float(pad)
    return np.column_stack((centers - half, centers + half))


def latent_axis_limits(xy, pad=0.05):
    """2D limits from training latent coordinates, not from the pointer."""
    xy = np.asarray(xy, dtype=float)
    lo = xy.min(axis=0)
    hi = xy.max(axis=0)
    span = hi - lo
    span = np.where(span <= 0.0, 1.0, span)
    margin = span * float(pad)
    return (float(lo[0] - margin[0]), float(hi[0] + margin[0])), (
        float(lo[1] - margin[1]),
        float(hi[1] + margin[1]),
    )


def most_significant_dims(model):
    """Two latent axes a GPLVM would show (ARD input sensitivity)."""
    q = int(getattr(model, "input_dim", latent_array(model).shape[1]))
    getter = getattr(model, "get_most_significant_input_dimensions", None)
    if callable(getter):
        dims = getter()
        dim_x = int(dims[0])
        dim_y = 0 if dims[1] is None else int(dims[1])
    else:
        dim_x, dim_y = 0, 1 if q > 1 else 0
    if dim_y == dim_x and q > 1:
        dim_y = 1 if dim_x == 0 else 0
    return dim_x, dim_y


def input_sensitivity_values(model):
    """Per-dimension kernel sensitivity, as in ``lvm_dimselect``."""
    return np.asarray(model.input_sensitivity(), dtype=float).reshape(-1)


def sensitivity_bar_ylim(sens, pad=0.1):
    """Y-limits for the ARD histogram, recomputed after every update.

    ``lvm_dimselect`` does ``cla()`` then ``bar()``, so matplotlib autoscales.
    HoloViews default ``framewise=False`` keeps the first-frame range. After
    Bayesian GPLVM training the sensitivities drop from O(1) to O(1e-3) and
    the bars vanish against the PCA-initialised axis.
    """
    peak = float(np.max(np.asarray(sens, dtype=float)))
    if not np.isfinite(peak) or peak <= 0.0:
        peak = 1.0
    return (0.0, peak * (1.0 + float(pad)))


def bar_index_from_event_x(x, n_dims):
    """Map a Bokeh bar-plot click to a latent dimension index."""
    if x is None:
        return None
    if isinstance(x, (bytes, str)):
        try:
            x = int(x)
        except ValueError:
            return None
    try:
        idx = int(np.round(float(x)))
    except (TypeError, ValueError):
        return None
    if 0 <= idx < int(n_dims):
        return idx
    return None


def event_has_shift(event):
    """True if a Bokeh ``Tap`` arrived with the shift key down."""
    mods = getattr(event, "modifiers", None)
    if mods is None:
        return False
    if isinstance(mods, dict):
        return bool(mods.get("shift"))
    return bool(getattr(mods, "shift", False))


def disable_bokeh_context_menu(fig):
    """Stop Bokeh's ToolMenu (the 'properties' popup) on right-click."""
    if hasattr(fig, "context_menu"):
        fig.context_menu = None


def menu_item_dimension(item, n_dims):
    """Read a latent index from ``MenuItemClick.item`` (the item label)."""
    if item is None:
        return None
    return bar_index_from_event_x(str(item).rsplit(None, 1)[-1], n_dims)


def install_bar_x_menu(fig, n_dims, on_pick):
    """MATLAB right-button on the histogram, via Bokeh's documented API.

    Bokeh does not emit ``Tap`` for the right mouse button (its pointer
    gestures ignore non-left clicks). Right-click is ``Plot.context_menu``.
    ``MenuItemClick`` is the Python event that selection sends back to the
    server — the same path as a Dropdown. See Bokeh's ``context_menu`` and
    ``bokeh.events.MenuItemClick``.
    """
    from bokeh.events import MenuItemClick
    from bokeh.models import Menu, MenuItem

    items = [MenuItem(label=str(k)) for k in range(int(n_dims))]
    fig.context_menu = Menu(items=items)

    def _on_menu(event):
        on_pick(getattr(event, "item", None))

    fig.on_event(MenuItemClick, _on_menu)


def latent_posterior_density_grid(model, dim_x, dim_y, xlim, ylim, resolution=50, default_vals=None):
    """Posterior density on two latent axes (MATLAB ``lvmScatterPlot``).

    Unused dimensions are held at ``default_vals`` (MATLAB ``defaultVals``,
    GPy ``Xgrid`` zeros). Returns ``-0.5 * sum(log varsigma)`` so low
    posterior variance is bright.
    """
    q = int(model.input_dim)
    d = int(model.output_dim)
    res = int(resolution)
    x1 = np.linspace(float(xlim[0]), float(xlim[1]), res)
    x2 = np.linspace(float(ylim[0]), float(ylim[1]), res)
    xx, yy = np.meshgrid(x1, x2)
    if default_vals is None:
        xtest = np.zeros((xx.size, q))
    else:
        xtest = np.repeat(np.asarray(default_vals, dtype=float).reshape(1, -1), xx.size, axis=0)
    xtest[:, int(dim_x)] = xx.ravel()
    xtest[:, int(dim_y)] = yy.ravel()
    varsigma = np.asarray(model.predict(xtest)[1], dtype=float)
    if varsigma.ndim == 1:
        varsigma = varsigma[:, None]
    clipped = np.clip(varsigma, 1e-12, None)
    if varsigma.shape[1] == 1:
        density = -0.5 * d * np.log(clipped[:, 0])
    else:
        density = -0.5 * np.log(clipped).sum(axis=1)
    return x1, x2, density.reshape(xx.shape)


def largest_training_pose(Y):
    """Training row used to open the stick plot (MATLAB ``lvmVisualise``)."""
    Y = np.atleast_2d(np.asarray(Y, dtype=float))
    return Y[int(np.argmax(np.sum(Y * Y, axis=1)))]


class StickView:
    """MATLAB ``stickVisualise`` / ``stickModify``, as Bokeh data sources.

    ``visualise`` creates the joint scatter and one line glyph per bone, then
    freezes a cubic equal-aspect box from that pose (``axis equal``).
    ``modify`` only writes the existing ColumnDataSources — the Bokeh analog of
    ``set(handle, 'XData', ..., 'YData', ..., 'ZData', ...)``. It does not
    rebuild the figure, restyle a Plotly scene, or touch the axes.

    GPy's ``mocap_data_show.modify`` deletes and redraws artists, which lets
    matplotlib autoscale. Plotly-in-Panel serialises a 3-D scene on every
    mouse move. Neither is what MATLAB did.
    """

    azimuth = -37.5
    elevation = 30.0

    def __init__(self, y, connect):
        from bokeh.models import ColumnDataSource, Range1d
        from bokeh.plotting import figure

        self.connect = np.asarray(connect)
        xyz = y_to_xyz(y)
        self.limits = cubic_axis_limits(xyz)
        xlim, ylim = projected_axis_limits(self.limits, self.azimuth, self.elevation)
        self.joint_source = ColumnDataSource(self._joint_data(xyz))
        self.bone_source = ColumnDataSource(self._bone_data(xyz))
        self.fig = figure(
            width=450,
            height=450,
            match_aspect=True,
            title="reconstruction",
            tools="",
            toolbar_location=None,
            x_range=Range1d(xlim[0], xlim[1], bounds="auto"),
            y_range=Range1d(ylim[0], ylim[1], bounds="auto"),
        )
        self.fig.multi_line(
            "xs",
            "ys",
            source=self.bone_source,
            line_color="#111111",
            line_width=2,
        )
        self.fig.scatter(
            "x",
            "y",
            source=self.joint_source,
            size=10,
            color="#d62728",
            marker="circle",
        )
        self.fig.grid.visible = True
        self.fig.xaxis.axis_label = None
        self.fig.yaxis.axis_label = None
        disable_bokeh_context_menu(self.fig)

    def _joint_data(self, xyz):
        u, v = matlab_view_project(xyz, self.azimuth, self.elevation)
        return {"x": u.tolist(), "y": v.tolist()}

    def _bone_data(self, xyz):
        u, v = matlab_view_project(xyz, self.azimuth, self.elevation)
        xs, ys = stick_bone_segments(u, v, self.connect)
        return {"xs": xs, "ys": ys}

    def modify(self, y):
        xyz = y_to_xyz(y)
        self.joint_source.data = self._joint_data(xyz)
        self.bone_source.data = self._bone_data(xyz)
        return self.fig


def load_stick_model(optimize=False):
    """OSU stick-man Bayesian GPLVM without importing matplotlib.

    Starts from PCA. Call ``optimize_stick_model`` or the explorer's
    Optimize button for Bayesian GPLVM training.
    """
    import GPy
    import pods
    from GPy.models import BayesianGPLVM

    data = pods.datasets.osu_run1()
    Q = 6
    kernel = GPy.kern.RBF(Q, lengthscale=np.repeat(0.5, Q), ARD=True)
    model = BayesianGPLVM(data["Y"], Q, init="PCA", num_inducing=20, kernel=kernel)
    model.data = data
    model.likelihood.variance = 0.001
    if optimize:
        optimize_stick_model(model)
    return model


def optimize_stick_model(model, max_iters=5000, messages=False, bfgs_factor=10):
    """Run BFGS as in ``stick_bgplvm`` (``max_iters=5e3``, ``bfgs_factor=10``)."""
    model.optimize("bfgs", messages=messages, max_iters=int(max_iters), bfgs_factor=bfgs_factor)
    return model


def stick_explorer(model=None, connect=None, optimize=False):
    """Panel app: latent scatter + Bokeh stick + two latent-axis selectors.

    Loads from PCA. Use the Optimize button for Bayesian GPLVM training.
    MATLAB ``lvmClassVisualise`` only updates after a click (``clicked``
    toggles tracking). Hovering onto empty latent space of an untrained GP
    is prior mean zero, which collapses the stick.
    """
    import holoviews as hv
    import panel as pn
    from holoviews import streams

    pn.extension()
    hv.extension("bokeh")

    if model is None:
        model = load_stick_model(optimize=optimize)
    if connect is None:
        connect = model.data["connect"]

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
    stick_view = StickView(largest_training_pose(model.Y), connect)
    stick_pane = pn.pane.Bokeh(stick_view.fig)

    def _send_cursor():
        i, j = int(dim_x.value), int(dim_y.value)
        cursor_pipe.send(np.array([[float(current[0, i]), float(current[0, j])]]))

    def _modify_stick(x, y, announce=False):
        if x is None or y is None:
            return
        z = assemble_latent(current, x, y, dim_x.value, dim_y.value)
        current[:] = z
        stick_view.modify(reconstruct_mean(model, z))
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
            _modify_stick(float(current[0, i]), float(current[0, j]), announce=True)

    def _optimize(_event=None):
        train_btn.loading = True
        train_btn.disabled = True
        tracking["on"] = False
        status.object = f"Optimizing Bayesian GPLVM ({int(max_iters.value)} iters)…"

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
                _modify_stick(event.x, event.y, announce=True)
            else:
                status.object = "Tracking off. Click the scatter to track again."

        def on_move(event):
            if tracking["on"]:
                _modify_stick(event.x, event.y)

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
        pts = hv.Points(data, ["x", "y"]).opts(
            size=7,
            color="#4c78a8",
            xlim=xlim,
            ylim=ylim,
            framewise=False,
            default_tools=plot_tools,
            tools=plot_tools,
        )
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

    return pn.Column(
        pn.pane.Markdown(
            "### Stick man latent explorer\n"
            "Starts from PCA. Optimize trains the Bayesian GPLVM. The latent "
            "position starts at 0 (MATLAB ``latentPos``). A click only writes "
            "the two visible axes; the rest stay where you left them. Switch "
            "the bar axes to set the other coordinates. Left-click a bar for "
            "red (y). Right-click the histogram and choose a dimension for "
            "green (x); double-click a bar also sets green."
        ),
        pn.Row(dim_x, dim_y, train_btn, max_iters),
        pn.Row(pn.Column(scatter, bars_dmap), stick_pane),
        status,
    )


