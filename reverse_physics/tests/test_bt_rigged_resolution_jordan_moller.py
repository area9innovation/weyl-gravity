"""Falsification tests for the BT rigged resolution-Jordan Moller gate."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_rigged_resolution_jordan_moller.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_rigged_resolution_jordan_moller.py")


class RiggedResolutionJordanMollerTests(unittest.TestCase):
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

    def test_producer(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_axis_value_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_gram"]["axis_value"].update(numerator=4)).returncode, 0)

    def test_log_fixture_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_gram"]["exact_fixtures"][0]["I"]["log_coefficient"].update(denominator=25)).returncode, 0)

    def test_cocycle_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_gram"].update(physical_per_pair_cocycle="log(c)/16")).returncode, 0)

    def test_false_C1_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(ordinary_strong_C1_mass_axis_Moller_column="CONSTRUCTED")).returncode, 0)

    def test_jordan_generator_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["rigged_resolution_jordan"].update(generator="N=[[0,1/4],[0,0]], N^2=0")).returncode, 0)

    def test_false_L2_vector_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(ordinary_L2_resolution_Jordan_vector="CONSTRUCTED")).returncode, 0)

    def test_public_identification_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(public_Rt_equals_physical_S_operator="ESTABLISHED")).returncode, 0)

    def test_full_moller_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(full_physical_Moller_operator="CONSTRUCTED")).returncode, 0)

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(Eq19_all_orders="PROVED")).returncode, 0)


if __name__ == "__main__":
    unittest.main()
