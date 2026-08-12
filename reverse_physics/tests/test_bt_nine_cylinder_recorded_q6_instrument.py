"""Falsification tests for the recorded nine-cylinder BT q6 instrument."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_nine_cylinder_recorded_q6_instrument import CERT, verify


class NineCylinderRecordedQ6InstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def reject(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def mutated(self):
        return copy.deepcopy(self.certificate)

    def test_independent_verifier(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_group_order_mutation(self):
        value = self.mutated()
        value["permutation_orbit"]["group_order"] = 35
        self.reject(value)

    def test_rejects_missing_orbit_channel(self):
        value = self.mutated()
        value["permutation_orbit"]["orbit"].pop()
        self.reject(value)

    def test_rejects_stabilizer_mutation(self):
        value = self.mutated()
        value["permutation_orbit"]["stabilizer_order"] = 3
        self.reject(value)

    def test_rejects_record_dimension_mutation(self):
        value = self.mutated()
        value["record_algebra"]["dimension"] = 9
        self.reject(value)

    def test_rejects_transport_incidence_mutation(self):
        value = self.mutated()
        value["transported_tag_incidence"]["by_cylinder"]["Delta_21"]["weight_five_masks"][0] = 11
        self.reject(value)

    def test_rejects_record_completeness_mutation(self):
        value = self.mutated()
        value["record_algebra"]["completeness"] = "sum Pi=0"
        self.reject(value)

    def test_rejects_cylinder_weight_mutation(self):
        value = self.mutated()
        value["equal_block_preparation"]["cylinder_union_weight"] = {"numerator": 8, "denominator": 10}
        self.reject(value)

    def test_rejects_individual_weight_mutation(self):
        value = self.mutated()
        value["equal_block_preparation"]["record_weights"]["Delta_12"] = {"numerator": 2, "denominator": 10}
        self.reject(value)

    def test_rejects_selected_q6_formula_mutation(self):
        value = self.mutated()
        value["probability_through_lambda6"]["selected_cylinder_probability"] = "q=0"
        self.reject(value)

    def test_rejects_relative_q6_mutation(self):
        value = self.mutated()
        value["probability_through_lambda6"]["relative_q6_coefficient"] = "R6=0"
        self.reject(value)

    def test_rejects_bulk_order_promotion(self):
        value = self.mutated()
        value["probability_through_lambda6"]["bulk_outcome"] = "q_bulk=lambda^6"
        self.reject(value)

    def test_rejects_recorded_total_mutation(self):
        value = self.mutated()
        value["probability_through_lambda6"]["recorded_total"] = "q_recorded=q4"
        self.reject(value)

    def test_rejects_unresolved_detector_promotion(self):
        value = self.mutated()
        value["disposition"]["coherent_unresolved_cross_stratum_detector"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_generic_kinematics_promotion(self):
        value = self.mutated()
        value["disposition"]["generic_continuous_hard_kinematics"] = "COEFFICIENT_COMPUTED"
        self.reject(value)

    def test_rejects_forward_promotion(self):
        value = self.mutated()
        value["disposition"]["forward_or_collinear_sectors"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_Eq19_promotion(self):
        value = self.mutated()
        value["disposition"]["general_Eq19"] = "PROVED"
        self.reject(value)

    def test_rejects_gravity_promotion(self):
        value = self.mutated()
        value["disposition"]["gravity_or_metric_BV_BRST_transfer"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_Lorentzian_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [
            row for row in value["does_not_establish"] if "LORENTZIAN-CAUSAL" not in row
        ]
        self.reject(value)

    def test_rejects_input_hash_mutation(self):
        value = self.mutated()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.reject(value)


if __name__ == "__main__":
    unittest.main()
