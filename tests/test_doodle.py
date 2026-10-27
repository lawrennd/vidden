import numpy as np
import pytest

from vidden.doodle import (
    FACE_DIM,
    FACE_STROKES,
    StrokeSpec,
    face_from_factors,
    make_face_dataset,
    pack_doodle,
    unpack_doodle,
)
from vidden.views.doodle import DoodleView, stroke_polylines


def test_pack_unpack_roundtrip():
    strokes = face_from_factors(0.5, -0.2)
    y = pack_doodle(strokes)
    assert y.shape == (FACE_DIM,)
    back = unpack_doodle(y)
    assert len(back) == len(FACE_STROKES)
    for a, b in zip(strokes, back, strict=True):
        np.testing.assert_allclose(a, b)


def test_make_face_dataset_has_known_factors():
    Y, Z, strokes = make_face_dataset(n_smile=2, n_round=2)
    assert Y.shape == (4, FACE_DIM)
    assert Z.shape == (4, 2)
    assert strokes is FACE_STROKES
    np.testing.assert_allclose(Z[0], [-1.0, -1.0])
    np.testing.assert_allclose(Z[-1], [1.0, 1.0])


def test_closed_stroke_repeats_first_vertex():
    spec = StrokeSpec("loop", 4, True)
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    y = pack_doodle([pts])
    xs, ys = stroke_polylines(y, (spec,))
    assert xs[0][0] == xs[0][-1]
    assert ys[0][0] == ys[0][-1]
    assert len(xs[0]) == 5


def test_nan_stroke_is_omitted():
    specs = (StrokeSpec("a", 2, False), StrokeSpec("b", 2, False))
    a = np.array([[0.0, 0.0], [1.0, 0.0]])
    b = np.full((2, 2), np.nan)
    y = pack_doodle([a, b])
    xs, ys = stroke_polylines(y, specs)
    assert xs[0] == [0.0, 1.0]
    assert xs[1] == []
    assert ys[1] == []


def test_doodle_view_modify_does_not_change_axes():
    pytest.importorskip("bokeh")
    y0 = pack_doodle(face_from_factors(-1.0, 0.0))
    y1 = pack_doodle(face_from_factors(1.0, 1.0))
    view = DoodleView(y0)
    ranges0 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    view.modify(y1)
    ranges1 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    np.testing.assert_allclose(ranges1, ranges0)
    xs, _ = stroke_polylines(y1)
    assert view.source.data["xs"][0][0] == xs[0][0]


def test_load_face_model_matches_stick_kernel_start():
    pytest.importorskip("GPy")
    from vidden.demos import load_face_model

    np.random.seed(0)
    model = load_face_model()
    assert model.X.mean.shape[1] == 2
    np.testing.assert_allclose(np.asarray(model.kern.lengthscale), np.repeat(0.5, 2))
    np.testing.assert_allclose(np.asarray(model.likelihood.variance).reshape(-1)[0], 0.001)


def test_doodle_explorer_builds_without_serving():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.host.panel import doodle_explorer, latent_explorer
    from vidden.views.doodle import DoodleView

    Y, _, strokes = make_face_dataset(n_smile=2, n_round=2)
    np.random.seed(2)
    model = GPy.models.GPLVM(Y, 2)
    view = DoodleView(Y[0], strokes)
    app = latent_explorer(model, view)
    assert app is not None
    wrapped = doodle_explorer(model=model, strokes=strokes)
    assert wrapped is not None
    assert len(wrapped) >= 3


def test_examples_doodle_is_servable_entry():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    example = (root / "examples" / "doodle.py").read_text()
    host = (root / "src" / "vidden" / "host" / "panel.py").read_text()
    view = (root / "src" / "vidden" / "views" / "doodle.py").read_text()
    assert ".servable()" in example
    assert "sys.path.insert" in example
    assert ".servable()" not in host
    assert ".servable()" not in view
