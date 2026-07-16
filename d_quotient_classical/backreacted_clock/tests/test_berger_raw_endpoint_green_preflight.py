import json
import unittest

from d_quotient_classical.backreacted_clock.berger_raw_endpoint_green_preflight import (
    CERTIFICATE_PATH,
    _exact_data,
)


class BergerRawEndpointGreenPreflightTests(unittest.TestCase):
    def test_rank_one_wave_extension_rebuilds(self):
        data = _exact_data()
        self.assertEqual(data["orders"]["BC_schur_correction"], 6)
        self.assertEqual(data["ranks"]["generic"], 1)
        self.assertEqual(data["ranks"]["null"], 0)

    def test_green_flags_remain_false(self):
        flags = json.loads(CERTIFICATE_PATH.read_text())["flags"]
        self.assertTrue(flags["BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT"])
        self.assertFalse(flags["BERGER_RAW_ENDPOINT_FILTERED_GREEN_EXTENSION"])
        self.assertFalse(flags["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])


if __name__ == "__main__":
    unittest.main()
