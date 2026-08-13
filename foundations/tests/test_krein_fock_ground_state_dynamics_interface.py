from __future__ import annotations

import copy
import unittest

from foundations.build_krein_fock_ground_state_dynamics_interface import build, canonical_digest
from foundations.check_krein_fock_ground_state_dynamics_interface import check
from foundations.verify_krein_fock_ground_state_dynamics_interface import verify


class KreinFockGroundStateDynamicsInterfaceTests(unittest.TestCase):
    def test_interface_certifies_scoped_selection_and_invariance(self):
        value = build()
        self.assertEqual(value["interface"]["id"], "SELECTION_TO_DYNAMICS")
        self.assertEqual(value["interface"]["relation"], "CONDITIONAL_BRIDGE")
        self.assertTrue(value["claim_flags"]["free_ground_state_selected"])
        self.assertTrue(value["claim_flags"]["vacuum_dynamics_invariance_proved"])
        self.assertFalse(value["claim_flags"]["stationarity_alone_implies_uniqueness"])

    def test_independent_exact_controls(self):
        errors, summary = check(build())
        self.assertEqual(errors, [])
        self.assertEqual(summary["zero_occupations"], [[0, 0, 0]])
        self.assertEqual(summary["gap"], 2)
        self.assertEqual(summary["non_ground_energy"], "32/25")

    def test_interacting_promotion_fails(self):
        value = copy.deepcopy(build())
        value["claim_flags"]["interacting_ground_state_selected"] = True
        value["canonical_digest"] = canonical_digest(value)
        self.assertIn("boundary flag interacting_ground_state_selected", check(value)[0])

    def test_independent_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
