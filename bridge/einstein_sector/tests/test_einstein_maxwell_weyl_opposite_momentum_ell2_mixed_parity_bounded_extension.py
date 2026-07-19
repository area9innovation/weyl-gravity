"""Tests for the tuned mixed-parity bounded-extension certificate."""

from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension import build


class MixedParityBoundedExtensionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_unique_collision(self) -> None:
        self.assertEqual(
            self.payload["collision_census"]["collisions"],
            [{"frequency": "two_omega_minus", "momentum": "K_zero", "ell": "4", "target": "p"}],
        )
        self.assertEqual(self.payload["collision_census"]["check_count"], 80)

    def test_bounded_extension_is_scoped(self) -> None:
        classes = self.payload["correction_classes"]
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "CERTIFIED")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        flags = self.payload["classification"]
        self.assertTrue(flags["one_nonzero_tuned_bounded_second_order_tangent_certified"])
        self.assertFalse(flags["general_mixed_null_face_classified"])

    def test_all_noncollisions_have_exact_witnesses(self) -> None:
        rows = self.payload["collision_census"]["checks"]
        self.assertEqual(sum(row["collision"] for row in rows), 1)
        self.assertTrue(
            all(
                row["collision"] or row["nonzero_witness"]["minimal_polynomial_constant"] != "0"
                for row in rows
            )
        )


if __name__ == "__main__":
    unittest.main()
