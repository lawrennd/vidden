import numpy as np
import pytest

from vidden.doodle import (
    FACE_DIM,
    FACE_STROKES,
    EXTRA_GREY,
    align_doodles,
    face_from_factors,
    looks_closed,
    query_match_colors,
    scramble_strokes,
    typical_template_index,
    unpack_doodle,
)

scipy = pytest.importorskip("scipy")


def test_looks_closed_head_not_mouth():
    strokes = face_from_factors(0.2, 0.1)
    by_name = {spec.name: pts for spec, pts in zip(FACE_STROKES, strokes, strict=True)}
    assert looks_closed(by_name["head"])
    assert looks_closed(by_name["left_eye"])
    assert not looks_closed(by_name["mouth"])
    assert not looks_closed(by_name["left_brow"])


def test_align_recovers_scrambled_stroke_order():
    closed = [spec.closed for spec in FACE_STROKES]
    template = face_from_factors(-0.4, 0.3)
    original = face_from_factors(0.7, -0.2)
    scrambled, perm, _closed_s = scramble_strokes(original, closed=closed, rng=0)
    Y, specs, assignments = align_doodles(
        [template, scrambled],
        closed=closed,
        n_vertices=[spec.n for spec in FACE_STROKES],
        names=[spec.name for spec in FACE_STROKES],
    )
    assert Y.shape == (2, FACE_DIM)
    assert specs == FACE_STROKES
    assert np.array_equal(perm[assignments[1]], np.arange(len(FACE_STROKES)))
    restored = unpack_doodle(Y[1], FACE_STROKES)
    for want, got in zip(original, restored, strict=True):
        np.testing.assert_allclose(got.mean(axis=0), np.asarray(want).mean(axis=0), atol=0.08)


def test_align_missing_stroke_is_nan():
    closed = [spec.closed for spec in FACE_STROKES]
    template = face_from_factors(0.1, 0.2)
    original = face_from_factors(0.6, -0.3)
    missing_mouth = original[:6] + original[7:]
    Y, _specs, assignments = align_doodles(
        [template, missing_mouth],
        closed=closed,
        n_vertices=[spec.n for spec in FACE_STROKES],
        names=[spec.name for spec in FACE_STROKES],
    )
    assert assignments[1][6] == -1
    unpacked = unpack_doodle(Y[1], FACE_STROKES)
    assert np.all(np.isnan(unpacked[6]))
    for i, pts in enumerate(unpacked):
        if i != 6:
            assert np.all(np.isfinite(pts))


def test_align_does_not_translate_onto_template():
    high = [np.column_stack((np.linspace(-0.3, 0.3, 10), np.full(10, 0.55)))]
    low = [np.column_stack((np.linspace(-0.25, 0.25, 14), np.full(14, -0.4)))]
    Y, specs, _assignments = align_doodles([high, low])
    got = unpack_doodle(Y[1], specs)[0]
    np.testing.assert_allclose(got[:, 1], -0.4, atol=0.05)


def test_typical_template_skips_extra_stroke():
    closed = [spec.closed for spec in FACE_STROKES]
    n_vertices = [spec.n for spec in FACE_STROKES]
    names = [spec.name for spec in FACE_STROKES]
    frown = face_from_factors(-1.0, 0.0)
    smile = face_from_factors(1.0, 0.0)
    tongue = [
        *face_from_factors(0.2, 0.0),
        np.array([[0.0, -0.7], [0.08, -0.95], [0.0, -0.85]], dtype=float),
    ]
    doodles = [frown, smile, tongue]
    assert typical_template_index(doodles) == 0
    Y, specs, assignments = align_doodles(
        doodles,
        template_index="typical",
        closed=closed,
        n_vertices=n_vertices,
        names=names,
    )
    assert specs == FACE_STROKES
    assert Y.shape == (3, FACE_DIM)
    assert np.all(assignments[0] >= 0)
    assert np.all(assignments[1] >= 0)
    assert np.all(assignments[2] >= 0)
    mouth_f = unpack_doodle(Y[0], FACE_STROKES)[6]
    mouth_s = unpack_doodle(Y[1], FACE_STROKES)[6]
    assert float(mouth_s[0, 1]) > float(mouth_f[0, 1]) + 0.08


def test_align_extra_stroke_is_dropped():
    closed = [spec.closed for spec in FACE_STROKES]
    template = face_from_factors(-0.2, 0.4)
    original = face_from_factors(0.5, 0.1)
    extra = [*original, np.array([[0.0, -1.1], [0.15, -1.05], [0.0, -1.0]], dtype=float)]
    Y, _specs, assignments = align_doodles(
        [template, extra],
        closed=closed,
        n_vertices=[spec.n for spec in FACE_STROKES],
        names=[spec.name for spec in FACE_STROKES],
    )
    assert np.all(assignments[1] >= 0)
    assert np.all(np.isfinite(Y[1]))
    assert Y.shape == (2, FACE_DIM)
    colors = query_match_colors(len(extra), assignments[1])
    assert colors[-1] == EXTRA_GREY
    assert colors[0] != EXTRA_GREY
