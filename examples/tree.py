"""Serve the hierarchical GP-LVM explorer.

From the repository root::

    panel serve examples/tree.py --show
"""

from pathlib import Path
import sys

_src = Path(__file__).resolve().parents[1] / "src"
if _src.is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from vidden.host.tree import tree_explorer

tree_explorer().servable()
