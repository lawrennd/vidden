"""Optional GPy demos. Import GPy only inside these functions."""

from __future__ import annotations

import numpy as np


def load_stick_model(optimize=False):
    """OSU stick-man Bayesian GPLVM without importing matplotlib.

    Starts from PCA. Call ``optimize_stick_model`` or the explorer's
    Optimize button for Bayesian GPLVM training.
    """
    import GPy
    import pods
    from GPy.models import BayesianGPLVM

    data = pods.datasets.osu_run1()
    Q = 6
    kernel = GPy.kern.RBF(Q, lengthscale=np.repeat(0.5, Q), ARD=True)
    model = BayesianGPLVM(data["Y"], Q, init="PCA", num_inducing=20, kernel=kernel)
    model.data = data
    model.likelihood.variance = 0.001
    if optimize:
        optimize_stick_model(model)
    return model


def optimize_stick_model(model, max_iters=5000, messages=False, bfgs_factor=10):
    """Run BFGS as in ``stick_bgplvm`` (``max_iters=5e3``, ``bfgs_factor=10``)."""
    model.optimize("bfgs", messages=messages, max_iters=int(max_iters), bfgs_factor=bfgs_factor)
    return model


def load_face_model(optimize=False, input_dim=2, num_inducing=10):
    """Smile × roundness cartoon faces as a 2-D Bayesian GPLVM.

    Same kernel start as the stick man: ARD RBF, lengthscale 0.5, noise
    0.001. Two latent dimensions match the known factors. Starts from
    PCA. Call ``optimize_stick_model`` or the explorer's Optimize button
    to train.
    """
    import GPy
    from GPy.models import BayesianGPLVM

    from vidden.doodle import make_face_dataset

    Y, Z, strokes = make_face_dataset()
    Q = int(input_dim)
    M = min(int(num_inducing), Y.shape[0])
    kernel = GPy.kern.RBF(Q, lengthscale=np.repeat(0.5, Q), ARD=True)
    model = BayesianGPLVM(Y, Q, init="PCA", num_inducing=M, kernel=kernel)
    model.likelihood.variance = 0.001
    model.doodle_strokes = strokes
    model.doodle_factors = Z
    if optimize:
        optimize_stick_model(model)
    return model
