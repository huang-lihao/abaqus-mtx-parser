# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import numpy as np
import unittest

from importlib.resources import files
from abaqus_mtx_parser import parse_mtx


class TestAbaqusMtxParser(unittest.TestCase):

    def test_unsymmetric_stiffness(self):
        mtx = files("abaqus_mtx_parser.mtx").joinpath("unsym.mtx")
        result = parse_mtx(mtx)
        for r in result:
            if (r[0] == "MATRIX" and
                r[1]["parameter"]["TYPE"] == "STIFFNESS"
            ):
                matrix = r[1]["data"]
                for v_pair in [
                    (matrix[1, 3], -.17762711516914E-09),
                    (matrix[3, 1], -.17680651844574E-09),
                ]:
                    self.assertAlmostEqual(
                        v_pair[0], v_pair[1], delta = v_pair[1] * 1e-5)

    def test_symmetric_stiffness(self):
        mtx = files("abaqus_mtx_parser.mtx").joinpath("sym.mtx")
        result = parse_mtx(mtx)
        for r in result:
            if (r[0] == "MATRIX" and
                r[1]["parameter"]["TYPE"] == "STIFFNESS"
            ):
                matrix = r[1]["data"]
                print(matrix)
                for v_pair in [
                    (matrix[1, 3], -.17773628812504E-09),
                    (matrix[3, 1], -.17773628812504E-09),
                ]:
                    self.assertAlmostEqual(
                        v_pair[0], v_pair[1], delta = v_pair[1] * 1e-5)


if __name__ == "__main__":
    unittest.main()
