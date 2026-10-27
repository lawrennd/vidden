"""Vector reconstruction view (GPy ``vector_show``).

Init draws index against value and freezes the axis box. ``modify``
only writes the ColumnDataSource.
"""

from __future__ import annotations

import numpy as np


def vector_y_limits(y, pad=0.05):
    """Y-range from a vector or training matrix, with a small pad."""
    vals = np.asarray(y, dtype=float)
    lo = float(np.min(vals))
    hi = float(np.max(vals))
    span = hi - lo
    if span <= 0.0:
        span = 1.0
    margin = span * float(pad)
    return lo - margin, hi + margin


class VectorView:
    """Packed observation as a Bokeh line of index vs value.

    Creating a ``VectorView`` does not start a Panel server. A host holds
    ``.fig`` and calls ``modify(y)``.
    """

    def __init__(self, y, limits=None):
        from bokeh.models import ColumnDataSource, Range1d
        from bokeh.plotting import figure

        y = np.asarray(y, dtype=float).reshape(-1)
        self.size = int(y.size)
        if limits is None:
            ymin, ymax = vector_y_limits(y)
        else:
            ymin, ymax = float(limits[0]), float(limits[1])
        self.limits = (ymin, ymax)
        self.source = ColumnDataSource(self._line_data(y))
        self.fig = figure(
            width=450,
            height=450,
            title="reconstruction",
            tools="",
            toolbar_location=None,
            x_range=Range1d(-0.5, self.size - 0.5, bounds="auto"),
            y_range=Range1d(ymin, ymax, bounds="auto"),
        )
        self.fig.line(
            "x",
            "y",
            source=self.source,
            line_color="#111111",
            line_width=2,
        )
        self.fig.scatter(
            "x",
            "y",
            source=self.source,
            size=6,
            color="#111111",
            marker="circle",
        )
        self.fig.grid.visible = True
        self.fig.xaxis.axis_label = "index"
        self.fig.yaxis.axis_label = "value"
        if hasattr(self.fig, "context_menu"):
            self.fig.context_menu = None

    def _line_data(self, y):
        y = np.asarray(y, dtype=float).reshape(-1)
        if y.size != self.size:
            raise ValueError(f"vector length {y.size} does not match view {self.size}")
        return {"x": list(range(self.size)), "y": y.tolist()}

    def modify(self, y):
        """Write the line. Do not touch axis ranges."""
        self.source.data = self._line_data(y)
        return self.fig
