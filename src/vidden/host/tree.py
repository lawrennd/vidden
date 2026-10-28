"""Hierarchical GP-LVM host: a tree of 2-D scatters plus one StickView.

This is not ``latent_explorer``. Parent predict writes child latent
positions; only leaves call ``modify`` on a composite skeleton.
"""

from __future__ import annotations

import numpy as np

from vidden.host.events import disable_bokeh_context_menu
from vidden.host.scatter import latent_training_points
from vidden.models import latent_array, latent_axis_limits, latent_posterior_density_grid
from vidden.tree import cascade, figure_pose, make_synthetic_hierarchy
from vidden.views.stick import StickView, largest_training_pose


_HEADING = (
    "### Hierarchical GP-LVM\n"
    "Top plot is the skeleton space (Lawrence and Moore, ICML 2007). "
    "Its output is abdomen, legs, and upper body; those split into "
    "the limb leaves. Leaves reconstruct CMU subject 35 walk and run "
    "(pods) onto one Acclaim skeleton. Click skeleton, then move. "
    "Click a limb plot to move only that branch."
)


def _leaf_indices(hierarchy):
    return [i for i, node in enumerate(hierarchy.nodes) if not node.children]


def _composite_from_leaves(hierarchy, leaf_ys):
    return figure_pose(hierarchy, leaf_ys)


def _training_composite(hierarchy):
    leaves = _leaf_indices(hierarchy)
    rows = []
    n = min(len(np.asarray(hierarchy.nodes[i].model.Y)) for i in leaves)
    for k in range(n):
        leaf_ys = {i: np.asarray(hierarchy.nodes[i].model.Y[k], dtype=float) for i in leaves}
        y, _ = _composite_from_leaves(hierarchy, leaf_ys)
        rows.append(y)
    return np.vstack(rows)


def _set_cursor(source, xy):
    if isinstance(source, dict):
        source = source.get("source")
    if source is None:
        return
    xy = np.asarray(xy, dtype=float).reshape(-1)
    source.data = {"x": [float(xy[0])], "y": [float(xy[1])]}


