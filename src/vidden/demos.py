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


def load_oil_model(optimize=False, N=200, input_dim=7, num_inducing=40):
    """Oil-flow Bayesian GPLVM, as ``bgplvm_oil`` without matplotlib.

    Observations are ``data["X"]`` (12-D). Labels are ``data["Y"]``.
    ARD RBF lengthscale 0.5 and noise 0.001 match the stick start.
    """
    import GPy
    from GPy.models import BayesianGPLVM

    try:
        import pods

        data = pods.datasets.oil()
    except ImportError:
        data = GPy.util.datasets.oil()

    np.random.seed(0)
    Y = np.asarray(data["X"][: int(N)], dtype=float)
    Q = int(input_dim)
    M = min(int(num_inducing), Y.shape[0])
    kernel = GPy.kern.RBF(Q, lengthscale=np.repeat(0.5, Q), ARD=True)
    model = BayesianGPLVM(Y, Q, init="PCA", num_inducing=M, kernel=kernel)
    model.likelihood.variance = 0.001
    labels = np.asarray(data["Y"][: int(N)])
    model.data_labels = labels.argmax(axis=1) if labels.ndim == 2 else labels
    model.data = data
    if optimize:
        optimize_stick_model(model)
    return model


def load_brendan_model(optimize=False, input_dim=2, num_inducing=20, n=None):
    """Brendan faces as a 2-D Bayesian GPLVM.

    Same normalisation as GPy ``brendan_faces``. Image flags are attached
    on the model for ``face_explorer``. Q stays 2.
    """
    import GPy
    from GPy.models import BayesianGPLVM

    from vidden.views.image import BRENDAN_IMAGE

    try:
        import pods

        data = pods.datasets.brendan_faces()
    except ImportError:
        data = GPy.util.datasets.brendan_faces()

    Y = np.asarray(data["Y"], dtype=float)
    if n is not None:
        Y = Y[: int(n)]
    Yn = Y - Y.mean()
    Yn /= Yn.std()
    Q = int(input_dim)
    M = min(int(num_inducing), Yn.shape[0])
    kernel = GPy.kern.RBF(Q, lengthscale=np.repeat(0.5, Q), ARD=True)
    model = BayesianGPLVM(Yn, Q, init="PCA", num_inducing=M, kernel=kernel)
    model.likelihood.variance = 0.001
    model.image_dimensions = BRENDAN_IMAGE["dimensions"]
    model.image_transpose = BRENDAN_IMAGE["transpose"]
    model.image_order = BRENDAN_IMAGE["order"]
    model.image_invert = BRENDAN_IMAGE["invert"]
    model.data = data
    if optimize:
        optimize_stick_model(model)
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
