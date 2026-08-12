"""Falsification tests for the crossed profile-selective parity obstruction."""
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
    "REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_crossed_profile_selective_parity_obstruction.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_crossed_profile_selective_parity_obstruction.py"
)


class CrossedProfileSelectiveParityObstructionTests(unittest.TestCase):
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

    def test_metric_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"]["metric_eta"][0].__setitem__(3, "-3")
        )

    def test_D_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"]["crossed_amplitude_D"][0].__setitem__(0, "q")
        )

    def test_R_minus_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"]["repaired_collapse_R_minus"][0].__setitem__(2, "1")
        )

    def test_base_spectrum_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"].update(
                base_characteristic_polynomial="z**2*(-2*q*v+z)**2"
            )
        )

    def test_sign_row_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"]["diagonal_unit_sign_census"][0].update(
                metric_type="KREIN_ANTI_ISOMETRY"
            )
        )

    def test_sign_repair_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"]["diagonal_unit_sign_census"][3].update(
                repairs_nonzero_spectrum=False
            )
        )

    def test_census_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["same_carrier_classification"]["census_summary"].update(
                krein_anti_isometries=3
            )
        )

    def test_prefix_vector_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["prefix_obstruction"]["prefix_vector"].__setitem__(1, "0")
        )

    def test_prefix_gram_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["prefix_obstruction"].update(prefix_gram="-3/2")
        )

    def test_parent_parity_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["prefix_obstruction"]["canonical_parent_parity"][2].__setitem__(2, "1")
        )

    def test_repaired_spectrum_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["prefix_obstruction"].update(
                repaired_characteristic_polynomial="z**2*(2*q*v+z)**2"
            )
        )

    def test_transformed_prefix_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["prefix_obstruction"]["transformed_prefix"].__setitem__(2, "1/2")
        )

    def test_public_parity_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["public_ghost_parity_test"]["neutral_degree_four_ghost_parity"][1].__setitem__(3, "-1")
        )

    def test_selected_metric_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["public_ghost_parity_test"]["selected_metric"][0].__setitem__(0, "1")
        )

    def test_selected_ghost_action_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["public_ghost_parity_test"]["selected_ghost_action"][0].__setitem__(0, "1")
        )

    def test_same_carrier_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["disposition"].update(
                same_carrier_regular_profile_selective_parity="CONSTRUCTED"
            )
        )

    def test_doubled_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["escape_architectures"].update(
                doubled_cross_paired_source="BT_DERIVED"
            )
        )

    def test_nonfactorizing_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["disposition"].update(
                nonfactorizing_crossed_six_point_term="COMPUTED"
            )
        )

    def test_eq19_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["disposition"].update(Eq19_all_orders="PROVED")
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assert_rejected(lambda v: v.update(does_not_establish=[]))

    def test_input_hash_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["provenance"]["inputs"][0].update(sha256="0" * 64)
        )


if __name__ == "__main__":
    unittest.main()
