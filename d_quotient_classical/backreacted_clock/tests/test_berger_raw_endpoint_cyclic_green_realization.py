import json
import unittest

from d_quotient_classical.backreacted_clock.berger_raw_endpoint_cyclic_green_realization import CERTIFICATE_PATH, _exact_data


class BergerRawEndpointCyclicGreenRealizationTests(unittest.TestCase):
    def test_graph_sdr_rebuilds(self):
        data = _exact_data()
        self.assertEqual(len(data["p36"]), 36)
        self.assertEqual(len(data["l13_sharp"]), 13)

    def test_ranks_and_lifecycle(self):
        payload = json.loads(CERTIFICATE_PATH.read_text())
        self.assertEqual(payload["row_layout"]["authoritative_BV_degree_ranks"], [5, 12, 12, 5])
        self.assertEqual(payload["row_layout"]["analytic_realization_degree_ranks"], [5, 13, 13, 5])
        self.assertTrue(payload["flags"]["BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION"])
        self.assertFalse(payload["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"])

    def test_zero_mode_policy_forbids_spatial_projector(self):
        payload = json.loads(CERTIFICATE_PATH.read_text())
        self.assertFalse(payload["causal_policy"]["spatial_zero_mode_projector"])
        self.assertIn("causal Cauchy", payload["causal_policy"]["zero_mode_policy"])


if __name__ == "__main__":
    unittest.main()
