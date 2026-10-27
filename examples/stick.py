"""Serve the stick-man latent explorer.

From the repository root::

    panel serve examples/stick.py --show

This is the only ``servable()`` call. ``stick_explorer`` itself returns a
pane.
"""

from vidden.host.panel import stick_explorer

stick_explorer().servable()
