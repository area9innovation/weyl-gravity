from __future__ import annotations

from copy import deepcopy
import json
import unittest

from lorentzian.berger_a104_endpoint_completion import OUTPUT, build, validate
from lorentzian.verify_berger_a104_endpoint_completion import verify as independent_verify


class BergerA104EndpointCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checked = json.loads(OUTPUT.read_text())
        cls.built, cls.operator = build()

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(self.built, self.checked)

    def test_full_coordinate_coverage(self) -> None:
        self.assertEqual(self.built["coverage"]["known_coordinates"], 10816)
        self.assertEqual(self.built["coverage"]["unknown_coordinates"], 0)
        self.assertEqual(self.operator["shape"], [104, 104])

    def test_independent_verifier(self) -> None:
        independent_verify()

    def test_q_cauchy_cannot_be_promoted(self) -> None:
        mutant = deepcopy(self.built)
        mutant["claim_flags"]["BERGER_Q_CAUCHY_104"] = True
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_previous_partial_operator_is_preserved(self) -> None:
        self.assertTrue(
            self.built["exact_checks"]["partial_10528_coordinates_preserved"]
        )

    def test_source_manifest_is_complete(self) -> None:
        self.assertEqual(len(self.built["provenance"]["source_manifest"]), 5)


if __name__ == "__main__":
    unittest.main()
