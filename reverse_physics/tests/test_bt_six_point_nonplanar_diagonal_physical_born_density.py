"""Mutation tests for the nonplanar diagonal BT Born-density theorem."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_NONPLANAR_DIAGONAL_PHYSICAL_BORN_DENSITY_V1.json",
)
VERIFIER = os.path.join(
    ROOT,
    "reverse_physics/verify_bt_six_point_nonplanar_diagonal_physical_born_density.py",
)
TEMP_ROOT = os.path.join(ROOT, "reverse_physics/.tmp_nonplanar_diagonal_tests")
os.makedirs(TEMP_ROOT, exist_ok=True)


class NonplanarDiagonalBornDensityTests(unittest.TestCase):
    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", dir=TEMP_ROOT
        ) as handle:
            json.dump(value, handle)
            handle.flush()
            return subprocess.run(
                [sys.executable, VERIFIER, "--fast", "--verify", handle.name],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

    def assert_rejected(self, mutation):
        result = self.mutate(mutation)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_tilt_ratio_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_nonplanar_family"]["tilt"].update(ratio="0")
        )

    def test_nonplanarity_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_nonplanar_family"].update(
                generic_outgoing_z_is_nonzero=False
            )
        )

    def test_middle_coefficient_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_nonplanar_family"]["middle_coefficients"][0]
            .update(coefficient="0")
        )

    def test_complement_identity_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_nonplanar_family"].update(
                ten_complement_pairs_equal=False
            )
        )

    def test_square_sum_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_nonplanar_family"].update(
                equals_twice_ten_square_sum=False
            )
        )

    def test_gcd_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_nonplanar_family"].update(
                degree_three_numerator_gcd="t"
            )
        )

    def test_two_parameter_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["interpretation"].update(
                complete_two_parameter_nonplanar_family="COMPUTED"
            )
        )

    def test_integrated_probability_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["interpretation"].update(
                integrated_normalized_probability="PROVED_POSITIVE"
            )
        )

    def test_boundary_deletion_rejected(self):
        self.assert_rejected(lambda v: v.update(does_not_establish=[]))

    def test_input_hash_mutation_rejected_early(self):
        self.assert_rejected(
            lambda v: v["provenance"]["inputs"][0].update(sha256="0" * 64)
        )


if __name__ == "__main__":
    unittest.main()
