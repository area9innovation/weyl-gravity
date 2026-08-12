"""Falsification tests for the crossed six-point Kallen obstruction."""
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
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_crossed_six_point_kallen_obstruction.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_crossed_six_point_kallen_obstruction.py"
)


class CrossedSixPointKallenObstructionTests(unittest.TestCase):
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
        result = self.mutate(mutation)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_producer_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_continuation_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["analytic_spacelike_crossing"].update(
                continuation="w=x"
            )
        )

    def test_kallen_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["analytic_spacelike_crossing"].update(
                kallen_polynomial="x**2"
            )
        )

    def test_q_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["analytic_spacelike_crossing"].update(
                continued_q=value["analytic_spacelike_crossing"]["positive_q_cross"]
            )
        )

    def test_external_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["analytic_spacelike_crossing"].update(
                external_delta_prime_sign=-1
            )
        )

    def test_image_basis_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_two_species_quotient"]
            ["image_basis"][2].__setitem__(0, "0")
        )

    def test_raw_gram_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_two_species_quotient"]
            ["image_raw_gram"][0].__setitem__(1, "0")
        )

    def test_fixed_hilbert_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_two_species_quotient"]
            ["fixed_profile_swap_hilbertized_gram"][0].__setitem__(
                0,
                value["crossed_two_species_quotient"]
                ["branch_flipped_hilbertized_gram"][0][0],
            )
        )

    def test_inertia_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_two_species_quotient"].update(
                inertia_with_certified_sharp=[2, 0, 0]
            )
        )

    def test_collapse_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_two_species_quotient"]
            ["collapse_on_image"][0].__setitem__(0, "0")
        )

    def test_density_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["bilateral_kallen_resolution"].update(
                density="1/x"
            )
        )

    def test_reference_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["bilateral_kallen_resolution"].update(
                exchange_fixed_reference="x0=1"
            )
        )

    def test_primitive_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["bilateral_kallen_resolution"].update(
                primitive="0"
            )
        )

    def test_range_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["bilateral_kallen_resolution"].update(
                range="a finite interval"
            )
        )

    def test_history_count_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["history_disposition"].update(
                reversed_history_count=11
            )
        )

    def test_history_status_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["history_disposition"].update(
                status="PHYSICALLY_AFFILIATED"
            )
        )

    def test_branch_flip_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                crossed_branch_sign_from_BT_dynamics="DERIVED"
            )
        )

    def test_physical_affiliation_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                twelve_reversed_HP_chambers_on_current_carrier="AFFILIATED"
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
