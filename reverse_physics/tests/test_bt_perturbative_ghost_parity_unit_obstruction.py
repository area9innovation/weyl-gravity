"""Falsification tests for the BT perturbative ghost-parity unit no-go."""
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
    "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_perturbative_ghost_parity_unit_obstruction.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_perturbative_ghost_parity_unit_obstruction.py"
)


class PerturbativeGhostParityUnitObstructionTests(unittest.TestCase):
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

    def test_source_ring_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["source_algebra"].update(coefficient_ring="Q[lambda,Z]")
        ).returncode, 0)

    def test_augmentation_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["source_algebra"].update(
                augmentation="epsilon(Z)=0; epsilon(nonzero-mode jets)=0"
            )
        ).returncode, 0)

    def test_F_degree_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["exact_generator_images"]["field_degrees_in_F"].update(
                {"Box(varphi)": 0}
            )
        ).returncode, 0)

    def test_Omega_image_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["exact_generator_images"].update(
                Omega_image="O=Z exp(lambda varphi)"
            )
        ).returncode, 0)

    def test_exponential_coefficient_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["exact_generator_images"]["exponential_inverse_replay"][8][
                "product_coefficients_through_cutoff"
            ][5].update(numerator=1)
        ).returncode, 0)

    def test_Omega_augmentation_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["exact_generator_images"].update(Omega_augmentation="0")
        ).returncode, 0)

    def test_Upsilon_augmentation_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["exact_generator_images"].update(Upsilon_augmentation="Z^-1")
        ).returncode, 0)

    def test_unit_status_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["unit_obstruction"].update(Upsilon_unit_status="UNIT")
        ).returncode, 0)

    def test_unit_lemma_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["unit_obstruction"].update(
                lemma="automorphisms need not preserve units"
            )
        ).returncode, 0)

    def test_conclusion_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["unit_obstruction"].update(
                conclusion="HIDDEN_PARITY_CONSTRUCTED"
            )
        ).returncode, 0)

    def test_localized_vacuum_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["escape_routes"]["localized_on_shell_chart"].update(
                vacuum_boundary="the F=0 vacuum is retained"
            )
        ).returncode, 0)

    def test_localized_completion_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["escape_routes"]["localized_on_shell_chart"].update(
                disposition="BT_COMPLETION_CONSTRUCTED"
            )
        ).returncode, 0)

    def test_doubled_source_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["escape_routes"]["doubled_sheet"].update(
                disposition="ORIGINAL_BT_SOURCE"
            )
        ).returncode, 0)

    def test_same_chart_affiliation_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["Eq19_consequence"].update(
                same_chart_regular_local_symbol_affiliation_of_two_branch_repair="PROVED"
            )
        ).returncode, 0)

    def test_singular_quantum_affiliation_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["Eq19_consequence"].update(
                singular_or_unbounded_quantum_affiliation="RULED_OUT"
            )
        ).returncode, 0)

    def test_charge_formula_retraction_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["Eq19_consequence"].update(charge_formula="REFUTED")
        ).returncode, 0)

    def test_enlarged_completion_no_go_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["Eq19_consequence"].update(
                unpublished_enlarged_completion="RULED_OUT"
            )
        ).returncode, 0)

    def test_physical_probability_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["disposition"].update(physical_probability="ESTABLISHED")
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
