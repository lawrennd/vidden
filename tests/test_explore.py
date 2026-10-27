import numpy as np
import pytest

from vidden.explore import (
    StickView,
    assemble_latent,
    assemble_latent_nearest,
    bar_index_from_event_x,
    cubic_axis_limits,
    disable_bokeh_context_menu,
    event_has_shift,
    install_bar_x_menu,
    input_sensitivity_values,
    menu_item_dimension,
    largest_training_pose,
    latent_array,
    latent_axis_limits,
    latent_mean_row,
    latent_posterior_density_grid,
    matlab_view_project,
    most_significant_dims,
    reconstruct_mean,
    sensitivity_bar_ylim,
    stick_bone_segments,
    stick_polylines,
    y_to_xyz,
)


def test_y_to_xyz_matches_visualize_reshape():
    y = np.arange(12, dtype=float)
    xyz = y_to_xyz(y)
    assert xyz.shape == (4, 3)
    np.testing.assert_array_equal(xyz, y.reshape(3, 4).T)
    with pytest.raises(ValueError, match="divisible by 3"):
        y_to_xyz(np.arange(4, dtype=float))


def test_cubic_axis_limits_degenerate_pose_has_span():
    xyz = np.zeros((3, 3))
    lim = cubic_axis_limits(xyz)
    assert lim.shape == (3, 2)
    assert np.all(lim[:, 1] > lim[:, 0])


def test_assemble_latent_writes_two_axes_only():
    mean = np.array([[1.0, 2.0, 3.0, 4.0]])
    z = assemble_latent(mean, x=9.0, y=-1.0, dim_x=0, dim_y=2)
    np.testing.assert_allclose(z, [[9.0, 2.0, -1.0, 4.0]])
    np.testing.assert_allclose(mean, [[1.0, 2.0, 3.0, 4.0]])
    z0 = assemble_latent(np.zeros((1, 4)), x=0.5, y=-0.25, dim_x=0, dim_y=1)
    np.testing.assert_allclose(z0, [[0.5, -0.25, 0.0, 0.0]])


def test_assemble_latent_nearest_uses_closest_training_row():
    X = np.array([[0.0, 10.0, 0.0], [1.0, 20.0, 1.0]])
    z = assemble_latent_nearest(X, 0.1, 0.0, 0, 2)
    np.testing.assert_allclose(z, [[0.1, 10.0, 0.0]])
    z2 = assemble_latent_nearest(X, 0.9, 1.0, 0, 2)
    np.testing.assert_allclose(z2, [[0.9, 20.0, 1.0]])


def test_stick_polylines_insert_nans_between_bones():
    xyz = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
    connect = np.zeros((3, 3))
    connect[0, 1] = 1.0
    connect[1, 2] = 1.0
    xs, ys, zs = stick_polylines(xyz, connect)
    assert np.isnan(xs[2])
    assert xs[0] == 0.0 and xs[1] == 1.0


def test_latent_row_from_gplvm_is_writable_and_2d():
    GPy = pytest.importorskip("GPy")

    np.random.seed(0)
    model = GPy.models.GPLVM(np.random.randn(8, 9), 2)
    row = latent_mean_row(model)
    assert row.shape == (1, 2)
    row[0, 0] = 99.0
    assert model.X[0, 0] != 99.0
    arr = latent_array(model)
    assert arr.shape == (8, 2)


def test_latent_row_from_bayesian_gplvm_uses_posterior_mean():
    GPy = pytest.importorskip("GPy")

    np.random.seed(3)
    model = GPy.models.BayesianGPLVM(np.random.randn(12, 9), 4, num_inducing=5)
    row = latent_mean_row(model)
    assert row.shape == (1, 4)
    row[0, 0] = 99.0
    assert float(model.X.mean[0, 0]) != 99.0
    assert latent_array(model).shape == (12, 4)


def test_cubic_axis_limits_match_visualize_finalize_axes():
    xyz = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    limits = cubic_axis_limits(xyz, pad=0.0)
    spans = limits[:, 1] - limits[:, 0]
    np.testing.assert_allclose(spans, spans[0])
    np.testing.assert_allclose(spans[0], 2.0)
    np.testing.assert_allclose(np.mean(limits, axis=1), [1.0, 0.5, 0.0])


