"""Falsification tests for the BT physical Moller defect completion."""
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
    "REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_physical_moller_defect_completion.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_physical_moller_defect_completion.py"
)


class PhysicalMollerDefectCompletionTests(unittest.TestCase):
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
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_probability_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_exact_witness"]
                ["outcome_probabilities"][0].update(numerator=2)
            ).returncode,
            0,
        )

    def test_amplitude_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_exact_witness"]
                ["outcome_amplitude_column"][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_householder_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_exact_witness"]
                ["householder_outcome_matrix"][0].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_defect_rotation_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_exact_witness"]
                ["defect_rotation_outcome_matrix"][1].__setitem__(1, "1")
            ).returncode,
            0,
        )

    def test_defect_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_exact_witness"].update(
                    incoming_defect_rank=5
                )
            ).returncode,
            0,
        )

    def test_unitary_hash_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_exact_witness"].update(
                    first_unitary_sha256="0" * 64
                )
            ).returncode,
            0,
        )

    def test_completion_formula_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["universal_completion_theorem"].update(
                    all_completions="S=M"
                )
            ).returncode,
            0,
        )

    def test_defect_condition_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["universal_completion_theorem"].update(
                    defect_condition="W^*W=0"
                )
            ).returncode,
            0,
        )

    def test_continuum_dimension_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["continuum_consequence"].update(
                    defect_dimension="FINITE"
                )
            ).returncode,
            0,
        )

    def test_dense_core_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["continuum_consequence"].update(
                    dense_core="one vector"
                )
            ).returncode,
            0,
        )

    def test_minimal_input_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["continuum_consequence"].update(
                    minimal_new_input="none"
                )
            ).returncode,
            0,
        )

    def test_amplitude_selection_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    completion_selected_by_public_amplitudes="PROVED"
                )
            ).returncode,
            0,
        )

    def test_bt_affiliation_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    BT_asymptotic_hamiltonian_affiliation="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_spacetime_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    spacetime_Moller_LSZ_S_operator="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
            ).returncode,
            0,
        )

    def test_source_audit_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["provenance"]["public_source_audit"].update(
                    result="Companion proves everything"
                )
            ).returncode,
            0,
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["provenance"]["inputs"][0].update(
                    sha256="0" * 64
                )
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
