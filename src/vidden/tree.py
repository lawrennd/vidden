"""Duck-typed hierarchical GP-LVM tree (Lawrence and Moore, ICML 2007).

A parent node's output is concatenated 2-D coordinates, one pair per
child. Only leaves map to pose. The host calls :func:`cascade`; it does
not need a GPy ``HGPLVM`` class.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from vidden.models import reconstruct_mean
from vidden.views.stick import y_to_xyz


@dataclass
class TreeNode:
    """One latent space in the hierarchy."""

    name: str
    model: object
    children: tuple = ()
    connect: object = None
    offset: tuple = (0.0, 0.0, 0.0)
    attach: object = None


@dataclass
class Hierarchy:
    """Indexed nodes. ``roots`` are nodes with no parent in this list."""

    nodes: list
    roots: tuple = field(default_factory=tuple)
    torso_xyz: object = None
    torso_connect: object = None

    def __post_init__(self):
        if not self.roots:
            childed = {c for node in self.nodes for c in node.children}
            self.roots = tuple(i for i in range(len(self.nodes)) if i not in childed)


class Mapping:
    """Local RBF interpolant so a synthetic tree needs no GPy.

    Nearest-neighbour snapping holds the pose until the pointer crosses
    a Voronoi edge, which feels like nothing is happening. The mean is
    a Gaussian-weighted average of training outputs; exact hits still
    return that row so cascade tests at ``X[t]`` stay interpolating.
    """

    def __init__(self, X, Y):
        self.X = np.asarray(X, dtype=float)
        self.Y = np.asarray(Y, dtype=float)
        if self.X.ndim != 2 or self.X.shape[1] < 2:
            raise ValueError("latent X must be (N, Q) with Q >= 2")
        if self.Y.ndim != 2 or self.Y.shape[0] != self.X.shape[0]:
            raise ValueError("Y must be (N, D) aligned with X")
        self.input_dim = self.X.shape[1]
        self.output_dim = self.Y.shape[1]
        self._ls2 = _rbf_lengthscale_sq(self.X[:, :2])

    def predict(self, z):
        z = np.atleast_2d(np.asarray(z, dtype=float))
        d2 = ((self.X[:, None, :2] - z[None, :, :2]) ** 2).sum(axis=2)
        idx = d2.argmin(axis=0)
        ls2 = self._ls2 if self._ls2 > 0.0 else 1.0
        w = np.exp(-0.5 * d2 / ls2)
        peak = w.max(axis=0)
        w_sum = w.sum(axis=0, keepdims=True)
        mu = np.zeros((z.shape[0], self.Y.shape[1]), dtype=float)
        ok = peak >= 1e-8
        if np.any(ok):
            mu[ok] = (w[:, ok] / np.maximum(w_sum[:, ok], 1e-15)).T @ self.Y
        if np.any(~ok):
            mu[~ok] = self.Y[idx[~ok]]
        hit = d2.min(axis=0) < 1e-16
        if np.any(hit):
            mu[hit] = self.Y[idx[hit]]
        var = (d2.min(axis=0) + 1e-3)[:, None]
        return mu, var


def _rbf_lengthscale_sq(X):
    """Median nearest-neighbour squared distance, floored on the data span.

    Duplicate latent rows (``sin(0)`` and ``sin(π)`` in the arm spaces) make
    the raw nearest-neighbour distance zero. A zero lengthscale underflows
    the kernel off the training points and the pose collapses to the origin.
    """
    X = np.asarray(X, dtype=float)
    if X.shape[0] < 2:
        return 1.0
    span = X.max(axis=0) - X.min(axis=0)
    span2 = float(np.sum(span * span))
    floor = 0.01 * span2 if span2 > 0.0 else 1.0
    d2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(d2, np.inf)
    d2 = np.where(d2 < 1e-12, np.inf, d2)
    nn = d2.min(axis=1)
    finite = nn[np.isfinite(nn)]
    med = float(np.median(finite)) if finite.size else 0.0
    if not np.isfinite(med) or med <= 0.0:
        med = floor
    return max(2.0 * med, floor)


def xyz_to_y(xyz):
    """Inverse of :func:`vidden.views.stick.y_to_xyz`."""
    xyz = np.asarray(xyz, dtype=float)
    return xyz.T.ravel()


def chain_connect(n_joints=3):
    """Open kinematic chain: joint i connected to i+1."""
    connect = np.zeros((n_joints, n_joints))
    for i in range(n_joints - 1):
        connect[i, i + 1] = 1.0
    return connect


def chain_pose(angle, n_joints=3, length=1.0):
    """Packed stick vector for a planar chain with equal hinge angles."""
    pts = np.zeros((n_joints, 3))
    heading = 0.0
    for i in range(1, n_joints):
        heading += float(angle)
        pts[i, 0] = pts[i - 1, 0] + length * np.cos(heading)
        pts[i, 1] = pts[i - 1, 1] + length * np.sin(heading)
    return xyz_to_y(pts)


def torso_xyz():
    """Pelvis, chest, head. Height is ``z``, as in mocap / ``StickView``."""
    return np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.85],
            [0.0, 0.0, 1.48],
        ],
        dtype=float,
    )


def torso_connect():
    connect = np.zeros((3, 3))
    connect[0, 1] = 1.0
    connect[1, 2] = 1.0
    return connect


def arm_xyz(side, shoulder_deg, elbow_deg):
    """Three-joint arm in world space. ``side`` is -1 (left) or +1 (right).

    Angle 0 hangs down (−z). Positive raises to that side and slightly
    forward (+y) so the MATLAB camera sees the swing, not an xz cardboard.
    """
    s = float(side)
    sh = np.array([0.42 * s, 0.0, 1.18], dtype=float)
    a1 = np.deg2rad(float(shoulder_deg))
    a2 = np.deg2rad(float(elbow_deg))
    upper, lower = 0.55, 0.50
    c1, s1 = np.cos(a1), np.sin(a1)
    c2, s2 = np.cos(a1 + a2), np.sin(a1 + a2)
    elbow = sh + np.array([s * upper * s1, 0.40 * upper * s1, -upper * c1])
    hand = elbow + np.array([s * lower * s2, 0.40 * lower * s2, -lower * c2])
    return np.vstack([sh, elbow, hand])


def assemble_figure(torso, torso_edges, limbs):
    """One skeleton: static torso plus limbs attached at torso joints.

    ``limbs`` is ``(xyz, connect, torso_parent_index)`` per leaf. The first
    joint of each limb is a child of that torso joint (a clavicle).
    """
    torso = np.asarray(torso, dtype=float)
    parts = [torso]
    n_torso = int(torso.shape[0])
    blocks = [(0, n_torso, np.asarray(torso_edges, dtype=float), None)]
    start = n_torso
    for limb_xyz, limb_connect, parent in limbs:
        limb_xyz = np.asarray(limb_xyz, dtype=float)
        j = int(limb_xyz.shape[0])
        blocks.append((start, start + j, np.asarray(limb_connect, dtype=float), int(parent)))
        parts.append(limb_xyz)
        start += j
    xyz = np.vstack(parts)
    n = int(xyz.shape[0])
    connect = np.zeros((n, n))
    for i0, i1, block, parent in blocks:
        connect[i0:i1, i0:i1] = block
        if parent is not None:
            connect[parent, i0] = 1.0
    return xyz_to_y(xyz), connect


def figure_pose(hierarchy, leaf_ys):
    """Packed composite pose for the current leaf reconstructions."""
    leaves = [i for i, node in enumerate(hierarchy.nodes) if not node.children]
    if hierarchy.torso_xyz is None:
        ys = [leaf_ys[i] for i in leaves]
        connects = [hierarchy.nodes[i].connect for i in leaves]
        offsets = [hierarchy.nodes[i].offset for i in leaves]
        return composite_stick(ys, connects, offsets)
    limbs = []
    for i in leaves:
        node = hierarchy.nodes[i]
        parent = 1 if node.attach is None else int(node.attach)
        limbs.append((y_to_xyz(leaf_ys[i]), node.connect, parent))
    return assemble_figure(hierarchy.torso_xyz, hierarchy.torso_connect, limbs)


def composite_stick(leaf_ys, connects, offsets):
    """Block-diagonal skeleton: each leaf's joints, offset in world space."""
    xyz_parts = []
    n_joints = []
    for y, offset in zip(leaf_ys, offsets, strict=True):
        xyz = y_to_xyz(y) + np.asarray(offset, dtype=float).reshape(1, 3)
        xyz_parts.append(xyz)
        n_joints.append(int(xyz.shape[0]))
    xyz = np.vstack(xyz_parts)
    n = int(sum(n_joints))
    connect = np.zeros((n, n))
    start = 0
    for block, j in zip(connects, n_joints, strict=True):
        block = np.asarray(block, dtype=float)
        connect[start : start + j, start : start + j] = block
        start += j
    return xyz_to_y(xyz), connect


