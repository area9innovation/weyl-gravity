from __future__ import annotations

import json
import unittest

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import CERTIFICATE
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.verify import verify_data


class EndpointEnclosureTests(unittest.TestCase):
    def test_certificate_boundary(self):
        self.assertTrue(verify_data(json.loads(CERTIFICATE.read_text())))

    def test_horizon_and_infinity_evidence_boundary(self):
        data = json.loads(CERTIFICATE.read_text())
        self.assertTrue(data["claim_flags"]["horizon_six_column_initializer_certified"])
        self.assertTrue(data["claim_flags"]["infinity_six_column_existence_enclosure_certified"])
        self.assertFalse(data["claim_flags"]["infinity_six_column_initializer_certified"])
        self.assertEqual(
            data["infinity"]["practical_handoff_disposition"],
            "NOT_STABLE_FOR_IVLINODE",
        )
        self.assertEqual(data["stop_condition_disposition"], "SHORTFALL")


if __name__ == "__main__":
    unittest.main()
