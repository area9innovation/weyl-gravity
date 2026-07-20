from __future__ import annotations

import unittest

from d_quotient_classical.compensator import (
    complex_scale_u1_full_bv_causal_gate as producer,
)
from d_quotient_classical.compensator import (
    verify_complex_scale_u1_full_bv_causal_gate as verifier,
)


class ComplexScaleU1FullBVCausalGateTest(unittest.TestCase):
    def test_exact_nonactivation(self) -> None:
        result = producer.build()
        self.assertFalse(result["activation_condition_satisfied"])
        self.assertEqual(
            result["result_state"],
            "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
        )

    def test_every_downstream_gate_not_activated(self) -> None:
        result = producer.build()
        self.assertTrue(
            all(
                row["status"] == "NOT_ACTIVATED"
                for row in result["skipped_gates"].values()
            )
        )

    def test_no_success_claim(self) -> None:
        result = producer.build()
        self.assertFalse(any(result["claim_flags"].values()))
        self.assertFalse(result["terminal_verdict"]["full_gate_activated"])

    def test_independent_replay(self) -> None:
        verifier.verify()


if __name__ == "__main__":
    unittest.main()
