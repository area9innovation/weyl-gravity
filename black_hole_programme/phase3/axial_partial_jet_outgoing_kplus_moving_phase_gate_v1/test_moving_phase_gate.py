"""Mutation tests for the outgoing moving-phase K-plus gate."""
from __future__ import annotations

import copy
import json
import unittest

from .verify import HERE, verify


class MovingPhaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify(copy.deepcopy(self.document))

    def test_rejects_static_rephasing(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["common_gauge_reissue_at_r31"][
            "relative_rephasing_tau_independent"
        ] = True
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_kplus_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["analytic_K_plus_zero_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_rate_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["common_gauge_reissue_at_r31"][
            "relative_log_tau_derivative"
        ] = "0"
        with self.assertRaises(RuntimeError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
