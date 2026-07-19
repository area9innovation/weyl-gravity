import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones import OUTPUT, build


class SameSignCollisionScalarOccupationConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.payload)

    def test_all_six_candidate_audits_are_complete(self) -> None:
        self.assertEqual([row["candidate_index"] for row in self.payload["candidate_rows"]], list(range(16, 22)))
        for row in self.payload["candidate_rows"]:
            self.assertEqual(row["counts"], {"support_three_minors": 20, "support_four_circuits": 15, "positive_extreme_rays": 4, "nonpositive_circuits": 11})

    def test_scope_remains_projected(self) -> None:
        flags = self.payload["classification"]
        self.assertTrue(flags["all_six_scalar_occupation_cones_classified"])
        self.assertFalse(flags["full_rotation_and_resonance_join_classified"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
