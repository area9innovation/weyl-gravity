from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.retained_biwave_volterra_import_readiness import (
    validate_readiness,
)
from lorentzian.retained_biwave_volterra_import_readiness_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class RetainedBiwaveVolterraImportReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                ROOT
                / "schema/berger-retained-biwave-volterra-import-readiness-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_D_and_adjoint_checks_hold(self) -> None:
        checks = self.certificate["exact_compatibility"]["checks"]
        self.assertGreaterEqual(len(checks), 15)
        self.assertTrue(all(checks.values()))
        self.assertTrue(
            self.certificate["claim_flags"][
                "BERGER_RETAINED_BIWAVE_D_EQUIVARIANT"
            ]
        )

    def test_committed_source_is_pinned_and_rejected_fail_closed(self) -> None:
        receipt = self.certificate["source_audit"]
        self.assertEqual(receipt["status"], "REJECTED_FAIL_CLOSED")
        self.assertEqual(
            receipt["source_commit"],
            "512545b781d4b0aff474bc5dc224890b246b070c",
        )
        self.assertTrue(all(receipt["structural_checks"].values()))
        self.assertEqual(len(receipt["defects"]), 8)
        self.assertFalse(
            self.certificate["claim_flags"][
                "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"
            ]
        )

    def test_all_known_analytic_contract_defects_are_named(self) -> None:
        defect_ids = {
            item["defect_id"] for item in self.certificate["source_audit"]["defects"]
        }
        self.assertEqual(
            defect_ids,
            {
                "UNDECLARED_DEPENDENCY_TAG",
                "MISSING_STRICT_SOURCE_SCHEMA",
                "CONFLATED_SOURCE_AND_SOLUTION_RESOLVENTS",
                "MALFORMED_FORMAL_ADJOINT_IDENTITY",
                "UNREFERENCED_ANALYTIC_BOOLEAN_ASSERTIONS",
                "MISSING_SOURCE_PROVENANCE_AND_VERIFICATION_RECEIPT",
                "SOURCE_SIDE_FACTORIAL_BOUND_NOT_STATED",
                "GRADED_ENERGY_MAPPING_UNDERSPECIFIED",
            },
        )

    def test_source_audit_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["source_audit"]["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source audit"):
            validate_readiness(mutant)

    def test_green_or_quantum_promotion_is_rejected(self) -> None:
        for flag in (
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.certificate)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "lifecycle"):
                validate_readiness(mutant)

    def test_stale_raw_route_cannot_be_removed_from_rejection_ledger(self) -> None:
        mutant = deepcopy(self.certificate)
        del mutant["realization_policy"]["rejected_routes"][
            "FULL_G13_ARBITRARY_SOURCE_METRIC_CONE"
        ]
        with self.assertRaisesRegex(ValueError, "stale raw"):
            validate_readiness(mutant)


if __name__ == "__main__":
    unittest.main()
