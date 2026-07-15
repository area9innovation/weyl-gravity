from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_causal_witness_preflight import (
    verify_certificate,
)


class BergerCausalWitnessPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_endpoint_factors(self) -> None:
        flags = self.payload["flags"]
        self.assertTrue(flags["BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC"])
        self.assertTrue(flags["BERGER_IDENTITY_ENDPOINT_GREEN_HYPERBOLIC"])

    def test_metric_boundary(self) -> None:
        boundary = self.payload["metric_mixed_order_boundary"]
        self.assertEqual(boundary["fourth_order_rank"], 8)
        self.assertEqual(boundary["fourth_order_kernel_dimension"], 2)
        self.assertFalse(boundary["green_realization_constructed"])

    def test_downstream_gates(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION"])
        self.assertFalse(flags["BERGER_CAUSAL_GREEN_HOMOTOPY"])
        self.assertFalse(flags["BERGER_ARITY_TWO_D_CARTAN"])


if __name__ == "__main__":
    unittest.main()
