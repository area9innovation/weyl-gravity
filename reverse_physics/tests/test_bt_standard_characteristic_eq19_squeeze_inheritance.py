"""Falsification tests for the standard n=3 Eq. 19 squeeze inheritance result."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_standard_characteristic_eq19_squeeze_inheritance.py"
)
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_standard_characteristic_eq19_squeeze_inheritance.py",
)


class StandardCharacteristicEq19SqueezeInheritanceTests(unittest.TestCase):
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

    def test_producer_check(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_particle_number_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["standard_characteristic_normalization"].update(particle_number=2)).returncode,
            0,
        )

    def test_species_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["standard_characteristic_normalization"].update(active_species_rank=6)).returncode,
            0,
        )

    def test_positive_tangent_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["homogeneous_charge_inheritance"]["s_less_than_one"].update(positive_component_rank=0)).returncode,
            0,
        )

    def test_odd_norm_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["homogeneous_charge_inheritance"]["s_equal_one"].update(ghost_odd_relative_norm="0")).returncode,
            0,
        )

    def test_fixture_norm_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["homogeneous_charge_inheritance"]["s_equal_one"].update(finite_box_ghost_odd_relative_norm="0")).returncode,
            0,
        )

    def test_support_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["homogeneous_charge_inheritance"]["s_equal_one"]["ghost_odd_support_ranks"].update({"2": 0})).returncode,
            0,
        )

    def test_s_greater_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["homogeneous_charge_inheritance"]["s_greater_than_one"].update(positive_free_component_ranks=[0, 0])).returncode,
            0,
        )

    def test_public_q10_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["q10_transport_disposition"].update(public_one_sheet_result="Q10_MATCH_PROVED")).returncode,
            0,
        )

    def test_doubled_trace_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["canonical_doubled_completion"].update(raw_finite_n3_trace=8)).returncode,
            0,
        )

    def test_doubled_public_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["canonical_doubled_completion"].update(status="PUBLIC_BT_EQ19_PROVED")).returncode,
            0,
        )

    def test_time_independence_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["minimality_and_boundary"].update(time_independence="PROVED")).returncode,
            0,
        )

    def test_continuum_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["minimality_and_boundary"].update(continuum_trace_domain="PROVED")).returncode,
            0,
        )

    def test_boundary_removal_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64

        self.assertNotEqual(self.mutate(mutation).returncode, 0)


if __name__ == "__main__":
    unittest.main()
