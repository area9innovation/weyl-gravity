from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.tau_adic_all_loop_qme_stability import build, validate
from anomalies.tau_adic_all_loop_qme_stability_certificate import (
    OUTPUT,
    certificate,
)
from anomalies.verify_tau_adic_all_loop_qme_stability import (
    verify,
    verify_payload,
)


class TauAdicAllLoopQMEStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, certificate())

    def test_independent_cohomology_and_induction_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY",
        )

    def test_rhat_squared_omission_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["stable_H04_module"]["even_free_generators"].remove(
            "R(g_hat)^2"
        )
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)

    def test_positive_antifield_sector_omission_rejected(self) -> None:
        mutant = deepcopy(self.value)
        del mutant["stable_H14_module"][
            "positive_antifield_independent_classes"
        ]
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)

    def test_qap_cannot_be_promoted_to_constructed_regulator(self) -> None:
        mutant = deepcopy(self.value)
        mutant["quantum_action_principle"]["status"] = "CERTIFIED_REGULATOR"
        mutant["lifecycle"]["constructed_all_loop_regulator"] = "CERTIFIED"
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)

    def test_unconditional_all_loop_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["UNCONDITIONAL_ALL_LOOP_QME"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted|boundary"):
            validate(mutant)

    def test_filtered_inverse_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["filtered_deformation_stability"][
            "inverse_coefficients_through_order_12"
        ][5] = 1
        with self.assertRaisesRegex(ValueError, "Neumann"):
            verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
