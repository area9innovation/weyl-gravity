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
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics", "bt_zero_mode_eq19_trilemma.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics", "verify_bt_zero_mode_eq19_trilemma.py"
)


class ZeroModeEq19TrilemmaTests(unittest.TestCase):
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

    def test_Z_exponent_mutation(self):
        result = self.mutate(
            lambda payload: payload["dressed_quadratic_kernel"]["rows"][0]
            .update(required_Z_exponent=0)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_quotient_remainder_mutation(self):
        result = self.mutate(
            lambda payload: payload["fixed_vacuum_quotient_obstruction"]
            ["remainder_mod_I"].update(numerator=0)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_squeeze_charge_mutation(self):
        result = self.mutate(
            lambda payload: payload["appendix_C_zero_mode_completion"].update(
                covariant_squeeze_charge=-2
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_soft_coefficient_mutation(self):
        result = self.mutate(
            lambda payload: payload["neutral_soft_block"]
            ["per_unordered_pair"].update(denominator=16)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_claim_mutation(self):
        result = self.mutate(
            lambda payload: payload["disposition"].update(
                physical_neutral_one_over_48="ESTABLISHED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
