from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.full_bv_ledger_composer import (
    ROOT,
    compose_from_path,
    compose_repository_multiplicity_export,
    mutation_receipts,
    validate_composed_repository_multiplicity_export,
)
from spectral.euclidean.full_bv_ledger_composer_readiness import (
    FIXTURE,
    OUTPUT,
    SCHEMA,
    _artifact,
    build,
)
from spectral.euclidean.verify_full_bv_ledger_composer_readiness import verify


class FullBVLedgerComposerTests(unittest.TestCase):
    def _fixture(self):
        payload = json.loads(FIXTURE.read_text())
        return payload, _artifact(FIXTURE), payload["classical_commit"]

    def test_composer_binds_exact_factor_exponents_and_zero_modes(self) -> None:
        tt, artifact, commit = self._fixture()
        ledger = compose_repository_multiplicity_export(
            tt,
            tt_dictionary_artifact=artifact,
            expected_classical_commit=commit,
        )
        factors = ledger["repository_factors"]
        self.assertEqual(
            [row["operator"] for row in factors],
            ["Delta_2_perp(4)", "Delta_0(-4)", "Delta_2_perp(2)", "Delta_1_perp(-3)"],
        )
        self.assertEqual(
            [row["determinant_exponent"] for row in factors],
            [
                {"numerator": -1, "denominator": 2},
                {"numerator": 1, "denominator": 2},
                {"numerator": -1, "denominator": 2},
                {"numerator": 1, "denominator": 2},
            ],
        )
        rows = {row["generator_id"]: row for row in ledger["integration_slice"]["rows"]}
        self.assertIn("delete_10_killing_vectors", rows["xi_T"]["zero_mode_policy_id"])
        self.assertIn("delete_5_conformal_modes", rows["omega"]["zero_mode_policy_id"])

    def test_file_entrypoint_content_addresses_the_input(self) -> None:
        ledger = compose_from_path(FIXTURE)
        self.assertEqual(ledger["result_id"], "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER")
        self.assertEqual(
            ledger["proof_artifacts"][0]["path"], str(FIXTURE.relative_to(ROOT))
        )

    def test_composed_ledger_replays_and_mutations_fail(self) -> None:
        tt, artifact, commit = self._fixture()
        ledger = compose_repository_multiplicity_export(
            tt,
            tt_dictionary_artifact=artifact,
            expected_classical_commit=commit,
        )
        receipt = validate_composed_repository_multiplicity_export(
            ledger,
            tt_payload=tt,
            tt_dictionary_artifact=artifact,
            expected_classical_commit=commit,
        )
        self.assertEqual(receipt["status"], "COMPOSED_LEDGER_SEMANTICALLY_ACCEPTED")
        self.assertTrue(
            all(
                row["rejected"]
                for row in mutation_receipts(
                    ledger,
                    tt_payload=tt,
                    tt_dictionary_artifact=artifact,
                    expected_classical_commit=commit,
                )
            )
        )

    def test_tt_payload_must_equal_its_content_addressed_artifact(self) -> None:
        tt, artifact, commit = self._fixture()
        mutant = deepcopy(tt)
        mutant["background"]["scalar_curvature"] = 13
        with self.assertRaises((ValueError, ValidationError)):
            compose_repository_multiplicity_export(
                mutant,
                tt_dictionary_artifact=artifact,
                expected_classical_commit=commit,
            )

    def test_readiness_claim_boundary_and_independent_verifier(self) -> None:
        value = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), value)
        self.assertEqual(verify(), value)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        mutant = deepcopy(value)
        mutant["claim_flags"]["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
