import json
import unittest

from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH,
    _exact_data,
)


class BergerRawClockReattachedWitnessTransportTests(unittest.TestCase):
    def test_exact_transport_rebuilds(self):
        data = _exact_data()
        self.assertEqual(data["temporal"][1][:10, :10].rank(), 10)
        self.assertEqual(data["temporal"][2][:10, :10].rank(), 10)

    def test_transport_promoted_but_green_is_not(self):
        payload = json.loads(CERTIFICATE_PATH.read_text())
        flags = payload["flags"]
        self.assertTrue(flags["BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT"])
        self.assertTrue(flags["BERGER_RAW_CLOCK_REATTACHED_PRINCIPAL_COMPATIBILITY"])
        self.assertFalse(flags["BERGER_RAW_CLOCK_REATTACHED_GREEN_INVERSION"])
        self.assertFalse(flags["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])

    def test_clock_block_is_triangular_not_propagating(self):
        payload = json.loads(CERTIFICATE_PATH.read_text())
        audit = payload["raw_principal_audit"]
        self.assertEqual(audit["clock_diagonal_order_four_rank"], 0)
        self.assertEqual(audit["metric_to_clock_order_four_rank"], 1)


if __name__ == "__main__":
    unittest.main()
