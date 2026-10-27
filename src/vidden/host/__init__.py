"""Hosts assemble views, pointer events, and layout.

Panel is the first host. It is not the only one we will ever have, and
it is not Referia (whose "panel" is a review-page region).
"""

from vidden.host.panel import doodle_explorer, latent_explorer, oil_explorer, stick_explorer

__all__ = ["doodle_explorer", "latent_explorer", "oil_explorer", "stick_explorer"]
