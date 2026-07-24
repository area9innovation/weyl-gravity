from __future__ import annotations

import copy
import json
import unittest

from .. import verify


class ParameterDeformationCohomologyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(verify.CERTIFICATE.read_text())

    def test_committed_certificate_verifies(self) -> None:
        self.assertEqual(verify.verify_document(self.document), [])

    def test_mass_family_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.document)
        mutated["mass_family_derivation"]["companion_A_M"][1][0] = "0"
        self.assertIn(
            "M-dependent companion drift",
            verify.verify_document(mutated),
        )

    def test_horizon_residue_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.document)
        mutated["trace_residue_audit"]["residues"]["r=2"] = "0"
        self.assertIn(
            "residue drift: r=2",
            verify.verify_document(mutated),
        )

    def test_scale_gauge_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.document)
        mutated["scale_coboundary"]["gauge_B_scale"][0][1] = "0"
        self.assertIn(
            "recorded scale gauge drift",
            verify.verify_document(mutated),
        )

    def test_pure_coboundary_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.document)
        mutated["cohomology_conclusion"][
            "pure_E_RW_coboundary_status"
        ] = "TRIVIAL"
        self.assertIn(
            "pure extension coboundary was overclaimed",
            verify.verify_document(mutated),
        )

    def test_beta_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.document)
        mutated["claim_flags"]["beta_n_computed"] = True
        self.assertIn(
            "open or negative flag promoted: beta_n_computed",
            verify.verify_document(mutated),
        )

    def test_lambda_admission_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.document)
        mutated["scope_refusals"]["Lambda"] = "d_Lambda A is allowed"
        self.assertIn(
            "undefined Lambda derivative was admitted",
            verify.verify_document(mutated),
        )


if __name__ == "__main__":
    unittest.main()
