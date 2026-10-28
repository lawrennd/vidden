"""Doodle geometry, correspondence, and JSON families.

Drawing and alignment *views* live in ``vidden.host``. This package is
the data pipeline those hosts call.
"""

from vidden.doodle.align import (
    EXTRA_GREY,
    align_doodles,
    looks_closed,
    match_to_template,
    pair_cost_and_align,
    query_match_colors,
    scramble_strokes,
    stroke_palette,
    typical_template_index,
)
from vidden.doodle.geometry import (
    DOODLE_LIMITS,
    FACE_DIM,
    FACE_STROKES,
    StrokeSpec,
    _ellipse,
    cartoon_doodles,
    face_from_factors,
    make_face_dataset,
    pack_doodle,
    resample_stroke,
    unpack_doodle,
)
from vidden.doodle.store import (
    ensure_cartoon_family,
    family_dir,
    family_slug,
    list_doodle_families,
    load_doodle_dir,
    load_doodles,
    picker_target,
    resolve_doodle_root,
    save_doodles,
    save_family,
    doodles_from_jsonable,
    doodles_to_jsonable,
)

__all__ = [
    "DOODLE_LIMITS",
    "EXTRA_GREY",
    "FACE_DIM",
    "FACE_STROKES",
    "StrokeSpec",
    "align_doodles",
    "cartoon_doodles",
    "doodles_from_jsonable",
    "doodles_to_jsonable",
    "ensure_cartoon_family",
    "face_from_factors",
    "family_dir",
    "family_slug",
    "list_doodle_families",
    "load_doodle_dir",
    "load_doodles",
    "looks_closed",
    "make_face_dataset",
    "match_to_template",
    "pack_doodle",
    "pair_cost_and_align",
    "picker_target",
    "query_match_colors",
    "resample_stroke",
    "resolve_doodle_root",
    "save_doodles",
    "save_family",
    "scramble_strokes",
    "stroke_palette",
    "typical_template_index",
    "unpack_doodle",
]
