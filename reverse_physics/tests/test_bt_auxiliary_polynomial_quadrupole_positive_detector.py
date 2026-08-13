import copy
import json
import os
import unittest

from reverse_physics.verify_bt_auxiliary_polynomial_quadrupole_positive_detector import (
    CERT_REL,
    ROOT,
    verify,
)


class AuxiliaryPolynomialQuadrupolePositiveDetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    @staticmethod
    def set_path(row, path, value):
        cursor = row
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    def assert_rejected(self, path, value):
        row = copy.deepcopy(self.certificate)
        self.set_path(row, path, value)
        checks = verify(row)
        self.assertFalse(all(checks.values()), checks)

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [name for name, value in checks.items() if not value])

    def test_rejects_identity(self):
        self.assert_rejected(["certificate"], "PROMOTED")

    def test_rejects_lifecycle(self):
        self.assert_rejected(["lifecycle_state"], "LORENTZIAN_CERTIFIED")

    def test_rejects_tags(self):
        self.assert_rejected(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.assert_rejected(["provenance", "inputs", 5, "sha256"], "0" * 64)

    def test_rejects_species_kappa(self):
        self.assert_rejected(["quadratic_species_classification", "fundamental_symmetry", 0, 1], "0")

    def test_rejects_responding_tensor(self):
        self.assert_rejected(["quadratic_species_classification", "responding_tensor", 0, 0], "0")

    def test_rejects_neutral_tensor(self):
        self.assert_rejected(["quadratic_species_classification", "neutral_tensor", 0, 1], "0")

    def test_rejects_neutral_response(self):
        self.assert_rejected(["quadratic_species_classification", "neutral_pure_pair_response", 0], "1")

    def test_rejects_charge_support(self):
        self.assert_rejected(["quadratic_species_classification", "responding_charge_support"], ["0"])

    def test_rejects_regular_chart(self):
        self.assert_rejected(["quadratic_species_classification", "regularity"], "USES_LOG")

    def test_rejects_classification_status(self):
        self.assert_rejected(["quadratic_species_classification", "status"], "NEUTRAL_RESPONDING")

    def test_rejects_pointer_charge(self):
        self.assert_rejected(["charge_balanced_pointer", "branch_charge_sums", 0], "-2-2=-4")

    def test_rejects_three_particle_kappa(self):
        self.assert_rejected(["charge_balanced_pointer", "three_particle_kappa", 0, 7], "0")

    def test_rejects_output_kappa(self):
        self.assert_rejected(["charge_balanced_pointer", "pointer_spectator_kappa", 0, 3], "0")

    def test_rejects_pair_map_first_branch(self):
        self.assert_rejected(["charge_balanced_pointer", "pair_map", 0, 0], "0")

    def test_rejects_pair_map_second_branch(self):
        self.assert_rejected(["charge_balanced_pointer", "pair_map", 3, 7], "0")

    def test_rejects_interaction(self):
        self.assert_rejected(["charge_balanced_pointer", "truncated_interaction", 0, 8], "0")

    def test_rejects_Hilbert_Gram(self):
        self.assert_rejected(["charge_balanced_pointer", "Hilbert_Gram", 11, 11], "-1")

    def test_rejects_operator_adjoint(self):
        self.assert_rejected(["charge_balanced_pointer", "operator_identities", 1], "V*=-V")

    def test_rejects_pointer_status(self):
        self.assert_rejected(["charge_balanced_pointer", "status"], "CHARGE_BREAKING")

    def test_rejects_pure_channel(self):
        self.assert_rejected(["compact_q8_response", "pure_channel"], "S=11")

    def test_rejects_tree_ratio(self):
        self.assert_rejected(["compact_q8_response", "connected_tree_relation"], "J_tree,pure=0")

    def test_rejects_tree_lower(self):
        self.assert_rejected(["compact_q8_response", "connected_tree_lower"], "J_tree,pure=0")

    def test_rejects_loop_lower(self):
        self.assert_rejected(["compact_q8_response", "loop_lower"], "J_loop<0")

    def test_rejects_relative_lower(self):
        self.assert_rejected(["compact_q8_response", "complete_relative_lower"], "J_R,aux=0")

    def test_rejects_local_lower(self):
        self.assert_rejected(["compact_q8_response", "local_lower"], "zero")

    def test_rejects_compact_lower(self):
        self.assert_rejected(["compact_q8_response", "compact_lower"], "zero")

    def test_rejects_probability_order(self):
        self.assert_rejected(["compact_q8_response", "probability"], "p_click=1")

    def test_rejects_response_status(self):
        self.assert_rejected(["compact_q8_response", "status"], "ALL_ORDER")

    def test_rejects_scalar_projection_promotion(self):
        self.assert_rejected(["disposition", "same_chart_scalar_hidden_parity_projection"], "CONSTRUCTED")

    def test_rejects_pointer_omission(self):
        self.assert_rejected(["disposition", "boost_neutral_total_pointer_coupling"], "NO_POINTER_NEEDED")

    def test_rejects_affiliation_promotion(self):
        self.assert_rejected(["disposition", "full_selfadjoint_local_net_affiliation"], "CONSTRUCTED")

    def test_rejects_all_orders_promotion(self):
        self.assert_rejected(["disposition", "all_orders_in_detector_or_BT_coupling"], "PROVED")

    def test_rejects_Eq19_promotion(self):
        self.assert_rejected(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.assert_rejected(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_rejects_Lorentzian_promotion(self):
        self.assert_rejected(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_rejects_next_gate_erasure(self):
        self.assert_rejected(["next_gate"], "done")


if __name__ == "__main__":
    unittest.main()
