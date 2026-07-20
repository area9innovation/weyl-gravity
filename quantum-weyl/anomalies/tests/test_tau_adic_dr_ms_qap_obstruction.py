from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.tau_adic_dr_ms_qap_obstruction import validate
from anomalies.tau_adic_dr_ms_qap_obstruction_certificate import (
    OUTPUT,
    certificate,
)
from anomalies.verify_tau_adic_dr_ms_qap_obstruction import (
    verify,
    verify_payload,
)


class TauAdicDrMsQapObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION",
        )

    def test_zero_euler_residue_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["first_incompatibility"]["nonzero_Euler_residue"] = {
            "numerator": 0,
            "denominator": 1,
        }
        mutant["first_incompatibility"]["finite_evanescent_coefficient"] = {
            "numerator": 0,
            "denominator": 1,
        }
        with self.assertRaisesRegex(ValueError, "schema|replay|boundary"):
            verify_payload(mutant)

    def test_all_regulators_no_go_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["ALL_REGULATORS_OBSTRUCTED"] = True
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)

    def test_unconditional_qme_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["UNCONDITIONAL_ALL_LOOP_QME"] = True
        with self.assertRaisesRegex(ValueError, "boundary"):
            validate(mutant)

    def test_missing_antifield_inventory_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["declared_architecture"]["variables"] = ""
        with self.assertRaisesRegex(ValueError, "schema|incomplete"):
            verify_payload(mutant)

    def test_missing_measure_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["declared_architecture"]["measure"] = ""
        with self.assertRaisesRegex(ValueError, "schema|incomplete"):
            verify_payload(mutant)

    def test_second_failed_qap_gate_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["qap_hypothesis_ledger"][0]["status"] = (
            "FAILED_EVANESCENT_EXTENSION_REQUIRED"
        )
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
