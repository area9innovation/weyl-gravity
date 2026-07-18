from __future__ import annotations

from copy import deepcopy
import json
import unittest

from spectral.euclidean.nonconformal_coefficient_match_receiver import (
    validate_nonconformal_coefficient_match,
)
from spectral.euclidean.repository_ricci_flat_coefficient_match import OUTPUT, ROOT, build
from spectral.euclidean.verify_repository_ricci_flat_coefficient_match import verify


class RepositoryRicciFlatCoefficientMatchTests(unittest.TestCase):
    def test_physical_coefficient_match_is_accepted(self) -> None:
        receipt = validate_nonconformal_coefficient_match(build()[-1], repository_root=ROOT)
        self.assertEqual(receipt["coefficients"]["C2"], {"numerator": 199, "denominator": 30})
        self.assertEqual(receipt["coefficients"]["E4"], {"numerator": -87, "denominator": 20})

    def test_factor_and_artifact_mutations_are_rejected(self) -> None:
        value = build()[-1]
        mutant = deepcopy(value)
        mutant["coefficient_result"]["factor_contributions"][0]["coordinates"]["C2"]["numerator"] += 1
        with self.assertRaisesRegex(ValueError, "factor sum"):
            validate_nonconformal_coefficient_match(mutant, repository_root=ROOT)
        mutant = deepcopy(value)
        mutant["operator_and_measure"]["local_measure_artifact"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_nonconformal_coefficient_match(mutant, repository_root=ROOT)
        mutant = deepcopy(value)
        mutant["coefficient_result"]["factor_contributions"].reverse()
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_nonconformal_coefficient_match(mutant, repository_root=ROOT)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build()[-1])
        self.assertEqual(verify()["status"], "SEMANTIC_RECEIVER_ACCEPTED")


if __name__ == "__main__":
    unittest.main()
