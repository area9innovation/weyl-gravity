from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from local_bv.schema_validation import validate_instance
from lorentzian.berger_retained_stationary_generator_acceptance import (
    INPUT_SCHEMA,
    MATRIX_SCHEMA,
    _canonical_hash,
    _expected_row_ids,
    _load_matrix_record,
)
from lorentzian.berger_retained_stationary_generator_readiness import READINESS_SCHEMA, build
from lorentzian.berger_retained_stationary_generator_readiness_certificate import OUTPUT
from lorentzian.verify_berger_retained_stationary_generator_readiness import verify


class BergerRetainedStationaryGeneratorReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build()

    def test_exact_consumer_and_mutation_witness(self) -> None:
        receipt = self.certificate["synthetic_consumer_receipt"]
        self.assertTrue(all(receipt["accepted_exact_checks"].values()))
        self.assertTrue(receipt["nonnilpotent_q_mutation_rejected"])

    def test_four_content_addressed_carriers_are_required(self) -> None:
        contract = self.certificate["input_contract"]
        self.assertEqual(
            contract["required_artifact_ids"],
            ["A104", "q_Cauchy_104", "G_Cauchy_104", "real_structure_104"],
        )
        self.assertEqual(contract["required_shape"], [104, 104])
        self.assertIn("blob_sha256", contract["content_addressing"])

    def test_serialized_104_row_PBW_record_is_hash_and_ordering_guarded(self) -> None:
        row_ids = _expected_row_ids()
        body = {
            "artifact_id": "A104",
            "shape": [104, 104],
            "row_ids": row_ids,
            "column_ids": row_ids,
            "entries": [],
        }
        payload = {
            "schema": "quantum-weyl-berger-retained-stationary-carrier-matrix-v1",
            **body,
            "sha256": _canonical_hash(body),
            "source_commit": "0" * 40,
        }
        Draft202012Validator(json.loads(MATRIX_SCHEMA.read_text())).validate(payload)
        self.assertEqual(len(_load_matrix_record(payload, "A104", row_ids)), 104)
        mutant = deepcopy(payload)
        mutant["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "internal hash"):
            _load_matrix_record(mutant, "A104", row_ids)

    def test_algebraic_import_does_not_claim_spectral_isolation(self) -> None:
        separation = self.certificate["analytic_separation"]
        self.assertFalse(separation["finite_PBW_import_can_decide_zero_is_isolated"])
        self.assertFalse(self.certificate["claim_flags"]["ZERO_FREQUENCY_LEDGER_COMPUTED"])
        self.assertFalse(self.certificate["claim_flags"]["GLOBAL_BRST_HADAMARD_STATE"])

    def test_input_schema_is_fail_closed(self) -> None:
        schema = json.loads(INPUT_SCHEMA.read_text())
        candidate = {
            "schema": "quantum-weyl-berger-retained-stationary-generator-input-v1",
            "result_id": "BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
            "classical_commit": "0" * 40,
            "artifacts": {
                name: {"path": f"d_quotient_classical/certificates/{name}.json", "sha256": "0" * 64}
                for name in ("A104", "q_Cauchy_104", "G_Cauchy_104", "real_structure_104")
            },
            "declared_scope": {
                "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
                "coefficient_ring": "Q[alpha_B,u,v]",
                "PBW_axis_order": ["t", "berger_frame_1", "berger_frame_2", "berger_frame_3"],
                "Cauchy_rank": 104,
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
                "analytic_zero_spectrum_claim": "NOT_PART_OF_ALGEBRAIC_IMPORT",
            },
            "claim_boundary": "A committed exact stationary carrier only; no spectral, Hadamard, positivity, renormalized-product, QME, particle or quantum statement follows from this manifest without independent consumer replay and analytic completion.",
        }
        Draft202012Validator(schema).validate(candidate)
        mutant = deepcopy(candidate)
        mutant["declared_scope"]["analytic_zero_spectrum_claim"] = "ISOLATED"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_persisted_output_and_strict_schemas(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        self.assertFalse(
            validate_instance(self.certificate, json.loads(READINESS_SCHEMA.read_text()))
        )
        for path in (INPUT_SCHEMA, MATRIX_SCHEMA, READINESS_SCHEMA):
            Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
