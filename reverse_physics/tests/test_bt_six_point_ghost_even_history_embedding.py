import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_ghost_even_history_embedding import CERT, verify


class GhostEvenHistoryEmbeddingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_exact_result_and_open_source_gate(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["complete_six_point_Choi_ghost_symmetry"], "EXACTLY_PROVED")
        self.assertEqual(result["input_projector_pushforward"], "NOT_CONSTRUCTED")

    def test_rejects_broken_complement_pair(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["neutral_six_leg_carrier"]["complement_masks"][0] = 55
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_false_Choi_symmetry(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["three_particle_Choi_process"]["intertwining_identity"] = "kappa3*A*kappa3=-A"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_global_isometry_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["global_history_rank_boundary"]["rank"] = 90
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_input_projector_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["input_projector_pushforward"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["Eq19_all_orders"] = "PROVED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
