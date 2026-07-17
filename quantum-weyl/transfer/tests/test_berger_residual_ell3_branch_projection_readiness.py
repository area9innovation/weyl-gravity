from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from local_bv.schema_validation import validate_instance
from transfer.berger_residual_ell3_branch_projection_readiness import (
    INPUT_SCHEMA,
    READINESS_SCHEMA,
    build,
)
from transfer.berger_residual_ell3_branch_projection_readiness_certificate import OUTPUT
from transfer.verify_berger_residual_ell3_branch_projection_readiness import verify


class BergerResidualEll3BranchProjectionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_mixed_contract_requires_gravity_and_Maxwell_carriers(self) -> None:
        contract = self.value["input_contract"]
        self.assertEqual(
            contract["required_dynamical_gravity_branch_ids"],
            ["Einstein_like", "extra_Weyl"],
        )
        self.assertEqual(
            contract["required_deformation_vertex_basis_ids"],
            ["e_C2_dynamical", "o_C_dual_C_topological"],
        )
        self.assertTrue(contract["Maxwell_branch_carrier_required"])
        self.assertIn("dynamical_branch_pairing_gram", contract["required_artifact_ids"])
        self.assertIn("topological_transgression_witness", contract["required_artifact_ids"])

    def test_synthetic_exact_contraction_and_mutation(self) -> None:
        receipt = self.value["synthetic_consumer_receipt"]
        self.assertTrue(all(receipt["exact_checks"].values()))
        self.assertTrue(receipt["projection_normalization_mutation_rejected"])

    def test_input_schema_rejects_gravity_only_manifest(self) -> None:
        schema = json.loads(INPUT_SCHEMA.read_text())
        artifacts = {
            name: {
                "artifact_id": name,
                "path": f"d_quotient_classical/certificates/{name}.json",
                "sha256": "0" * 64,
                "canonical_sha256": "1" * 64,
            }
            for name in self.value["input_contract"]["required_artifact_ids"]
        }
        candidate = {
            "schema": "quantum-weyl-berger-residual-ell3-branch-basis-input-v1",
            "result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1",
            "classical_commit": "0" * 40,
            "setting_id": "compact_positive_berger_clock_fixed_coupling",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "accepted_ell3": {
                "result_id": "BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE",
                "sha256": "2" * 64,
            },
            "declared_scope": {
                "ambient_retained_rank": 36,
                "coefficient_field": "Q(sqrt(10))",
                "factorial_convention": "suspended-graded-symmetric-factorial-v1",
                "dynamical_gravity_branch_ids": ["Einstein_like", "extra_Weyl"],
                "deformation_vertex_basis_ids": [
                    "e_C2_dynamical",
                    "o_C_dual_C_topological",
                ],
                "Maxwell_branch_ids": ["Maxwell_physical"],
                "branch_list_exhaustive_for_declared_sector": True,
                "kinetic_health_claim": "NOT_PART_OF_ELL3_BRANCH_PROJECTION",
            },
            "artifacts": artifacts,
            "claim_boundary": "An exact classical residual branch carrier with gravity and Maxwell sectors. It supplies only the basis and contraction data required to compute a branch-space ell3. Every branch is normalized and content-addressed, and the declared list is exhaustive only for the stated projection sector. It does not claim kinetic positivity, QME restoration, a Hadamard state, residual quantum transfer, particles or a quantum theorem.",
        }
        Draft202012Validator(schema).validate(candidate)
        mutant = deepcopy(candidate)
        mutant["declared_scope"]["Maxwell_branch_ids"] = []
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_readiness_remains_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["RESIDUAL_ELL3_BRANCH_PROJECTION_CONSUMER_READY"])
        self.assertFalse(flags["RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE"])
        self.assertFalse(flags["RESIDUAL_ELL3_MIXING_TABLE_COMPUTED"])
        self.assertFalse(flags["DEFORMATION_VERTEX_PROJECTION_COMPUTED"])
        self.assertFalse(flags["RESIDUAL_QUANTUM_TRANSFERRED"])
        self.assertFalse(flags["QUANTUM_CLAIM"])

    def test_persisted_output_and_strict_schemas(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.value)
        self.assertFalse(
            validate_instance(self.value, json.loads(READINESS_SCHEMA.read_text()))
        )
        for path in (INPUT_SCHEMA, READINESS_SCHEMA):
            Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
