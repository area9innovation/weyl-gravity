from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system import (
    CERT,
    verify,
)


class CrossFibreAmplitudeSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_independent_replay(self) -> None:
        verify()

    def test_physical_fibres_are_separate(self) -> None:
        summary = self.value["summary"]
        self.assertEqual(summary["pairwise_distinct_algebraic_circumference_fibres"], 21)
        self.assertEqual((summary["L1_fibres"], summary["L3_fibres"], summary["L4_fibres"]), (3, 6, 12))

    def test_all_m_system_is_complete(self) -> None:
        summary = self.value["summary"]
        self.assertEqual(summary["target_parity_adjoint_equations_before_M_expansion"], 54)
        self.assertEqual(summary["ordered_branch_basis_fixtures"], 128)
        self.assertEqual(summary["certified_reduced_internal_coefficients"], 164)
        self.assertEqual(summary["nonzero_reduced_internal_coefficients"], 162)
        self.assertEqual(summary["zero_reduced_internal_coefficients"], 2)
        self.assertEqual(summary["factorized_complex_scalar_magnetic_equations"], 418)
        self.assertTrue(
            self.value["classification"]["factorized_cross_fibre_resonance_system_certified"]
        )

    def test_zero_variety_and_taub_join_stay_open(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["mandatory_first_fibre_zero_plane_certified"])
        self.assertTrue(classification["mandatory_second_fibre_zero_plane_certified"])
        self.assertFalse(classification["irreducible_zero_variety_decomposition_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
