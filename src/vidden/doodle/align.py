"""Stroke correspondence for a doodle family.

Hungarian matching of unordered polylines onto a template. No drawing,
no files, no Panel. Packed ``Y`` is what :func:`vidden.host.panel.doodle_explorer`
already consumes.
"""

from __future__ import annotations

import numpy as np

from vidden.doodle.geometry import StrokeSpec, pack_doodle, resample_stroke

EXTRA_GREY = "#b8b8b8"
TAB10 = (
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
)


def stroke_palette(n):
    """``n`` distinct colours, cycling Tableau-10."""
    if n <= 0:
        return []
    return [TAB10[i % len(TAB10)] for i in range(n)]


def query_match_colors(n_query, assignment, colors=None):
    """Hex colour per query stroke. Grey if that stroke was not matched."""
    assignment = np.asarray(assignment, dtype=int)
    palette = colors if colors is not None else stroke_palette(len(assignment))
    out = [EXTRA_GREY] * max(int(n_query), 0)
    for i, j in enumerate(assignment):
        if j >= 0 and j < len(out):
            out[int(j)] = palette[i]
    return out


def looks_closed(points, factor=2.5):
    """True when the start–end gap is comparable to a typical segment length."""
    pts = np.asarray(points, dtype=float)
    if len(pts) < 4:
        return False
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1)).mean()
    gap = np.linalg.norm(pts[0] - pts[-1])
    return gap < factor * (seg + 1e-8)


def typical_template_index(doodles):
    """Index of a doodle whose stroke count is the most common.

    The packed topology should be a typical drawing, not the one with extras
    (a tongue, a hat). Extra strokes on other drawings are dropped; missing
    ones become NaN.
    """
    counts = [len(doodle) for doodle in doodles]
    if not counts:
        raise ValueError("need at least one doodle")
    freq = {}
    for count in counts:
        freq[count] = freq.get(count, 0) + 1
    mode = max(freq.values())
    typical = min(count for count, n in freq.items() if n == mode)
    return next(i for i, count in enumerate(counts) if count == typical)


def _centroid_length(points):
    pts = np.asarray(points, dtype=float)
    centroid = pts.mean(axis=0)
    seglen = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1)).sum() if len(pts) > 1 else 0.0
    return centroid, seglen


def _aligned_mse(template, query, closed):
    """Best MSE of ``query`` against ``template`` over reverse and cyclic shifts."""
    t = np.asarray(template, dtype=float)
    q = np.asarray(query, dtype=float)
    n = len(t)
    if len(q) != n:
        q = resample_stroke(q, n, closed=closed)
    best_mse = np.inf
    best = q
    for seq in (q, q[::-1].copy()):
        if closed:
            for k in range(n):
                cand = np.roll(seq, k, axis=0)
                mse = float(np.mean((cand - t) ** 2))
                if mse < best_mse:
                    best_mse = mse
                    best = cand
        else:
            mse = float(np.mean((seq - t) ** 2))
            if mse < best_mse:
                best_mse = mse
                best = seq
    return best_mse, best


def _match_parameterization(template, query, closed):
    """Reverse / cyclic-align ``query`` to ``template`` without translating it.

    Scoring uses centred polylines so a frown mouth can still match a smile
    mouth. The returned polyline keeps the query's original position: vertex
    correspondence is a parameterization, not a Procrustes onto the template.
    """
    t = np.asarray(template, dtype=float)
    q = np.asarray(query, dtype=float)
    t0 = t - t.mean(axis=0)
    best_mse = np.inf
    best = q
    for seq in (q, q[::-1].copy()):
        seq0 = seq - seq.mean(axis=0)
        if closed:
            for k in range(len(seq)):
                mse = float(np.mean((np.roll(seq0, k, axis=0) - t0) ** 2))
                if mse < best_mse:
                    best_mse = mse
                    best = np.roll(seq, k, axis=0)
        else:
            mse = float(np.mean((seq0 - t0) ** 2))
            if mse < best_mse:
                best_mse = mse
                best = seq
    return best_mse, best


def pair_cost_and_align(template, query, closed, n_shape=24, centroid_weight=0.6, length_weight=0.15):
    """Cost of matching ``query`` to ``template``, and the resampled aligned stroke."""
    template = np.asarray(template, dtype=float)
    query = np.asarray(query, dtype=float)
    n = len(template)
    ct, lt = _centroid_length(template)
    cq, lq = _centroid_length(query)
    centroid_pen = float(np.sum((ct - cq) ** 2))
    length_pen = float(np.log((lt + 1e-6) / (lq + 1e-6)) ** 2)

    t_shape = resample_stroke(template, n_shape, closed=closed)
    q_shape = resample_stroke(query, n_shape, closed=closed)
    t0 = t_shape - t_shape.mean(axis=0)
    q0 = q_shape - q_shape.mean(axis=0)
    nt = np.linalg.norm(t0)
    nq = np.linalg.norm(q0)
    if nq > 0 and nt > 0:
        q0 = q0 * (nt / nq)
    shape_mse, _ = _aligned_mse(t0, q0, closed)

    q_full = resample_stroke(query, n, closed=closed)
    _, aligned = _match_parameterization(template, q_full, closed)
    cost = shape_mse + centroid_weight * centroid_pen + length_weight * length_pen
    return cost, aligned


