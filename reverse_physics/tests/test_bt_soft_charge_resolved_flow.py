import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics", "certificates", "REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics", "bt_soft_charge_resolved_flow.py")
VERIFIER = os.path.join(ROOT, "reverse_physics", "verify_bt_soft_charge_resolved_flow.py")


class SoftChargeResolvedFlowTests(unittest.TestCase):
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

    def test_charge_mutation(self):
        result = self.mutate(lambda p: p["fixed_vacuum_charge_decomposition"]["logarithmic_rows"][0].update(first_generator_charge=0))
        self.assertNotEqual(result.returncode, 0)

    def test_factorial_mutation(self):
        result = self.mutate(lambda p: p["normalization_ledger_before_charge_projection"]["per_unordered_pair"].update(numerator=1, denominator=16))
        self.assertNotEqual(result.returncode, 0)

    def test_hard_sign_mutation(self):
        result = self.mutate(lambda p: p["normalization_ledger_before_charge_projection"]["absolute_hard_response"].update(numerator=3, denominator=512))
        self.assertNotEqual(result.returncode, 0)

    def test_regulator_mutation(self):
        result = self.mutate(lambda p: p["finite_cutoff_flow"].update(common_rescaling_response="zero"))
        self.assertNotEqual(result.returncode, 0)

    def test_claim_mutation(self):
        result = self.mutate(lambda p: p["disposition"].update(physical_neutral_one_over_48="ESTABLISHED"))
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