def cascade(hierarchy, index, x, y, *, update_child=None):
    """MATLAB ``updateVisualisation``: parent ``(x, y)`` writes descendants.

    Returns ``(positions, leaves)``. ``positions[i]`` is the 2-D latent
    coordinate of node ``i``. ``leaves[i]`` is the reconstructed pose of
    a leaf. Parent output is pairs ``(mu[2i], mu[2i+1])`` for child ``i``.
    """
    nodes = hierarchy.nodes
    node = nodes[int(index)]
    mu = np.asarray(reconstruct_mean(node.model, [[float(x), float(y)]]), dtype=float).reshape(-1)
    positions = {int(index): np.array([float(x), float(y)], dtype=float)}
    leaves = {}
    children = tuple(node.children)
    if children:
        for i, child in enumerate(children):
            if update_child is not None and not update_child[int(index)][i]:
                continue
            if mu.size < 2 * (i + 1):
                raise ValueError(
                    f"node {index} output length {mu.size} is shorter than "
                    f"2×{len(children)} child coordinates"
                )
            cx, cy = float(mu[2 * i]), float(mu[2 * i + 1])
            sub_pos, sub_leaves = cascade(hierarchy, child, cx, cy, update_child=update_child)
            positions.update(sub_pos)
            leaves.update(sub_leaves)
    else:
        leaves[int(index)] = mu
    return positions, leaves


