"""Falsification tests for the BT detector-resolution dilation theorem."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_detector_resolution_dilation.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_detector_resolution_dilation.py")


class DetectorResolutionDilationTests(unittest.TestCase):
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

    def test_smooth_trace_mutation(self):
        result = self.mutate(
            lambda value: value["profile_fixtures"]["cubic_smoothstep"]["unit_shift_density"][0]["integral"].update(denominator=3)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_smooth_polynomial_mutation(self):
        result = self.mutate(
            lambda value: value["profile_fixtures"]["cubic_smoothstep"]["unit_shift_density"][1]["density_coefficients_ascending"][0].update(numerator=-3)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_real_coefficient_mutation(self):
        result = self.mutate(
            lambda value: value["physical_response"]["real_per_pair_born_normalized_per_unit_a"].update(denominator=47)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_hard_sign_mutation(self):
        result = self.mutate(
            lambda value: value["physical_response"]["hard_survival_born_normalized_per_unit_a"].update(numerator=1)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_time_hamiltonian_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(time_asymptotic_Hamiltonian="CONSTRUCTED")
        )
        self.assertNotEqual(result.returncode, 0)

    def test_aqft_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(spacetime_local_LSZ_or_AQFT_affiliation="ESTABLISHED")
        )
        self.assertNotEqual(result.returncode, 0)

    def test_eq19_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
