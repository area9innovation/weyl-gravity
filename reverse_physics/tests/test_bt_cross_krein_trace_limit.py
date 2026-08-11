import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics", "bt_cross_krein_trace_limit.py")
VERIFIER = os.path.join(
    ROOT, "reverse_physics", "verify_bt_cross_krein_trace_limit.py"
)


class CrossKreinTraceLimitTests(unittest.TestCase):
    def run_command(self, command):
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutation(payload)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(payload, handle)
            handle.flush()
            return self.run_command(
                [sys.executable, VERIFIER, "--verify", handle.name]
            )

    def test_producer(self):
        self.assertEqual(
            self.run_command([sys.executable, PRODUCER, "--check"]).returncode,
            0,
        )

    def test_verifier(self):
        self.assertEqual(
            self.run_command([sys.executable, VERIFIER]).returncode,
            0,
        )

    def test_orbit_fundamental_symmetry_mutation(self):
        result = self.mutate(
            lambda payload: payload["orbit_Krein_completion"]["exact_rows"][0]
            .update(J_image_index=99)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_cross_krein_core_mutation(self):
        result = self.mutate(
            lambda payload: payload["cross_Krein_squeeze_core"].update(
                operator_status="BOUNDED_UNITARY"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_finite_rank_trace_mutation(self):
        result = self.mutate(
            lambda payload: payload["finite_rank_Born_trace"].update(
                disposition="TRACE_ON_ALL_BOUNDED_OPERATORS"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_normalized_trace_bound_mutation(self):
        result = self.mutate(
            lambda payload: payload["normalized_trace_extension_no_go"]
            ["translate_bounds"][3]
            ["common_rank_one_weight_upper_bound_if_tau_identity_is_one"]
            .update(denominator=1)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_exact_density_mutation(self):
        result = self.mutate(
            lambda payload: payload["thermodynamic_trace_norm_barrier"]
            ["gamma_half_coefficient_times_mu_cubed_over_pi"]
            ["coefficients"][3]
            .update(denominator=8)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_trace_norm_limit_mutation(self):
        result = self.mutate(
            lambda payload: payload["thermodynamic_trace_norm_barrier"].update(
                disposition="NORMAL_LIMIT_CONSTRUCTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_physical_claim_mutation(self):
        result = self.mutate(
            lambda payload: payload["disposition"].update(
                physical_neutral_one_over_48="ESTABLISHED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
