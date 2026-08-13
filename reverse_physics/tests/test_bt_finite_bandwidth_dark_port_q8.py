import copy
import json
import os
import unittest

from reverse_physics.verify_bt_finite_bandwidth_dark_port_q8 import (
    CERT_REL,
    ROOT,
    verify,
)


class FiniteBandwidthDarkPortQ8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        row = copy.deepcopy(self.certificate)
        mutation(row)
        self.assertFalse(all(verify(row).values()))

    @staticmethod
    def set_path(row, path, value):
        cursor = row
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    def alter(self, path, value):
        self.assert_rejected(lambda row: self.set_path(row, path, value))

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [name for name, ok in checks.items() if not ok])

    def test_rejects_certificate_identity(self):
        self.alter(["certificate"], "PROMOTED")

    def test_rejects_dependency_tag_promotion(self):
        self.alter(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.alter(["provenance", "inputs", 1, "sha256"], "0" * 64)

    def test_rejects_missing_predecessor(self):
        self.alter(["provenance", "inputs", 1, "path"], "missing.json")

    def test_rejects_Dyson_coefficient(self):
        self.alter(["off_diagonal_temporal_kernel", "coefficient_check", 7, "coefficient_without_i_power"], "1/2")

    def test_rejects_Dyson_multiplicity(self):
        self.alter(["off_diagonal_temporal_kernel", "coefficient_check", 8, "multiplicity"], 1)

    def test_rejects_tree_Dyson_conflation(self):
        self.alter(["off_diagonal_temporal_kernel", "ordered_Dyson_integral"], "f(x)=tree")

    def test_rejects_divided_difference(self):
        self.alter(["off_diagonal_temporal_kernel", "divided_difference"], "d=f")

    def test_rejects_interference_normalization(self):
        self.alter(["off_diagonal_temporal_kernel", "interference_kernel"], "k=Im(d)")

    def test_rejects_closed_form_sign(self):
        self.alter(["off_diagonal_temporal_kernel", "closed_form"], "k=[1+cos]/(y-x)")

    def test_rejects_diagonal_kernel(self):
        self.alter(["off_diagonal_temporal_kernel", "energy_diagonal"], "k(0,y)=1/y")

    def test_rejects_nonremovable_resonance(self):
        self.alter(["off_diagonal_temporal_kernel", "resonant_values"], "singular")

    def test_rejects_sinc_value(self):
        self.alter(["off_diagonal_temporal_kernel", "sinc_floor", "exact"], "1")

    def test_rejects_sinc_hash(self):
        self.alter(["off_diagonal_temporal_kernel", "sinc_floor", "canonical_sha256"], "0" * 64)

    def test_rejects_uv_constant(self):
        self.alter(["ultraviolet_and_continuity", "uv_constant", "exact"], "6")

    def test_rejects_uv_hash(self):
        self.alter(["ultraviolet_and_continuity", "uv_constant", "canonical_sha256"], "f" * 64)

    def test_rejects_uv_power_loss(self):
        self.alter(["ultraviolet_and_continuity", "uv_difference_bound"], "O(1/y)")

    def test_rejects_new_counterterm(self):
        self.alter(["ultraviolet_and_continuity", "counterterm"], "introduce a mismatch counterterm")

    def test_rejects_conditional_uv_tail(self):
        self.alter(["ultraviolet_and_continuity", "absolute_convergence"], "oscillatory only")

    def test_rejects_dropped_cut(self):
        self.alter(["ultraviolet_and_continuity", "cut_boundary"], "discard the absorptive sector")

    def test_rejects_zero_direct_integral_measure(self):
        self.alter(["finite_bandwidth_packet", "measure"], "zero measure")

    def test_rejects_distributional_packet(self):
        self.alter(["finite_bandwidth_packet", "normalizability"], "delta distribution")

    def test_rejects_nonfibrewise_dark_cancellation(self):
        self.alter(["finite_bandwidth_packet", "leading_symmetry"], "cancels at the center only")

    def test_rejects_fabricated_radius(self):
        self.alter(["finite_bandwidth_packet", "radius_status"], "RADIUS_EQUALS_1_OVER_100")

    def test_rejects_retained_contrast(self):
        self.alter(["absolute_dark_port_coefficient", "retained_q6_lower", "exact"], "49/534336")

    def test_rejects_retained_hash(self):
        self.alter(["absolute_dark_port_coefficient", "retained_q6_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_dark_lower(self):
        self.alter(["absolute_dark_port_coefficient", "exact_rational_lower", "exact"], "0")

    def test_rejects_dark_hash(self):
        self.alter(["absolute_dark_port_coefficient", "exact_rational_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_numeric_bandwidth_promotion(self):
        self.alter(["disposition", "numerical_bandwidth_radius"], "COMPUTED")

    def test_rejects_local_apparatus_promotion(self):
        self.alter(["disposition", "local_detector_for_the_fibrewise_projector"], "CONSTRUCTED")

    def test_rejects_Eq19_promotion(self):
        self.alter(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.alter(["disposition", "gravity_or_metric_BV_BRST_transfer"], "PROVED")

    def test_rejects_Lorentzian_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"] if "LORENTZIAN-CAUSAL" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_priority_claim(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"] if item != "literature priority"
            ]
        self.assert_rejected(mutate)


if __name__ == "__main__":
    unittest.main()
