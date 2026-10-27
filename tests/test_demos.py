import numpy as np
import pytest


def test_load_brendan_model_attaches_gpy_image_flags(monkeypatch):
    pytest.importorskip("GPy")
    pods = pytest.importorskip("pods")
    from vidden.demos import load_brendan_model
    from vidden.views.image import BRENDAN_IMAGE

    rng = np.random.default_rng(0)
    fake = {"Y": rng.normal(size=(12, 20 * 28))}
    monkeypatch.setattr(pods.datasets, "brendan_faces", lambda: fake)
    monkeypatch.setattr("vidden.demos.optimize_stick_model", lambda model, **kwargs: model)

    model = load_brendan_model(n=8, num_inducing=4, optimize=True)
    assert model.Y.shape == (8, 20 * 28)
    assert model.X.mean.shape[1] == 2
    assert model.image_dimensions == BRENDAN_IMAGE["dimensions"]
    assert model.image_transpose is True
    assert model.image_order == "F"
    assert model.image_invert is False
    np.testing.assert_allclose(np.asarray(model.kern.lengthscale), np.repeat(0.5, 2))
    np.testing.assert_allclose(np.asarray(model.likelihood.variance).reshape(-1)[0], 0.001)


def test_load_stick_model_uses_osu_connect(monkeypatch):
    pytest.importorskip("GPy")
    pods = pytest.importorskip("pods")
    from vidden.demos import load_stick_model

    rng = np.random.default_rng(1)
    fake = {"Y": rng.normal(size=(10, 9)), "connect": np.eye(3)}
    monkeypatch.setattr(pods.datasets, "osu_run1", lambda: fake)
    model = load_stick_model()
    assert model.Y.shape == (10, 9)
    assert model.X.mean.shape[1] == 6
    np.testing.assert_array_equal(model.data["connect"], np.eye(3))


def test_load_oil_model_optimize_flag(monkeypatch):
    pytest.importorskip("GPy")
    pytest.importorskip("pods")
    from vidden.demos import load_oil_model

    called = {}

    def _opt(model, **kwargs):
        called["yes"] = True
        return model

    monkeypatch.setattr("vidden.demos.optimize_stick_model", _opt)
    model = load_oil_model(N=12, input_dim=3, num_inducing=6, optimize=True)
    assert called["yes"]
    assert model.Y.shape == (12, 12)


def test_load_face_model_optimize_flag(monkeypatch):
    pytest.importorskip("GPy")
    from vidden.demos import load_face_model

    called = {}

    def _opt(model, **kwargs):
        called["yes"] = True
        return model

    monkeypatch.setattr("vidden.demos.optimize_stick_model", _opt)
    model = load_face_model(num_inducing=4, optimize=True)
    assert called["yes"]
    assert model.X.mean.shape[1] == 2
