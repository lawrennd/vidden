import numpy as np
import pytest

from vidden.tree import (
    Hierarchy,
    Mapping,
    TreeNode,
    acclaim_feature_ind,
    assemble_figure,
    cascade,
    chain_connect,
    chain_pose,
    composite_stick,
    figure_pose,
    make_synthetic_hierarchy,
    mocap_xyz_for_stick,
    pca_latent,
    prepare_hgplvm_channels,
    xyz_to_y,
)
from vidden.views.stick import y_to_xyz


def test_xyz_to_y_roundtrip():
    y = chain_pose(0.3)
    xyz = y_to_xyz(y)
    np.testing.assert_allclose(xyz_to_y(xyz), y)


def test_hierarchy_infers_roots_when_omitted():
    hier = make_synthetic_hierarchy(n=6)
    inferred = Hierarchy(nodes=list(hier.nodes), roots=())
    assert inferred.roots == (0,)


def test_mapping_rejects_bad_shapes():
    with pytest.raises(ValueError, match="latent X"):
        Mapping(np.array([0.0, 1.0]), np.zeros((2, 3)))
    with pytest.raises(ValueError, match="aligned"):
        Mapping(np.zeros((2, 2)), np.zeros((3, 4)))


def test_mapping_predict_is_local_interpolant():
    X = np.array([[0.0, 0.0], [1.0, 0.0]])
    Y = np.array([[0.0, 0.0, 0.0, 0.0], [10.0, 20.0, 30.0, 40.0]])
    model = Mapping(X, Y)
    mu, var = model.predict([[0.0, 0.0]])
    np.testing.assert_allclose(mu[0], Y[0])
    mu, _ = model.predict([[0.5, 0.0]])
    assert 2.0 < float(mu[0, 0]) < 8.0
    assert var.shape[0] == 1


def test_mapping_lengthscale_survives_duplicate_latents():
    X = np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 0.0]])
    Y = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    model = Mapping(X, Y)
    assert model._ls2 > 1e-6
    mu, _ = model.predict([[0.5, 0.0]])
    assert float(np.max(np.abs(mu))) > 0.1


def test_click_off_grid_does_not_collapse_arms():
    hier = make_synthetic_hierarchy()
    for node in hier.nodes:
        assert node.model._ls2 > 1e-6
    x0 = hier.nodes[0].model.X[0]
    _, leaves = cascade(hier, 0, float(x0[0]) + 0.08, float(x0[1]) + 0.08)
    packed, _ = figure_pose(hier, leaves)
    xyz = y_to_xyz(packed)
    assert float(np.linalg.norm(xyz[5])) > 0.5
    assert float(np.linalg.norm(xyz[8])) > 0.5


def test_cascade_parent_writes_both_leaves():
    hier = make_synthetic_hierarchy(n=12)
    t = 0
    x, y = float(hier.nodes[0].model.X[t, 0]), float(hier.nodes[0].model.X[t, 1])
    positions, leaves = cascade(hier, 0, x, y)
    assert set(positions) == {0, 1, 2}
    assert set(leaves) == {1, 2}
    np.testing.assert_allclose(positions[1], hier.nodes[1].model.X[t])
    np.testing.assert_allclose(positions[2], hier.nodes[2].model.X[t])
    np.testing.assert_allclose(leaves[1], hier.nodes[1].model.Y[t])
    np.testing.assert_allclose(leaves[2], hier.nodes[2].model.Y[t])


def test_cascade_leaf_does_not_touch_sibling():
    hier = make_synthetic_hierarchy(n=8)
    x, y = float(hier.nodes[1].model.X[1, 0]), float(hier.nodes[1].model.X[1, 1])
    positions, leaves = cascade(hier, 1, x, y)
    assert set(positions) == {1}
    assert set(leaves) == {1}


def test_cascade_can_skip_a_child():
    hier = make_synthetic_hierarchy(n=8)
    x, y = float(hier.nodes[0].model.X[0, 0]), float(hier.nodes[0].model.X[0, 1])
    update = {0: [True, False]}
    positions, leaves = cascade(hier, 0, x, y, update_child=update)
    assert 1 in leaves
    assert 2 not in leaves
    assert 2 not in positions


def test_cascade_rejects_short_parent_output():
    X = np.array([[0.0, 0.0]])
    Y = np.array([[1.0]])
    parent = TreeNode("p", Mapping(X, Y), children=(1,))
    leaf = TreeNode("c", Mapping(X, np.zeros((1, 9))), connect=chain_connect(3))
    hier = Hierarchy(nodes=[parent, leaf], roots=(0,))
    with pytest.raises(ValueError, match="shorter"):
        cascade(hier, 0, 0.0, 0.0)


