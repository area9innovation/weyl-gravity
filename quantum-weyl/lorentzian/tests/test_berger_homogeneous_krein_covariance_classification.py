from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from lorentzian.berger_homogeneous_krein_covariance_classification import build
from lorentzian.berger_homogeneous_krein_covariance_classification_certificate import (
    OUTPUT,
)
from lorentzian.verify_berger_homogeneous_krein_covariance_classification import (
    verify,
    verify_payload,
)


class HomogeneousKreinCovarianceClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_producer_exact_totals(self) -> None:
        value = build()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            value["homogeneous_spectral_classification"]["totals"],
            {
                "combined_real_dimension": 80,
                "forced_positive_radical_dimension": 26,
                "invariant_symmetric_parameter_dimension": 128,
                "positive_cone_linear_span_dimension": 95,
                "positive_rank_capacity": 54,
            },
        )

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "BERGER_HOMOGENEOUS_KREIN_COVARIANCE_CLASSIFICATION",
        )

    def test_real_root_mutation_is_rejected(self) -> None:
        value = deepcopy(self.value)
        value["homogeneous_spectral_classification"][
            "instability_root_ledger"
        ]["polynomial_coefficients_descending"][0] = 10
        with self.assertRaisesRegex(ValueError, "root mutation"):
            verify_payload(value)

    def test_commutator_mutation_is_rejected(self) -> None:
        value = deepcopy(self.value)
        value["action_pairing"]["matrix_hashes"]["Omega80"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Omega80"):
            verify_payload(value)

    def test_real_involution_mutation_is_rejected(self) -> None:
        value = deepcopy(self.value)
        value["action_pairing"]["matrix_hashes"]["real_involution80"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "real-involution"):
            verify_payload(value)

    def test_positive_claim_mutation_is_rejected(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"][
            "HOMOGENEOUS_STATIONARY_POSITIVE_CCR_COVARIANCE_EXISTS"
        ] = True
        with self.assertRaises(ValueError):
            verify_payload(value)


if __name__ == "__main__":
    unittest.main()
