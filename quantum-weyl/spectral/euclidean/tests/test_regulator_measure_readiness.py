from __future__ import annotations

import json
import unittest

from spectral.euclidean.regulator_measure_readiness import OUTPUT, build, mutation_receipts
from spectral.euclidean.regulator_measure_receiver import synthetic_payload
from spectral.euclidean.verify_regulator_measure_readiness import verify


class RegulatorMeasureReadinessTests(unittest.TestCase):
    def test_exact_mutations_are_rejected(self) -> None:
        self.assertTrue(all(row["rejected"] for row in mutation_receipts(synthetic_payload())))

    def test_candidates_do_not_compose_implicitly(self) -> None:
        value = build()
        self.assertTrue(all(not row["complete"] for row in value["current_candidate_audit"]))
        self.assertFalse(value["claim_flags"]["REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED"])
        self.assertTrue(value["claim_flags"]["NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND"])
        standard = value["current_candidate_audit"][0]
        self.assertTrue(standard["global_phase_policy"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
