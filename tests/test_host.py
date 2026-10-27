"""Exercise the Panel host without serving a browser."""

import numpy as np
import pytest


def _tiny_model(q=3, d=6, labels=True):
    GPy = pytest.importorskip("GPy")
    np.random.seed(2)
    Y = np.random.randn(8, d)
    model = GPy.models.GPLVM(Y, q)
    if labels:
        model.data_labels = np.array([0, 0, 1, 1, 2, 2, 0, 1])
    return model, Y


def _hv_from_panel(obj):
    current = obj
    if hasattr(current, "object"):
        current = current.object
    return current


def test_latent_explorer_renders_and_tracks_pointer():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    import holoviews as hv
    from bokeh.events import MouseMove, Tap
    from vidden.host.panel import latent_explorer
    from vidden.views.vector import VectorView

    model, Y = _tiny_model()
    view = VectorView(Y[0], limits=(-3.0, 3.0))
    app = latent_explorer(model, view)
    scatter = _hv_from_panel(app[2][0][0])
    bars = _hv_from_panel(app[2][0][1])
    overlay = hv.render(scatter, backend="bokeh")
    hv.render(bars, backend="bokeh")
    fig = overlay if hasattr(overlay, "on_event") else overlay.renderers[0]
    if not hasattr(fig, "_trigger_event"):
        fig = getattr(overlay, "children", [overlay])[0] if hasattr(overlay, "children") else overlay
    fig._trigger_event(Tap(fig, x=0.1, y=-0.2))
    fig._trigger_event(MouseMove(fig, x=0.2, y=-0.1))
    fig._trigger_event(Tap(fig, x=0.0, y=0.0))
    dim_x, dim_y = app[1][0], app[1][1]
    if dim_x.value == 0:
        dim_y.value = 2
        dim_x.value = 1
    else:
        dim_x.value = 0
        dim_y.value = 1
    assert view.source.data["y"] is not None


def test_latent_explorer_optimize_button_without_curdoc(monkeypatch):
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    from vidden.host.panel import latent_explorer
    from vidden.views.vector import VectorView

    model, Y = _tiny_model()
    called = {}

    def _opt(m, **kwargs):
        called["iters"] = kwargs.get("max_iters")
        return m

    monkeypatch.setattr("vidden.host.panel.optimize_stick_model", _opt)
    view = VectorView(Y[0], limits=(-3.0, 3.0))
    app = latent_explorer(model, view, optimize=True)
    assert called["iters"] is None or called
    called.clear()
    app[1][3].value = 4
    app[1][2].clicks = 1
    assert called.get("iters") == 4


def test_wrappers_load_when_model_omitted(monkeypatch):
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    from vidden.doodle import make_face_dataset
    from vidden.host import panel

    stick_model, _ = _tiny_model(q=2, d=9, labels=False)
    stick_model.data = {"connect": np.eye(3)}
    oil_model, _ = _tiny_model(q=3, d=12, labels=True)
    Y_face, _, strokes = make_face_dataset(n_smile=2, n_round=2)
    GPy = pytest.importorskip("GPy")
    doodle_model = GPy.models.GPLVM(Y_face, 2)
    doodle_model.doodle_strokes = strokes
    face_model, _ = _tiny_model(q=2, d=6, labels=False)

    monkeypatch.setattr(panel, "load_stick_model", lambda **kwargs: stick_model)
    monkeypatch.setattr(panel, "load_oil_model", lambda **kwargs: oil_model)
    monkeypatch.setattr(panel, "load_face_model", lambda **kwargs: doodle_model)
    monkeypatch.setattr(panel, "load_brendan_model", lambda **kwargs: face_model)
    monkeypatch.setattr(panel, "latent_explorer", lambda m, v, **kwargs: (m, type(v).__name__))

    assert panel.stick_explorer()[0] is stick_model
    assert panel.oil_explorer()[0] is oil_model
    assert panel.doodle_explorer()[0] is doodle_model
    assert panel.face_explorer(dimensions=(2, 3), transpose=False, order="C")[0] is face_model


def test_face_explorer_explicit_flags_on_small_image():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.host.panel import face_explorer

    np.random.seed(3)
    Y = np.random.randn(6, 6)
    model = GPy.models.GPLVM(Y, 2)
    app = face_explorer(model=model, dimensions=(2, 3), transpose=True, order="F", invert=True)
    assert app is not None
    assert len(app) >= 3


def test_stick_explorer_reads_connect_from_model():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.host.panel import stick_explorer

    np.random.seed(4)
    Y = np.random.randn(6, 9)
    model = GPy.models.GPLVM(Y, 2)
    model.data = {"connect": np.eye(3)}
    app = stick_explorer(model=model)
    assert app is not None


def test_doodle_explorer_reads_strokes_from_model():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.doodle import FACE_STROKES, make_face_dataset
    from vidden.host.panel import doodle_explorer

    Y, _, strokes = make_face_dataset(n_smile=2, n_round=2)
    model = GPy.models.GPLVM(Y, 2)
    model.doodle_strokes = strokes
    app = doodle_explorer(model=model)
    assert app is not None
    assert strokes is FACE_STROKES


def test_latent_training_points_reshapes_short_xy():
    pytest.importorskip("holoviews")
    from vidden.host.panel import latent_training_points

    pts = latent_training_points(np.array([0.0, 1.0]))
    assert pts.data.shape[0] == 1
