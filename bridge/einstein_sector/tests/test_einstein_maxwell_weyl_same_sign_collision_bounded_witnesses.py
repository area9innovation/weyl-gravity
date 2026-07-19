import json
import unittest
from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_bounded_witnesses import OUTPUT, build

class SameSignBoundedWitnessTests(unittest.TestCase):
    def test_certificate_current(self): self.assertEqual(json.loads(OUTPUT.read_text()), build())
    def test_all_six_points_but_not_full_cones(self):
        p=build(); self.assertEqual([r["candidate_index"] for r in p["witness_rows"]],list(range(16,22)))
        self.assertTrue(p["classification"]["all_six_nonzero_bounded_points_certified"])
        self.assertFalse(p["classification"]["all_six_complete_bounded_cones_classified"])

    def test_isolated_resonances_are_crosswalked_and_candidate21_is_normalized(self):
        p = build()
        for row in p["witness_rows"]:
            self.assertEqual(row["isolated_resonance_crosswalk"]["canonical_signed_momenta"], [1, 2])
            self.assertEqual(row["rho"], row["isolated_resonance_crosswalk"]["rho"])
        candidate21 = p["witness_rows"][-1]["cross_fibre_resonance"]
        self.assertIn("kappa_A(r)", candidate21["amplitude_factorization"])
        self.assertIn("kappa_B(s)>0", candidate21["amplitude_factorization"])

if __name__ == "__main__": unittest.main()
