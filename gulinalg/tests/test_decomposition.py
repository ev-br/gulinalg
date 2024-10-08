"""
Tests different implementations of decomposition functions.
"""

from __future__ import print_function
from unittest import TestCase, skipIf
import numpy as np
from numpy.testing import assert_allclose
from pkg_resources import parse_version
import gulinalg

n_batch = 8

class TestLU(TestCase):
    """
    Test LU decomposition.
    """
    def test_lu_m_gt_n(self):
        """LU decompose a matrix where dimension m > n"""
        a = np.ascontiguousarray(np.random.randn(75, 50))
        p, l, u = gulinalg.lu(a)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    def test_lu_m_lt_n(self):
        """LU decompose a matrix where dimension m < n"""
        a = np.ascontiguousarray(np.random.randn(50, 75))
        p, l, u = gulinalg.lu(a)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_lu_m_and_n_zero(self):
        """Corner case of decomposing where m = 0 and n = 0"""
        a = np.ascontiguousarray(np.random.randn(0, 0))
        p, l, u = gulinalg.lu(a)
        # p is MxM, l is MxK, u is KxN where K = min(M, N)
        # As M = 0 here, all three of them should be empty.
        assert p.shape == (0, 0)
        assert l.shape == (0, 0)
        assert u.shape == (0, 0)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_lu_m_zero(self):
        """Corner case of decomposing where m = 0"""
        a = np.ascontiguousarray(np.random.randn(0, 2))
        p, l, u = gulinalg.lu(a)
        # p is MxM, l is MxK, u is KxN where K = min(M, N)
        # As M = 0 here, all three of them should be empty.
        assert p.shape == (0, 0)
        assert l.shape == (0, 0)
        assert u.shape == (0, 2)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_lu_n_zero(self):
        """Corner case of decomposing where n = 0"""
        a = np.ascontiguousarray(np.random.randn(2, 0))
        p, l, u = gulinalg.lu(a)
        # p is MxM, l is MxK, u is KxN where K = min(M, N)
        # As N = 0 here, assert following dimensions.
        assert p.shape == (2, 2)
        assert l.shape == (2, 0)
        assert u.shape == (0, 0)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    def test_lu_size_one_matrix(self):
        """Corner case of decomposing size 1 matrix"""
        a = np.ascontiguousarray(np.random.randn(1, 1))
        p, l, u = gulinalg.lu(a)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    def test_lu_permute_m_gt_n(self):
        """LU decompose a matrix where dimension m > n"""
        a = np.ascontiguousarray(np.random.randn(75, 50))
        pl, u = gulinalg.lu(a, permute_l=True)
        assert_allclose(np.dot(pl, u), a)

    def test_lu_permute_m_lt_n(self):
        """LU decompose a matrix where dimension m < n"""
        a = np.ascontiguousarray(np.random.randn(50, 75))
        pl, u = gulinalg.lu(a, permute_l=True)
        assert_allclose(np.dot(pl, u), a)

    def test_lu_permute_size_1_matrix(self):
        a = np.ascontiguousarray(np.random.randn(1, 1))
        pl, u = gulinalg.lu(a, permute_l=True)
        assert_allclose(np.dot(pl, u), a)

    def test_complex_numbers(self):
        """Test for complex numbers input."""
        a = np.array([[1 + 2j, 3 + 4j], [5 + 6j, 7 + -8j]])
        p, l, u = gulinalg.lu(a)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    def test_fortran_layout_matrix(self):
        """Input matrix is fortran layout matrix"""
        a = np.asfortranarray(np.random.randn(75, 50))
        pl, u = gulinalg.lu(a, permute_l=True)
        assert_allclose(np.dot(pl, u), a)

    def test_input_matrix_non_contiguous(self):
        """Input matrix is not a contiguous matrix"""
        a = np.ascontiguousarray(np.random.randn(50, 75, 2))[:, :, 0]
        assert not a.flags.c_contiguous and not a.flags.f_contiguous
        p, l, u = gulinalg.lu(a)
        assert_allclose(np.dot(np.dot(p, l), u), a)

    def test_vector(self):
        """test vectorized LU decomposition"""
        a = np.ascontiguousarray(np.random.randn(10, 75, 50))
        for workers in [1, -1]:
            p, l, u = gulinalg.lu(a, workers=workers)
            res = np.stack([np.dot(np.dot(p[i], l[i]), u[i])
                            for i in range(len(a))])
            assert_allclose(res, a)

    def test_vector_permute_l(self):
        """test vectorized LU decomposition"""
        a = np.ascontiguousarray(np.random.randn(10, 75, 50))
        for workers in [1, -1]:
            pl, u = gulinalg.lu(a, permute_l=True, workers=workers)
            res = np.stack([np.dot(pl[i], u[i])
                            for i in range(len(a))])
            assert_allclose(res, a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_vector_m_and_n_zero(self):
        """Corner case of decomposing where m = 0 and n = 0"""
        a = np.ascontiguousarray(np.random.randn(10, 0, 0))
        p, l, u = gulinalg.lu(a)
        # p is MxM, l is MxK, u is KxN where K = min(M, N)
        # As M = 0 here, all three of them should be empty.
        assert p.shape == (10, 0, 0)
        assert l.shape == (10, 0, 0)
        assert u.shape == (10, 0, 0)
        res = np.stack([np.dot(np.dot(p[i], l[i]), u[i])
                        for i in range(len(a))])
        assert_allclose(res, a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_vector_m_zero(self):
        """Corner case of decomposing where m = 0"""
        a = np.ascontiguousarray(np.random.randn(10, 0, 2))
        p, l, u = gulinalg.lu(a)
        # p is MxM, l is MxK, u is KxN where K = min(M, N)
        # As M = 0 here, all three of them should be empty.
        assert p.shape == (10, 0, 0)
        assert l.shape == (10, 0, 0)
        assert u.shape == (10, 0, 2)
        res = np.stack([np.dot(np.dot(p[i], l[i]), u[i])
                        for i in range(len(a))])
        assert_allclose(res, a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_vector_n_zero(self):
        """Corner case of decomposing where n = 0"""
        a = np.ascontiguousarray(np.random.randn(10, 2, 0))
        p, l, u = gulinalg.lu(a)
        # p is MxM, l is MxK, u is KxN where K = min(M, N)
        # As N = 0 here, assert following dimensions.
        assert p.shape == (10, 2, 2)
        assert l.shape == (10, 2, 0)
        assert u.shape == (10, 0, 0)
        res = np.stack([np.dot(np.dot(p[i], l[i]), u[i])
                        for i in range(len(a))])
        assert_allclose(res, a)

    def test_vector_size_one_matrix(self):
        """Corner case of decomposing size 1 matrix"""
        a = np.ascontiguousarray(np.random.randn(10, 1, 1))
        p, l, u = gulinalg.lu(a)
        res = np.stack([np.dot(np.dot(p[i], l[i]), u[i])
                        for i in range(len(a))])
        assert_allclose(res, a)

    def test_nan_handling(self):
        """NaN in one output shouldn't contaminate remaining outputs"""
        a = np.array([[[3, 4, 5], [2, np.nan, 3]],
                      [[3, 4, 5], [2, 1, 3]]])
        pl, u = gulinalg.lu(a, permute_l=True)
        ref_pl = np.array([[[1., 0.], [0.66666667, 1.]],
                           [[1., 0.], [0.66666667, 1.]]])
        ref_u = np.array([[[3., 4., 5.], [0., np.nan, -0.33333333]],
                          [[3., 4., 5.], [0., -1.66666667, -0.33333333]]])
        assert_allclose(pl, ref_pl)
        assert_allclose(u, ref_u)

    def test_infinity_handling(self):
        """Infinity in one output shouldn't contaminate remaining outputs"""
        a = np.array([[[3, 4, 5], [2, np.inf, 3]],
                      [[3, 4, 5], [2, 1, 3]]])
        pl, u = gulinalg.lu(a, permute_l=True)
        ref_pl = np.array([[[1., 0.], [0.66666667, 1.]],
                           [[1., 0.], [0.66666667, 1.]]])
        ref_u = np.array([[[3., 4., 5.], [0., np.inf, -0.33333333]],
                          [[3., 4., 5.], [0., -1.66666667, -0.33333333]]])
        assert_allclose(pl, ref_pl)
        assert_allclose(u, ref_u)


class TestQR(TestCase):
    """Test QR decomposition"""
    def test_m_lt_n(self):
        """For M < N, return full MxM Q matrix and all M rows of R."""
        m = 50
        n = 75
        a = np.ascontiguousarray(np.random.randn(m, n))
        q, r = gulinalg.qr(a)
        assert_allclose(np.dot(q, q.T), np.identity(m), atol=1e-15)
        assert_allclose(np.dot(q, r), a)

    def test_m_gt_n(self):
        """For M > N, return full MxM Q matrix and all M rows of R."""
        m = 75
        n = 50
        a = np.ascontiguousarray(np.random.randn(m, n))
        q, r = gulinalg.qr(a)
        assert q.shape == (m, m)
        assert r.shape == (m, n)
        assert_allclose(np.dot(q, q.T), np.identity(m), atol=1e-15)
        assert_allclose(np.dot(q, r), a)

    def test_m_gt_n_economy(self):
        """
        If M > N, economy mode returns only N columns for Q and N rows for R.
        """
        m = 75
        n = 50
        a = np.ascontiguousarray(np.random.randn(m, n))
        q, r = gulinalg.qr(a, economy=True)
        assert q.shape == (m, n)
        assert r.shape == (n, n)
        assert_allclose(np.dot(q, r), a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_m_and_n_zero(self):
        """Corner case of decomposing where m = 0 and n = 0"""
        a = np.ascontiguousarray(np.random.randn(0, 0))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N). As M = 0, K = 0. so q and r should be empty.
        assert q.shape == (0, 0)
        assert r.shape == (0, 0)
        assert_allclose(np.dot(q, r), a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_m_zero(self):
        """Corner case of decomposing where m = 0"""
        a = np.ascontiguousarray(np.random.randn(0, 2))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N).
        assert q.shape == (0, 0)
        assert r.shape == (0, 2)
        assert_allclose(np.dot(q, r), a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_n_zero(self):
        """Corner case of decomposing where n = 0"""
        a = np.ascontiguousarray(np.random.randn(2, 0))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N).
        assert q.shape == (2, 2)
        assert r.shape == (2, 0)
        assert_allclose(np.dot(q, r), a)

    def test_qr_size_one_matrix(self):
        """Corner case of decomposing size 1 matrix"""
        m = 1
        n = 1
        a = np.ascontiguousarray(np.random.randn(m, n))
        q, r = gulinalg.qr(a)
        assert q.shape == (m, n)
        assert r.shape == (n, n)
        assert_allclose(np.dot(q, r), a)

    def test_complex_numbers(self):
        """Test for complex numbers input."""
        a = np.array([[1 + 2j, 3 + 4j], [5 + 6j, 7 + -8j]])
        q, r = gulinalg.qr(a)
        assert_allclose(np.dot(q, r), a)

    def test_fortran_layout_matrix(self):
        """Input matrix is fortran layout matrix"""
        m = 75
        n = 50
        a = np.asfortranarray(np.random.randn(m, n))
        q, r = gulinalg.qr(a, economy=True)
        assert q.shape == (m, n)
        assert r.shape == (n, n)
        assert_allclose(np.dot(q, r), a)

    def test_input_matrix_non_contiguous(self):
        """Input matrix is not a contiguous matrix"""
        m = 75
        n = 50
        a = np.ascontiguousarray(np.random.randn(m, n, 2))[:, :, 0]
        assert not a.flags.c_contiguous and not a.flags.f_contiguous
        q, r = gulinalg.qr(a, economy=True)
        assert q.shape == (m, n)
        assert r.shape == (n, n)
        assert_allclose(np.dot(q, r), a)

    def test_vector(self):
        """test vectorized QR decomposition"""
        a = np.ascontiguousarray(np.random.randn(10, 75, 50))
        for economy in [False, True]:
            for workers in [1, -1]:
                q, r = gulinalg.qr(a, economy=economy, workers=workers)
                res = np.stack([np.dot(q[i], r[i]) for i in range(len(a))])
                assert_allclose(res, a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_vector_m_and_n_zero(self):
        """Corner case of decomposing where m = 0 and n = 0"""
        a = np.ascontiguousarray(np.random.randn(10, 0, 0))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N). As M = 0, K = 0. so q and r should be empty.
        assert q.shape == (10, 0, 0)
        assert r.shape == (10, 0, 0)
        res = np.stack([np.dot(q[i], r[i]) for i in range(len(a))])
        assert_allclose(res, a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_vector_m_zero(self):
        """Corner case of decomposing where m = 0"""
        a = np.ascontiguousarray(np.random.randn(10, 0, 2))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N).
        assert q.shape == (10, 0, 0)
        assert r.shape == (10, 0, 2)
        res = np.stack([np.dot(q[i], r[i]) for i in range(len(a))])
        assert_allclose(res, a)

    @skipIf(parse_version(np.__version__) < parse_version('1.13'),
            "Prior to 1.13, numpy low level iterators didn't support removing "
            "empty axis. So gufunc couldn't be called with empty inner loop")
    def test_vector_n_zero(self):
        """Corner case of decomposing where n = 0"""
        a = np.ascontiguousarray(np.random.randn(10, 2, 0))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N).
        assert q.shape == (10, 2, 2)
        assert r.shape == (10, 2, 0)
        res = np.stack([np.dot(q[i], r[i]) for i in range(len(a))])
        assert_allclose(res, a)

    def test_vector_size_one_matrices(self):
        """Corner case of decomposing where m = 1 and n = 1"""
        a = np.ascontiguousarray(np.random.randn(10, 1, 1))
        q, r = gulinalg.qr(a)
        # q is MxM or MxK (economy mode) and r is MxN or KxN (economy mode)
        # where K = min(M, N). As M = 0, K = 0. so q and r should be empty.
        assert q.shape == (10, 1, 1)
        assert r.shape == (10, 1, 1)
        res = np.stack([np.dot(q[i], r[i]) for i in range(len(a))])
        assert_allclose(res, a)

    def test_nan_handling(self):
        """NaN in one output shouldn't contaminate remaining outputs"""
        a = np.array([[[3, 4, 5], [np.nan, 1, 3]],
                      [[3, 4, 5], [2, 1, 3]]])
        q, r = gulinalg.qr(a)
        ref_q = np.array([[-0.83205029, -0.5547002],
                          [-0.5547002, 0.83205029]])
        ref_r = np.array([[-3.60555128, -3.88290137, -5.82435206],
                          [0., -1.38675049, -0.2773501]])
        # For NaN input i.e. a[0], expected output in ATLAS, MKL and SCIPY is:
        # [[nan, nan], [nan, nan]]
        # However openblas output is:
        # [[nan, 0], [nan, 1]].
        # As this test checks that nan in one input should not impact output
        # for second input matrix, comparing output for second is enough.
        assert_allclose(q[1], ref_q)
        assert_allclose(r[1], ref_r)

    def test_infinity_handling(self):
        """Infinity in one output shouldn't contaminate remaining outputs"""
        a = np.array([[[3, 4, 5], [np.inf, 1, 3]],
                      [[3, 4, 5], [2, 1, 3]]])
        q, r = gulinalg.qr(a)
        ref_q = np.array([[-0.83205029, -0.5547002],
                          [-0.5547002, 0.83205029]])
        ref_r = np.array([[-3.60555128, -3.88290137, -5.82435206],
                          [0., -1.38675049, -0.2773501]])
        # For infinity input i.e. a[0], expected output in ATLAS, MKL and SCIPY
        # is: [[nan, nan], [nan, nan]]
        # However openblas output is:
        # [[-0.707107, nan], [nan, nan]].
        # As this test checks that infinity in one input should not impact
        # output for second input, comparing output for second is enough.
        assert_allclose(q[1], ref_q)
        assert_allclose(r[1], ref_r)


class TestCholesky(TestCase):
    """Test Cholesky decomposition"""
    def test_real_L(self):
        m = 10
        a = np.ascontiguousarray(np.random.randn(m, m))
        a = np.dot(a, a.T)  # make Hermetian symmetric
        L = gulinalg.cholesky(a, UPLO='L')
        assert_allclose(np.matmul(L, L.T), a)

    def test_real_U(self):
        m = 10
        a = np.ascontiguousarray(np.random.randn(m, m))
        a = np.dot(a, a.T)  # make Hermetian symmetric
        U = gulinalg.cholesky(a, UPLO='U')
        assert_allclose(np.matmul(U.T, U), a)

    def test_complex_L(self):
        m = 10
        a = np.ascontiguousarray(np.random.randn(m, m))
        a = a + 1j * np.ascontiguousarray(np.random.randn(m, m))
        a = np.dot(a, np.conj(a).T)  # make Hermetian symmetric
        L = gulinalg.cholesky(a, UPLO='L')
        assert_allclose(np.matmul(L, np.conj(L).T), a)

    def test_complex_U(self):
        m = 10
        a = np.ascontiguousarray(np.random.randn(m, m))
        a = a + 1j * np.ascontiguousarray(np.random.randn(m, m))
        a = np.dot(a, np.conj(a).T)  # make Hermetian symmetric
        U = gulinalg.cholesky(a, UPLO='U')
        assert_allclose(np.matmul(np.conj(U).T, U), a)

    def test_real_noncontiguous(self):
        m = 10
        a = np.asfortranarray(np.random.randn(m, m))
        a = np.dot(a, a.T)  # make Hermetian symmetric
        a = a[::2, ::2]
        L = gulinalg.cholesky(a, UPLO='L')
        assert_allclose(np.matmul(L, L.T), a)

    def test_real_fortran(self):
        m = 10
        a = np.asfortranarray(np.random.randn(m, m))
        a = np.dot(a, a.T)  # make Hermetian symmetric
        L = gulinalg.cholesky(a, UPLO='L')
        assert_allclose(np.matmul(L, L.T), a)

    def test_real_broadcast_L(self):
        m = 5
        a = np.asfortranarray(np.random.randn(m, m))
        a = np.dot(a, a.T)  # make Hermetian symmetric
        a = np.stack((a,) * n_batch, axis=0)
        for workers in [1, -1]:
            L = gulinalg.cholesky(a, UPLO='L', workers=workers)
            assert_allclose(np.matmul(L, L.swapaxes(-2, -1)), a)

    def test_real_broadcast_U(self):
        m = 5
        a = np.asfortranarray(np.random.randn(m, m))
        a = np.dot(a, a.T)  # make Hermetian symmetric
        a = np.stack((a,) * n_batch, axis=0)
        for workers in [1, -1]:
            U = gulinalg.cholesky(a, UPLO='U', workers=workers)
            assert_allclose(np.matmul(U.swapaxes(-2, -1), U), a)

    def test_complex_broadcast_U(self):
        m = 5
        a = np.asfortranarray(np.random.randn(m, m))
        a = a + 1j * np.asfortranarray(np.random.randn(m, m))
        a = np.dot(a, np.conj(a).T)  # make Hermetian symmetric
        a = np.stack((a,) * n_batch, axis=0)
        for workers in [1, -1]:
            U = gulinalg.cholesky(a, UPLO='U', workers=workers)
            assert_allclose(np.matmul(np.conj(U).swapaxes(-2, -1), U), a)

    def test_complex_broadcast_L(self):
        m = 5
        a = np.asfortranarray(np.random.randn(m, m))
        a = a + 1j * np.asfortranarray(np.random.randn(m, m))
        a = np.dot(a, np.conj(a).T)  # make Hermetian symmetric
        a = np.stack((a,) * n_batch, axis=0)
        for workers in [1, -1]:
            L = gulinalg.cholesky(a, UPLO='L', workers=workers)
            assert_allclose(np.matmul(L, np.conj(L).swapaxes(-2, -1)), a)


class TestEig(TestCase):
    """Test Eigenvalue Decomposition"""

    def _check_eigen(self, A, w, v):
        '''vectorial check of Mv==wv'''
        lhs = gulinalg.matrix_multiply(A, v)
        rhs = w*v
        assert_allclose(lhs, rhs, rtol=1e-6)

    def _run_single(self, a):
        w, v = gulinalg.eig(a)
        w_2 = gulinalg.eigvals(a)
        assert_allclose(w, w_2)
        self._check_eigen(a, w, v)

    def _run_vector(self, a):
        for workers in [1, -1]:
            w, v = gulinalg.eig(a, workers=workers)
            w_2 = gulinalg.eigvals(a, workers=workers)
            assert_allclose(w, w_2)
            self._check_eigen(a, w[:, np.newaxis, :], v)

    def test_real(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(m, m)
        self._run_single(a)

    def test_complex(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(m, m) + 1j * rstate.randn(m, m)
        self._run_single(a)

    def test_real_vector(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m)
        self._run_vector(a)

    def test_complex_vector(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m)
        a = a + 1j * rstate.randn(n_batch, m, m)
        self._run_vector(a)

    def test_real_vector_f(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m)
        a = np.asfortranarray(a)
        self._run_vector(a)

    def test_real_vector_noncontig(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m, 2)[..., 0]
        self._run_vector(a)


class TestEigh(TestCase):
    """Test Eigenvalue Decomposition of (Hermetian) symmetric matrices"""

    def _check_eigen(self, A, w, v):
        '''vectorial check of Mv==wv'''
        lhs = gulinalg.matrix_multiply(A, v)
        rhs = w*v
        assert_allclose(lhs, rhs, rtol=1e-6)

    def _run_single(self, a):
        for uplo in ['L', 'U']:
            if uplo == 'L':
                w, v = gulinalg.eigh(np.tril(a), UPLO='L')
                w_2 = gulinalg.eigvalsh(np.tril(a), UPLO='L')
            else:
                w, v = gulinalg.eigh(np.triu(a), UPLO='U')
                w_2 = gulinalg.eigvalsh(np.triu(a), UPLO='U')
            assert_allclose(w, w_2)
            self._check_eigen(a, w, v)

    def _run_vector(self, a):
        for workers in [1, -1]:
            for uplo in ['L', 'U']:
                if uplo == 'L':
                    w, v = gulinalg.eigh(np.tril(a), UPLO='L', workers=workers)
                    w_2 = gulinalg.eigvalsh(np.tril(a), UPLO='L',
                                            workers=workers)
                else:
                    w, v = gulinalg.eigh(np.triu(a), UPLO='U', workers=workers)
                    w_2 = gulinalg.eigvalsh(np.triu(a), UPLO='U',
                                            workers=workers)
                assert_allclose(w, w_2)
                self._check_eigen(a, w[:, np.newaxis, :], v)

    def test_real(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(m, m)
        a = np.dot(a, a.T)  # make Hermetian symmetric
        self._run_single(a)

    def test_complex(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(m, m) + 1j * rstate.randn(m, m)
        a = np.dot(a, np.conj(a).T)  # make Hermetian symmetric
        self._run_single(a)

    def test_real_vector(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m)
        a = gulinalg.matrix_multiply(a, a.swapaxes(-2, -1))  # make symmetric
        self._run_vector(a)

    def test_complex_vector(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m)
        a = a + 1j * rstate.randn(n_batch, m, m)
        a = gulinalg.matrix_multiply(
            a, np.conj(a).swapaxes(-2, -1)  # make symmetric
        )
        self._run_vector(a)

    def test_real_vector_f(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m)
        a = gulinalg.matrix_multiply(a, a.swapaxes(-2, -1))  # make symmetric
        a = np.asfortranarray(a)
        self._run_vector(a)

    def test_real_vector_noncontig(self):
        m = 10
        rstate = np.random.RandomState(5)
        a = rstate.randn(n_batch, m, m, 2)[..., 0]
        a = gulinalg.matrix_multiply(a, a.swapaxes(-2, -1))  # make symmetric
        self._run_vector(a)


class TestLDL(TestCase):
    """Test LDL Decomposition of (Hermetian) symmetric matrices"""

    def _check_ldl(self, a, l, d):
        '''vectorial check of Mv==wv'''
        matmul = gulinalg.matrix_multiply
        assert_allclose(matmul(l, matmul(d, np.conj(l).swapaxes(-2, -1))), a)

    def test_real(self):
        m = 10
        a = np.random.randn(m, m)
        a = np.matmul(a, a.T)  # make symmetric
        l, d = gulinalg.ldl(a)
        self._check_ldl(a, l, d)

    def test_complex(self):
        m = 10
        a = np.random.randn(m, m) + 1j * np.random.randn(m, m)
        a = np.dot(a, np.conj(a).T)  # make Hermetian symmetric
        l, d = gulinalg.ldl(a)
        self._check_ldl(a, l, d)

    # TODO: fix workers > 1 case in MKL environments.
    #       segfault has been observed within mkl_blas_avx512_xdswap
    def test_real_vector(self):
        m = 10
        a = np.random.randn(n_batch, m, m)
        a = np.matmul(a, a.swapaxes(-2, -1))  # make symmetric
        for workers in [1, -1]:
            l, d = gulinalg.ldl(a, workers=workers)
            self._check_ldl(a, l, d)

    # TODO: fix workers > 1 case in MKL environments.
    #       segfault has been observed within mkl_blas_avx512_xdswap
    def test_complex_vector(self):
        m = 10
        a = np.random.randn(n_batch, m, m) + 1j * np.random.randn(n_batch, m, m)
        a = np.matmul(a, np.conj(a).swapaxes(-2, -1))  # make symmetric
        for workers in [1, ]:  #  -1]:    # XXX https://github.com/Quansight/gulinalg/issues/12
            l, d = gulinalg.ldl(a, workers=workers)
            self._check_ldl(a, l, d)
