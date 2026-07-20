import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification import (
    OUTPUT,
    build,
    exact_incidence_algebra,
    occupation_strata,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification import (
    verify,
)


class Candidate1720ComponentIncidenceClassificationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = build()

    def test_frozen_payload_rebuilds(self) -> None:
        self.assertEqual(self.payload, json.loads(OUTPUT.read_text()))

    def test_exact_boundary_incidence(self) -> None:
        algebra = exact_incidence_algebra()
        self.assertEqual(algebra["negative_delta_incidence"]["identity"], "0")
        self.assertEqual(algebra["positive_delta_incidence"]["identity"], "0")

    def test_occupation_partition_retains_boundaries(self) -> None:
        strata = occupation_strata()
        self.assertEqual(
            [item["id"] for item in strata],
            ["interior", "F_zero", "G_zero", "origin"],
        )
        self.assertIn("U(1)_F", strata[1]["forced_stabilizer"])
        self.assertIn("U(1)_G", strata[2]["forced_stabilizer"])

    def test_each_candidate_chamber_has_one_incident_component(self) -> None:
        for record in self.payload["candidate_components"].values():
            self.assertEqual(record["component_count"], 1)
            self.assertTrue(record["components"][0]["meets_incidence"])
            self.assertEqual(record["nonincident_components"], [])

    def test_fail_closed_boundaries(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["candidate17_candidate20_identified"])
        self.assertFalse(
            flags["occupation_strata_glued_across_distinct_total_occupations"]
        )
        self.assertFalse(flags["final_residual_descent"])
        self.assertFalse(flags["causal_observer_or_quantum_claim"])

    def test_independent_verifier(self) -> None:
        verify()


if __name__ == "__main__":
    unittest.main()