def match_to_template(template, query, closed, max_cost=None):
    """Hungarian match of ``query`` strokes onto ``template``.

    ``template`` and ``query`` are lists of ``(k, 2)`` arrays. ``closed`` is a
    boolean per template stroke. Returns aligned query strokes in template
    order, and an array ``assignment`` where ``assignment[i]`` is the query
    index matched to template stroke ``i``, or ``-1`` if that stroke is
    missing.

    The cost matrix is rectangular: extra query strokes are left unmatched
    (dropped). Unmatched template strokes become all-NaN polylines, i.e.
    missing observations in the packed vector. If ``max_cost`` is set, a
    matched pair whose cost exceeds it is treated as missing as well.
    """
    from scipy.optimize import linear_sum_assignment

    n = len(template)
    m = len(query)
    assignment = np.full(n, -1, dtype=int)
    if m == 0:
        matched = [np.full((len(t), 2), np.nan) for t in template]
        return matched, assignment
    costs = np.empty((n, m))
    cache = {}
    for i in range(n):
        for j in range(m):
            cost, aligned = pair_cost_and_align(template[i], query[j], bool(closed[i]))
            costs[i, j] = cost
            cache[i, j] = aligned
    rows, cols = linear_sum_assignment(costs)
    assignment[rows] = cols
    if max_cost is not None:
        for i in range(n):
            j = assignment[i]
            if j >= 0 and costs[i, j] > max_cost:
                assignment[i] = -1
    matched = []
    for i in range(n):
        j = assignment[i]
        if j < 0:
            matched.append(np.full((len(template[i]), 2), np.nan))
        else:
            matched.append(cache[i, j])
    return matched, assignment


def scramble_strokes(strokes, closed=None, rng=None):
    """Permute stroke order, reverse some, and change vertex counts.

    Used to test correspondence: the drawing is the same, the encoding is not.
    Returns ``(scrambled, permutation, closed_scrambled)`` where
    ``permutation[k]`` is the original index of scrambled stroke ``k``.
    """
    rng = np.random.default_rng(rng)
    n = len(strokes)
    perm = rng.permutation(n)
    if closed is None:
        closed = [looks_closed(s) for s in strokes]
    scrambled = []
    closed_out = []
    for i in perm:
        pts = np.asarray(strokes[i], dtype=float)
        if rng.random() < 0.5:
            pts = pts[::-1].copy()
        n_new = max(6, len(pts) + int(rng.integers(-5, 6)))
        is_closed = bool(closed[i])
        scrambled.append(resample_stroke(pts, n_new, closed=is_closed))
        closed_out.append(is_closed)
    return scrambled, perm, closed_out


def align_doodles(doodles, closed=None, n_vertices=None, names=None, max_cost=None, template_index=0):
    """Align a list of doodles to one example's stroke topology.

    Each doodle is a list of polylines. Stroke order, vertex counts, and
    stroke *counts* may differ. The template (default: the first doodle)
    defines the packed dimension; pass ``template_index="typical"`` to use a
    drawing with the most common stroke count. Query strokes that do not
    match a template stroke are dropped; template strokes with no match are
    packed as NaN (missing data for the GPLVM). Matched strokes keep their
    drawn position. Returns ``Y, specs, assignments``.
    """
    if len(doodles) < 1:
        raise ValueError("need at least one doodle")
    if template_index == "typical":
        template_index = typical_template_index(doodles)
    if template_index < 0 or template_index >= len(doodles):
        raise IndexError(f"template_index {template_index} out of range for {len(doodles)} doodles")
    template = [np.asarray(s, dtype=float) for s in doodles[template_index]]
    if closed is None:
        closed = [looks_closed(s) for s in template]
    if n_vertices is None:
        n_vertices = [len(s) for s in template]
    if names is None:
        names = [f"stroke{i}" for i in range(len(template))]
    template_rs = [resample_stroke(s, n, c) for s, n, c in zip(template, n_vertices, closed, strict=True)]
    packed = []
    assignments = []
    for doodle in doodles:
        query = [np.asarray(s, dtype=float) for s in doodle]
        matched, assign = match_to_template(template_rs, query, closed, max_cost=max_cost)
        packed.append(pack_doodle(matched))
        assignments.append(assign)
    specs = tuple(StrokeSpec(name, n, bool(c)) for name, n, c in zip(names, n_vertices, closed, strict=True))
    return np.asarray(packed, dtype=float), specs, assignments
