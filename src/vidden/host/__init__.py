"""Hosts assemble views, pointer events, and layout.

Panel is the first host. It is not the only one we will ever have, and
it is not Referia (whose "panel" is a review-page region).
"""

from vidden.host.correspondence import doodle_align
from vidden.host.panel import (
    doodle_explorer,
    face_explorer,
    latent_explorer,
    latent_training_points,
    oil_explorer,
    stick_explorer,
)
from vidden.host.studio import doodle_studio
from vidden.host.tree import tree_explorer

__all__ = [
    "doodle_align",
    "doodle_explorer",
    "doodle_studio",
    "face_explorer",
    "latent_explorer",
    "latent_training_points",
    "oil_explorer",
    "stick_explorer",
    "tree_explorer",
]
