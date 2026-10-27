"""Doodle reconstruction view (Visualise / Modify).

Init draws packed strokes and freezes the family's axis box. ``modify``
only writes the ColumnDataSource. NaN strokes are unmatched template
strokes: skip them, do not draw them at the origin.
"""

from __future__ import annotations

import numpy as np

from vidden.doodle import DOODLE_LIMITS, FACE_STROKES, unpack_doodle


def stroke_polylines(y, strokes=FACE_STROKES):
    """One polyline per spec. Missing (NaN) strokes become empty lists."""
    xs, ys = [], []
    for spec, pts in zip(strokes, unpack_doodle(y, strokes), strict=True):
        if not np.isfinite(pts).all():
            xs.append([])
            ys.append([])
            continue
        x = pts[:, 0].tolist()
        v = pts[:, 1].tolist()
        if spec.closed and x and (x[0] != x[-1] or v[0] != v[-1]):
            x.append(x[0])
            v.append(v[0])
        xs.append(x)
        ys.append(v)
    return xs, ys


class DoodleView:
    """Packed doodle as a Bokeh ``multi_line``.

    Creating a ``DoodleView`` does not start a Panel server. A host holds
    ``.fig`` and calls ``modify(y)``.
    """

    def __init__(self, y, strokes=FACE_STROKES, limits=DOODLE_LIMITS):
        from bokeh.models import ColumnDataSource, Range1d
        from bokeh.plotting import figure

        self.strokes = tuple(strokes)
        xmin, xmax, ymin, ymax = (float(v) for v in limits)
        self.limits = (xmin, xmax, ymin, ymax)
        self.source = ColumnDataSource(self._stroke_data(y))
        self.fig = figure(
            width=450,
            height=450,
            match_aspect=True,
            title="reconstruction",
            tools="",
            toolbar_location=None,
            x_range=Range1d(xmin, xmax, bounds="auto"),
            y_range=Range1d(ymin, ymax, bounds="auto"),
        )
        self.fig.multi_line(
            "xs",
            "ys",
            source=self.source,
            line_color="#111111",
            line_width=2,
        )
        self.fig.grid.visible = True
        self.fig.xaxis.axis_label = None
        self.fig.yaxis.axis_label = None
        if hasattr(self.fig, "context_menu"):
            self.fig.context_menu = None

    def _stroke_data(self, y):
        xs, ys = stroke_polylines(y, self.strokes)
        return {"xs": xs, "ys": ys}

    def modify(self, y):
        """Write stroke polylines. Do not touch axis ranges."""
        self.source.data = self._stroke_data(y)
        return self.fig
