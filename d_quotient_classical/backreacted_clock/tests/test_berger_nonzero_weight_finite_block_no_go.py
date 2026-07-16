from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_nonzero_weight_finite_block_no_go import verify_certificate


class BergerNonzeroWeightFiniteBlockNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_square_map_is_anisotropic(self) -> None:
        self.assertTrue(self.payload["flags"]["BERGER_Q2_SQUARE_MAP_ANISOTROPIC"])
        self.assertEqual(
            self.payload["real_anisotropy_certificate"]["leading_principal_minors"],
            ["171/80", "44649/6400", "38549/15360"],
        )

    def test_first_leakage_is_normalized(self) -> None:
        failed = self.payload["first_failed_block"]
        self.assertEqual(failed["missing_output_weight"], 2)
        self.assertEqual(failed["first_failed_row"], "E_u_(+2)")
        self.assertEqual(failed["first_failed_coefficient"], "27/80")
        self.assertEqual(failed["witness_evaluation"], "1")

    def test_scope_is_fail_closed(self) -> None:
        flags = self.payload["flags"]
        self.assertTrue(flags["BERGER_NONZERO_WEIGHT_FINITE_BLOCK_NO_GO"])
        self.assertTrue(flags["NONZERO_WEIGHT_MODE_CLOSURE_OBSTRUCTION"])
        self.assertFalse(flags["NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"])
        self.assertFalse(flags["CLASSICAL_SUPPORT_LOCAL_Q2"])
        self.assertFalse(flags["ND2_PHYSICAL_EXECUTION_AUTHORIZED"])


if __name__ == "__main__":
    unittest.main()
