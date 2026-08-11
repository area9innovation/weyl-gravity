"""Falsification tests for BT complement/hard-profile separation."""
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
    "REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_complement_hard_profile_separation.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_complement_hard_profile_separation.py"
)


class ComplementHardProfileSeparationTests(unittest.TestCase):
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
                lambda value: value["shared_fixture"]["rho"].update(numerator=820)
            ).returncode,
            0,
        )

    def test_hard_coordinate_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["shared_fixture"]["hard_coordinate_values"][1].update(
                    numerator=35
                )
            ).returncode,
            0,
        )

    def test_endpoint_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["shared_fixture"]["endpoint_c1"].update(
                    numerator=14820
                )
            ).returncode,
            0,
        )

    def test_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["shared_fixture"]["forced_missing_gram"][0][1].update(
                    numerator=-820
                )
            ).returncode,
            0,
        )

    def test_inner_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["shared_fixture"]["inner_coefficients"][0].update(
                    numerator=-6698
                )
            ).returncode,
            0,
        )

    def test_difference_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["shared_fixture"]["inner_coefficient_difference"].update(
                    numerator=224
                )
            ).returncode,
            0,
        )

    def test_rho_only_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    rho_only_unification="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_dynamic_bundle_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["separation_theorem"][
                    "smallest_justified_architecture"
                ].update(status="BT_DERIVED")
            ).returncode,
            0,
        )

    def test_profile_jump_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    BT_derived_profile_jump="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_probability_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_fourth_probability="NORMALIZED"
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
