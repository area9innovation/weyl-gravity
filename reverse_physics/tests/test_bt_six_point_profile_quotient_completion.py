"""Falsification tests for the six-point BT profile quotient completion."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_six_point_profile_quotient_completion.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_six_point_profile_quotient_completion.py"
)


class SixPointProfileQuotientCompletionTests(unittest.TestCase):
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

    def test_producer(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_carrier_dimension_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["declared_carrier"].update(dimension=3)
            ).returncode,
            0,
        )

    def test_tensor_metric_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["declared_carrier"]["tensor_metric_eta"][0].__setitem__(
                    3, "2"
                )
            ).returncode,
            0,
        )

    def test_projector_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_quotient"][
                    "projector_P_generic"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_kernel_visibility_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_quotient"].update(
                    kernel_disposition="DEGENERATE"
                )
            ).returncode,
            0,
        )

    def test_image_gram_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_quotient"].update(
                    image_raised_endomorphism="u*v*I2"
                )
            ).returncode,
            0,
        )

    def test_conditional_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["branching_affiliation"][
                    "conditional_second_rate"
                ].update(numerator=4)
            ).returncode,
            0,
        )

    def test_second_jump_affiliation_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    second_positive_scalar_species_jump="NOT_AFFILIATED"
                )
            ).returncode,
            0,
        )

    def test_third_jump_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    third_jump_species_affiliation="AFFILIATED"
                )
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


if __name__ == "__main__":
    unittest.main()
