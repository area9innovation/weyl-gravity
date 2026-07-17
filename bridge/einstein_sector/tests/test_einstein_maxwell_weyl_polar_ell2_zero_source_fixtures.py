"""Regression test for the polar ell=2 Hermitian source-rank audit."""

import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ell2_zero_source_fixtures import verify_fixtures


class PolarEll2ZeroSourceFixturesTest(unittest.TestCase):
    def test_fixtures(self) -> None:
        verify_fixtures()


if __name__ == "__main__":
    unittest.main()
