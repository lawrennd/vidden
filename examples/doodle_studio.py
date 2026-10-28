"""Serve the user doodle studio.

From the repository root::

    panel serve examples/doodle_studio.py --show
"""

from pathlib import Path
import sys

_src = Path(__file__).resolve().parents[1] / "src"
if _src.is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from vidden.host.studio import doodle_studio

doodle_studio().servable()
