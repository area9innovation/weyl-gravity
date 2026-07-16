import json
import unittest

from d_quotient_classical.backreacted_clock import berger_54_row_causal_green_homotopy as theorem


class Berger54RowCausalGreenHomotopyTest(unittest.TestCase):
    def test_complete_causal_lift(self):
        payload = theorem.build()
        theorem.verify(payload)
        self.assertTrue(payload["flags"]["BERGER_CAUSAL_GREEN_HOMOTOPY"])
        self.assertFalse(payload["flags"]["BERGER_HADAMARD_DATA"])

    def test_persisted_certificate(self):
        self.assertEqual(json.loads(theorem.CERTIFICATE_PATH.read_text()), theorem.build())


if __name__ == "__main__":
    unittest.main()
