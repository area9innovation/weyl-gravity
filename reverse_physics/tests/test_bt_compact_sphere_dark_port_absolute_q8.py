"""Falsification tests for compact-sphere BT dark-port q8."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_compact_sphere_dark_port_absolute_q8 import CERT, verify


class CompactSphereDarkPortQ8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def mutated(self):
        return copy.deepcopy(self.certificate)

    def reject(self, value):
        self.assertFalse(all(verify(value).values()))

    def alter(self, path, value):
        row = self.mutated()
        target = row
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        self.reject(row)

    def test_independent_verifier(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_input_hash(self):
        row = self.mutated()
        row["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.reject(row)

    def test_rejects_lifecycle_promotion(self):
        self.alter(["lifecycle_state"], "RESIDUAL_TRANSFERRED")

    def test_rejects_dependency_tag_removal(self):
        self.alter(["dependency_tags"], ["REDUCED-MODE"])

    def test_rejects_dc_measure(self):
        self.alter(["invariant_packet_geometry", "measure"], "dc")

    def test_rejects_packet_half_width(self):
        self.alter(["invariant_packet_geometry", "half_width"], "1/100")

    def test_rejects_bin_zero(self):
        self.alter(["invariant_packet_geometry", "bin_0"], "point phi=pi/2")

    def test_rejects_bin_one(self):
        self.alter(["invariant_packet_geometry", "bin_1"], "point phi=acos(3/5)")

    def test_rejects_c0_lower_value(self):
        self.alter(["invariant_packet_geometry", "c_interval_0", "lower", "exact"], "-1/2")

    def test_rejects_c0_lower_hash(self):
        self.alter(["invariant_packet_geometry", "c_interval_0", "lower", "canonical_sha256"], "0" * 64)

    def test_rejects_c1_upper_value(self):
        self.alter(["invariant_packet_geometry", "c_interval_1", "upper", "exact"], "9/10")

    def test_rejects_c1_upper_hash(self):
        self.alter(["invariant_packet_geometry", "c_interval_1", "upper", "canonical_sha256"], "f" * 64)

    def test_rejects_zero_measure_cells(self):
        self.alter(["invariant_packet_geometry", "positive_measure_cells"], "measure=0")

    def test_rejects_unnormalized_packets(self):
        self.alter(["invariant_packet_geometry", "normalized_packets"], "h_j=indicator(B_j)")

    def test_rejects_nonorthogonal_packets(self):
        self.alter(["invariant_packet_geometry", "orthogonality"], "<h0,h1>=1")

    def test_rejects_geometry_status(self):
        self.alter(["invariant_packet_geometry", "status"], "DELTA_MODES")

    def test_rejects_W0_lower_value(self):
        self.alter(["exact_equatorial_margins", "W_angle_part_0", "lower", "exact"], "0")

    def test_rejects_W1_upper_hash(self):
        self.alter(["exact_equatorial_margins", "W_angle_part_1", "upper", "canonical_sha256"], "0" * 64)

    def test_rejects_tree_contrast_value(self):
        self.alter(["exact_equatorial_margins", "tree_contrast", "lower", "exact"], "1/2")

    def test_rejects_tree_simple_bound(self):
        self.alter(["exact_equatorial_margins", "tree_simple_bound"], "DeltaW>0")

    def test_rejects_loop_reduction(self):
        self.alter(["exact_equatorial_margins", "loop_reduction"], "B(c)=common")

    def test_rejects_H0_lower_value(self):
        self.alter(["exact_equatorial_margins", "H_pair_0", "lower", "exact"], "0")

    def test_rejects_H1_upper_hash(self):
        self.alter(["exact_equatorial_margins", "H_pair_1", "upper", "canonical_sha256"], "0" * 64)

    def test_rejects_loop_contrast_value(self):
        self.alter(["exact_equatorial_margins", "loop_contrast", "lower", "exact"], "1/1000")

    def test_rejects_loop_simple_bound(self):
        self.alter(["exact_equatorial_margins", "loop_simple_bound"], "DeltaB>0")

    def test_rejects_loop_cancellation(self):
        self.alter(["exact_equatorial_margins", "cancellation"], "scale remains")

    def test_rejects_tree_continuity_removal(self):
        self.alter(["compact_thickening", "tree_kernel_input"], "unknown")

    def test_rejects_loop_continuity_removal(self):
        self.alter(["compact_thickening", "loop_kernel_input"], "unknown")

    def test_rejects_uniformity_argument_removal(self):
        self.alter(["compact_thickening", "uniformity_argument"], "pointwise only")

    def test_rejects_fabricated_radius(self):
        self.alter(["compact_thickening", "radius_status"], "EPSILON=1/10")

    def test_rejects_signed_packet_choice(self):
        self.alter(["compact_thickening", "packet_choice"], "arbitrary signed distributions")

    def test_rejects_point_kernel_margin(self):
        self.alter(["compact_thickening", "pointwise_tree_kernel_contrast_after_thickening"], "DeltaW_kernel>0")

    def test_rejects_packet_functional_overclaim(self):
        self.alter(["compact_thickening", "packet_tree_functional_contrast"], "DeltaC_tree>1/40")

    def test_rejects_thickened_loop_bound(self):
        self.alter(["compact_thickening", "loop_contrast_after_thickening"], "DeltaB_packet>0")

    def test_rejects_complete_contrast_formula(self):
        self.alter(["compact_thickening", "complete_contrast"], "DeltaR6=DeltaB")

    def test_rejects_complete_lower(self):
        self.alter(["compact_thickening", "complete_lower_bound"], "DeltaR6>0")

    def test_rejects_dark_effect(self):
        self.alter(["absolute_dark_port_coefficient", "dark_effect"], "P_minus=I")

    def test_rejects_leading_annihilation(self):
        self.alter(["absolute_dark_port_coefficient", "leading_annihilation"], "P_minus*X2=X2")

    def test_rejects_probability_order(self):
        self.alter(["absolute_dark_port_coefficient", "probability"], "q_dark=lambda^6")

    def test_rejects_Cauchy_factor(self):
        self.alter(["absolute_dark_port_coefficient", "Cauchy_bound"], "Q8/q4>=DeltaR6^2/4")

    def test_rejects_absolute_value(self):
        self.alter(["absolute_dark_port_coefficient", "exact_rational_lower", "exact"], "1/1000000000")

    def test_rejects_absolute_hash(self):
        self.alter(["absolute_dark_port_coefficient", "exact_rational_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_absolute_comparison(self):
        self.alter(["absolute_dark_port_coefficient", "comparison"], "Q8>=0")

    def test_rejects_dark_disposition(self):
        self.alter(["disposition", "absolute_dark_port_q8_probability"], "NOT_COMPUTED")

    def test_rejects_bandwidth_promotion(self):
        self.alter(["disposition", "finite_total_momentum_or_invariant_mass_bandwidth"], "CONSTRUCTED")

    def test_rejects_apparatus_promotion(self):
        self.alter(["disposition", "local_detector_Hamiltonian_for_these_exact_packets"], "CONSTRUCTED")

    def test_rejects_bright_promotion(self):
        self.alter(["disposition", "recorded_or_bright_port_absolute_q8"], "COMPUTED")

    def test_rejects_Eq19_promotion(self):
        self.alter(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.alter(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_rejects_Lorentzian_boundary_removal(self):
        row = self.mutated()
        row["does_not_establish"] = [
            item for item in row["does_not_establish"] if "LORENTZIAN-CAUSAL" not in item
        ]
        self.reject(row)

    def test_rejects_priority_boundary_removal(self):
        row = self.mutated()
        row["does_not_establish"] = [
            item for item in row["does_not_establish"] if item != "literature priority"
        ]
        self.reject(row)


if __name__ == "__main__":
    unittest.main()
