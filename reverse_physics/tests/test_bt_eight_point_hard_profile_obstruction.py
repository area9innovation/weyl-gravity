"""Falsification tests for the BT eight-point hard-profile obstruction."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_eight_point_fourth_moment.py")
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eight_point_fourth_moment.py"
)


class EightPointHardProfileObstructionTests(unittest.TestCase):
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

    def test_tree_count_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["topology"].update(total=34299)).returncode,
            0,
        )

    def test_soft_fixture_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["correlated_boundary"]["soft_fixture"]
                .__setitem__(0, 2)
            ).returncode,
            0,
        )

    def test_finite_value_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["correlated_boundary"]["rows"][0].update(
                    finite_projected_value="0"
                )
            ).returncode,
            0,
        )

    def test_hierarchy_valuation_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["correlated_boundary"]["rows"][1]
                ["hierarchy_valuations"][2].__setitem__(1, 0)
            ).returncode,
            0,
        )

    def test_residue_difference_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["correlated_boundary"]
                ["strong_residue_difference"].update(numerator=258)
            ).returncode,
            0,
        )

    def test_hard_independence_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    hard_independent_scalar_fourth_jump="COMPUTED"
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

    def test_two_atom_cox_promotion_rejected(self):
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
