"""Serve the latent doodle-space explorer on generated faces.

From the repository root::

    panel serve examples/doodle.py --show
"""

from vidden.host.panel import doodle_explorer

doodle_explorer().servable()
