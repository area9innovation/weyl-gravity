"""Tests for the d-times-axial-extra adjoint map."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_d_axial_ell2_extra_resonance import DEFAULT_OUTPUT


class DAxialResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_pairing_isomorphism(self) -> None:
        self.assertEqual(self.payload["pairing_theorem"]["determinant"], "832")
        self.assertTrue(self.payload["classification"]["d_cross_adjoint_map_invertible"])

    def test_all_m(self) -> None:
        self.assertTrue(self.payload["classification"]["all_m_by_SO3_equivariance"])

    def test_scope_boundary(self) -> None:
        self.assertFalse(self.payload["classification"]["full_second_order_equation_solved"])
        self.assertFalse(self.payload["classification"]["polar_d_cross_block_classified"])
        self.assertEqual(self.payload["correction_class"], "BOUNDED_OR_FINITE_QUASIPERIODIC")


if __name__ == "__main__":
    unittest.main()
