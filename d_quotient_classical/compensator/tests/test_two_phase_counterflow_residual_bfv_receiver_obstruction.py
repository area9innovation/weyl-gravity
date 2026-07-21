import json
import unittest
from copy import deepcopy

from d_quotient_classical.compensator.two_phase_counterflow_residual_bfv_receiver_obstruction import build_payload, documents, jacobi_defects


class ResidualBFVReceiverObstructionTests(unittest.TestCase):
    def test_generated_documents(self):
        cert, payload = documents()
        self.assertEqual(cert["stabilizer_dimension"], 5)
        self.assertEqual(payload["receiver_status"]["terminal_state"], "OBSTRUCTED_MISSING_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS")

    def test_exact_lie_algebra(self):
        self.assertEqual(jacobi_defects(), [])
        self.assertEqual(len(build_payload()["old_round_crosswalk"]["broken_generators"]), 10)

    def test_no_receiver_promotion(self):
        payload = build_payload()
        mutated = deepcopy(payload)
        mutated["receiver_status"]["full_BFV_nilpotency"] = "CERTIFIED"
        self.assertNotEqual(mutated["receiver_status"], payload["receiver_status"])
        self.assertIn("cannot be assembled", payload["missing_carrier"]["consequence"])


if __name__ == "__main__":
    unittest.main()
