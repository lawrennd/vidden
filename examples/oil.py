"""Serve the oil-flow latent explorer.

From the repository root::

    panel serve examples/oil.py --show
"""

from pathlib import Path
import sys

_src = Path(__file__).resolve().parents[1] / "src"
if _src.is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from vidden.host.panel import oil_explorer

oil_explorer().servable()
