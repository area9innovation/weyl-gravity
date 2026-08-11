import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_DETECTOR_PUSHFORWARD_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_finite_detector_pushforward.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_finite_detector_pushforward.py")


class FiniteDetectorPushforwardTests(unittest.TestCase):
    def run_command(self, command):
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutation(payload)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(payload, handle)
            handle.flush()
            return self.run_command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self):
        self.assertEqual(self.run_command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_verifier(self):
        self.assertEqual(self.run_command([sys.executable, VERIFIER]).returncode, 0)

    def test_amplitude_mutation(self):
        result = self.mutate(lambda payload: payload["finite_detector_model"]["per_cell_amplitude_squared"].update(numerator=2))
        self.assertNotEqual(result.returncode, 0)

    def test_projector_mutation(self):
        result = self.mutate(lambda payload: payload["finite_detector_model"]["fixture_P2"][0][0]["rational"].update(numerator=-2))
        self.assertNotEqual(result.returncode, 0)

    def test_trace_norm_mutation(self):
        result = self.mutate(lambda payload: payload["finite_detector_model"]["exact_rows"][4]["P1_trace_norm_squared"].update(numerator=4))
        self.assertNotEqual(result.returncode, 0)

    def test_charge_mutation(self):
        result = self.mutate(lambda payload: payload["zero_mode_and_charge"]["completed_generator_charge_pairs"][0].__setitem__(0, 1))
        self.assertNotEqual(result.returncode, 0)

    def test_squeeze_mutation(self):
        result = self.mutate(lambda payload: payload["weighted_squeeze_test"]["one_pair_excited_positive_norm_squared"].update(numerator=79))
        self.assertNotEqual(result.returncode, 0)

    def test_trace_limit_promotion_mutation(self):
        result = self.mutate(lambda payload: payload["disposition"].update(uniform_soft_trace_class_limit="ESTABLISHED"))
        self.assertNotEqual(result.returncode, 0)

    def test_eq19_promotion_mutation(self):
        result = self.mutate(lambda payload: payload["disposition"].update(Eq19="REPRODUCED"))
        self.assertNotEqual(result.returncode, 0)

    def test_physical_promotion_mutation(self):
        result = self.mutate(lambda payload: payload["disposition"].update(physical_neutral_one_over_48="ESTABLISHED"))
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
