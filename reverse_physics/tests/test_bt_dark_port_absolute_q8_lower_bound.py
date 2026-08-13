"""Falsification tests for the absolute BT dark-port q8 lower bound."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_dark_port_absolute_q8_lower_bound import CERT, verify


class DarkPortAbsoluteQ8LowerBoundTests(unittest.TestCase):
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

    def test_rejects_dependency_tag(self):
        self.alter(["dependency_tags"], ["REDUCED-MODE"])

    def test_rejects_lifecycle_promotion(self):
        self.alter(["lifecycle_state"], "RESIDUAL_TRANSFERRED")

    def test_rejects_dark_projector(self):
        self.alter(["dark_port_ledger", "dark_effect"], "P_minus=I")

    def test_rejects_leading_annihilation(self):
        self.alter(["dark_port_ledger", "leading_annihilation"], "P_minus*X2=X2")

    def test_rejects_probability_order(self):
        self.alter(["dark_port_ledger", "absolute_probability"], "q_dark=lambda^6")

    def test_rejects_q8_norm_factor(self):
        self.alter(["dark_port_ledger", "absolute_q8_coefficient"], "Q8_dark=||DeltaX4||^2")

    def test_rejects_X6_absence(self):
        self.alter(["dark_port_ledger", "X2_X6_disposition"], "UNKNOWN")

    def test_rejects_leading_coefficient(self):
        self.alter(["q6_to_q8_inequality", "per_cell_leading_coefficient"], "q4_bar=2*||x2||^2")

    def test_rejects_q6_relation(self):
        self.alter(["q6_to_q8_inequality", "complete_q6_relation"], "Re=R6")

    def test_rejects_contrast_relation(self):
        self.alter(["q6_to_q8_inequality", "contrast_relation"], "Re=q4_bar*DeltaR6")

    def test_rejects_Cauchy_step(self):
        self.alter(["q6_to_q8_inequality", "Cauchy_step"], "norm2>=0")

    def test_rejects_dark_bound_factor(self):
        self.alter(["q6_to_q8_inequality", "dark_lower_bound"], "Q8_dark/q4_bar>=DeltaR6^2/4")

    def test_rejects_angle(self):
        self.alter(["exact_two_angle_witness", "angles"], ["0", "1/2"])

    def test_rejects_duration(self):
        self.alter(["exact_two_angle_witness", "duration"], "kappa*T=2")

    def test_rejects_tree_lower_value(self):
        self.alter(["exact_two_angle_witness", "tree_contrast_lower_receipt", "exact"], "1/10")

    def test_rejects_tree_lower_hash(self):
        self.alter(["exact_two_angle_witness", "tree_contrast_lower_receipt", "canonical_sha256"], "0" * 64)

    def test_rejects_tree_upper_value(self):
        self.alter(["exact_two_angle_witness", "tree_contrast_upper_receipt", "exact"], "1/100")

    def test_rejects_loop_lower_value(self):
        self.alter(["exact_two_angle_witness", "loop_contrast_lower_receipt", "exact"], "1/10")

    def test_rejects_loop_lower_hash(self):
        self.alter(["exact_two_angle_witness", "loop_contrast_lower_receipt", "canonical_sha256"], "f" * 64)

    def test_rejects_loop_upper_value(self):
        self.alter(["exact_two_angle_witness", "loop_contrast_upper_receipt", "exact"], "1/1000")

    def test_rejects_scheme_cancellation(self):
        self.alter(["exact_two_angle_witness", "scale_and_scheme_dependence"], "UNKNOWN")

    def test_rejects_spectator_norm(self):
        self.alter(["finite_volume_complete_contrast", "spectator_norm"], "N_s=1")

    def test_rejects_complete_contrast_formula(self):
        self.alter(["finite_volume_complete_contrast", "formula"], "DeltaR6=DeltaW+DeltaB")

    def test_rejects_tree_sign(self):
        self.alter(["finite_volume_complete_contrast", "tree_sign"], "UNKNOWN")

    def test_rejects_loop_sign(self):
        self.alter(["finite_volume_complete_contrast", "loop_sign"], "UNKNOWN")

    def test_rejects_pi_bound(self):
        self.alter(["finite_volume_complete_contrast", "pi_bound"], "pi<4")

    def test_rejects_q6_lower(self):
        self.alter(["finite_volume_complete_contrast", "relative_q6_lower_bound"], "DeltaR6>0")

    def test_rejects_absolute_value(self):
        self.alter(["absolute_q8_bound", "exact_rational_lower", "exact"], "1/1000000000")

    def test_rejects_absolute_hash(self):
        self.alter(["absolute_q8_bound", "exact_rational_lower", "canonical_sha256"], "0" * 64)

    def test_rejects_absolute_comparison(self):
        self.alter(["absolute_q8_bound", "comparison"], "Q8_dark>=0")

    def test_rejects_leading_probability(self):
        self.alter(["absolute_q8_bound", "leading_probability"], "q_dark>0")

    def test_rejects_dark_disposition(self):
        self.alter(["disposition", "absolute_dark_port_q8_probability"], "NOT_COMPUTED")

    def test_rejects_recorded_promotion(self):
        self.alter(["disposition", "absolute_recorded_q8_probability"], "COMPUTED")

    def test_rejects_bright_promotion(self):
        self.alter(["disposition", "absolute_bright_port_q8_probability"], "COMPUTED")

    def test_rejects_packet_promotion(self):
        self.alter(["disposition", "compact_continuum_packet_extension"], "CONSTRUCTED")

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
