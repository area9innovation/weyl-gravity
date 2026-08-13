import copy
import json
import os
import unittest

from reverse_physics.verify_bt_local_quadrupole_dark_detector_q8 import (
    CERT_REL,
    ROOT,
    verify,
)


class LocalQuadrupoleDarkDetectorQ8Tests(unittest.TestCase):
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

    def assert_rejected(self, mutation):
        row = copy.deepcopy(self.certificate)
        mutation(row)
        self.assertFalse(all(verify(row).values()))

    def alter(self, path, value):
        self.assert_rejected(lambda row: self.set_path(row, path, value))

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [name for name, ok in checks.items() if not ok])

    def test_rejects_identity(self):
        self.alter(["certificate"], "PROMOTED")

    def test_rejects_dependency_promotion(self):
        self.alter(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.alter(["provenance", "inputs", 1, "sha256"], "0" * 64)

    def test_rejects_missing_input(self):
        self.alter(["provenance", "inputs", 2, "path"], "missing.json")

    def test_rejects_symbol_trace_sign(self):
        self.alter(["local_quadrupole_density", "symbol"], "F2=traceful")

    def test_rejects_derivative_order(self):
        self.alter(["local_quadrupole_density", "derivative_order"], 2)

    def test_rejects_central_reduction(self):
        self.alter(["local_quadrupole_density", "central_reduction"], "F2=1")

    def test_rejects_boosted_mean(self):
        self.alter(["local_quadrupole_density", "rational_boosted_values", 0], "1")

    def test_rejects_non_even_symbol(self):
        self.alter(["local_quadrupole_density", "reality_and_exchange"], "odd under exchange")

    def test_rejects_tree_lower_hash(self):
        self.alter(["exact_P2_moments", "tree_interval", "lower", "canonical_sha256"], "0" * 64)

    def test_rejects_tree_lower_value(self):
        self.alter(["exact_P2_moments", "tree_interval", "lower", "exact"], "0")

    def test_rejects_tree_upper_hash(self):
        self.alter(["exact_P2_moments", "tree_interval", "upper", "canonical_sha256"], "f" * 64)

    def test_rejects_tree_upper_value(self):
        self.alter(["exact_P2_moments", "tree_interval", "upper", "exact"], "0")

    def test_rejects_tree_sign(self):
        self.alter(["exact_P2_moments", "tree_simple_lower"], "J_tree<0")

    def test_rejects_loop_hash(self):
        self.alter(["exact_P2_moments", "loop_lower_partial", "canonical_sha256"], "0" * 64)

    def test_rejects_loop_value(self):
        self.alter(["exact_P2_moments", "loop_lower_partial", "exact"], "1/400")

    def test_rejects_loop_bound(self):
        self.alter(["exact_P2_moments", "loop_simple_lower"], "J_loop<0")

    def test_rejects_complete_moment(self):
        self.alter(["exact_P2_moments", "complete_relative_moment"], "J_R=0")

    def test_rejects_legendre_integrals(self):
        self.alter(["local_detector_probability", "Legendre_integrals"], "int P2=1")

    def test_rejects_cauchy_factor(self):
        self.alter(["local_detector_probability", "Cauchy_factor"], "factor=1/8")

    def test_rejects_central_lower_hash(self):
        self.alter(["local_detector_probability", "central_relative_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_central_lower_value(self):
        self.alter(["local_detector_probability", "central_relative_lower", "exact"], "1/100")

    def test_rejects_bandwidth_hash(self):
        self.alter(["local_detector_probability", "finite_bandwidth_relative_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_bandwidth_value(self):
        self.alter(["local_detector_probability", "finite_bandwidth_relative_lower", "exact"], "1/19200")

    def test_rejects_dark_hash(self):
        self.alter(["local_detector_probability", "exact_rational_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_dark_value(self):
        self.alter(["local_detector_probability", "exact_rational_lower", "exact"], "0")

    def test_rejects_nonvacuum_outcome(self):
        self.alter(["local_detector_probability", "selected_outcome"], "pointer only")

    def test_rejects_RWA_deletion(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "without the selected final field-vacuum outcome" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_joint_order(self):
        self.alter(["local_detector_probability", "joint_expansion"], "p=lambda^8")

    def test_rejects_continuity_loss(self):
        self.alter(["local_detector_probability", "finite_bandwidth_argument"], "central fibre only")

    def test_rejects_compact_support_promotion(self):
        self.alter(["disposition", "compact_spacetime_support"], "PROVED")

    def test_rejects_detector_all_orders_promotion(self):
        self.alter(["disposition", "all_orders_in_external_detector_coupling"], "PROVED")

    def test_rejects_Eq19_promotion(self):
        self.alter(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.alter(["disposition", "gravity_or_metric_BV_BRST_transfer"], "PROVED")

    def test_rejects_Lorentzian_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "LORENTZIAN-CAUSAL" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_priority_claim(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if item != "literature priority"
            ]
        self.assert_rejected(mutate)


if __name__ == "__main__":
    unittest.main()
