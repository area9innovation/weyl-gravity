import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_six_point_shell_tree_normalization import CERT, verify


class ShellTreeNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_hamiltonian_fixed_but_probability_open(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["six_point_tree_coupling_normalization"], "COMPUTED")
        self.assertEqual(result["dimensionless_three_to_three_detector_probability"], "NOT_COMPUTED")

    def test_rejects_common_multiplier_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tree_topology_normalization"]["common_amplitude_multiplier"] = "8*i*lambda^4"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_phase_coefficient_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["finite_shell_coefficient"]["labeled_phase_weighted_coefficient"] = "27*lambda^8*T/(640*pi^4)"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_dimension_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["dimensional_and_detector_audit"]["required_incoming_projector_cell_weight_mass_dimension"] = 0
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["dimensionless_three_to_three_detector_probability"] = "COMPUTED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
