from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_retained_minimal_operator import (
    verify_certificate,
)


class BergerRetainedMinimalOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_complete_minimal_q1(self) -> None:
        flags = self.payload["flags"]
        self.assertTrue(flags["retained_q1_coefficients_complete"])
        self.assertTrue(flags["retained_q1_squared_verified"])
        self.assertTrue(flags["retained_cyclicity_verified"])
        self.assertTrue(flags["BERGER_RETAINED_MINIMAL_OPERATOR"])

    def test_all_bach_orders_present(self) -> None:
        counts = self.payload["bach_PBW_term_counts_by_order"]
        self.assertEqual(set(counts), {"0", "1", "2", "3", "4"})
        self.assertTrue(all(counts[str(order)] > 0 for order in range(5)))

    def test_downstream_gates_remain_open(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["BERGER_NONMINIMAL_COMPLETION"])
        self.assertFalse(flags["BERGER_CAUSAL_GREEN_HOMOTOPY"])
        self.assertFalse(flags["CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"])


if __name__ == "__main__":
    unittest.main()
