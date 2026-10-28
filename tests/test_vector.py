import numpy as np
import pytest

from vidden.views.vector import VectorView, vector_y_limits


def test_vector_y_limits_pad_around_range():
    lo, hi = vector_y_limits([-1.0, 1.0], pad=0.1)
    np.testing.assert_allclose((lo, hi), (-1.2, 1.2))


def test_vector_y_limits_on_training_matrix():
    Y = np.array([[-2.0, 0.0], [2.0, 1.0]])
    lo, hi = vector_y_limits(Y, pad=0.0)
    np.testing.assert_allclose((lo, hi), (-2.0, 2.0))


def test_vector_y_limits_constant_vector_has_span():
    lo, hi = vector_y_limits([3.0, 3.0], pad=0.1)
    assert hi > lo


def test_vector_view_default_limits_come_from_row():
    pytest.importorskip("bokeh")
    y = np.array([-1.0, 1.0, 0.0])
    view = VectorView(y)
    expected = vector_y_limits(y)
    np.testing.assert_allclose((view.fig.y_range.start, view.fig.y_range.end), expected)


def test_vector_view_modify_does_not_change_axes():
    pytest.importorskip("bokeh")
    y0 = np.linspace(-1.0, 1.0, 12)
    y1 = np.linspace(-0.2, 0.4, 12)
    view = VectorView(y0, limits=(-1.5, 1.5))
    ranges0 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    view.modify(y1)
    ranges1 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    np.testing.assert_allclose(ranges1, ranges0)
    np.testing.assert_allclose(view.source.data["y"], y1)
    assert len(view.source.data["x"]) == 12


def test_vector_view_rejects_length_change():
    pytest.importorskip("bokeh")
    view = VectorView(np.zeros(4))
    with pytest.raises(ValueError, match="vector length"):
        view.modify(np.zeros(5))


def test_oil_explorer_builds_without_serving():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.host.panel import latent_explorer, oil_explorer
    from vidden.views.vector import VectorView

    np.random.seed(2)
    Y = np.random.randn(8, 12)
    model = GPy.models.GPLVM(Y, 3)
    model.data_labels = np.array([0, 0, 1, 1, 2, 2, 0, 1])
    view = VectorView(Y[0], limits=(-3.0, 3.0))
    app = latent_explorer(model, view)
    assert app is not None
    wrapped = oil_explorer(model=model)
    assert wrapped is not None
    assert len(wrapped) >= 3


def test_reconstruct_mean_writes_vector_view():
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.models import assemble_latent, latent_mean_row, reconstruct_mean

    np.random.seed(1)
    Y = np.random.randn(10, 12)
    model = GPy.models.GPLVM(Y, 2)
    z = assemble_latent(latent_mean_row(model), 0.1, -0.2, 0, 1)
    mu = reconstruct_mean(model, z)
    view = VectorView(Y[0], limits=vector_y_limits(Y))
    ranges0 = (view.fig.y_range.start, view.fig.y_range.end)
    view.modify(mu)
    np.testing.assert_allclose(view.source.data["y"], mu)
    np.testing.assert_allclose((view.fig.y_range.start, view.fig.y_range.end), ranges0)


def test_latent_training_points_colour_when_labels_match():
    pytest.importorskip("holoviews")
    from vidden.host.scatter import latent_training_points

    xy = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 0.0]])
    labelled = latent_training_points(xy, [0, 1, 0])
    assert "label" in labelled.vdims
    plain = latent_training_points(xy)
    assert "label" not in plain.vdims
    mismatch = latent_training_points(xy, [0, 1])
    assert "label" not in mismatch.vdims


def test_load_oil_model_has_twelve_outputs_and_labels():
    pytest.importorskip("GPy")
    pytest.importorskip("pods")
    from vidden.demos import load_oil_model

    model = load_oil_model(N=12, input_dim=3, num_inducing=6)
    assert model.Y.shape == (12, 12)
    assert model.X.mean.shape[1] == 3
    labels = np.asarray(model.data_labels)
    assert labels.shape == (12,)
    assert len(np.unique(labels)) >= 2
    np.testing.assert_allclose(np.asarray(model.kern.lengthscale), np.repeat(0.5, 3))
    np.testing.assert_allclose(np.asarray(model.likelihood.variance).reshape(-1)[0], 0.001)


def test_oil_explorer_freezes_ylim_from_full_training_matrix():
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.views.stick import largest_training_pose

    np.random.seed(4)
    Y = np.array([[-2.0, 0.0, 0.5], [2.0, 1.0, -0.5], [0.0, 0.2, 0.0]])
    lo, hi = vector_y_limits(Y)
    view = VectorView(largest_training_pose(Y), limits=vector_y_limits(Y))
    np.testing.assert_allclose((view.fig.y_range.start, view.fig.y_range.end), (lo, hi))


def test_examples_oil_is_servable_entry():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    example = (root / "examples" / "oil.py").read_text()
    host = (root / "src" / "vidden" / "host" / "panel.py").read_text()
    view = (root / "src" / "vidden" / "views" / "vector.py").read_text()
    assert ".servable()" in example
    assert "sys.path.insert" in example
    assert ".servable()" not in host
    assert ".servable()" not in view
