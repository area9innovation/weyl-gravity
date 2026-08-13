import copy
import json
import os
import unittest

from reverse_physics.verify_bt_compact_spacetime_quadrupole_dark_detector_q8 import (
    CERT_REL,
    ROOT,
    verify,
)


class CompactSpacetimeQuadrupoleDarkDetectorQ8Tests(unittest.TestCase):
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
        checks = verify(row)
        self.assertFalse(all(checks.values()), checks)

    def alter(self, path, value):
        self.assert_rejected(lambda row: self.set_path(row, path, value))

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [k for k, v in checks.items() if not v])

    def test_rejects_identity(self):
        self.alter(["certificate"], "PROMOTED")

    def test_rejects_dependency_promotion(self):
        self.alter(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.alter(["provenance", "inputs", 1, "sha256"], "0" * 64)

    def test_rejects_missing_input(self):
        self.alter(["provenance", "inputs", 2, "path"], "missing.json")

    def test_rejects_noncompact_cutoff(self):
        self.alter(["compact_cutoff_sequence", "cutoff"], "chi=1")

    def test_rejects_sequence_change(self):
        self.alter(["compact_cutoff_sequence", "sequence"], "h_R=h0")

    def test_rejects_support_change(self):
        self.alter(["compact_cutoff_sequence", "support"], "global")

    def test_rejects_noncompact_quadratures(self):
        self.alter(["compact_cutoff_sequence", "Hermitian_realization"], "complex")

    def test_rejects_bad_leibniz_bound(self):
        self.alter(["compact_cutoff_sequence", "Leibniz_bound"], "grows with R")

    def test_rejects_compact_Fourier_promotion(self):
        self.alter(["compact_cutoff_sequence", "Fourier_statement"], "compact Fourier support")

    def test_rejects_tree_input(self):
        self.alter(["tempered_response_gate", "tree_input"], "pointwise tree")

    def test_rejects_endpoint_model(self):
        self.alter(["tempered_response_gate", "loop_endpoint_model"], "pole")

    def test_rejects_log_integral(self):
        self.alter(["tempered_response_gate", "log_integral"], "diverges")

    def test_rejects_growth_bound(self):
        self.alter(["tempered_response_gate", "growth"], "exponential growth")

    def test_rejects_tempered_functional(self):
        self.alter(["tempered_response_gate", "functional"], "formal")

    def test_rejects_continuity_consequence(self):
        self.alter(["tempered_response_gate", "continuity_consequence"], "R=infinity")

    def test_rejects_leading_identity(self):
        self.alter(["exact_darkness_and_probability", "leading_identity"], "A2 is small")

    def test_rejects_fibrewise_reason(self):
        self.alter(["exact_darkness_and_probability", "reason"], "central fibre only")

    def test_rejects_amplitude_retention(self):
        self.alter(["exact_darkness_and_probability", "amplitude_retention"], "nonnegative")

    def test_rejects_imported_hash(self):
        self.alter(["exact_darkness_and_probability", "imported_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_imported_value(self):
        self.alter(["exact_darkness_and_probability", "imported_lower", "exact"], "0")

    def test_rejects_compact_hash(self):
        self.alter(["exact_darkness_and_probability", "compact_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_compact_value(self):
        self.alter(["exact_darkness_and_probability", "compact_lower", "exact"], "1/20000000000")

    def test_rejects_comparison(self):
        self.alter(["exact_darkness_and_probability", "comparison"], "Q8=0")

    def test_rejects_joint_order(self):
        self.alter(["exact_darkness_and_probability", "joint_expansion"], "p=lambda^8")

    def test_rejects_numeric_radius_promotion(self):
        self.alter(["disposition", "finite_support_radius"], "R0=1")

    def test_rejects_Fourier_tail_deletion(self):
        self.alter(["disposition", "Fourier_support"], "COMPACT")

    def test_rejects_pAQFT_promotion(self):
        self.alter(["disposition", "causal_pAQFT_observable"], "CONSTRUCTED")

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
