from __future__ import annotations

import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_companion_hadamard_existence_audit import validate
from lorentzian.berger_companion_hadamard_existence_audit_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_companion_hadamard_existence_audit import verify


class BergerCompanionHadamardExistenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-companion-hadamard-existence-audit-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))
        validate(self.certificate)

    def test_decomposability_is_not_promoted_to_existence(self) -> None:
        criterion = self.certificate["literature_criterion"]
        self.assertFalse(criterion["general_existence_from_decomposability_alone"])
        self.assertFalse(criterion["theorem_5_3_applies_to_companion"])
        self.assertTrue(
            self.certificate["claim_flags"][
                "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
            ]
        )
        self.assertFalse(
            self.certificate["claim_flags"][
                "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
            ]
        )

    def test_stationary_receiving_contract_is_exact_next_gate(self) -> None:
        self.assertEqual(
            self.certificate["next_gate"],
            "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
        )
        self.assertTrue(
            all(value == "REQUIRED" for value in self.certificate["minimal_missing_carrier"].values())
        )

    def test_independent_verifier_and_mutations(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
