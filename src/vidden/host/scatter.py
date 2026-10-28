"""HoloViews scatter of latent training points.

Visualization, not an app. Panel hosts import this the same way they
import Bokeh event helpers. Do not put layout, ``servable()``, or a
second host's explorer here. Do not inject this into other capabilities.
"""

from __future__ import annotations

import numpy as np


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
