import copy
import json
import os
import unittest

from reverse_physics.verify_bt_fully_rearranged_bubble_bridge_covariant_block import (
    CERT_REL,
    ROOT,
    verify,
)


class BubbleBridgeCovariantBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def mutate(self, path, value):
        candidate = copy.deepcopy(self.certificate)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        self.assertFalse(all(verify(candidate).values()))

    def test_00_certificate_passes(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_top_level_injection_fails(self):
        self.mutate(["injected"], True)

    def test_identity_mutation(self):
        self.mutate(["certificate"], "X")

    def test_lifecycle_mutation(self):
        self.mutate(["lifecycle_state"], "CLASSIFIED")

    def test_tags_mutation(self):
        self.mutate(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_hash_mutation(self):
        self.mutate(["provenance", "inputs", 2, "sha256"], "0" * 64)

    def test_graph_count_mutation(self):
        self.mutate(["graph_and_master", "counts", "I"], 4)

    def test_role_count_mutation(self):
        self.mutate(["graph_and_master", "labeled_role_count"], 59)

    def test_vertex_factor_mutation(self):
        self.mutate(["graph_and_master", "net_tensor_prefactor"], "8")

    def test_symmetry_mutation(self):
        self.mutate(["graph_and_master", "bubble_symmetry_factor"], "1")

    def test_master_mutation(self):
        self.mutate(["graph_and_master", "bubble_master"], "log only")

    def test_amplitude_mutation(self):
        self.mutate(["graph_and_master", "amplitude"], "0")

    def test_neutral_masks_mutation(self):
        self.mutate(["species_tensor", "neutral_masks", 0], 0)

    def test_tensor_mutation(self):
        self.mutate(["species_tensor", "tensors", 0, 1, 3], 0)

    def test_weight_profile_mutation(self):
        self.mutate(["species_tensor", "per_role_profile"], "twenty unit")

    def test_HS_mutation(self):
        self.mutate(["species_tensor", "per_role_HS_square"], 53)

    def test_assignment_sum_mutation(self):
        self.mutate(["species_tensor", "sum_over_all_roles_on_each_neutral_assignment"], 89)

    def test_source_profile_mutation(self):
        self.mutate(["species_tensor", "source_weight_profile", "double_roles"], 35)

    def test_role_kinematics_mutation(self):
        self.mutate(["role_kinematics", "rows", 0, "bubble_invariant"], "0")

    def test_role_source_weight_mutation(self):
        self.mutate(["role_kinematics", "rows", 0, "source_weight"], 1)

    def test_bubble_margin_mutation(self):
        self.mutate(["role_kinematics", "minimum_abs_bubble_invariant"], "0")

    def test_on_shell_roles_mutation(self):
        self.mutate(["role_kinematics", "on_shell_bridge_role_indices", 0], 59)

    def test_hard_roles_mutation(self):
        self.mutate(["role_kinematics", "hard_zero_spatial_bridge_role_indices", 0], 59)

    def test_surviving_margin_mutation(self):
        self.mutate(["role_kinematics", "minimum_source_surviving_bridge_spatial_square"], "0")

    def test_group_identity_mutation(self):
        self.mutate(["tree_incidence", "group_identity"], "none")

    def test_group_role_mutation(self):
        self.mutate(["tree_incidence", "group_rows", 0, "role_indices", 0], 59)

    def test_cross_Gram_mutation(self):
        self.mutate(["tree_incidence", "cross_Gram", 0, 0], "7")

    def test_cross_multiplicity_mutation(self):
        self.mutate(["tree_incidence", "entry_multiplicities", "15/2"], 59)

    def test_cross_sum_mutation(self):
        self.mutate(["tree_incidence", "row_sum"], "404")

    def test_power_count_mutation(self):
        self.mutate(["renormalization", "overall_superficial_degree"], 0)

    def test_counterterm_mutation(self):
        self.mutate(["renormalization", "primitive_six_point_counterterm"], "REQUIRED")

    def test_RG_explicit_mutation(self):
        self.mutate(["renormalization", "explicit_scale_identity"], "0")

    def test_running_mutation(self):
        self.mutate(["renormalization", "running"], "beta=0")

    def test_RG_sum_mutation(self):
        self.mutate(["renormalization", "RG_sum"], "nonzero")

    def test_finite_time_collapse_mutation(self):
        self.mutate(["renormalization", "finite_time_local_identity"], "none")

    def test_off_diagonal_status_mutation(self):
        self.mutate(["finite_time_gate", "status"], "COMPUTED")

    def test_BT_substitution_mutation(self):
        self.mutate(["finite_time_gate", "why_existing_B_T_is_insufficient"], "B_T multiplies directly")

    def test_common_Born_mutation(self):
        self.mutate(["common_Born_interference", "status"], "SIGN_POSITIVE")

    def test_covariant_disposition_mutation(self):
        self.mutate(["disposition", "covariant_bubble_bridge_block"], "NOT_COMPUTED")

    def test_finite_time_disposition_mutation(self):
        self.mutate(["disposition", "finite_time_bubble_bridge"], "COEFFICIENT_COMPUTED")

    def test_q10_mutation(self):
        self.mutate(["disposition", "complete_q10"], "COEFFICIENT_COMPUTED")

    def test_Eq19_mutation(self):
        self.mutate(["disposition", "general_Eq19"], "PROVED")

    def test_gravity_mutation(self):
        self.mutate(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_causal_mutation(self):
        self.mutate(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_boundaries_mutation(self):
        self.mutate(["does_not_establish"], [])

    def test_next_gate_mutation(self):
        self.mutate(["next_gate"], "multiply by B_T")

    def test_producer_check_mutation(self):
        self.mutate(["checks", "details", "grouped_tensor_is_forty_times_tree_residue"], False)

    def test_report_mutation(self):
        self.mutate(["report"], "none")


if __name__ == "__main__":
    unittest.main()
