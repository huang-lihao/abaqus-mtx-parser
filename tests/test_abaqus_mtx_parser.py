# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from importlib.resources import files
from abaqus_mtx_parser import parse_mtx


class TestAbaqusMtxParser(unittest.TestCase):

    def test_unsymmetric_stiffness(self):
        mtx = files("abaqus_mtx_parser.mtx").joinpath("unsym.mtx")
        result = parse_mtx(mtx)
    
    def test_symmetric_stiffness(self):
        mtx = files("abaqus_mtx_parser.mtx").joinpath("sym.mtx")
        result = parse_mtx(mtx)


if __name__ == "__main__":
    unittest.main()