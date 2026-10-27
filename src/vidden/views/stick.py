"""Stick-man reconstruction view (MATLAB ``stickVisualise`` / ``stickModify``).

Init creates glyphs and freezes a cubic equal-aspect box. ``modify`` only
writes ColumnDataSources — the Bokeh analog of MATLAB ``set`` on line
handles. It does not rebuild the figure, restyle a Plotly scene, or
touch the axes.

Live stick is 2-D. 3-D joints are projected with MATLAB's default camera
(azimuth -37.5, elevation 30). A 3-D skeleton is a later view, not this
pointer path.
"""

from __future__ import annotations

import numpy as np


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
    """Orthographic screen coordinates for MATLAB's default ``view``."""
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


def largest_training_pose(Y):
    """Training row used to open the stick plot (MATLAB ``lvmVisualise``)."""
    Y = np.atleast_2d(np.asarray(Y, dtype=float))
    return Y[int(np.argmax(np.sum(Y * Y, axis=1)))]


class StickView:
    """MATLAB ``stickVisualise`` / ``stickModify``, as Bokeh data sources.

    Creating a ``StickView`` does not start a Panel server. A host holds
    ``.fig`` and calls ``modify(y)`` with a reconstructed output row.
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
        if hasattr(self.fig, "context_menu"):
            self.fig.context_menu = None

    def _joint_data(self, xyz):
        u, v = matlab_view_project(xyz, self.azimuth, self.elevation)
        return {"x": u.tolist(), "y": v.tolist()}

    def _bone_data(self, xyz):
        u, v = matlab_view_project(xyz, self.azimuth, self.elevation)
        xs, ys = stick_bone_segments(u, v, self.connect)
        return {"xs": xs, "ys": ys}

    def modify(self, y):
        """Write joint and bone sources. Do not touch axis ranges."""
        xyz = y_to_xyz(y)
        self.joint_source.data = self._joint_data(xyz)
        self.bone_source.data = self._bone_data(xyz)
        return self.fig
