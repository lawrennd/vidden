import numpy as np
import pytest

from vidden.tree import (
    Hierarchy,
    Mapping,
    TreeNode,
    assemble_figure,
    cascade,
    chain_connect,
    chain_pose,
    composite_stick,
    figure_pose,
    make_synthetic_hierarchy,
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


def test_tree_explorer_builds_without_serving():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    import holoviews as hv
    from vidden.host.tree import tree_explorer

    app = tree_explorer(make_synthetic_hierarchy(n=8))
    assert app is not None
    assert len(app) >= 3
    default = tree_explorer()
    assert default is not None
    parent = app[1][0]
    obj = parent.object if hasattr(parent, "object") else parent
    hv.render(obj, backend="bokeh")


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
