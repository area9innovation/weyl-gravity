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
from spectral.euclidean.multiplicity_export_receiver import (
    ROOT as REPOSITORY_ROOT,
    synthetic_multiplicity_payload,
    validate_repository_multiplicity_export,
)


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
        fixture = synthetic_multiplicity_payload()
        Draft202012Validator(schema).validate(fixture)
        mutant = deepcopy(fixture)
        mutant["cancellations"]["scalar_ghost_reduction_status"] = "NOT_COMPUTED"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_semantic_receiver_accepts_complete_fixture(self) -> None:
        receipt = validate_repository_multiplicity_export(
            synthetic_multiplicity_payload(),
            repository_root=REPOSITORY_ROOT,
            expected_classical_commit="0" * 40,
            expected_analytic_route="EUCLIDEAN_ELLIPTIC",
        )
        self.assertEqual(receipt["target_bundle_ranks"], [5, 1, 5, 3])
        self.assertEqual(receipt["target_signed_rank"], 6)
        self.assertEqual(
            (receipt["scalar_ghost_input_rank"], receipt["scalar_ghost_output_rank"]),
            (2, 1),
        )

    def test_semantic_receiver_rejects_orphan_factor_and_row(self) -> None:
        orphan_factor = synthetic_multiplicity_payload()
        extra_factor = deepcopy(orphan_factor["repository_factors"][0])
        extra_factor["factor_id"] = "orphan_factor"
        orphan_factor["repository_factors"].append(extra_factor)
        with self.assertRaisesRegex(ValueError, "factor coverage is incomplete"):
            validate_repository_multiplicity_export(
                orphan_factor,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

        orphan_row = synthetic_multiplicity_payload()
        extra_row = deepcopy(orphan_row["integration_slice"]["rows"][0])
        extra_row["generator_id"] = "orphan_row"
        orphan_row["integration_slice"]["rows"].append(extra_row)
        with self.assertRaisesRegex(ValueError, "row coverage is incomplete"):
            validate_repository_multiplicity_export(
                orphan_row,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

    def test_semantic_receiver_rejects_duplicate_map_and_scalar_drift(self) -> None:
        duplicate = synthetic_multiplicity_payload()
        duplicate["standard_factor_map"][1]["repository_factor_ids"] = [
            "repo_physical_0"
        ]
        with self.assertRaisesRegex(ValueError, "more than one standard factor"):
            validate_repository_multiplicity_export(
                duplicate,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

        scalar_drift = synthetic_multiplicity_payload()
        scalar_drift["cancellations"]["scalar_ghost_output_repository_factor_id"] = (
            "repo_physical_0"
        )
        with self.assertRaisesRegex(ValueError, "rank-two to rank-one"):
            validate_repository_multiplicity_export(
                scalar_drift,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

    def test_semantic_receiver_rejects_bad_hash_route_and_target_rank(self) -> None:
        bad_hash = synthetic_multiplicity_payload()
        bad_hash["proof_artifacts"][0] = deepcopy(bad_hash["proof_artifacts"][0])
        bad_hash["proof_artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
            validate_repository_multiplicity_export(
                bad_hash,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

        with self.assertRaisesRegex(ValueError, "analytic route drifted"):
            validate_repository_multiplicity_export(
                synthetic_multiplicity_payload(),
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="LORENTZIAN_CAUSAL",
            )

        wrong_rank = synthetic_multiplicity_payload()
        wrong_rank["standard_factor_map"][0]["target_bundle_rank"] = 4
        with self.assertRaises(ValidationError):
            validate_repository_multiplicity_export(
                wrong_rank,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

        wrong_factor_rank = synthetic_multiplicity_payload()
        wrong_factor_rank["repository_factors"][0]["component_rank"] = 4
        with self.assertRaisesRegex(ValueError, "rank/statistics"):
            validate_repository_multiplicity_export(
                wrong_factor_rank,
                repository_root=REPOSITORY_ROOT,
                expected_classical_commit="0" * 40,
                expected_analytic_route="EUCLIDEAN_ELLIPTIC",
            )

    def test_certificate_reproduces_validates_and_verifies(self) -> None:
        checked = json.loads(OUTPUT.read_text())
        self.assertEqual(checked, build())
        self.assertEqual(checked, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(checked)


if __name__ == "__main__":
    unittest.main()
