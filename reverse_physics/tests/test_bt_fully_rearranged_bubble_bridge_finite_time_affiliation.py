import copy
import json
import os
import unittest

from reverse_physics.verify_bt_fully_rearranged_bubble_bridge_finite_time_affiliation import (
    CERT_REL,
    ROOT,
    verify,
)


class BubbleBridgeFiniteTimeAffiliationTests(unittest.TestCase):
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
        self.mutate(["provenance", "inputs", 3, "sha256"], "0" * 64)

    def test_bubble_frequency_mutation(self):
        self.mutate(["renormalized_time_distribution", "bubble_frequency_kernel"], "real part only")

    def test_Fourier_mutation(self):
        self.mutate(["renormalized_time_distribution", "transform_convention"], "opposite sign")

    def test_momentum_derivative_mutation(self):
        self.mutate(["renormalized_time_distribution", "momentum_derivative"], "0")

    def test_finite_part_mutation(self):
        self.mutate(["renormalized_time_distribution", "nonlocal_form"], "ordinary function")

    def test_scale_mutation(self):
        self.mutate(["renormalized_time_distribution", "scale_derivative"], "0")

    def test_bridge_time_mutation(self):
        self.mutate(["renormalized_time_distribution", "bridge_time_distribution"], "1")

    def test_bridge_Fourier_identity_mutation(self):
        self.mutate(["renormalized_time_distribution", "bridge_Fourier_identity"], "missing i")

    def test_distribution_status_mutation(self):
        self.mutate(["renormalized_time_distribution", "status"], "PARTIAL")

    def test_time_pairing_mutation(self):
        self.mutate(["three_vertex_kernel", "time_pairing"], "two times")

    def test_spectral_pairing_mutation(self):
        self.mutate(["three_vertex_kernel", "spectral_pairing"], "B_T times tree")

    def test_bridge_frequency_mutation(self):
        self.mutate(["three_vertex_kernel", "bridge_frequency_kernel"], "1/(rho^2-E^2+i0)")

    def test_frequency_factor_mutation(self):
        self.mutate(["three_vertex_kernel", "frequency_factors", "A", "nu"], 1)

    def test_frequency_cancellation_mutation(self):
        self.mutate(["three_vertex_kernel", "internal_frequency_cancellation", "rho"], 1)

    def test_amplitude_mutation(self):
        self.mutate(["three_vertex_kernel", "amplitude"], "0")

    def test_BT_warning_mutation(self):
        self.mutate(["three_vertex_kernel", "warning"], "insert B_T")

    def test_kernel_status_mutation(self):
        self.mutate(["three_vertex_kernel", "status"], "NOT_COMPUTED")

    def test_ordering_row_mutation(self):
        self.mutate(["six_ordering_exhaustion", "rows", 0, "first_cut_edges"], [])

    def test_ordering_class_mutation(self):
        self.mutate(["six_ordering_exhaustion", "rows", 0, "UV_class"], "TWO_LARGE_DEFECTS")

    def test_ordering_count_mutation(self):
        self.mutate(["six_ordering_exhaustion", "one_large_defect_count"], 3)

    def test_local_face_mutation(self):
        self.mutate(["six_ordering_exhaustion", "cube_identity"], "no local face")

    def test_ordering_status_mutation(self):
        self.mutate(["six_ordering_exhaustion", "status"], "FIVE_ONLY")

    def test_window_bound_mutation(self):
        self.mutate(["spectral_convergence", "window_bound"], "unbounded")

    def test_threshold_mutation(self):
        self.mutate(["spectral_convergence", "bubble_thresholds"], "nonintegrable")

    def test_bridge_pole_mutation(self):
        self.mutate(["spectral_convergence", "bridge_poles"], "point value")

    def test_nu_tail_mutation(self):
        self.mutate(["spectral_convergence", "nu_axis"], "O(1)")

    def test_rho_tail_mutation(self):
        self.mutate(["spectral_convergence", "rho_axis"], "O(1)")

    def test_cancellation_tail_mutation(self):
        self.mutate(["spectral_convergence", "cancellation_line"], "O(1)")

    def test_generic_tail_mutation(self):
        self.mutate(["spectral_convergence", "generic_cone"], "O(1)")

    def test_on_shell_mutation(self):
        self.mutate(["spectral_convergence", "on_shell_bridge"], "evaluate pole")

    def test_convergence_status_mutation(self):
        self.mutate(["spectral_convergence", "status"], "DIVERGENT")

    def test_local_collapse_mutation(self):
        self.mutate(["finite_time_renormalization", "local_identity"], "0")

    def test_species_forest_mutation(self):
        self.mutate(["finite_time_renormalization", "species_forest_identity"], "20 R_C")

    def test_scale_identity_mutation(self):
        self.mutate(["finite_time_renormalization", "scale_identity"], "0")

    def test_RG_cancellation_mutation(self):
        self.mutate(["finite_time_renormalization", "cancellation"], "nonzero")

    def test_renormalization_status_mutation(self):
        self.mutate(["finite_time_renormalization", "status"], "UNMATCHED")

    def test_bubble_margin_mutation(self):
        self.mutate(["packet_bound", "bubble_spatial_margin"], "zero")

    def test_hard_bridge_mutation(self):
        self.mutate(["packet_bound", "hard_bridge"], "survives u0")

    def test_bridge_margin_mutation(self):
        self.mutate(["packet_bound", "surviving_bridge_margin"], "zero")

    def test_Lipschitz_mutation(self):
        self.mutate(["packet_bound", "time_domain_bounds"], "none")

    def test_finite_part_bound_mutation(self):
        self.mutate(["packet_bound", "finite_part_bound"], "diverges")

    def test_packet_consequence_mutation(self):
        self.mutate(["packet_bound", "consequence"], "unbounded")

    def test_packet_scope_mutation(self):
        self.mutate(["packet_bound", "scope"], "full carrier")

    def test_boundary_delta_mutation(self):
        self.mutate(["covariant_boundary", "translation_invariant_limit"], "zero")

    def test_boundary_match_mutation(self):
        self.mutate(["covariant_boundary", "role_boundary"], "triangle")

    def test_phase_stripped_boundary_mutation(self):
        self.mutate(["covariant_boundary", "phase_stripped_role_boundary"], "phase omitted")

    def test_boundary_shell_mutation(self):
        self.mutate(["covariant_boundary", "on_shell_rule"], "point value")

    def test_common_Born_mutation(self):
        self.mutate(["common_Born_interference", "status"], "SIGN_POSITIVE")

    def test_coefficient_disposition_mutation(self):
        self.mutate(["disposition", "finite_time_bubble_bridge"], "NOT_COMPUTED")

    def test_connected_T6_mutation(self):
        self.mutate(["disposition", "selected_source_direct_auxiliary_connected_finite_time_T6"], "INCOMPLETE")

    def test_full_carrier_mutation(self):
        self.mutate(["disposition", "full_carrier_zero_mode_extension"], "CONSTRUCTED")

    def test_interference_mutation(self):
        self.mutate(["disposition", "connected_y4_y6_interference_value"], "POSITIVE")

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
        self.mutate(["next_gate"], "q10 complete")

    def test_producer_check_mutation(self):
        self.mutate(["checks", "details", "energy_diagonal_B_T_is_not_used_as_vertex"], False)

    def test_report_mutation(self):
        self.mutate(["report"], "none")


if __name__ == "__main__":
    unittest.main()
