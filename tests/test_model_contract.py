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
