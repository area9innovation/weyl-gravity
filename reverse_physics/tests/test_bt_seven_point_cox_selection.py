"""Falsification tests for the BT seven-point Cox-selection result."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_seven_point_cox_selection.py")
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_seven_point_cox_selection.py"
)


class SevenPointCoxSelectionTests(unittest.TestCase):
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
            self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0
        )

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_tree_count_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["topology"].update(total=2484)).returncode,
            0,
        )

    def test_projected_expression_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["correlated_boundary"].update(
                    projected_expression="0"
                )
            ).returncode,
            0,
        )

    def test_inner_cocycle_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["threshold_analysis"]["inner_reduction"][
                    "r_log_r_coefficient"
                ].update(numerator=-25)
            ).returncode,
            0,
        )

    def test_external_sign_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["threshold_analysis"]["normalization"].update(
                    signed_raw_triple_cocycle={"numerator": -81, "denominator": 128}
                )
            ).returncode,
            0,
        )

    def test_P3_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["threshold_analysis"]["normalization"][
                    "leading_three_count_coefficient"
                ].update(numerator=15)
            ).returncode,
            0,
        )

    def test_third_cumulant_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["threshold_analysis"]["factorial_data"][
                    "third_factorial_cumulant_coefficient"
                ].update(numerator=0)
            ).returncode,
            0,
        )

    def test_gamma_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    gamma_cox_completion="SELECTED"
                )
            ).returncode,
            0,
        )

    def test_two_atom_support_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["cox_completion"][
                    "minimal_two_atom_cox_candidate"
                ]["support"].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_uniqueness_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    unique_all_order_count_law="PROVED"
                )
            ).returncode,
            0,
        )

    def test_full_probability_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    complete_five_body_probability="CONSTRUCTED"
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

    def test_hard_angle_boundary_mutation(self):
        phrase = (
            "universal hard-angle independence beyond the exact producer "
            "and verifier fixtures"
        )
        self.assertNotEqual(
            self.mutate(
                lambda value: value["does_not_establish"].remove(phrase)
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
