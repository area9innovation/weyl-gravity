"""Falsification tests for covariant formal BT Eq. 19 charge support."""
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
    "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_covariant_formal_eq19_charge_support.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_covariant_formal_eq19_charge_support.py"
)


class CovariantFormalEq19ChargeSupportTests(unittest.TestCase):
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

    def test_Omega_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_Eq16_equivariance"]["Omega_replay"][3][
                    "coefficient"
                ].update(numerator=2)
            ).returncode,
            0,
        )

    def test_Omega_charge_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_Eq16_equivariance"]["Omega_replay"][2]
                .update(charge=-1)
            ).returncode,
            0,
        )

    def test_Upsilon_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_Eq16_equivariance"]["Upsilon_replay"][3][
                    "terms"
                ][1]["coefficient"].update(numerator=-1)
            ).returncode,
            0,
        )

    def test_Upsilon_charge_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_Eq16_equivariance"]["Upsilon_replay"][2]
                .update(orbit_power=1)
            ).returncode,
            0,
        )

    def test_word_census_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_Eq16_equivariance"]["word_census"][4][
                    "charge_multiplicities"
                ].update({"0": 5})
            ).returncode,
            0,
        )

    def test_two_sidedness_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["formal_inverse_and_projector_consequence"].update(
                    formal_two_sidedness="R R^dagger=1 only"
                )
            ).returncode,
            0,
        )

    def test_time_translated_intertwining_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_Eq16_equivariance"].update(
                    time_translated_intertwining="NOT_PROVED"
                )
            ).returncode,
            0,
        )

    def test_inverse_intertwining_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["formal_inverse_and_projector_consequence"].update(
                    inverse_intertwining_identity="NOT_PROVED"
                )
            ).returncode,
            0,
        )

    def test_fixture_projector_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["formal_inverse_and_projector_consequence"][
                    "finite_fixture"
                ]["output_projector"][1].__setitem__(1, "0")
            ).returncode,
            0,
        )

    def test_Q_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    strict_negative_Q_on_covariant_formal_algebra="NONZERO"
                )
            ).returncode,
            0,
        )

    def test_fixed_vacuum_descent_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fixed_vacuum_and_asymptotic_boundary"].update(
                    charge_theorem_descends_to_Z_equals_1="YES"
                )
            ).returncode,
            0,
        )

    def test_object_type_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["typed_object_separation"].update(
                    Eq19_object="P_out(S_phi-1)P_in"
                )
            ).returncode,
            0,
        )

    def test_graph_ledger_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["typed_object_separation"].update(
                    eight_point_K4_and_graph_slope="RT_COEFFICIENT"
                )
            ).returncode,
            0,
        )

    def test_ghost_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    ghost_even_neutral_component="PROVED"
                )
            ).returncode,
            0,
        )

    def test_time_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    neutral_component_time_independence="PROVED"
                )
            ).returncode,
            0,
        )

    def test_asymptotic_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    asymptotic_limits="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_full_Eq19_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(full_Eq19="PROVED")
            ).returncode,
            0,
        )

    def test_physical_probability_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_probability="ESTABLISHED"
                )
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
