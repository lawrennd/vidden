"""Serve the stick-man latent explorer.

From the repository root::

    panel serve examples/stick.py --show

``stick_explorer`` itself returns a pane. Serve entries live under
``examples/``.
"""

from pathlib import Path
import sys

_src = Path(__file__).resolve().parents[1] / "src"
if _src.is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from vidden.host.panel import stick_explorer

stick_explorer().servable()
