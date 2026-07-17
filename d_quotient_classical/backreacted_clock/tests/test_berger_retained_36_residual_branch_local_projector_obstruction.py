import json
import unittest

from d_quotient_classical.backreacted_clock import berger_retained_36_residual_branch_local_projector_obstruction as producer


class ProjectorObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = producer.build()

    def test_exact_witness_is_normalized(self):
        self.assertEqual(self.payload["normalized_obstruction_witness"]["normalized_evaluation"], "1")
        self.assertNotEqual(self.payload["normalized_obstruction_witness"]["division_remainder"], "0")

    def test_binary_handoff_is_fail_closed(self):
        self.assertFalse(self.payload["requested_binary_handoff"]["successful_basis_artifact_issued"])
        self.assertTrue(self.payload["requested_binary_handoff"]["normalized_obstruction_issued"])
        self.assertFalse(self.payload["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"])

    def test_category_boundary(self):
        self.assertTrue(self.payload["category_guards"]["Einstein_like_is_dynamical"])
        self.assertTrue(self.payload["category_guards"]["extra_Weyl_is_dynamical"])
        self.assertFalse(self.payload["category_guards"]["topological_odd_direction_is_particle_branch"])

    def test_scope_does_not_overclaim(self):
        boundary = self.payload["claim_boundary"]
        self.assertIn("does not prove global nonexistence", boundary)
        self.assertIn("mixed-bundle", boundary)

    def test_mutation_guard_rejects_promotion(self):
        mutant = json.loads(json.dumps(self.payload))
        mutant["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] = True
        with self.assertRaises(AssertionError):
            producer.verify(mutant)


if __name__ == "__main__":
    unittest.main()
