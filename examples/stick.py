"""Serve the stick-man latent explorer.

From the repository root::

    panel serve examples/stick.py --show

``stick_explorer`` itself returns a pane. Serve entries live under
``examples/``.
"""

from vidden.host.panel import stick_explorer

stick_explorer().servable()
