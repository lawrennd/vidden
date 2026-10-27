import numpy as np

from vidden.explore import assemble_latent, latent_array, reconstruct_mean


class _ArrayX:
    def __init__(self):
        self.X = np.array([[1.0, 2.0], [3.0, 4.0]])

    def predict(self, z):
        z = np.atleast_2d(z)
        return np.zeros((z.shape[0], 3)), np.ones((z.shape[0], 3))


class _MeanX:
    def __init__(self):
        self.X = type("Posterior", (), {"mean": np.array([[9.0, 8.0]])})()


def test_latent_array_uses_plain_x_not_ndarray_mean():
    arr = latent_array(_ArrayX())
    np.testing.assert_allclose(arr, [[1.0, 2.0], [3.0, 4.0]])


def test_latent_array_uses_array_valued_mean():
    arr = latent_array(_MeanX())
    np.testing.assert_allclose(arr, [[9.0, 8.0]])


def test_reconstruct_mean_falls_back_to_predict():
    mu = reconstruct_mean(_ArrayX(), assemble_latent(np.zeros((1, 2)), 0.1, -0.2, 0, 1))
    assert mu.shape == (3,)


def test_reconstruct_mean_inverts_normalizer():
    class _Norm:
        def inverse_mean(self, mu):
            return np.asarray(mu) + 1.0

    class _Raw:
        X = np.zeros((2, 2))
        normalizer = _Norm()

        def _raw_predict(self, z, full_cov=False):
            z = np.atleast_2d(z)
            return np.zeros((z.shape[0], 3)), np.ones((z.shape[0], 3))

    mu = reconstruct_mean(_Raw(), [[0.1, -0.2]])
    np.testing.assert_allclose(mu, [1.0, 1.0, 1.0])


def test_latent_array_skips_non_array_mean():
    class _BadMean:
        def __array__(self):
            raise TypeError("not an array")

    class _X:
        mean = _BadMean()

        def __array__(self):
            return np.array([[1.0, 2.0]])

    class _Model:
        X = _X()

    arr = latent_array(_Model())
    np.testing.assert_allclose(arr, [[1.0, 2.0]])


def test_most_significant_dims_without_gpy_helpers():
    from vidden.models import most_significant_dims

    class _Plain:
        input_dim = 3
        X = np.zeros((4, 3))

        def get_most_significant_input_dimensions(self):
            return (0, None)

    dim_x, dim_y = most_significant_dims(_Plain())
    assert dim_x == 0
    assert dim_y == 1

    class _Same:
        input_dim = 3
        X = np.zeros((2, 3))

        def get_most_significant_input_dimensions(self):
            return (1, 1)

    dim_x, dim_y = most_significant_dims(_Same())
    assert dim_x == 1
    assert dim_y == 0

    class _NoGetter:
        input_dim = 1
        X = np.zeros((2, 1))

    dim_x, dim_y = most_significant_dims(_NoGetter())
    assert dim_x == 0
    assert dim_y == 0

    class _NoGetterQ2:
        input_dim = 2
        X = np.zeros((2, 2))

    dim_x, dim_y = most_significant_dims(_NoGetterQ2())
    assert (dim_x, dim_y) == (0, 1)


def test_posterior_density_grid_variance_shapes():
    from vidden.models import latent_posterior_density_grid

    class _Var1d:
        input_dim = 2
        output_dim = 4
        X = np.zeros((3, 2))

        def predict(self, z):
            n = len(np.atleast_2d(z))
            return np.zeros((n, 4)), np.ones(n)

    x1, x2, density = latent_posterior_density_grid(
        _Var1d(), 0, 1, (-1.0, 1.0), (-1.0, 1.0), resolution=3
    )
    assert density.shape == (3, 3)

    class _Var2d:
        input_dim = 2
        output_dim = 3
        X = np.zeros((3, 2))

        def predict(self, z):
            n = len(np.atleast_2d(z))
            return np.zeros((n, 3)), np.ones((n, 3))

    _, _, density2 = latent_posterior_density_grid(
        _Var2d(), 0, 1, (-1.0, 1.0), (-1.0, 1.0), resolution=3, default_vals=[0.1, -0.2]
    )
    assert density2.shape == (3, 3)
