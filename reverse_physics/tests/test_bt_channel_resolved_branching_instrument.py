"""Falsification tests for the BT channel-resolved branching instrument."""
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
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_channel_resolved_branching_instrument.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_channel_resolved_branching_instrument.py"
)


class ChannelResolvedBranchingInstrumentTests(unittest.TestCase):
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

    def test_history_count_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["history_carrier"]["levels"][3].update(
                    history_count=59
                )
            ).returncode,
            0,
        )

    def test_outdegree_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["rate_factorization"].update(
                    children_per_parent=[3, 4, 4]
                )
            ).returncode,
            0,
        )

    def test_extension_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["rate_factorization"][
                    "extension_rate_squares"
                ][1].update(numerator=1)
            ).returncode,
            0,
        )

    def test_physical_gram_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_affiliation"][
                    "first_per_channel_gram"
                ].update(denominator=47)
            ).returncode,
            0,
        )

    def test_species_rank_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["branching_instrument"].update(
                    physical_species_dimension=1
                )
            ).returncode,
            0,
        )

    def test_generator_hash_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["branching_instrument"].update(
                    generator_entry_sha256="0"*64
                )
            ).returncode,
            0,
        )

    def test_population_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["branching_instrument"][
                    "level_population_taylor_coefficients"
                ][3][3].update(numerator=8)
            ).returncode,
            0,
        )

    def test_fixed_mark_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    fixed_three_mark_Cox_lift="CHANNEL_COMPLETE"
                )
            ).returncode,
            0,
        )

    def test_species_affiliation_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    higher_point_species_and_phase_affiliation="DERIVED"
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
                lambda value: value["disposition"].update(
                    Eq19_all_orders="PROVED"
                )
            ).returncode,
            0,
        )

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value.update(does_not_establish=[])
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
