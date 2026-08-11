"""Falsification tests for the BT eight-point tau2-threshold profile."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_eight_point_tau2_threshold_profile.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eight_point_tau2_threshold_profile.py"
)


class EightPointTau2ThresholdProfileTests(unittest.TestCase):
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
                    tau2_profile="0"
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

    def test_middle_replay_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_analysis"][
                    "tau2_seven_after_first_two_functionals"
                ].update(numerator=334238)
            ).returncode,
            0,
        )

    def test_third_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["threshold_chain"][
                    "third_threshold_profile_functional_difference"
                ].update(numerator=23228)
            ).returncode,
            0,
        )

    def test_physical_normalization_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_normalization="ASSEMBLED"
                )
            ).returncode,
            0,
        )

    def test_universality_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    three_threshold_scalar_universality="RESTORED"
                )
            ).returncode,
            0,
        )

    def test_inner_reduction_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    remaining_independent_mass_tau1_reduction="COMPUTED"
                )
            ).returncode,
            0,
        )

    def test_final_moment_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    threshold_integrated_fourth_moment="COMPUTED"
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
