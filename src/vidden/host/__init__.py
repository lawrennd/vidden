"""Hosts assemble views, pointer events, and layout.

Panel is the first host. It is not the only one we will ever have, and
it is not Referia (whose "panel" is a review-page region).
"""

from vidden.host.panel import (
    doodle_explorer,
    face_explorer,
    latent_explorer,
    latent_training_points,
    oil_explorer,
    stick_explorer,
)

__all__ = [
    "doodle_explorer",
    "face_explorer",
    "latent_explorer",
    "latent_training_points",
    "oil_explorer",
    "stick_explorer",
]
