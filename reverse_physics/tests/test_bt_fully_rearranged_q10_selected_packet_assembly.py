import copy
import json
import os
import unittest

from reverse_physics.verify_bt_fully_rearranged_q10_selected_packet_assembly import (
    CERT_REL,
    ROOT,
    verify,
)


class FullyRearrangedQ10SelectedPacketAssemblyTests(unittest.TestCase):
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

    def test_injection_fails(self):
        self.mutate(["injected"], True)

    def test_identity_mutation(self):
        self.mutate(["certificate"], "X")

    def test_lifecycle_mutation(self):
        self.mutate(["lifecycle_state"], "CLASSIFIED")

    def test_tags_mutation(self):
        self.mutate(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_hash_mutation(self):
        self.mutate(["provenance", "inputs", 9, "sha256"], "0" * 64)

    def test_coupling_mutation(self):
        self.mutate(["fixed_auxiliary_expansion", "coupling"], "g=lambda")

    def test_amplitude_mutation(self):
        self.mutate(["fixed_auxiliary_expansion", "restricted_amplitude"], "lambda^5*T5")

    def test_y5_mutation(self):
        self.mutate(["fixed_auxiliary_expansion", "fixed_y5"], "nonzero")

    def test_q10_formula_mutation(self):
        self.mutate(["fixed_auxiliary_expansion", "q10"], "norm(y5)^2")

    def test_expansion_status_mutation(self):
        self.mutate(["fixed_auxiliary_expansion", "status"], "INCOMPLETE")

    def test_external_support_mutation(self):
        self.mutate(["order_g3_exhaustion", "external_disconnected"], "unknown")

    def test_forward_mutation(self):
        self.mutate(["order_g3_exhaustion", "forward_survival"], "survives")

    def test_vacuum_mutation(self):
        self.mutate(["order_g3_exhaustion", "vacuum"], "included")

    def test_topologies_mutation(self):
        self.mutate(["order_g3_exhaustion", "normal_ordered_topologies"], ["triangle"])

    def test_complete_kernel_mutation(self):
        self.mutate(["order_g3_exhaustion", "complete_kernel"], "triangle only")

    def test_exhaustion_status_mutation(self):
        self.mutate(["order_g3_exhaustion", "status"], "MISSING")

    def test_selected_similarity_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "selected_scalar_identity"], "not invariant")

    def test_general_relation_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "general_relation"], "none")

    def test_fixture_y5_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "exact_fixture", "pulled_y5"], ["0", "0"])

    def test_fixture_norm_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "exact_fixture", "y5_norm"], "0")

    def test_fixture_cross_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "exact_fixture", "second_order_dressing_cross"], "5")

    def test_fixture_sum_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "exact_fixture", "dressing_sum"], "1")

    def test_fixture_q10_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "exact_fixture", "pulled_q10"], "3")

    def test_fixture_orthogonality_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "exact_fixture", "rotation_is_exactly_orthogonal"], False)

    def test_dressing_scope_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "scope"], "general Eq. (19)")

    def test_dressing_status_mutation(self):
        self.mutate(["similarity_dressing_cancellation", "status"], "UNCANCELLED")

    def test_functional_kernel_mutation(self):
        self.mutate(["assembled_packet_functional", "complete_T6"], "triangle only")

    def test_functional_formula_mutation(self):
        self.mutate(["assembled_packet_functional", "q10"], "0" * 101)

    def test_packet_domain_mutation(self):
        self.mutate(["assembled_packet_functional", "packet_domain"], "unrelated packets")

    def test_boundedness_mutation(self):
        self.mutate(["assembled_packet_functional", "boundedness"], "divergent")

    def test_value_mutation(self):
        self.mutate(["assembled_packet_functional", "value"], "UNIVERSAL_NUMBER")

    def test_sign_mutation(self):
        self.mutate(["assembled_packet_functional", "sign"], "POSITIVE")

    def test_functional_status_mutation(self):
        self.mutate(["assembled_packet_functional", "status"], "CLASSIFIED")

    def test_Born_effect_mutation(self):
        self.mutate(["common_Born_identity", "effect"], "unequal")

    def test_Born_conclusion_mutation(self):
        self.mutate(["common_Born_identity", "conclusion"], "public differs")

    def test_Born_status_mutation(self):
        self.mutate(["common_Born_identity", "status"], "NOT_ESTABLISHED")

    def test_bubble_scale_mutation(self):
        self.mutate(["renormalization_group", "bubble_scale_derivative"], "0")

    def test_q10_scale_mutation(self):
        self.mutate(["renormalization_group", "q10_scale_derivative"], "0")

    def test_beta_mutation(self):
        self.mutate(["renormalization_group", "beta"], "0")

    def test_RG_cancellation_mutation(self):
        self.mutate(["renormalization_group", "cancellation"], "nonzero")

    def test_scheme_mutation(self):
        self.mutate(["renormalization_group", "finite_scheme_rule"], "universal")

    def test_RG_status_mutation(self):
        self.mutate(["renormalization_group", "status"], "SCALE_DEPENDENT")

    def test_disposition_mutation(self):
        self.mutate(["disposition", "selected_finite_time_q10"], "NOT_COMPUTED")

    def test_common_Born_disposition_mutation(self):
        self.mutate(["disposition", "selected_q10_common_Born"], "NOT_PROVED")

    def test_projector_promotion_mutation(self):
        self.mutate(["disposition", "standard_shift_invariant_projector"], "CONSTRUCTED")

    def test_Eq19_mutation(self):
        self.mutate(["disposition", "general_Eq19"], "PROVED")

    def test_gravity_mutation(self):
        self.mutate(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_causal_mutation(self):
        self.mutate(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_boundaries_mutation(self):
        self.mutate(["does_not_establish"], [])

    def test_next_gate_mutation(self):
        self.mutate(["next_gate"], "done")

    def test_producer_check_mutation(self):
        self.mutate(["checks", "details", "fixed_y5_and_q9_are_zero"], False)

    def test_report_mutation(self):
        self.mutate(["report"], "none")


if __name__ == "__main__":
    unittest.main()
