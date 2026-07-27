"""Tests for the complete massive axial first-jet crosswalk."""
from __future__ import annotations

import copy
import json
import unittest

from . import produce, verify


class CompleteMassiveJetCrosswalkTest(unittest.TestCase):
    def test_producer_and_verifier(self) -> None:
        produced = produce.produce()
        self.assertEqual(
            produced["status"],
            "EXACT_COMPLETE_MASSIVE_FIRST_JET_FACTOR_THREE_PASS",
        )
        verify.verify()

    def test_false_physical_promotion_fails_closed(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        mutant = copy.deepcopy(payload)
        mutant["claim_flags"]["physical_QNM_velocity_certified"] = True
        with self.assertRaises(AssertionError):
            verify.verify(mutant)

    def test_wrong_factor_fails_closed(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        mutant = copy.deepcopy(payload)
        mutant["bach_crosswalk"]["physical_scaling"] = "I*omega/2"
        with self.assertRaises(AssertionError):
            verify.verify(mutant)

    def test_imported_flow_mutation_fails_closed(self) -> None:
        payload = json.loads(verify.CERTIFICATE.read_text())
        mutant = copy.deepcopy(payload)
        mutant["complete_massive_axial_system"]["massless_flow"][1][2] = (
            "7*(r-3)*(r-2)/r**4"
        )
        with self.assertRaises(AssertionError):
            verify.verify(mutant)


if __name__ == "__main__":
    unittest.main()
