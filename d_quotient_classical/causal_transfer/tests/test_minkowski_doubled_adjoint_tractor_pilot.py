from __future__ import annotations

import json
import unittest

from d_quotient_classical.causal_transfer import minkowski_doubled_adjoint_tractor_pilot as pilot


class MinkowskiDoubledAdjointTractorPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = pilot.build_proof()
        cls.consumer = pilot.build_consumer(cls.proof)

    def test_non_cylinder_background(self) -> None:
        self.assertTrue(self.proof["background"]["not_conformal_cylinder"])
        self.assertEqual(self.proof["background"]["riemann_tensor"], "0")

    def test_mixed_operator_is_nontrivial(self) -> None:
        q = self.proof["exact_flavor_fixture"]["mixed_unary_matrix"]
        self.assertNotEqual([row[2:] for row in q[:2]], [[0, 0], [0, 0]])

    def test_exact_fixture(self) -> None:
        self.assertTrue(all(value == 0 for value in self.proof["exact_flavor_fixture"]["identity_defects"].values()))

    def test_descent_direction(self) -> None:
        self.assertEqual(self.consumer["SDR"]["transfer_direction"], "FULL_TO_ENDPOINT_DESCENT")

    def test_complete_doubled_ranks(self) -> None:
        self.assertEqual(self.consumer["complexes"]["full"]["degree_ranks"], [30, 120, 120, 30])
        self.assertEqual(self.consumer["complexes"]["endpoint"]["degree_ranks"], [8, 18, 18, 8])

    def test_fail_closed_scope(self) -> None:
        self.assertFalse(self.proof["flags"]["INTERACTING_MIXED_FIELD_THEORY"])
        self.assertFalse(self.proof["flags"]["G3_OPEN_BACKGROUND_CLASS"])
        self.assertFalse(self.proof["flags"]["QUANTUM_CLAIM"])

    def test_written_artifacts_match(self) -> None:
        self.assertEqual(json.loads(pilot.PROOF_PATH.read_text()), self.proof)
        self.assertEqual(json.loads(pilot.CONSUMER_PATH.read_text()), self.consumer)


if __name__ == "__main__":
    unittest.main()
