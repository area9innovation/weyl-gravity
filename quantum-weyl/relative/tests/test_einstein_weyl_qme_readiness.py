from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from relative.einstein_weyl_qme_readiness import validate
from relative.einstein_weyl_qme_readiness_certificate import HERE, OUTPUT, build_certificate
from relative.verify_einstein_weyl_qme_readiness import verify


class EinsteinWeylQMEReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads((HERE / "schema/einstein-weyl-qme-readiness-v1.schema.json").read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_shared_row_is_complete_and_fail_closed(self) -> None:
        row = self.certificate["shared_relative_row"]
        self.assertEqual(
            set(row),
            {"setting", "map_iota", "cofiber", "relative_pairing", "O2", "residual_action", "observable_map", "quantum_lift"},
        )
        self.assertEqual(row["map_iota"], "ONSHELL_MAP_ONLY_IMPORTED_BY_HASH")
        self.assertEqual(row["quantum_lift"], "ANALYTIC_FRAMEWORK_MISSING")

    def test_three_classical_spine_inputs_are_explicitly_missing(self) -> None:
        gate = self.certificate["classical_import_gate"]
        self.assertEqual(gate["status"], "NOT_SATISFIED")
        self.assertEqual(len(gate["required_result_ids"]), 3)
        self.assertIn("do not reconstruct", gate["forbidden_fallback"])

    def test_relative_anomaly_is_a_contract_not_a_claim(self) -> None:
        anomaly = self.certificate["relative_anomaly_contract"]
        self.assertEqual(anomaly["formal_expression"], "[A_rel]=[A_Weyl-iota_* A_Einstein]")
        self.assertEqual(anomaly["status"], "NOT_CONSTRUCTED")
        self.assertIn("antifield", anomaly["separate_ledgers"])
        self.assertIn("boundary_corner", anomaly["separate_ledgers"])

    def test_frameworks_and_qme_are_not_conflated(self) -> None:
        ledger = self.certificate["framework_ledger"]
        self.assertEqual(set(ledger), {"LOCAL_ALGEBRAIC", "EUCLIDEAN_SPECTRAL", "REDUCED_MODE", "LORENTZIAN_CAUSAL"})
        self.assertEqual(ledger["LORENTZIAN_CAUSAL"]["status"], "ANALYTIC_FRAMEWORK_MISSING")
        self.assertFalse(self.certificate["qme_and_transfer_gate"]["residual_quantum_transfer_authorized"])

    def test_overclaims_are_rejected(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["RELATIVE_ANOMALY_CLASS_DEFINED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["shared_relative_row"]["quantum_lift"] = "QME_RESTORED"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
