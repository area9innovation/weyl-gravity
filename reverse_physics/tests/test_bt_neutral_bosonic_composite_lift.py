"""Falsification tests for the BT neutral bosonic composite lift."""
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
    "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_neutral_bosonic_composite_lift.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_neutral_bosonic_composite_lift.py"
)


class NeutralBosonicCompositeLiftTests(unittest.TestCase):
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

    def test_rho_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["degree_four_neutral_sector"]["rho"].update(
                    numerator=820
                )
            ).returncode,
            0,
        )

    def test_basis_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["degree_four_neutral_sector"]["basis"]
                .__setitem__(0, "wrong")
            ).returncode,
            0,
        )

    def test_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["degree_four_neutral_sector"][
                    "gram_over_rho_power_eight"
                ][0].__setitem__(8, "5")
            ).returncode,
            0,
        )

    def test_parity_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["degree_four_neutral_sector"][
                    "ghost_parity_occupation_swap"
                ][0].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_positive_metric_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["degree_four_neutral_sector"][
                    "positive_fundamental_metric_over_rho_power_eight"
                ][0].__setitem__(0, "-4")
            ).returncode,
            0,
        )

    def test_degree_two_index_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["bosonic_neutral_census"]["rows"][1].update(
                    negative_index=2
                )
            ).returncode,
            0,
        )

    def test_minimal_degree_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["bosonic_neutral_census"].update(
                    minimal_total_degree=2
                )
            ).returncode,
            0,
        )

    def test_embedding_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_neutral_lift"][
                    "normalized_embedding_U"
                ][1].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_normalized_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_neutral_lift"]["normalized_gram"][0]
                .__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_forward_block_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_neutral_lift"]["forward_block_B4"][1]
                .__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_pullback_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_neutral_lift"]["pullback"][0]
                .__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_charge_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_neutral_lift"].update(charge="NEGATIVE")
            ).returncode,
            0,
        )

    def test_ghost_parity_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_neutral_lift"].update(
                    ghost_parity="EVEN"
                )
            ).returncode,
            0,
        )

    def test_Eq19_P_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    ghost_even_Eq19_P_term="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_physical_probability_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_fourth_probability="ESTABLISHED"
                )
            ).returncode,
            0,
        )

    def test_all_order_Eq19_promotion_rejected(self):
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
