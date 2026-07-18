from __future__ import annotations

import json
import unittest

from spectral.euclidean.round_s4_conformal_volume_locality import OUTPUT, build, conformal_dimension
from spectral.euclidean.verify_round_s4_conformal_volume_locality import verify


class RoundS4ConformalVolumeLocalityTests(unittest.TestCase):
    def test_conformal_dimension_and_noncompact_volume(self) -> None:
        self.assertEqual(conformal_dimension(), 15)
        value = build()
        self.assertEqual(value["group_ledger"]["naive_Haar_volume"], "NONCOMPACT_DIVERGENT")
        self.assertFalse(value["claim_flags"]["GLOBAL_COLLECTIVE_COORDINATE_MEASURE_NORMALIZED"])

    def test_local_and_global_measure_status_are_separate(self) -> None:
        flags = build()["claim_flags"]
        self.assertTrue(flags["VOLUME_NORMALIZATION_IRRELEVANT_TO_LOCAL_SLAVNOV_FIXED_STRATUM"])
        self.assertFalse(flags["REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
