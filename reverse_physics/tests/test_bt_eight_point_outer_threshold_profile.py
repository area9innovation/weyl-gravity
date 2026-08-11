"""Falsification tests for the BT eight-point outer-threshold profile."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_eight_point_outer_threshold_profile.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eight_point_outer_threshold_profile.py"
)


class EightPointOuterThresholdProfileTests(unittest.TestCase):
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
        result = self.command([sys.executable, PRODUCER, "--fast-check"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_independent_verifier(self):
        result = self.command([sys.executable, VERIFIER])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_profile_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["hard_profile_analysis"]["rows"][0].update(
                    outer_profile="0"
                )
            ).returncode,
            0,
        )

    def test_leading_profile_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["hard_profile_analysis"]["rows"][1].update(
                    leading_e3_profile="0"
                )
            ).returncode,
            0,
        )

    def test_J2_direction_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["hard_profile_analysis"].update(
                    leading_profile_difference="257/(1568*tau4)"
                )
            ).returncode,
            0,
        )

    def test_fixed_u_replay_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["hard_profile_analysis"][
                    "fixed_u_three_difference"
                ].update(numerator=258)
            ).returncode,
            0,
        )

    def test_threshold_pole_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["hard_profile_analysis"][
                    "threshold_e3_pole_difference"
                ].update(numerator=770)
            ).returncode,
            0,
        )

    def test_outer_universality_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    outer_threshold_scalar_universality="RESTORED"
                )
            ).returncode,
            0,
        )

    def test_fourth_moment_promotion_rejected(self):
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