def make_synthetic_hierarchy(n=8, n_style=5):
    """Parent (phase × style) with left and right arm leaves.

    Parent ``Y`` is concatenated child latent coordinates, as in MATLAB
    HGPLVM. Arms hang in ``z`` (mocap up) and attach to a shared torso so
    the reconstruction is one figure, not two floating chains. Child
    latents are arm angles, not copies of the parent's circle. ``Mapping``
    interpolates, so dragging gait swings the arms instead of snapping.
    """
    phases = np.linspace(0.0, 2.0 * np.pi, int(n), endpoint=False)
    styles = np.linspace(-1.0, 1.0, int(n_style))
    phase, style = np.meshgrid(phases, styles, indexing="ij")
    phase = phase.reshape(-1)
    style = style.reshape(-1)
    xp = np.column_stack((phase / np.pi - 1.0, style))
    left_raise = np.sin(phase)
    left_bend = 0.6 * style
    right_raise = np.sin(phase + np.pi)
    right_bend = -0.6 * style
    x_left = np.column_stack((left_raise, left_bend))
    x_right = np.column_stack((right_raise, right_bend))

    def _deg(raise_n, bend_n):
        shoulder = 8.0 + 110.0 * 0.5 * (float(raise_n) + 1.0)
        elbow = 8.0 + 70.0 * 0.5 * (float(bend_n) + 1.0)
        return shoulder, elbow

    y_left = np.stack([xyz_to_y(arm_xyz(-1.0, *_deg(r, b))) for r, b in zip(left_raise, left_bend, strict=True)])
    y_right = np.stack([xyz_to_y(arm_xyz(1.0, *_deg(r, b))) for r, b in zip(right_raise, right_bend, strict=True)])
    yp = np.hstack([x_left, x_right])
    connect = chain_connect(3)
    parent = TreeNode("gait", Mapping(xp, yp), children=(1, 2))
    left = TreeNode("left arm", Mapping(x_left, y_left), connect=connect, attach=1)
    right = TreeNode("right arm", Mapping(x_right, y_right), connect=connect, attach=1)
    return Hierarchy(
        nodes=[parent, left, right],
        roots=(0,),
        torso_xyz=torso_xyz(),
        torso_connect=torso_connect(),
    )
