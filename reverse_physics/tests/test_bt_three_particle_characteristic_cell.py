import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_three_particle_characteristic_cell import CERT, verify


class ThreeParticleCharacteristicCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_declared_probability_but_not_universal_cross_section(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["dimensionless_local_detector_shell_probability"], "COEFFICIENT_COMPUTED")
        self.assertEqual(result["detector_independent_three_body_cross_section"], "NOT_DEFINED")

    def test_rejects_constraint_jacobian_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["declared_incoming_cell"]["constraint_jacobian_determinant"] = "3/5"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_missing_outgoing_orbit(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["factorial_and_orbit_audit"]["outgoing_S3_orbit_multiplicity"] = 1
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_rate_coefficient_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_shell_probability"]["declared_rate_density"] = "Gamma_Xi=3*lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_detector_independence_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["detector_independent_three_body_cross_section"] = "COMPUTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_dimension_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_shell_probability"]["mass_dimension_of_rate"] = 0
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
