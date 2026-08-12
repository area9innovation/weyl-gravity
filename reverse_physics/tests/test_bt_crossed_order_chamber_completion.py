"""Falsification tests for the BT crossed-order chamber completion."""
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
    "REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_crossed_order_chamber_completion.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_crossed_order_chamber_completion.py"
)


class CrossedOrderChamberCompletionTests(unittest.TestCase):
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

    def assert_rejected(self, mutation):
        self.assertNotEqual(self.mutate(mutation).returncode, 0)

    def test_producer_fast_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_history_count_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["order_chamber_completion"]
            ["history_counts"].__setitem__(2, 13)
        )

    def test_chamber_count_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["order_chamber_completion"]
            ["chambers_per_history"].__setitem__(3, 5)
        )

    def test_completed_sheet_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["order_chamber_completion"]
            ["completed_history_sheets"].__setitem__(3, 300)
        )

    def test_missing_sheet_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["order_chamber_completion"]
            ["missing_crossed_sheets"].__setitem__(2, 0)
        )

    def test_missing_total_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["order_chamber_completion"].update(
                missing_crossed_total=311
            )
        )

    def test_direct_leakage_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["order_chamber_completion"]
            ["direct_canonical_input_leakage"][1].update(
                direct_crossed_sheets=0
            )
        )

    def test_rate_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["finite_exact_leakage_witness"]
            ["rate_q1"].update(numerator=0)
        )

    def test_coefficient_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["finite_exact_leakage_witness"]
            ["coefficient_B"][2].__setitem__(0, "0")
        )

    def test_skew_generator_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["finite_exact_leakage_witness"]
            ["skew_generator_K"][0].__setitem__(2, "0")
        )

    def test_cayley_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["finite_exact_leakage_witness"]
            ["cayley_unitary"][0].__setitem__(0, "1")
        )

    def test_leakage_probability_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["finite_exact_leakage_witness"]
            ["reversed_chamber_probability"].update(numerator=0)
        )

    def test_gauge_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["HP_gauge_theorem"]["gauge_deltas"].update(
                creation_Q_change=1
            )
        )

    def test_first_missing_block_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["physical_transfer_gate"].update(
                first_missing_block="none"
            )
        )

    def test_external_permutation_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["physical_transfer_gate"].update(
                external_permutation_boundary="crossing supplies everything"
            )
        )

    def test_two_sided_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                two_sided_reduced_mode_physical_operator="CONSTRUCTED"
            )
        )

    def test_spacetime_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                spacetime_Moller_LSZ_S_operator="CONSTRUCTED"
            )
        )

    def test_eq19_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value.update(does_not_establish=[])
        )

    def test_input_hash_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["provenance"]["inputs"][0].update(
                sha256="0" * 64
            )
        )


if __name__ == "__main__":
    unittest.main()
