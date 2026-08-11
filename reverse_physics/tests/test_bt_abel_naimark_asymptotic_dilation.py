"""Falsification tests for the BT Abel--Naimark asymptotic dilation."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_abel_naimark_asymptotic_dilation.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_abel_naimark_asymptotic_dilation.py")


class AbelNaimarkAsymptoticDilationTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT) as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_abel_sign_mutation(self):
        result = self.mutate(
            lambda value: value["abel_time_intertwiner"]["coefficient_fixtures"][0]
            ["lowering_coefficient"]["real"].update(numerator=1)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_logistic_norm_mutation(self):
        result = self.mutate(
            lambda value: value["abel_time_intertwiner"]["coefficient_fixtures"][1]
            ["logistic_profile_value"].update(denominator=6)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_coherent_distance_mutation(self):
        result = self.mutate(
            lambda value: value["coherent_limit_obstruction"]["scale_fixtures"][0]
            ["coherent_coefficient_of_logc"].update(numerator=1, denominator=2)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_false_strong_limit_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(
                ordinary_strong_Abel_wave_column_limit="CONSTRUCTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_naimark_marginal_mutation(self):
        result = self.mutate(
            lambda value: value["naimark_probability_dilation"].update(
                detector_marginal="integral p_s ds=q_R"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_physical_density_mutation(self):
        result = self.mutate(
            lambda value: value["naimark_probability_dilation"]["real_norm_square"].update(
                denominator=15
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_operator_identification_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(
                public_Rt_equals_physical_S_operator="ESTABLISHED"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_eq19_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
