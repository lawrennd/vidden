import numpy as np
import pytest

from vidden.views.image import ImageView, image_color_limits, reshape_image


def test_reshape_c_order_then_transpose():
    y = np.arange(6, dtype=float)
    img = reshape_image(y, (2, 3), order="C", transpose=False)
    np.testing.assert_array_equal(img, [[0, 1, 2], [3, 4, 5]])
    img_t = reshape_image(y, (2, 3), order="C", transpose=True)
    np.testing.assert_array_equal(img_t, [[0, 3], [1, 4], [2, 5]])


def test_reshape_fortran_order_brendan_flags():
    y = np.arange(6, dtype=float)
    img = reshape_image(y, (2, 3), order="F", transpose=False)
    np.testing.assert_array_equal(img, [[0, 2, 4], [1, 3, 5]])
    img_t = reshape_image(y, (2, 3), order="F", transpose=True)
    np.testing.assert_array_equal(img_t, [[0, 1], [2, 3], [4, 5]])


def test_reshape_invert_and_preset():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    img = reshape_image(y, (2, 2), invert=True, preset_mean=1.0, preset_std=2.0)
    np.testing.assert_allclose(img, -np.array([[1.0, 2.0], [3.0, 4.0]]) * 2.0 + 1.0)


def test_reshape_rejects_short_vector():
    with pytest.raises(ValueError, match="shorter"):
        reshape_image(np.zeros(3), (2, 2))


def test_image_color_limits_use_training_matrix():
    Y = np.array([[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 4.0]])
    lo, hi = image_color_limits(Y, (2, 2), invert=False)
    np.testing.assert_allclose((lo, hi), (0.0, 4.0))
    lo_i, hi_i = image_color_limits(Y, (2, 2), invert=True)
    np.testing.assert_allclose((lo_i, hi_i), (-4.0, 0.0))
    lo_c, hi_c = image_color_limits(np.ones((3, 4)), (2, 2))
    np.testing.assert_allclose((lo_c, hi_c), (1.0, 2.0))
    lo_p, hi_p = image_color_limits(Y, (2, 2), preset_mean=1.0, preset_std=2.0)
    np.testing.assert_allclose((lo_p, hi_p), (1.0, 9.0))


def test_image_view_constant_frame_has_colour_span():
    pytest.importorskip("bokeh")
    view = ImageView(np.ones(4), (2, 2))
    assert view.mapper.high == view.mapper.low + 1.0


def test_image_view_modify_does_not_change_axes_or_clim():
    pytest.importorskip("bokeh")
    y0 = np.linspace(0.0, 1.0, 20 * 28)
    y1 = np.linspace(0.2, 0.8, 20 * 28)
    view = ImageView(y0, (20, 28), transpose=True, order="F", color_limits=(0.0, 1.0))
    ranges0 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    clim0 = (view.mapper.low, view.mapper.high)
    view.modify(y1)
    ranges1 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    np.testing.assert_allclose(ranges1, ranges0)
    assert (view.mapper.low, view.mapper.high) == clim0
    expected = np.flipud(reshape_image(y1, (20, 28), order="F", transpose=True))
    np.testing.assert_allclose(view.source.data["image"][0], expected)


def test_reconstruct_mean_writes_image_view():
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.models import assemble_latent, latent_mean_row, reconstruct_mean

    np.random.seed(1)
    Y = np.random.randn(8, 20 * 28)
    model = GPy.models.GPLVM(Y, 2)
    z = assemble_latent(latent_mean_row(model), 0.1, -0.2, 0, 1)
    mu = reconstruct_mean(model, z)
    view = ImageView(Y[0], (20, 28), transpose=True, order="F", color_limits=(-3.0, 3.0))
    ranges0 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    view.modify(mu)
    expected = np.flipud(reshape_image(mu, (20, 28), order="F", transpose=True))
    np.testing.assert_allclose(view.source.data["image"][0], expected)
    ranges1 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    np.testing.assert_allclose(ranges1, ranges0)
    assert (view.mapper.low, view.mapper.high) == (-3.0, 3.0)


def test_face_explorer_builds_without_serving():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.host.panel import face_explorer, latent_explorer
    from vidden.views.image import ImageView

    np.random.seed(2)
    Y = np.random.randn(6, 20 * 28)
    model = GPy.models.GPLVM(Y, 2)
    model.image_dimensions = (20, 28)
    model.image_transpose = True
    model.image_order = "F"
    model.image_invert = False
    view = ImageView(Y[0], (20, 28), transpose=True, order="F")
    app = latent_explorer(model, view)
    assert app is not None
    wrapped = face_explorer(model=model)
    assert wrapped is not None
    assert len(wrapped) >= 3


def test_examples_faces_is_servable_entry():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    example = (root / "examples" / "faces.py").read_text()
    host = (root / "src" / "vidden" / "host" / "panel.py").read_text()
    view = (root / "src" / "vidden" / "views" / "image.py").read_text()
    assert ".servable()" in example
    assert "sys.path.insert" in example
    assert ".servable()" not in host
    assert ".servable()" not in view
