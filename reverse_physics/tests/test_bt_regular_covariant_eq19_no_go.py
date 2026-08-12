"""Falsification tests for the regular covariant BT Eq. (19) no-go."""
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
    "REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_regular_covariant_eq19_no_go.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_regular_covariant_eq19_no_go.py")


class RegularCovariantEq19NoGoTests(unittest.TestCase):
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

    def test_producer_check(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_charge_premise_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["charge_projection_argument"].update(
                premise="A may contain positive charge"
            )
        ).returncode, 0)

    def test_negative_projection_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["charge_projection_argument"].update(
                forced_remainder="Q_<0 may be nonzero"
            )
        ).returncode, 0)

    def test_neutral_identification_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["charge_projection_argument"].update(
                forced_neutral_term="N_0 differs from A"
            )
        ).returncode, 0)

    def test_public_support_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["order_lambda_contradiction"].update(public_support=[0])
        ).returncode, 0)

    def test_ghost_support_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["order_lambda_contradiction"].update(
                ghost_conjugate_support=[-1]
            )
        ).returncode, 0)

    def test_rank_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["order_lambda_contradiction"].update(commutator_rank=3)
        ).returncode, 0)

    def test_odd_norm_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["order_lambda_contradiction"].update(
                canonical_odd_relative_norm="0"
            )
        ).returncode, 0)

    def test_higher_order_repair_mutation_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["order_lambda_contradiction"].update(
                higher_order_boundary="lambda^2 cancels the lambda defect"
            )
        ).returncode, 0)

    def test_public_repair_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["repair_and_escape_boundary"].update(
                public_affiliation="SUPPLIED_BY_PUBLIC_RT"
            )
        ).returncode, 0)

    def test_regular_repair_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["repair_and_escape_boundary"].update(
                regular_same_chart_affiliation="CONSTRUCTED"
            )
        ).returncode, 0)

    def test_fixed_vacuum_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["disposition"].update(fixed_vacuum_Eq19="REFUTED")
        ).returncode, 0)

    def test_enlarged_completion_no_go_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["disposition"].update(
                unpublished_enlarged_Eq19="REFUTED"
            )
        ).returncode, 0)

    def test_physical_probability_promotion_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value["disposition"].update(
                complete_physical_probability="ESTABLISHED"
            )
        ).returncode, 0)

    def test_scope_boundary_removal_rejected(self):
        self.assertNotEqual(self.mutate(
            lambda value: value.update(does_not_establish=[])
        ).returncode, 0)

    def test_input_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64
        self.assertNotEqual(self.mutate(mutation).returncode, 0)


if __name__ == "__main__":
    unittest.main()