def test_largest_training_pose_matches_matlab_lvm_visualise():
    Y = np.array([[1.0, 0.0, 0.0], [0.0, 3.0, 4.0], [0.0, 1.0, 0.0]])
    np.testing.assert_array_equal(largest_training_pose(Y), Y[1])


def test_matlab_view_project_puts_z_up():
    xyz = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    u, v = matlab_view_project(xyz)
    assert v[1] > v[0]


def test_stick_bone_segments_match_matlab_line_handles():
    xyz = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
    connect = np.zeros((3, 3))
    connect[0, 1] = 1.0
    connect[1, 2] = 1.0
    u, v = matlab_view_project(xyz)
    xs, ys = stick_bone_segments(u, v, connect)
    assert len(xs) == 2
    np.testing.assert_allclose(xs[0], [u[0], u[1]])
    np.testing.assert_allclose(ys[1], [v[1], v[2]])


def test_stick_view_modify_updates_data_not_axes():
    pytest.importorskip("bokeh")
    y0 = np.array([0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0])
    y1 = y0 * 0.25
    connect = np.zeros((3, 3))
    connect[0, 1] = 1.0
    connect[1, 2] = 1.0
    view = StickView(y0, connect)
    ranges0 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    view.modify(y1)
    ranges1 = (view.fig.x_range.start, view.fig.x_range.end, view.fig.y_range.start, view.fig.y_range.end)
    np.testing.assert_allclose(ranges1, ranges0)
    u, v = matlab_view_project(y_to_xyz(y1))
    np.testing.assert_allclose(view.joint_source.data["x"], u)
    np.testing.assert_allclose(view.joint_source.data["y"], v)
    assert view.fig.x_range.start == ranges0[0]


def test_stick_view_keeps_visualise_limits():
    pytest.importorskip("bokeh")
    y = np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    view = StickView(y, np.eye(3))
    x0, x1 = view.fig.x_range.start, view.fig.x_range.end
    view.modify(y * 0.1)
    assert view.fig.x_range.start == x0
    assert view.fig.x_range.end == x1


def test_latent_axis_limits_come_from_training_points():
    xy = np.array([[-1.0, 0.0], [1.0, 2.0]])
    xlim, ylim = latent_axis_limits(xy, pad=0.0)
    assert xlim == (-1.0, 1.0)
    assert ylim == (0.0, 2.0)


def test_reconstruct_mean_matches_predict_mean():
    GPy = pytest.importorskip("GPy")

    np.random.seed(8)
    model = GPy.models.GPLVM(np.random.randn(8, 6), 2)
    z = latent_mean_row(model)
    mu, _ = model.predict(z)
    np.testing.assert_allclose(reconstruct_mean(model, z), mu[0])


def test_predict_from_assembled_latent():
    GPy = pytest.importorskip("GPy")

    np.random.seed(1)
    Y = np.random.randn(10, 9)
    model = GPy.models.GPLVM(Y, 2)
    z = assemble_latent(latent_mean_row(model), 0.1, -0.2, 0, 1)
    mu, _ = model.predict(z)
    assert mu.shape == (1, 9)
    pytest.importorskip("bokeh")
    view = StickView(mu[0], np.eye(3))
    view.modify(mu[0])
    assert len(view.joint_source.data["x"]) == 3


def test_bar_index_from_event_x_accepts_numeric_and_factor():
    assert bar_index_from_event_x(2.4, 6) == 2
    assert bar_index_from_event_x("3", 6) == 3
    assert bar_index_from_event_x(-1, 6) is None
    assert bar_index_from_event_x(9, 6) is None
    assert bar_index_from_event_x(None, 6) is None
    assert bar_index_from_event_x("nope", 6) is None
    assert bar_index_from_event_x(object(), 6) is None


def test_event_has_shift_reads_bokeh_modifiers():
    class _Evt:
        def __init__(self, modifiers):
            self.modifiers = modifiers

    assert event_has_shift(_Evt({"shift": True, "ctrl": False, "alt": False}))
    assert not event_has_shift(_Evt({"shift": False}))
    assert not event_has_shift(_Evt(None))

    class _Mods:
        shift = True

    assert event_has_shift(_Evt(_Mods()))


