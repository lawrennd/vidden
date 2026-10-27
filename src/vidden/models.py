"""Duck-typed latent-model contract. GPy is a client, not an import."""

from __future__ import annotations

import numpy as np


def _is_array_mean(value):
    """True when ``X.mean`` is data, not ``ndarray.mean`` / ``Param.mean``."""
    if value is None or callable(value):
        return False
    try:
        np.asarray(value)
    except (TypeError, ValueError):
        return False
    return True


def _latent_values(model):
    """Latent locations: posterior mean when present, ``X`` otherwise.

    Do not use ``hasattr(X, "mean")``: Param/ndarray ``mean`` is a method.
    """
    X = model.X
    mean = getattr(X, "mean", None)
    if _is_array_mean(mean):
        return mean
    return X


def latent_mean_row(model):
    """Writable ``(1, Q)`` row from a GPLVM or BayesianGPLVM."""
    vals = _latent_values(model)
    row = np.array(np.asarray(vals[:1, :]), dtype=float, copy=True)
    return np.atleast_2d(row.reshape(row.shape[0], -1)[:1])


def latent_array(model):
    """``(N, Q)`` latent locations for the scatter plot."""
    return np.array(np.asarray(_latent_values(model)), dtype=float, copy=True)


def reconstruct_mean(model, z):
    """Posterior mean only. Skip predictive variance (not drawn)."""
    z = np.atleast_2d(z)
    raw = getattr(model, "_raw_predict", None)
    if callable(raw):
        mu = raw(z, full_cov=False)[0]
        if getattr(model, "normalizer", None) is not None:
            mu = model.normalizer.inverse_mean(mu)
    else:
        mu = model.predict(z)[0]
    return np.asarray(mu, dtype=float)[0]


def assemble_latent(mean_row, x, y, dim_x, dim_y):
    """Write the two visible axes; leave every other coordinate as it was.

    MATLAB ``lvmVisualise`` starts ``latentPos`` at zeros and
    ``lvmClassVisualise('move')`` only updates ``dim1`` and ``dim2``.
    """
    z = np.array(np.asarray(mean_row), dtype=float, copy=True)
    z = np.atleast_2d(z.reshape(z.shape[0], -1)[:1])
    z[0, int(dim_x)] = float(x)
    z[0, int(dim_y)] = float(y)
    return z


def assemble_latent_nearest(X, x, y, dim_x, dim_y):
    """Unused coordinates from the nearest training embedding (not MATLAB)."""
    X = np.atleast_2d(np.asarray(X, dtype=float))
    dim_x = int(dim_x)
    dim_y = int(dim_y)
    d2 = (X[:, dim_x] - float(x)) ** 2 + (X[:, dim_y] - float(y)) ** 2
    z = np.array(X[int(np.argmin(d2))], dtype=float, copy=True)[None, :]
    z[0, dim_x] = float(x)
    z[0, dim_y] = float(y)
    return z


def latent_axis_limits(xy, pad=0.05):
    """2D limits from training latent coordinates, not from the pointer."""
    xy = np.asarray(xy, dtype=float)
    lo = xy.min(axis=0)
    hi = xy.max(axis=0)
    span = hi - lo
    span = np.where(span <= 0.0, 1.0, span)
    margin = span * float(pad)
    return (float(lo[0] - margin[0]), float(hi[0] + margin[0])), (
        float(lo[1] - margin[1]),
        float(hi[1] + margin[1]),
    )


def most_significant_dims(model):
    """Two latent axes a GPLVM would show (ARD input sensitivity)."""
    q = int(getattr(model, "input_dim", latent_array(model).shape[1]))
    getter = getattr(model, "get_most_significant_input_dimensions", None)
    if callable(getter):
        dims = getter()
        dim_x = int(dims[0])
        dim_y = 0 if dims[1] is None else int(dims[1])
    else:
        dim_x, dim_y = 0, 1 if q > 1 else 0
    if dim_y == dim_x and q > 1:
        dim_y = 1 if dim_x == 0 else 0
    return dim_x, dim_y


def input_sensitivity_values(model):
    """Per-dimension kernel sensitivity, as in ``lvm_dimselect``."""
    return np.asarray(model.input_sensitivity(), dtype=float).reshape(-1)


def sensitivity_bar_ylim(sens, pad=0.1):
    """Y-limits for the ARD histogram, recomputed after every update.

    ``lvm_dimselect`` does ``cla()`` then ``bar()``, so matplotlib autoscales.
    HoloViews default ``framewise=False`` keeps the first-frame range. After
    Bayesian GPLVM training the sensitivities drop from O(1) to O(1e-3) and
    the bars vanish against the PCA-initialised axis.
    """
    peak = float(np.max(np.asarray(sens, dtype=float)))
    if not np.isfinite(peak) or peak <= 0.0:
        peak = 1.0
    return (0.0, peak * (1.0 + float(pad)))


def latent_posterior_density_grid(model, dim_x, dim_y, xlim, ylim, resolution=50, default_vals=None):
    """Posterior density on two latent axes (MATLAB ``lvmScatterPlot``).

    Unused dimensions are held at ``default_vals`` (MATLAB ``defaultVals``,
    GPy ``Xgrid`` zeros). Returns ``-0.5 * sum(log varsigma)`` so low
    posterior variance is bright.
    """
    q = int(model.input_dim)
    d = int(model.output_dim)
    res = int(resolution)
    x1 = np.linspace(float(xlim[0]), float(xlim[1]), res)
    x2 = np.linspace(float(ylim[0]), float(ylim[1]), res)
    xx, yy = np.meshgrid(x1, x2)
    if default_vals is None:
        xtest = np.zeros((xx.size, q))
    else:
        xtest = np.repeat(np.asarray(default_vals, dtype=float).reshape(1, -1), xx.size, axis=0)
    xtest[:, int(dim_x)] = xx.ravel()
    xtest[:, int(dim_y)] = yy.ravel()
    varsigma = np.asarray(model.predict(xtest)[1], dtype=float)
    if varsigma.ndim == 1:
        varsigma = varsigma[:, None]
    clipped = np.clip(varsigma, 1e-12, None)
    if varsigma.shape[1] == 1:
        density = -0.5 * d * np.log(clipped[:, 0])
    else:
        density = -0.5 * np.log(clipped).sum(axis=1)
    return x1, x2, density.reshape(xx.shape)
