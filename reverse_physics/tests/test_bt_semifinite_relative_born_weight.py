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
    "REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics", "bt_semifinite_relative_born_weight.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics", "verify_bt_semifinite_relative_born_weight.py"
)


class SemifiniteRelativeBornWeightTests(unittest.TestCase):
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

    def test_identity_weight_mutation(self):
        result = self.mutate(
            lambda payload: payload["semifinite_orbit_trace"].update(
                identity_weight="Tau(1)=1"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_relative_traciality_mutation(self):
        result = self.mutate(
            lambda payload: payload["relative_detector_state"]
            ["traciality_counterexample"]["omega_YX"].update(numerator=1)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_conditional_weight_mutation(self):
        result = self.mutate(
            lambda payload: payload["conditional_Born_theorem"]
            ["rational_partition_fixture"]["process_weights"][1].update(
                numerator=15
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_weak_null_mutation(self):
        result = self.mutate(
            lambda payload: payload["conditional_Born_theorem"]
            ["weak_null_fixture"]["Tr_Cdagger_C"].update(numerator=1)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_thermodynamic_promotion_mutation(self):
        result = self.mutate(
            lambda payload: payload["disposition"].update(
                thermodynamic_normal_state="CONSTRUCTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_physical_promotion_mutation(self):
        result = self.mutate(
            lambda payload: payload["disposition"].update(
                physical_neutral_one_over_48="ESTABLISHED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
