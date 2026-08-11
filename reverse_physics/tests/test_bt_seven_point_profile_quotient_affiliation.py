"""Falsification tests for the seven-point BT signed-profile quotient."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_seven_point_profile_quotient_affiliation.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_seven_point_profile_quotient_affiliation.py"
)


class SevenPointProfileQuotientAffiliationTests(unittest.TestCase):
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

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_pretrace_component_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["amplitude_components"].update(
                    F1_singleton="0"
                )
            ).returncode,
            0,
        )

    def test_parent_profile_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["recombined_six_point_parent"].update(
                    H0_singleton="0"
                )
            ).returncode,
            0,
        )

    def test_physical_pullback_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_quotient"][
                    "physical_raised_pullback_generic"
                ][0].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_external_sign_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_quotient"].update(
                    seven_external_delta_prime_sign=1
                )
            ).returncode,
            0,
        )

    def test_conditional_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["branching_affiliation"][
                    "conditional_third_rate"
                ].update(numerator=26)
            ).returncode,
            0,
        )

    def test_third_jump_affiliation_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["branching_affiliation"].update(
                    third_jump="NOT_AFFILIATED"
                )
            ).returncode,
            0,
        )

    def test_fourth_jump_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(fourth_jump="COMPUTED")
            ).returncode,
            0,
        )

    def test_complete_probability_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    complete_BT_probability="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
            ).returncode,
            0,
        )

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation(self):
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
