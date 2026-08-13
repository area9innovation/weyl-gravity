import copy
import json
import os
import unittest

from reverse_physics.verify_bt_fully_rearranged_v4_cubed_finite_time_affiliation import (
    CERT_REL,
    ROOT,
    verify,
)


class FullyRearrangedV4CubedFiniteTimeAffiliationTests(unittest.TestCase):
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

    def test_tag_mutation(self):
        self.mutate(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_hash_mutation(self):
        self.mutate(["provenance", "inputs", 2, "sha256"], "0" * 64)

    def test_coefficient_mutation(self):
        self.mutate(["three_vertex_time_kernel", "coefficient_check", 4, "coefficient_without_i_power"], "1/7")

    def test_simplex_mutation(self):
        self.mutate(["three_vertex_time_kernel", "simplex"], "one-dimensional kernel")

    def test_collision_mutation(self):
        self.mutate(["three_vertex_time_kernel", "collision_rule"], "singular")

    def test_ordering_mutation(self):
        self.mutate(["six_ordering_exhaustion", "rows", 0, "first_interval_defect"], "Delta1=0")

    def test_factorial_mutation(self):
        self.mutate(["six_ordering_exhaustion", "factorial_identity"], "an extra 1/6 remains")

    def test_energy_routing_mutation(self):
        self.mutate(["six_ordering_exhaustion", "internal_edge_energies"], "two lines only")

    def test_scalar_triangle_mutation(self):
        self.mutate(["finite_time_triangle", "scalar_kernel"], "covariant C0 only")

    def test_amplitude_mutation(self):
        self.mutate(["finite_time_triangle", "amplitude"], "T6=0")

    def test_phase_convention_mutation(self):
        self.mutate(["finite_time_triangle", "normalization"], "phase omitted")

    def test_boundary_mutation(self):
        self.mutate(["finite_time_triangle", "covariant_boundary"], "not matched")

    def test_transient_mutation(self):
        self.mutate(["finite_time_triangle", "transient_decomposition"], "R_T=0")

    def test_counterterm_mutation(self):
        self.mutate(["finite_time_triangle", "counterterm"], "MSBAR REQUIRED")

    def test_packet_margin_mutation(self):
        self.mutate(["packet_convergence", "minimum_external_pair_spatial_square"], "0")

    def test_IR_mutation(self):
        self.mutate(["packet_convergence", "finite_region"], "three lines may be soft")

    def test_endpoint_mutation(self):
        self.mutate(["packet_convergence", "endpoint_identity"], "h(0)=1")

    def test_integration_by_parts_mutation(self):
        self.mutate(["packet_convergence", "integration_by_parts"], "O(1)")

    def test_tail_mutation(self):
        self.mutate(["packet_convergence", "tail"], "O(dr)")

    def test_common_Born_mutation(self):
        self.mutate(["common_Born_interference", "status"], "KREIN_ONLY")

    def test_sign_mutation(self):
        self.mutate(["common_Born_interference", "sign"], "POSITIVE")

    def test_complete_q10_mutation(self):
        self.mutate(["disposition", "complete_q10"], "COEFFICIENT_COMPUTED")

    def test_Eq19_mutation(self):
        self.mutate(["disposition", "general_Eq19"], "PROVED")

    def test_gravity_mutation(self):
        self.mutate(["disposition", "gravity_or_BV_BRST_transfer"], "CONSTRUCTED")

    def test_causal_mutation(self):
        self.mutate(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_boundaries_mutation(self):
        self.mutate(["does_not_establish"], [])

    def test_next_gate_mutation(self):
        self.mutate(["next_gate"], "done")

    def test_report_mutation(self):
        self.mutate(["report"], "none")


if __name__ == "__main__":
    unittest.main()
