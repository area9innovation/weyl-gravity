"""Falsification tests for the finite BT three-jump Krein--Moller jet."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_three_jump_krein_moller_jet.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_three_jump_krein_moller_jet.py")


class ThreeJumpKreinMollerJetTests(unittest.TestCase):
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

    def test_producer_fast_check(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_ladder_weight_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["unique_ladder_factorization"]["edge_amplitudes"].__setitem__(1, "sqrt(10)/7")).returncode, 0)

    def test_rate_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["unique_ladder_factorization"]["extension_rate_squares"][2].update(numerator=26)).returncode, 0)

    def test_generator_hash_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["krein_skew_generator"].update(sparse_entry_sha256="0" * 64)).returncode, 0)

    def test_rank_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["krein_skew_generator"].update(rank=50)).returncode, 0)

    def test_aggregate_probability_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["physical_moller_column"]["aggregate_leading_probabilities"][2].update(numerator=8)).returncode, 0)

    def test_additive_generator_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["disposition"].update(additive_resolution_strong_generator="CONSTRUCTED")).returncode, 0)

    def test_all_order_hamiltonian_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["disposition"].update(all_order_BT_asymptotic_hamiltonian="CONSTRUCTED")).returncode, 0)

    def test_fourth_jump_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["disposition"].update(fourth_jump="COMPUTED")).returncode, 0)

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["disposition"].update(Eq19_all_orders="PROVED")).returncode, 0)

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value.update(does_not_establish=[])).returncode, 0)

    def test_input_hash_mutation(self):
        self.assertNotEqual(self.mutate(lambda value: value["provenance"]["inputs"][0].update(sha256="0" * 64)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
