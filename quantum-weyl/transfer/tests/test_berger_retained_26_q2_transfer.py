from __future__ import annotations

import json
import unittest

from local_bv.schema_validation import validate_instance
from transfer import berger_retained_26_q2_transfer as TRANSFER
from transfer import berger_retained_26_q2_transfer_certificate as CERTIFICATE


class BergerRetained26Q2TransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = CERTIFICATE.validate_checked_receipt()
        cls.payload = json.loads(CERTIFICATE.PAYLOAD.read_text())

    def test_checked_receipts_and_strict_schemas(self) -> None:
        for path, value in (
            (
                CERTIFICATE.ROOT / "schema/berger-retained-26-q2-transfer-v1.schema.json",
                self.certificate,
            ),
            (
                CERTIFICATE.ROOT / "schema/berger-retained-26-q2-payload-v1.schema.json",
                self.payload,
            ),
        ):
            schema = json.loads(path.read_text())
            self.assertFalse(validate_instance(value, schema))

    def test_exact_transfer_counts_and_identities(self) -> None:
        operation = self.certificate["transfer"]["operation"]
        self.assertEqual(operation["name"], "q2_26")
        self.assertEqual(operation["nonzero_coefficient_count"], 54236)
        self.assertEqual(operation["nonzero_output_rows"], 26)
        self.assertEqual(operation["maximum_total_jet_order"], 4)
        self.assertTrue(all(self.certificate["transfer"]["exact_checks"].values()))

    def test_retained_is_not_promoted_to_minimal_residual(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["CLASSICAL_RETAINED_26_Q2_TRANSFERRED"])
        self.assertFalse(flags["MINIMAL_RESIDUAL_ELL2_COMPUTED"])
        self.assertFalse(flags["BARE_D_CARTAN_RESTORED"])
        self.assertFalse(flags["QUANTUM_CLAIM"])

    def test_small_output_mutation_breaks_nilpotency_and_cyclicity(self) -> None:
        q1 = {(2, 1, ()): TRANSFER.q10.ONE}
        degrees = (0, 1, 2)
        fixture = {(1, 0, 0, (), ()): TRANSFER.q10.ONE}
        self.assertTrue(TRANSFER.q10.arity_two_defect(q1, fixture, degrees))
        pairing = {
            (0, 1): TRANSFER.q10.ONE,
            (1, 0): TRANSFER.q10.qneg(TRANSFER.q10.ONE),
        }
        cyclic_mutation = {(1, 0, 1, (), ()): TRANSFER.q10.ONE}
        self.assertTrue(
            TRANSFER._cyclicity_defect(cyclic_mutation, pairing, (0, 1))
        )


if __name__ == "__main__":
    unittest.main()
