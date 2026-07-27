"""Mutation tests for the complete massive axial Jost crosswalk."""
from __future__ import annotations

import copy
import json
import unittest

from . import produce, verify


class MassiveJostCrosswalkTest(unittest.TestCase):
    def test_producer_and_verifier(self) -> None:
        result = produce.produce()
        self.assertEqual(
            result["status"],
            "ANALYTIC_COMPLETE_MASSIVE_JOST_CROSSWALK_AND_NONZERO_QNM_VELOCITY",
        )
        verify.verify()

    def test_false_causal_promotion_fails_closed(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        mutant = copy.deepcopy(payload)
        mutant["claim_flags"]["global_causal_resolvent_certified"] = True
        with self.assertRaises(AssertionError):
            verify.verify(mutant)

    def test_phase_residual_mutation_fails_closed(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        mutant = copy.deepcopy(payload)
        mutant["infinity_jost"]["phase_residual"] = "0"
        with self.assertRaises(AssertionError):
            verify.verify(mutant)

    def test_velocity_promotion_requires_zero_exclusion(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        mutant = copy.deepcopy(payload)
        mutant["mass_velocity"]["certified_outer_enclosure"]["re"] = [
            "-0.251",
            "0.251",
        ]
        with self.assertRaises(AssertionError):
            verify.verify(mutant)


if __name__ == "__main__":
    unittest.main()
