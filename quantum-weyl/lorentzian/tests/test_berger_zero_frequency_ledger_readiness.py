from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from lorentzian.berger_zero_frequency_ledger_readiness import build, validate
from lorentzian.berger_zero_frequency_ledger_readiness_certificate import HERE, OUTPUT, build_certificate
from lorentzian.verify_berger_zero_frequency_ledger_readiness import verify


class BergerZeroFrequencyLedgerReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_exact_known_unknown_partition(self) -> None:
        audit = self.payload["known_entry_audit"]
        self.assertEqual(audit["known_coordinates"] + audit["unknown_coordinates"], 104**2)
        self.assertEqual(audit["unknown_coordinates"], 2 * 12**2)

    def test_nonidentifiability_witness_changes_nullity_by_24(self) -> None:
        witness = self.payload["nonidentifiability_witness"]
        self.assertTrue(witness["agreement_on_all_exported_coordinates"])
        self.assertEqual(witness["zero_eigenspace_dimension_difference"], 24)

    def test_receiving_contract_has_all_four_carriers(self) -> None:
        artifacts = self.payload["minimal_stationary_carrier_contract"]["required_artifacts"]
        self.assertEqual(
            [row["artifact_id"] for row in artifacts],
            ["A104", "q_Cauchy_104", "G_Cauchy_104", "real_structure_104"],
        )

    def test_certificate_reproduces_and_validates(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (HERE / "schema/berger-zero-frequency-ledger-readiness-v1.schema.json").read_text()
        )
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)

    def test_overclaim_is_rejected(self) -> None:
        mutant = deepcopy(self.payload)
        mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build_certificate())


if __name__ == "__main__":
    unittest.main()
