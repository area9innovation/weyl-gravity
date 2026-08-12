import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_hard_nonforward_physical_stratified_atlas import CERT, verify


class HardNonforwardPhysicalStratifiedAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_profile_count_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_partition_census"]["profile_counts"][8]["count"] = 14
        self.assert_rejected(mutation)

    def test_rejects_singleton_total_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_partition_census"]["singleton_containing"] = 161
        self.assert_rejected(mutation)

    def test_rejects_two_plus_four_split_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_partition_census"]["two_plus_four"]["spectator_cylinders"] = 8
        self.assert_rejected(mutation)

    def test_rejects_three_plus_three_support_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_partition_census"]["three_plus_three"]["hard_domain_supported"] = 1
        self.assert_rejected(mutation)

    def test_rejects_three_plus_three_orientation_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_partition_census"]["three_plus_three"]["orientation_obstructions"]["mixed_block_forces_same_side_collinearity"] = 8
        self.assert_rejected(mutation)

    def test_rejects_perfect_matching_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_partition_census"]["two_plus_two_plus_two"]["forward_permutations"] = 5
        self.assert_rejected(mutation)

    def test_rejects_missing_cylinder(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["spectator_cylinder_incidence"]["cylinders"].pop()
        self.assert_rejected(mutation)

    def test_rejects_wrong_cylinder_equation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["spectator_cylinder_incidence"]["cylinders"][0]["equation"] = "p_0=k_1"
        self.assert_rejected(mutation)

    def test_rejects_intersection_type_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["spectator_cylinder_incidence"]["intersection_types"]["distinct_pairs_force_third_and_forward"] = 17
        self.assert_rejected(mutation)

    def test_rejects_bulk_order_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_local_physical_atlas"]["bulk"]["leading_probability"] = "q_bulk=O(lambda^6)"
        self.assert_rejected(mutation)

    def test_rejects_spectator_order_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_local_physical_atlas"]["spectator_cylinder"]["leading_probability"] = "q_ia=O(lambda^8)"
        self.assert_rejected(mutation)

    def test_rejects_additional_generic_stratum(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_local_physical_atlas"]["additional_generic_strata"] = "TWO_SPECTATOR_STRATUM"
        self.assert_rejected(mutation)

    def test_rejects_cross_stratum_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["one_finite_resolution_cross_stratum_detector"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_lambda6_interference_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("the order-lambda6 interference between a spectator amplitude and the connected six-point amplitude in one unresolved output record")
        self.assert_rejected(mutation)

    def test_rejects_forward_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["forward_and_collinear_boundaries"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_gravity_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["gravity_or_BV_BRST_transfer"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["Lorentzian_causal_claim"] = "ESTABLISHED"
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
