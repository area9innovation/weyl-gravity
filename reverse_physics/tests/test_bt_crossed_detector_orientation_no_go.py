"""Falsification tests for the crossed detector orientation no-go."""
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
    "REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_crossed_detector_orientation_no_go.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_crossed_detector_orientation_no_go.py"
)


class CrossedDetectorOrientationNoGoTests(unittest.TestCase):
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

    def assert_rejected(self, mutation):
        result = self.mutate(mutation)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_producer_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_crossing_matrix_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["standard_orientation_no_go"]
            ["ordinary_crossing_matrix"][1].__setitem__(1, "-1")
        )

    def test_species_gram_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["standard_orientation_no_go"]
            ["fixed_species_gram"][0].__setitem__(0, "6*q_x*v")
        )

    def test_orientation_gram_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["standard_orientation_no_go"]
            ["orientation_gram"][0].__setitem__(1, "0")
        )

    def test_combined_gram_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["standard_orientation_no_go"]
            ["combined_gram"][0].__setitem__(0, "0")
        )

    def test_factorization_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["standard_orientation_no_go"].update(
                factorization_boundary="complete amplitude computed"
            )
        )

    def test_R_plus_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["coherent_collapse_classification"]
            ["outgoing_style_collapse_R_plus"][0].__setitem__(2, "-1")
        )

    def test_R_minus_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["coherent_collapse_classification"]
            ["repaired_collapse_R_minus"][0].__setitem__(2, "1")
        )

    def test_R_minus_projector_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["coherent_collapse_classification"]
            ["R_minus_projector"][0].__setitem__(0, "0")
        )

    def test_internal_parity_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["internal_parity_boundary"]
            ["internal_jet_parity"][1].__setitem__(1, "1")
        )

    def test_internal_metric_law_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["internal_parity_boundary"].update(
                internal_parity_metric_law="S^T J S=J"
            )
        )

    def test_history_count_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["history_disposition"].update(
                reversed_history_count=11
            )
        )

    def test_history_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                twelve_reversed_physical_intertwiners="CONSTRUCTED"
            )
        )

    def test_internal_affiliation_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                internal_jet_parity_BT_affiliation="DERIVED"
            )
        )

    def test_nonfactorizing_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                nonfactorizing_crossed_detector_terms="ZERO"
            )
        )

    def test_eq19_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assert_rejected(lambda value: value.update(does_not_establish=[]))

    def test_input_hash_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["provenance"]["inputs"][0].update(
                sha256="0" * 64
            )
        )


if __name__ == "__main__":
    unittest.main()
