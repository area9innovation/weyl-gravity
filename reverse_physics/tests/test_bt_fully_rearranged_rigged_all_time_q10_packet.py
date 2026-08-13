"""Falsification tests for the selected rigged all-time BT q10 theorem."""
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
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1.json",
)
PRODUCER = os.path.join(
    ROOT,
    "reverse_physics/bt_fully_rearranged_rigged_all_time_q10_packet.py",
)
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_fully_rearranged_rigged_all_time_q10_packet.py",
)


class RiggedAllTimeQ10PacketTests(unittest.TestCase):
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

    def test_center_time_rule_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"].update(external_time_rule="retain an extra T"))

    def test_one_gap_sign_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"].update(one_gap="pi*delta(s)-i*PV(1/s)"))

    def test_three_window_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"].update(three_window="F_T(x)*F_T(y)"))

    def test_overlap_formula_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"].update(inverse_Fourier_overlap="1"))

    def test_overlap_fixture_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"]["overlap_fixtures"][2].update(normalized_overlap={"numerator": 1, "denominator": 1}))

    def test_L1_tail_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"].update(L1_proof="assumed"))

    def test_two_delta_boundary_mutation_rejected(self):
        self.assert_rejected(lambda value: value["anchored_temporal_limit"].update(boundary="delta(x+y)"))

    def test_mask_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"]["exchange_rows"][4].update(mask=7))

    def test_channel_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"]["exchange_rows"][1].update(exchange_channel=[2, 2]))

    def test_bridge_sign_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"]["exchange_rows"][2].update(canonical_bridge_momentum="q_ia"))

    def test_bridge_invariant_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"]["exchange_rows"][7].update(bridge_invariant={"numerator": 0, "denominator": 1}))

    def test_rotation_numerator_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"]["exchange_rows"][3].update(rotation_numerator_N={"numerator": 0, "denominator": 1}))

    def test_dK2_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"]["exchange_rows"][8].update(partial_t_K_squared={"numerator": 0, "denominator": 1}))

    def test_unique_shell_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"].update(unique_shell_exchange=[0, 0]))

    def test_mask_set_mutation_rejected(self):
        self.assert_rejected(lambda value: value["bridge_chart_audit"].update(mask_set=[7, 11]))

    def test_triangle_coefficient_mutation_rejected(self):
        self.assert_rejected(lambda value: value["all_time_loop_operator"].update(triangle="T6=0"))

    def test_bubble_coefficient_mutation_rejected(self):
        self.assert_rejected(lambda value: value["all_time_loop_operator"].update(bubble_bridge="T6=0"))

    def test_complete_loop_mutation_rejected(self):
        self.assert_rejected(lambda value: value["all_time_loop_operator"].update(complete_loop="triangle only"))

    def test_bridge_coarea_removal_rejected(self):
        self.assert_rejected(lambda value: value["all_time_loop_operator"].update(bridge_distribution="pointwise pole"))

    def test_q10_formula_mutation_rejected(self):
        self.assert_rejected(lambda value: value["q10_packet_coefficient"].update(q10="q10=0"))

    def test_q10_sign_promotion_rejected(self):
        self.assert_rejected(lambda value: value["q10_packet_coefficient"].update(sign="POSITIVE"))

    def test_common_Born_mutation_rejected(self):
        self.assert_rejected(lambda value: value["q10_packet_coefficient"].update(common_Born="not established"))

    def test_RG_coefficient_mutation_rejected(self):
        self.assert_rejected(lambda value: value["renormalization_group"].update(q10_scale_derivative="0"))

    def test_RG_cancellation_mutation_rejected(self):
        self.assert_rejected(lambda value: value["renormalization_group"].update(cancellation="fails"))

    def test_finite_time_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(matched_finite_time_q10="COMPUTED"))

    def test_S_operator_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(Moller_LSZ_S="CONSTRUCTED"))

    def test_Eq19_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(general_Eq19="PROVED"))

    def test_gravity_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(gravity_BV_BRST_QME="CONSTRUCTED"))

    def test_causal_promotion_rejected(self):
        self.assert_rejected(lambda value: value["claim_boundary"].update(Lorentzian_causal_claim="ESTABLISHED"))

    def test_boundary_ledger_removal_rejected(self):
        self.assert_rejected(lambda value: value.update(does_not_establish=[]))


if __name__ == "__main__":
    unittest.main()
