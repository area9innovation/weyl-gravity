from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_residual_ell3_branch_projection_readiness_v2 import (
    INPUT_SCHEMA,
    OUTPUT,
    SCHEMA,
    build,
)
from transfer.verify_berger_residual_ell3_branch_projection_readiness_v2 import verify


class BergerResidualEll3BranchProjectionReadinessV2Tests(unittest.TestCase):
    def test_split_field_contract(self) -> None:
        value = json.loads(OUTPUT.read_text())
        contract = value["input_contract"]
        self.assertEqual(contract["operator_coefficient_field"], "Q(sqrt(10))")
        self.assertEqual(
            contract["deformation_coefficient_field"], "Q(sqrt(2),sqrt(10))"
        )
        self.assertFalse(value["claim_flags"]["RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE"])
        self.assertFalse(value["field_repair_receipt"]["old_schema_rewritten"])

    def test_input_schema_rejects_wrong_deformation_field(self) -> None:
        schema = json.loads(INPUT_SCHEMA.read_text())
        artifact = {
            "artifact_id": "x",
            "path": "x.json",
            "sha256": "0" * 64,
            "canonical_sha256": "1" * 64,
            "coefficient_field": "Q(sqrt(10))",
        }
        instance = {
            "schema": "quantum-weyl-berger-residual-ell3-branch-basis-input-v2",
            "result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2",
            "classical_commit": "0" * 40,
            "setting_id": "compact_positive_berger_clock_fixed_coupling",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "accepted_ell3": {
                "result_id": "BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE",
                "sha256": "2" * 64,
            },
            "declared_scope": {
                "ambient_retained_rank": 36,
                "operator_coefficient_field": "Q(sqrt(10))",
                "deformation_coefficient_field": "Q(sqrt(2),sqrt(10))",
                "deformation_basis_normalization": "e=(W_plus_squared+W_minus_squared)/sqrt(2); o=(W_plus_squared-W_minus_squared)/sqrt(2); Gram=I2",
                "factorial_convention": "suspended-graded-symmetric-factorial-v1",
                "dynamical_gravity_branch_ids": ["Einstein_like", "extra_Weyl"],
                "deformation_vertex_basis_ids": ["e_C2_dynamical", "o_C_dual_C_topological"],
                "Maxwell_branch_ids": ["Maxwell_physical"],
                "branch_list_exhaustive_for_declared_sector": True,
                "kinetic_health_claim": "NOT_PART_OF_ELL3_BRANCH_PROJECTION",
            },
            "artifacts": {name: dict(artifact) for name in (
                "retained_q1", "dynamical_branch_ledger", "dynamical_branch_inclusion",
                "dynamical_branch_projection", "dynamical_branch_pairing_gram",
                "parity_operator", "real_structure", "K_Berger_weight_operator",
                "deformation_vertex_basis", "deformation_Euler_Lagrange_map",
                "topological_transgression_witness",
            )},
            "claim_boundary": "x" * 300,
        }
        validator = Draft202012Validator(schema)
        self.assertTrue(list(validator.iter_errors(instance)))
        for name in (
            "deformation_vertex_basis",
            "deformation_Euler_Lagrange_map",
            "topological_transgression_witness",
        ):
            instance["artifacts"][name]["coefficient_field"] = "Q(sqrt(2),sqrt(10))"
        self.assertFalse(list(validator.iter_errors(instance)))

    def test_persisted_certificate_reproduces_and_overclaims_fail(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build())
        self.assertEqual(value, verify())
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        for flag in (
            "RESIDUAL_BRANCH_BASIS_INPUT_AVAILABLE",
            "DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE",
            "RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED",
            "RESIDUAL_ELL3_MIXING_TABLE_COMPUTED",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            self.assertTrue(list(validator.iter_errors(mutant)), flag)


if __name__ == "__main__":
    unittest.main()
