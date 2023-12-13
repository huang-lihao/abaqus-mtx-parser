# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import numpy as np
import unittest

from importlib.resources import files
from abaqus_mtx_parser import parse_mtx


class TestAbaqusMtxParser(unittest.TestCase):

    def test_unsymmetric_stiffness(self):
        mtx = files("abaqus_mtx_parser.mtx.unsymmetric").joinpath("inner.mtx")
        result = parse_mtx(mtx)

        # Test nodes and dof
        self.assertListEqual(result.nodes, [2, 3, 4, 5, 6, 7])
        self.assertDictEqual(result.dof, {2: [1, 2, 3, 4, 5, 6], 3: [1, 2, 3, 4, 5, 6], 4: [1, 2, 3, 4, 5, 6], 5: [1, 2, 3, 4, 5, 6], 6: [1, 2, 3, 4, 5, 6], 7: [1, 2, 3, 4, 5, 6]})

        # Test stiffness matrix
        matrix = result.stiffness
        for v_pair in [
            (matrix[1, 3], -.17762711516914E-09),
            (matrix[3, 1], -.17680651844574E-09),
        ]:
            self.assertAlmostEqual(
                v_pair[0], v_pair[1], delta = v_pair[1] * 1e-5)

    def test_symmetric_stiffness(self):
        mtx = files("abaqus_mtx_parser.mtx.symmetric").joinpath("inner.mtx")
        result = parse_mtx(mtx)

        # Test nodes and dof
        self.assertListEqual(result.nodes, [2, 3, 4, 5, 6, 7])
        self.assertDictEqual(result.dof, {2: [1, 2, 3, 4, 5, 6], 3: [1, 2, 3, 4, 5, 6], 4: [1, 2, 3, 4, 5, 6], 5: [1, 2, 3, 4, 5, 6], 6: [1, 2, 3, 4, 5, 6], 7: [1, 2, 3, 4, 5, 6]})

        # Test stiffness matrix
        matrix = result.stiffness
        for v_pair in [
            (matrix[1, 3], -.17773628812504E-09),
            (matrix[3, 1], -.17773628812504E-09),
        ]:
            self.assertAlmostEqual(
                v_pair[0], v_pair[1], delta = v_pair[1] * 1e-5)
    
    def test_symmetric_static_condensation(self):
        inner = parse_mtx(
            files("abaqus_mtx_parser.mtx.symmetric").joinpath("inner.mtx"))
        outer = parse_mtx(
            files("abaqus_mtx_parser.mtx.symmetric").joinpath("outer.mtx"))
        total = parse_mtx(
            files("abaqus_mtx_parser.mtx.symmetric").joinpath("total.mtx"))

        K = np.zeros((72, 72))
        E = np.arange( 0, 36,  1)
        R = np.arange(36, 72,  1)
        K[np.ix_(E, E)] += inner.stiffness
        K += outer.stiffness

        K_EE = K[np.ix_(E, E)]
        K_RE = K[np.ix_(R, E)]
        K_ER = K[np.ix_(E, R)]
        K_RR = K[np.ix_(R, R)]

        K1 = K_RR - np.linalg.multi_dot([K_RE, np.linalg.inv(K_EE), K_ER])

        self.assertTrue(np.allclose(K1, total.stiffness))
    
    def test_unsymmetric_static_condensation(self):
        inner = parse_mtx(
            files("abaqus_mtx_parser.mtx.unsymmetric").joinpath("inner.mtx"))
        outer = parse_mtx(
            files("abaqus_mtx_parser.mtx.unsymmetric").joinpath("outer.mtx"))
        total = parse_mtx(
            files("abaqus_mtx_parser.mtx.unsymmetric").joinpath("total.mtx"))

        K = np.zeros((72, 72))
        E = np.arange( 0, 36,  1)
        R = np.arange(36, 72,  1)
        K[np.ix_(E, E)] += inner.stiffness
        K += outer.stiffness

        K_EE = K[np.ix_(E, E)]
        K_RE = K[np.ix_(R, E)]
        K_ER = K[np.ix_(E, R)]
        K_RR = K[np.ix_(R, R)]

        K1 = K_RR - np.linalg.multi_dot([K_RE, np.linalg.inv(K_EE), K_ER])

        self.assertTrue(np.allclose(K1, total.stiffness))

if __name__ == "__main__":
    unittest.main()
