from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_nonminimal_algebraic_completion import verify_certificate


class BergerNonminimalAlgebraicCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_complete_row_inventory_and_contraction(self) -> None:
        self.assertEqual(self.payload["row_layout"]["total_rows"], 54)
        self.assertEqual(self.payload["row_layout"]["nonminimal_rows"], 20)
        self.assertTrue(self.payload["flags"]["BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION"])

    def test_gauge_shear_is_fail_closed(self) -> None:
        self.assertFalse(self.payload["gauge_fermion_template"]["canonical_transform_applied"])
        self.assertFalse(self.payload["flags"]["BERGER_NONMINIMAL_COMPLETION"])
        self.assertEqual(self.payload["next_gate"], "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM")

    def test_quantum_wishlist_remains_open(self) -> None:
        flags = self.payload["flags"]
        for key in (
            "CLASSICAL_SUPPORT_LOCAL_Q2",
            "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
            "BERGER_GENERAL_KOSZUL_TATE_EXPORT",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_HADAMARD_DATA",
        ):
            self.assertFalse(flags[key])


if __name__ == "__main__":
    unittest.main()