def _node_overlay(model, cursor_xy, title, on_pointer, *, width=320, height=280):
    """HoloViews overlay in the Panel layout; cursor is a Bokeh source.

    Pre-rendering with ``hv.render`` and wrapping each node in
    ``pn.pane.Bokeh`` put the stick figure in a different Bokeh document
    than the pointer. ``modify`` wrote sources the browser never saw.
    Keep the overlay as HoloViews (as ``latent_explorer`` does) so Panel
    owns one document. Do not rebuild the density on mousemove.
    """
    import holoviews as hv
    from bokeh.models import ColumnDataSource

    X = latent_array(model)[:, :2]
    xlim, ylim = latent_axis_limits(X)
    plot_tools = ["tap", "reset", "save"]
    x1, x2, density = latent_posterior_density_grid(
        model, 0, 1, xlim, ylim, resolution=25, default_vals=np.zeros(model.input_dim)
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
    pts = latent_training_points(X, getattr(model, "data_labels", None))
    if "label" in pts.vdims:
        pts = pts.opts(color="label", cmap="Category10", show_legend=False, **point_opts)
    else:
        pts = pts.opts(color="#4c78a8", **point_opts)
    holder = {}
    tracking = {"on": False}

    def _hook(plot, element):
        fig = plot.state
        toolbar = getattr(fig, "toolbar", None)
        if toolbar is not None:
            toolbar.active_drag = None
            toolbar.active_scroll = None
        disable_bokeh_context_menu(fig)
        flag = "_vidden_tree_events"
        if getattr(fig, flag, False):
            return
        setattr(fig, flag, True)
        xy = np.asarray(cursor_xy, dtype=float).reshape(1, 2)
        source = ColumnDataSource(data={"x": [float(xy[0, 0])], "y": [float(xy[0, 1])]})
        fig.scatter(
            "x",
            "y",
            source=source,
            marker="x",
            size=16,
            color="red",
            line_width=3,
        )
        holder["source"] = source

        def on_tap(event):
            tracking["on"] = not tracking["on"]
            if tracking["on"]:
                on_pointer(event.x, event.y, announce=True)
            else:
                on_pointer(None, None, announce=True, tracking_on=False)

        def on_move(event):
            if tracking["on"]:
                on_pointer(event.x, event.y)

        fig.on_event("tap", on_tap)
        fig.on_event("mousemove", on_move)

    overlay = (img * pts).opts(
        width=int(width),
        height=int(height),
        xlim=xlim,
        ylim=ylim,
        xlabel="",
        ylabel="",
        title=title,
        framewise=False,
        default_tools=plot_tools,
        tools=plot_tools,
        active_tools=["tap"],
        toolbar=None,
        show_legend=False,
        hooks=[_hook],
    )
    return overlay, holder


def tree_explorer(hierarchy=None):
    """Panel layout: node scatters by depth, one composite ``StickView``.

    Creating the explorer does not call ``servable()``.
    """
    import holoviews as hv
    import panel as pn

    pn.extension()
    hv.extension("bokeh")

    if hierarchy is None:
        try:
            from vidden.demos import load_walk_run_tree

            hierarchy = load_walk_run_tree()
        except ImportError:
            hierarchy = make_synthetic_hierarchy()

    leaves = _leaf_indices(hierarchy)
    root = int(hierarchy.roots[0])
    x0 = float(hierarchy.nodes[root].model.X[0, 0])
    y0 = float(hierarchy.nodes[root].model.X[0, 1])
    start_pos, leaf_ys = cascade(hierarchy, root, x0, y0)
    packed0, connect = _composite_from_leaves(hierarchy, leaf_ys)
    Y_train = _training_composite(hierarchy)
    view = StickView(largest_training_pose(np.vstack([Y_train, packed0[None, :]])), connect)
    view.modify(packed0)
    view_pane = pn.pane.Bokeh(view.fig)
    root_name = hierarchy.nodes[root].name
    status = pn.pane.Markdown(
        f"Click {root_name} to track. Limb leaves reconstruct one skeleton."
    )
    plot_w, plot_h = (220, 190) if len(hierarchy.nodes) > 4 else (320, 280)
    cursors = {}

    def _apply(index, x, y, *, announce=False, tracking_on=True):
        if not tracking_on:
            if announce:
                status.object = "Tracking off. Click a plot to track again."
            return
        if x is None or y is None:
            return
        positions, new_leaves = cascade(hierarchy, index, x, y)
        leaf_ys.update(new_leaves)
        packed, _ = _composite_from_leaves(hierarchy, leaf_ys)
        view.modify(packed)
        for i, xy in positions.items():
            if i in cursors:
                _set_cursor(cursors[i], xy)
        if announce:
            held = ", ".join(
                f"{hierarchy.nodes[i].name}=({xy[0]:.2f},{xy[1]:.2f})"
                for i, xy in sorted(positions.items())
            )
            status.object = f"node {hierarchy.nodes[index].name}: {held}"

    depths = [0] * len(hierarchy.nodes)
    changed = True
    while changed:
        changed = False
        for i, node in enumerate(hierarchy.nodes):
            for child in node.children:
                nxt = depths[i] + 1
                if nxt > depths[child]:
                    depths[child] = nxt
                    changed = True
    max_depth = max(depths) if depths else 0
    rows = []
    for d in range(max_depth + 1):
        panes = []
        for i, node in enumerate(hierarchy.nodes):
            if depths[i] != d:
                continue

            def _pointer(x, y, index=i, announce=False, tracking_on=True):
                _apply(index, x, y, announce=announce, tracking_on=tracking_on)

            start_xy = start_pos.get(i, np.array([0.0, 0.0]))
            scatter, source = _node_overlay(
                node.model, start_xy, node.name, _pointer, width=plot_w, height=plot_h
            )
            cursors[i] = source
            panes.append(scatter)
        rows.append(pn.Row(*panes))

    return pn.Column(
        pn.pane.Markdown(_HEADING),
        *rows,
        view_pane,
        status,
    )
