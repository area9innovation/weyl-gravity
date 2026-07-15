from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_gauge_fixed_nonminimal_completion import verify_certificate


class BergerGaugeFixedNonminimalCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_gauge_fixed_unary_package(self) -> None:
        self.assertTrue(self.payload["flags"]["BERGER_NONMINIMAL_COMPLETION"])
        self.assertEqual(self.payload["classical_unary_q1"]["shape"], [54, 54])
        self.assertTrue(self.payload["classical_unary_q1"]["squared_zero"])

    def test_portable_contraction(self) -> None:
        self.assertEqual(self.payload["row_layout"]["total_rows"], 54)
        self.assertTrue(self.payload["contraction"]["support_local"])
        self.assertLessEqual(self.payload["contraction"]["maximum_differential_order"], 4)

    def test_nonlinear_and_analytic_gates_remain_open(self) -> None:
        self.assertEqual(self.payload["next_gate"], "CLASSICAL_SUPPORT_LOCAL_Q2_AND_D_ACTION")
        for key in (
            "CLASSICAL_SUPPORT_LOCAL_Q2",
            "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
            "BERGER_GENERAL_KOSZUL_TATE_EXPORT",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_HADAMARD_DATA",
        ):
            self.assertFalse(self.payload["flags"][key])


if __name__ == "__main__":
    unittest.main()
