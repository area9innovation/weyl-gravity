from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_all_weight_arity_two_d_cartan import verify_certificate


class BergerAllWeightArityTwoDCartanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_nonzero_weight_cartan_contraction(self) -> None:
        self.assertTrue(self.payload["arity_two_Cartan_source"]["nonzero_for_generic_nonzero_weights"])
        self.assertTrue(self.payload["flags"]["BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN"])
        self.assertTrue(self.payload["flags"]["NONZERO_WEIGHT_D_CARTAN_TESTED"])
        self.assertFalse(self.payload["flags"]["NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"])

    def test_locality_and_closure(self) -> None:
        self.assertEqual(self.payload["all_weight_complex"]["weight_lattice"], "Z")
        self.assertTrue(self.payload["linear_Cartan_homotopy"]["support_local_in_time"])
        self.assertTrue(self.payload["arity_two_Cartan_homotopy"]["support_local_in_time"])
        self.assertEqual(self.payload["arity_two_Cartan_homotopy"]["differential_order_in_time"], 1)

    def test_full_theory_boundary(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["FULL_4D_SUPPORT_LOCAL_Q2"])
        self.assertFalse(flags["COMPLETE_54_ROW_ARITY_TWO_D_CARTAN"])
        self.assertFalse(flags["ND2_PHYSICAL_EXECUTION_AUTHORIZED"])


if __name__ == "__main__":
    unittest.main()
