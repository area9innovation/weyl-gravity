from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from anomalies.regulated_slavnov_breaking_preflight import (
    OUTPUT,
    ROOT,
    SCHEMA,
    analysis,
    build,
    receiver_fixture_payload,
    validate_regulated_breaking_export,
)
from anomalies.verify_regulated_slavnov_breaking_preflight import verify


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
        with self.assertRaisesRegex(ValueError, "does not match frozen G2"):
            validate_regulated_breaking_export(payload, repository_root=ROOT)

    def test_actual_receiver_rejects_wrong_artifact_roles(self) -> None:
        payload = receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)), nontrivial=False
        )
        payload["classical_commit"] = json.loads(
            (
                ROOT
                / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
            ).read_text()
        )["classical_commit"]
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

    def test_output_reproduces_validates_and_verifies(self) -> None:
        checked = json.loads(OUTPUT.read_text())
        self.assertEqual(checked, build())
        self.assertEqual(checked, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(checked)


if __name__ == "__main__":
    unittest.main()
