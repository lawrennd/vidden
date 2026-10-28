"""Compatibility imports. Prefer ``vidden.views`` and ``vidden.host``.

Jupyter::

    from vidden.explore import doodle_explorer, stick_explorer
    stick_explorer()
    doodle_explorer()

Standalone (from the repository root)::

    panel serve examples/stick.py --show
    panel serve examples/doodle.py --show
    panel serve examples/oil.py --show
    panel serve examples/faces.py --show
    panel serve examples/tree.py --show
"""

from vidden.demos import (
    load_brendan_model,
    load_face_model,
    load_oil_model,
    load_stick_model,
    load_synthetic_tree,
    load_walk_run_tree,
    load_walk_tree,
    optimize_stick_model,
)
from vidden.host.events import (
    bar_index_from_event_x,
    disable_bokeh_context_menu,
    event_has_shift,
    install_bar_x_menu,
    menu_item_dimension,
)
from vidden.host.panel import (
    doodle_explorer,
    face_explorer,
    latent_explorer,
    latent_training_points,
    oil_explorer,
    stick_explorer,
)
from vidden.host.tree import tree_explorer
from vidden.models import (
    assemble_latent,
    assemble_latent_nearest,
    input_sensitivity_values,
    latent_array,
    latent_axis_limits,
    latent_mean_row,
    latent_posterior_density_grid,
    most_significant_dims,
    reconstruct_mean,
    sensitivity_bar_ylim,
)
from vidden.views.doodle import DoodleView
from vidden.views.image import ImageView
from vidden.views.vector import VectorView
from vidden.views.stick import (
    StickView,
    cubic_axis_limits,
    largest_training_pose,
    matlab_view_project,
    stick_bone_segments,
    stick_polylines,
    y_to_xyz,
)

__all__ = [
    "DoodleView",
    "ImageView",
    "StickView",
    "VectorView",
    "doodle_explorer",
    "face_explorer",
    "latent_explorer",
    "tree_explorer",
    "latent_training_points",
    "oil_explorer",
    "assemble_latent",
    "assemble_latent_nearest",
    "bar_index_from_event_x",
    "cubic_axis_limits",
    "disable_bokeh_context_menu",
    "event_has_shift",
    "input_sensitivity_values",
    "install_bar_x_menu",
    "largest_training_pose",
    "latent_array",
    "latent_axis_limits",
    "latent_mean_row",
    "latent_posterior_density_grid",
    "load_synthetic_tree",
    "load_walk_run_tree",
    "load_walk_tree",
    "load_brendan_model",
    "load_face_model",
    "load_oil_model",
    "load_stick_model",
    "matlab_view_project",
    "menu_item_dimension",
    "most_significant_dims",
    "optimize_stick_model",
    "reconstruct_mean",
    "sensitivity_bar_ylim",
    "stick_bone_segments",
    "stick_explorer",
    "stick_polylines",
    "y_to_xyz",
]
