from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import ValidationError

from d_quotient_classical.causal_transfer import (
    berger_26_row_smooth_bikernel_homotopy_support_gate as subject,
)
from d_quotient_classical.causal_transfer.verify_berger_26_row_smooth_bikernel_homotopy_support_gate import (
    verify,
)


class BergerSmoothBikernelHomotopySupportGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = subject.build()

    def test_one_sided_classes_and_full_smooth_boundary(self) -> None:
        rows = {
            row["class_id"]: row for row in self.value["support_classes"]
        }
        self.assertTrue(rows["K_PC_X"]["continuous_extension"])
        self.assertTrue(rows["K_FC_X"]["continuous_extension"])
        self.assertTrue(rows["K_TC_X"]["continuous_extension"])
        self.assertFalse(
            rows["K_SC_X_EQUALS_ALL_SMOOTH"]["continuous_extension"]
        )

    def test_cutoff_escape_fixture(self) -> None:
        fixture = self.value["negative_fixture"]
        self.assertIn(
            "f_n tends to 0",
            fixture["retarded_sequence"]["source_limit"],
        )
        self.assertIn(
            "tends to h",
            fixture["retarded_sequence"]["image_limit"],
        )
        self.assertIn(
            "no continuous extension",
            fixture["advanced_sequence"]["conclusion"],
        )

    def test_C26_membership_fails_closed(self) -> None:
        boundary = self.value["C26_import_boundary"]
        self.assertEqual(
            boundary["typed_need"],
            "C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER",
        )
        self.assertFalse(
            self.value["classification"][
                "C26_in_positive_extension_domain_certified"
            ]
        )

    def test_mutations_rejected(self) -> None:
        for key in (
            "full_smooth_factorized_extension_certified",
            "C26_in_positive_extension_domain_certified",
            "smooth_Ward_correction_constructed",
            "retained_BRST_Hadamard_promoted",
            "positivity_or_quantum_claim",
        ):
            mutant = deepcopy(self.value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError, msg=key):
                subject.validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
