"""Falsification tests for the BT q10 time-normalization obstruction."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT,
    "reverse_physics/bt_fully_rearranged_q10_time_normalization_obstruction.py",
)
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_fully_rearranged_q10_time_normalization_obstruction.py",
)


class Q10TimeNormalizationObstructionTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def assert_rejected(self, mutation):
        result = self.mutate(mutation)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_producer_check(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64
        self.assert_rejected(mutation)

    def test_fixed_total_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"].update(fixed_total_rule="Omega is unconstrained"))

    def test_full_sector_factor_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"].update(exact_factorization="I3=A3"))

    def test_two_vertex_F_coefficient_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"]["two_vertex_series"][4].update(F_T_coefficient_without_i_power={"numerator": 0, "denominator": 1}))

    def test_two_vertex_taper_coefficient_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"]["two_vertex_series"][7].update(anchored_taper_coefficient_without_i_power={"numerator": 1, "denominator": 1}))

    def test_factor_two_witness_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"].update(finite_time_mismatch="A2=F_T"))

    def test_triangle_coefficient_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"]["three_vertex_series"][5].update(anchored_coefficient_without_i_power={"numerator": 0, "denominator": 1}))

    def test_triangle_T_power_mutation_rejected(self):
        self.assert_rejected(lambda value: value["time_normalization_audit"]["three_vertex_series"][2].update(full_power_of_T=4))

    def test_forest_overlap_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bubble_forest_correction"].update(fixed_total_reduction="no overlap taper"))

    def test_old_RG_promotion_rejected(self):
        self.assert_rejected(lambda value: value["bubble_forest_correction"].update(status="FINITE_TIME_RG_IDENTITY_PROVED"))

    def test_one_gap_sign_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_distributional_boundary"].update(one_gap="A2 -> pi*delta(s)-i*PV(1/s)"))

    def test_two_gap_tensor_removal_rejected(self):
        self.assert_rejected(lambda value: value["anchored_distributional_boundary"].update(two_gap="a scalar pointwise limit"))

    def test_three_window_factor_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_distributional_boundary"].update(three_window="W_T -> delta(x+y)"))

    def test_q10_unsuperseded_mutation_rejected(self):
        self.assert_rejected(lambda value: value["supersession_and_retention"].update(q10_selected_packet_assembly="RETAINED"))

    def test_graph_retention_mutation_rejected(self):
        self.assert_rejected(lambda value: value["supersession_and_retention"].update(connected_graph_exhaustion="SUPERSEDED"))

    def test_q8_retention_mutation_rejected(self):
        self.assert_rejected(lambda value: value["supersession_and_retention"].update(leading_all_time_q8="SUPERSEDED"))

    def test_matched_q10_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(matched_finite_time_q10="COMPUTED"))

    def test_all_time_q10_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(all_time_q10="COMPUTED"))

    def test_Eq19_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(general_Eq19="PROVED"))

    def test_causal_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(Lorentzian_causal_claim="ESTABLISHED"))

    def test_boundary_ledger_removal_rejected(self):
        self.assert_rejected(lambda value: value.update(does_not_establish=[]))


if __name__ == "__main__":
    unittest.main()