def test_disable_bokeh_context_menu_clears_auto_tool_menu():
    pytest.importorskip("bokeh")
    from bokeh.plotting import figure

    fig = figure()
    assert fig.context_menu == "auto"
    disable_bokeh_context_menu(fig)
    assert fig.context_menu is None


def test_install_bar_x_menu_uses_bokeh_menu_item_click():
    pytest.importorskip("bokeh")
    from bokeh.models import Menu
    from bokeh.plotting import figure

    fig = figure()
    picked = []
    install_bar_x_menu(fig, 6, picked.append)
    assert isinstance(fig.context_menu, Menu)
    assert len(fig.context_menu.items) == 6
    assert "menu_item_click" in fig.subscribed_events
    from bokeh.events import MenuItemClick

    fig._trigger_event(MenuItemClick(fig, item="2"))
    assert picked == ["2"]


def test_menu_item_dimension_reads_item_label():
    assert menu_item_dimension("3", 6) == 3
    assert menu_item_dimension("x-axis 4", 6) == 4
    assert menu_item_dimension("9", 6) is None
    assert menu_item_dimension(None, 6) is None


def test_most_significant_dims_follow_input_sensitivity():
    GPy = pytest.importorskip("GPy")

    np.random.seed(5)
    model = GPy.models.GPLVM(np.random.randn(10, 6), 3)
    dim_x, dim_y = most_significant_dims(model)
    assert dim_x != dim_y
    assert {dim_x, dim_y} <= {0, 1, 2}
    assert input_sensitivity_values(model).shape == (3,)


def test_sensitivity_bar_ylim_follows_current_peak():
    lo, hi = sensitivity_bar_ylim([4.0, 4.0, 4.0], pad=0.1)
    assert lo == 0.0
    np.testing.assert_allclose(hi, 4.4)
    lo, hi = sensitivity_bar_ylim([0.003, 0.001, 0.002], pad=0.1)
    assert lo == 0.0
    np.testing.assert_allclose(hi, 0.0033)
    lo, hi = sensitivity_bar_ylim([0.0, 0.0])
    assert hi > 0.0


def test_latent_posterior_density_grid_matches_matlab_shape():
    GPy = pytest.importorskip("GPy")

    np.random.seed(6)
    model = GPy.models.GPLVM(np.random.randn(8, 6), 2)
    xlim, ylim = ((-1.0, 1.0), (-2.0, 2.0))
    x1, x2, density = latent_posterior_density_grid(model, 0, 1, xlim, ylim, resolution=7)
    assert x1.shape == (7,)
    assert x2.shape == (7,)
    assert density.shape == (7, 7)
    assert np.isfinite(density).all()
    centre = density[3, 3]
    corner = density[0, 0]
    assert centre > corner


def test_untrained_predict_collapses_away_from_embeddings():
    """Untrained GP mean is prior zero off the initial X; that is the collapse."""
    GPy = pytest.importorskip("GPy")

    np.random.seed(4)
    Y = np.random.randn(8, 9)
    model = GPy.models.GPLVM(Y, 2)
    at_data = model.predict(latent_mean_row(model))[0]
    far = assemble_latent(latent_mean_row(model), 8.0, -8.0, 0, 1)
    away = model.predict(far)[0]
    assert np.linalg.norm(at_data) > 5 * np.linalg.norm(away)


def test_optimize_stick_model_runs_bfgs():
    GPy = pytest.importorskip("GPy")
    from vidden.explore import optimize_stick_model

    np.random.seed(7)
    model = GPy.models.GPLVM(np.random.randn(8, 6), 2)
    before = float(model.log_likelihood())
    optimize_stick_model(model, max_iters=3)
    assert float(model.log_likelihood()) >= before - 1e-6


def test_stick_explorer_builds_without_serving():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    GPy = pytest.importorskip("GPy")
    from vidden.explore import stick_explorer

    np.random.seed(2)
    Y = np.random.randn(6, 9)
    model = GPy.models.GPLVM(Y, 3)
    model.data = {"connect": np.eye(3)}
    app = stick_explorer(model=model, connect=model.data["connect"])
    assert app is not None
    assert len(app) >= 3
