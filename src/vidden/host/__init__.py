"""Hosts assemble views, pointer events, and layout.

Panel is the first host. It is not the only one we will ever have, and
it is not Referia (whose "panel" is a review-page region).
"""

from vidden.host.panel import stick_explorer

__all__ = ["stick_explorer"]
