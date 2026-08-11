"""Falsification tests for the BT eight-point inner-threshold obstruction."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_eight_point_inner_threshold_obstruction.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eight_point_inner_threshold_obstruction.py"
)


class EightPointInnerThresholdObstructionTests(unittest.TestCase):
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

    def test_profile_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_analysis"]["rows"][0].update(
                    inner_profile="0"
                )
            ).returncode,
            0,
        )

    def test_difference_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_analysis"].update(difference="0")
            ).returncode,
            0,
        )

    def test_fixture_residue_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["inner_threshold"]["fixture_residues"][0][
                    "r_log_r_coefficient"
                ].update(numerator=-6698)
            ).returncode,
            0,
        )

    def test_difference_residue_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["inner_threshold"][
                    "hard_difference_r_log_r_coefficient"
                ].update(numerator=224)
            ).returncode,
            0,
        )

    def test_fixed_replay_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_analysis"][
                    "fixed_inner_fixture_after_first_three"
                ].update(numerator=23228)
            ).returncode,
            0,
        )

    def test_homogeneity_normalization_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_analysis"]["normalization"].update(
                    homogeneity_status="RATIO_FIXED"
                )
            ).returncode,
            0,
        )

    def test_scalar_obstruction_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    hard_independent_scalar_fourth_jump="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_profile_successor_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    profile_or_channel_valued_successor="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_probability_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_fourth_probability_normalization="ASSEMBLED"
                )
            ).returncode,
            0,
        )

    def test_cox_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    two_atom_Cox_completion="RULED_OUT"
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
