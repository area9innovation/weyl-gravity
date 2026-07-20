from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.paneitz_higher_derivative_anomaly_column import build, validate
from anomalies.paneitz_higher_derivative_anomaly_column_certificate import (
    OUTPUT,
    build as build_certificate,
)
from anomalies.verify_paneitz_higher_derivative_anomaly_column import (
    verify,
    verify_payload,
)


class PaneitzHigherDerivativeAnomalyColumnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_two_routes_and_exact_checks(self) -> None:
        value = build()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            value["verified_column"]["coordinates"],
            [
                {"numerator": -1, "denominator": 15},
                {"numerator": 7, "denominator": 90},
                {"numerator": 0, "denominator": 1},
                {"numerator": 1, "denominator": 15},
            ],
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build_certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN",
        )

    def test_box_r_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["verified_column"]["coordinates"][3]["numerator"] = 2
        with self.assertRaisesRegex(ValueError, "coefficient"):
            verify_payload(mutant)

    def test_factorized_route_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["coefficient_routes"]["factorized_spectral_and_Casimir"][
            "summed_R2_b4"
        ]["numerator"] = 8
        with self.assertRaisesRegex(ValueError, "schema|route"):
            verify_payload(mutant)

    def test_first_solution_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["projected_anomaly_lattice"][
            "first_solution_by_minimal_vector_count"
        ]["multiplicities"]["N_vector"] = 60
        with self.assertRaisesRegex(ValueError, "lattice"):
            verify_payload(mutant)

    def test_zero_mode_policy_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["operator_payload"]["zero_mode_policy"] = "discard all zeros"
        with self.assertRaisesRegex(ValueError, "operator/sign"):
            verify_payload(mutant)

    def test_healthy_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["HEALTHY_CANCELLATION_EXISTS"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_gauge_column_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["HIGHER_DERIVATIVE_GAUGE_COLUMN_VERIFIED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