def test_synthetic_figure_is_one_person_not_two_chains():
    hier = make_synthetic_hierarchy(n=4, n_style=3)
    parent_x = hier.nodes[0].model.X
    assert len(np.unique(np.round(parent_x[:, 0], 5))) >= 4
    assert len(np.unique(np.round(parent_x[:, 1], 5))) >= 3
    assert not np.allclose(hier.nodes[1].model.X, parent_x)
    x, y = float(parent_x[0, 0]), float(parent_x[0, 1])
    _, leaves = cascade(hier, 0, x, y)
    packed, connect = figure_pose(hier, leaves)
    xyz = y_to_xyz(packed)
    assert xyz.shape == (9, 3)
    assert xyz[2, 2] > xyz[1, 2] > xyz[0, 2]
    assert connect[1, 3] == 1.0
    assert connect[1, 6] == 1.0
    reached = {0}
    frontier = [0]
    while frontier:
        i = frontier.pop()
        for j in np.nonzero(connect[i])[0]:
            if int(j) not in reached:
                reached.add(int(j))
                frontier.append(int(j))
    assert 5 in reached
    assert 8 in reached


def test_assemble_figure_clavicle_from_chest():
    torso = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.5]])
    tconn = np.zeros((3, 3))
    tconn[0, 1] = 1.0
    tconn[1, 2] = 1.0
    arm = np.array([[0.4, 0.0, 1.2], [0.7, 0.0, 0.7], [0.9, 0.0, 0.3]])
    packed, connect = assemble_figure(torso, tconn, [(arm, chain_connect(3), 1)])
    xyz = y_to_xyz(packed)
    assert xyz.shape == (6, 3)
    assert connect[1, 3] == 1.0


def test_composite_stick_is_block_diagonal_and_offset():
    y0 = chain_pose(0.2)
    y1 = chain_pose(-0.2)
    connect = chain_connect(3)
    packed, union = composite_stick([y0, y1], [connect, connect], [(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)])
    xyz = y_to_xyz(packed)
    assert xyz.shape == (6, 3)
    np.testing.assert_allclose(xyz[:3], y_to_xyz(y0) + np.array([[-1.0, 0.0, 0.0]]))
    np.testing.assert_allclose(xyz[3:], y_to_xyz(y1) + np.array([[1.0, 0.0, 0.0]]))
    assert union.shape == (6, 6)
    np.testing.assert_allclose(union[:3, :3], connect)
    np.testing.assert_allclose(union[3:, 3:], connect)
    np.testing.assert_allclose(union[:3, 3:], 0.0)


def test_parent_latent_changes_the_figure():
    hier = make_synthetic_hierarchy(n=8, n_style=5)
    x0 = hier.nodes[0].model.X
    _, a = cascade(hier, 0, float(x0[0, 0]), float(x0[0, 1]))
    _, b = cascade(hier, 0, float(x0[5, 0]), float(x0[5, 1]))
    pa, _ = figure_pose(hier, a)
    pb, _ = figure_pose(hier, b)
    assert float(np.max(np.abs(pa - pb))) > 0.2


def _hv_from_panel(obj):
    current = obj
    if hasattr(current, "object"):
        current = current.object
    return current


def _bokeh_fig(obj):
    import holoviews as hv

    overlay = hv.render(_hv_from_panel(obj), backend="bokeh")
    stack = [overlay]
    while stack:
        fig = stack.pop()
        if hasattr(fig, "_trigger_event") and hasattr(fig, "on_event"):
            return fig
        stack.extend(getattr(fig, "children", []) or [])
        stack.extend(getattr(fig, "renderers", []) or [])
    raise AssertionError("no triggerable Bokeh figure")


def test_tree_explorer_builds_without_serving():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    from vidden.host.tree import tree_explorer

    app = tree_explorer(make_synthetic_hierarchy(n=8))
    assert app is not None
    assert len(app) >= 3
    _bokeh_fig(app[1][0])


def test_tree_explorer_click_cascades_and_can_stop_tracking():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    from bokeh.events import MouseMove, Tap
    from vidden.host.tree import tree_explorer

    hier = make_synthetic_hierarchy(n=8)
    labels = np.array(["a" if i % 2 == 0 else "b" for i in range(len(hier.nodes[0].model.X))])
    for node in hier.nodes:
        node.model.data_labels = labels[: len(node.model.X)]
    app = tree_explorer(hier)
    figs = []
    for row in app[1:-2]:
        for pane in row:
            figs.append(_bokeh_fig(pane))
    parent = figs[0]
    x1, y1 = (float(v) for v in hier.nodes[0].model.X[5, :2])
    parent._trigger_event(Tap(parent, x=x1, y=y1))
    parent._trigger_event(MouseMove(parent, x=None, y=None))
    parent._trigger_event(MouseMove(parent, x=x1 + 0.05, y=y1))
    assert "gait" in str(app[-1].object)
    parent._trigger_event(Tap(parent, x=0.0, y=0.0))
    parent._trigger_event(MouseMove(parent, x=0.0, y=0.0))
    assert "Tracking off" in str(app[-1].object)


