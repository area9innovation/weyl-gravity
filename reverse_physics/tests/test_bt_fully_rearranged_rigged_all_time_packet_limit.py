"""Falsification tests for the BT rigged all-time packet-limit theorem."""
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
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json",
)
PRODUCER = os.path.join(
    ROOT,
    "reverse_physics/bt_fully_rearranged_rigged_all_time_packet_limit.py",
)
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_fully_rearranged_rigged_all_time_packet_limit.py",
)


class RiggedAllTimePacketLimitTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(
            argv, cwd=ROOT, capture_output=True, text=True
        )

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command(
                [sys.executable, VERIFIER, "--verify", handle.name]
            )

    def assert_rejected(self, mutation):
        self.assertNotEqual(self.mutate(mutation).returncode, 0)

    def test_producer_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(
            self.command([sys.executable, VERIFIER]).returncode, 0
        )

    def test_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64

        self.assert_rejected(mutation)

    def test_channel_row_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["exact_chart_phase_audit"]["rows"][4].update(
                q_squared={"numerator": 0, "denominator": 1}
            )
        )

    def test_rotation_numerator_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["exact_chart_phase_audit"]["rows"][7].update(
                rotation_numerator_N={"numerator": 0, "denominator": 1}
            )
        )

    def test_unique_shell_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["exact_chart_phase_audit"].update(
                unique_shell=[0, 0]
            )
        )

    def test_common_coordinate_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["exact_chart_phase_audit"].update(
                common_coordinate="an assumed channel-dependent coordinate"
            )
        )

    def test_delta_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["half_line_distribution"].update(
                tempered_boundary="pi*delta(s)-i*PV(1/s)"
            )
        )

    def test_pointwise_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["half_line_distribution"].update(
                pointwise_boundary="POINTWISE_LIMIT_EXISTS"
            )
        )

    def test_even_Gaussian_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["half_line_distribution"][
                "even_Gaussian_fixture"
            ]["coefficients"][3].update(
                coefficient={"numerator": 0, "denominator": 1}
            )
        )

    def test_odd_Gaussian_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["half_line_distribution"][
                "odd_Gaussian_fixture"
            ]["coefficients"][0].update(
                coefficient={"numerator": -1, "denominator": 4}
            )
        )

    def test_tail_removal_rejected(self):
        self.assert_rejected(
            lambda value: value["half_line_distribution"].update(
                tail_bound="no uniform bound"
            )
        )

    def test_domain_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["rigged_packet_limit"].update(
                domain="all of L2 with the operator norm"
            )
        )

    def test_coarea_Jacobian_removal_rejected(self):
        self.assert_rejected(
            lambda value: value["rigged_packet_limit"].update(
                channel_coarea_density="g=F"
            )
        )

    def test_leading_coefficient_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["rigged_packet_limit"].update(
                leading_coefficient="q8=0"
            )
        )

    def test_strictness_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["rigged_packet_limit"].update(
                strict_nontriviality="not established"
            )
        )

    def test_probability_limit_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["rigged_packet_limit"].update(
                probability_limit="diverges"
            )
        )

    def test_bounded_operator_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["operator_and_claim_boundary"].update(
                bounded_L2_operator_extension="PROVED"
            )
        )

    def test_Moller_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["operator_and_claim_boundary"].update(
                strong_Moller_operator="CONSTRUCTED"
            )
        )

    def test_q10_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["operator_and_claim_boundary"].update(
                q10_all_time_limit="COMPUTED"
            )
        )

    def test_Eq19_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["operator_and_claim_boundary"].update(
                general_Eq19="PROVED"
            )
        )

    def test_boundary_removal_rejected(self):
        self.assert_rejected(
            lambda value: value.update(does_not_establish=[])
        )


if __name__ == "__main__":
    unittest.main()
