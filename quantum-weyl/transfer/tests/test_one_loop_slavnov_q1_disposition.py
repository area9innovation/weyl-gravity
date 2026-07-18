from __future__ import annotations

from copy import deepcopy
import unittest

from transfer.one_loop_slavnov_q1_disposition import build, validate
from transfer.verify_one_loop_slavnov_q1_disposition import verify


class OneLoopSlavnovQ1DispositionTests(unittest.TestCase):
    def test_certificate_builds_and_replays(self) -> None:
        payload = build()
        validate(payload)
        verify()

    def test_residual_transfer_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(Exception):
            validate(payload)

    def test_complete_q1_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"] = True
        with self.assertRaises(Exception):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