def test_tree_explorer_defaults_to_walk_run_then_synthetic(monkeypatch):
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    from vidden.host import tree as host_tree

    hier = make_synthetic_hierarchy(n=4)
    monkeypatch.setattr("vidden.demos.load_walk_run_tree", lambda: hier)
    app = host_tree.tree_explorer()
    assert app is not None

    def _boom():
        raise ImportError("no pods")

    monkeypatch.setattr("vidden.demos.load_walk_run_tree", _boom)
    fallback = host_tree.tree_explorer()
    assert fallback is not None


def test_set_cursor_accepts_holder_source_or_nothing():
    pytest.importorskip("bokeh")
    from bokeh.models import ColumnDataSource
    from vidden.host.tree import _set_cursor

    _set_cursor(None, (1.0, 2.0))
    _set_cursor({}, (1.0, 2.0))
    source = ColumnDataSource(data={"x": [0.0], "y": [0.0]})
    _set_cursor({"source": source}, (0.3, -0.4))
    assert source.data["x"] == [0.3]
    assert source.data["y"] == [-0.4]
    _set_cursor(source, (1.5, 2.5))
    assert source.data["x"] == [1.5]


def test_examples_tree_is_servable_entry():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    example = (root / "examples" / "tree.py").read_text()
    host = (root / "src" / "vidden" / "host" / "tree.py").read_text()
    core = (root / "src" / "vidden" / "tree.py").read_text()
    assert ".servable()" in example
    assert "sys.path.insert" in example
    assert ".servable()" not in host
    assert ".servable()" not in core
    assert "hv.DynamicMap" not in host
    assert "streams.Pipe" not in host
    assert "load_walk_run_tree" in host
    assert "cmu_mocap" in example or "walk" in example.lower()


def test_mocap_height_is_stick_z():
    xyz = np.array([[1.0, 17.0, -28.0]])
    np.testing.assert_allclose(mocap_xyz_for_stick(xyz), [[1.0, -28.0, 17.0]])


def test_prepare_hgplvm_channels_pins_ground_plane():
    Y = np.array([[1.5, 17.0, -28.0, 400.0, -10.0]])
    out = prepare_hgplvm_channels(Y)
    np.testing.assert_allclose(out[0, :3], [0.0, 17.0, 0.0])
    assert -90.0 <= out[0, 3] <= 90.0


def test_pca_latent_is_two_d():
    rng = np.random.default_rng(0)
    X = pca_latent(rng.normal(size=(20, 8)))
    assert X.shape == (20, 2)


def test_walk_run_tree_matches_acclaim_split():
    pytest.importorskip("pods")
    from vidden.demos import load_walk_run_tree

    hier = load_walk_run_tree()
    names = [node.name for node in hier.nodes]
    assert names == [
        "skeleton",
        "abdomen",
        "legs",
        "upper body",
        "left leg",
        "right leg",
        "left arm",
        "head",
        "right arm",
    ]
    assert hier.roots == (0,)
    assert hier.skel is not None
    assert hier.nodes[0].children == (1, 2, 3)
    assert hier.nodes[2].children == (4, 5)
    assert hier.nodes[3].children == (6, 7, 8)
    leaves = [i for i, node in enumerate(hier.nodes) if not node.children]
    assert leaves == [1, 4, 5, 6, 7, 8]
    n = hier.nodes[0].model.X.shape[0]
    assert n == 21 + 34
    labels = hier.nodes[0].model.data_labels
    assert list(labels[:21]) == ["run"] * 21
    assert list(labels[21:]) == ["walk"] * 34
    abd = acclaim_feature_ind(
        hier.skel,
        "root",
        ("lclavicle", "rclavicle", "lowerneck", "lhipjoint", "rhipjoint"),
    )
    np.testing.assert_array_equal(hier.nodes[1].feature_ind, abd)
    assert 0 in set(abd) and 1 in set(abd) and 2 in set(abd)
    x0 = hier.nodes[0].model.X
    _, a = cascade(hier, 0, float(x0[0, 0]), float(x0[0, 1]))
    _, b = cascade(hier, 0, float(x0[-1, 0]), float(x0[-1, 1]))
    pa, connect = figure_pose(hier, a)
    pb, _ = figure_pose(hier, b)
    assert y_to_xyz(pa).shape[0] == len(hier.skel.vertices)
    assert connect.shape[0] == len(hier.skel.vertices)
    assert float(np.max(np.abs(pa - pb))) > 0.2
    # Height lives in stick z after the Acclaim permute.
    xyz = y_to_xyz(pa)
    assert float(np.ptp(xyz[:, 2])) > float(np.ptp(xyz[:, 1]))
