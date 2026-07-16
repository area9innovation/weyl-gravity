import unittest

from d_quotient_classical.backreacted_clock.berger_metric_lower_by_two_biwave import build, verify


class BergerMetricLowerByTwoBiwaveTest(unittest.TestCase):
    def test_exact_normal_form(self):
        payload, _ = build()
        verify(payload)
        self.assertEqual(payload["normal_form"]["maximum_order_V2"], 2)
        self.assertEqual(payload["normal_form"]["degree_two_symbol_ranks"]["null"], 7)
        self.assertFalse(payload["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"])


if __name__ == "__main__":
    unittest.main()
