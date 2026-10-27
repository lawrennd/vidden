import numpy as np
import pytest

from vidden.views.vector import VectorView, vector_y_limits


def test_vector_y_limits_pad_around_range():
    lo, hi = vector_y_limits([-1.0, 1.0], pad=0.1)
    np.testing.assert_allclose((lo, hi), (-1.2, 1.2))


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
