"""Falsification tests for the BT resolution-local coherent Born process."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_resolution_local_coherent_born_process.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_resolution_local_coherent_born_process.py")


class ResolutionLocalCoherentBornTests(unittest.TestCase):
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

    def test_pair_rate_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["probability_law"]["per_pair_rate"].update(denominator=16)).returncode, 0)

    def test_species_rank_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["rank_two_GNS_purification"].update(minimal_rank=1)).returncode, 0)

    def test_vacuum_rate_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["probability_law"].update(hard_no_emission_probability="P_0(a)=exp(-a/48)")).returncode, 0)

    def test_fixture_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["probability_law"]["exact_fixtures"][0]["total_mean"].update(denominator=48)).returncode, 0)

    def test_false_global_implementer_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["global_representation_boundary"].update(conclusion="GLOBAL_FOCK_IMPLEMENTER_EXISTS")).returncode, 0)

    def test_coherent_assumption_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(actual_BT_nonlinear_multiple_emission_dynamics="PROVED_COHERENT")).returncode, 0)

    def test_spacetime_S_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(spacetime_local_physical_S_matrix="CONSTRUCTED")).returncode, 0)

    def test_public_identification_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(public_Rt_equals_physical_S_operator="ESTABLISHED")).returncode, 0)

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(Eq19_all_orders="PROVED")).returncode, 0)


if __name__ == "__main__":
    unittest.main()
