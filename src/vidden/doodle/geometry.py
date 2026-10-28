"""Packed stroke vectors and generated cartoon faces.

This module does not match strokes or write files. Correspondence is
:mod:`vidden.doodle.align`. JSON families are :mod:`vidden.doodle.store`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StrokeSpec:
    """One named polyline in an aligned doodle family."""

    name: str
    n: int
    closed: bool


FACE_STROKES: tuple[StrokeSpec, ...] = (
    StrokeSpec("head", 48, True),
    StrokeSpec("left_eye", 16, True),
    StrokeSpec("right_eye", 16, True),
    StrokeSpec("left_pupil", 10, True),
    StrokeSpec("right_pupil", 10, True),
    StrokeSpec("nose", 8, False),
    StrokeSpec("mouth", 20, False),
    StrokeSpec("left_brow", 12, False),
    StrokeSpec("right_brow", 12, False),
)

FACE_DIM = 2 * sum(stroke.n for stroke in FACE_STROKES)
DOODLE_LIMITS = (-1.35, 1.35, -1.45, 1.35)


def _ellipse(cx, cy, rx, ry, n, rot=0.0):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = rx * np.cos(t)
    y = ry * np.sin(t)
    if rot:
        c, s = np.cos(rot), np.sin(rot)
        x, y = c * x - s * y, s * x + c * y
    return np.column_stack((cx + x, cy + y))


def resample_stroke(points, n, closed=False):
    """Arc-length resample a polyline to ``n`` vertices."""
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError(f"expected (k, 2) polyline, got {pts.shape}")
    if len(pts) == 0:
        raise ValueError("empty stroke")
    if closed and len(pts) > 1 and not np.allclose(pts[0], pts[-1]):
        pts = np.vstack([pts, pts[0]])
    if len(pts) == 1:
        return np.repeat(pts, n, axis=0)
    target = n + 1 if closed else n
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1))
    u = np.concatenate([[0.0], np.cumsum(seg)])
    total = u[-1]
    if total <= 0:
        return np.repeat(pts[:1], n, axis=0)
    u = u / total
    t = np.linspace(0.0, 1.0, target, endpoint=True)
    sampled = np.column_stack((np.interp(t, u, pts[:, 0]), np.interp(t, u, pts[:, 1])))
    return sampled[:-1] if closed else sampled


def pack_doodle(strokes):
    """Concatenate ``[(n_i, 2), ...]`` polylines into a length-``2 Σ n_i`` vector."""
    return np.concatenate([np.asarray(s, dtype=float).reshape(-1) for s in strokes])


def unpack_doodle(y, strokes=FACE_STROKES):
    """Inverse of :func:`pack_doodle`."""
    y = np.asarray(y, dtype=float).reshape(-1)
    expected = 2 * sum(spec.n for spec in strokes)
    if y.size != expected:
        raise ValueError(f"doodle length {y.size} does not match stroke spec {expected}")
    out = []
    offset = 0
    for spec in strokes:
        n = spec.n
        out.append(y[offset : offset + 2 * n].reshape(n, 2))
        offset += 2 * n
    return out


def face_from_factors(smile, roundness):
    """Build one aligned face from smile and roundness in ``[-1, 1]``.

    ``smile > 0`` is a smile (corners up); ``roundness > 0`` is a rounder head.
    """
    smile = float(np.clip(smile, -1.0, 1.0))
    roundness = float(np.clip(roundness, -1.0, 1.0))

    rx = 0.78 + 0.20 * roundness
    ry = 1.08 - 0.14 * roundness
    eye_y = 0.22 + 0.04 * roundness
    eye_dx = 0.30 + 0.03 * roundness
    eye_rx, eye_ry = 0.15, 0.11
    pupil_r = 0.045
    brow_y = eye_y + 0.22
    brow_tilt = 0.10 * smile
    mouth_y = -0.42 - 0.04 * roundness
    mouth_w = 0.30 + 0.04 * roundness

    head = _ellipse(0.0, 0.0, rx, ry, FACE_STROKES[0].n)
    left_eye = _ellipse(-eye_dx, eye_y, eye_rx, eye_ry, FACE_STROKES[1].n)
    right_eye = _ellipse(eye_dx, eye_y, eye_rx, eye_ry, FACE_STROKES[2].n)
    left_pupil = _ellipse(-eye_dx + 0.02, eye_y - 0.01, pupil_r, pupil_r, FACE_STROKES[3].n)
    right_pupil = _ellipse(eye_dx - 0.02, eye_y - 0.01, pupil_r, pupil_r, FACE_STROKES[4].n)
    nose = resample_stroke([(-0.07, 0.04), (0.0, -0.18), (0.07, 0.04)], FACE_STROKES[5].n)

    mx = np.linspace(-mouth_w, mouth_w, FACE_STROKES[6].n)
    my = mouth_y + 0.16 * smile * ((mx / mouth_w) ** 2 - 0.45)
    mouth = np.column_stack((mx, my))

    bx = np.linspace(-0.14, 0.14, FACE_STROKES[7].n)
    left_brow = np.column_stack((-eye_dx + bx, brow_y + brow_tilt * (bx / 0.14)))
    right_brow = np.column_stack((eye_dx + bx, brow_y + brow_tilt * (-bx / 0.14)))

    return [
        head,
        left_eye,
        right_eye,
        left_pupil,
        right_pupil,
        nose,
        mouth,
        left_brow,
        right_brow,
    ]


def cartoon_doodles(n_smile=4, n_round=3):
    """Stroke lists for the smile × roundness grid (12 faces by default)."""
    smiles = np.linspace(-1.0, 1.0, n_smile)
    rounds = np.linspace(-1.0, 1.0, n_round)
    return [face_from_factors(smile, roundness) for smile in smiles for roundness in rounds]


def make_face_dataset(n_smile=4, n_round=3):
    """Return ``Y, Z, strokes`` for a grid of smile × roundness examples.

    ``Y`` is ``(N, D)`` packed doodles. ``Z`` is the true ``(N, 2)`` factor
    grid with columns ``(smile, roundness)``.
    """
    doodles = cartoon_doodles(n_smile=n_smile, n_round=n_round)
    smiles = np.linspace(-1.0, 1.0, n_smile)
    rounds = np.linspace(-1.0, 1.0, n_round)
    Y = np.asarray([pack_doodle(doodle) for doodle in doodles], dtype=float)
    Z = np.asarray([(s, r) for s in smiles for r in rounds], dtype=float)
    return Y, Z, FACE_STROKES
