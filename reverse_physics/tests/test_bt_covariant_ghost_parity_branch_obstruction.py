"""Falsification tests for the BT covariant ghost-parity branch result."""
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
    "REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_covariant_ghost_parity_branch_obstruction.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_covariant_ghost_parity_branch_obstruction.py"
)


class CovariantGhostParityBranchTests(unittest.TestCase):
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

    def test_gram_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["finite_resonant_block"]["gram"][0].__setitem__(1, "0")
        ).returncode, 0)

    def test_daughter_map_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["finite_resonant_block"]["daughter_to_parent_map"][0].__setitem__(1, "-1/12")
        ).returncode, 0)

    def test_generator_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["finite_resonant_block"]["K_plus"][0].__setitem__(3, "0")
        ).returncode, 0)

    def test_projector_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["finite_resonant_block"]["P0"][1].__setitem__(1, "0")
        ).returncode, 0)

    def test_tangent_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["finite_resonant_block"]["commutator_K_plus_P0"][0].__setitem__(3, "0")
        ).returncode, 0)

    def test_public_laurent_branch_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["public_branch_obstruction"]["public_first_coefficient"].update(
                {"1": value["public_branch_obstruction"]["public_first_coefficient"].pop("-1")}
            )
        ).returncode, 0)

    def test_conjugate_branch_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["public_branch_obstruction"]["ghost_conjugate_first_coefficient"]["1"][0].__setitem__(2, "0")
        ).returncode, 0)

    def test_ghost_defect_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["public_branch_obstruction"]["ghost_defect"]["-1"][0].__setitem__(3, "0")
        ).returncode, 0)

    def test_defect_support_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["public_branch_obstruction"].update(
                ghost_defect_Laurent_support=[-1]
            )
        ).returncode, 0)

    def test_stationarity_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["stationarity"].update(order_lambda="OBSTRUCTED")
        ).returncode, 0)

    def test_full_eq19_promotion_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["disposition"].update(
                Eq19_ghost_even_neutral_term_on_declared_public_branch="PROVED"
            )
        ).returncode, 0)

    def test_odd_remainder_nullity_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["public_branch_obstruction"]["canonical_parity_split"].update(
                tau_0_C1sharp_C1="0"
            )
        ).returncode, 0)

    def test_hidden_parity_unit_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["hidden_source_parity_domain"].update(
                augmentation_of_F_at_the_Fock_vacuum=1
            )
        ).returncode, 0)

    def test_repair_generator_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["minimal_two_branch_repair"]["generator_coefficients"]["1"][0].__setitem__(2, "0")
        ).returncode, 0)

    def test_repair_first_coefficient_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["minimal_two_branch_repair"]["first_projector_coefficient"]["-1"][0].__setitem__(3, "0")
        ).returncode, 0)

    def test_repair_affiliation_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["minimal_two_branch_repair"].update(
                affiliation="PUBLIC_RT_DERIVED"
            )
        ).returncode, 0)

    def test_physical_probability_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["disposition"].update(
                physical_probability="ESTABLISHED"
            )
        ).returncode, 0)

    def test_scope_boundary_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value.update(does_not_establish=[])
        ).returncode, 0)

    def test_input_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64
        self.assertNotEqual(self.mutate(mutation).returncode, 0)


if __name__ == "__main__":
    unittest.main()
