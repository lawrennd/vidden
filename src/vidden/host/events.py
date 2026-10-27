"""Bokeh pointer helpers for hosts. Read the toolkit manuals.

Rules we already paid for:

- ``Tap`` is left-click only. Pointer gestures ignore other buttons.
- Right-click is ``Plot.context_menu``. Python gets ``MenuItemClick``
  (``event.item`` is the label).
- Do not ``preventDefault`` the browser menu to fake a right-button Tap.
- CustomJS ``source.stream()`` does not notify Python ``on_change('data')``.
  Assign a whole new ``source.data`` dict.
- Attach ``fig.on_event`` on the Bokeh figure HoloViews built. Do not
  rely on HoloViews ``PointerXY`` / ``Tap`` streams on an Image overlay.
"""

from __future__ import annotations

import numpy as np


def bar_index_from_event_x(x, n_dims):
    """Map a Bokeh bar-plot click to a latent dimension index."""
    if x is None:
        return None
    if isinstance(x, (bytes, str)):
        try:
            x = int(x)
        except ValueError:
            return None
    try:
        idx = int(np.round(float(x)))
    except (TypeError, ValueError):
        return None
    if 0 <= idx < int(n_dims):
        return idx
    return None


def event_has_shift(event):
    """True if a Bokeh ``Tap`` arrived with the shift key down."""
    mods = getattr(event, "modifiers", None)
    if mods is None:
        return False
    if isinstance(mods, dict):
        return bool(mods.get("shift"))
    return bool(getattr(mods, "shift", False))


def disable_bokeh_context_menu(fig):
    """Stop Bokeh's ToolMenu (the 'properties' popup) on right-click."""
    if hasattr(fig, "context_menu"):
        fig.context_menu = None


def menu_item_dimension(item, n_dims):
    """Read a latent index from ``MenuItemClick.item`` (the item label)."""
    if item is None:
        return None
    return bar_index_from_event_x(str(item).rsplit(None, 1)[-1], n_dims)


def install_bar_x_menu(fig, n_dims, on_pick):
    """MATLAB right-button on the histogram, via Bokeh's documented API."""
    from bokeh.events import MenuItemClick
    from bokeh.models import Menu, MenuItem

    items = [MenuItem(label=str(k)) for k in range(int(n_dims))]
    fig.context_menu = Menu(items=items)

    def _on_menu(event):
        on_pick(getattr(event, "item", None))

    fig.on_event(MenuItemClick, _on_menu)
