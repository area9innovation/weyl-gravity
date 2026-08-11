"""Falsification tests for the BT physical collinear operator certificate."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_physical_collinear_operator_factorization.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_physical_collinear_operator_factorization.py")


class PhysicalCollinearOperatorTests(unittest.TestCase):
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

    def test_L_sign_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["amplitude_factorization"].update(L="+(a0-a1)^2/(4*tau)")).returncode, 0)

    def test_Q_fixture_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["amplitude_factorization"]["exact_fixtures"][0]["twice_Q"].update(numerator=92)).returncode, 0)

    def test_physical_rank_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["public_Rt_comparison"].update(physical_gram_rank=1)).returncode, 0)

    def test_public_jordan_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["public_Rt_comparison"].update(minimal_polynomial="x-2")).returncode, 0)

    def test_normalization_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["normalization_ledger"]["combined_ratio"].update(denominator=16)).returncode, 0)

    def test_public_identification_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(public_D_equals_physical_splitting="IDENTIFIED")).returncode, 0)

    def test_full_moller_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(full_physical_Moller_operator="CONSTRUCTED")).returncode, 0)

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(Eq19_all_orders="PROVED")).returncode, 0)


if __name__ == "__main__":
    unittest.main()
