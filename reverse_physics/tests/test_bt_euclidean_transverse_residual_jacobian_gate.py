"""Tests for the exact BT transverse residual-Jacobian gate."""

from __future__ import annotations

import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_transverse_residual_jacobian_gate as gate


class TransverseResidualJacobianGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_all_certificate_checks_pass(self) -> None:
        self.assertTrue(self.result["checks"]["ok"])
        self.assertEqual(self.result["checks"]["passed"], 17)

    def test_physical_projection_changes_the_laurent_sign_structure(self) -> None:
        audit = self.result["laurent_audit"]
        self.assertEqual(audit["unprojected_Dr"]["negative_term_count"], 0)
        self.assertEqual(audit["centered_P_H_Dr"]["negative_term_count"], 342)
        self.assertNotEqual(
            audit["unprojected_Dr"]["canonical_polynomial_sha256"],
            audit["centered_P_H_Dr"]["canonical_polynomial_sha256"],
        )

    def test_vacuum_is_strict_local_minimum_modulo_scale(self) -> None:
        eigenvalues = [
            Fraction(row["numerator"], row["denominator"])
            for row in self.result["local_vacuum_result"]["fourier_eigenvalues"]
        ]
        self.assertEqual(eigenvalues[0], 0)
        self.assertTrue(all(value > 0 for value in eigenvalues[1:]))

    def test_nonconvexity_witness_is_exactly_negative(self) -> None:
        witness = self.result["exact_nonconvexity_witness"]
        value = Fraction(
            witness["negative_order_five_minor"]["numerator"],
            witness["negative_order_five_minor"]["denominator"],
        )
        self.assertLess(value, 0)
        self.assertEqual(witness["dyadic_log2_exponents"], [1, -1, 2, -2, -2, 2])

    def test_finite_search_is_not_promoted_to_global_proof(self) -> None:
        self.assertEqual(
            self.result["finite_search"]["status"],
            "EXACT_FINITE_AUDIT_NOT_GLOBAL_PROOF",
        )
        self.assertEqual(
            self.result["method_disposition"]["centered_global_vacuum_minimum"],
            "OPEN",
        )

    def test_constant_scale_drops_out(self) -> None:
        polynomial = gate.jacobian_squared(projected=True)
        self.assertTrue(all(sum(exponent) == 0 for exponent in polynomial))

    def test_dropping_centering_is_detected(self) -> None:
        physical = gate.stats(gate.jacobian_squared(projected=True))
        mutation = gate.stats(gate.jacobian_squared(projected=False))
        self.assertNotEqual(physical["term_count"], mutation["term_count"])
        self.assertNotEqual(
            physical["canonical_polynomial_sha256"],
            mutation["canonical_polynomial_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
