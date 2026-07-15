from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_clock_reattached_principal_witness import (
    verify_certificate,
)


class BergerClockReattachedPrincipalWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_full_principal_completion(self) -> None:
        flags = self.payload["flags"]
        self.assertTrue(flags["BERGER_FULL_METRIC_BIWAVE_PRINCIPAL"])
        self.assertTrue(flags["BERGER_FULL_GHOST_BIWAVE_PRINCIPAL"])
        self.assertEqual(self.payload["principal_identities"]["metric_rank_off_characteristic"], 10)
        self.assertEqual(self.payload["principal_identities"]["ghost_rank_off_characteristic"], 5)

    def test_clock_reattachment_is_local(self) -> None:
        layout = self.payload["reattached_layout"]
        self.assertTrue(layout["support_local"])
        self.assertTrue(layout["clock_rows_remain_contractible"])
        self.assertEqual(layout["degree_ranks"], [5, 12, 12, 5])

    def test_downstream_claims_remain_open(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["BERGER_CURVED_CLOCK_REATTACHED_WITNESS"])
        self.assertFalse(flags["BERGER_CAUSAL_GREEN_HOMOTOPY"])
        self.assertFalse(flags["BERGER_ARITY_TWO_D_CARTAN"])


if __name__ == "__main__":
    unittest.main()
