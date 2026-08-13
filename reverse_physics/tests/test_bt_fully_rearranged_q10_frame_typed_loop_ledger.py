import copy
import json
import os
import unittest

from reverse_physics.verify_bt_fully_rearranged_q10_frame_typed_loop_ledger import (
    CERT_REL,
    ROOT,
    verify,
)


class FullyRearrangedQ10FrameTypedLoopLedgerTests(unittest.TestCase):
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
        self.mutate(["lifecycle_state"], "COEFFICIENT_COMPUTED")

    def test_tags_mutation(self):
        self.mutate(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_hash_mutation(self):
        self.mutate(["provenance", "inputs", 2, "sha256"], "0" * 64)

    def test_phi_action_mutation(self):
        self.mutate(["frame_dictionary", "original_phi_action"], "auxiliary")

    def test_auxiliary_vertex_mutation(self):
        self.mutate(["frame_dictionary", "auxiliary_vertices"], "contains V3")

    def test_typing_rule_mutation(self):
        self.mutate(["frame_dictionary", "typing_rule"], "add both lists")

    def test_projector_rule_mutation(self):
        self.mutate(["frame_dictionary", "projector_rule"], "automatic")

    def test_phi_row_mutation(self):
        self.mutate(["original_phi_order6", "rows", 1, "I"], 5)

    def test_phi_class_mutation(self):
        self.mutate(["original_phi_order6", "vertex_count_classes"], ["V4^3"])

    def test_auxiliary_count_mutation(self):
        self.mutate(["direct_auxiliary_order6", "labeled_multigraph_count"], 15)

    def test_auxiliary_orbit_mutation(self):
        self.mutate(["direct_auxiliary_order6", "orbit_count"], 3)

    def test_adjacency_mutation(self):
        self.mutate(["direct_auxiliary_order6", "rows", 0, "canonical_adjacency", 2, 2], 0)

    def test_orbit_size_mutation(self):
        self.mutate(["direct_auxiliary_order6", "rows", 1, "labeled_orbit_size"], 3)

    def test_external_profile_mutation(self):
        self.mutate(["direct_auxiliary_order6", "rows", 3, "external_leg_profile"], [1, 2, 3])

    def test_subgraph_mutation(self):
        self.mutate(["direct_auxiliary_order6", "rows", 1, "proper_loop_subgraph"], "NONE")

    def test_normal_order_status_mutation(self):
        self.mutate(["direct_auxiliary_order6", "rows", 0, "normal_ordered_massless_status"], "RETAINED")

    def test_survivors_mutation(self):
        self.mutate(["direct_auxiliary_order6", "normal_ordered_massless_survivors"], ["triangle"])

    def test_triangle_counterterm_mutation(self):
        self.mutate(["direct_auxiliary_order6", "counterterm_ledger", "triangle"], "MSBAR")

    def test_bubble_counterterm_mutation(self):
        self.mutate(["direct_auxiliary_order6", "counterterm_ledger", "bubble_with_bridge"], "finite")

    def test_tadpole_scheme_mutation(self):
        self.mutate(["direct_auxiliary_order6", "counterterm_ledger", "tadpoles"], "universally zero")

    def test_supersession_mutation(self):
        self.mutate(["correction", "status"], "NO_CORRECTION")

    def test_invalid_interpretation_mutation(self):
        self.mutate(["correction", "invalid_interpretation"], "none")

    def test_retained_triangle_mutation(self):
        self.mutate(["correction", "retained_exact_results"], [])

    def test_bubble_disposition_mutation(self):
        self.mutate(["disposition", "direct_auxiliary_bubble_with_bridge"], "COMPUTED")

    def test_cross_frame_mutation(self):
        self.mutate(["disposition", "cross_frame_addition_of_original_V3_classes"], "ALLOWED")

    def test_complete_q10_mutation(self):
        self.mutate(["disposition", "complete_q10"], "COEFFICIENT_COMPUTED")

    def test_Eq19_mutation(self):
        self.mutate(["disposition", "general_Eq19"], "PROVED")

    def test_gravity_mutation(self):
        self.mutate(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_causal_mutation(self):
        self.mutate(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_boundaries_mutation(self):
        self.mutate(["does_not_establish"], [])

    def test_producer_check_mutation(self):
        self.mutate(["checks", "details", "original_V3_classes_are_not_auxiliary_addends"], False)

    def test_next_gate_mutation(self):
        self.mutate(["next_gate"], "compute V3^2 V4^2")

    def test_report_mutation(self):
        self.mutate(["report"], "none")


if __name__ == "__main__":
    unittest.main()
