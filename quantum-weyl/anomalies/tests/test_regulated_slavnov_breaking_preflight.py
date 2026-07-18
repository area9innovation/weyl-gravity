from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator, ValidationError

from classical_import.classical_snapshot_compatibility_receiver import (
    synthetic_payload as snapshot_compatibility_payload,
)
from anomalies.regulated_slavnov_breaking_preflight import (
    OUTPUT,
    PROOF_RESULT_IDS,
    ROOT,
    SCHEMA,
    EXPORT_SCHEMA,
    analysis,
    build,
    receiver_fixture_payload,
    validate_regulated_breaking_export,
)
from anomalies.verify_regulated_slavnov_breaking_preflight import verify
from spectral.euclidean.multiplicity_export_receiver import (
    synthetic_multiplicity_payload,
)


class RegulatedSlavnovBreakingPreflightTests(unittest.TestCase):
    def test_exact_quotient_map_kills_only_box_r(self) -> None:
        value = build()
        reduction = value["cohomology_reduction"]
        self.assertEqual(reduction["matrix_shape"], [3, 4])
        self.assertEqual(reduction["kernel"], ["ANOM_OMEGA_BOX_R"])
        self.assertEqual(
            [(row["row"], row["column"]) for row in reduction["matrix_entries"]],
            [(0, 0), (1, 1), (2, 2)],
        )

    def test_known_even_vector_is_exact_and_nonzero(self) -> None:
        result = analysis()
        self.assertEqual(
            result["standard_even_vector"],
            [
                {"numerator": 199, "denominator": 30},
                {"numerator": -87, "denominator": 20},
            ],
        )
        self.assertEqual(
            result["standard_quotient_vector"],
            [
                {"numerator": 199, "denominator": 30},
                {"numerator": -87, "denominator": 20},
                {"numerator": 0, "denominator": 1},
            ],
        )
        self.assertTrue(build()["complete_dual_witness_binding"]["known_even_vector_nonzero"])
        self.assertEqual(
            build()["standard_background_input"]["parity_odd_status"],
            "WARD_VERIFIED_ZERO_FOR_STANDARD_PARITY_EVEN_REGULATOR",
        )

    def test_conditional_theorem_remains_inactive(self) -> None:
        value = build()
        theorem = value["conditional_obstruction_theorem"]
        self.assertEqual(theorem["status"], "PROVED_CONDITIONAL_NOT_ACTIVATED")
        self.assertFalse(theorem["activated"])
        self.assertFalse(value["claim_flags"]["REGULATED_SLAVNOV_BREAKING_COMPUTED"])
        self.assertFalse(value["claim_flags"]["QME_OBSTRUCTED"])
        self.assertTrue(value["claim_flags"]["ANALYTIC_SLAVNOV_EXPORT_RECEIVER_READY"])
        self.assertTrue(value["claim_flags"]["FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND"])
        self.assertTrue(
            value["claim_flags"]["FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_BOUND"]
        )
        self.assertTrue(value["claim_flags"]["FULL_BV_LEDGER_COMPOSER_READY"])
        self.assertTrue(
            value["claim_flags"][
                "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED"
            ]
        )
        self.assertTrue(
            value["claim_flags"]["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"]
        )
        self.assertTrue(
            value["claim_flags"][
                "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED"
            ]
        )
        self.assertTrue(
            value["claim_flags"]["REGULATED_BV_INSERTION_V2_RECEIVER_READY"]
        )
        self.assertEqual(
            value["accepted_export_schema"],
            "quantum-weyl-regulated-slavnov-breaking-export-v2",
        )
        self.assertEqual(
            value["minimal_missing_carrier_theorem"]["scalar_ghost_gap_rank"], 0
        )
        self.assertEqual(
            value["minimal_missing_carrier_theorem"]["status"],
            "EXACT_REGULATED_BV_INSERTION_GAP",
        )
        physical = value["repository_physical_input"]
        self.assertEqual(
            physical["round_S4_Euler_coefficient"]["a"],
            {"numerator": 87, "denominator": 20},
        )
        self.assertEqual(
            physical["round_S4_C2_status"], "NOT_DETERMINED_ON_ROUND_S4"
        )
        self.assertEqual(
            physical["repository_BV_anomaly_vector_status"], "NOT_COMPUTED"
        )

    def test_receiver_mechanics_classifies_both_qme_branches(self) -> None:
        value = build()
        mechanics = value["receiver_mechanics"]
        self.assertEqual(
            mechanics["nontrivial_branch"]["qme_disposition"],
            "OBSTRUCTED_STRICT_FIELD_CONTENT",
        )
        self.assertEqual(
            mechanics["trivial_branch"]["qme_disposition"],
            "RESTORABLE_BY_LOCAL_COUNTERTERM",
        )
        self.assertEqual(
            value["accepted_proof_result_ids"]["measure_contour"],
            "REPOSITORY_MEASURE_CONTOUR_LEDGER",
        )

    def test_receiver_rejects_a_false_obstruction_disposition(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(1)), nontrivial=False
        )
        mutant = deepcopy(payload)
        mutant["classification"] = {
            "status": "NONTRIVIAL",
            "exact_counterterm": None,
        }
        mutant["qme_disposition"]["status"] = "OBSTRUCTED_STRICT_FIELD_CONTENT"
        with self.assertRaisesRegex(ValueError, "invalid QME disposition"):
            validate_regulated_breaking_export(
                mutant, repository_root=ROOT, allow_synthetic_fixture=True
            )

    def test_actual_receiver_rejects_null_classical_commit(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)), nontrivial=False
        )
        with self.assertRaisesRegex(ValueError, "local BV commit does not match frozen G2"):
            validate_regulated_breaking_export(payload, repository_root=ROOT)

    def test_actual_receiver_rejects_wrong_artifact_roles(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)), nontrivial=False
        )
        commit = json.loads(
            (
                ROOT
                / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
            ).read_text()
        )["classical_commit"]
        payload["classical_commit"] = commit
        payload["classical_snapshot_compatibility"].update(
            local_BV_commit=commit,
            analytic_operator_commit=commit,
        )
        with self.assertRaisesRegex(ValueError, "expected 'REPOSITORY_AUXILIARY"):
            validate_regulated_breaking_export(payload, repository_root=ROOT)

    def test_receiver_rejects_unverified_measure_status(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)), nontrivial=False
        )
        payload["operator_and_measure"]["measure_contour_status"] = "NOT_COMPUTED"
        with self.assertRaisesRegex(ValueError, "proof status is incomplete"):
            validate_regulated_breaking_export(
                payload, repository_root=ROOT, allow_synthetic_fixture=True
            )

    def test_v2_receiver_requires_complete_insertion_decomposition(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)), nontrivial=False
        )
        del payload["insertion_decomposition"]["antifield_completion_artifact"]
        with self.assertRaisesRegex(ValueError, "insertion-decomposition fields"):
            validate_regulated_breaking_export(
                payload, repository_root=ROOT, allow_synthetic_fixture=True
            )

    def test_fourth_order_route_does_not_invent_an_auxiliary_gate(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
            nontrivial=False,
            formulation="FOURTH_ORDER_METRIC",
        )
        accepted = validate_regulated_breaking_export(
            payload, repository_root=ROOT, allow_synthetic_fixture=True
        )
        self.assertEqual(accepted["classification"], "TRIVIAL_OR_ZERO")
        self.assertIsNone(
            payload["operator_and_measure"]["auxiliary_fourth_order_match_artifact"]
        )
        mutant = deepcopy(payload)
        mutant["operator_and_measure"]["auxiliary_fourth_order_match_status"] = (
            "VERIFIED"
        )
        export_schema = json.loads(EXPORT_SCHEMA.read_text())
        with self.assertRaises(ValidationError):
            Draft202012Validator(export_schema).validate(mutant)
        with self.assertRaisesRegex(ValueError, "auxiliary-only proof gate"):
            validate_regulated_breaking_export(
                mutant, repository_root=ROOT, allow_synthetic_fixture=True
            )

    def test_distinct_classical_commits_require_a_compatibility_artifact(self) -> None:
        g2 = json.loads(
            (
                ROOT
                / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
            ).read_text()
        )
        analytic_commit = "1" * 40
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
            nontrivial=False,
        )
        payload["classical_commit"] = analytic_commit
        payload["classical_snapshot_compatibility"].update(
            local_BV_commit=g2["classical_commit"],
            analytic_operator_commit=analytic_commit,
            status="CONTENT_HASH_COMPATIBLE",
        )
        with tempfile.TemporaryDirectory(
            dir=ROOT / "quantum-weyl/anomalies/tests"
        ) as temporary:
            path = Path(temporary) / "compatibility.json"
            path.write_text(
                json.dumps(
                    {"result_id": PROOF_RESULT_IDS["snapshot_compatibility"]}
                )
                + "\n"
            )
            payload["classical_snapshot_compatibility"]["proof_artifact"] = {
                "format": "JSON_PROOF",
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            with self.assertRaisesRegex(ValueError, "semantic replay failed"):
                validate_regulated_breaking_export(payload, repository_root=ROOT)

            frozen_import_path = (
                ROOT
                / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
            )
            frozen_import = json.loads(frozen_import_path.read_text())
            hashes = frozen_import["independent_replay"]["canonical_hashes"]
            analytic_proof = Path(temporary) / "analytic-export.json"
            analytic_proof.write_text(
                json.dumps(
                    {
                        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
                        "classical_commit": analytic_commit,
                        "canonical_hashes": hashes,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            compatibility = snapshot_compatibility_payload(
                local_commit=g2["classical_commit"],
                analytic_commit=analytic_commit,
                canonical_hashes=hashes,
            )
            compatibility["proof_artifacts"][1] = {
                "format": "JSON_PROOF",
                "path": str(analytic_proof.relative_to(ROOT)),
                "sha256": hashlib.sha256(analytic_proof.read_bytes()).hexdigest(),
            }
            path.write_text(json.dumps(compatibility, sort_keys=True) + "\n")
            payload["classical_snapshot_compatibility"]["proof_artifact"][
                "sha256"
            ] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "expected 'REPOSITORY_AUXILIARY"):
                validate_regulated_breaking_export(payload, repository_root=ROOT)

            analytic_mutant = json.loads(analytic_proof.read_text())
            analytic_mutant["canonical_hashes"]["differential_hash"] = "0" * 64
            analytic_proof.write_text(json.dumps(analytic_mutant, sort_keys=True) + "\n")
            compatibility["proof_artifacts"][1]["sha256"] = hashlib.sha256(
                analytic_proof.read_bytes()
            ).hexdigest()
            path.write_text(json.dumps(compatibility, sort_keys=True) + "\n")
            payload["classical_snapshot_compatibility"]["proof_artifact"][
                "sha256"
            ] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "semantic replay failed"):
                validate_regulated_breaking_export(payload, repository_root=ROOT)

            payload["classical_snapshot_compatibility"]["proof_artifact"][
                "sha256"
            ] = "0" * 64
            with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
                validate_regulated_breaking_export(payload, repository_root=ROOT)

    def test_actual_receiver_executes_semantic_multiplicity_validation(self) -> None:
        def write_json(directory: Path, name: str, value: dict) -> dict[str, str]:
            path = directory / name
            path.write_text(json.dumps(value, sort_keys=True) + "\n")
            return {
                "format": "JSON_PROOF",
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }

        g2 = json.loads(
            (
                ROOT
                / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
            ).read_text()
        )
        with tempfile.TemporaryDirectory(
            dir=ROOT / "quantum-weyl/anomalies/tests"
        ) as temporary:
            directory = Path(temporary)
            payload = receiver_fixture_payload(
                (Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
                nontrivial=False,
            )
            payload["classical_commit"] = g2["classical_commit"]
            payload["classical_snapshot_compatibility"].update(
                local_BV_commit=g2["classical_commit"],
                analytic_operator_commit=g2["classical_commit"],
            )
            payload["classification"]["exact_counterterm"] = None

            coefficient_hash = hashlib.sha256(
                json.dumps(
                    payload["coefficients"],
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()

            def bound_proof(result_id: str) -> dict:
                return {
                    "result_id": result_id,
                    "classical_commit": payload["classical_commit"],
                    "analytic_route": payload["analytic_route"],
                    "coefficient_basis": payload["coefficient_basis"],
                    "coefficients_sha256": coefficient_hash,
                }

            operator_roles = {
                "complete_complex_artifact": PROOF_RESULT_IDS[
                    "complete_complex_EUCLIDEAN_ELLIPTIC"
                ],
                "auxiliary_fourth_order_match_artifact": PROOF_RESULT_IDS[
                    "auxiliary_fourth_order_match"
                ],
                "zero_mode_ledger_artifact": PROOF_RESULT_IDS["zero_mode_ledger"],
                "measure_contour_artifact": PROOF_RESULT_IDS["measure_contour"],
            }
            for key, result_id in operator_roles.items():
                payload["operator_and_measure"][key] = write_json(
                    directory, f"{key}.json", {"result_id": result_id}
                )

            multiplicity = synthetic_multiplicity_payload()
            multiplicity["classical_commit"] = g2["classical_commit"]
            multiplicity_artifact = write_json(
                directory, "multiplicity.json", multiplicity
            )
            payload["operator_and_measure"]["multiplicity_artifact"] = (
                multiplicity_artifact
            )
            insertion_roles = {
                "regulated_slavnov_action_artifact": PROOF_RESULT_IDS[
                    "slavnov_action"
                ],
                "total_derivative_artifact": PROOF_RESULT_IDS[
                    "total_derivative"
                ],
                "gauge_parameter_dependence_artifact": PROOF_RESULT_IDS[
                    "gauge_dependence"
                ],
                "regularization_dependence_artifact": PROOF_RESULT_IDS[
                    "regularization_dependence"
                ],
                "antifield_completion_artifact": PROOF_RESULT_IDS[
                    "antifield_completion"
                ],
            }
            for key, result_id in insertion_roles.items():
                payload["insertion_decomposition"][key] = write_json(
                    directory, f"{key}.json", bound_proof(result_id)
                )
            payload["consistency"]["wess_zumino_proof"] = write_json(
                directory,
                "wess_zumino.json",
                bound_proof(PROOF_RESULT_IDS["wess_zumino"]),
            )
            payload["consistency"]["parity_proof"] = write_json(
                directory,
                "parity.json",
                bound_proof(PROOF_RESULT_IDS["parity_ward_zero"]),
            )
            payload["qme_disposition"]["proof_artifact"] = write_json(
                directory,
                "qme.json",
                bound_proof(PROOF_RESULT_IDS["qme_disposition"]),
            )

            accepted = validate_regulated_breaking_export(
                payload, repository_root=ROOT
            )
            self.assertEqual(accepted["classification"], "TRIVIAL_OR_ZERO")

            stale_wz = bound_proof(PROOF_RESULT_IDS["wess_zumino"])
            stale_wz["coefficients_sha256"] = "0" * 64
            payload["consistency"]["wess_zumino_proof"] = write_json(
                directory, "wess_zumino.json", stale_wz
            )
            with self.assertRaisesRegex(ValueError, "breaking binding drifted"):
                validate_regulated_breaking_export(payload, repository_root=ROOT)
            payload["consistency"]["wess_zumino_proof"] = write_json(
                directory,
                "wess_zumino.json",
                bound_proof(PROOF_RESULT_IDS["wess_zumino"]),
            )

            orphan = deepcopy(multiplicity["integration_slice"]["rows"][0])
            orphan["generator_id"] = "orphan_row"
            multiplicity["integration_slice"]["rows"].append(orphan)
            payload["operator_and_measure"]["multiplicity_artifact"] = write_json(
                directory, "multiplicity.json", multiplicity
            )
            with self.assertRaisesRegex(ValueError, "row coverage is incomplete"):
                validate_regulated_breaking_export(payload, repository_root=ROOT)

    def test_output_reproduces_validates_and_verifies(self) -> None:
        checked = json.loads(OUTPUT.read_text())
        self.assertEqual(checked, build())
        self.assertEqual(checked, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(checked)
        mutant = deepcopy(checked)
        mutant["repository_physical_input"]["round_S4_C2_status"] = "COMPUTED"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
