import json
import unittest

from d_quotient_classical.backreacted_clock.berger_raw_endpoint_rank_one_wave_extension import CERTIFICATE_PATH, _exact_data


class BergerRawEndpointRankOneWaveExtensionTests(unittest.TestCase):
    def test_exact_prolongation_rebuilds(self):
        data = _exact_data()
        self.assertEqual(data["b2"].rank(), 1)
        self.assertEqual(data["c4"].rank(), 1)

    def test_extension_promoted_but_green_remains_open(self):
        payload = json.loads(CERTIFICATE_PATH.read_text())
        self.assertTrue(payload["flags"]["BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION"])
        self.assertFalse(payload["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"])
        self.assertFalse(payload["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])

    def test_fixed_incidence_no_go_is_scoped(self):
        payload = json.loads(CERTIFICATE_PATH.read_text())
        no_go = payload["fixed_incidence_no_go"]
        self.assertEqual(no_go["defect_nonzero_entries"], 8)
        self.assertIn("fixed K12", no_go["scope"])


if __name__ == "__main__":
    unittest.main()
