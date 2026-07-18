from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.full_bv_multiplicity_preflight import (
    EXPORT_SCHEMA,
    OUTPUT,
    SCHEMA,
    build,
    transverse_traceless_rank_4d,
)
from spectral.euclidean.verify_full_bv_multiplicity_preflight import verify


class FullBVMultiplicityPreflightTests(unittest.TestCase):
    def test_standard_factor_ranks_and_signed_rank(self) -> None:
        value = build()
        rows = value["standard_factor_multiplicities"]["rows"]
        self.assertEqual([row["bundle_rank"] for row in rows], [5, 1, 5, 3])
        self.assertEqual(
            sum(row["determinant_sign"] * row["bundle_rank"] for row in rows),
            6,
        )
        self.assertEqual([transverse_traceless_rank_4d(i) for i in range(3)], [1, 3, 5])

    def test_scalar_gap_is_exactly_rank_one(self) -> None:
        value = build()
        ranks = value["exact_rank_decomposition"]
        self.assertEqual(ranks["scalar_ghost_candidate_rank"], 2)
        self.assertEqual(ranks["standard_scalar_ghost_factor_rank"], 1)
        self.assertEqual(ranks["unresolved_scalar_cancellation_rank"], 1)
        self.assertFalse(
            value["claim_flags"]["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"]
        )

    def test_classical_component_rows_are_rejected_as_loop_multiplicities(self) -> None:
        audit = build()["forbidden_shortcut_audit"]
        self.assertEqual((audit["Berger_total_component_rows"], audit["Berger_minimal_component_rows"], audit["Berger_nonminimal_component_rows"]), (54, 34, 20))
        self.assertFalse(audit["component_rows_equal_determinant_multiplicities"])

    def test_export_schema_fails_closed_on_unverified_scalar_reduction(self) -> None:
        schema = json.loads(EXPORT_SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        fixture = {
            "schema": "quantum-weyl-repository-full-bv-multiplicity-export-v1",
            "result_id": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            "classical_commit": "0" * 40,
            "analytic_route": "EUCLIDEAN_ELLIPTIC",
            "integration_slice": {
                "status": "VERIFIED",
                "gauge": "fixture",
                "rows": [
                    {
                        "generator_id": "g",
                        "role": "field",
                        "statistics": "BOSONIC",
                        "component_rank": 10,
                        "operator_id": "K_g",
                        "determinant_exponent": {"numerator": -1, "denominator": 2},
                        "zero_mode_policy_id": "fixture",
                    }
                ],
                "antifields_integrated_independently": False,
                "all_rows_accounted": True,
                "proof_artifact": {"format": "TEXT_PROOF", "path": "proof.txt", "sha256": "0" * 64},
            },
            "repository_factors": [
                {
                    "factor_id": factor_id,
                    "bundle": "fixture",
                    "statistics": "BOSONIC" if factor_id.startswith("physical") else "FERMIONIC",
                    "component_rank": rank,
                    "operator": "fixture",
                    "determinant_exponent": {"numerator": 1, "denominator": 1},
                    "source_generator_ids": ["g"],
                    "derivation_artifact": {"format": "TEXT_PROOF", "path": "proof.txt", "sha256": "0" * 64},
                }
                for factor_id, rank in (("physical_depth_0", 5), ("ghost_depth_0", 1), ("physical_depth_1", 5), ("ghost_depth_1", 3))
            ],
            "standard_factor_map": [
                {
                    "target_factor_id": factor_id,
                    "repository_factor_ids": [factor_id],
                    "status": "VERIFIED",
                    "proof_artifact": {"format": "TEXT_PROOF", "path": "proof.txt", "sha256": "0" * 64},
                }
                for factor_id in ("physical_depth_0", "ghost_depth_0", "physical_depth_1", "ghost_depth_1")
            ],
            "cancellations": {
                "contractible_pairs_status": "VERIFIED",
                "scalar_ghost_reduction_status": "VERIFIED",
                "scalar_ghost_input_rank": 2,
                "scalar_ghost_output_rank": 1,
                "nonminimal_Berezinian_status": "VERIFIED",
                "proof_artifact": {"format": "TEXT_PROOF", "path": "proof.txt", "sha256": "0" * 64},
            },
            "proof_artifacts": [{"format": "TEXT_PROOF", "path": "proof.txt", "sha256": "0" * 64}],
            "claim_boundary": "Synthetic schema-only fixture; this is not a scientific multiplicity export.",
        }
        Draft202012Validator(schema).validate(fixture)
        mutant = deepcopy(fixture)
        mutant["cancellations"]["scalar_ghost_reduction_status"] = "NOT_COMPUTED"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_certificate_reproduces_validates_and_verifies(self) -> None:
        checked = json.loads(OUTPUT.read_text())
        self.assertEqual(checked, build())
        self.assertEqual(checked, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(checked)


if __name__ == "__main__":
    unittest.main()
