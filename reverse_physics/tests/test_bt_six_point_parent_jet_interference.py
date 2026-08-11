"""Falsification tests for the six-point BT parent-jet obstruction."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_six_point_parent_jet_interference.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_six_point_parent_jet_interference.py"
)


class SixPointParentJetInterferenceTests(unittest.TestCase):
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
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_strong_component_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["amplitude_components"][
                    "strong_order_components"
                ].update({"1": "0"})
            ).returncode,
            0,
        )

    def test_parent_coefficient_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["parent_jet_factorization"].update(u="0")
            ).returncode,
            0,
        )

    def test_species_matrix_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["species_interference"][
                    "raised_profile_normalized_endomorphism"
                ][0].__setitem__(1, "0")
            ).returncode,
            0,
        )

    def test_scalar_history_weight_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["amplitude_components"][
                    "scalar_selected_history_relative_to_Born"
                ].update(numerator=4)
            ).returncode,
            0,
        )

    def test_identity_species_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    second_positive_scalar_I2_species_jump="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_amplitude_affiliation_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    amplitude_affiliation_above_first_jump="AFFILIATED"
                )
            ).returncode,
            0,
        )

    def test_enlarged_carrier_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    minimal_enlarged_profile_carrier="CONSTRUCTED"
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
                lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
            ).returncode,
            0,
        )

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
