"""Falsification tests for the complete relative two-angle BT q8 result."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_two_angle_q8_coherence_difference import CERT, verify


class TwoAngleQ8CoherenceDifferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def mutated(self):
        return copy.deepcopy(self.certificate)

    def reject(self, value):
        self.assertFalse(all(verify(value).values()))

    def test_independent_verifier(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_selected_output_mutation(self):
        value = self.mutated()
        value["complete_q8_ledger"]["selected_output"] = "X=lambda^2*X2"
        self.reject(value)

    def test_rejects_pair_omission(self):
        value = self.mutated()
        value["complete_q8_ledger"]["ordered_coefficient_pairs"].pop()
        self.reject(value)

    def test_rejects_odd_pair_survival(self):
        value = self.mutated()
        value["complete_q8_ledger"]["vanishing_pairs"] = []
        self.reject(value)

    def test_rejects_hermitian_class_mutation(self):
        value = self.mutated()
        value["complete_q8_ledger"]["surviving_hermitian_classes"] = ["(2,6)"]
        self.reject(value)

    def test_rejects_recorded_ledger_mutation(self):
        value = self.mutated()
        value["complete_q8_ledger"]["recorded_coefficient"] = "q8=||X4||^2"
        self.reject(value)

    def test_rejects_coherent_ledger_mutation(self):
        value = self.mutated()
        value["complete_q8_ledger"]["coherent_coefficient"] = "q8=0"
        self.reject(value)

    def test_rejects_leading_fixed_point_mutation(self):
        value = self.mutated()
        value["cross_invariance"]["leading_fixed_point"] = "E_epsilon X2=0"
        self.reject(value)

    def test_rejects_cross_identity_mutation(self):
        value = self.mutated()
        value["cross_invariance"]["self_adjoint_step"] = "<X2,E X6>=0"
        self.reject(value)

    def test_rejects_relative_formula_sign(self):
        value = self.mutated()
        value["relative_q8_coefficient"]["formula"] = "q8[E]-q8[I]=+(epsilon/2)*||X4(c1)-X4(c2)||^2"
        self.reject(value)

    def test_rejects_relative_sign_promotion(self):
        value = self.mutated()
        value["relative_q8_coefficient"]["sign"] = "POSITIVE"
        self.reject(value)

    def test_rejects_equality_condition_mutation(self):
        value = self.mutated()
        value["relative_q8_coefficient"]["equality"] = "always"
        self.reject(value)

    def test_rejects_pure_coherent_endpoint_mutation(self):
        value = self.mutated()
        value["relative_q8_coefficient"]["pure_coherent_endpoint"] = "q8[P_plus]=q8[I2]"
        self.reject(value)

    def test_rejects_fixture_cross_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["coherent_X2_X6_cross"] = "0"
        self.reject(value)

    def test_rejects_fixture_recorded_q8_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["recorded_q8"] = "5031/315"
        self.reject(value)

    def test_rejects_fixture_coherent_q8_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["coherent_q8"] = "3962/315"
        self.reject(value)

    def test_rejects_fixture_difference_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["difference"] = "17/5"
        self.reject(value)

    def test_rejects_absolute_q8_promotion(self):
        value = self.mutated()
        value["absolute_q8_boundary"]["status"] = "COMPUTED"
        self.reject(value)

    def test_rejects_recorded_q8_disposition_promotion(self):
        value = self.mutated()
        value["disposition"]["absolute_recorded_q8_probability"] = "COMPUTED"
        self.reject(value)

    def test_rejects_coherent_q8_disposition_promotion(self):
        value = self.mutated()
        value["disposition"]["absolute_coherent_q8_probability"] = "COMPUTED"
        self.reject(value)

    def test_rejects_dynamical_selection_promotion(self):
        value = self.mutated()
        value["disposition"]["BT_dynamical_detector_selection"] = "ESTABLISHED"
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
