"""Reconstruction views: Visualise once, then only modify data.

A view owns artists and frozen axes. It does not start a Panel server,
optimize a model, or interpret pointer events. Hosts hold the view and
call ``modify(y)``.
"""

from vidden.views.stick import StickView

__all__ = ["StickView"]
