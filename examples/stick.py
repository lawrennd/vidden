"""Serve the stick-man latent explorer.

From the repository root::

    panel serve examples/stick.py --show
"""

from vidden.explore import stick_explorer

stick_explorer().servable()
