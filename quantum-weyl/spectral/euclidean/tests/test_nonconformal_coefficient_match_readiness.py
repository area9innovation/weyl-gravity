from __future__ import annotations

import json
import unittest

from spectral.euclidean.nonconformal_coefficient_match_readiness import (
    OUTPUT,
    build,
    mutation_receipts,
)
from spectral.euclidean.nonconformal_coefficient_match_receiver import synthetic_payload
from spectral.euclidean.verify_nonconformal_coefficient_match_readiness import verify


class NonconformalCoefficientMatchReadinessTests(unittest.TestCase):
    def test_receiver_mutations_are_rejected(self) -> None:
        self.assertTrue(all(row["rejected"] for row in mutation_receipts(synthetic_payload())))

    def test_current_candidates_fail_complementary_gates(self) -> None:
        value = build()
        by_id = {row["candidate_id"]: row for row in value["current_candidate_audit"]}
        self.assertTrue(by_id["NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1"]["C2_visible"])
        self.assertFalse(
            by_id["NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1"][
                "Euclidean_elliptic_full_BV"
            ]
        )
        self.assertFalse(by_id["REPOSITORY_ROUND_S4_EULER_COEFFICIENT"]["C2_visible"])
        self.assertFalse(value["claim_flags"]["REPOSITORY_C2_COEFFICIENT_COMPUTED"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
