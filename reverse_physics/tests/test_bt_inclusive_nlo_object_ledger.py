"""Falsification tests for the BT inclusive NLO object ledger."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_inclusive_nlo_object_ledger.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_inclusive_nlo_object_ledger.py")


class InclusiveNloObjectLedgerTests(unittest.TestCase):
    def run_command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT) as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.run_command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self):
        self.assertEqual(self.run_command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.run_command([sys.executable, VERIFIER]).returncode, 0)

    def test_real_response_mutation(self):
        result = self.mutate(lambda value: value["object_types"]["physical_process"]["real_pair_absolute_response"].update(numerator=2))
        self.assertNotEqual(result.returncode, 0)

    def test_normalization_mutation(self):
        result = self.mutate(lambda value: value["object_types"]["physical_process"]["real_pair_Born_normalized"].update(denominator=47))
        self.assertNotEqual(result.returncode, 0)

    def test_Rt_response_mutation(self):
        result = self.mutate(lambda value: value["combined_ledger"]["nonphysical_Rt_comparison_response"].update(numerator=-3, denominator=512))
        self.assertNotEqual(result.returncode, 0)

    def test_object_conflation_mutation(self):
        result = self.mutate(lambda value: value["object_types"]["physical_process"].update(symbol="R_t P R_t^dagger"))
        self.assertNotEqual(result.returncode, 0)

    def test_correction_erasure_mutation(self):
        result = self.mutate(lambda value: value["correction"].update(status="CONFIRMED"))
        self.assertNotEqual(result.returncode, 0)

    def test_probability_promotion_mutation(self):
        result = self.mutate(lambda value: value["disposition"].update(physical_inclusive_NLO_probability="ESTABLISHED"))
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
