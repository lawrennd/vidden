"""Image reconstruction view (GPy ``image_show``).

Reshape a packed ``Y`` row with the same ``dimensions`` / ``order`` /
``transpose`` / ``invert`` flags as GPy. Init freezes the pixel box and
colour limits. ``modify`` only writes the ColumnDataSource.

Mosaic of several images in one vector is out of scope.
"""

from __future__ import annotations

import numpy as np

BRENDAN_IMAGE = {
    "dimensions": (20, 28),
    "transpose": True,
    "order": "F",
    "invert": False,
}

OLIVETTI_IMAGE = {
    "dimensions": (112, 92),
    "transpose": False,
    "order": "C",
    "invert": False,
}


def reshape_image(y, dimensions, *, order="C", transpose=False, invert=False, preset_mean=0.0, preset_std=1.0):
    """GPy ``image_show.set_image`` for a single packed row (no mosaic)."""
    y = np.asarray(y, dtype=float).reshape(-1)
    height, width = int(dimensions[0]), int(dimensions[1])
    dim = height * width
    if y.size < dim:
        raise ValueError(f"image vector length {y.size} is shorter than {height}×{width}")
    img = np.reshape(y[:dim], (height, width), order=order)
    if transpose:
        img = img.T
    if invert:
        img = -img
    return img * float(preset_std) + float(preset_mean)


def image_color_limits(Y, dimensions, *, order="C", transpose=False, invert=False, preset_mean=0.0, preset_std=1.0):
    """Frozen greyscale limits from the training matrix, not from one frame."""
    Y = np.atleast_2d(np.asarray(Y, dtype=float))
    vals = Y[:, : int(dimensions[0]) * int(dimensions[1])]
    if invert:
        vals = -vals
    vals = vals * float(preset_std) + float(preset_mean)
    lo = float(np.min(vals))
    hi = float(np.max(vals))
    if hi <= lo:
        hi = lo + 1.0
    return lo, hi


class ImageView:
    """Packed greyscale image as a Bokeh ``image``.

    Creating an ``ImageView`` does not start a Panel server. A host holds
    ``.fig`` and calls ``modify(y)``. The array is flipped vertically so
    row 0 is at the top, matching matplotlib ``imshow``.
    """

    def __init__(
        self,
        y,
        dimensions=(16, 16),
        *,
        transpose=False,
        order="C",
        invert=False,
        preset_mean=0.0,
        preset_std=1.0,
        color_limits=None,
    ):
        from bokeh.models import ColumnDataSource, LinearColorMapper, Range1d
        from bokeh.plotting import figure

        self.dimensions = (int(dimensions[0]), int(dimensions[1]))
        self.transpose = bool(transpose)
        self.order = order
        self.invert = bool(invert)
        self.preset_mean = float(preset_mean)
        self.preset_std = float(preset_std)
        img = self._reshape(y)
        height, width = img.shape
        if color_limits is None:
            vmin, vmax = float(img.min()), float(img.max())
            if vmax <= vmin:
                vmax = vmin + 1.0
        else:
            vmin, vmax = float(color_limits[0]), float(color_limits[1])
        self.color_limits = (vmin, vmax)
        self.mapper = LinearColorMapper(palette="Greys256", low=vmin, high=vmax)
        self.source = ColumnDataSource(self._image_data(img))
        self.fig = figure(
            width=450,
            height=450,
            match_aspect=True,
            title="reconstruction",
            tools="",
            toolbar_location=None,
            x_range=Range1d(0, width, bounds="auto"),
            y_range=Range1d(0, height, bounds="auto"),
        )
        self.fig.image(
            image="image",
            x=0,
            y=0,
            dw=width,
            dh=height,
            source=self.source,
            color_mapper=self.mapper,
        )
        self.fig.grid.visible = False
        self.fig.xaxis.visible = False
        self.fig.yaxis.visible = False
        if hasattr(self.fig, "context_menu"):
            self.fig.context_menu = None

    def _reshape(self, y):
        return reshape_image(
            y,
            self.dimensions,
            order=self.order,
            transpose=self.transpose,
            invert=self.invert,
            preset_mean=self.preset_mean,
            preset_std=self.preset_std,
        )

    def _image_data(self, img):
        return {"image": [np.flipud(np.asarray(img, dtype=float))]}

    def modify(self, y):
        """Write image pixels. Do not touch axis ranges or colour limits."""
        self.source.data = self._image_data(self._reshape(y))
        return self.fig
