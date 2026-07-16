import unittest

from d_quotient_classical.backreacted_clock.berger_raw_endpoint_metric_cone_no_go import build, verify


class BergerRawEndpointMetricConeNoGoTest(unittest.TestCase):
    def test_extra_characteristic_is_exact_and_fail_closed(self):
        payload = build()
        verify(payload)
        symbol = payload["douglis_symbol"]
        self.assertEqual(symbol["extra_characteristic_speed"], "sqrt(2)")
        self.assertEqual(symbol["rank_on_generic_extra_characteristic"], 12)
        self.assertFalse(payload["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"])


if __name__ == "__main__":
    unittest.main()
